import csv
import json
import pandas as pd
from Gramatica import getGrammar, getTerminalList

EBNF = getGrammar()
TERMINAL_LIST = getTerminalList()

BASE_CHAR = "$"


# EBNF = {
#     "<EXP>": [
#         ["<TERM>", "<EXP_>"]
#     ],
#     "<EXP_>": [
#         ["<ADDOP>", "<TERM>", "<EXP_>"],
#         []
#     ],
#     "<ADDOP>": [
#         ["+"],
#         ["-"]
#     ],
#     "<TERM>": [
#         ["<FACTOR>", "<TERM_>"]
#     ],
#     "<TERM_>": [
#         ["<MULOP>", "<FACTOR>", "<TERM_>"],
#         []
#     ],
#     "<MULOP>": [
#         ["*"],
#     ],
#     "<FACTOR>": [
#         ["(", "<EXP>", ")"],
#         ["number"]
#     ]
# }
# TERMINAL_LIST = {
#     "+", "-", "*", "(", ")", "number"
# }



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
    # Parsing table with non-terminals as rows and terminals as columns
    # Each cell contains a list of tuples containing the non-terminal and the production
    table: dict[str, dict[str, list[
        tuple[str, list[str]]
    ]]]

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

        self.table = table


class Token:
    type_: str
    value: str

    def __init__(self, value: str, type_: str) -> None:
        self.type_ = type_
        self.value = value

    def __repr__(self) -> str:
        return f"Token({self.type_}, {self.value})"


parser = Parser(
    ebnf=EBNF,
    start=EBNF.keys().__iter__().__next__(),
    terminal_list=TERMINAL_LIST,
    input_=[]  # TODO: add input
)

# Read output.txt that has value | type format and create a list of tokens
with open("output.txt", "r") as f:
    reader = csv.reader(f, delimiter="|")
    token_list = [Token(value.strip(), type_.strip())
                  for value, type_ in reader]
    

# If any cell of the table has more than one production, the grammar is not LL(1)
# Print which cells have more than one production
for non_terminal, row in parser.table.items():
    for terminal, productions in row.items():
        if len(productions) > 1:
            print(
                f"Cell [{non_terminal}, {terminal}] has more than one production: {productions}")


# Write parser.table to an excel file with non-terminal as rows, terminals as columns, and productions as values
# Convert the parsing table to a DataFrame
df = pd.DataFrame(parser.table).T

# Map the table values to a string representation
df = df.map(lambda cell: ', '.join(
    [f"{nt} -> {' '.join(prod)}" for nt, prod in cell]))

# Write the DataFrame to an Excel file
df.to_excel("parsing_table.xlsx", index=True)


# Write the first and follow sets to a json file
with open("first_set.json", "w") as f:
    json.dump({k: list(v) for k, v in parser.first.items()}, f, indent=4)

with open("follow_set.json", "w") as f:
    json.dump({k: list(v) for k, v in parser.follow.items()}, f, indent=4)
