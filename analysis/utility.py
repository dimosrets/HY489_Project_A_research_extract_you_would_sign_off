#!/usr/bin/env python3
"""WP1 · How far does each candidate release move the researchers' answer?

    python3 analysis/utility.py release/R-k5.csv release/R-k10.csv release/R-k5-l2.csv

Runs the yardstick analysis (analysis/yardstick.py) on the original extract
and on every release given, and writes one row per release to
outputs/utility_table.csv and outputs/utility_table.md.

The columns, in the units the researchers care about:

  rows_lost_pct        share of the original patients missing from the release
                       (suppressed rows, or rows with the outcome suppressed)
  overall_pct          share controlled overall
  diff_pp, d_diff_pp   difference small - large in percentage points, and how
                       far it moved from the original
  or, or_ci            adjusted odds ratio small vs large and its 95% interval
  or_change_pct        relative change in the odds ratio
  same_conclusion      does the release lead to the same conclusion as the
                       original? (interval includes 1 in both, or excludes 1 on
                       the same side in both)
  cells_comparable     how many of the original's town group x age band x sex
                       cells can still be computed from the release
  cell_mae_pp          mean absolute error of the cell percentages, over the
                       cells that can be compared
"""

from __future__ import annotations

import csv
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import common as C  # noqa: E402
from yardstick import analyse  # noqa: E402

FIELDS = ["release", "rows", "rows_lost_pct", "overall_pct", "diff_pp", "d_diff_pp",
          "or", "or_ci", "or_change_pct", "same_conclusion", "cells_comparable", "cell_mae_pp"]


def conclusion(orr):
    if orr is None:
        return "no estimate"
    if orr["hi"] < 1:
        return "worse in small towns"
    if orr["lo"] > 1:
        return "better in small towns"
    return "no clear difference"


def row(name, res, base):
    n0 = base["overall"]["n"]
    orr, orr0 = res["odds_ratio_small_vs_large"], base["odds_ratio_small_vs_large"]
    cells0 = {(c["town_group"], c["age_band"], c["sex"]): c["pct"] for c in base["cells"]}
    cells = {(c["town_group"], c["age_band"], c["sex"]): c["pct"] for c in res["cells"]}
    common = [k for k in cells0 if k in cells]
    diff = res.get("difference_pp", {}).get("value")
    diff0 = base["difference_pp"]["value"]
    return {
        "release": name,
        "rows": res["rows"],
        "rows_lost_pct": round(100 * (1 - res["overall"]["n"] / n0), 1),
        "overall_pct": res["overall"]["pct"],
        "diff_pp": diff,
        "d_diff_pp": None if diff is None else round(diff - diff0, 1),
        "or": None if orr is None else round(orr["or"], 2),
        "or_ci": None if orr is None else "%.2f-%.2f" % (orr["lo"], orr["hi"]),
        "or_change_pct": None if orr is None else round(100 * (orr["or"] / orr0["or"] - 1), 1),
        "same_conclusion": "yes" if conclusion(orr) == conclusion(orr0) else "NO (%s)" % conclusion(orr),
        "cells_comparable": "%d/%d" % (len(common), len(cells0)),
        "cell_mae_pp": round(sum(abs(cells[k] - cells0[k]) for k in common) / len(common), 1) if common else None,
    }


def main():
    base_path = os.path.join(C.OUTPUTS, "extract_minimised.csv")
    if not os.path.exists(base_path):
        sys.exit("Run analysis/build_extract.py first.")
    base = analyse(pd.read_csv(base_path, dtype=str))
    rows = [row("original", base, base)]
    for path in sys.argv[1:]:
        rows.append(row(os.path.splitext(os.path.basename(path))[0], analyse(pd.read_csv(path, dtype=str)), base))

    with open(os.path.join(C.OUTPUTS, "utility_table.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    md = ["| " + " | ".join(FIELDS) + " |", "|" + "---|" * len(FIELDS)]
    md += ["| " + " | ".join("" if r[f] is None else str(r[f]) for f in FIELDS) + " |" for r in rows]
    with open(os.path.join(C.OUTPUTS, "utility_table.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(md) + "\n")
    print("\n".join(md))
    if len(sys.argv) == 1:
        print("\n  (no releases given: only the original row. Pass release CSV files as arguments.)")


if __name__ == "__main__":
    main()
