## Rationale
- Each test set is stored in the test folder
- Within this folder are a set of tests to perform and a config file defining the relationship between tests and their source files.
- Each test file contains one function called `main()` which takes the student configuration, target file, and test spec as arguments.
- Each test file contains the logic for testing a given assignment including static analysis(linting), veracity checks, and anything else that may be required. It may call subprocesses.
- The `mark.py` script is the entry point for all testing, providing a predictable interface for running tests.
- Running `mark.py` involves pointing it at two major files, the `students.json` configuration file, and the `config.json` file:
  - `students.json` contains the details of each student
  - `config.json` contains the configuration for which tests to run
  
## TODO
- Add documentation on implementing new tests
- Add a first attempt at a json -> markdown parsing
- Github auto pull and auto feedback push
