<!-- ![alt text](logo/logo.png =100) -->


# <img src="logo/Diseño sin título(2).png" width="100"> Zorro - Static Analyzer for Circom DSL
------------

## WIP

This is a work in progress, feel free to contribute!
- [Guidelines](Guidelines/guidelines.md)


# Acknowledgements

All the vulnerabilities are from [zk-bug-tracker](https://github.com/0xPARC/zk-bug-tracker). Including examples and solutions.

This is software intended to detect unwated patterns or bad practices.

# How to use

1. Clone this repository
2. Make directory with your circuits
3. Run this command

```code
~/Zorro$ python3 zorro_analyzer_main.py <your_directory/>
```

example:
```code
~/Zorro$ python3 zorro_analyzer_main.py tests/
```

## Detectors
1. Bad practices
2. Arithmetic Over/Under Flows


| Detector | Bug Type | Test Cases |
-----------|----------|------------| 
| [to_do_comment](detectors/to_do_comment.py) | 1 | [1](tests/product_proof.circom) |
| [has_range_check](detectors/has_range_check.py) | 2 | [1](tests/insecure_substraction.circom) |
| [has_less_than_check](detectors/has_less_than_check.py) | 2 | [1](tests/has_range_but_no_less.circom) |