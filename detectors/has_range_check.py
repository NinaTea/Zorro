from tree_sitter import Node
from visitor import Visitor


class Signal():

    def __init__(self, name, signal_type, node):
        self.name = name
        self.has_range_check = False
        self.is_input = signal_type == "input"
        self.is_output = signal_type == "output"
        self.node = node
        self.is_used_in_substraction = False
        self.from_long_div = False  
        self.arrow_assignment_node = None 

    def has_range(self):
        self.has_range_check = True

    def is_used_in_subs(self):
        self.is_used_in_substraction = True

    def mark_from_long_div(self, assignment_node):  
        self.from_long_div = True
        self.arrow_assignment_node = assignment_node


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


class HasRangeCheck(Visitor):
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
        self.MSG = "This signal is used in an arithmetic operation but no range check is done before using it."
        self.HELP = "Consider using Num2Bits(n) before any operation to check that it is still in range."
        self.FOOTNOTE = None
        self.signals = {}
        self.components = {}

    def visit_node(self, node: Node, run_number: int):


        if node.type == "signal_declaration_statement" and node.child_count >= 3:
            try:
                signal_type = node.child(1).text.decode()
                signal_name = node.child(2).text.decode()
                self.signals[signal_name] = Signal(
                    signal_name, signal_type, node)

            except (AttributeError, IndexError):
                print(f"[DEBUG] HasRangeCheck Failed: {e}")
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
                print(f"[DEBUG] HasRangeCheck Failed: {e}")
                pass  # Skip if parsing fails

        # Track Num2Bits component declarations
        if node.type == "component_declaration_statement" and node.child_count >= 4:
            try:
                comp_name = node.child(1).text.decode()
                template_called = node.child(3).text.decode()
                if "Num2Bits" in template_called:
                    self.components[comp_name] = Component(
                        comp_name, template_called)
                    # print(f"[DEBUG] Collected Num2Bits component: {comp_name}")
            except (AttributeError, IndexError):
                print(f"[DEBUG] HasRangeCheck Failed: {e}")
                pass  # Skip if parsing fails

        # Track assignments to components and -= operations
        if node.type == "assignment_expression" and node.child_count >= 3:
            try:
                # Check for component input assignments (comp.in <== signal)
                left_side = node.child(0)
                operator = node.child(1).text.decode()
                right_side = node.child(2)
                if operator == "<==" and left_side.child_count >= 3:
                    comp_name = left_side.child(0).text.decode()
                    property_name = left_side.child(2).text.decode()

                    if comp_name in self.components and property_name == "in":
                
                        right_name = None
                        if right_side.type == "identifier":
                            right_name = right_side.text.decode()
                        elif right_side.type == "array_access_expression":
                            # For mod[i], get "mod"
                            right_name = right_side.child(0).text.decode()

            
                        if right_name and right_name in self.signals:
                            self.signals[right_name].has_range()
                 

                # Check for -= operations
                elif operator == "-=":
                    left = node.child(0).text.decode()
                    right_name = right_side.text.decode()
                    if left in self.signals and right_name in self.signals:
                        self.signals[left].is_used_in_subs()
                        self.signals[right_name].is_used_in_subs()

                # Check for <-- assignments from long_div
                elif operator == "<--":
                    # Get signal name from left side 
                    left_name = None
                    if left_side.type == "identifier":
                        left_name = left_side.text.decode()
                    elif left_side.type == "array_access_expression":
                        # For mod[i], get "mod"
                        left_name = left_side.child(0).text.decode()

                    # Check if right side references "longdiv" variable
                    # The AST gives us just the identifier, not the full array access
                    right_text = right_side.text.decode()
                    is_from_longdiv = (right_text == "longdiv")
                    if left_name and is_from_longdiv:
                        if left_name in self.signals:
                            self.signals[left_name].mark_from_long_div(
                                node)
            except (AttributeError, IndexError) as e:
                print(f"[DEBUG] HasRangeCheck Failed: {e}")
                pass  # Skip if parsing fails

    def post_process(self):
        """Called after all nodes have been visited to perform final checks"""

        for signal_name, signal in self.signals.items():
 
            # check: input signals used in subtraction
            if not signal.has_range_check and signal.is_input and signal.is_used_in_substraction:
                
                self.add_finding(signal.node, signal.node)

            # check: signals from long_div without range check
    
            elif signal.from_long_div and not signal.has_range_check:
                
                if signal.arrow_assignment_node:
                    
                    self.add_finding(signal.arrow_assignment_node,
                                     signal.arrow_assignment_node)
                else:
                    
                    self.add_finding(signal.node, signal.node)
