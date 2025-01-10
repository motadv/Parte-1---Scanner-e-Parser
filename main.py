import sys

from src.gramatica import get_grammar, get_terminal_list
from src.options import Options
from src.scanner import scan
from parser import parse
from src.semantic import get_symbol_table

import json

options = Options(sys.argv, "files/")

scan(options)
sat = parse(options, get_grammar(), get_terminal_list())
symbol_table =get_symbol_table(sat)

print(
    json.dumps(
        symbol_table,
        indent=4,
        separators=(",", ": ")
    )
)
