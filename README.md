# Automarker

This is an automarker developed from the ground-up to be used in conjunction with the materials contained within TheMulQuaBio. It has been designed to handle a wide variety of assignments in a number of coding languages, and to create structured output suitable for generating automated feedback for students by further extension.

## Dependencies

Currently, this package has minimal dependencies. However the presently required dependencies are listed below:

### Python
- `python >= 3.10`
- `plotext`
- `tqdm`
- `ruff`

### R
- `tidyverse`

> Note: you can get a list of currently imported python packages within the folder by running `python tools/find_deps.py` from the root dir. This specifically excludes dependencies in students' work.

## Structure

### Main marking script - `mark.py`
At the root of the repository lies the `mark.py` script. This is the main port of call when running marking. This script takes arguments as follows

```
usage: mark.py [-h] [-d] [students] [config] [fileloc] [outputloc]

Mark a set of files according to a grading structure.

positional arguments:
  students           A folder containing files to mark.
  config             A json file containing the overarching marking configuration.
  fileloc            The folder containing student work.
  outputloc          The folder within which to write output and logs.

options:
  -h, --help         show this help message and exit
  -d, --debug        enable debugging information
                     currently unused)
```

For example a typical run may look something like

`python mark.py -d data/students.json data/config.json data results`

### Student config generator - `make_students_json.py`
Also located at the root of the repository is a convenience script to make loading students easier. This script is configured as follows:

```
usage: make_students_json.py [-h] [dir] [outfile]

Create a basic student config json from a directory.

positional arguments:
  dir         A folder containing student folders to mark.
  outfile     A json file containing the overarching marking configuration.

options:
  -h, --help  show this help message and exit
```

A typical run may look like:

`python make_students_json.py data data/students.json`

### Marking statistics - `marking_statistics.py`
The other main script at the root of the repository parses the results json file from a run of `mark.py` and outputs some summary data about it. This is still very much a work in progress.

## Configuration files

There are 2 main configuration files that must be set in order to run `mark.py` (alongside further files per-week, more on those later).

### Course config - `config.json`
The main course config defines which modules of TheMulQuaBio are to be marked. If you only want to mark weeks 2 and 3 for example, here is where you would set this. It follows the following structure:

```json
{
  "<MODULEID>": {
    "name": "<MODULE NAME>",
    "test_location": "<MODULE TEST LOCATION>",
    "folder": "<MODULE FOLDER NAME>"
  },
  "<MODULE2ID>": {
    "name": "<MODULE 2 NAME>",
    "test_location": "<MODULE 2 TEST LOCATION>",
    "folder": "<MODULE 2 FOLDER NAME>"
  }
}
```

Here:

- `MODULEID` is simply an identifier and only used for logging and output formatting.
- `name` is the folder within `tests/` that contains the tests for that module.
- `test_location` is the full path to the folder that contains the tests for that module.
- `folder` is the folder within a student's submission that contains their work for this module.

> Note: Currently `name` and `test_location` are both required, though they contain very similar data and so will probably eventually not both be needed.

#### Example

```json
{
  "week1": {
    "name": "week1",
    "test_location": "tests/week1",
    "folder": "week1"
  }
}
```

### Student config - `students.json`
The student config file defines the students in the class.

```json
{
  "students": {
    "<STUDENTID>": {
      "name": "Firstname Surname",
      "folder":  "<STUDENT FOLDER>",
      "github": "<STUDENT GITHUB REPO>"
    },
    "STUDENTID2": {
      "name": "Firstname2 Surname2",
      "folder":  "<STUDENT 2 FOLDER>",
      "github": "<STUDENT 2 GITHUB REPO>"
    }
  }
}
```

Here:

- `STUDENTID` is simply an identifier and only used for logging and output formatting.
- `name` is the student's preferred name, again just used for logging.
- `folder` is the folder within the data folder (chosen in the args of `mark.py`) that contains this student's work.
- `github` is the url of this student's github repo. It is not presently used.

#### Example

```json
{
  "students": {
    "FrancisWindram": {
      "name": "Francis Windram",
      "folder":  "FrancisWindram_",
      "github": "..."
    },
    "DavidBridgwood": {
      "name": "David Bridgwood",
      "folder":  "DavidBridgwood_",
      "github": "..."
    }
  }
}
```

## Tests
Each test set is stored in the test folder. Within this folder are a set of tests (as `.py` files) to perform and a config file defining the relationship between tests and their source files.

Each test file contains the logic for testing a given assignment including static analysis(linting), veracity checks, and anything else that may be required. It may call subprocesses.

Every test file contains one function called `main()` which must accept 5 arguments:

- `filelocation` - _str_ - The location of the student data (chosen in the args of `mark.py`)
- `targetfile` - _str_ - The name of the file to test, loaded from the module-level config.
- `studentspec` - _dict_ - The data of the currently targeted student, pulled from `students.json`.
- `modulespec` - _dict_ - The metadata of the current module, pulled from `config.json`
- `testspec` - _dict_ - The data of the current test, pulled from the module-level config.

> Note: You do not generally have to worry about how the data is passed into these arguments (as that all happens within `mark.py`), however when writing tests it is important to know what information is available to your tester.

Every test file is also expected to return a tuple of four items:

- `run_stdout` - _str_ - The raw output from stdout generated by running the student script (if it succeeded). 
- `linter_result.stdout` - _str_ - The raw output from linting the student script. 
- `deductions` - _dict_ - A dictionary containing two values:
  - `value`: A numeric value for the total score deduction that this student should
  - `reasons`: A list of strings, one for each error type that occurred. (e.g. `["no_readme", "file_missing"]`)
- `other` - _dict_ - A place to return any arbitrary data from the test. This should at least contain a value called `exectime_s` specifying the time in seconds that execution of the script took to complete.

Aside from this, anything that you would like to do within your own test is your own choice. You can make it as complex or as simple as you would like.

### General tips and rules
- **_Never_** print using `print()`. This will _not_ appear when the test is running. Instead use logging.
- The base script creates a logger called `mark` which is set up appropriately. You should load this logger in the preamble of your test using `logger = logging.getLogger("mark")`
- When logging, anything you output at "INFO" level or higher will be visible to the student. Use the "DEBUG" logging level to output information that students should not see.
- If you are outputting iterables or large structures, it is worth using the `pformat` function from `pprint`. This attempts to nicely format the iterable within the log, which will make it much easier to see and understand.
  - For example `logger.debug(pformat(dict_to_output))`
- It is generally much-preferred to create test files within your test script. This makes the test fully portable and minimises the amount of data that must be uploaded to the repository.
  - This can sometimes require some inventive coding, but it is generally worth it at the end.
  - See `tests/week1/test_tiff2png.py` for an extreme example of this.
- Whenever you create files while testing, try to make sure these are removed after the test is complete (they can affect marks for repo-cleanness if testing is performed multiple times in succession).
- Check inside the `tests/templates` folder when writing a new test. This usually will contain a demo test wrapper for the type of file you are looking to test.
- Generally speaking the `test_shell.py` example can be used for testing most files at a basic level. You may wish to change the linter to a more appropriate one than `shellcheck` if you are not testing a bash script.
- Always set timeouts for subprocesses! You don't want to be wasting an hour testing only to find that a student decided to ask for input on line 2.
- If you are stuck on how to create your own test, look at the files in `tests/week1` for some functional tests to crib from.

### Test example
The basic format of a test is as follows:

```python
import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mark")
def main(filelocation, targetfile,studentspec, modulespec, testspec):
  
    run_stdout = ""
    linter_stdout = ""
    deductions = {}
    other = {}
    
    # Set up code paths

    # Check if file is present

    # Lint

    # Setup (if required)

    # Run script

    # Verify

    # Parse exec time

    # Check error code
        # Evaluate veracity

    # Cleanup
    return run_stdout, linter_stdout, deductions, other
```

## Module-level config - `modulename_config.json`
Each suite of tests lives in a folder (as described above). This folder must also contain a json file called `modulename_config.json`, so for week1 this would be `week1_config.json`.

This file takes the following form:

```json
{
  "name": "<MODULENAME>",
  "tests": {
    "FILE_TO_TEST.sh": {
      "testfile": "test_FILE_TO_TEST.py",
      "required": 1,
      "timeout": 5
    },
    "OPTIONAL_FILE2_TO_TEST.sh": {
      "testfile": "test_OPTIONAL_FILE2_TO_TEST.py",
      "required": 0,
      "timeout": 5
    }
  },
  "extra_files": ["FILE3_TO_IGNORE.tex", "FILE4_TO_IGNORE.bib"]
}
```

There are 3 keys at the top level of this file:

- `name` - _str_ - The `name` of the module, as specified in the `name` field of the module in `config.json`.
- `tests` - _dict_ -  A dictionary containing a set of test specifications, keyed by the name of the file to test.
- `extra_files` - _list_ - A list of file names that should be ignored when checking for errant files.

Within tests, each file to be tested should have an entry keyed by the name of the file. The other fields within each test specification are:
- `testfile` - _str_ - The name of the test file to use.
- `required` - _int_ - 1 if this file is required, 0 if not.
- `timeout` - _int_ or _float_ - The amount of time to allow the script to run for before considering it to have "timed out".

## Outputs
`mark.py` outputs a set of logs to the folder specified in the arguments. One of these (`mark.log`) is the overall log for the testing run, including DEBUG-level logs. The others are named as the student IDs, and contain the log for ONLY THAT STUDENT'S testing, at the INFO level.

The marking runner also outputs a json file into the results folder. This file contains a structured report of everything encountered when marking the work of the student.

## Useful data locations
There are some common variables that will be passed into every test. Here are the most useful ones for writing tests:

- `studentspec["folder"]` - The student's home folder
- `modulespec["folder"]` - The name of the folder for this module's work
- `modulespec["codeloc"]` - The student's code folder (within the module folder)
- `modulespec["dataloc"]` - The student's data folder (within the module folder)
- `modulespec["resultsloc"]` - The student's results folder (within the module folder)

Often it is worthwhile setting these up as full paths like so:
```python
moduledirpath = os.path.join(filelocation, studentspec["folder"], modulespec["folder"])
codedirpath = os.path.join(moduledirpath, modulespec["codeloc"])
datadirpath = os.path.join(moduledirpath, modulespec["dataloc"])
resultsdirpath = os.path.join(moduledirpath, modulespec["resultsloc"])
```

## TODO
- Add a first attempt at a json -> markdown parsing
- Github auto pull and auto feedback push
