import os
import sys
from pprint import pformat

def find_imports(p):
    with open(p, "r") as f:
        lines = [line.strip().split(" ")[1] for line in f.readlines() if line.strip().startswith(("import ", "from "))]
    return lines


def main():
    """Find non-standard imports used within py files in this dir.

    :return:
    """
    os.chdir("..")
    ignoredirs = ["data", "venv"]
    found_files = []
    for roots, dirs, files in os.walk("."):
        try:
            if roots.split("/")[1] not in ignoredirs:
                pyfiles = [os.path.join(roots, file) for file in files if os.path.splitext(file)[1] == ".py"]
                found_files += pyfiles
        except IndexError:
            pyfiles = [os.path.join(roots, file) for file in files if os.path.splitext(file)[1] == ".py"]
            found_files += pyfiles

    imports = []
    for x in found_files:
        imports += find_imports(x)
    imports_filtered = [i for i in list(set(imports)) if i.split(".")[0] not in sys.stdlib_module_names]
    return imports_filtered


if __name__ == '__main__':
    print(pformat(main()))