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

            # Toda classe deve ter em seu escopo de variaveis o atributo 'this' que é do tipo da própria classe
            self.symbol_table[cIdentifier]["variables"]["this"] = {
                "type": cIdentifier
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
        
        valid_types = ["int", "boolean", "int[]", *[k for k in self.symbol_table.keys()]]

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
                    # Check if type is valid
                    if v["type"] not in valid_types:
                        raise Exception(f"Invalid type '{v['type']}' in inherited variable '{k}'")
                    scope_manager.add_variable(k, v)
                for k, v in inherited["methods"].items():
                    # Check if type is valid
                    if v["type"] not in valid_types:
                        raise Exception(f"Invalid type '{v['type']}' in inherited method '{k}'")
                    scope_manager.add_variable(k, v)

            # Add to class scope all of its variables and methods
            for k, v in self.symbol_table[clsIdentifier]["variables"].items():
                # Check if type is valid
                if v["type"] not in valid_types:
                    raise Exception(f"Invalid type '{v['type']}' in variable '{k}'")
                scope_manager.add_or_modify_variable(k, v)
            for k, v in self.symbol_table[clsIdentifier]["methods"].items():
                # Check if type is valid
                if v["type"] not in valid_types:
                    raise Exception(f"Invalid type '{v['type']}' in method '{k}'")
                scope_manager.add_or_modify_variable(k, v)


            currentMethod = cls.children[5] # LMETODO    
            while currentMethod.children[0].token.type_ != EMPTY_CHAR:
                # Visit method
                method = currentMethod.children[0] # METODO

                scope_manager.enter_scope() #* Entering method scope
                
                methodIdentifier = method.children[2].token.value

                # Add to method scope all of its parameters
                for k, v in self.symbol_table[clsIdentifier]["methods"][methodIdentifier]["params"].items():
                    # Check if type is valid
                    if v["type"] not in valid_types:
                        raise Exception(f"Invalid type '{v['type']}' in parameter '{k}'")
                    scope_manager.add_variable(k, v)

                # Add to method scope all of its variables
                for k, v in self.symbol_table[clsIdentifier]["methods"][methodIdentifier]["variables"].items():
                    # Check if type is valid
                    if v["type"] not in valid_types:
                        raise Exception(f"Invalid type '{v['type']}' in variable '{k}'")
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
                self.analyze_expression(command.children[2], scope_manager) # EXP
                # Analyze commands inside while scope
                scope_manager.enter_scope()
                self.analyze_command(command.children[4], scope_manager) # CMD
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
        
    def analyze_expression(self, expression: Node, scope_manager: ScopeManager, other_data = None):
        """
        """
        if expression.token.type_ == "<EXP>":
            # EXP -> REXP EXP_
            # Retornamos o tipo e substituímos o valor e tipo do nó atual para pré calcular expressões entre constantes
            
            resultado_rexp = self.analyze_expression(expression.children[0], scope_manager) # REXP
            resultado_exp_ = self.analyze_expression(expression.children[1], scope_manager) # EXP_

            if resultado_exp_:
                if resultado_exp.get("has_identifier", False) or resultado_rexp.get("has_identifier", False):
                    return {
                        "type": "boolean",
                        "value": None,
                        "has_identifier": True
                    }
                else:
                    return {
                        "type": "boolean",
                        "value": resultado_rexp["value"] and resultado_exp_["value"]
                    }
            
            return resultado_rexp


        elif expression.token.type_ == "<EXP_>":
            # EXP_ -> && REXP EXP_
            # EXP_ -> ε

            if expression.children[0].token.type_ != EMPTY_CHAR:
                resultado_rexp = self.analyze_expression(expression.children[1], scope_manager) # REXP
                resultado_exp_ = self.analyze_expression(expression.children[2], scope_manager) # EXP_

                if resultado_exp_:
                    if resultado_exp.get("has_identifier", False) or resultado_rexp.get("has_identifier", False):
                        return {
                            "type": "boolean",
                            "value": None,
                            "has_identifier": True
                        }
                        
                    else:
                        return {
                            "type": "boolean",
                            "value": resultado_rexp["value"] and resultado_exp_["value"]
                        }
                
                return resultado_rexp
                
            else:
                return None

        elif expression.token.type_ == "<REXP>":
            # REXP -> AEXP REXP_
            resultado_aexp = self.analyze_expression(expression.children[0], scope_manager) # AEXP
            resultado_rexp_ = self.analyze_expression(expression.children[1], scope_manager) # REXP_

            # resultado_rexp_ é None ou um dicionário com o tipo, valor e operador da expressão
            if resultado_rexp_:
                if resultado_rexp.get("has_identifier", False) or resultado_aexp.get("has_identifier", False):
                    return {
                        "type": "boolean",
                        "value": None,
                        "has_identifier": True
                    }
                
                
                if resultado_rexp_["operator"] == "<":
                    return {
                        "type": "boolean",
                        "value": resultado_aexp["value"] < resultado_rexp_["value"]
                    }
                elif resultado_rexp_["operator"] == "==":
                    return {
                        "type": "boolean",
                        "value": resultado_aexp["value"] == resultado_rexp_["value"]
                    }
                elif resultado_rexp_["operator"] == "!=":
                    return {
                        "type": "boolean",
                        "value": resultado_aexp["value"] != resultado_rexp_["value"]
                    }
                
            return resultado_aexp

        elif expression.token.type_ == "<REXP_>":
            # REXP_ -> < AEXP REXP_
            # REXP_ -> == AEXP REXP_
            # REXP_ -> != AEXP REXP_
            # REXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                resultado_aexp = self.analyze_expression(expression.children[1], scope_manager) # AEXP
                resultado_rexp_ = self.analyze_expression(expression.children[2], scope_manager) # REXP_

                this_operator = expression.children[0].token.value

                if resultado_rexp_:
                    if resultado_rexp.get("has_identifier", False) or resultado_aexp.get("has_identifier", False):
                        return {
                            "type": "boolean",
                            "value": None,
                            "has_identifier": True,
                            "operator": this_operator
                        }
                        
                    if resultado_rexp_["operator"] == "<":
                        return {
                            "type": "boolean",
                            "value": resultado_aexp["value"] < resultado_rexp_["value"],
                            "operator": this_operator
                        }
                    elif resultado_rexp_["operator"] == "==":
                        return {
                            "type": "boolean",
                            "value": resultado_aexp["value"] == resultado_rexp_["value"],
                            "operator": this_operator
                        }
                    elif resultado_rexp_["operator"] == "!=":
                        return {
                            "type": "boolean",
                            "value": resultado_aexp["value"] != resultado_rexp_["value"],
                            "operator": this_operator
                        }
                    
                return resultado_aexp
            else:
                return None

        elif expression.token.type_ == "<AEXP>":
            # AEXP -> MEXP AEXP_
            resultado_mexp = self.analyze_expression(expression.children[0], scope_manager) # MEXP
            resultado_aexp_ = self.analyze_expression(expression.children[1], scope_manager) # AEXP_

            if resultado_aexp_:
                if resultado_aexp_.get("has_identifier", False) or resultado_mexp.get("has_identifier", False):
                    return {
                        "type": "int",
                        "value": None,
                        "has_identifier": True
                    }
                
                if resultado_aexp_["operator"] == "+":
                    return {
                        "type": "int",
                        "value": resultado_mexp["value"] + resultado_aexp_["value"]
                    }
                elif resultado_aexp_["operator"] == "-":
                    return {
                        "type": "int",
                        "value": resultado_mexp["value"] - resultado_aexp_["value"]
                    }
                
            return resultado_mexp

        elif expression.token.type_ == "<AEXP_>":
            # AEXP_ -> + MEXP AEXP_
            # AEXP_ -> - MEXP AEXP_
            # AEXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                resultado_mexp  = self.analyze_expression(expression.children[1], scope_manager) # MEXP
                resultado_aexp_  = self.analyze_expression(expression.children[2], scope_manager) # AEXP_

                this_operator = expression.children[0].token.value

                if resultado_aexp_:
                    if resultado_aexp_.get("has_identifier", False) or resultado_mexp.get("has_identifier", False):
                        return {
                            "type": "int",
                            "value": None,
                            "has_identifier": True,
                            "operator": this_operator
                        }
                    if resultado_aexp_["operator"] == "+":
                        return {
                            "type": "int",
                            "value": resultado_mexp["value"] + resultado_aexp_["value"],
                            "operator": this_operator
                        }
                    elif resultado_aexp_["operator"] == "-":
                        return {
                            "type": "int",
                            "value": resultado_mexp["value"] - resultado_aexp_["value"],
                            "operator": this_operator
                        }
                
                return {
                    "type": "int",
                    "value": resultado_mexp["value"],
                    "operator": this_operator
                }

            else:
                return None

        elif expression.token.type_ == "<MEXP>":
            # MEXP -> SEXP MEXP_
            resultado_sexp = self.analyze_expression(expression.children[0], scope_manager) # SEXP
            resultado_mexp_ = self.analyze_expression(expression.children[1], scope_manager) # MEXP_

            if resultado_mexp_:
                if resultado_mexp_.get("has_identifier", False) or resultado_sexp.get("has_identifier", False):
                    return {
                        "type": "int",
                        "value": None,
                        "has_identifier": True
                    }
                if resultado_mexp_["operator"] == "*":
                    return {
                        "type": "int",
                        "value": resultado_sexp["value"] * resultado_mexp_["value"]
                    }
                
            return resultado_sexp

        elif expression.token.type_ == "<MEXP_>":
            # MEXP_ -> * SEXP MEXP_
            # MEXP_ -> ε
            if expression.children[0].token.type_ != EMPTY_CHAR:
                resultado_sexp = self.analyze_expression(expression.children[1], scope_manager) # SEXP
                resultado_mexp_ = self.analyze_expression(expression.children[2], scope_manager) # MEXP_

                if resultado_mexp_:
                    if resultado_mexp_.get("has_identifier", False) or resultado_sexp.get("has_identifier", False):
                        return {
                            "type": "int",
                            "value": None,
                            "has_identifier": True
                        }
                    if resultado_mexp_["operator"] == "*":
                        return {
                            "type": "int",
                            "value": resultado_sexp["value"] * resultado_mexp_["value"],
                            "operator": "*"                            
                        }
                    
                return {
                    "type": "int",
                    "value": resultado_sexp["value"],
                    "operator": "*"
                }
            else:
                return None

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
                resultado_sexp = self.analyze_expression(expression.children[1], scope_manager) # SEXP
                if resultado_sexp.get("has_identifier", False):
                    return {
                        "type": "boolean",
                        "value": None,
                        "has_identifier": True
                    }
                    
                return {
                    "type": "boolean",
                    "value": not resultado_sexp["value"]
                }
                
            elif expression.children[0].token.type_ == "-":
                resultado_sexp = self.analyze_expression(expression.children[1], scope_manager) # SEXP
                if resultado_sexp.get("has_identifier", False):
                    return {
                        "type": "int",
                        "value": None,
                        "has_identifier": True
                    }
                return {
                    "type": "int",
                    "value": -resultado_sexp["value"]
                }
            
            elif expression.children[0].token.type_ == "true":
                return {
                    "type": "boolean",
                    "value": True
                }
                
            elif expression.children[0].token.type_ == "false":
                return {
                    "type": "boolean",
                    "value": False
                }
                
            elif expression.children[0].token.type_ == "number":
                return {
                    "type": "int",
                    "value": int(expression.children[0].token.value)
                }
                
            elif expression.children[0].token.type_ == "null":
                return {
                    "type": "null",
                    "value": None
                }
            
            elif expression.children[0].token.type_ == "new":
                resultado_newexp = self.analyze_expression(expression.children[1], scope_manager) # NEWEXP
                # Resultado de NEWEXP é um dicionário com o tipo e valor do objeto instanciado e sempre tem has_identifier = True
                return resultado_newexp
             
            elif expression.children[0].token.type_ == "<PEXP>":   
                # Em um caso como id.attr, é preciso checar se o attr chamado faz parte da classe do id
                # em um caso como id.metodo(), é preciso checar se o método existe e se os parâmetros passados são válidos
                
                # PEXP é um identificador, this ou uma expressão entre parênteses
                resultado_pexp = self.analyze_expression(expression.children[0], scope_manager) # PEXP
                resultado_spexp = self.analyze_expression(expression.children[1], scope_manager, resultado_pexp["type"]) # SPEXP

                if resultado_spexp:
                    return resultado_spexp

                return resultado_pexp

        elif expression.token.type_ == "<PEXP>":
            # PEXP -> identifier
            # PEXP -> this
            # PEXP -> ( EXP )
            if expression.children[0].token.type_ == "identifier":
                # Should return the identifier type so that SPEXP can check if the attribute or method exists
                # Should not return types for pre-calculation if dealing with non-constant values
                try:
                    variable_name = expression.children[0].token.value
                    variable_info = scope_manager.get_variable(variable_name)

                    return {
                        "type": variable_info["type"],
                        "value": None,
                        "has_identifier": True
                    }
                except Exception as e:
                    raise Exception(f"Variable '{expression.children[0].token.value}' not declared") from e
            
            elif expression.children[0].token.type_ == "this":
                # 'this' is always of the same type as the current class
                # We are already adding 'this' to the class scope in the scan_declarations method
                try:
                    variable_info = scope_manager.get_variable("this")
                    return {
                        "type": variable_info["type"],
                        "value": None,
                        "has_identifier": True
                    }

                except Exception as e:
                    raise Exception(f"Variable 'this' not accessible.") from e

            elif expression.children[0].token.type_ == "(":
                resultado_exp = self.analyze_expression(expression.children[1], scope_manager) # EXP
                return resultado_exp
        
        elif expression.token.type_ == "<SPEXP>":
            # SPEXP -> . SPEXP_
                # Esse caso é o de chamar um método e passar os parâmetros ou pegar o length 
            # SPEXP -> [ EXP ]
                # Esse caso é o de acessar um elemento de um array
            # SPEXP -> ε

            # SPEXP só existe após um PEXP ou ao final de SPEXP_
            #  então o other_data é o tipo do simbolo anterior
            current_type = other_data
            if expression.children[0].token.type_ == ".":

                # Passar para o SPEXP_ o tipo da variável atual para que ele possa verificar se o método ou atributo existe
                resultado_spexp_ = self.analyze_expression(expression.children[1], scope_manager, current_type) # SPEXP_

                return resultado_spexp_

            elif expression.children[0].token.type_ == "[":
                # Não é possível acessar um elemento com [] de um tipo que não seja array
                if current_type == "int[]":
                    resultado_exp = self.analyze_expression(expression.children[1], scope_manager) # EXP
                    if resultado_exp != "int":
                        raise Exception(f"Array access with non-integer index, expected 'int' but got '{resultado_exp}'")
                else:
                    raise Exception(f"Type '{current_type}' is not an array")
                
                # Só temos arrays de inteiros, então se um array é acessado, o tipo do resultado é int
                return {
                    "type": "int",
                    "value": None,
                    "has_identifier": True # Para indicar que é um array acessado e não podemos pré calcular valores
                }
            
            else:
                return None

        elif expression.token.type_ == "<SPEXP_>":
            # SPEXP_ -> identifier SPEXP__ SPEXP
            # SPEXP_ -> length

            # Deve retornar o tipo do identificador ou int caso seja length

            # other_data aqui é o tipo da variavel que está sendo acesdsada via id.attr ou id.metodo()
            current_type = other_data

            if expression.children[0].token.type_ == "identifier":
                try:
                    variable_name = expression.children[0].token.value
                    variable_info = scope_manager.get_variable(variable_name)
                except Exception as e:
                    raise Exception(f"Variable '{expression.children[0].token.value}' not declared") from e

                # Tente ver se o identificador está presente na symbol_table como um possível atributo ou método
                if variable_name not in self.symbol_table[current_type]["variables"] and variable_name not in self.symbol_table[current_type]["methods"]:
                    # Se não estiver, então é um erro
                    raise Exception(f"Symbol '{variable_name}' is not an attribute or method of '{current_type}'")
                
                # Aqui sabemos que o identificador é um atributo ou método da variável atual
                # Precisamos verificar qual o seu tipo para passarmos para SPEXP em children[2]
                # Se for um metodo, precisamos passar para SPEXP__ em children[1] quais são os parametros aceitos
                isMethod = variable_name in self.symbol_table[current_type]["methods"]
                # Se for um atributo, passamos o tipo do atributo para SPEXP
                isAttribute = variable_name in self.symbol_table[current_type]["variables"]

                idenfitier_type = self.symbol_table[current_type]["methods"][variable_name]["type"] if isMethod else self.symbol_table[current_type]["variables"][variable_name]["type"]
                method_params = self.symbol_table[current_type]["methods"][variable_name]["params"] if isMethod else None

                resultado_spexp__ = self.analyze_expression(expression.children[1], scope_manager, method_params) # SPEXP__
                resultado_spexp = self.analyze_expression(expression.children[2], scope_manager, idenfitier_type) # SPEXP

                return {
                    "type": idenfitier_type,
                    "value": None,
                    "has_identifier": True # Para indicar que é um atributo ou método acessado e não podemos pré calcular valores
                }

            elif expression.children[0].token.value == "length":
                # Só é possível acessar o length de um array
                if current_type != "int[]":
                    raise Exception(f"Type '{current_type}' is not an array, cannot access 'length'")
                
                return {
                    "type": "int",
                    "value": None,
                    "has_identifier": True # Para indicar que é um array acessado e não podemos pré calcular valores
                }

        elif expression.token.type_ == "<SPEXP__>":
            # SPEXP__ -> ( OEXPS )
            # SPEXP__ -> ε

            # other_data aqui é o dicionário de parametros do método que está sendo chamado ou None se não for um método
            current_params = other_data
            # Transformar o dicionário de parametros em uma lista de tipos para comparar com os parametros passados
            current_params = [v["type"] for v in current_params.values()] if current_params else None

            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager, current_params) # OEXPS
                # Não há retorno para OEXPS
                
            else:
                if current_params:
                    raise Exception("Method called with too few parameters, missing parameters of types: " + ", ".join(current_params))
                

            return None # Não há retorno para SPEXP__

        elif expression.token.type_ == "<OEXPS>":
            # OEXPS -> EXPS
            # OEXPS -> ε

            # other_data aqui é a lista de tipos dos parametros do método que está sendo chamado
            if expression.children[0].token.type_ != EMPTY_CHAR:
                # Aqui garantimos que há pelo menos um parametro, pois EXPS não deriva epsilon
                if not other_data:
                    raise Exception("Method called with no parameters, but it requires at least one")

                self.analyze_expression(expression.children[0], scope_manager, other_data) # EXPS
                # Não há retorno para EXPS
            
            else:
                if other_data:
                    raise Exception("Method called with too few parameters, missing parameters of types: " + ", ".join(other_data))
                
            return None # Não há retorno para OEXPS

        elif expression.token.type_ == "<EXPS>":
            # EXPS -> EXP EXPS_

            # other_data aqui é a lista de tipos dos parametros do método que está sendo chamado
            # Devemos consumir o primeiro parametro e passar o restante para EXPS_
            # Ao consumir o primeiro parametro, devemos verificar se ele é do tipo correto

            if not other_data:
                # Esgotaram os parametros que o método aceita mas ainda há parametros a serem passados
                raise Exception("Method called with too many parameters")
            
            resultado_exp = self.analyze_expression(expression.children[0], scope_manager) # EXP
            
            if resultado_exp["type"] != other_data[0]:
                raise Exception(f"Method called with parameter of wrong type, expected '{other_data[0]}' but got '{resultado_exp["type"]} '")
            
            self.analyze_expression(expression.children[1], scope_manager, other_data[1:]) # EXPS_
            # Não há retorno para EXPS_
            
            return None

        elif expression.token.type_ == "<EXPS_>":
            # EXPS_ -> , EXPS
            # EXPS_ -> ε

            # other_data aqui é a lista de tipos dos parametros do método que está sendo chamado
            # Se EXPS_ deriva epsilon, então não há mais parametros a serem passados
            if expression.children[0].token.type_ != EMPTY_CHAR:
                self.analyze_expression(expression.children[1], scope_manager, other_data) # EXPS
            else:
                if other_data:
                    raise Exception("Method called with too few parameters, missing parameters of types: " + ", ".join(other_data))

            # Não há retorno para EXPS_
            return None

        elif expression.token.type_ == "<NEWEXP>":
            # NEWEXP -> identifier ( ) SPEXP
            # NEWEXP -> int [ EXP ]

            if expression.children[0].token.type_ == "identifier":
                # Check if variable is a declared class in symbol table
                is_valid_class = expression.children[0].token.value in self.symbol_table
                if not is_valid_class:
                    raise Exception(f"Cannot instantiate undeclared class '{expression.children[0].token.value}'")
                
                # Se o identificador é uma variável, então é um objeto instanciado
                resultado_spexp = self.analyze_expression(expression.children[3], scope_manager) # SPEXP
                
                if resultado_spexp:
                    return resultado_spexp
                
                return {
                    "type": expression.children[0].token.value,
                    "value": None,
                    "has_identifier": True
                }
                
            elif expression.children[0].token.value == "int":
                resultado_exp = self.analyze_expression(expression.children[2], scope_manager)
                if resultado_exp != "int":
                    raise Exception("Array size must be an integer")
                
                return {
                    "type": "int[]",
                    "value": None,
                    "has_identifier": True # Para indicar que é um array acessado e não podemos pré calcular valores
                }

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