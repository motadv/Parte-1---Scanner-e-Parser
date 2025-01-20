# MIPS code generator with heap allocation
# To be run in the MARS MIPS simulator

from src.options import Options
from src.parser import Node, EMPTY_CHAR

class ScopeManager():
    scopes = []
    
    def __init__(self):
        self.scopes = []
        
    def enter_scope(self):
        self.scopes.append({})
    
    def exit_scope(self):
        self.scopes.pop()
        
    def add_or_modify_symbol(self, symbol, value = None):
        self.scopes[-1][symbol] = value
        
    def get_symbol(self, symbol):
        for scope in reversed(self.scopes):
            if symbol in scope:
                return scope[symbol]
        return None
    

class CodeGeneratorWithHeap():
    scopeManager = None
    symbol_table = None
    code = []
    if_count = 0
    while_count = 0
    
    def __init__(self, symbol_table):
        self.scopeManager = ScopeManager()
        self.symbol_table = symbol_table
        self.code = []
        self.if_count = 0
        self.while_count = 0
    
    def make_method_label(self, class_name, method_name):
        return f"{class_name}_{method_name}:"
        
        
    def generate_code(self, node: Node, data):
        if data == None:
            data = {}
        
        match node.token.type_:
            case "<PROG>":
                self.code.append(".text")
                # First generate the code for the classes to have the functions available
                lclasses = node.children[1]
                self.generate_code(lclasses, data)
                
                # Then generate the code for the main function
                main = node.children[0]
                self.generate_code(main, data)
            case "<MAIN>":
                # Main function declaration
                self.code.append(".main:")
                self.scopeManager.enter_scope()
                cmd = node.children[14]
                self.generate_code(cmd, data)
                self.scopeManager.exit_scope()
                
            case "<CLASSE>":
                class_name = node.children[1].token.value
                class_lvar = node.children[4]
                class_lmetodo = node.children[5]
                
                data = {
                    "class_name": class_name
                }
                
                self.scopeManager.enter_scope()
                
                self.generate_code(class_lvar, data)
                self.generate_code(class_lmetodo, data)
                
                self.scopeManager.exit_scope()
            
            case "<LCLASSE>":
                if node.children[0].token.type_ != EMPTY_CHAR:
                    self.generate_code(node.children[0], data)
                    self.generate_code(node.children[1], data)
            
            case "<METODO>":
                class_name = data["class_name"]
                method_name = node.children[2].token.value
                
                self.scopeManager.enter_scope()
                # object address will be in $a0
                
                # Calculate the size of the activation record
                activation_record_size = 4 # object address (free $a0)
                method_params = self.symbol_table[class_name][method_name]["params"]
                for param, p_info in method_params.items():
                    p_info["offset"] = activation_record_size
                    self.scopeManager.add_or_modify_symbol(param, p_info)
                    activation_record_size += 4
                
                method_variables = self.symbol_table[class_name][method_name]["variables"]
                for var, v_info in method_variables.items():
                    v_info["offset"] = activation_record_size
                    self.scopeManager.add_or_modify_symbol(var, v_info)
                    activation_record_size += 4
                
                # Generate the method label
                method_label = self.make_method_label(class_name, method_name)
                self.code.append(method_label)
                # Parans will be in the R.A.
                # Address of the object will be in $a0
                # R.A Structure:
                # 0: Object Address
                # (nParams*4): Parameters
                # (nParams*4)+(nLVars*4): Local variables
                
                self.code.append("move $fp, $sp") # RA is in the stack, save it in the fp
                # move the stack pointer to the end of the activation record
                self.code.append(f"addi $sp, $sp, {activation_record_size}")

                self.code.append("sw $ra, 0($sp)") # Save the return address
                
                self.code.append("sw $a0, 0($fp)") # Save the object address
                
                # Initialize the local variables to 0
                for var, v_info in method_variables.items():
                    self.code.append(f"sw $zero, {v_info['offset']}($fp)")
                
                # Generate the code for the method LCMD
                method_lcmd = node.children[9]
                self.generate_code(method_lcmd, data)
                
                # Save the return value
                self.generate_code(node.children[12], data) # EXP saves the return value in $a0
                
                # Restore the stack pointer to the previous value
                # effectively deallocating the activation record
                
                self.code.append(f"lw $ra, 4($sp)") # Restore the return address
                self.code.append("addi $sp, $sp, -4") #? Deallocate the return address
                
                self.code.append(f"move $sp, $fp")
                
                self.code.append("jr $ra") # Return to the caller

                # clear scope
                self.scopeManager.exit_scope()
          
            case "<LMETODO>":
                if node.children[0].token.type_ != EMPTY_CHAR:
                    self.generate_code(node.children[0], data)
                    self.generate_code(node.children[1], data)
                                  
            case "<CMD>":
                first_child = node.children[0]
                if first_child.token.type_ == "{":
                    self.scopeManager.enter_scope()
                    self.generate_code(node.children[1], data)
                    self.scopeManager.exit_scope()
                elif first_child.token.type_ == "if":
                    # Evaluate the expression
                    self.if_count += 1
                    self.generate_code(node.children[2], data) # EXP
                    self.code.append(f"beq $a0, $zero, else_{self.if_count}")
                    self.code.append(f"if_{self.if_count}:")
                    self.generate_code(node.children[5], data)
                    self.code.append(f"b end_if_{self.if_count}")
                    self.code.append(f"else_{self.if_count}:")   
                    self.generate_code(node.children[7], data)
                    self.code.append(f"end_if_{self.if_count}:")
                elif first_child.token.type_ == "while":
                    self.while_count += 1
                    self.code.append(f"while_{self.while_count}:")
                    self.generate_code(node.children[2], data) # EXP
                    self.code.append(f"beq $a0, $zero, end_while_{self.while_count}")
                    self.generate_code(node.children[4], data) # CMD
                    self.code.append(f"b while_{self.while_count}")
                    self.code.append(f"end_while_{self.while_count}:")
                elif first_child.token.type_ == "System.out.println":
                    self.generate_code(node.children[2], data) # EXP
                    self.code.append("li $v0, 1")
                    self.code.append("syscall")
                elif first_child.token.type_ == "identifier":
                    # Assignment to a variable or array
                    var_name = first_child.token.value
                    # * Already dealing with possibilities for CMDID
                    cmd_id = node.children[1]
                    cmd_id_type = cmd_id.children[0].token.type_
                    if cmd_id_type == "=":
                        # Assignment to a variable
                        # evaluate the expression
                        self.generate_code(cmd_id.children[1], data) # EXP
                        # get the variable address from the scope
                        var_info = self.scopeManager.get_symbol(var_name)
                        
                        if var_info != None:
                            var_offset = var_info["offset"]
                            # store the value in the address
                            self.code.append(f"sw $a0, {var_offset}($fp)")
                            
                        else:
                            # Variable is a class variable
                            # get class name
                            class_name = data["class_name"]
                            class_variables = self.symbol_table[class_name]["variables"]
                            var_offset = 0
                            for var, v_info in class_variables.items():
                                if var == var_name:
                                    break
                                var_offset += 4
                                
                                
                            # Load the object address in $a0
                            self.code.append("lw $t0, 4($fp)") # Object address
                            # Store the value in the address
                            self.code.append(f"sw $a0, {var_offset}($t0)")
                        
                        pass
                    elif cmd_id_type == "[":
                        # Assignment to an array
                        # get the variable address from the scope
                        var_info = self.scopeManager.get_symbol(var_name)
                        if var_info != None:
                            # Variable is a method variable or parameter
                            var_offset = var_info["offset"]
                            # load the adress into $t0
                            self.code.append(f"lw $t0, {var_offset}($fp)")
                            # save it in the stack
                            self.code.append("sw $t0, 0($sp)")
                            self.code.append("addi $sp, $sp, -4")
                            
                        else:
                            # Variable is a class variable
                            class_name = data["class_name"]
                            class_variables = self.symbol_table[class_name]["variables"]
                            var_offset = 0
                            for var, v_info in class_variables.items():
                                if var == var_name:
                                    break
                                var_offset += 4
                                
                            # Load the object address in $t0
                            self.code.append("lw $t0, 4($fp)") # Object address
                            # Save the address in the stack
                            self.code.append("sw $t0, 0($sp)")
                            self.code.append("addi $sp, $sp, -4")
                        
                        # evaluate the expression for the index
                        self.generate_code(cmd_id.children[1], data)
                        # offset the address by 4*index + 4
                        self.code.append("lw $t0, 4($sp)")
                        self.code.append("addi $sp, $sp, 4") # pop the index
                        
                        self.code.append("mul $a0, $a0, 4") # multiply the index by 4
                        self.code.append("addi $a0, $a0, 4") # Skip array size
                        self.code.append("add $a0, $a0, $t0") # offset the address by 4*index + 4
                        # save the int address in the stack
                        self.code.append("sw $a0, 0($sp)")
                        self.code.append("addi $sp, $sp, -4")
                        # evaluate the expression for the value
                        self.generate_code(cmd_id.children[3], data) # EXP to be stored
                        # load the address
                        self.code.append("lw $t0, 4($sp)")
                        self.code.append("addi $sp, $sp, 4")
                        # store the value in the address
                        self.code.append("sw $a0, 0($t0)")         
                            
                            
            case "<LCMD>":
                first_child = node.children[0]
                if first_child.token.type_ != EMPTY_CHAR:
                    self.generate_code(first_child, data)
                    self.generate_code(node.children[1], data)
            case "<CMDELSE>":
                first_child = node.children[0]
                if first_child.token.type_ != EMPTY_CHAR:
                    self.scopeManager.enter_scope()
                    self.generate_code(node.children[2], data) # CMD
                    self.scopeManager.exit_scope()
            case "<EXP>":
                # Check if EXP_ derives to EMPTY_CHAR
                # If it does, then its just the REXP
                # If it doesnt, then we need to evaluate the AND operation of REXP and EXP_
                self.generate_code(node.children[0], data) # REXP
                
                has_and = node.children[1].children[0].token.type_ == "&&"
                if has_and:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    self.generate_code(node.children[1], data) # EXP_
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    
                    # AND operation
                    self.code.append("mul $a0, $a0, $t0")
            case "<EXP_>":
                self.generate_code(node.children[1], data)
                has_and = node.children[2].children[0].token.type_ == "&&"
                if has_and:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    self.generate_code(node.children[2], data)
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    
                    # AND operation
                    self.code.append("mul $a0, $a0, $t0")
                    
            case "<REXP>":
                self.generate_code(node.children[0], data) # AEXP
                operation = node.children[1].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[1], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                if operation == "<":
                    # Compare
                    self.code.append("slt $a0, $t0, $a0")
                elif operation == "==":
                    self.code.append("seq $a0, $a0, $t0")
                elif operation == "!=":
                    self.code.append("sne $a0, $a0, $t0")        
                
            case "<REXP_>":
                self.generate_code(node.children[1], data) # AEXP
                operation = node.children[2].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[2], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                if operation == "<":
                    # Compare
                    self.code.append("slt $a0, $t0, $a0")
                elif operation == "==":
                    self.code.append("seq $a0, $a0, $t0")
                elif operation == "!=":
                    self.code.append("sne $a0, $a0, $t0")        
                
            case "<AEXP>":
                self.generate_code(node.children[0], data)
                operation = node.children[1].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[1], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    if operation == "+":
                        self.code.append("add $a0, $a0, $t0")
                    elif operation == "-":
                        self.code.append("sub $a0, $t0, $a0")
                    
            case "<AEXP_>":
                self.generate_code(node.children[1], data)
                operation = node.children[2].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[2], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    if operation == "+":
                        self.code.append("add $a0, $a0, $t0")
                    elif operation == "-":
                        self.code.append("sub $a0, $t0, $a0")
            case "<MEXP>":
                self.generate_code(node.children[0], data)
                operation = node.children[1].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[1], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    if operation == "*":
                        self.code.append("mul $a0, $a0, $t0")
                        
            case "<MEXP_>":
                self.generate_code(node.children[1], data)
                operation = node.children[2].children[0].token.type_
                if operation != EMPTY_CHAR:
                    # Save $a0 in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # Evaluate the second expression
                    self.generate_code(node.children[2], data)
                    
                    # Load $a0 from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    if operation == "*":
                        self.code.append("mul $a0, $a0, $t0")
            case "<SEXP>":
                first_child = node.children[0]
                if first_child.token.type_ == "!":
                    self.generate_code(node.children[1], data)
                    self.code.append("seq $a0, $a0, $zero")
                elif first_child.token.type_ == "-":
                    self.generate_code(node.children[1], data)
                    self.code.append("sub $a0, $zero, $a0")
                elif first_child.token.type_ == "<CONSTANT>":
                    self.generate_code(first_child, data)
                elif first_child.token.type_ == "new":
                    newexp = node.children[1]
                    newexp_first = newexp.children[0]

                    if newexp_first.token.type_ == "int":
                        # Get the size of the array
                        self.generate_code(newexp.children[2], data)
                        # Multiply the size by 4
                        self.code.append("mul $a0, $a0, 4")
                        # The first 4 bytes will store the size of the array
                        self.code.append("addi $a0, $a0, 4")
                        # Allocate the memory
                        self.code.append("li $v0, 9")
                        self.code.append("syscall")
                        # $v0 has the address of the array
                        # Store the size of the array in the first 4 bytes
                        self.code.append("sw $a0, 0($v0)")
                        # Move the address to $a0
                        self.code.append("move $a0, $v0")
                        
                    elif newexp_first.token.type_ == "identifier":
                        # Get the class name
                        class_name = newexp_first.token.value
                        # Get the size of the class
                        class_size = 0;
                        for var, v_info in self.symbol_table[class_name]["variables"].items():
                            class_size += 4
                        
                        # Allocate the memory in the heap
                        self.code.append(f"li $v0, 9") # Allocate memory SBRK
                        self.code.append(f"li $a0, {class_size}") # Size of the class
                        self.code.append("syscall")
                        
                        # $v0 has the address of the class
                        # set the first 4 bytes to the class address
                        self.code.append(f"sw $v0, 0($v0)")
                        self.code.append("move $a0, $v0")
                        
                        # Pass onwards the class name
                        data["class_name"] = class_name
                        
                        # Call the cgen of SPEXP
                        self.generate_code(newexp.children[3], data) # SPEXP
                        
                    
                elif first_child.token.type_ == "<PEXP>":
                    pexp = node.children[0]
                    pexp_first_child = pexp.children[0]
                    if pexp_first_child.token.type_ in ["identifier", "this"]:
                        # Get the variable address from the scope
                        var_name = pexp_first_child.token.value
                        var_info = self.scopeManager.get_symbol(var_name)
                        if var_info == None:
                            # identifier is a class variable
                            # Get the object address in the R.A offset 4
                            self.code.append("lw $a0, 4($fp)")
                            # Find this var_name in the class symbol table and get its index
                            class_name = data["class_name"]
                            class_variables = self.symbol_table[class_name]["variables"]
                            var_offset = 0
                            for var, v_info in class_variables.items():
                                if var == var_name:
                                    break
                                var_offset += 4
                                
                            # Load the value from the address
                            self.code.append(f"lw $a0, {var_offset}($a0)")
                            
                        else:
                            # identifier is a method variable or parameter
                            var_offset = var_info["offset"]
                            
                            # Load the value from the address
                            self.code.append(f"lw $a0, {var_offset}($fp)")
                            
                    elif pexp_first_child.token.type_ == "(":
                        self.generate_code(pexp.children[1], data)
                        
                        
            case "<SPEXP>":
                first_child = node.children[0]
                
                if first_child.token.type_ == ".": # SPEXP_
                    self.generate_code(node.children[1], data) # SPEXP_
                elif first_child.token.type_ == "[":
                    # save the address in the stack
                    self.code.append("sw $a0, 0($sp)")
                    self.code.append("addi $sp, $sp, -4")
                    
                    # evaluate the expression to find the index
                    self.generate_code(node.children[1], data)
                    self.code.append("mul $a0, $a0, 4")
                    self.code.append("addi $a0, $a0, 4")
                    
                    # load the address from the stack
                    self.code.append("lw $t0, 4($sp)")
                    self.code.append("addi $sp, $sp, 4")
                    
                    # add the index to the address
                    self.code.append("add $a0, $a0, $t0")
                    # load the value from the address
                    self.code.append("lw $a0, 0($a0)")
                
            case "<SPEXP_>":
                first_child = node.children[0]
                if first_child.token.type_ == "length":
                    # Get the size of the array
                    self.code.append("lw $a0, 0($a0)")
                    
                elif first_child.token.type_ == "identifier":
                    # Get the class name
                    class_name = data["class_name"]
                    
                    # Check if this identifier is a method call
                    if node.children[1].children[0].token.type_ == "(":
                        # Is a method call
                        
                        # Save the fp in the stack
                        self.code.append("sw $fp, 0($sp)") # Old fp
                        self.code.append("addi $sp, $sp, -4")
                        
                        
                        self.code.append("move $fp, $sp") # RA is in the stack, save it in the fp
                        
                        self.code.append("sw $a0, 0($fp)") # object address
                        self.code.append("addiu $fp $fp -4") # Move the fp to the first parameter
                        
                        # Evaluate the parameters and write them in the R.A.
                        self.generate_code(node.children[1].children[1], data) # OEXPS                        
                        
                        # Go to method entry
                        self.code.append(f"jal {class_name}_{first_child.token.value}")
                        # Return value is in $a0
                        
                        # Restore the old frame pointer
                        self.code.append("lw $fp, 4($sp)")
                        
                    else:
                        # Is a class variable
                        # Get the variable address from the class
                        class_variables = self.symbol_table[class_name]["variables"]
                        var_offset = 0
                        for var, v_info in class_variables.items():
                            if var == first_child.token.value:
                                break
                            var_offset += 4
                            
                        # Load the value from the address
                        self.code.append(f"lw $a0, {var_offset}($a0)")
                        
                
            case "<OEXPS>":
                if node.children[0].token.type_ != EMPTY_CHAR:
                    self.generate_code(node.children[0], data) # EXPS
                
                
            case "<EXPS>":
                self.generate_code(node.children[0], data) # EXP
                # Save the value in the R.A. 
                self.code.append("sw $a0, 0($fp)")
                self.code.append("addiu $fp, $fp, -4")
                
                self.generate_code(node.children[1], data) # EXPS_
                
            case "<EXPS_>":
                if node.children[0].token.type_ != EMPTY_CHAR:
                    self.generate_code(node.children[0], data) # EXPS
            
            case "<CONSTANT>":
                self.code.append(f"li $a0, {node.children[0].token.value}")
            case _:
                pass
        

def write_code_to_file(options: Options, symbol_table: dict, semantic_tree: Node):
    code_generator = CodeGeneratorWithHeap(symbol_table)
    code_generator.generate_code(semantic_tree, None)
    
    with open(options.files_dir+"mars_code.asm", "w") as f:
        for line in code_generator.code:
            f.write(line + "\n")
            
    print(f"Code written to {options.files_dir}mars_code.asm")