"""Shared paths, loaders and study definitions for the whole team (WP1, WP2, WP3).

Every script in this repository imports from here, so that the population, the
outcome and the town groups are defined once and everybody agrees on them.

The data is not copied into this repository. It lives in the course repository
(https://github.com/kon0925/hy489), which has to be cloned next to this one, or
pointed to with the environment variable HY489_COURSE_REPO.
"""

from __future__ import annotations

import csv
import hashlib
import hmac
import os
import sys
from datetime import date

# The Windows console is not UTF-8 by default; the reports print ✔ ✘ ⚠.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUTS = os.path.join(ROOT, "outputs")


# ----------------------------------------------------------------------
# where the course repository is
# ----------------------------------------------------------------------
def course_repo() -> str:
    """Find the clone of the course repository.

    Order: HY489_COURSE_REPO, then a folder called hy489 one, two or three
    levels above this repository (our local layout is HY489/hy489 next to
    HY489/project_2_teamD/<this repository>).
    """
    env = os.environ.get("HY489_COURSE_REPO")
    candidates = [env] if env else []
    for up in ("..", os.path.join("..", ".."), os.path.join("..", "..", "..")):
        candidates.append(os.path.join(ROOT, up, "hy489"))
    for c in candidates:
        if c and os.path.exists(os.path.join(c, "labs", "lab01", "data", "patients.csv")):
            return os.path.normpath(c)
    sys.exit("Cannot find the course repository.\n"
             "Clone https://github.com/kon0925/hy489 next to this repository,\n"
             "or set HY489_COURSE_REPO to the folder of your clone.")


def data_path(name: str) -> str:
    return os.path.join(course_repo(), "labs", "lab01", "data", name)


def read_csv(name: str) -> list[dict]:
    with open(data_path(name), newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


# ----------------------------------------------------------------------
# the study, defined once
# ----------------------------------------------------------------------
# Hypertension: either of the two SNOMED CT codes the cohort uses.
HYPERTENSION_CODES = {
    "59621000": "Essential hypertension",
    "38341003": "Hypertensive disorder, systemic arterial",
}
SYSTOLIC = "8480-6"     # LOINC Systolic blood pressure
DIASTOLIC = "8462-4"    # LOINC Diastolic blood pressure

# The outcome is measured on the most recent pair of readings in this window.
WINDOW_START = "2024-01-01"
MIN_AGE = 18

# Controlled = systolic below 140 AND diastolic below 90 mmHg.
SBP_LIMIT = 140
DBP_LIMIT = 90

# The comparison the researchers care about.
LARGE_TOWNS = ["Heraklion", "Chania"]
SMALL_TOWNS = ["Rethymno", "Agios Nikolaos", "Sitia", "Ierapetra"]
TOWN_GROUP = {**{t: "large" for t in LARGE_TOWNS}, **{t: "small" for t in SMALL_TOWNS}}

# Age bands used by the researchers' analysis.
AGE_BANDS = [(18, 39, "18-39"), (40, 59, "40-59"), (60, 79, "60-79"), (80, 200, "80+")]


def age_band(age: int) -> str:
    for lo, hi, label in AGE_BANDS:
        if lo <= age <= hi:
            return label
    raise ValueError("age %r is outside every band" % age)


def age_on(birth: str, on: str) -> int:
    b, d = date.fromisoformat(birth[:10]), date.fromisoformat(on[:10])
    return d.year - b.year - ((d.month, d.day) < (b.month, b.day))


# ----------------------------------------------------------------------
# pseudonyms
# ----------------------------------------------------------------------
# A keyed pseudonym (Lab 5): without the key nobody can recompute it from the
# patient Id, and the hospital keeps the key. The default key is for
# development only; set HY489_PSEUDONYM_KEY to the custodian's real key.
DEV_KEY = "hy489-teamD-development-key-not-secret"


def pseudonym(patient_id: str) -> str:
    key = os.environ.get("HY489_PSEUDONYM_KEY", DEV_KEY).encode()
    return hmac.new(key, patient_id.encode(), hashlib.sha256).hexdigest()[:12]
