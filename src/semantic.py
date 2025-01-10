from parser import Node, EMPTY_CHAR

class ScopeManager:
    def __init__(self):
        self.scopes: list[dict[str, dict]] = [{}]

    def enter_scope(self, optional_variables: list[tuple[str, dict]] | None = None):
        self.scopes.append({})
        if optional_variables:
            for var in optional_variables:
                self.add_variable(*var)

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
        else:
            raise Exception("Cannot exit the global scope")
        
    def add_variable(self, name: str, var_info: dict):
        if name in self.scopes[-1]:
            raise Exception(f"Variable '{name}' already declared in this scope")
        self.scopes[-1][name] = var_info

    def get_variable(self, name: str):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise Exception(f"Variable '{name}' not declared")
    


class Semantic:
    scope_manager = ScopeManager()
    symbol_table = {}

    def __init__(self):
        self.scope_manager = ScopeManager()
        self.symbol_table = {}

    def scan_declarations(self, program: Node):
        if program.token.type_ != "<PROG>":
            raise Exception("Invalid program")
        
        # region Scan Class declarations
        currentClass = program.children[1]
        while currentClass.children[0].token.type_ != EMPTY_CHAR:
            # Visit class
            c = currentClass.children[0]
            cIdentifier = c.children[1].token.value
            cExtends = c.children[2].children[1].token.value if c.children[2].children[0].token.type_ != EMPTY_CHAR else None
            
            cVarDecls = c.children[4]
            cMethodDecls = c.children[5]

            self.symbol_table[cIdentifier] = {
                "type": "class",
                "extends": cExtends,
                "variables": {},
                "methods": {}
            }

            # Scan variable declarations
            currentVarDecls = cVarDecls
            while currentVarDecls.children[0].token.type_ != EMPTY_CHAR:
                # Visit variable declaration
                v = currentVarDecls.children[0]
                #Check if type is int []
                vType = v.children[0].children[0].token.value
                if vType == "int" and v.children[0].children[1].children[0].token.value == "[":
                    vType += "[]"

                vIdentifier = v.children[1].token.value

                self.symbol_table[cIdentifier]["variables"][vIdentifier] = {
                    "type": vType
                }

                currentVarDecls = currentVarDecls.children[1]
            
            # Scan method declarations
            currentMethodDecls = cMethodDecls
            # while this LMETODO dont derive epsilon
            while currentMethodDecls.children[0].token.type_ != EMPTY_CHAR:
                # Visit method declaration
                m = currentMethodDecls.children[0]
                mType = m.children[1].children[0].token.value
                if mType == "int" and m.children[1].children[1].children[0].token.value == "[": # Check if type is int []
                    mType += "[]"

                mIdentifier = m.children[2].token.value

                # OPARAMS
                mParams = m.children[4]

                self.symbol_table[cIdentifier]["methods"][mIdentifier] = {
                    "type": mType,
                    "params": {},
                }

                # Scan method params
                if mParams.children[0].token.type_ != EMPTY_CHAR:
                    currentParams = mParams.children[0] #PARAMS
                    # At this point we have at least one param
                    # Extract first param
                    pType = currentParams.children[0].children[0].token.value
                    if pType == "int" and currentParams.children[0].children[1].children[0].token.value == "[":
                        pType += "[]"

                    pIdentifier = currentParams.children[1].token.value

                    self.symbol_table[cIdentifier]["methods"][mIdentifier]["params"][pIdentifier] = {
                        "type": pType
                    }

                    # Extract next params
                    currentParams = currentParams.children[2] # PARAMS_
                    # while this PARAMS_ dont derive epsilon
                    while currentParams.children[0].token.type_ != EMPTY_CHAR:
                        pType = currentParams.children[1].children[0].token.value
                        if pType == "int" and currentParams.children[1].children[1].children[0].token.value == "[":
                            pType += "[]"

                        pIdentifier = currentParams.children[2].token.value

                        self.symbol_table[cIdentifier]["methods"][mIdentifier]["params"][pIdentifier] = {
                            "type": pType
                        }

                        currentParams = currentParams.children[3]

                

                currentMethodDecls = currentMethodDecls.children[1]

            # get next class
            currentClass = currentClass.children[1]
            # endregion



def get_symbol_table(ast: Node):
    sem = Semantic()
    sem.scan_declarations(ast)
    return sem.symbol_table


