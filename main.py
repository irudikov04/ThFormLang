from main_lexer import Lexer
from main_parser import Parser


def main():
    path = "text.txt" #input("Введите путь до программы: ")
    with open(path, "r", encoding="utf-8") as file:
        lex = Lexer(file.read())
    result, id_array = lex()

    with open('lexems.txt', 'w') as file:
        for elem in result:
            file.write(str(elem) + '\n')
    if id_array != "error":
        print("Лексический анализ текста завершён успешно")
        parse = Parser(result, id_array)
        parse()
        print(id_array)
    else:
        print("Лексический анализ текста завершён с ошибкой")


if __name__ == '__main__':
    main()
