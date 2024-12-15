import json
import pandas as pd

EBNF = {
    "<PROG>": [
        ["<MAIN>", "<LCLASSE>"]
    ],
    "<MAIN>": [
        ["class", "identifier", "{", "public", "static", "void", "main",
            "(", "String", "[", "]", "identifier", ")", "{", "<CMD>", "}", "}"]
    ],
    "<CLASSE>": [
        ["class", "identifier", "<OEXTEND>", "{", "<LVAR>", "<LMETODO>", "}"]
    ],
    "<LCLASSE>": [
        ["<CLASSE>", "<LCLASSE>"],
        []
    ],
    "<OEXTEND>": [
        ["extends", "identifier"],
        []
    ],
    "<VAR>": [
        ["<TIPO>", "identifier", ";"]
    ],
    "<LVAR>": [
        ["<VAR>", "<LVAR>"],
        []
    ],
    "<METODO>": [
        ["public", "<TIPO>", "identifier", "(", "<OPARAMS>", ")", "{", "<LVAR>", "<LCMD>", "return", "<EXP>", ";",
         "}"]
    ],
    "<LMETODO>": [
        ["<METODO>", "<LMETODO>"],
        []
    ],
    "<PARAMS>": [
        ["<TIPO>", "identifier", "<PARAMS_>"]
    ],
    "<PARAMS_>": [
        [",", "<TIPO>", "identifier", "<PARAMS_>"],
        []
    ],
    "<OPARAMS>": [
        ["<PARAMS>"],
        []
    ],
    "<TIPO>": [
        ["int", "<TIPO_>"],
        ["boolean"],
        ["identifier"]
    ],
    "<TIPO_>": [
        ["[", "]"],
        []
    ],
    "<CMD>": [
        ["{", "<LCMD>", "}"],
        ["if", "(", "<EXP>", ")", "<CMD>", "<CMDELSE>"],
        ["while", "(", "<EXP>", ")", "<CMD>"],
        ["System.out.println", "(", "<EXP>", ")", ";"],
        ["identifier", "<CMDID>"]
    ],
    "<CMDELSE>": [
        ["else", "<CMD>"],
        []
    ],
    "<CMDID>": [
        ["=", "<EXP>", ";"],
        ["[", "<EXP>", "]", "=", "<EXP>", ";"]
    ],
    "<LCMD>": [
        ["<CMD>", "<LCMD>"],
        []
    ],
    "<EXP>": [
        ["<REXP>", "<EXP_>"]
    ],
    "<EXP_>": [
        ["&&", "<REXP>", "<EXP_>"],
        []
    ],
    "<REXP>": [
        ["<AEXP>", "<REXP_>"]
    ],
    "<REXP_>": [
        ["<", "<AEXP>", "<REXP_>"],
        ["==", "<AEXP>", "<REXP_>"],
        ["!=", "<AEXP>", "<REXP_>"],
        []
    ],
    "<AEXP>": [
        ["<MEXP>", "<AEXP_>"]
    ],
    "<AEXP_>": [
        ["+", "<MEXP>", "<AEXP_>"],
        ["-", "<MEXP>", "<AEXP_>"],
        []
    ],
    "<MEXP>": [
        ["<SEXP>", "<MEXP_>"]
    ],
    "<MEXP_>": [
        ["*", "<SEXP>", "<MEXP_>"],
        []
    ],
    "<SEXP>": [
        ["!", "<SEXP>"],
        ["-", "<SEXP>"],
        ["true"],
        ["false"],
        ["number"],
        ["null"],
        ["new", "<NEWEXP>"],
        ["<PEXP>", "<SEXP_>"]
    ],
    "<SEXP_>": [
        [".", "length"],
        ["[", "<EXP>", "]"],
        []
    ],
    "<PEXP>": [
        ["identifier", "<PEXP_>"],
        ["this", "<PEXP_>"],
        ["(", "<EXP>", ")", "<PEXP_>"]
    ],
    "<PEXP_>": [
        [".", "identifier", "<PEXP__>"],
        []
    ],
    "<PEXP__>": [
        ["<PEXP_>"],
        ["(", "<OEXPS>", ")", "<PEXP_>"]
    ],
    "<NEWEXP>": [
        ["identifier", "(", ")", "<PEXP_>"],
        ["int", "[", "<EXP>", "]"]
    ],
    "<EXPS>": [
        ["<EXP>", "<EXPS_>"]
    ],
    "<EXPS_>": [
        [",", "<EXP_>"],
        []
    ],
    "<OEXPS>": [
        ["<EXPS>"],
        []
    ],
}

TERMINAL_LIST = {
    "class", "public", "static", "void", "main", "String", "[", "]", "identifier", "(", ")", "{", "}", "extends",
    ";", "return", "int", "boolean", "if", "else", "while", "System.out.println", "=", "&&", "<", "==", "!=", "+",
    "-", "*", "!", "true", "false", "number", "null", "new", ".", "length", "this", ",",
}

BASE_CHAR = "$"


class Token:
    type_: str
    value: str

    def __init__(self, type_: str, value: str) -> None:
        self.type_ = type_
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type_}, {self.value})"


class Node:
    token: Token
    children: list

    def __init__(self, token: Token, children=None):
        self.token = token
        if children is None:
            children = []
        self.children = children

    def __repr__(self) -> str:
        return f"Node({self.token} -> {self.children})"


class Parser:
    ebnf: dict[str, list[list[str]]]
    first: dict[str, set[str | None]]
    follow: dict[str, set[str | None]]
    input_: list[Token]
    parser: list[str]
    start: str
    terminal_list: set[str]
    table: dict[str, dict[str, list[tuple[str, list[str]]]]]

    def __init__(
        self,
        ebnf: dict[str, list[list[str]]],
        input_: list[Token],
        start: str,
        terminal_list: set[str]
    ) -> None:
        self.ebnf = ebnf
        self.terminal_list = terminal_list
        self.start = start

        self.input_ = [*input_, BASE_CHAR]
        self.parser = [self.start, BASE_CHAR]

        self.create_first()
        self.create_follow()
        self.create_table()

    def create_first(self) -> None:
        """
        Creates the *First* set for each non-terminal token in the EBNF.
        """

        first_set = {token: set() for token in self.ebnf.keys()}

        for terminal in self.terminal_list:
            first_set[terminal] = {terminal}

        def derives_epsilon(token: str) -> bool:
            """
            Checks if the token *first* value can reach *Epsilon*.

            :param token: Non-terminal token.
            :return: True if token *first* value can reach *Epsilon*.
            """

            return None in first_set[token]

        def add_to_first(target: str, source: set[str | None]) -> bool:
            """
            Adds a value in the *First* set if it's not duplicated.

            :param target: The new *first* value.
            :param source: The *First* set for the value to be added.
            :return: True if the value has been added.
            """

            initial_size = len(first_set[target])
            first_set[target].update(source)
            return len(first_set[target]) > initial_size

        changed = True
        while changed:
            changed = False
            for non_terminal, productions in self.ebnf.items():
                for production in productions:
                    skip = False
                    for token in production:
                        if not skip:
                            if token in self.terminal_list or token not in self.ebnf:
                                changed |= add_to_first(non_terminal, {token})
                                skip = True
                            else:
                                changed |= add_to_first(
                                    non_terminal, first_set[token])
                                if not derives_epsilon(token):
                                    skip = True
                    else:
                        if len(production) == 0 or not skip:
                            changed |= add_to_first(non_terminal, {None})

        self.first = first_set

    def subset_first(self, subset: list[str]) -> set[str | None]:
        """
        Computes the *First* set for a subset of tokens (a production rule).

        :param subset: A list of tokens (terminals and non-terminals).
        :return: A set representing the *First* set for the subset, including None if epsilon is derivable.
        """
        result = set()

        for token in subset:
            # Add the First set of the current token to the result
            result.update(self.first[token] - {None})

            # If the current token does not derive epsilon, stop
            if None not in self.first[token]:
                break
        else:
            # If all tokens derive epsilon, add epsilon (None) to the result
            result.add(None)

        return result

    def create_follow(self) -> None:
        """
        Creates the *Follow* set for each non-terminal token in the EBNF.
        """

        follow_set = {token: set() for token in self.ebnf.keys()}
        # The start token always follows the base character.
        follow_set[self.start].add(BASE_CHAR)

        def add_to_follow(target: str, source: set[str | None]) -> bool:
            """
            Adds a value in the *Follow* set if it's not duplicated.

            :param target: The new *follow* value.
            :param source: The *Follow* set for the values to be added.
            :return: True if the value has been added.
            """

            initial_size = len(follow_set[target])
            follow_set[target].update(source)
            return len(follow_set[target]) > initial_size

        changed = True
        while changed:
            changed = False
            for non_terminal, productions in self.ebnf.items():
                for production in productions:
                    for i, token in enumerate(production):
                        if token in self.ebnf:
                            # Add the first of the next token to the follow of the current token except for epsilon
                            if i < len(production) - 1:
                                changed |= add_to_follow(
                                    token, self.subset_first(
                                        production[i + 1:]) - {None}
                                )
                            # If last token in production, add follow of non-terminal to the current token
                            # or if the next token can derive epsilon, add follow of non-terminal to the current token
                            if i == len(production) - 1 or (None in self.subset_first(production[i + 1:])):
                                changed |= add_to_follow(
                                    token, follow_set[non_terminal]
                                )

        self.follow = follow_set

    def create_table(self) -> None:
        # EBNF: A -> Epsilon = A contains []

        table = {non_terminal: {terminal: [] for terminal in (self.terminal_list | {BASE_CHAR})}
                 for non_terminal in self.ebnf.keys()}

        # For each production for that particular non-terminal
        for A, productions in self.ebnf.items():
            # For each terminal in the first of the non-terminal, add the production to table[non_terminal][terminal]
            for alpha in productions:
                first_of_alpha = self.subset_first(alpha)
                A_alpha = (A, alpha)
                for a in first_of_alpha - {None}:
                    table[A][a].append(
                        A_alpha)
                    if None in first_of_alpha:
                        for a in self.follow[A]:
                            if A_alpha not in table[A][a]:
                                table[A][a].append(
                                    A_alpha)

        self.table = table

    def execute(self) -> Node:
        # TODO: execute first node recursion
        pass

    def read(self, node: Node) -> Node:
        # TODO: read single node
        pass


with open("output.txt", "r") as f:
    tokens = [Token(*line.strip().split(" | ")) for line in f]

parser = Parser(
    ebnf=EBNF,
    start=EBNF.keys().__iter__().__next__(),
    terminal_list=TERMINAL_LIST,
    input_=tokens
)

# for non_terminal, row in parser.table.items():
#     for terminal, productions in row.items():
#         if len(productions) > 1:
#             print(
#                 f"Cell [{non_terminal}, {terminal}] has more than one production: {productions}")
#
# df = pd.DataFrame(parser.table).T
# df = df.map(lambda cell: ', '.join(
#     [f"{nt} -> {' '.join(prod)}" for nt, prod in cell]))
# df.to_excel("parsing_table.xlsx", index=True)
#
# with open("first_set.json", "w") as f:
#     json.dump({k: list(v) for k, v in parser.first.items()}, f, indent=4)
# with open("follow_set.json", "w") as f:
#     json.dump({k: list(v) for k, v in parser.follow.items()}, f, indent=4)
