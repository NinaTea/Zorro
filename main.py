import tree_sitter_circom as tscircom
from tree_sitter import Language, Parser

# TODO FIX because this is deprecated
CIRCOM = Language(
    "tree-sitter-circom/build/lib.linux-x86_64-cpython-310/tree_sitter_circom/_binding.abi3.so", "circom")

parser = Parser()
parser.set_language(CIRCOM)

source_code = b"""
template Adder() {
    signal input a, b;
    signal output c;
    c <== a + b;
}
"""


tree = parser.parse(source_code)
root_node = tree.root_node

# Print the syntax tree
print(root_node.sexp())

# You can also traverse the tree


# def print_tree(node, indent=0):
#     print("  " * indent +
#           f"{node.type}: {node.text if len(node.children) == 0 else ''}")
#     for child in node.children:
#         print_tree(child, indent + 1)


# print("\n--- Tree Structure ---")
# print_tree(root_node)
