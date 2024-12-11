EBNF = {
    "<PROG>": [
        ["<MAIN>", "<LCLASSE>"]
    ],
    "<MAIN>": [
        ["class", "identifier", "{", "public", "static", "void", "main", "(", "String", "[", "]", "identifier", ")", "{", "<CMD>", "}", "}"]
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
        ["int", "[", "]"],
        ["boolean"],
        ["int"],
        ["identifier"]
    ],
    "<CMD>": [
        ["<MATCH>"],
        ["<UNMATCH>"]
    ],
    "<LCMD>": [
        ["<CMD>", "<LCMD>"],
        []
    ],
    "<MATCH>": [
        ["if", "(", "<EXP>", ")", "<MATCH>", "else", "<MATCH>"],
        ["{", "<LCMD>", "}"],
        ["while", "(", "<EXP>", ")", "<CMD>"],
        ["System.out.println", "(", "<EXP>", ")", ";"],
        ["identifier", "=", "<MATCH_>"]
    ],
    "<MATCH_>": [
        ["=", "<EXP>", ";"],
        ["[", "<EXP>", "]", "=", "<EXP>", ";"]
    ],
    "<UNMATCH>": [
        ["if", "(", "<EXP>", ")", "<UNMATCH_>"]
    ],
    "<UNMATCH_>": [
        ["<CMD>"],
        ["<MATCH>", "else", "<UNMATCH>"]
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
        ["new", "int", "[", "<EXP>", "]"],
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
        ["new", "identifier", "(", ")", "<PEXP_>"],
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


class Node:
    label: str
    value: str

    def __init__(self, label: str, value: str, children=None):
        if children is None:
            children = []
        self.children = children
        self.label = label
        self.value = value


class Parser:
    ebnf: dict[str, list[list[str]]]
    first: dict[str, set[str | None]]
    follow: dict[str, set[str | None]]
    input_: list[str]
    parser: list[str]
    start: str
    terminal_list: set[str]

    def __init__(
        self,
        ebnf: dict[str, list[list[str]]],
        input_: list[str],
        start: str,
        terminal_list: set[str]
    ) -> None:
        self.ebnf = ebnf
        self.terminal_list = terminal_list
        self.start = start

        self.input_ = [BASE_CHAR, *input_]
        self.parser = [BASE_CHAR, self.start]

        self.create_first()
        self.create_follow()

    def create_first(self) -> None:
        """
        Creates the *First* set for each non-terminal token in the EBNF.
        """

        first_set = {token: set() for token in self.ebnf.keys()}

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
                                changed |= add_to_first(non_terminal, first_set[token])
                                if not derives_epsilon(token):
                                    skip = True
                    else:
                        if len(production) == 0 or not skip:
                            changed |= add_to_first(non_terminal, {None})

        self.first = first_set

    def create_follow(self) -> None:
        """
        Creates the *Follow* set for each non-terminal token in the EBNF.
        """

        follow_set = {token: set() for token in self.ebnf.keys()}
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
                    trailer = follow_set[non_terminal].copy()

                    for token in reversed(production):
                        if token in self.ebnf:
                            changed |= add_to_follow(token, trailer)

                            if None in self.first[token]:
                                trailer.update(self.first[token] - {None})
                            else:
                                trailer = self.first[token]
                        else:
                            trailer = {token}

        self.follow = follow_set


parser = Parser(
    ebnf=EBNF,
    start="<PROG>",
    terminal_list=TERMINAL_LIST,
    input_=[]  # TODO: add input
)
