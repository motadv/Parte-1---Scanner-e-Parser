import json
import pandas as pd

import anytree as at
import anytree.exporter as exporter
import subprocess

from src.options import Options


BASE_CHAR = "$"
EMPTY_CHAR = "ε"


class Token:
    type_: str
    value: str

    def __init__(self, value: str, type_: str) -> None:
        self.type_ = type_
        self.value = value

    def __repr__(self) -> str:
        if self.type_ == self.value:
            return f"{self.value}"
        return f"{self.type_}, {self.value}"


class Node:
    token: Token
    children: list
    result: str | None

    def __init__(self, token: Token, children=None):
        self.token = token
        if children is None:
            children = []
        self.children = children

    def __repr__(self) -> str:
        return f"{self.token}"

    def to_tree(self, level: int = 0):
        text = "\t" * level + self.__repr__()
        for child in self.children:
            text += "\n" + child.to_tree(level + 1)
        return text





class Parser:
    ebnf: dict[str, list[list[str]]]
    first: dict[str, set[str | None]]
    follow: dict[str, set[str | None]]
    input_: list[Token]
    parser: list[str]
    start: str
    terminal_list: set[str]
    # Parsing table with non-terminals as rows and terminals as columns
    # Each cell contains a list of tuples containing the non-terminal and the production
    table: dict[str, dict[str, list[
        tuple[str, list[str]]
    ]]]

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

        self.input_ = [*input_, Token(BASE_CHAR, BASE_CHAR)]
        self.parser = [self.start, Token(BASE_CHAR, BASE_CHAR)]

        self.create_first()
        self.create_follow()
        self.create_table()
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

            # If the current token does not derive εpsilon, stop
            if None not in self.first[token]:
                break
        else:
            # If all tokens derive εpsilon, add εpsilon (None) to the result
            result.add(None)

        return result

    def create_follow(self) -> None:
        """
        Creates the *Follow* set for each non-terminal token in the EBNF.
        """

        follow_set = {token: set() for token in self.ebnf.keys()}
        # The start token always follows the base character.
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
                    # trailer = follow_set[non_terminal].copy()
                    # trailer = follow_set[non_terminal].copy()

                    # for token in reversed(production):
                    #     if token in self.ebnf:
                    #         changed |= add_to_follow(token, trailer)

                    #         if None in self.first[token]:
                    #             trailer.update(self.first[token] - {None})
                    #         else:
                    #             trailer = self.first[token]
                    #     else:
                    #         trailer = {token}

                    for i, token in enumerate(production):
                        if token in self.ebnf:
                            # Add the first of the next token to the follow of the current token
                            # except for epsilon
                            if i < len(production) - 1:
                                subset = self.subset_first(production[i + 1:])
                                
                                changed |= add_to_follow(
                                    token, self.subset_first(
                                        production[i + 1:]) - {None}
                                )
                                
                                # if("else" in subset) and (token == "<CMDELSE>"):
                                #     print(f"    Else adicionado ao follow de {token} porque else esta no first de {production[i + 1:]}")
                                #     print(f"        Caso encontrado analisando as produções de {non_terminal}")
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
                        if (A_alpha not in table[A][a]):
                            table[A][a].append(
                                A_alpha)

        # Create error detection for table
        # Iterate through each cell for each row and check if there are no productions
        # If thats the case, if the colum is in the follow set of the row or if its the BASECHAR column, add a DESEMPILHA
        # If the column is not BASECHAR nor in the follow set, add an AVANÇA
        for non_terminal, row in table.items():
            for terminal, productions in row.items():
                if len(productions) == 0:
                    if terminal in self.follow[non_terminal] or terminal == BASE_CHAR:
                        table[non_terminal][terminal].append(("ERROR", ["DESEMPILHA"]))
                    else:
                        table[non_terminal][terminal].append(("ERROR", ["AVANÇA"]))

        self.table = table

    def read(self, level: int = 0, add_to_graph: bool = True) -> Node:
        """
        Creates the parsing tree by reading the input and the parser stacks.
        """
        current_parser = self.parser.pop(0)
        current_input = self.input_[0].type_
        current_value = self.input_[0].value

        # If symbol is the stack base
        if current_parser == BASE_CHAR:
            if current_input == BASE_CHAR:
                return Node(Token("Finished parsing", "SUCCESS"))
            else:
                return Node(Token("Input not fully consumed", "ERROR"))

        # If symbol is terminal
        if current_parser in self.terminal_list:
            # If symbol matches input
            if current_parser == current_input:
                self.input_.pop(0)
                if current_value == current_input:
                    return Node(Token(current_value, current_parser))
                return Node(Token(current_value, current_parser))
            else:
                # Avança
                node = Node(Token(current_parser, current_parser))
                self.parser.insert(0, current_parser)
                self.input_.pop(0)
                child = Node(Token(current_value, "AVANÇA"))
                child.children = [self.read(level + 1, False)]
                node.children = [child]
                if not add_to_graph:
                    node = child
                return node

        # If symbol is non-terminal
        if current_parser in self.ebnf:
            derivations = self.table[current_parser][current_input]

            # If EBNF is not LL(1)
            if len(derivations) > 1:
                return Node(Token(f"Multiple derivations of '{current_parser}' for input '{current_input}'", "ERROR"))

            if not derivations:
                return Node(Token(f"No production for '{current_parser}' with input '{current_input}'", "ERROR"))

            if derivations[0][0] == "ERROR":
                node = Node(Token(current_parser, current_parser))
                child = Node(Token("", ""))
                if derivations[0][1][0] == "DESEMPILHA":
                    child = Node(Token(f"DESEMPILHA", "DESEMPILHA"))
                elif derivations[0][1][0] == "AVANÇA":
                    self.parser.insert(0, current_parser)
                    self.input_.pop(0)
                    child = Node(Token(current_value, "AVANÇA"))
                    child.children = [self.read(level + 1, False)]
                else:
                    child = Node(Token(f"UNKNOWN ERROR: {derivations[0][1]}", "ERROR"))
                node.children = [child]
                if not add_to_graph:
                    node = child
                return node

            production = derivations[0][1]
            self.parser = production + self.parser

            # Create non-terminal node
            node = Node(Token(current_parser, current_parser))
            node.children = [self.read(level + 1) for _ in production]

            # If production is epsilon, return epsilon node
            if len(production) == 0:
                node.children = [Node(Token(EMPTY_CHAR, EMPTY_CHAR))]

            return node

        return Node(Token(f"UNKNOWN SYMBOL: '{current_parser}'", "ERROR"))


def create_graph(node: Node, parent: Node = None) -> at.Node:
    graph_node = at.Node(node, parent)
    type_ = node.token.type_
    if type_ in ["AVANÇA", "DESEMPILHA"]:
        graph_node.color = "yellow"
    elif type_ == "ERROR":
        graph_node.color = "red"
    elif type_ in ["<EXP>","<REXP>", "<AEXP>", "<MEXP>", "<SEXP>", "<PEXP>", "<SPEXP>", "<SPEXP_>", "<SPEXP__>", "<OEXPS>", "<EXPS>", "<EXPS_>", "<NEWEXP>"]:
        graph_node.color = "lightblue"
    elif type_ in ["number", "true", "false", "null"]:
        graph_node.color = "lightgreen"
    elif type_ in ["identifier", "this"]:
        graph_node.color = "orange"
    else:
        graph_node.color = "white"

    for child in node.children:
        create_graph(child, graph_node)
    return graph_node


def node_attr(node: at.Node) -> str:
    return f'label="{node.name}" fillcolor="{node.color}" style="filled"'


def check_duplicate(parser: Parser) -> None:
    for non_terminal, row in parser.table.items():
        for terminal, productions in row.items():
            if len(productions) > 1:
                print(f"Cell [{non_terminal}, {terminal}] has more than one production: {productions}")


def parse(
        options: Options,
        ebnf: dict[str, list[list[str]]],
        terminal_list: set[str]
) -> Node:
    with open(f"{options.files_dir}scan.txt", "r") as f:
        tokens = [Token(*line.strip().split(" | ")) for line in f]

    parser = Parser(
        ebnf=ebnf,
        start=ebnf.keys().__iter__().__next__(),
        terminal_list=terminal_list,
        input_=tokens
    )

    result = parser.read()

    # Create graph
    graph = create_graph(result)
    for pre, fill, node in at.RenderTree(graph):
        print("%s%s" % (pre, node.name))

    if options.graph:
        exporter.UniqueDotExporter(graph, nodeattrfunc=node_attr).to_dotfile(f"{options.files_dir}parsing_tree.dot")
        subprocess.run(
            ["dot", f"{options.files_dir}parsing_tree.dot", "-Tpdf", "-o", f"{options.files_dir}parsing_tree.pdf"],
            check=True
        )

    if options.m_table:
        df = pd.DataFrame(parser.table).T
        df = df.map(lambda cell: ', '.join(
            [f"{nt} -> {' '.join(prod)}" for nt, prod in cell]))
        df.to_excel(f"{options.files_dir}parsing_table.xlsx", index=True)

    if options.sets:
        with open(f"{options.files_dir}first_set.json", "w") as f:
            json.dump({k: list(v) for k, v in parser.first.items()}, f, indent=4)
        with open(f"{options.files_dir}follow_set.json", "w") as f:
            json.dump({k: list(v) for k, v in parser.follow.items()}, f, indent=4)


    return result