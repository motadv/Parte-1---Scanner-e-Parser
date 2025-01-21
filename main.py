import sys

from src.gramatica import get_grammar, get_terminal_list
from src.options import Options
from src.scanner import scan
from src.parser import parse
from src.semantic import analyze_semantics
# from src.code_generator import generate_code
from src.code_generator_heap import write_code_to_file


options = Options(sys.argv, "files/")

scan(options)
sat = parse(options, get_grammar(), get_terminal_list())

symbol_table, semantic_tree = analyze_semantics(options, sat)

write_code_to_file(options, symbol_table, semantic_tree)
