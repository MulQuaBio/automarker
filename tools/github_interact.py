import subprocess
import os
import sys
import logging
import json
import argparse
from pprint import pformat
import shutil
import multiprocessing
from math import ceil
from datetime import datetime

def download_student(student, datafolder, timeout):
    if not student["git"]:
        return f"No git defined for {student['name']}"
    if os.path.isdir(student["folder"]):
        shutil.rmtree(student["folder"])
    try:
        run_result = subprocess.run(f"git clone {student['git']} {student['folder']}", cwd=datafolder,
                                    shell=True, text=True, timeout=timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except Exception as e:
        return f"Git error: {str(e)}"
    return run_result.stdout


def main(args):
    timeout = 30
    with open(args["students"], "r") as f:
        students = json.load(f)["students"]
    print(pformat(students))
    os.chdir(args["datafolder"])
    outlist = []
    starttime = datetime.now()
    if args["multicore"]:
        cpus = max(multiprocessing.cpu_count() - 4, 1)
        print(f"Running on {cpus} CPUs")
        var_list = [[student, args["datafolder"], timeout] for student in students.values()]
        chunksize = int(ceil(len(var_list) / cpus))
        with multiprocessing.Pool(cpus) as p:
            for result in p.starmap(download_student, var_list, chunksize=chunksize):
                # print("Completed %s", result[0])
                outlist.append(result)
    else:
        for student in students.values():
            result = download_student(student, args["datafolder"], timeout)
            outlist.append(result)
    endtime = datetime.now()
    elapsed = endtime - starttime
    print(f"Ran in {elapsed.total_seconds()}s")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a basic student config json from a directory.")
    parser.add_argument("students", help="A json file containing the student configuration.", nargs="?",
                        const="../data/students.json", default="../data/students.json")
    parser.add_argument("datafolder", help="The folder to save data in.", nargs="?",
                        const="../data", default="../data")
    parser.add_argument("-m", "--multicore", action="store_true", help="enable multicore cloning.")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)