class CustomError(BaseException):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class MissingDelimiterException(CustomError):
    def __init__(self, message, line_position, start_position):
        self.message = f'Пропущен \'{message}\': ({line_position}, {start_position})'
        super().__init__(self.message)


class FalseProgramEnd(CustomError):
    def __init__(self, line_position, start_position):
        self.message = f'Конец программы был на: ({line_position}, {start_position})'
        super().__init__(self.message)


class UnexpectedSymbol(CustomError):
    def __init__(self, message, line_position, start_position):
        self.message = f'Неожиданная последовательность символов {message}: ({line_position}, {start_position})'
        super().__init__(self.message)


class UndeclaredID(CustomError):
    def __init__(self, message, line_position, start_position):
        self.message = f'Необъявленный идентификатор {message}: ({line_position}, {start_position})'
        super().__init__(self.message)


class IDRedeclaration(CustomError):
    def __init__(self, message, line_position, start_position):
        self.message = f'Повторное объявление идентификатора {message}: ({line_position}, {start_position})'
        super().__init__(self.message)


class TypeExpressionError(CustomError):
    def __init__(self, message, line_position, start_position, expected_type, real_type):
        self.message = f'Ошибка типа в {message}: ({line_position}, {start_position}). Ожидалось {expected_type}, получено {real_type}'
        super().__init__(self.message)


class WrongExpressionError(CustomError):
    def __init__(self, line_position):
        self.message = f'Ошибка типа в выражении на {line_position} строке'
        super().__init__(self.message)
