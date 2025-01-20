import json

from src.options import Options
from src.parser import Node, EMPTY_CHAR


def create_label(class_: str, method: str) -> str:
    return f"{class_.lower()}_{method.lower()}:"


def get_label(class_: str, method: str) -> str:
    return f"{class_.lower()}_{method.lower()}"


def get_stack_pos(values: dict, target: str) -> int:
    size = len(values)
    return (size - list(values.keys()).index(target)) * 4 + 4


class CodeGenerator:
    symbol_table: dict
    classes: dict[str, dict[str, dict]]
    if_count: int
    while_count: int

    def __init__(self, symbol_table: dict):
        self.symbol_table = symbol_table
        self.if_count = 1
        self.while_count = 1
        self.classes = {}

    def read_classes(self, root: Node):
        lclass = root.children[1]
        while lclass.children[0].token.value != EMPTY_CHAR:
            node = lclass.children[0]
            class_name = node.children[1].token.value
            class_ = self.classes.get(class_name, dict())
            lvar = node.children[4]
            attributes = class_.get("attributes", dict())
            while lvar.children[0].token.value != EMPTY_CHAR:
                var = lvar.children[0]
                var_type = var.children[0].children[0].token.value
                var_name = var.children[1].token.value
                attributes[var_name] = var_type
                lvar = lvar.children[1]
            class_["attributes"] = attributes
            lmetodo = node.children[5]
            methods = class_.get("methods", dict())
            while lmetodo.children[0].token.value != EMPTY_CHAR:
                metodo = lmetodo.children[0]
                method_name = metodo.children[2].token.value
                method_type = metodo.children[1].children[0].token.value

                params = dict()
                oparam = metodo.children[4]
                if oparam.children[0].token.value != EMPTY_CHAR:
                    param = oparam.children[0]
                    param_type = param.children[0].children[0].token.value
                    param_name = param.children[1].token.value
                    params[param_name] = param_type
                    lparam = param.children[2]
                    while lparam.children[0].token.value != EMPTY_CHAR:
                        param_type = lparam.children[1].children[0].token.value
                        param_name = lparam.children[2].token.value
                        params[param_name] = param_type
                        lparam = lparam.children[3]
                variables = dict()
                lvar = metodo.children[7]
                while lvar.children[0].token.value != EMPTY_CHAR:
                    var = lvar.children[0]
                    var_type = var.children[0].children[0].token.value
                    var_name = var.children[1].token.value
                    variables[var_name] = var_type
                    lvar = lvar.children[1]
                methods[method_name] = {"type": method_type, "params": params, "variables": variables}
                lmetodo = lmetodo.children[1]
            class_["methods"] = methods
            self.classes[class_name] = class_
            lclass = lclass.children[1]

    def cgen(self, node: Node, variables: dict[str, str] = None, is_function: bool = False) -> list[str]:
        if variables is None:
            variables = {}
        else:
            variables = variables.copy()

        local_output = []

        # print(f"Type: {node.token.type_}, Value: {node.token.value}")
        if node.token.value == EMPTY_CHAR:
            return local_output
        # Done
        if node.token.type_ == "<PROG>":
            local_output.extend(self.cgen(node.children[0], variables, is_function))
            local_output.extend(self.cgen(node.children[1], variables, is_function))
        # Done
        elif node.token.type_ == "<MAIN>":
            local_output.append(create_label(node.children[1].token.value, node.children[6].token.value))
            local_output.extend(self.cgen(node.children[14], variables, is_function))
            local_output.append("li $v0, 10")
            local_output.append("syscall")
            local_output.append("")
        elif node.token.type_ == "<LCLASSE>":
            if node.children[0].token.value != EMPTY_CHAR:
                local_output.extend(self.cgen(node.children[0], variables, is_function))
                local_output.extend(self.cgen(node.children[1], variables, is_function))
        elif node.token.type_ == "<CLASSE>":
            variables = {}
            class_name = node.children[1].token.value
            for var_name, var_type in self.classes[class_name]["attributes"].items():
                variables[var_name] = var_type
            # local_output.extend(self.cgen(node.children[5], variables, is_function))
            lmetodo = node.children[5]
            while lmetodo.children[0].token.value != EMPTY_CHAR:
                metodo = lmetodo.children[0]
                method_name = metodo.children[2].token.value
                params = self.classes[class_name]["methods"][method_name]["params"]
                for param_name, param_type in params.items():
                    variables[param_name] = param_type
                method_variables = self.classes[class_name]["methods"][method_name]["variables"]
                for var_name, var_type in method_variables.items():
                    variables[var_name] = var_type
                local_output.append(create_label(class_name, method_name))
                local_output.append("move $fp, $sp")
                local_output.append("sw $ra, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                for _ in range(len(method_variables)):
                    local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(metodo.children[9], variables, is_function=True))
                local_output.append("lw $ra, 4($sp)")
                local_output.append(f"addiu $sp, $sp, {len(variables) * 4 + 8}")
                local_output.append("lw $fp, 0($sp)")
                local_output.append("jr $ra")
                local_output.append("")
                lmetodo = lmetodo.children[1]
        # Done
        elif node.token.type_ == "<CMD>":
            if node.children[0].token.value == "{":
                local_output.extend(self.cgen(node.children[1], variables, is_function))
            elif node.children[0].token.value == "if":
                local_output.extend(self.cgen(node.children[2], variables, is_function))
                local_output.append(f"beq $a0, $zero, false_if_{self.if_count}")
                local_output.append(f"true_if_{self.if_count}:")
                local_output.extend(self.cgen(node.children[5], variables, is_function))
                local_output.append(f"b end_if_{self.if_count}")
                local_output.append(f"false_if_{self.if_count}:")
                local_output.extend(self.cgen(node.children[7], variables, is_function))
                local_output.append(f"end_if_{self.if_count}:")
                self.if_count += 1
            elif node.children[0].token.value == "while":
                local_output.append(f"while_{self.while_count}:")
                local_output.extend(self.cgen(node.children[2], variables, is_function))
                local_output.append(f"beq $a0, $zero, end_while_{self.while_count}")
                local_output.extend(self.cgen(node.children[4], variables, is_function))
                local_output.append(f"b while_{self.while_count}")
                local_output.append(f"end_while_{self.while_count}:")
                self.while_count += 1
            elif node.children[0].token.value == "System.out.println":
                local_output.extend(self.cgen(node.children[2], variables, is_function))
                local_output.append("li $v0, 1")
                local_output.append("syscall")
            elif node.children[0].token.type_ == "identifier":
                print(f"Identifier: {node.children[0].token.value}")
                # TODO: implement array verification
                name = node.children[0].token.value
                cmdid = node.children[1]
                if cmdid.children[0].token.value == "=":
                    local_output.extend(self.cgen(cmdid.children[1], variables, is_function))
                    local_output.append(f"sw $a0, {list(variables.keys()).index(name) * 4}($sp)")
                else:
                    raise Exception("No array support")
        elif node.token.type_ == "<LCMD>":
            if node.children[0].token.value != EMPTY_CHAR:
                local_output.extend(self.cgen(node.children[0], variables, is_function))
                local_output.extend(self.cgen(node.children[1], variables, is_function))
        # Done
        elif node.token.type_ == "<EXP>":
            local_output.extend(self.cgen(node.children[0], variables, is_function))
            if node.children[1].children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(node.children[1], variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                local_output.append("mul $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<EXP_>":
            local_output.extend(self.cgen(node.children[1], variables, is_function))
            if node.children[1].children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(node.children[2], variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                local_output.append("mul $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<REXP>":
            local_output.extend(self.cgen(node.children[0], variables, is_function))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "<":
                    local_output.append("slt $a0, $t1, $a0")
                elif operator == "==":
                    local_output.append("seq $a0, $t1, $a0")
                elif operator == "!=":
                    local_output.append("sne $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<REXP_>":
            local_output.extend(self.cgen(node.children[1], variables, is_function))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "<":
                    local_output.append("slt $a0, $t1, $a0")
                elif operator == "==":
                    local_output.append("seq $a0, $t1, $a0")
                elif operator == "!=":
                    local_output.append("sne $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<AEXP>":
            local_output.extend(self.cgen(node.children[0], variables, is_function))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "+":
                    local_output.append("add $a0, $t1, $a0")
                elif operator == "-":
                    local_output.append("sub $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<AEXP_>":
            local_output.extend(self.cgen(node.children[1], variables, is_function))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "<":
                    local_output.append("slt $a0, $t1, $a0")
                elif operator == "==":
                    local_output.append("seq $a0, $t1, $a0")
                elif operator == "!=":
                    local_output.append("sne $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
            # Done
        # Done
        elif node.token.type_ == "<MEXP>":
            local_output.extend(self.cgen(node.children[0], variables, is_function))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "*":
                    local_output.append("mul $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<MEXP_>":
            local_output.extend(self.cgen(node.children[1], variables, is_function))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables, is_function))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "*":
                    local_output.append("mul $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        elif node.token.type_ == "<SEXP>":
            first = node.children[0]
            if first.token.value == "!":
                local_output.extend(self.cgen(node.children[1], variables, is_function))
                local_output.append("not $a0, $a0")
            elif first.token.value == "-":
                local_output.extend(self.cgen(node.children[1], variables, is_function))
                local_output.append("neg $a0, $a0")
            elif first.token.value == "new":
                local_output.extend(self.cgen(node.children[1], variables, is_function))
            elif first.token.type_ == "<PEXP>":
                if first.children[0].token.value == "(":
                    local_output.extend(self.cgen(first.children[1], variables, is_function)) # ( EXP )
                elif first.children[0].token.type_ == "identifier":
                    name = first.children[0].token.value
                    if not is_function:
                        local_output.append(f"lw $a0, {list(variables.keys()).index(name) * 4}($sp)") 
                    else:
                        local_output.append(f"lw $a0, {list(variables.keys()).index(name) * 4}($fp)")
                elif first.children[0].token.value == "this":
                    # TODO: use local variable
                    pass
        elif node.token.type_ == "<OEXPS>":
            # TODO: add parameters
            pass
        elif node.token.type_ == "<NEWEXP>":
            if node.children[0].token.value == "int":
                raise Exception("No array support")
            class_name = node.children[0].token.value
            spexp = node.children[3]
            while spexp.children[0].token.value != EMPTY_CHAR:
                if spexp.children[0] == "[":
                    raise Exception("No array support")
                spexp_ = spexp.children[1]
                object_call_name = spexp_.children[0].token.value
                if object_call_name == "length":
                    raise Exception("No array support")
                spexp__ = spexp_.children[1]
                if spexp__.children[0].token.value == EMPTY_CHAR:
                    if not is_function:
                        local_output.append(
                            f"lw $a0, {get_stack_pos(self.classes[class_name]['attributes'], object_call_name)}($sp)"
                        )
                elif spexp__.children[0].token.value == "(":
                    local_output.append("sw $fp 0($sp)")
                    local_output.append("addiu $sp, $sp, -4")
                    oexps = spexp__.children[1]
                    args = []
                    if oexps.children[0].token.value != EMPTY_CHAR:
                        exps = oexps.children[0]
                        exps_ = exps.children[1]
                        # Attributes
                        for _ in self.classes[class_name]["attributes"].keys():
                            args.append("addiu $sp, $sp, -4")
                        # Args
                        while exps_.children[0].token.value != EMPTY_CHAR:
                            # Reversed order
                            args.append("addiu $sp, $sp, -4")
                            args.append("sw $a0, 0($sp)")
                            args.extend(self.cgen(exps.children[0], variables, is_function))
                            exps = exps_.children[1]
                            exps_ = exps.children[1]
                        args.append("addiu $sp, $sp, -4")
                        args.append("sw $a0, 0($sp)")
                        args.extend(self.cgen(exps.children[0], variables, is_function))
                    local_output.extend(reversed(args))
                    local_output.append(f"jal {get_label(class_name, object_call_name)}")
                spexp = spexp_.children[2]
        elif node.token.type_ == "<CONSTANT>":
            local_output.append(f"li $a0, {node.children[0].token.value}")
        return local_output


def generate_code(options: Options, symbol_table: dict, semantic_tree: Node):

    code_generator = CodeGenerator(symbol_table)

    code_generator.read_classes(semantic_tree)

    # json_object = json.dumps(code_generator.classes, indent=4)
    #
    # # Print JSON object
    # print(json_object)

    result = code_generator.cgen(semantic_tree)

    with open(f"{options.files_dir}code_gen.txt", "w") as f:
        print()
        for line in result:
            f.write(f"{line}\n")
            print(line)
