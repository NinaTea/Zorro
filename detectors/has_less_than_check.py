from tree_sitter import Node
from visitor import Visitor


class Signal():
    def __init__(self, name, type, node):
        self.name = name
        self.is_input = type == "input"
        self.node = node
        self.has_less_than_check = False
        self.is_used_in_substraction = False
        self.is_minuend = False

    def mark_less_than_check(self):
        self.has_less_than_check = True

    def mark_used_in_substraction(self):
        self.is_used_in_substraction = True

    def mark_as_minuend(self):
        self.is_minuend = True


class Component():
    def __init__(self, name, called):
        self.name = name
        self.called = called


class LessThanCheck(Visitor):
    """
    Checks that subtractions have proper LessThan comparisons.

    """

    def __init__(self, print_output: bool = True):
        super().__init__(print_output)
        self.MSG = "This signal is used in a substraction but it has not been previously checked."
        self.HELP = "Consider using LessThan(n) to ensure the subtrahend is less than or equal to the minuend."
        self.FOOTNOTE = None
        self.signals = {}
        self.components = {}

    def visit_node(self, node: Node, run_number: int):

        if node.grammar_name == "signal_declaration_statement":
            signal_type = node.child(1).text.decode()
            signal_name = node.child(2).text.decode()
            self.signals[signal_name] = Signal(signal_name, signal_type, node)

        if node.grammar_name == "binary_expression" and node.child_count >= 3:
            left = node.child(0).text.decode()
            op = node.child(1).text.decode()
            right = node.child(2).text.decode()

            if op == "-":
                if left in self.signals:
                    self.signals[left].mark_as_minuend()
                    self.signals[left].mark_used_in_substraction()

                if right in self.signals:
                    self.signals[right].mark_used_in_substraction()

        # Track LessThan declarations
        if node.grammar_name == "component_declaration_statement":
            template_called = node.child(3).text.decode()
            if "LessThan" in template_called:
                comp_name = node.child(1).text.decode()
                self.components[comp_name] = Component(
                    comp_name, template_called)

        # Track LessThan input assignments
        if node.grammar_name == "assignment_expression" and node.child_count >= 3:
            # Check for pattern: lt.in[0] = signal or lt.in[1] = signal
            if node.child(0).grammar_name == "array_access_expression":
                # Get the member_expression (lt.in)
                member_expr = node.child(0).child(0)

                if member_expr.grammar_name == "member_expression":
                    comp_name = member_expr.child(0).text.decode()
                    member_name = member_expr.child(2).text.decode()

                    # Get the array index [0] or [1]
                    array_index = node.child(0).child(2).text.decode()
                    is_in0 = (array_index == "0")

                    if member_name == 'in' and comp_name in self.components:
                        assigned_value = node.child(2).text.decode()

                        base_signal = assigned_value.replace(
                            " ", "").split("+")[0].split("-")[0]

                        if base_signal in self.signals:
                            signal = self.signals[base_signal]
                            signal.mark_less_than_check()

    def post_process(self):
        """Check if all input signals used in subtractions have LessThan checks"""
        for signal_name, signal in self.signals.items():

            if (signal.is_input and
                signal.is_used_in_substraction and
                    not signal.has_less_than_check):

                self.add_finding(signal.node, signal.node)
