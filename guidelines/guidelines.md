# Hi! Thank you for wanting to collaborate to open source

## Getting started

Create a new issue on Zorro repository with the name of the new detector or test case you wish to contribute. Then, link a new branch to that issue.


    ❗ Requirement: All detectors should follow the CamelCase naming convention.

## Detectors

To contribute a new detector:

1. Check the structure a new detector should follow  in `guidelines/template.py`.

2. Add your modified `template.py` file inside the detectors directory.

3. To check if your detector is working properly, run the following command `python3 zorro_analyzer_main.py tests/your_circuit.circom`

## Test Cases

When you create a new detector, please also add a new test case. To add a new one:

1. Create a new file in the tests directory. Remember to follow the naming convention for the file name.
2. Done!
