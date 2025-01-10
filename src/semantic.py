from src.parser import Node, EMPTY_CHAR

class ScopeManager:
    def __init__(self, global_scope: dict[str, dict] = {}):
        self.scopes: list[dict[str, dict]] = [global_scope]

    def enter_scope(self, optional_variables: list[tuple[str, dict]] | None = None):
        print("Entering Scope:")
        self.scopes.append({})
        if optional_variables:
            for var in optional_variables:
                self.add_variable(*var)

    def exit_scope(self):
        if len(self.scopes) > 1:

            # Print current scope
            print("Exiting Scope:")
            print("{")
            for k, v in self.scopes[-1].items():
                print(f"{k}: {v}")
            print("}")

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
    

    def modify_variable(self, name: str, var_info: dict):
        for scope in reversed(self.scopes):
            if name in scope:
                current_var_info = scope[name]
                current_var_info.update(var_info)
                scope[name] = current_var_info
                return
        raise Exception(f"Variable '{name}' not declared")
    
    def add_or_modify_variable(self, name: str, var_info: dict):
        for scope in reversed(self.scopes):
            if name in scope:
                current_var_info = scope[name]
                current_var_info.update(var_info)
                scope[name] = current_var_info
                return
        self.scopes[-1][name] = var_info
    


class Semantic:
    symbol_table = {}

    def __init__(self):
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
                mVarDecls = m.children[7] # LVAR


                # OPARAMS
                mParams = m.children[4]

                self.symbol_table[cIdentifier]["methods"][mIdentifier] = {
                    "type": mType,
                    "params": {},
                    "variables": {}
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



                # Scan method body for local variables
                currentVarDecls = mVarDecls
                while currentVarDecls.children[0].token.type_ != EMPTY_CHAR:
                    # Visit variable declaration
                    v = currentVarDecls.children[0] # VAR
                    #Check if type is int []
                    vType = v.children[0].children[0].token.value
                    if vType == "int" and v.children[0].children[1].children[0].token.value == "[":
                        vType += "[]"

                    vIdentifier = v.children[1].token.value

                    self.symbol_table[cIdentifier]["methods"][mIdentifier]["variables"][vIdentifier] = {
                        "type": vType
                    }

                    currentVarDecls = currentVarDecls.children[1]

                

                currentMethodDecls = currentMethodDecls.children[1]

            # get next class
            currentClass = currentClass.children[1]
            # endregion

    def semantic_analysis(self, program: Node):
        if program.token.type_ != "<PROG>":
            raise Exception("Invalid program, first node must be <PROG>")
        
        # All classes with their variables and methods are now in the symbol table
        self.scan_declarations(program)
        scope_manager = ScopeManager(self.symbol_table)


        # region Semantic Analysis

        # Check classes methods for variables present in their scope
        currentClass = program.children[1]
        while currentClass.children[0].token.type_ != EMPTY_CHAR:
            # Visit class
            scope_manager.enter_scope()
            cls = currentClass.children[0]
            clsIdentifier = cls.children[1].token.value
            clsExtends = cls.children[2].children[1].token.value if cls.children[2].children[0].token.type_ != EMPTY_CHAR else None

            # Add to class scope all of its inherited variables and methods
            if clsExtends:
                try:
                    inherited = self.symbol_table[clsExtends]
                except Exception as e:
                    raise Exception(f"Class '{clsIdentifier}' is trying to extend undeclared class '{clsExtends}'") from e
                for k, v in inherited["variables"].items():
                    scope_manager.add_variable(k, v)
                for k, v in inherited["methods"].items():
                    scope_manager.add_variable(k, v)

            # Add to class scope all of its variables and methods
            for k, v in self.symbol_table[clsIdentifier]["variables"].items():
                scope_manager.add_or_modify_variable(k, v)
            for k, v in self.symbol_table[clsIdentifier]["methods"].items():
                scope_manager.add_or_modify_variable(k, v)


            currentMethod = cls.children[5] # LMETODO    
            while currentMethod.children[0].token.type_ != EMPTY_CHAR:
                # Visit method
                method = currentMethod.children[0] # METODO

                scope_manager.enter_scope() #* Entering method scope
                
                methodIdentifier = method.children[2].token.value

                # Add to method scope all of its parameters
                for k, v in self.symbol_table[clsIdentifier]["methods"][methodIdentifier]["params"].items():
                    scope_manager.add_variable(k, v)

                # Add to method scope all of its variables
                for k, v in self.symbol_table[clsIdentifier]["methods"][methodIdentifier]["variables"].items():
                    scope_manager.add_or_modify_variable(k, v)

                # Analyze its commands
                methodCmds = method.children[9] # LCMD

                scope_manager.enter_scope() #* Entering LCMD scope
                self.analyze_command(methodCmds, scope_manager)
                scope_manager.exit_scope() #* Exiting LCMD scope

                scope_manager.exit_scope() # *Exiting method scope
                currentMethod = currentMethod.children[1]
            
            scope_manager.exit_scope()
            currentClass = currentClass.children[1]

    def analyze_command(self, command: Node, scope_manager: ScopeManager):
        """
        Only checks if variables used are already declared.
        
        No type checking or value attribution is done here.
        
        Supports:
            CMD, LCMD, CMDELSE and CMDID
        """
        if command.token.type_ == "<CMD>":
            if command.children[0].token.value == "{":
                # CMD -> { LCMD }

                # Enter a new block scope
                scope_manager.enter_scope()
                # Analyze commands inside the block
                self.analyze_command(command.children[1], scope_manager)
                # Exit the block scope
                scope_manager.exit_scope()

            elif command.children[0].token.value == "if":
                # CMD -> if ( EXP ) { CMD } CMDELSE
                
                # Analyze expression inside if
                self.analyze_expression(command.children[2], scope_manager)
                # Analyze commands inside if scope
                scope_manager.enter_scope()
                self.analyze_command(command.children[5], scope_manager)
                scope_manager.exit_scope()
                # Analyze else commands
                self.analyze_command(command.children[6], scope_manager)

            elif command.children[0].token.value == "while":
                # CMD -> while ( EXP ) CMD
                
                # Analyze expression inside while
                self.analyze_expression(command.children[2], scope_manager)
                # Analyze commands inside while scope
                scope_manager.enter_scope()
                self.analyze_command(command.children[4], scope_manager)
                scope_manager.exit_scope()

            elif command.children[0].token.value == "System.out.println":
                # CMD -> System.out.println ( EXP ) ;

                # Analyze expression inside println
                self.analyze_expression(command.children[2], scope_manager)

            else:
                # CMD -> identifier CMDID
                
                # Check if identifier is a declared variable
                try:
                    scope_manager.get_variable(command.children[0].token.value)
                except Exception as e:
                    raise Exception(f"Variable '{command.children[0].token.value}' not declared") from e
                
                # Analyze CMDID
                self.analyze_command(command.children[1], scope_manager)



        elif command.token.type_ == "<LCMD>":
            # LCMD -> CMD LCMD
            # LCMD -> ε
            if command.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_command(command.children[0], scope_manager)
                self.analyze_command(command.children[1], scope_manager)

        elif command.token.type_ == "<CMDELSE>":
            # CMDELSE -> else { CMD }
            # CMDELSE -> ε
            if command.children[0].token.type_ != EMPTY_CHAR:
                scope_manager.enter_scope()
                self.analyze_command(command.children[2], scope_manager)
                scope_manager.exit_scope()

        elif command.token.type_ == "<CMDID>":
            # CMDID -> = EXP ; 
            # CMDID -> [ EXP ] = EXP ;
            if command.children[0].token.value == "=":
                # CMDID -> = EXP ;
                self.analyze_expression(command.children[1], scope_manager)
            elif command.children[0].token.value == "[":
                # CMDID -> [ EXP ] = EXP ;
                self.analyze_expression(command.children[1], scope_manager)
                self.analyze_expression(command.children[4], scope_manager)


        else:
            raise Exception("Invalid command node")
        
    def analyze_expression(self, expression: Node, scope_manager: ScopeManager):
        """
        Only checks if variables used are already declared.
        
        No type checking or value attribution is done here.
        
        Supports:
            EXP, EXP_, REXP, REXP_, AEXP, AEXP_, MEXP, MEXP_, SEXP
        """
        if expression.token.type_ == "<EXP>":
            # EXP -> REXP EXP_
            self.analyze_expression(expression.children[0], scope_manager)
            self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<EXP_>":
            # EXP_ -> && REXP EXP_
            # EXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)
                self.analyze_expression(expression.children[2], scope_manager)

        elif expression.token.type_ == "<REXP>":
            # REXP -> AEXP REXP_
            self.analyze_expression(expression.children[0], scope_manager)
            self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<REXP_>":
            # REXP_ -> < AEXP REXP_
            # REXP_ -> == AEXP REXP_
            # REXP_ -> != AEXP REXP_
            # REXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)
                self.analyze_expression(expression.children[2], scope_manager)

        elif expression.token.type_ == "<AEXP>":
            # AEXP -> MEXP AEXP_
            self.analyze_expression(expression.children[0], scope_manager)
            self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<AEXP_>":
            # AEXP_ -> + MEXP AEXP_
            # AEXP_ -> - MEXP AEXP_
            # AEXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)
                self.analyze_expression(expression.children[2], scope_manager)

        elif expression.token.type_ == "<MEXP>":
            # MEXP -> SEXP MEXP_
            self.analyze_expression(expression.children[0], scope_manager)
            self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<MEXP_>":
            # MEXP_ -> * SEXP MEXP_
            # MEXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)
                self.analyze_expression(expression.children[2], scope_manager)

        elif expression.token.type_ == "<SEXP>":
            # SEXP -> ! SEXP
            # SEXP -> - SEXP
            # SEXP -> true
            # SEXP -> false
            # SEXP -> number
            # SEXP -> null
            # SEXP -> new NEWEXP
            # SEXP -> PEXP SPEXP
            
            if expression.children[0].token.type_ == "!":
                self.analyze_expression(expression.children[1], scope_manager)
            elif expression.children[0].token.type_ == "-":
                self.analyze_expression(expression.children[1], scope_manager)
            elif expression.children[0].token.type_ == "new":
                self.analyze_expression(expression.children[1], scope_manager)
            elif expression.children[0].token.type_ == "<PEXP>":
                scope_manager.enter_scope()
                self.analyze_expression(expression.children[0], scope_manager)
                self.analyze_expression(expression.children[1], scope_manager)
                scope_manager.exit_scope()


        elif expression.token.type_ == "<PEXP>":
            # PEXP -> identifier
            # PEXP -> this
            # PEXP -> ( EXP )
            if expression.children[0].token.type_ == "identifier":
                try:
                    variable_name = expression.children[0].token.value
                    variable_info = scope_manager.get_variable(variable_name)

                    # Get attributes and methods of the variable if its a class
                    if variable_info["type"] == "class":
                        # Add class attributes and methods to the current scope
                        for k, v in variable_info["variables"].items():
                            scope_manager.add_variable(k, v)
                        for k, v in variable_info["methods"].items():
                            scope_manager.add_variable(k, v)

                    #! TODO Implementar a ideia de abrir um escopo em SEXP, adicionar os atributos e metodos da classe em PEXP e fechar quando sair de SEXP


                except Exception as e:
                    raise Exception(f"Variable '{expression.children[0].token.value}' not declared") from e
            elif expression.children[0].token.type_ == "this":
                pass
            elif expression.children[0].token.type_ == "(":
                self.analyze_expression(expression.children[1], scope_manager)
        
        elif expression.token.type_ == "<SPEXP>":
            # SPEXP -> . SPEXP_
                # Esse caso é o de chamar um método e passar os parâmetros ou pegar o length 
            # SPEXP -> [ EXP ]
                # Esse caso é o de acessar um elemento de um array
            # SPEXP -> ε
            if expression.children[0].token.type_ == ".":
                scope_manager.enter_scope()
                self.analyze_expression(expression.children[1], scope_manager) # SPEXP_
                scope_manager.exit_scope()
            elif expression.children[0].token.type_ == "[":
                self.analyze_expression(expression.children[1], scope_manager)


        elif expression.token.type_ == "<SPEXP_>":
            # SPEXP_ -> identifier SPEXP__ SPEXP
            # SPEXP_ -> length
            if expression.children[0].token.type_ == "identifier":
                try:
                    variable_name = expression.children[0].token.value
                    scope_manager.get_variable(variable_name)

                    # Get attributes and methods of the variable if its a class
                    if variable_info["type"] == "class":
                        # Add class attributes and methods to the current scope
                        for k, v in variable_info["variables"].items():
                            scope_manager.add_variable(k, v)
                        for k, v in variable_info["methods"].items():
                            scope_manager.add_variable(k, v)

                except Exception as e:
                    raise Exception(f"Variable '{expression.children[0].token.value}' not declared") from e
                self.analyze_expression(expression.children[1], scope_manager)
                self.analyze_expression(expression.children[2], scope_manager)
            elif expression.children[0].token.value == "length":
                pass

        elif expression.token.type_ == "<SPEXP__>":
            # SPEXP__ -> ( OEXPS )
                # ! Extra de verificar os parametros passados para a chamada de métodos
            # SPEXP__ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<OEXPS>":
            # OEXPS -> EXPS
            # OEXPS -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[0], scope_manager)

        elif expression.token.type_ == "<EXPS>":
            # EXPS -> EXP EXPS_
            self.analyze_expression(expression.children[0], scope_manager)
            self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<EXPS_>":
            # EXPS_ -> , EXPS
            # EXPS_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager)

        elif expression.token.type_ == "<NEWEXP>":
            # NEWEXP -> identifier ( ) SPEXP
            # NEWEXP -> int [ EXP ]
            if expression.children[0].token.type_ == "identifier":
                try:
                    scope_manager.get_variable(expression.children[0].token.value)
                except Exception as e:
                    raise Exception(f"Variable '{expression.children[0].token.value}' not declared") from e
                self.analyze_expression(expression.children[3], scope_manager)
            elif expression.children[0].token.value == "int":
                self.analyze_expression(expression.children[2], scope_manager)

        else:
            raise Exception("Invalid expression node")


def get_symbol_table(ast: Node):
    sem = Semantic()
    sem.scan_declarations(ast)
    return sem.symbol_table

def analyze_semantics(ast: Node):
    sem = Semantic()
    sem.semantic_analysis(ast)
    return sem.symbol_table