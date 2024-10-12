import logging
import os
import subprocess
from base64 import b64decode
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
    # demo TIF base64-encoded raw bytes
    tifstr = (
        b'SUkqABQAAAAAAAD///////8AAAARAAABAwABAAAAAgAAAAEBAwABAAAAAgAAAAIBAwADAAAA9gAAAAMBAwABAAAAAQAAAAYBAwABAAAA'
        b'AgAAABEBBAABAAAACAAAABIBAwABAAAAAQAAABUBAwABAAAAAwAAABYBAwABAAAAgAAAABcBBAABAAAADAAAABoBBQABAAAA5gAAABsB'
        b'BQABAAAA7gAAABwBAwABAAAAAQAAAB0BAgALAAAAogMAACgBAwABAAAAAgAAAFMBAwADAAAA/AAAAHOHBwCgAgAAAgEAAAAAAAAsAQAA'
        b'AQAAACwBAAABAAAACAAIAAgAAQABAAEAAAACoGxjbXMEMAAAbW50clJHQiBYWVogB+gACgAIAA4AFgAuYWNzcE1TRlQAAAAAAAAAAAAA'
        b'AAAAAAAAAAAAAAAAAAAAAPbWAAEAAAAA0y1sY21zAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAN'
        b'ZGVzYwAAASAAAABAY3BydAAAAWAAAAA2d3RwdAAAAZgAAAAUY2hhZAAAAawAAAAsclhZWgAAAdgAAAAUYlhZWgAAAewAAAAUZ1hZWgAA'
        b'AgAAAAAUclRSQwAAAhQAAAAgZ1RSQwAAAhQAAAAgYlRSQwAAAhQAAAAgY2hybQAAAjQAAAAkZG1uZAAAAlgAAAAkZG1kZAAAAnwAAAAk'
        b'bWx1YwAAAAAAAAABAAAADGVuVVMAAAAkAAAAHABHAEkATQBQACAAYgB1AGkAbAB0AC0AaQBuACAAcwBSAEcAQm1sdWMAAAAAAAAAAQAA'
        b'AAxlblVTAAAAGgAAABwAUAB1AGIAbABpAGMAIABEAG8AbQBhAGkAbgAAWFlaIAAAAAAAAPbWAAEAAAAA0y1zZjMyAAAAAAABDEIAAAXe'
        b'///zJQAAB5MAAP2Q///7of///aIAAAPcAADAblhZWiAAAAAAAABvoAAAOPUAAAOQWFlaIAAAAAAAACSfAAAPhAAAtsRYWVogAAAAAAAA'
        b'YpcAALeHAAAY2XBhcmEAAAAAAAMAAAACZmYAAPKnAAANWQAAE9AAAApbY2hybQAAAAAAAwAAAACj1wAAVHwAAEzNAACZmgAAJmcAAA9c'
        b'bWx1YwAAAAAAAAABAAAADGVuVVMAAAAIAAAAHABHAEkATQBQbWx1YwAAAAAAAAABAAAADGVuVVMAAAAIAAAAHABzAFIARwBCQmFja2dy'
        b'b3VuZAA=')

    with open(os.path.join(codedirpath, "test.tif"), "wb") as f:
        f.write(b64decode(tifstr))

    # Run script
    starttime = datetime.now()
    try:
        run_result = subprocess.run(f"bash {targetfile} test.tif", cwd=codedirpath, shell=True, text=True, timeout = timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    except subprocess.TimeoutExpired as e:
        timedout = True
        run_result = e
        logger.critical("{} timed out! -1 point".format(targetfile))
        deductions["value"] += 1
        deductions["reasons"].append("timeout")
    endtime = datetime.now()

    # Verify
    # Evaluate veracity
    verify_out = subprocess.run(f"file ../{modulespec['dataloc']}/test.png -b", cwd=codedirpath, shell=True, text=True,
                                timeout=timeout,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    verify_out_alt = subprocess.run(f"file ../{modulespec['codeloc']}/test.png -b", cwd=codedirpath, shell=True,
                                    text=True,
                                    timeout=timeout,
                                    stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

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
            logger.debug("Error:\n{}".format(run_result.stdout))
            deductions["value"] += 1
            deductions["reasons"].append("run_error")

        elif not verify_out.stdout.strip().startswith("PNG image data") and not verify_out_alt.stdout.strip().startswith("PNG image data"):
            logger.warning("{} gave possibly incorrect output. -0.5 points".format(targetfile))
            deductions["value"] += 0.5
            deductions["reasons"].append("result_error")
        run_stdout = run_result.stdout

    # Cleanup
    # <CLEANUP CODE HERE>
    for x in ["test.tif", "test.png"]:
        try:
            os.remove(os.path.join(datadirpath, x))
            logger.debug("Removed {}".format(os.path.join(datadirpath, x)))
        except FileNotFoundError:
            pass

    for x in ["test.tif", "test.png"]:
        try:
            os.remove(os.path.join(codedirpath, x))
            logger.debug("Removed {}".format(os.path.join(codedirpath, x)))
        except FileNotFoundError:
            pass

    return run_stdout, linter_result.stdout, deductions, other
