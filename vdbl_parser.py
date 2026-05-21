# VDBL Parser

import lark
import vdbl_grammar_lark as grammar
import vdbl_trans

parser = lark.Lark(grammar.VDBL_GRAMMAR, parser="lalr", start="start")

def parse(text : str):
    tree = parser.parse(text)
    return vdbl_trans.ASTBuilder().transform(tree)


