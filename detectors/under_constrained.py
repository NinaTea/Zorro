from tree_sitter import Node
from visitor import Visitor


class Signal():
    def __init__(self, name, node):
        self.name = name              # Signal identifier
        self.node = node

        # Constraints
        self.is_constrained = False

        # Assignments
        self.is_assigned = False

        self.assignment_node = None

    def mark_assigned(self):
        self.is_assigned = True

    def mark_constrained(self):
        self.is_constrained = True


class AssignedButNotConstrainedDetector(Visitor):
    """
    Detects signals that are assigned using <-- but never constrained.

    Example vulnerable pattern:
        signal temp;
        temp <-- in * 2;  // Assignment without constraint
        out <== temp;     // temp can be ANY value!

    Fix: Use <== instead of <-- or add explicit constraint:
        temp <== in * 2;  // Correct
        // OR
        temp <-- in * 2;
        temp === in * 2;  // Explicit constraint
    """

    def __init__(self, print_output: bool = True):
        super().__init__(print_output)
        self.MSG = "Signal is assigned (<--) but never constrained."
        self.HELP = "Use <== instead of <-- or add an explicit constraint using ===."
        self.FOOTNOTE = "Signals assigned without constraints can be set to arbitrary values, leading to soundness vulnerabilities."
        self.signals = {}

    def extract_signal_name(self, node: Node) -> str | None:
        """Extract the name from the signal declaration statement"""
        for i in range(node.child_count):
            child = node.child(i)
            if child.grammar_name == "identifier":
                return child.text.decode()
        return None

    def visit_node(self, node: Node, run_number: int):

        if run_number == 4:
            if node.grammar_name == "signal_declaration_statement":
                signal_name = self.extract_signal_name(node)
                if signal_name:
                    self.signals[signal_name] = Signal(signal_name, node)

        # Second pass: Track constraints and assignments
        elif run_number > 4:
            if node.grammar_name == "assignment_expression":
                self.process_assignment(node)

    def process_assignment(self, node: Node):
        """Process assignment expressions and track <-- vs <=="""
        if node.child_count < 3:
            return

        left = node.child(0)
        operator = node.child(1).text.decode()
        # TODO: Revise this case: "a * b === 1" declarations are not being taken into account

        left_signal = left.text.decode()

        if left_signal and left_signal in self.signals:

            if operator in ["<--", "-->", "="]:
                self.signals[left_signal].mark_assigned()
                self.signals[left_signal].assignment_node = left

            if operator in ["<==", "==>", "==="]:
                self.signals[left_signal].mark_constrained()
                self.signals[left_signal].mark_assigned()

    def post_process(self):
        """Check for signals assigned with <-- but never constrained"""

        for signal_name, signal in self.signals.items():
            if signal.is_assigned and not signal.is_constrained:
                self.MSG = f"Signal '{signal_name}' is assigned (<--) but never constrained."
                self.HELP = f"Use <== instead of <-- or add an explicit constraint (===) for signal '{signal_name}'."
                self.add_finding(
                    signal.assignment_node if signal.assignment_node else signal.node,
                    signal.assignment_node if signal.assignment_node else signal.node
                )
