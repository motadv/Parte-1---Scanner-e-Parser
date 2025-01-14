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

        print(f"Type: {node.token.type_}, Value: {node.token.value}")
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
                local_output.extend(self.cgen(node.children[0], variables))
                local_output.extend(self.cgen(node.children[1], variables))
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
        elif node.children[0].token.type_ == "<CONSTANT>":
            local_output.append(f"li $a0, {node.children[0].children[0].token.value}")
        return local_output

# %%
# def generate_program(self, semantic_tree: Node):
#     self.output.append(".data")
#     for element in semantic_tree:
#         if element["type"] == "class":
#             self.generate_class(element)
#
#     self.output.extend(self.data_section)
#     self.output.extend(self.text_section)
#
# def generate_class(self, class_node):
#     if "main" in class_node:
#         self.generate_main(class_node["main"])
#
# def generate_main(self, main_node):
#     self.text_section.append("main:")
#     for cmd in main_node.get("commands", []):
#         self.generate_command(cmd)
#     self.text_section.append("    li $v0, 10")
#     self.text_section.append("    syscall")
#
# def generate_command(self, cmd_node):
#     if cmd_node.get("type") == "assignment":
#         target = cmd_node["target"]
#         expression = self.generate_expression(cmd_node["expression"])
#         self.text_section.append(f"    li $t0, {expression}")
#         self.text_section.append(f"    sw $t0, {target}")
#         self.data_section.append(f"{target}: .word 0")
#
# def generate_expression(self, expr_node):
#     if expr_node.get("type") == "constant":
#         return expr_node["value"]
#     elif expr_node.get("type") == "identifier":
#         return f"{expr_node['name']}"
#     elif expr_node.get("type") == "operation":
#         left = self.generate_expression(expr_node["left"])
#         right = self.generate_expression(expr_node["right"])
#         op = expr_node["operator"]
#
#         if op == "+":
#             self.text_section.append(f"    li $t1, {left}")
#             self.text_section.append(f"    li $t2, {right}")
#             self.text_section.append("    add $t0, $t1, $t2")
#         elif op == "-":
#             self.text_section.append(f"    li $t1, {left}")
#             self.text_section.append(f"    li $t2, {right}")
#             self.text_section.append("    sub $t0, $t1, $t2")
#         elif op == "*":
#             self.text_section.append(f"    li $t1, {left}")
#             self.text_section.append(f"    li $t2, {right}")
#             self.text_section.append("    mul $t0, $t1, $t2")
#         elif op == "/":
#             self.text_section.append(f"    li $t1, {left}")
#             self.text_section.append(f"    li $t2, {right}")
#             self.text_section.append("    div $t0, $t1, $t2")
#
#         return "$t0"
#
# def get_output(self):
#     return "\n".join(self.output)


def generate_code(symbol_table: dict, semantic_tree: Node):

    # symbol_table = {
    #     "A": {
    #         "type": "class",
    #         "extends": None,
    #         "variables": {
    #             "this": {
    #                 "type": "A"
    #             },
    #             "num1": {
    #                 "type": "int"
    #             },
    #             "num2": {
    #                 "type": "int"
    #             },
    #             "num3": {
    #                 "type": "int"
    #             },
    #             "result": {
    #                 "type": "int"
    #             }
    #         },
    #         "methods": {
    #             "foo": {
    #                 "type": "int",
    #                 "params": {
    #                     "p1": {
    #                         "type": "int"
    #                     },
    #                     "p2": {
    #                         "type": "int"
    #                     },
    #                     "p3": {
    #                         "type": "int"
    #                     }
    #                 },
    #                 "variables": {}
    #             },
    #             "bar": {
    #                 "type": "B",
    #                 "params": {},
    #                 "variables": {}
    #             }
    #         }
    #     },
    #     "B": {
    #         "type": "class",
    #         "extends": None,
    #         "variables": {
    #             "this": {
    #                 "type": "B"
    #             },
    #             "a": {
    #                 "type": "A"
    #             },
    #             "returnVal": {
    #                 "type": "int"
    #             }
    #         },
    #         "methods": {
    #             "foo": {
    #                 "type": "int",
    #                 "params": {},
    #                 "variables": {}
    #             }
    #         }
    #     },
    #     "C": {
    #         "type": "class",
    #         "extends": None,
    #         "variables": {
    #             "this": {
    #                 "type": "C"
    #             }
    #         },
    #         "methods": {
    #             "foo": {
    #                 "type": "int",
    #                 "params": {},
    #                 "variables": {}
    #             }
    #         }
    #     }
    # }

    code_generator = CodeGenerator(symbol_table)

    result = code_generator.cgen(semantic_tree)
    for line in result:
        print(line)



