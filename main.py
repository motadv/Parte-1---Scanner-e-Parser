import sys

from src.gramatica import get_grammar, get_terminal_list
from src.options import Options
from src.scanner import scan
from src.parser import parse
from src.semantic import analyze_semantics


options = Options(sys.argv, "files/")

scan(options)
sat = parse(options, get_grammar(), get_terminal_list())

analyze_semantics(options, sat)


