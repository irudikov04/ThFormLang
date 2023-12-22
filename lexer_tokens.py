from enum import Enum


class TokenType(Enum):
    ID = 0
    INTEGER = 1
    FLOAT = 2
    EQUAL = 3
    PLUS = 4
    MULT = 5
    NOT = 6
    KEYWORD = 7
    END_PROG = 8
    BEGIN_COMPLEX = 9
    END_COMPLEX = 10
    TYPE = 11
    COMMA = 12
    SEMICOLON = 13
    LINE_BREAK = 14
    COLON = 15
    ASSIGN = 16
    IF = 17
    THEN = 18
    ELSE = 19
    FOR = 20
    WHILE = 21
    READ = 22
    WRITE = 23
    TRUE = 24
    FALSE = 25
    BEGIN_COMMENT = 26
    END_COMMENT = 27
    ERR = 28
    LEFT_PAREN = 29
    RIGHT_PAREN = 30
    TYPE_I = 31
    TYPE_F = 32
    TYPE_B = 33
    MINUS = 34
    DIVIDE = 35
    AND = 36
    OR = 37
    NEQ = 38
    GEQ = 39
    GREATER = 40
    LEQ = 41
    LESS = 42
    EMPTY = 43
    NEXT = 44
    END = 45
    STEP = 46
    BEGIN = 47
    TO = 48
