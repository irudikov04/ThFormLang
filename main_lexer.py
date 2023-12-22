from lexer_tokens import TokenType

class Lexer:
    def __init__(self, text: str):
        self.text = text + " "
        self.position = 0
        self.symbol = self.text[self.position]
        self.symbol_position = 0
        self.word_position = 0
        self.word = ""
        self.line_number = 0
        self.state = self.start_state
        self.token_array = []
        self.id_array = {}
        self.comment_flag = False
        self.complex_flag = False

    def next_symbol(self):
        self.position += 1
        self.symbol_position += 1
        if self.position != len(self.text):
            self.symbol = self.text[self.position]

    def add_symbol(self):
        self.word += self.symbol

    """
    Добавляет токен в массив токенов и сбрасывает автомат в начальное положение
    """
    def add_token(self, token_type: TokenType):
        if not self.comment_flag and (self.complex_flag or token_type != TokenType.LINE_BREAK):
            self.token_array.append(Token(token_type, self.word, self.line_number + 1, self.word_position + 1))
        self.word = ""
        self.word_position = self.symbol_position
        self.state = self.start_state

    def __call__(self):
        try:
            while self.position < len(self.text):
                self.state()
            return self.token_array, self.id_array
        except LexerError as e:
            print(e.message)
            return self.token_array, "error"


    def err_state(self):
        while self.symbol not in all_delimiters:
            self.add_symbol()
            self.next_symbol()
        raise LexerError(self.word, self.line_number + 1, self.word_position + 1)

    def start_state(self):
        if self.symbol.isalpha():
            self.state = self.id_state
        elif self.symbol in "01":
            self.state = self.bin_state
        elif self.symbol in "234567":
            self.state = self.oct_state
        elif self.symbol in "89":
            self.state = self.dec_state
        elif self.symbol == '.':
            self.state = self.fract_state
        elif self.symbol in "/*":
            self.state = self.comment_state
        elif self.symbol in "!=":
            self.state = self.compare_state
        elif self.symbol in ":=":
            self.state = self.assign_state
        elif self.symbol == "&":
            self.state = self.and_state
        elif self.symbol == "|":
            self.state = self.or_state
        elif self.symbol in "\t\n ":
            if self.symbol == "\n":
                self.add_symbol()
                self.next_symbol()
                self.add_token(TokenType.LINE_BREAK)
                self.line_number += 1
                self.symbol_position = 0
                self.word_position = 0
            elif self.symbol == "\t":
                self.next_symbol()
                self.symbol_position += 3
                self.word_position += 4
            else:
                self.next_symbol()
                self.word_position += 1
        else:
            self.state = self.delimiter_state


    def id_state(self):
        self.add_symbol()
        self.next_symbol()
        if not self.symbol.isalnum():
            token_type = decode_token_type(self.word)
            if token_type != TokenType.EMPTY:
                self.add_token(token_type)
            else:
                if not self.comment_flag:
                    self.id_array.setdefault(self.word, {"type": None, "declared": False})
                self.add_token(TokenType.ID)

    def comment_state(self):
        '''Состояние комменатриев'''
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "/*":
            self.add_symbol()
            self.next_symbol()
            if self.word == "/*":
                self.comment_flag = True
                self.add_token(TokenType.BEGIN_COMMENT)
            elif self.word == "*/":
                self.add_token(TokenType.END_COMMENT)
                self.comment_flag = False
            else:
                self.state = self.err_state
        else:
            self.state = self.operator_state


    def and_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol == "&":
            self.add_symbol()
            self.next_symbol()
            self.add_token(TokenType.AND)
        else:
            self.state = self.err_state

    def assign_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "<>=":
            self.state = self.assign_state
        else:
            token_type = decode_token_type(self.word)
            if token_type != TokenType.EMPTY:
                self.add_token(token_type)
            else:
                self.state = self.err_state

    def or_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol == "|":
            self.add_symbol()
            self.next_symbol()
            self.add_token(TokenType.OR)
        else:
            self.state = self.err_state

    def operator_state(self):
        if self.word in ["*", "/"]:
            self.add_token(decode_token_type(self.word))
        else:
            self.state = self.err_state

    def delimiter_state(self):
        self.add_symbol()
        self.next_symbol()
        token_type = decode_token_type(self.word)
        if token_type != TokenType.EMPTY:
            self.add_token(token_type)
            if token_type == TokenType.BEGIN_COMPLEX:
                self.complex_flag = True
            elif token_type == TokenType.END_COMPLEX:
                self.complex_flag = False
        else:
            self.state = self.err_state

    def compare_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "<>=":
            self.state = self.compare_state
        else:
            token_type = decode_token_type(self.word)
            if token_type != TokenType.EMPTY:
                self.add_token(token_type)
            else:
                self.state = self.err_state

    def bin_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "01":
            self.state = self.bin_state
        elif self.symbol in "234567":
            self.state = self.oct_state
        elif self.symbol in "89":
            self.state = self.dec_state
        elif self.symbol == ".":
            self.state = self.fract_state
        elif self.symbol in "eE":
            self.state = self.exp_state
        elif self.symbol in "bB":
            self.state = self.bin_end_state
        elif self.symbol in "dD":
            self.state = self.dec_end_state
        elif self.symbol in "oO":
            self.state = self.oct_end_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        elif self.symbol in "acfACF":
            self.state = self.hex_state
        elif self.symbol.isalpha():
            self.state = self.err_state
        else:
            self.add_token(TokenType.INTEGER)

    def bin_end_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in all_delimiters:
            self.add_token(TokenType.INTEGER)
        elif self.symbol.isnumeric() or self.symbol in "abcdefABCDEF":
            self.state = self.hex_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        else:
            self.state = self.err_state

    def oct_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "01234567":
            self.state = self.oct_state
        elif self.symbol in "89":
            self.state = self.dec_state
        elif self.symbol == ".":
            self.state = self.fract_state
        elif self.symbol in "eE":
            self.state = self.exp_state
        elif self.symbol in "dD":
            self.state = self.dec_end_state
        elif self.symbol in "oO":
            self.state = self.oct_end_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        elif self.symbol in "abcfABCF":
            self.state = self.hex_state
        elif self.symbol.isalpha():
            self.state = self.err_state
        else:
            self.add_token(TokenType.INTEGER)

    def oct_end_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in all_delimiters:
            self.add_token(TokenType.INTEGER)
        else:
            self.state = self.err_state

    def dec_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.dec_state
        elif self.symbol == ".":
            self.state = self.fract_state
        elif self.symbol in "eE":
            self.state = self.exp_state
        elif self.symbol in "dD":
            self.state = self.dec_end_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        elif self.symbol in "abcfABCF":
            self.state = self.hex_state
        elif self.symbol.isalpha():
            self.state = self.err_state
        else:
            self.add_token(TokenType.INTEGER)

    def dec_end_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in all_delimiters:
            self.add_token(TokenType.INTEGER)
        elif self.symbol.isnumeric() or self.symbol in "abcdefABCDEF":
            self.state = self.hex_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        else:
            self.state = self.err_state

    def hex_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric() or self.symbol in "abcdefABCDEF":
            self.state = self.hex_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        else:
            self.state = self.err_state

    def hex_end_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in all_delimiters:
            self.add_token(TokenType.INTEGER)
        else:
            self.state = self.err_state

    def fract_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.fract_value_state
        else:
            self.state = self.err_state

    def fract_value_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.fract_value_state
        elif self.symbol in "eE":
            self.state = self.fract_exp_state
        elif self.symbol in all_delimiters:
            self.add_token(TokenType.FLOAT)
        else:
            self.state = self.err_state

    def exp_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.unsigned_exp_state
        elif self.symbol in "+-":
            self.state = self.sign_exp_state
        elif self.symbol in "abcdefABCDEF":
            self.state = self.hex_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        else:
            self.state = self.err_state

    def unsigned_exp_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.unsigned_exp_state
        elif self.symbol in "abcdefABCDEF":
            self.state = self.hex_state
        elif self.symbol in "hH":
            self.state = self.hex_end_state
        elif self.symbol in all_delimiters:
            self.add_token(TokenType.FLOAT)
        else:
            self.state = self.err_state

    def fract_exp_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol in "+-":
            self.state = self.sign_exp_state
        elif self.symbol.isnumeric():
            self.state = self.value_exp_state
        else:
            self.state = self.err_state

    def sign_exp_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.value_exp_state
        else:
            self.state = self.err_state

    def value_exp_state(self):
        self.add_symbol()
        self.next_symbol()
        if self.symbol.isnumeric():
            self.state = self.value_exp_state
        elif self.symbol in all_delimiters:
            self.add_token(TokenType.FLOAT)
        else:
            self.state = self.err_state




class Token:
    def __init__(self, token_type: TokenType = TokenType.EMPTY,
                 word: str = '', line_number: int = -1, begin_position: int = -1):
        self.token_type = token_type
        self.word = word
        self.line_number = line_number
        self.begin_position = begin_position

    def __str__(self):
        if self.word == '\n':
            return f"({self.token_type}, \\n, {self.line_number}, {self.begin_position})"
        return f"({self.token_type}, {self.word}, {self.line_number}, {self.begin_position})"

all_delimiters = ["\t", "\n", " ", ":", ",", ";", "{", "}", "[", "]", "(", ")",
                  "%", "$", "!", "+", "-", "/", "*", "<", ">", "="]

keywords = {
    ":=": TokenType.ASSIGN,
    "if": TokenType.IF,
    "then": TokenType.THEN,
    "else": TokenType.ELSE,
    "for": TokenType.FOR,
    "step": TokenType.STEP,
    "begin": TokenType.BEGIN,
    "next": TokenType.NEXT,
    "while": TokenType.WHILE,
    "readln": TokenType.READ,
    "writeln": TokenType.WRITE,
    "true": TokenType.TRUE,
    "false": TokenType.FALSE,
    "to": TokenType.TO,
    "&&": TokenType.AND,
    "||": TokenType.OR,
    "not": TokenType.NOT,
    "%": TokenType.TYPE_I,
    "!": TokenType.TYPE_F,
    "$": TokenType.TYPE_B,
    "end": TokenType.END_PROG,
    "[": TokenType.BEGIN_COMPLEX,
    "]": TokenType.END_COMPLEX,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    ",": TokenType.COMMA,
    ";": TokenType.SEMICOLON,
    #":": TokenType.COLON,
    ":": TokenType.TYPE,
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "/": TokenType.DIVIDE,
    "*": TokenType.MULT,
    "/*": TokenType.BEGIN_COMMENT,
    "*/": TokenType.END_COMMENT,
    "!=": TokenType.NEQ,
    "==": TokenType.EQUAL,
    "<": TokenType.LESS,
    "<=": TokenType.LEQ,
    ">": TokenType.GREATER,
    ">=": TokenType.GEQ,
}


def decode_token_type(token: str):
    global keywords
    return keywords[token] if token in keywords else TokenType.EMPTY


class LexerError(BaseException):
    def __init__(self, message, line_number, start_position):
        self.message = f"Неопознанная лексема {message}: ({line_number}, {start_position})"
        super().__init__(message)
