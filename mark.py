import argparse
import importlib
import importlib.util
import json
import logging
import os
import sys
from logging import exception
from pathlib import Path
from datetime import datetime
from pprint import pformat
try:
    from tqdm import tqdm
except ImportError:
    def tqdm(x, *args, **kwargs):
        # Return transparent tqdm wrapper just to make sure everything works even if tqdm is not installed
        return x

def ohhimark():
    x = """
...................................................&&&&&........................
...........................................&..........&&&.......................
..........................................&............&&&&.....................
........................................&&&............&&&&&....................
........................................&&..............&&&&&...................
........................................&&.....&.......&&&&&&...................
........................................&&.............&&&&&&&..................
.......................................&&&...&&&......&&&&&&&&..................
.......................................&&&............&&&&&&&&..................
......................................&&&&&..........&&&&&&&&&..................
......................................&&&&&&.......&&&&&&&&&&&&.................
......................................&&&&&&&........&&&&&&&&&&.................
......................................&&&&&&&........&&&&&&&&&&&&...............
....................................&&&&&&&&&........&&&&&&&&&&&&&..............
.................................&&&&&&&&&&&&&&......&&&&&&&&&&&&&&&&...........
.............................&&&&&&&&&&&&&&&&&&&.....&&&&&&&&&&&&&&&&&&&........
...........................&&&&&&&&&&&&&&&&&&&&&....&&&&&&&&&&&&&&&&&&&&&.......
..........................&&&&&&&&&&&&&&&&&&&&.....&&&&&&&&&&&&&&&&&&&&&&&......
.........................&&&&&&&&&&&&&&&&&&&&&&..&&&&&&&&&&&&&&&&&&&&&&&&&......
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&......
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.....
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.....
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&....
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&....
........................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...
.......................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...
.......................&&&&&&&&&&&&&&&&&&&&&&&&&.......&&&&&&&&&&&&&&&&&&&&&....
......................&&&&&&&&&&&&&&&&&&&&&&&&...........&&&&&&&&&&&&&&&&&&&....
......................&&&&&&&&&&&&&&&&&&&&&&&&............&&&&&&&&&&&&&&&&&&....
......................&&&&&&&&&&&&&&&&&&&&&&&&&&.........&&&&&&&&&&&&&&&&&&&....
......................&&&&&&&&&&&&&&&&&&&&&&&&&&&&.......&&&&&&&&&&&&&&&&&&&....
.....................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&.....
.....................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&......
.....................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&........
.....................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&..........
.....................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&...........
...................&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&............
               ____  _       _     _                        _    
              / __ \| |     | |   (_)                      | |   
             | |  | | |__   | |__  _   _ __ ___   __ _ _ __| | __
             | |  | | '_ \  | '_ \| | | '_ ` _ \ / _` | '__| |/ /
             | |__| | | | | | | | | | | | | | | | (_| | |  |   < 
              \____/|_| |_| |_| |_|_| |_| |_| |_|\__,_|_|  |_|\_\ 
"""
    return x


class CustomFormatter(logging.Formatter):
    grey = "\033[37m"
    cyan = "\033[96m"
    yellow = "\033[93m"
    red = "\033[31m"
    bold_red = "\033[91;1m"
    reset = "\033[0m"
    format = "%(asctime)s - %(filename)s - %(levelname)s: %(message)s"

    FORMATS = {
        logging.DEBUG: grey + format + reset,
        logging.INFO: cyan + format + reset,
        logging.WARNING: yellow + format + reset,
        logging.ERROR: red + format + reset,
        logging.CRITICAL: bold_red + format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


logger = logging.getLogger("mark")
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(CustomFormatter())
logger.addHandler(ch)

pathstub = ""

def weekchecker(fileloc, studentfolder, modulefolder, module_config):
    """Check the structure and contents of a module folder.

    :param fileloc: general location of student work.
    :param studentfolder: folder containing specific student work.
    :param modulefolder: folder that should contain module assignments.
    :param module_config: configuration dict containing module config data.
    :return:
    """

    deductions = {"value": 0, "reasons": []}

    abs_studentfolder = os.path.join(fileloc, studentfolder)
    abs_modulefolder = os.path.join(abs_studentfolder, modulefolder)
    logger.info("  General check of {}...".format(abs_modulefolder))

    # Check that folder is present
    if not os.path.exists(abs_modulefolder):
        logger.warning("  {} does not exist! Trying to find alternate variants...".format(abs_modulefolder))
        # studentfolder_contents = os.listdir(abs_studentfolder)
        # logger.debug(pformat(studentfolder_contents))
        localfolders = []
        # Find top level dirs
        for (dirpath, dirnames, filenames) in os.walk(abs_studentfolder):
            localfolders = dirnames
            break
        matchingfolders = [folder for folder in localfolders if folder.lower() == modulefolder.lower()]
        if len(matchingfolders) > 0:
            modulefolder = matchingfolders[0]
            logger.info("  Found probable alternate folder: {}!".format(modulefolder))
            abs_modulefolder = os.path.join(abs_studentfolder, modulefolder)
        else:
            logger.critical("  Could not find appropriate folder!")
            deductions["value"] += 100
            deductions["reasons"].append("no_folder")

            return True, None, None, None, None, deductions

    # Check for README
    modulecontents_folders = []
    modulecontents_files = []
    # Find module-level files and directories
    for (dirpath, dirnames, filenames) in os.walk(abs_modulefolder):
        modulecontents_folders = dirnames
        modulecontents_files = filenames
        break
    readmes = [name for name in modulecontents_files if "readme" in name.lower()]
    if len(readmes) == 0:
        logger.warning("  No module-level readme detected!")
        deductions["value"] += 1
        deductions["reasons"].append("no_readme")
    else:
        logger.info("  Found module-level readme: {}".format(readmes[0]))

    ## MODULE LEVEL GITIGNORES ARE NOT _REQUIRED_
    # gitignores = [name for name in modulecontents_files if ".gitignore" in name.lower()]
    # if len(gitignores) == 0:
    #     logger.warning("  No module-level gitignore detected!")
    #     # TODO: Dock points
    # else:
    #     logger.info("  Found module-level gitignore: {}".format(gitignores[0]))

    # Check for proper file structure
    code_folders = [name for name in modulecontents_folders if "code" in name.lower()]
    data_folders = [name for name in modulecontents_folders if "data" in name.lower()]
    results_folders = [name for name in modulecontents_folders if "results" in name.lower()]
    if len(code_folders) == 0:
        logger.critical("  No code folder detected!")
        return True, None, None, None, None, 0
    if len(data_folders) == 0:
        logger.warning("  No data folder detected!")
        deductions["value"] += 1
        deductions["reasons"].append("no_data_folder")
    if len(results_folders) == 0:
        logger.warning("  No results folder detected!")
        newresults = "results"
        try:
            # Try to infer the naming scheme that the student is using
            if code_folders[0].isupper():
                newresults = "RESULTS"
            elif code_folders[0][0].isupper():
                newresults = "Results"
        except IndexError:
            pass
        logger.warning("  Creating results folder '{}' based on assumed folder naming scheme...".format(newresults))
        os.mkdir(os.path.join(abs_modulefolder, newresults))
        results_folders = [newresults]

    # Decide on final names of internal folders for later use.
    final_codefolder = code_folders[0]
    final_datafolder = data_folders[0]
    final_resultsfolder = results_folders[0]

    # Check for unwanted files in results
    results_files = os.listdir(os.path.join(abs_modulefolder, final_resultsfolder))
    results_files = [file for file in results_files if file not in [".gitkeep", ".gitignore"]]
    if len(results_files) > 0:
        logger.warning("  Found {} file/s in results folder: {}".format(len(results_files), pformat(results_files)))
        logger.warning("  Docking 0.5pts per results file ({} total)".format(len(results_files) * 0.5))
        deductions["value"] += len(results_files) * 0.5
        deductions["reasons"].append("extra_results_files")
    else:
        logger.info("  Results folder empty, good!")
    # Check for unwanted files elsewhere?
    # Create list of expected files for this module
    expected_files = [".gitignore", "readme.md", "readme.txt", "readme" ".gitkeep"] + list(module_config["tests"].keys()) + module_config["extra_files"]
    expected_files = [file.lower() for file in expected_files]
    # Get files in code folder
    code_files = [file.lower() for _,_,files in os.walk(os.path.join(abs_modulefolder, final_codefolder)) for file in files]
    code_files = [file for file in code_files if not file.startswith(".")]

    # Find unwanted files
    extra_code_files = list(set(code_files) - set(expected_files))
    if len(extra_code_files) > 0:
        logger.warning("  Found {} extra file/s in code folder: {}".format(len(extra_code_files), pformat(extra_code_files)))
        logger.warning("  Docking 0.5pts per extra code file ({} total)".format(len(extra_code_files) * 0.5))
        deductions["value"] += len(extra_code_files) * 0.5
        deductions["reasons"].append("extra_code_files")

    # return structure: fatal error?, code folder, data, results, deductions
    return False, modulefolder, final_codefolder, final_datafolder, final_resultsfolder, deductions

def repochecker(fileloc, studentfolder):
    """Check the structure and contents of a repo folder.

        :param fileloc: general location of student work.
        :param studentfolder: folder containing specific student work.
        :return:
        """
    deductions = {"value": 0, "reasons": []}

    abs_studentfolder = os.path.join(fileloc, studentfolder)

    if not os.path.isdir(abs_studentfolder):
        logger.critical("Repo missing entirely!")
        deductions = {"value": 100, "reasons": ["missing_repo"]}
        return True, deductions

    # Check for README
    modulecontents_files = []
    # Find module-level files and directories
    for (dirpath, dirnames, filenames) in os.walk(abs_studentfolder):
        modulecontents_files = filenames
        break
    readmes = [name for name in modulecontents_files if "readme" in name.lower()]

    if len(readmes) == 0:
        logger.warning("  No repo-level readme detected!")
        deductions["value"] += 1
        deductions["reasons"].append("no_repo_readme")
    else:
        logger.info("  Found repo-level readme: {}".format(readmes[0]))

    # MODULE LEVEL GITIGNORES ARE NOT _REQUIRED_
    gitignores = [name for name in modulecontents_files if ".gitignore" in name.lower()]
    if len(gitignores) == 0:
        logger.warning("  No repo-level gitignore detected!")
        deductions["value"] += 1
        deductions["reasons"].append("no_repo_gitignore")
    else:
        logger.info("  Found repo-level gitignore: {}".format(gitignores[0]))

    # Find files larger than 100MB
    # Slightly hacky way to format these nice and quick
    largefiles = [str(Path(*Path(os.path.join(foldername, file)).parts[2:]))
                  for foldername, subfolders, filenames in os.walk(abs_studentfolder)
                  for file in filenames
                  if os.path.getsize(os.path.join(foldername, file)) > 100000000]
    largefiles = [file for file in largefiles if not file.startswith(".git/")]

    if len(largefiles) > 0:
        logger.warning("  Found large {} file/s in repo folder (>100MB), -1pt per file\n{}".format(len(largefiles), pformat(largefiles)))
        deductions["value"] += 1 * len(largefiles)
        deductions["reasons"].append("large_files")

    return False, deductions


def main(args):
    starttime = datetime.now()
    # First of all check to see if there's a place to put output and logs.
    logger.debug("Checking output dir")
    if not os.path.exists(args["outputloc"]):
        logger.warning("Output location not found! Creating...")
        os.makedirs(args["outputloc"])
    logdir = os.path.join(args["outputloc"], "logs")
    if not os.path.exists(logdir):
        logger.info("Creating log folder...")
        os.makedirs(logdir)

    # Init logging file handler
    fh = logging.FileHandler(os.path.join(logdir, "mark.log"), mode="w")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s"))
    logger.addHandler(fh)

    if args["debug"]:
        logger.setLevel(logging.DEBUG)
        logger.warning("Running in debug mode...")
        logger.debug("Args: \n%s", pformat(args))
        logger.debug(ohhimark())

    logger.info("Loading JSON files...")

    logger.debug("Loading students...")
    with open(args["students"]) as f:
        students = json.load(f)
    logger.debug("Loading config...")
    with open(args["config"]) as f:
        config = json.load(f)
    logger.debug("Loaded JSON files:\n{}\n{}".format(pformat(students), pformat(config)))

    overall_results_dict = {}
    # Main loop through config
    for studentid,studentspec in students["students"].items():
        # Set up student level logger
        sfh = logging.FileHandler(os.path.join(logdir, f"{studentid}.log"), mode="w")
        sfh.setLevel(logging.INFO)
        sfh.setFormatter(logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s: %(message)s"))
        logger.addHandler(sfh)

        logger.info("Marking {}...".format(studentspec["name"]))
        repo_results_raw = repochecker(args["fileloc"], studentspec["folder"])
        repo_results = {"deductions": repo_results_raw[1]}
        student_results_dict = {"repo_results": repo_results}

        for moduleid, modulespec in config.items():
            if repo_results_raw[0]:
                # Just skip through if the repo has a catastrophic error.
                continue
            logger.info("  Marking {}...".format(moduleid))
            module_results_dict = {}

            # Load test config
            testloc = os.path.join(pathstub, modulespec["test_location"])
            with open(os.path.join(testloc, f"{modulespec['name']}_config.json")) as f:
                module_config = json.load(f)
            module_tests = module_config["tests"]

            # Check week structure if arg given, possibly identify alternate names for code, data, and results folders if required
            weekchecker_results = weekchecker(args["fileloc"], studentspec["folder"], modulespec["folder"], module_config)
            module_results_dict["weekchecker_results"] = {"deductions": weekchecker_results[5]}

            if weekchecker_results[0]:
                logger.critical("Fatal error at week level for {}, skipping...".format(moduleid))
                student_results_dict[moduleid] = module_results_dict
                continue

            # Add detected folder name and week level folder names to module spec
            modulespec["folder"] = weekchecker_results[1]
            modulespec["codeloc"] = weekchecker_results[2]
            modulespec["dataloc"] = weekchecker_results[3]
            modulespec["resultsloc"] = weekchecker_results[4]

            # At this point we load each test module in turn using importlib.
            for targetfile, testspec in module_tests.items():
                # Load test module and run main function
                try:
                    testmodule = importlib.import_module(f"tests.{modulespec['name']}.{os.path.splitext(testspec['testfile'])[0]}")
                except ModuleNotFoundError as e:
                    logger.critical("CONFIG ERROR - test file '{}' not found! Skipping...".format(testspec['testfile']))
                    logger.critical("Expected based upon {}_config.json: \n    '{}': {}".format(modulespec['name'], targetfile, pformat(testspec)))
                    continue
                try:
                    runout, lintout, deductions, other = testmodule.main(args["fileloc"], targetfile, studentspec, modulespec, testspec)
                except Exception as e:
                    logger.debug("TEST ERROR")
                    logger.debug(e, exc_info=True)
                    raise
                # Pack test results into module results dict
                module_results_dict[targetfile] = {"stdout": runout, "linterout": lintout, "deductions": deductions, "other": other}

            # Pack module results into student results dict
            student_results_dict[moduleid] = module_results_dict

        # Pack student results into overall results
        overall_results_dict[studentid] = student_results_dict
        # Get rid of student level logger
        logger.removeHandler(logger.handlers[-1])

    # Finishing up
    # logger.info(pformat(overall_results_dict))
    endtime = datetime.now()
    elapsed = endtime - starttime
    logger.info("Finished marking in {}".format(elapsed))
    logger.info("Done!")
    # Save file to output location for further parsing
    with open(os.path.join(args["outputloc"], "overall_results.json"), "w") as f:
        json.dump(overall_results_dict, f)
    return overall_results_dict

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Mark a set of files according to a grading structure.")
    parser.add_argument("students", help="A json file specifying students to mark.", nargs="?", const="data/test_students.json", default="data/test_students.json")
    parser.add_argument("config", help="A json file containing the overarching marking configuration.", nargs="?", const="data/test_config.json", default="data/test_config.json")
    parser.add_argument("fileloc", help="The folder containing student work.", nargs="?",
                        const="data", default="data")
    parser.add_argument("outputloc", help="The folder within which to write output and logs.", nargs="?",
                        const="results", default="results")
    parser.add_argument("-d", "--debug", action="store_true", help="enable debugging information")
    parser.add_argument("-n", "--noweekcheck", action="store_true", help="do not check directory structure (could cause later tests to fail unexpectedly, currently unused)")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)