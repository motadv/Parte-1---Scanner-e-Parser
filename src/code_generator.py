from src.parser import Node, EMPTY_CHAR


def create_label(class_: str, method: str) -> str:
    return f"{class_.lower()}_{method.lower()}:"


class CodeGenerator:
    symbol_table: dict
    if_count: int
    while_count: int

    def __init__(self, symbol_table: dict):
        self.symbol_table = symbol_table
        self.if_count = 1
        self.while_count = 1

    def cgen(self, node: Node, variables=None) -> list[str]:
        if variables is None:
            variables = []

        local_output = []

        # print(f"Type: {node.token.type_}, Value: {node.token.value}")
        if node.token.value == EMPTY_CHAR:
            return local_output
        # Done
        if node.token.type_ == "<PROG>":
            local_output.extend(self.cgen(node.children[0], variables))
            local_output.extend(self.cgen(node.children[1], variables))
        # Done
        elif node.token.type_ == "<MAIN>":
            local_output.append(create_label(node.children[1].token.value, node.children[6].token.value))
            local_output.extend(self.cgen(node.children[14], variables))
            local_output.append("li $v0, 10")
            local_output.append("syscall")
        # Done
        elif node.token.type_ == "<CMD>":
            if node.children[0].token.value == "{":
                local_output.extend(self.cgen(node.children[1], variables))
            elif node.children[0].token.value == "if":
                local_output.extend(self.cgen(node.children[2], variables))
                local_output.append(f"beq $a0, $zero, false_if_{self.if_count}")
                local_output.append(f"true_if_{self.if_count}:")
                local_output.extend(self.cgen(node.children[5], variables))
                local_output.append(f"b end_if_{self.if_count}")
                local_output.append(f"false_if_{self.if_count}:")
                local_output.extend(self.cgen(node.children[7], variables))
                local_output.append(f"end_if_{self.if_count}:")
                self.if_count += 1
            elif node.children[0].token.value == "while":
                local_output.append(f"while_{self.while_count}:")
                local_output.extend(self.cgen(node.children[2], variables))
                local_output.append(f"beq $a0, $zero, end_while_{self.while_count}")
                local_output.extend(self.cgen(node.children[4], variables))
                local_output.append(f"b while_{self.while_count}")
                local_output.append(f"end_while_{self.while_count}:")
                self.while_count += 1
            elif node.children[0].token.value == "System.out.println":
                local_output.extend(self.cgen(node.children[2], variables))
                local_output.append("li $v0, 1")
                local_output.append("syscall")
            elif node.children[0].token.type_ == "identifier":
                # TODO: implement array verification
                name = node.children[0].token.value
                cmdid = node.children[1]
                if cmdid.token.value == "=":
                    local_output.extend(self.cgen(node.children[1], variables))
                    local_output.append(f"sw $a0, {(len(variables) - variables.index(name) - 1) * 4}($sp)")
                else:
                    raise Exception("No array support")
        # Done
        elif node.token.type_ == "<EXP>":
            local_output.extend(self.cgen(node.children[0], variables))
            if node.children[1].children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(node.children[1], variables))
                local_output.append("lw $t1, 4($sp)")
                local_output.append("mult $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<EXP_>":
            local_output.extend(self.cgen(node.children[1], variables))
            if node.children[1].children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(node.children[2], variables))
                local_output.append("lw $t1, 4($sp)")
                local_output.append("mult $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<REXP>":
            local_output.extend(self.cgen(node.children[0], variables))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
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
            local_output.extend(self.cgen(node.children[1], variables))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
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
            local_output.extend(self.cgen(node.children[0], variables))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "+":
                    local_output.append("add $a0, $t1, $a0")
                elif operator == "-":
                    local_output.append("sub $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<AEXP_>":
            local_output.extend(self.cgen(node.children[1], variables))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
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
            local_output.extend(self.cgen(node.children[0], variables))
            child = node.children[1]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "*":
                    local_output.append("mult $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # Done
        elif node.token.type_ == "<MEXP_>":
            local_output.extend(self.cgen(node.children[1], variables))
            child = node.children[2]
            if child.children[0].token.value != EMPTY_CHAR:
                local_output.append("sw $a0, 0($sp)")
                local_output.append("addiu $sp, $sp, -4")
                local_output.extend(self.cgen(child, variables))
                local_output.append("lw $t1, 4($sp)")
                operator = child.children[0].token.value
                if operator == "*":
                    local_output.append("mult $a0, $t1, $a0")
                local_output.append("addiu $sp, $sp, 4")
        # TODO
        elif node.token.type_ == "<SEXP>":
            first = node.children[0]
            if first.token.value == "!":
                local_output.extend(self.cgen(node.children[1], variables))
                local_output.append("not $a0, $a0")
            elif first.token.value == "-":
                local_output.extend(self.cgen(node.children[1], variables))
                local_output.append("neg $a0, $a0")
            elif first.token.value == "new":
                local_output.extend(self.cgen(node.children[1], variables))
            elif first.token.type_ == "<PEXP>":
                if first.children[0].token.value == "(":
                    local_output.extend(self.cgen(first.children[1], variables))
                elif first.children[0].token.type_ == "identifier":
                    name = first.children[0].token.value
                    # TODO: use variable
                elif first.children[0].token.value == "this":
                    # TODO: use local variable
                    pass
        elif node.token.type_ == "<OEXPS>":
            # TODO: add parameters
            pass
        elif node.token.type_ == "<CONSTANT>":
            local_output.append(f"li $a0, {node.children[0].token.value}")
        return local_output


def generate_code(symbol_table: dict, semantic_tree: Node):

    code_generator = CodeGenerator(symbol_table)

    result = code_generator.cgen(semantic_tree)
    for line in result:
        print(line)



