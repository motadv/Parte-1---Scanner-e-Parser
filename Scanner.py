from typing import List, Tuple
import re


blanks = [" ", "\n", "\t", "\r", "\f"]
reserved_words = [
    "boolean",
    "class",
    "extends",
    "public",
    "static",
    "void",
    "main",
    "String",
    "return",
    "int",
    "if",
    "else",
    "while",
    "System.out.println",
    "length",
    "true",
    "false",
    "this",
    "new",
    "null"
]

terminal_symbols = [
    "(", ")",
    "{", "}",
    "[", "]",
    ";", ",", ".",
    "=",
    "==", "!=", "<", "<=", ">", ">=",
    "&&", "+", "-", "*"
]


def isIdentifier(str) -> bool:
    """
    Checks if a string is an identifier.
    :param str: The string to check.
    :return: True if the string is an identifier, False otherwise.
    """
    return re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", str) is not None


def isReservedWord(str) -> bool:
    """
    Checks if a string is a reserved word.
    :param str: The string to check.
    :return: True if the string is a reserved word, False otherwise.
    """
    return str in reserved_words


def parseToken(string) -> tuple[str, str]:
    """
    Parses a token from a string.
    :param string: The string to parse.
    :return: A tuple containing the token and its type.
    """

    # FDA for tokens
    pass


def remove_comments(string) -> str:
    """
    Removes comments from a string.
    :param string: The string to remove comments from.
    :return: The string without comments.
    """
    out_string = re.sub(r"//.*?[\n\r]", "", string)
    out_string = re.sub(r"/\*.*?\*/", "", out_string, flags=re.DOTALL)
    return out_string


def add_spaces(string) -> str:
    """
    Adds spaces around terminal symbols.
    :param string: The string to add spaces to.
    :return: The string with spaces around terminal symbols.
    """
    for symbol in terminal_symbols:
        string = string.replace(symbol, f" {symbol} ")
    return string


def isIntegerNumber(str) -> bool:
    """
    Checks if a string is an integer number.
    :param str: The string to check.
    :return: True if the string is an integer number, False otherwise.
    """
    return re.match(r"^[0-9]+$", str) is not None


def unify_println(string) -> str:
    """
    Unifies System.out.println into a single token.
    :param string: The string to unify.
    :return: The string with System.out.println unified.
    """
    out_string = re.sub(
        r"System[\s\n\t\r\f]*\.[\s\n\t\r\f]*out[\s\n\t\r\f]*\.[\s\n\t\r\f]*println",
        "System.out.println", string
    )

    return out_string


def parseProgram(program) -> List[Tuple[str, str]]:
    """
    Parses a program from a string.
    Returns a list of tokens where each token is the [word, type].
    :param string: The string to parse.
    :return: The list of tokens sequentially. Throws an exception if a token is not recognized.
    """

    tokenList = []

    # Pré-processamento
    # Remove todos os comentários de linha
    program = remove_comments(program)
    program = add_spaces(program)
    program = unify_println(program)

    for word in program.split():
        if word in reserved_words:
            tokenList.append((word, word))
        elif word in terminal_symbols:
            tokenList.append((word, word))
        elif isIdentifier(word):
            tokenList.append((word, "identifier"))
        elif isIntegerNumber(word):
            tokenList.append((word, "number"))
        else:
            raise Exception(
                f"Não foi possível interpretar um token no programa: {word}")

    return tokenList


token_list = []

# Abre o arquivo para leitura
with open("program.java", "r") as f:
    program = f.read()
    tokenList = parseProgram(program)

with open("output.txt", "w") as f:
    for token in tokenList:
        f.write(f"{token[0]} | {token[1]}\n")
