from tree_sitter import Node
from visitor import Visitor


class Signal():
    name = ""
    has_range_check = False
    has_less_than = False
    is_input = False
    node = None
    is_used_in_substraction = False

    def __init__(self, name, signal_type, node):
        self.name = name
        self.is_input = signal_type == "input"
        self.node = node

    def has_range(self):
        self.has_range_check = True

    def has_less_than(self):
        self.has_less_than_check = True

    def is_used_in_subs(self):
        self.is_used_in_substraction = True


class Component():
    name = ""
    called = ""
    took_in = ""
    took_out = ""

    def __init__(self, name, called):
        self.name = name
        self.called = called

    def set_int(self, took_in):
        self.took_in = took_in

    def set_out(self, out):
        self.took_out = out


class InsecureSubstraction(Visitor):
    """
    A field element is a value in the domain of Z/pZ, where p is the prime number set by default to

    p = 21888242871839275222246405745257275088548364400416034343698204186575808495617.

    As such, field elements are operated in arithmetic modulo p.
    Because of this, (p + 1 == 0) and (0 - 1 = p) are both true.

    A secure substraction is given by checked ranges and correct use of libraries.
    > we need to check ranges
    > we need to ensure that second operand is less than the other one

    The idea is to check if bare input signals are used in substractions operations.

    """

    def __init__(self, print_output: bool = True):
        super().__init__(print_output)
        self.MSG = "This signal is used in a substraction operation but no range check is done before using it."
        self.HELP = "Consider using Num2Bits(n) before any operation."
        self.FOOTNOTE = None
        self.signals = {}
        self.components = {}

    def visit_node(self, node: Node, run_number: int):

        # We save all signals declared
        if node.type == "signal_declaration_statement" and node.child_count >= 3:
            try:
                signal_type = node.child(1).text.decode()
                signal_name = node.child(2).text.decode()
                self.signals[signal_name] = Signal(
                    signal_name, signal_type, node)
            except (AttributeError, IndexError):
                pass  # Skip if parsing fails

        # Track binary subtraction operations
        if node.type == "binary_expression" and node.child_count >= 3:
            try:
                left = node.child(0).text.decode()
                op = node.child(1).text.decode()
                right = node.child(2).text.decode()
                if op == "-":
                    if left in self.signals and right in self.signals:
                        self.signals[left].is_used_in_subs()
                        self.signals[right].is_used_in_subs()
            except (AttributeError, IndexError):
                pass  # Skip if parsing fails

        # Track Num2Bits component declarations
        if node.type == "component_declaration_statement" and node.child_count >= 4:
            try:
                comp_name = node.child(1).text.decode()
                template_called = node.child(3).text.decode()
                if "Num2Bits" in template_called:
                    self.components[comp_name] = Component(
                        comp_name, template_called)
            except (AttributeError, IndexError):
                pass  # Skip if parsing fails

        # Track assignments to components and -= operations
        if node.type == "assignment_expression" and node.child_count >= 3:
            try:
                # Check for component input assignments (comp.in <== signal)
                left_side = node.child(0)
                operator = node.child(1).text.decode()
                right_name = node.child(2).text.decode()

                if operator == "<==" and left_side.child_count >= 3:
                    comp_name = left_side.child(0).text.decode()
                    property_name = left_side.child(2).text.decode()

                    if comp_name in self.components and property_name == "in":
                        if right_name in self.signals:
                            self.signals[right_name].has_range()

                # Check for -= operations
                elif operator == "-=":
                    left = node.child(0).text.decode()
                    if left in self.signals and right_name in self.signals:
                        self.signals[left].is_used_in_subs()
                        self.signals[right_name].is_used_in_subs()

            except (AttributeError, IndexError):
                pass  # Skip if parsing fails

    def post_process(self):
        """Called after all nodes have been visited to perform final checks"""
        for signal in self.signals:

            if not self.signals[signal].has_range_check and self.signals[signal].is_input and self.signals[signal].is_used_in_substraction:
                self.add_finding(
                    self.signals[signal].node, self.signals[signal].node)
