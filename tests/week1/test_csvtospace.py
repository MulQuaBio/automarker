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

    # Setup
    _ = subprocess.run(f"echo '1,hello,goodbye,hmm\n5,6,7,8' > ../{modulespec['dataloc']}/testcsv.csv", cwd=codedirpath, shell=True,
                       text=True, timeout=timeout,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # Run script
    starttime = datetime.now()
    try:
        # run
        teststr = f"bash {targetfile} ../{modulespec['dataloc']}/testcsv.csv"
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
    # Verify csv output using `file` command of bash.
    try:
        # verify_out = subprocess.run(f"file ../{modulespec['dataloc']}/testtsv.csv -b", cwd=codedirpath, shell=True, text=True,
        #                             timeout=timeout,
        #                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        # verify_out_alt = subprocess.run(f"file ../{modulespec['dataloc']}/testtsv.tsv.csv -b", cwd=codedirpath, shell=True, text=True,
        #                                 timeout=timeout,
        #                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        # Using grep instead to verify number of tabs (should be 0)
        verify_out = []
        for x in [
            f"{modulespec['dataloc']}/testcsv.txt",
            f"{modulespec['dataloc']}/testcsv.csv.txt",
            f"{modulespec['resultsloc']}/testcsv.txt",
            f"{modulespec['resultsloc']}/testcsv.csv.txt",
            f"{modulespec['codeloc']}/testcsv.txt",
            f"{modulespec['codeloc']}/testcsv.csv.txt"
        ]:
            verify_out.append((x, subprocess.run(f"grep -o -P ',' ../{x}  | wc -l",
                                        cwd=codedirpath, shell=True,
                                        text=True,
                                        timeout=timeout,
                                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT).stdout.strip()))
    except subprocess.TimeoutExpired as e:
        logger.critical("MARKER ERROR - {} verification timed out!".format(targetfile))

    # Parse exec time
    elapsed = endtime - starttime
    other["exectime_s"] = elapsed.total_seconds()
    logger.info("Ran {} in {}".format(targetfile, elapsed))

    # Check error code
    if timedout:
        run_stdout = run_result.stdout.decode()
    else:
        # Wrap up
        if run_result.returncode != 0:
            logger.critical("{} errored! -1 point".format(targetfile))
            logger.critical("Error:\n{}".format(run_result.stdout))
            deductions["value"] += 1
            deductions["reasons"].append("run_error")

        elif all([v[1] != "0" for v in verify_out]):
            logger.warning("{} gave possibly incorrect output. -0.5 points".format(targetfile))
            logger.info("One of these should have been a 0 with no error:\n{}".format("\n".join([f'{v[0]}: {v[1]}' for v in verify_out])))
            deductions["value"] += 0.5
            deductions["reasons"].append("result_error")

        run_stdout = run_result.stdout

    # Cleanup
    for x in ["testcsv.csv", "testcsv.txt", "testcsv.csv.txt"]:
        for y in [datadirpath, resultsdirpath, codedirpath]:
            try:
                os.remove(os.path.join(y, x))
                logger.debug("Removed {}".format(os.path.join(y, x)))
            except FileNotFoundError:
                pass

    return run_stdout, linter_result.stdout, deductions, other
