import argparse
import inspect
import os
import sys
from importlib.util import spec_from_file_location, module_from_spec

from linter_runner import LinterRunner
from visitor import Visitor, Finding


class Analyzer:
    DETECTOR_MAP = {}

    @staticmethod
    def find_detectors():
        found = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        detectors_dir = os.path.join(current_dir, 'detectors')

        for fname in os.listdir(detectors_dir):
            if not fname.endswith('.py') or fname == '__init__.py':
                continue

            module_name = fname[:-3]
            module_path = os.path.join(detectors_dir, fname)

            spec = spec_from_file_location(module_name, module_path)
            mod = module_from_spec(spec)
            spec.loader.exec_module(mod)

            for attr in dir(mod):
                if attr == 'Visitor':
                    continue
                obj = getattr(mod, attr)
                if inspect.isclass(obj) and issubclass(obj, Visitor):
                    found.append(obj)

        return {obj.__name__: obj for obj in found}

    def __init__(self):
        self.DETECTOR_MAP = self.find_detectors()
        self.isatty = sys.stdout.isatty()

    def main(self):
        parser = argparse.ArgumentParser(
            description='Zorro - Static Analyzer for Circom circuits')
        parser.add_argument(
            "path", type=str, nargs='?', default="tests",
            help="Path to the Circom circuit file or directory (default: tests)")

        args = parser.parse_args()

        detectors = list(self.DETECTOR_MAP.values())
        path = args.path

        if path.endswith(".circom"):
            self.lint_file(path, detectors, True, 0, 0)
        else:
            for root, _, files in os.walk(path):
                for file in files:
                    if file.endswith(".circom"):
                        self.lint_file(os.path.join(root, file),
                                       detectors, True, 0, 0)

    def lint_file(self, filename, lints: list[Visitor], print_output: bool, leading: int, trailing: int):

        if print_output:
            LIGHT_ORANGE = "\033[38;5;215m"  # Light orange
            RESET = "\033[0m"

            if self.isatty:
                print(f"{LIGHT_ORANGE}====== Linting {filename}... ======{RESET}")
            else:
                print(f"====== Linting {filename}... ======")
        with open(filename, 'r') as file:
            source = file.read()

        runner: LinterRunner = LinterRunner(source, print_output, filename)
        runner.add_lints(lints, leading, trailing)

        findings: list[Finding] = runner.run()

        return findings


if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.main()
