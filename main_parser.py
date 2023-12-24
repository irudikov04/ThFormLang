from lexer_tokens import TokenType
from main_lexer import Token
from parser_errors import *
import json

operations_array = {('%', '+', '%'): '%',
                    ('%', '-', '%'): '%',
                    ('%', '*', '%'): '%',
                    ('%', '/', '%'): '%',
                    ('%', '+', '!'): '!',
                    ('%', '-', '!'): '!',
                    ('%', '*', '!'): '!',
                    ('%', '/', '!'): '!',
                    ('!', '+', '!'): '!',
                    ('!', '-', '!'): '!',
                    ('!', '*', '!'): '!',
                    ('!', '/', '!'): '!',
                    ('%', '=', '%'): '$',
                    ('%', '=', '!'): '$',
                    ('!', '=', '!'): '$',
                    ('%', '<', '%'): '$',
                    ('%', '<', '!'): '$',
                    ('!', '<', '!'): '$',
                    ('$', '=', '$'): '$',
                    ('$', '&', '$'): '$',
                    ('$', '|', '$'): '$'}

equal_names = {'%': TokenType.TYPE_I,
               '$': TokenType.TYPE_B,
               '!': TokenType.TYPE_F}


class Parser:
    def __init__(self, tokens: list[Token], id_array: dict):
        self.tokens = tokens
        self.position = 0
        self.k = 0
        self.previous_token = Token()
        self.current_token = Token()
        self.id_array = id_array
        self.stack = []
        self.previous_previous_token = Token()

    def __call__(self):
        try:
            self.program()
            with open('id.json', 'w') as file:
                for elem in self.id_array:
                    self.id_array[elem]['type'] = str(self.id_array[elem]['type'])
                json.dump(self.id_array, file, ensure_ascii=False, indent=4)
            print('Синтаксический и семантический анализ завершены успешно')
        except CustomError as e:
            print(e.message)
            print('Анализ программы завершён с ошибкой')

    def next_token(self):
        self.position += 1
        self.previous_token = self.current_token
        self.current_token = self.tokens[self.position - 1] if self.position - 1 != len(self.tokens) else Token()

    def previous_token1(self):
        self.position -= 1
        self.current_token = self.tokens[self.position] if self.position != -1 else Token()
        self.previous_token = self.tokens[self.position - 1] if self.position - 1 != -1 else Token()
        self.previous_previous_token = self.tokens[self.position - 2] if self.position - 2 != -1 else Token()

    def get_previous_previous_token(self):
        return self.previous_previous_token
    def get_expression_type(self):
        operand1 = self.stack.pop()
        if len(self.stack) == 0:
            self.stack.append(operand1)
            return
        op = self.stack.pop()
        operand2 = self.stack.pop()
        if (operand1, op, operand2) in operations_array:
            self.stack.append(operations_array[(operand1, op, operand2)])
        elif (operand2, op, operand1) in operations_array:
            self.stack.append(operations_array[(operand2, op, operand1)])
        else:
            raise WrongExpressionError(self.previous_token.line_number)

    def program(self):

        self.program_text()

    def initialize_variable(self):
        if self.current_token.token_type != TokenType.ID:
            raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)
        else:

            self.id_array[self.current_token.word]["type"] = self.current_token.token_type
            self.id_array[self.current_token.word]["declared"] = True

            self.next_token()
            if self.current_token.token_type != TokenType.TYPE:
                raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                       self.current_token.begin_position)
            self.next_token()
            if self.current_token.token_type not in (TokenType.TYPE_I, TokenType.TYPE_B, TokenType.TYPE_F):
                raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                       self.current_token.begin_position)

            d = list(self.id_array.keys())
            b = d[self.k]
            self.id_array[b]={'type': self.current_token.token_type, 'declared': True}
            self.next_token()
            if self.current_token.token_type != TokenType.SEMICOLON:
                raise MissingDelimiterException(';', self.previous_token.line_number,
                                                self.previous_token.begin_position)

    def peek_next_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        else:
            return None

    def peek_next_token2(self):
        return self.tokens[self.position].token_type
    def program_text(self):
        self.next_token()
        if self.current_token.token_type == TokenType.END_PROG:
            self.program_end()
        elif self.current_token.token_type == TokenType.EMPTY:
            raise MissingDelimiterException('end', self.previous_token.line_number,
                                            self.previous_token.begin_position + 1)
        else:
            if self.current_token.token_type == TokenType.ID and self.id_array[self.current_token.word]["declared"] == False and self.id_array[self.current_token.word]["type"] == None:
                next_token = self.peek_next_token()
                if next_token is not None:
                    if (next_token.token_type != TokenType.ASSIGN):
                        self.initialize_variable()
                        self.k += 1
            else:
                self.operator()
            self.program_text()


    def program_end(self):
        self.next_token()
        if self.current_token.token_type != TokenType.EMPTY:
            raise FalseProgramEnd(self.previous_token.line_number, self.previous_token.begin_position)


    def operator(self):
        self.next_token()
        match self.previous_token.token_type:
            case TokenType.BEGIN:
                self.complex_operator()
            case TokenType.ID:
                self.assign_operator()
            case TokenType.IF:
                self.condition_operator()
            case TokenType.FOR:
                self.for_operator()
            case TokenType.WHILE:
                self.while_operator()
            case TokenType.READ:
                self.read_operator()
            case TokenType.WRITE:
                self.write_operator()
            case TokenType.LINE_BREAK:
                self.operator()
            case TokenType.NEXT:
                self.previous_token1()
            case _:
                raise UnexpectedSymbol(self.previous_token.word, self.previous_token.line_number,
                                       self.previous_token.begin_position)



    def complex_operator(self):
        self.operator()
        if self.current_token.token_type in (TokenType.BEGIN, TokenType.SEMICOLON):
            if self.current_token.token_type == TokenType.END_PROG or self.peek_next_token().token_type == TokenType.END_PROG:
                self.next_token()
            else:
                self.next_token()
                self.complex_operator()
        elif self.current_token.token_type == TokenType.END_PROG:
            self.next_token()
        else:
            raise MissingDelimiterException('end', self.previous_token.line_number,
                                            self.previous_token.begin_position)


    def assign_operator(self):
        if self.current_token.token_type != TokenType.ASSIGN:
            raise MissingDelimiterException(':=', self.current_token.line_number,
                                            self.current_token.begin_position)
        else:
            if not self.id_array[self.previous_token.word]['declared']:
                raise UndeclaredID(self.previous_token.word, self.previous_token.line_number,
                                   self.previous_token.begin_position)
            current_id = self.previous_token
            id_type = self.id_array[self.previous_token.word]['type']
            self.next_token()
            self.expression()
            expr_type = self.stack.pop()
            self.previous_token1()
            if equal_names[expr_type] != id_type:
                raise TypeExpressionError(current_id.word, current_id.line_number,
                                          current_id.begin_position, id_type, equal_names[expr_type])
            self.next_token()
            if self.current_token.token_type != TokenType.SEMICOLON and self.get_previous_previous_token() == TokenType.FOR:
                raise MissingDelimiterException(';', self.previous_token.line_number,
                                                self.previous_token.begin_position)

    def condition_operator(self):
        self.expression()
        expr_type = self.stack.pop()
        if expr_type != '$':
            raise TypeExpressionError("условии", self.previous_token.line_number,
                                      self.previous_token.begin_position, TokenType.TYPE_B, equal_names[expr_type])
        else:
            self.operator()
            if self.current_token.token_type == TokenType.ELSE:
                self.next_token()
                self.operator()

    def for_operator(self):
        current_id = self.current_token
        if current_id.token_type != TokenType.ID:
            raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)
        if not self.id_array[current_id.word]['declared']:
            raise UndeclaredID(current_id.word, current_id.line_number, current_id.begin_position)
        if self.id_array[current_id.word]['type'] != TokenType.TYPE_I:
            raise TypeExpressionError(current_id.word, current_id.line_number, current_id.begin_position,
                                      TokenType.TYPE_I, self.id_array[self.current_token.word]['type'])
        self.next_token()
        self.assign_operator()

        if self.current_token.token_type != TokenType.TO:
            raise MissingDelimiterException('to', self.current_token.line_number,
                                            self.current_token.begin_position)
        else:
            if self.current_token != TokenType.INTEGER:
                self.next_token()
                self.expression()
                expr_type = equal_names[self.stack.pop()]
                if expr_type != self.id_array[current_id.word]['type']:
                    raise TypeExpressionError(current_id.word, current_id.line_number, current_id.begin_position,
                                              self.id_array[current_id.word]['type'], expr_type)
                else:
                    self.next_token()
                    self.next_token()
                    if self.current_token != TokenType.NEXT:
                        self.operator()
                    else:
                        self.next_token()
            else:
                self.next_token()
                self.next_token()
                if self.current_token != TokenType.NEXT:
                    self.operator()
                else:
                    self.next_token()



    def while_operator(self):
        self.expression()
        expr_type = self.stack.pop()
        if expr_type != '$':
            raise TypeExpressionError("условии цикла", self.previous_token.line_number,
                                      self.previous_token.begin_position, TokenType.TYPE_B, equal_names[expr_type])
        else:
            self.operator()

    def read_operator(self):
        if self.current_token.token_type != TokenType.LEFT_PAREN:
            raise MissingDelimiterException('(', self.current_token.line_number,
                                            self.current_token.begin_position)
        else:
            self.next_token()
            self.id_sequence()
            if self.current_token.token_type != TokenType.RIGHT_PAREN:
                raise MissingDelimiterException(')', self.current_token.line_number,
                                                self.current_token.begin_position)

    def write_operator(self):
        if self.current_token.token_type != TokenType.LEFT_PAREN:
            raise MissingDelimiterException('(', self.current_token.line_number,
                                            self.current_token.begin_position)
        else:
            self.next_token()
            self.expression_sequence()
            if self.current_token.token_type != TokenType.RIGHT_PAREN:
                raise MissingDelimiterException(')', self.current_token.line_number,
                                                self.current_token.begin_position)

    def id_sequence(self):
        if self.current_token.token_type != TokenType.ID:
            raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)
        else:
            if not self.id_array[self.current_token.word]['declared']:
                raise UndeclaredID(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)
            self.next_token()
            if self.current_token.token_type == TokenType.COMMA:
                self.next_token()
                self.id_sequence()

    def expression_sequence(self):
        self.expression()
        self.stack.pop()
        if self.current_token.token_type == TokenType.COMMA:
            self.next_token()
            self.expression_sequence()

    def expression(self):
        self.operand()
        if self.current_token.token_type in (TokenType.NEQ, TokenType.EQUAL,
                                             TokenType.LEQ, TokenType.LESS,
                                             TokenType.GEQ, TokenType.GREATER):
            if self.current_token.token_type in (TokenType.NEQ, TokenType.EQUAL):
                self.stack.append('=')
            else:
                self.stack.append('<')
            self.next_token()
            self.expression()
            self.get_expression_type()
        elif self.current_token.token_type == TokenType.ERR:
            raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)

    def operand(self):
        self.summand()
        if self.current_token.token_type in (TokenType.PLUS, TokenType.MINUS, TokenType.OR):
            match self.current_token.token_type:
                case TokenType.PLUS:
                    self.stack.append('+')
                case TokenType.MINUS:
                    self.stack.append('-')
                case TokenType.OR:
                    self.stack.append('|')
            self.next_token()
            self.operand()
            self.get_expression_type()

    def summand(self):
        self.multiplier()
        if self.current_token.token_type in (TokenType.MULT, TokenType.DIVIDE, TokenType.AND):
            match self.current_token.token_type:
                case TokenType.MULT:
                    self.stack.append('*')
                case TokenType.DIVIDE:
                    self.stack.append('/')
                case TokenType.AND:
                    self.stack.append('&')
            self.next_token()
            self.summand()
            self.get_expression_type()

    def multiplier(self):
        if self.current_token.token_type == TokenType.NOT:
            self.next_token()
            self.multiplier()
            if self.stack[0] != '$':
                raise TypeExpressionError(self.current_token.word, self.current_token.line_number,
                                          self.current_token.begin_position, equal_names[self.stack[0]], TokenType.TYPE_B)
        elif self.current_token.token_type == TokenType.LEFT_PAREN:
            self.next_token()
            self.expression()
            if self.current_token.token_type != TokenType.RIGHT_PAREN:
                raise MissingDelimiterException(')', self.previous_token.line_number,
                                                self.previous_token.begin_position)  # error
            else:
                self.next_token()
        elif self.current_token.token_type in (TokenType.ID, TokenType.INTEGER, TokenType.FLOAT,
                                               TokenType.TRUE, TokenType.FALSE):
            match self.current_token.token_type:
                case TokenType.ID:
                    match self.id_array[self.current_token.word]['type']:
                        case TokenType.TYPE_I:
                            self.stack.append('%')
                        case TokenType.TYPE_F:
                            self.stack.append('!')
                        case TokenType.TYPE_B:
                            self.stack.append('$')
                        case None:
                            raise UndeclaredID(self.current_token.word, self.current_token.line_number,
                                               self.current_token.begin_position)
                case TokenType.INTEGER:
                    self.stack.append('%')
                case TokenType.FLOAT:
                    self.stack.append('!')
                case TokenType.TRUE:
                    self.stack.append('$')
                case TokenType.FALSE:
                    self.stack.append('$')

            self.next_token()
        else:
            raise UnexpectedSymbol(self.current_token.word, self.current_token.line_number,
                                   self.current_token.begin_position)
