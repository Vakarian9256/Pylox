# Pylox Interpreter
An implementation of a tree walker interpreter for the Lox language from the book Crafting Interpreters by Bob Nystrom in Python.
The interpreter can be used in two different modes:
1. REPL, statements are executed while expressions are evaluated and displayed.
2. Passing a file as an argument.

# Progress
Finished chapters 1-11. 

Challenges completed:
* [Comma operator](https://en.wikipedia.org/wiki/Comma_operator)
* [Ternary Operator](https://en.wikipedia.org/wiki/%3F:)
* Error reporting on binary operators missing a left-hand operand.
* Added comparison operators to strings, chose not to allow comparison between mixed types.
* Added support for concatenating strings and numbers.
* Error report for division by zero.
* REPL now works in the following way: statements are executed, while expressions are evaluted and displayed.
* Accessing an undefined variable is now a runtime error.
* Added support for a break statement.
* Lambda functions are now supported.
* An unused & defined variable now raises a runtime error.
* Changed implementation of an environment to a list instead of a dictionary.
* Added metaclasses & static methods
