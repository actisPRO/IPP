![BUT FIT logo](https://wis.fit.vutbr.cz/images/fitnewben.png)

# Principles of Programming Languages 

**Author**: Denis Karev ([xkarev00@stud.fit.vutbr.cz](mailto:xkarev00@stud.fit.vutbr.cz))

**This project should not be used for non-educational purposes.**

*This file contains documentation for interpret.py and test.php.*

# Execution

To run interpreter use the following command:
```
python3.8 interpret.py
```
To run tester use the following command:
```
php8.1 parse.php
```

Both scripts support various arguments, information about those arguments 
can be retrieved using the `--help` argument.

# Interpreter

Interpreter consists of several files and classes.

## interpret.py

`interpret.py` is the main executable file of the interpreter. It is responsible for
processing command-line arguments, general exception handling (for unexpected errors 
with code 99) and instance creation of the `Interpreter` class.

## Interpreter

`interpreter.py` contains `Intepreter` class definition. This class loads source code in the
XML format and input from the file (or `stdin`). It also performs some validation checks on XML.
As input might have unsorted instructions with random `order` values, this class forcefully
sorts them and maps to increasing by 1 sequence.
After everything is loaded and checks are finished, code can by executed using `Context.execute()`.

## Context

Context represents the current state of code execution. It also contains some helper methods 
for defining, updating and getting variables from frames.

## Instruction

Every instruction is hard-coded as a method of this class. There is an `if-elif-else` sequence 
in the `execute` method which is used to determine the function to execute.
This is not the most elegant solution to represent instructions, but it works fine for such a tiny
language as IPPcode22.

There are some helper classes for type-checking and mathematical operations:

* `TypeChecker` contains some methods for validating types.
* `ArithmeticEvaluator` is an abstraction layer between arithmetic instructions and Python arithmetic
operations.
* `LogicEvaluator` is an `ArithmeticEvaluator` but for logic instructions.

## Variable

This class represent variables and constants. Every value is stored as a string and the class 
includes methods for wrapping and unwrapping Python-typed values.

## Extensions 

Some extensions were implemented.

* `FLOAT` adds a `float` type which supports mathematical operations.
* `STATI` adds some arguments for collecting statistics (see `--help`)
* `STACK` adds some instructions for working with stack. Arithmetic and logic instructions 
also use evaluators.

## Tester

Tester has relatively simple logic comparing to the interpreter. 

It loads test names search for test files (ending with `.src`) in the specified directory or 
loads them from the specified file (if `--testlist` is set).

Test name is a path to the test, but it does not contain any file extension. It is added dynamically later.

After test are collected, they are executed one-by-one. 
External scripts are executed using the `exec` function. The stderr is redirected to the `%testname%.%scriptname%.stderr`
file, which is removed after execution if `--noclean` is not turned on.

Execution result is stored in an array with the following fields:
* `out` - stdout of the script.
* `stderr` - stderr of the script.
* `type` - can be `xml` or `text`.
* `code` - exit code.

After the execution of the parser and interpreter, exit code is compared with the reference. 
If they are equal, but not 0, test is finished.

If exit code is 0, script output is compared with the reference output using `JExamlXML` for the parser output and 
`diff` for the interpreter output.

Test output is stored in an array with the following fields:
* `success` - true, if passed or false, if failed.
* `message` - if test has failed, contains the information about the reason.
* `stderr` - stderr of the script.
* `path` - test path without file extensions.
* `expected` - reference output
* `actual` - stdout of the script.
* `difference` - content of the `delta.xml` for XML files or `diff` output for text.

Some fields might not exist, depending on the failure reasons.

After the test execution, an HTML file is generated. It contains some basic CSS styles for better representation
and a small JavaScript function which allows user to show only failed or passed tests.
