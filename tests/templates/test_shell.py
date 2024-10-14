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

    # Setup (if required)
    # <SETUP CODE HERE>

    # Run script
    starttime = datetime.now()
    try:
        teststr = f"bash {targetfile}"
        logger.info("Running {} using following command: {}".format(targetfile, teststr))
        run_result = subprocess.run(teststr, cwd=codedirpath, shell=True, text=True, timeout = timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired as e:
        timedout = True
        run_result = e
        logger.critical("{} timed out! -1 point".format(targetfile))
        deductions["value"] += 1
        deductions["reasons"].append("timeout")
    endtime = datetime.now()

    # Verify
    # <VERACITY CODE HERE>

    # Parse exec time
    elapsed = endtime - starttime
    other["exectime_s"] = elapsed.total_seconds()
    logger.info("Ran {} in {}".format(targetfile, elapsed))

    # Check error code
    if timedout:
        run_stdout = run_result.stdout.decode()
    else:
        if run_result.returncode != 0:
            logger.critical("{} errored! -1 point".format(targetfile))
            logger.critical("Error:\n{}".format(run_result.stdout))
            deductions["value"] += 1
            deductions["reasons"].append("run_error")
        run_stdout = run_result.stdout
        # Evaluate veracity
        # <VERACITY EVALUATION CODE HERE>

    # Cleanup
    # <CLEANUP CODE HERE>
    # for x in []:
    #     try:
    #         os.remove(os.path.join(datadirpath, x))
    #         logger.debug("Removed {}".format(os.path.join(datadirpath, x)))
    #     except FileNotFoundError:
    #         pass

    return run_stdout, linter_result.stdout, deductions, other
