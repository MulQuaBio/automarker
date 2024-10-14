import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path

logger = logging.getLogger("mark")

def main(filelocation, targetfile,studentspec, modulespec, testspec):
    timedout = False
    # Default timeout of 10m.
    timeout = testspec.get('timeout', 600)
    deductions = {"value": 0, "reasons": []}
    other = {}

    target_lines = 0
    final_lines = 0

    logger.info("Testing {}".format(targetfile))

    # Set up code paths
    moduledirpath = os.path.join(filelocation, studentspec["folder"], modulespec["folder"])
    codedirpath = os.path.join(moduledirpath, modulespec["codeloc"])
    datadirpath = os.path.join(moduledirpath, modulespec["dataloc"])
    resultsdirpath = os.path.join(moduledirpath, modulespec["resultsloc"])

    # Check if file is present
    filepath = Path(os.path.join(codedirpath, targetfile))
    if filepath.is_file():
        logger.debug("File {} present!".format(targetfile))
    else:
        # Try to find a matching but differently capitalised file
        potential_files = [file for file in os.listdir(codedirpath) if file.lower() == targetfile.lower()]
        if len(potential_files) > 0:
            targetfile = potential_files[0]
            logger.warning("Inferred target file as {}".format(targetfile))
        else:
            if not testspec["required"]:
                logger.warning("File {} absent but not required!".format(targetfile))
            else:
                logger.critical("File {} absent!".format(targetfile))
                deductions["value"] += 1
                deductions["reasons"].append("file_missing")
                return "File missing!", "File missing!", deductions, other

    # Lint
    linter_result = subprocess.run(f"shellcheck {targetfile}", cwd=codedirpath, shell=True, text=True, timeout = timeout,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    # Veracity setup
    target_wc = subprocess.run(f"wc -l < {targetfile}", cwd=codedirpath,
                               shell=True, text=True, timeout=timeout,
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    target_lines = int(target_wc.stdout.strip())
    logger.debug("{} lines in target.".format(target_lines))

    # Run script
    starttime = datetime.now()
    try:
        teststr = f"bash {targetfile} {targetfile} {targetfile} ../{modulespec['dataloc']}/testout.demo"
        logger.info("Running {} using following command: {}".format(targetfile, teststr))
        # Actually run script
        run_result = subprocess.run(teststr, cwd=codedirpath, shell=True, text=True, timeout = timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired as e:
        timedout = True
        run_result = e
        logger.critical("{} timed out! -1 point".format(targetfile))
        deductions["value"] += 1
        deductions["reasons"].append("timeout")
    endtime = datetime.now()

    # Parse exec time
    elapsed = endtime - starttime
    other["exectime_s"] = elapsed.total_seconds()
    logger.info("Ran {} in {}".format(targetfile, elapsed))

    # Veracity post-test
    #
    final_wc = subprocess.run(f"wc -l < ../{modulespec['dataloc']}/testout.demo", cwd=codedirpath,
                              shell=True, text=True, timeout=timeout,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    final_lines = 0
    try:
        final_lines = int(final_wc.stdout.strip())
        logger.debug("{} lines in final.".format(final_lines))
    except ValueError:
        logger.warning("Ouput file not found!")

    # Check error code
    if timedout:
        run_stdout = run_result.stdout.decode()
    else:
        if run_result.returncode != 0:
            logger.critical("{} errored! -1 point".format(targetfile))
            logger.critical("Error:\n{}".format(run_result.stdout))
            deductions["value"] += 1
            deductions["reasons"].append("run_error")

        # Veracity evaluation
        elif final_lines != target_lines*2:
            logger.critical("{} incorrect! expected {} lines, got {} lines. -1 point".format(targetfile, target_lines * 2, final_lines))
            deductions["value"] += 1
            deductions["reasons"].append("result_error")

        run_stdout = run_result.stdout

    # Cleanup
    for x in ["testout.demo"]:
        try:
            os.remove(os.path.join(datadirpath, x))
            logger.debug("Removed {}".format(os.path.join(datadirpath, x)))
        except FileNotFoundError:
            pass

    return run_stdout, linter_result.stdout, deductions, other
