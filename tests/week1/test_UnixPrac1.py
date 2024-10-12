import logging
import os
from pathlib import Path

logger = logging.getLogger("mark")

def main(filelocation, targetfile,studentspec, modulespec, testspec):
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

    return "", "", deductions, other