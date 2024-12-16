import sys

from src.gramatica import get_grammar, get_terminal_list
from src.options import Options
from src.scanner import scan
from src.parser import parse


options = Options(sys.argv, "files/")

scan(options)
parse(options, get_grammar(), get_terminal_list())
