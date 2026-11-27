#!/usr/bin/env python3
"""WP1 · The researchers' analysis: the yardstick every release is judged by.

    python3 analysis/yardstick.py                       # on outputs/extract_minimised.csv
    python3 analysis/yardstick.py release/some_file.csv # on any candidate release

The question: is blood pressure control worse in the smaller towns of Crete
(Rethymno, Agios Nikolaos, Sitia, Ierapetra) than in the two large ones
(Heraklion, Chania), by age band and sex?

What it computes, in the units the researchers care about:

  1. the share of patients with controlled blood pressure, overall and per town
  2. the difference small - large, in percentage points, with a 95% interval
  3. the share controlled in every cell town group x age band x sex
  4. a logistic regression  controlled ~ town_group + age_band + sex, reported
     as the odds ratio for small towns against large ones, with a 95% interval

The same function, analyse(), runs on the original extract and on every
candidate release. A release may have generalised the columns, so analyse()
accepts either `age` (years) or `age_band` (any labels), and either `town` or
`town_group`. Suppressed values ("*", empty) are treated as missing and the
row is left out of whatever needs that value.
"""

from __future__ import annotations

import json
import math
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import common as C  # noqa: E402

MISSING = {"", "*", "NA", "nan", "None", "suppressed"}
Z = 1.959964


# ----------------------------------------------------------------------
# preparing any file into the shape the analysis needs
# ----------------------------------------------------------------------
def prepare(df: pd.DataFrame) -> pd.DataFrame:
    """Return a frame with columns controlled, sex, town_group, age_band (+ town if known)."""
    df = df.copy().astype(str).replace({m: np.nan for m in MISSING})
    out = pd.DataFrame(index=df.index)
    out["controlled"] = pd.to_numeric(df["controlled"], errors="coerce")
    out["sex"] = df["sex"]
    if "town" in df:
        out["town"] = df["town"]
        out["town_group"] = df["town"].map(C.TOWN_GROUP)
        # a release may have replaced the town with its group already
        out.loc[df["town"].isin(["large", "small"]), "town_group"] = df["town"]
    else:
        out["town_group"] = df["town_group"]
    if "age" in df and pd.to_numeric(df["age"], errors="coerce").notna().any():
        age = pd.to_numeric(df["age"], errors="coerce")
        out["age_band"] = age.map(lambda a: C.age_band(int(a)) if pd.notna(a) else np.nan)
    else:
        out["age_band"] = df["age_band"]
    return out


# ----------------------------------------------------------------------
# logistic regression by iteratively reweighted least squares
# ----------------------------------------------------------------------
def logistic(y: np.ndarray, X: np.ndarray, names: list[str], iters: int = 50):
    beta = np.zeros(X.shape[1])
    for _ in range(iters):
        p = 1 / (1 + np.exp(-(X @ beta)))
        w = np.clip(p * (1 - p), 1e-9, None)
        H = X.T @ (X * w[:, None])
        step = np.linalg.solve(H, X.T @ (y - p))
        beta += step
        if np.max(np.abs(step)) < 1e-8:
            break
    se = np.sqrt(np.diag(np.linalg.inv(H)))
    return {n: (b, s) for n, b, s in zip(names, beta, se)}


def odds_ratio_small(d: pd.DataFrame):
    d = d.dropna(subset=["controlled", "town_group", "age_band", "sex"])
    if d["town_group"].nunique() < 2 or len(d) < 10:
        return None
    X = pd.get_dummies(d[["town_group", "age_band", "sex"]], drop_first=False).astype(float)
    # reference levels: large towns, the most common age band, female
    ref_age = "age_band_" + d["age_band"].value_counts().idxmax()
    X = X.drop(columns=[c for c in ("town_group_large", ref_age, "sex_F") if c in X])
    X = X.loc[:, X.std() > 0]
    X.insert(0, "intercept", 1.0)
    fit = logistic(d["controlled"].to_numpy(float), X.to_numpy(), list(X.columns))
    if "town_group_small" not in fit:
        return None
    b, s = fit["town_group_small"]
    return {"or": math.exp(b), "lo": math.exp(b - Z * s), "hi": math.exp(b + Z * s),
            "n": int(len(d)), "reference_age_band": ref_age.replace("age_band_", "")}


# ----------------------------------------------------------------------
# the analysis
# ----------------------------------------------------------------------
def share(s: pd.Series):
    s = s.dropna()
    return {"n": int(len(s)), "controlled": int(s.sum()),
            "pct": round(100 * s.mean(), 1) if len(s) else None}


def analyse(df: pd.DataFrame) -> dict:
    d = prepare(df)
    res = {"rows": int(len(d)), "overall": share(d["controlled"])}

    res["by_town_group"] = {g: share(d.loc[d["town_group"] == g, "controlled"]) for g in ("large", "small")}
    if "town" in d and d["town"].isin(C.TOWN_GROUP).any():
        res["by_town"] = {t: share(d.loc[d["town"] == t, "controlled"]) for t in C.LARGE_TOWNS + C.SMALL_TOWNS}

    # difference small - large, percentage points, Wald interval
    a, b = res["by_town_group"]["small"], res["by_town_group"]["large"]
    if a["n"] and b["n"]:
        p1, p2 = a["pct"] / 100, b["pct"] / 100
        se = math.sqrt(p1 * (1 - p1) / a["n"] + p2 * (1 - p2) / b["n"])
        diff = p1 - p2
        res["difference_pp"] = {"value": round(100 * diff, 1),
                                "lo": round(100 * (diff - Z * se), 1),
                                "hi": round(100 * (diff + Z * se), 1)}

    # cells town group x age band x sex
    cells = (d.dropna(subset=["controlled", "town_group", "age_band", "sex"])
              .groupby(["town_group", "age_band", "sex"])["controlled"].agg(["size", "sum"]))
    res["cells"] = [{"town_group": g, "age_band": ab, "sex": s, "n": int(r["size"]),
                     "pct": round(100 * r["sum"] / r["size"], 1)}
                    for (g, ab, s), r in cells.iterrows()]

    res["odds_ratio_small_vs_large"] = odds_ratio_small(d)
    return res


# ----------------------------------------------------------------------
# reporting
# ----------------------------------------------------------------------
def to_markdown(res: dict, title: str) -> str:
    L = ["# Yardstick: %s" % title, ""]
    o = res["overall"]
    L.append("Patients analysed: **%d** of %d rows. Controlled overall: **%s%%** (%d of %d)."
             % (o["n"], res["rows"], o["pct"], o["controlled"], o["n"]))
    L += ["", "## By town group", "", "| group | n | controlled | % |", "|---|---|---|---|"]
    for g, s in res["by_town_group"].items():
        L.append("| %s | %d | %d | %s |" % (g, s["n"], s["controlled"], s["pct"]))
    if "difference_pp" in res:
        dpp = res["difference_pp"]
        L += ["", "**Difference small - large: %+.1f percentage points (95%% CI %+.1f to %+.1f).**"
              % (dpp["value"], dpp["lo"], dpp["hi"])]
    orr = res["odds_ratio_small_vs_large"]
    if orr:
        L += ["", "**Adjusted odds ratio of control, small vs large towns: %.2f (95%% CI %.2f to %.2f)**, "
              "adjusted for age band and sex, n = %d." % (orr["or"], orr["lo"], orr["hi"], orr["n"])]
    if "by_town" in res:
        L += ["", "## By town", "", "| town | n | controlled | % |", "|---|---|---|---|"]
        for t, s in res["by_town"].items():
            L.append("| %s | %d | %d | %s |" % (t, s["n"], s["controlled"], s["pct"]))
    L += ["", "## Town group x age band x sex", "", "| town group | age band | sex | n | % controlled |",
          "|---|---|---|---|---|"]
    for c in res["cells"]:
        flag = " ⚠" if c["n"] < 5 else ""
        L.append("| %s | %s | %s | %d%s | %s |" % (c["town_group"], c["age_band"], c["sex"], c["n"], flag, c["pct"]))
    L += ["", "⚠ = fewer than 5 patients in the cell."]
    return "\n".join(L) + "\n"


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(C.OUTPUTS, "extract_minimised.csv")
    if not os.path.exists(path):
        sys.exit("%s not found. Run analysis/build_extract.py first." % path)
    name = os.path.splitext(os.path.basename(path))[0]
    res = analyse(pd.read_csv(path, dtype=str))
    os.makedirs(C.OUTPUTS, exist_ok=True)
    with open(os.path.join(C.OUTPUTS, "yardstick_%s.json" % name), "w", encoding="utf-8") as fh:
        json.dump(res, fh, indent=2, ensure_ascii=False)
    md = to_markdown(res, name)
    with open(os.path.join(C.OUTPUTS, "yardstick_%s.md" % name), "w", encoding="utf-8") as fh:
        fh.write(md)
    print(md)


if __name__ == "__main__":
    main()
