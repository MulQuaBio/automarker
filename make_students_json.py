import argparse
import json
import logging
import os
from pprint import pformat


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

def main(args):
    for (dirpath, dirnames, filenames) in os.walk(args["dir"]):
        localfolders = dirnames
        break
    logger.info(f"Found {len(localfolders)} student/s")

    students = {}
    for student in localfolders:
        studentdict = {}
        studentdict["name"] = student.strip("_")
        studentdict["folder"] = student
        studentdict["github"] = "..."
        students[studentdict["name"]] = studentdict

    final_dict = {"students": students}
    logger.info(f"\n{pformat(final_dict)}")
    with open(args["outfile"], "w") as f:
        json.dump(final_dict, f)
    logger.info(f"Wrote students to {args['outfile']}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a basic student config json from a directory.")
    parser.add_argument("dir", help="A folder containing student folders to mark.", nargs="?",
                        const="data", default="data")
    parser.add_argument("outfile", help="A json file containing the overarching marking configuration.", nargs="?",
                        const="data/students.json", default="data/students.json")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)