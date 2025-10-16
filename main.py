import tree_sitter
import tree_sitter_circom


CIRCOM = tree_sitter.Language(tree_sitter_circom.language())

parser = tree_sitter.Parser()
parser.language = CIRCOM


source_code = b"""
template Adder() {
    signal input a, b;
    signal output c;
    c <== a + b;
}
"""

tree = parser.parse(source_code)
root_node = tree.root_node
print(root_node.str())
