from tree_sitter import Node
from visitor import Visitor
import re


class ToDoComment(Visitor):

    def __init__(self, print_output: bool = True):
        super().__init__(print_output)
        self.MSG = "Remove TODO: comment before deploying circuit"
        self.HELP = None
        self.FOOTNOTE = None

    def visit_node(self, node: Node, run_number: int):
        # TODO: fix that 6.
        if run_number == 6:
            if node.grammar_name == "comment":
                text = node.text.decode("utf-8")[2:]
                if re.search(r"^todo:|TODO:|TODO", text):
                    self.add_finding(node, node)
