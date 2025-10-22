from tree_sitter import Node
from visitor import Visitor


class YourDtector(Visitor):

    """
    Implement the logic of your detector here
    """

    def __init__(self):
        super().__init__()
        self.MSG = "MSG"
        self.FOOTNOTE = "FOOTNOTE"
        self.HELP = "HELP"  # optional

    def visit_node(self, node, round_number):
        pass

    def post_process():
        pass
