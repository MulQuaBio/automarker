import subprocess
import os
import sys
import logging
import json
import argparse
from pprint import pformat
import shutil

def main(args):
    timeout = 30
    with open(args["students"], "r") as f:
        students = json.load(f)["students"]
    print(pformat(students))
    os.chdir(args["datafolder"])
    for student in students.values():
        print(student["folder"])
        print(student["git"])
        if not student["git"]:
            continue
        if os.path.isdir(student["folder"]):
            shutil.rmtree(student["folder"])
        try:
            run_result = subprocess.run(f"git clone {student['git']} {student['folder']}", cwd=args["datafolder"], shell=True, text=True, timeout=timeout,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print(run_result.stdout)
        except Exception as e:
            print(e)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a basic student config json from a directory.")
    parser.add_argument("students", help="A json file containing the student configuration.", nargs="?",
                        const="../data/test_students_auto_fromcsv.json", default="../data/students.json")
    parser.add_argument("datafolder", help="The folder to save data in.", nargs="?",
                        const="../data", default="../data")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)