import csv
import json
import argparse
from pprint import pformat

class Student:
    def __init__(self, username, firstname, surname, email, group, git):
        self.username = username
        self.firstname = firstname
        self.surname = surname
        self.fullname = " ".join([self.firstname, self.surname])
        self.email = email
        self.group = group
        self.git = git
        self.userid = "".join(self.fullname.split())

    def as_dict(self):
        return self.userid, dict(name=self.fullname,folder=self.userid, email=self.email, group=self.group, git=self.git)

    def __str__(self):
        return f"Student {self.userid}:\n  Name: {self.fullname}  Email: \n{self.email}\n  Group: {self.group}\n  Git: {self.git}"

    def __repr__(self):
        return f"Student({self.username}, {self.firstname}, {self.surname}, {self.email}, {self.group}, {self.git})"


def main(args):
    with open(args["csv"], "r") as f:
        csvfile = csv.reader(f)
        next(csvfile, None)
        students = [Student(*st) for st in csvfile]

    print(students)
    students_final = [s.as_dict() for s in students]
    students_final = {s[0]: s[1] for s in students_final}

    print(pformat(dict(students=students_final)))

    print(f"Writing {len(students_final)} student/s to {args['outfile']}")

    with open(args["outfile"], "w") as f:
        json.dump(students_final, f)

    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Create a basic student config json from a csv.")
    parser.add_argument("csv", help="A csv file containing student data.", nargs="?",
                        const="../data/students.csv", default="../data/students.csv")
    parser.add_argument("outfile", help="A json file containing the overarching marking configuration.", nargs="?",
                        const="../data/test_students_auto_fromcsv.json", default="../data/test_students_auto_fromcsv.json")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)