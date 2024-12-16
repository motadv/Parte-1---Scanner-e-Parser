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
        ["public", "<TIPO>", "identifier", "(", "<OPARAMS>", ")", "{", "<LVAR>", "{", "<LCMD>", "}", "return", "<EXP>", ";",
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
        ["if", "(", "<EXP>", ")", "{", "<CMD>", "}", "<CMDELSE>"],
        ["while", "(", "<EXP>", ")", "<CMD>"],
        ["System.out.println", "(", "<EXP>", ")", ";"],
        ["identifier", "<CMDID>"]
    ],
    "<CMDELSE>": [
        ["else", "{", "<CMD>", "}"],
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
        ["<PEXP>", "<SPEXP>"]
    ],
    "<PEXP>": [
        ["identifier"],
        ["this"],
        ["(", "<EXP>", ")"]
    ],
    "<SPEXP>": [
        [".", "<SPEXP_>"],
        ["[", "<EXP>", "]"],
        []
    ],
    "<SPEXP_>": [
        ["identifier", "<SPEXP__>", "<SPEXP>"],
        ["length"],
    ],
    "<SPEXP__>": [
        ["(", "<OEXPS>", ")"],
        []
    ],
    "<NEWEXP>": [
        ["identifier", "(", ")", "<SPEXP>"],
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


# Export the grammar and the terminal list
def get_grammar():
    return EBNF


def get_terminal_list():
    return TERMINAL_LIST
