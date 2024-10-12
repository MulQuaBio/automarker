#!/usr/bin/env python
import argparse
import json
import os
from pprint import pformat
from collections import Counter
import plotext as plt

def count_deduction_reasons(d):
    reasons = []
    for module in d.values():
        reasons += module.get("deductions", {}).get("reasons", [])
    return reasons
def main(args):
    with open(args["results"], "r") as f:
        results = json.load(f)

    # barplot = plt.bar
    barplot = plt.simple_bar
    if args["simple"]:
        barplot = plt.simple_bar

    # Count all different error classes
    reasons = []
    for v in results.values():
        reasons += count_deduction_reasons(v)
        for w in v.values():
            reasons += count_deduction_reasons(w)
    counted_reasons = Counter(reasons)
    counted_reasons = {k: v for k, v in sorted(counted_reasons.items(), key=lambda item: item[1], reverse=True)}
    barplot(counted_reasons.keys(), counted_reasons.values(), width = plt.tw()-5)
    plt.theme("clear")
    plt.show()
    # plt.themes()
    # Find all analysed weeks

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Print vital statistics from a marking results json.")
    parser.add_argument("results", help="The results json file to analyse", nargs="?",
                        const="results/overall_results.json", default="results/overall_results.json")
    parser.add_argument("-s", "--simple", action="store_true", help="simple plots")

    arglist = parser.parse_args()
    arglist = vars(arglist)
    main(arglist)