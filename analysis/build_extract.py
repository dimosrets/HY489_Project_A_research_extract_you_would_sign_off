#!/usr/bin/env python3
"""WP1 · Build the minimised analysis extract from the original cohort.

    python3 analysis/build_extract.py

Reads the five Lab 1 tables, applies the study definitions in common.py and
writes two files, one row per patient:

outputs/extract_minimised.csv   the minimised extract (input to WP2)
    rid         keyed pseudonym; for the custodians' bookkeeping only. WP2
                drops it (or re-keys it) before any release, WP3 uses it as
                the ground truth when scoring an attack
    age         age in whole years at the date of the outcome reading
    sex         F / M
    town        one of the six towns
    controlled  1 if systolic < 140 and diastolic < 90 mmHg, else 0

outputs/extract_custodian.csv   the same rows plus what the custodians used to
    derive the outcome and keep for checking: bp_date, sbp, dbp. Never released.

The minimised extract is NOT a release: it still holds exact ages and towns.

Also writes outputs/extract_flow.csv: who was excluded at each step and why.
"""

from __future__ import annotations

import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C  # noqa: E402

MINIMISED = ["rid", "age", "sex", "town", "controlled"]
CUSTODIAN = ["rid", "age", "sex", "town", "bp_date", "sbp", "dbp", "controlled"]


def build():
    patients = {r["Id"]: r for r in C.read_csv("patients.csv")}

    # first hypertension diagnosis per patient
    diagnosed = {}
    for r in C.read_csv("conditions.csv"):
        if r["CODE"] in C.HYPERTENSION_CODES:
            d = r["START"][:10]
            diagnosed[r["PATIENT"]] = min(diagnosed.get(r["PATIENT"], d), d)

    # blood pressure readings, paired by timestamp
    readings = {}
    for r in C.read_csv("observations.csv"):
        if r["CODE"] in (C.SYSTOLIC, C.DIASTOLIC) and r["PATIENT"] in diagnosed:
            readings.setdefault(r["PATIENT"], {}).setdefault(r["DATE"], {})[r["CODE"]] = float(r["VALUE"])

    flow = [("patients in the cohort", len(patients)),
            ("with a hypertension diagnosis", len(diagnosed))]

    rows, no_reading, child = [], 0, 0
    for pid, dx_date in diagnosed.items():
        start = max(C.WINDOW_START, dx_date)
        pairs = [(t, v) for t, v in readings.get(pid, {}).items()
                 if t[:10] >= start and C.SYSTOLIC in v and C.DIASTOLIC in v]
        if not pairs:
            no_reading += 1
            continue
        when, v = max(pairs)                       # the most recent pair
        p = patients[pid]
        age = C.age_on(p["BIRTHDATE"], when)
        if age < C.MIN_AGE:
            child += 1
            continue
        sbp, dbp = v[C.SYSTOLIC], v[C.DIASTOLIC]
        rows.append({
            "rid": C.pseudonym(pid),
            "age": age,
            "sex": p["GENDER"],
            "town": p["CITY"],
            "bp_date": when[:10],
            "sbp": int(round(sbp)),
            "dbp": int(round(dbp)),
            "controlled": int(sbp < C.SBP_LIMIT and dbp < C.DBP_LIMIT),
        })

    flow += [("  excluded: no BP pair after diagnosis and since %s" % C.WINDOW_START, -no_reading),
             ("  excluded: under %d at the outcome reading" % C.MIN_AGE, -child),
             ("in the analysis extract", len(rows))]
    rows.sort(key=lambda r: r["rid"])              # no order that leaks the source
    return rows, flow


def main():
    rows, flow = build()
    os.makedirs(C.OUTPUTS, exist_ok=True)
    for name, cols in (("extract_minimised.csv", MINIMISED), ("extract_custodian.csv", CUSTODIAN)):
        with open(os.path.join(C.OUTPUTS, name), "w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
    with open(os.path.join(C.OUTPUTS, "extract_flow.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["step", "patients"])
        w.writerows(flow)
    for step, n in flow:
        print("  %-62s %6d" % (step, n))
    print("\n  wrote outputs/extract_minimised.csv, extract_custodian.csv, extract_flow.csv")


if __name__ == "__main__":
    main()
