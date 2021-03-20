# Pylox Interpreter
An implementation of a tree walker interpreter for the Lox language from the book [Crafting Interpreters by Bob Nystrom](https://craftinginterpreters.com/index.html) in Python.
The interpreter can be used in two different modes:
1. REPL - statements & expressions are passed through the terminal. statements are executed while expressions are evaluated and displayed.
2. Passing a file as a command line argument.

# Progress
The interpreter is now complete. 

Challenges completed:

Chapter 6 - Parsing Expressions:
* [Comma operator](https://en.wikipedia.org/wiki/Comma_operator).
* [Ternary Operator](https://en.wikipedia.org/wiki/%3F:).
* Error reporting on binary operators missing a left-hand operand.

Chapter 7 - Evaluating Expressions:
* Added comparison operators to strings, chose not to allow comparison between mixed types.
* Added support for concatenating strings and numbers.
* Error report for division by zero.

Chapter 8 - Statements And State:
* REPL now works in the following way: statements are executed, while expressions are evaluted and displayed.
* Accessing an undefined variable is now a runtime error.

Chapter 9 - Control Flow:
* Added support for a break statement.

Chapter 10 - Functions:
* Lambda functions are now supported.

Chapter 11 - Resolving And Binding:
* An unused & defined variable now raises a runtime error.
* Changed implementation of an environment to a list instead of a dictionary.

Chapter 12 - Classes:
* Added [metaclasses](https://en.wikipedia.org/wiki/Metaclass), and through them added support for [class methods](https://en.wikipedia.org/wiki/Method_(computer_programming)#Class_methods).
* Added support for [get methods](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/get) - more info [here](https://craftinginterpreters.com/classes.html#challenges).

# Personal Additions
* Added a native input command - read(message) - message will be printed as a prompt for the user.
* Added a native array class which has the following methods:

  set(i, value) - if i is not nil then set value at index i, otherwise append value to the end.
  
  get(i) - returns the value at index i.
  
  length() - returns the length of the array.
* Changed print to be a native function.
