import tree_sitter_circom as tscircom
from node_iterator import NodeIterator
from visitor import Visitor
from tree_sitter import Language, Parser, Tree, Node

import re

CIRCOM = Language(
    "tree-sitter-circom/build/lib.linux-x86_64-cpython-310/tree_sitter_circom/_binding.abi3.so", "circom")

__TIMES__ = 3


class LinterRunner:
    source: str
    tree: Tree
    root_node: Node
    iterator: NodeIterator
    lints: list[Visitor]
    round_number: int

    def __init__(self, source: str, print_output: bool, src_name: str):
        self.source = source
        self.print_output = print_output
        self.src_name = src_name
        parser = Parser()
        parser.set_language(CIRCOM)
        self.tree = parser.parse(bytes(self.source, "utf8"))
        self.root_node = self.tree.root_node
        self.iterator = NodeIterator(self.root_node)
        self.lints = []
        self.round_number = __TIMES__

    def add_lint(self, lint):
        self.lints.append(lint)
        return self

    def add_lints(self, lint_classes: list[Visitor], leading: int, trailing: int):
        for lint_class in lint_classes:
            lint = lint_class(self.print_output)
            lint.set_context(leading, trailing)
            lint.add_source(self.source, self.src_name)
            self.lints.append(lint)

    def run_lints(self, node: Node):
        for lint in self.lints:
            lint.visit_node(node, self.round_number)

    def reset_cursor(self):
        self.iterator = NodeIterator(self.root_node)

    def run(self):

        for i in range(__TIMES__):
            self.round_number = self.round_number + 1

            for node in self.iterator:
                self.run_lints(node)
            self.reset_cursor()

        # Call post_process method for lints that have it
        for lint in self.lints:

            if hasattr(lint, 'post_process'):
                lint.post_process()

        return [finding for lint in self.lints
                for finding in lint.get_findings()]
