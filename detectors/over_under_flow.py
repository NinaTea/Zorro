"""
Zk cryptography often involves modular arithmetic over a scalar field. This means that all operations are done modulo the order of the field. Circom circuits are built over a scalar field with the following order:

p = 21888242871839275222246405745257275088548364400416034343698204186575808495617

It’s easy to forget this fact, and not account for over/under flows. This means that the following arithmetic statements are true in Circom:

(0 - 1) === 21888242871839275222246405745257275088548364400416034343698204186575808495616;

(21888242871839275222246405745257275088548364400416034343698204186575808495616 + 1) === 0;

This can cause unintended consequences if there are no checks preventing these patterns.

Attack Scenario

For example, consider the following circuit that computes a user’s new balance:

template getNewBalance() {
   signal input currentBalance;
   signal input withdrawAmount;
   signal output newBalance;

   newBalance <== currentBalance - withdrawAmount;
}

If a user inputs a withdrawAmount that is greater than their currentBalance, the newBalance output will underflow and will be an extremely large number close to p. This is clearly not what was intended by the circuit writer.

The fix

We can use the LessThan and Num2Bits templates defined by Circomlib to ensure the values we are working with are within the correct bounds, and will not cause overflows or underflows:

// Ensure that both values are positive.
component n2b1 = Num2Bits(64);
n2b1.in <== withdrawAmount;

component n2b2 = Num2Bits(64);
n2b2.in <== currentBalance;

// Ensure that withdrawAmount <= currentBalance.
component lt = LessThan(64);
lt.in[0] = withdrawAmount;
lt.in[1] = currentBalance + 1;
lt.out === 1;

Here, Num2Bits(n) is used as a range check to ensure that the input lies in the interval [0, 2^n). In particular, if n is small enough this ensures that the input is positive. If we forgot these range checks a malicious user could input a withdrawAmount equal to p - 1. This would satisfy the constraints defined by LessThan as long as the current balance is non-negative since p - 1 = -1 < currentBalance.

"""
from tree_sitter import Node
from visitor import Visitor


class ToDoComment(Visitor):

    def __init__(self, print_output: bool = True):
        super().__init__(print_output)
        self.MSG = "Remove TODO: comment before deploying contract"
        self.HELP = None
        self.FOOTNOTE = None

    def visit_node(self, node: Node, run_number: int):
        if node.grammar_name == "comment":
            if "todo" in node.text.decode("utf-8"):
                # print("Remove TODO comment")
                self.add_finding(node, node)
