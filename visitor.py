import math
import sys
from dataclasses import dataclass
from typing import Optional
from tree_sitter import Node


@dataclass
class Location:
    lineno: int
    start_tabs: int
    span: tuple[int, int]
    line_code: str


@dataclass
class Finding:
    marked_nodes: (Node, Node)
    visitor: str
    source: str
    msg: str
    help_msg: Optional[str]
    footnote: Optional[str]
    location: Optional[Location]


def pretty_print_warn(visitor, parent: Node, specific_node: Node, msg: str, help_msg: str | None,
                      footnote: str | None, leading_context: int, trailing_context: int):
    line_number = parent.start_point[0] + 1
    num_size_spaces = " " * (int(math.log10(line_number)) + 2)

    all_lines = visitor.source.split('\n')
    total_lines = len(all_lines)

    start_line = max(0, line_number - leading_context - 1)
    end_line = min(total_lines, line_number + trailing_context)

    print(f"Warning:{msg}")
    print(f" {num_size_spaces}|")

    for i in range(start_line, end_line):
        current_line = i + 1
        contract_code = all_lines[i]
        start_tabs = contract_code.count('\t') + 1
        contract_code = contract_code.replace('\t', '    ')

        print(
            f" {current_line} |{contract_code}")

        if current_line == line_number:
            arrows = "^" * (specific_node.end_point[1] -
                            specific_node.start_point[1])
            spaces = " " * \
                ((specific_node.start_point[1] * start_tabs) + 1)
            print(f" {num_size_spaces}|{spaces}{arrows}")
            if help_msg is not None:
                print(
                    f" {num_size_spaces}|{spaces}{help_msg}")

    if footnote is not None:
        print(f" {num_size_spaces}Note:{footnote}")

    print()


class Visitor:
    source: str | None
    MSG: str
    HELP: str | None
    FOOTNOTE: str | None
    print_output: bool
    ignores: dict[str, ([int], Node)]
    leading_context: int
    trailing_context: int

    def __init__(self, print_output: bool, ):
        self.ignores = {}
        self.source = self.src_name = None
        self.findings = []
        self.print_output = print_output

    def set_context(self, leading: int, trailing: int):
        self.leading_context = leading
        self.trailing_context = trailing

    def add_source(self, src: str, src_name: str = None):
        self.source = src
        self.src_name = src_name

    def set_ignores(self, ignores):
        self.ignores = ignores

    # noinspection PyShadowingBuiltins
    def visit_node(self, node: Node, round: int):
        sys.exit("visit_node not implemented")

    def get_contract_code_lines(self):
        return self.source.split('\n')

    def add_finding(self, node: Node, specific_node: Node):
        if self.finding_is_ignored(node):
            return

        if self.print_output:
            pretty_print_warn(self, node, specific_node, self.MSG, self.HELP,
                              self.FOOTNOTE, self.leading_context, self.trailing_context)

        parent = node.parent
        line_number = parent.start_point[0] + 1

        line_code = self.get_contract_code_lines()[line_number - 1]
        location = Location(parent.start_point[0] + 1,
                            line_code.count('\t') + 1,
                            (node.start_point[1], node.end_point[1]),
                            self.get_contract_code_lines()[line_number - 1])
        finding = Finding((node, specific_node), self.Name,
                          self.src_name, self.MSG, self.HELP, self.FOOTNOTE, location)
        self.findings.append(finding)
        return sorted(self.findings, key=lambda f: f.location.lineno)

    def get_findings(self):
        return self.findings

    def get_ignored_findings(self):
        return self.ignores

    def finding_is_ignored(self, node):
        line_node = node.start_point[0]

        if self.Name in self.ignores and line_node in self.ignores[self.Name][0]:
            self.ignores[self.Name][0].remove(line_node)
            return True

        return False

    @property
    def Name(self):
        return self.__class__.__name__
