#!/usr/bin/env python3
"""WP1 · Score our data access request with the Week 10 Five Safes rubric.

    python3 request/score_request.py

Uses the fifteen criteria and the decision rule exactly as they are in the
course repository (lectures/week10/request.py), so the score is the course's
rubric and not one we wrote to suit ourselves.

Two versions of the same request are scored:

  as_submitted     what the research group asked for in its email
  with_conditions  the same project once the conditions we attach are met
                   (signed agreement, ethics approval, minimised and protected
                   extract, output checking and a release register)

Writes outputs/request_score.md.
"""

from __future__ import annotations

import importlib.util
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C  # noqa: E402


def load_rubric():
    path = os.path.join(C.course_repo(), "lectures", "week10", "request.py")
    spec = importlib.util.spec_from_file_location("week10_request", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


AS_SUBMITTED = {
    "key": "bp_submitted",
    "short": "BP control by town, as submitted",
    "title": "Blood pressure control in small vs large towns of Crete (as submitted)",
    "applicant": "Public health research group, a Greek university medical school (fictional)",
    "asks_for": "patients.csv without names, with full date of birth, sex, town and postcode; "
                "all hypertension diagnoses; every blood pressure reading with its date; "
                "antihypertensive prescriptions; the patient Id to join them",
    "purpose": "whether blood pressure control is worse in the smaller towns, by age band and sex",
    "setting": "the group's shared university file server",
    "outputs": "a journal article and a conference poster",
    "findings": {
        "P1": (0, "the PhD student who will run the analysis has no accredited researcher training"),
        "P2": (1, "a named principal investigator and a university that can be held to account"),
        "P3": (0, "no data access agreement yet; the request arrived as a letter"),
        "J1": (0, "ethics application submitted to the university committee, not yet approved"),
        "J2": (1, "unequal hypertension care across Crete is a public health question with a public answer"),
        "J3": (0, "full date of birth, postcode, prescriptions and every reading exceed the stated analysis"),
        "S1": (0, "the university file server is not operated by the hospital"),
        "S2": (0, "the request is for a record-level copy to leave the hospital"),
        "S3": (0, "the shared drive has no access log that anybody reads"),
        "D1": (1, "names, SSN, address and contact fields are not requested"),
        "D2": (0, "the hospital patient Id joins every table and any other release made with it"),
        "D3": (0, "full date of birth and postcode for a question asked by age band and town"),
        "O1": (1, "an article and a poster are aggregate"),
        "O2": (0, "only the co-authors read the tables before publication"),
        "O3": (0, "no record of what has already been published from the data"),
    },
}

WITH_CONDITIONS = {
    "key": "bp_conditions",
    "short": "BP control by town, with our conditions",
    "title": "Blood pressure control in small vs large towns of Crete (with conditions met)",
    "applicant": AS_SUBMITTED["applicant"],
    "asks_for": "one row per patient: age, sex, town and controlled yes/no, derived by the hospital "
                "and then generalised and suppressed by WP2; no identifier of any kind",
    "purpose": AS_SUBMITTED["purpose"],
    "setting": "a named, access-controlled university server; the copy is destroyed at the end",
    "outputs": "aggregate tables and model summaries, checked by the hospital before publication",
    "findings": {
        "P1": (1, "condition: the analyst completes accredited researcher training before access"),
        "P2": (1, "a named principal investigator and a university that can be held to account"),
        "P3": (1, "condition: a signed data access agreement with named sanctions and an audit right"),
        "J1": (1, "condition: ethics approval granted; basis GDPR Art 6(1)(e) with Art 9(2)(j) and Art 89 safeguards"),
        "J2": (1, "unequal hypertension care across Crete is a public health question with a public answer"),
        "J3": (1, "minimised to the four columns the analysis uses (see request.md)"),
        "S1": (0, "still the university's server, not the hospital's: a safeguarded release, not a TRE"),
        "S2": (0, "a record-level file still leaves the hospital; this is why the data itself must be protected"),
        "S3": (1, "condition: access to the folder is logged and the PI reviews the log monthly"),
        "D1": (1, "no direct identifiers in the extract"),
        "D2": (1, "no patient Id and no pseudonym in the release; the hospital alone keeps the keyed pseudonym"),
        "D3": (1, "age instead of date of birth, no dates at all, no postcode; generalised further by WP2"),
        "O1": (1, "only aggregate tables and model summaries may be published"),
        "O2": (1, "condition: every output is checked by the hospital custodians against the output rule"),
        "O3": (1, "condition: a cumulative release register is kept and consulted (WP3)"),
    },
}


def report(rubric, req):
    scores = {s: rubric.safe_score(req, s) for s in rubric.SAFES}
    decision, why = rubric.decide(req)
    L = ["## %s" % req["title"], "",
         "- **Applicant:** %s" % req["applicant"],
         "- **Asks for:** %s" % req["asks_for"],
         "- **Purpose:** %s" % req["purpose"],
         "- **Setting:** %s" % req["setting"],
         "- **Outputs:** %s" % req["outputs"], "",
         "| safe | criterion | met | reason |", "|---|---|---|---|"]
    for safe, cid, text, _ in rubric.CRITERIA:
        met, reason = req["findings"][cid]
        L.append("| %s | %s: %s | %s | %s |" % (safe, cid, text, "✔" if met else "✘", reason))
    L += ["", "Per safe: " + " · ".join("%s %d/3" % (s, scores[s]) for s in rubric.SAFES),
          "", "**Total %d/15 → %s** (%s)" % (rubric.total(req), decision, why)]
    unmet = rubric.conditions(req)
    if unmet:
        L += ["", "Criteria still not met, and what the rubric would ask for:"]
        L += ["- %s: %s" % (cid, what) for cid, what in unmet]
    return "\n".join(L)


def main():
    rubric = load_rubric()
    md = "# Five Safes score of our request (Week 10 rubric)\n\n" + \
         "\n\n".join(report(rubric, r) for r in (AS_SUBMITTED, WITH_CONDITIONS)) + "\n"
    os.makedirs(C.OUTPUTS, exist_ok=True)
    with open(os.path.join(C.OUTPUTS, "request_score.md"), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
