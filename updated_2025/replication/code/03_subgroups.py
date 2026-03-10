"""
03_subgroups.py
===============
Replicates Table 8 (income-group subgroups) and Table 9 (time-period subgroups).

Subgroups:
  Income:       Advanced (idc == 1), Emerging (emg == 1),
                Low income (ldc == 1 & emg == 0)
  Time-period:  Pre-GFC (year < 2008), Post-GFC (year >= 2008)

Same specification as baseline (C00058):
  X = fixed_er, current_def, comm_ex, manu_ex, opn_l1, gsur_3_yr_l1
  Reference category: Explosive
  SEs: cluster-robust, clustered at country level (cn)

Notes on identification:
  - Advanced subgroup has only 15 explosive obs → McFadden R² returns NaN
    (log-null ≈ log-lik; paper correctly marks 'n/a').
  - Low income has only 3 explosive obs → model skipped entirely; paper marks 'n/a'.

Output: output/03_subgroups.xlsx
Sheets: fit_stats | comparison_wide | coef_all_long | advanced | emerging |
        low_income | pre_gfc | post_gfc
"""

from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT       = Path(__file__).resolve().parent.parent
DATA_FILE  = ROOT / "data" / "mnl_reg_data.xlsx"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
EXCEL_OUT  = OUTPUT_DIR / "03_subgroups.xlsx"

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"
x_vars      = ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]

regime_categories = ["Explosive", "Stationary", "Unit root"]

# Minimum explosive obs to attempt estimation; below this, model is skipped
MIN_EXPLOSIVE = 5

TERM_LABELS = {
    "const":          "Constant",
    "fixed_er":       "Fixed exchange rate",
    "current_def":    "Current account deficit",
    "comm_ex":        "Commodity exporter",
    "manu_ex":        "Manufacturing exporter",
    "opn_l1":         "Trade openness (t-1)",
    "gsur_3_yr_l1":   "Fiscal balance, 3-yr avg (t-1)",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def star_from_p(p: float) -> str:
    """Convention: * p<0.10, ** p<0.05, *** p<0.01."""
    if p < 0.01:  return "***"
    if p < 0.05:  return "**"
    if p < 0.10:  return "*"
    return ""


def col_to_label_map(res, categories: list) -> dict:
    """
    Robust mapping: params.columns -> outcome labels.
    Handles both 0-indexed [0,1] and 1-indexed [1,2] column labels.
    """
    nonbase    = categories[1:]      # ['Stationary', 'Unit root']
    param_cols = sorted(res.params.columns)
    return {int(c): nonbase[i] for i, c in enumerate(param_cols)}


# ---------------------------------------------------------------------------
# Load + prepare data
# ---------------------------------------------------------------------------
print("Loading data from:", DATA_FILE)
df = pd.read_excel(DATA_FILE)
df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
df = df.replace({"." : np.nan, "": np.nan, " ": np.nan})

# Normalize regime labels
df[y_var] = (
    df[y_var].astype(str)
      .str.replace("\u00a0", " ", regex=False)
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)
      .replace({
          "explosive":  "Explosive",
          "Stationary": "Stationary", "stationary": "Stationary",
          "Unit Root":  "Unit root",  "Unit root":  "Unit root",
          "unit root":  "Unit root",  "UNIT ROOT":  "Unit root",
      })
)
df[y_var] = pd.Categorical(df[y_var], categories=regime_categories, ordered=False)

# Numeric conversion
for c in ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn", "gsur_3_yr"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Create lags on FULL dataset before any subsetting (critical for time subgroups)
df = df.sort_values([cluster_var, year_var]).copy()
df["opn_l1"]       = df.groupby(cluster_var)["opn"].shift(1)
df["gsur_3_yr_l1"] = df.groupby(cluster_var)["gsur_3_yr"].shift(1)

# Extract integer year (year stored as date string e.g. "1985-01-01")
yr_int = pd.to_datetime(df[year_var], errors="coerce").dt.year

print(f"Full dataset: {len(df)} rows, {df[cluster_var].nunique()} countries")


# ---------------------------------------------------------------------------
# Subgroup definitions
# ---------------------------------------------------------------------------
# idc=1  → Advanced (Industrial Developed Countries)
# emg=1  → Emerging markets
# ldc=1 & emg=0  → Low income / frontier
SUBGROUPS = {
    "Advanced":   df["idc"] == 1,
    "Emerging":   df["emg"] == 1,
    "Low income": (df["ldc"] == 1) & (df["emg"] == 0),
    "Pre-GFC":    yr_int < 2008,
    "Post-GFC":   yr_int >= 2008,
}


# ---------------------------------------------------------------------------
# Fit function
# ---------------------------------------------------------------------------
def fit_subgroup(df_sub: pd.DataFrame, name: str):
    """
    Fit MNLogit with cluster-robust SEs on a pre-filtered subgroup.
    Falls back from Newton to BFGS on singular Hessian.
    Returns: res, col_to_label, nobs, n_countries, regime_dist
    """
    needed = [cluster_var, y_var] + x_vars
    d = df_sub[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()

    regime_dist = d[y_var].value_counts().reindex(regime_categories, fill_value=0)
    n_explosive = int(regime_dist.get("Explosive", 0))

    if n_explosive < MIN_EXPLOSIVE:
        raise RuntimeError(
            f"{name}: only {n_explosive} explosive obs — explosive equation not identified. "
            "Skipping."
        )
    if n_explosive < 15:
        print(f"  WARNING {name}: only {n_explosive} explosive obs — "
              "McFadden R² may be unreliable (near-unidentified).")

    d[y_var] = pd.Categorical(d[y_var], categories=regime_categories, ordered=False)
    y_codes  = d[y_var].cat.codes
    X        = sm.add_constant(d[x_vars].astype(float), has_constant="add")

    model = MNLogit(y_codes, X)
    try:
        res = model.fit(
            method="newton", maxiter=300, disp=False,
            cov_type="cluster", cov_kwds={"groups": d[cluster_var]}
        )
    except np.linalg.LinAlgError:
        print(f"  {name}: Newton singular Hessian — retrying with BFGS")
        res = model.fit(
            method="bfgs", maxiter=500, disp=False,
            cov_type="cluster", cov_kwds={"groups": d[cluster_var]}
        )

    converged  = getattr(res, "mle_retvals", {}).get("converged", None)
    nobs       = int(X.shape[0])
    n_ctries   = int(d[cluster_var].nunique())
    col_map    = col_to_label_map(res, regime_categories)

    print(f"  {name}: nobs={nobs}, countries={n_ctries}, "
          f"explosive={n_explosive}, converged={converged}")

    return res, col_map, nobs, n_ctries, regime_dist, d


# ---------------------------------------------------------------------------
# Table-building helpers
# ---------------------------------------------------------------------------
def build_coef_long(res, col_map: dict, name: str) -> pd.DataFrame:
    rows = []
    for t in ["const"] + x_vars:
        for col in res.params.columns:
            oc = col_map[int(col)]
            pv = float(res.pvalues.loc[t, col])
            b  = float(res.params.loc[t, col])
            se = float(res.bse.loc[t, col])
            rows.append({
                "subgroup": name,
                "outcome":  oc,
                "term":     t,
                "label":    TERM_LABELS.get(t, t),
                "coef":     round(b, 4),
                "se":       round(se, 4),
                "z":        round(b / se if se != 0 else np.nan, 3),
                "p_value":  round(pv, 4),
                "stars":    star_from_p(pv),
            })
    return pd.DataFrame(rows)


def build_fit_row(res, nobs: int, n_ctries: int,
                  regime_dist: pd.Series, name: str) -> dict:
    llf    = float(res.llf)
    llnull = float(res.llnull)
    return {
        "subgroup":     name,
        "nobs":         nobs,
        "countries":    n_ctries,
        "n_explosive":  int(regime_dist.get("Explosive",  0)),
        "n_stationary": int(regime_dist.get("Stationary", 0)),
        "n_unit_root":  int(regime_dist.get("Unit root",  0)),
        "log_lik":      round(llf, 4),
        "mcfadden_R2":  round(1 - llf / llnull, 4) if llnull else np.nan,
        "bic_per_obs":  round(float(res.bic) / nobs, 4),
        "converged":    getattr(res, "mle_retvals", {}).get("converged", None),
    }


def build_paper_block(res, col_map: dict,
                      outcomes: tuple = ("Stationary", "Unit root")) -> pd.DataFrame:
    """
    Coef + SE rows in paper-table format.
    Columns: label | row_type | Stationary | Unit root
    """
    rows = []
    for t in ["const"] + x_vars:
        lab    = TERM_LABELS.get(t, t)
        r_coef = {"label": lab, "row_type": "coef"}
        r_se   = {"label": "",  "row_type": "se"}
        for col in res.params.columns:
            oc = col_map[int(col)]
            if oc not in outcomes:
                continue
            b  = float(res.params.loc[t, col])
            se = float(res.bse.loc[t, col])
            pv = float(res.pvalues.loc[t, col])
            r_coef[oc] = f"{b:.3f}{star_from_p(pv)}"
            r_se[oc]   = f"({se:.3f})"
        rows += [r_coef, r_se]

    blk = pd.DataFrame(rows)
    for oc in outcomes:
        if oc not in blk.columns:
            blk[oc] = ""
    return blk[["label", "row_type"] + list(outcomes)]


def build_wide_comparison(paper_blocks: dict,
                          outcomes: tuple = ("Stationary", "Unit root")) -> pd.DataFrame:
    """Stitch per-subgroup paper blocks side by side."""
    master = None
    for name, blk in paper_blocks.items():
        renamed = blk.rename(columns={oc: f"{oc} ({name})" for oc in outcomes})
        if master is None:
            master = renamed
        else:
            master = master.merge(renamed, on=["label", "row_type"], how="outer")
    return master


# ---------------------------------------------------------------------------
# Run all subgroups
# ---------------------------------------------------------------------------
all_coef_long = []
all_fit_rows  = []
paper_blocks  = {}

for name, mask in SUBGROUPS.items():
    print(f"\n--- {name} ---")
    df_sub = df[mask].copy()
    try:
        res, col_map, nobs, n_ctries, regime_dist, d_used = fit_subgroup(df_sub, name)
    except RuntimeError as e:
        print(f"  SKIPPED: {e}")
        continue
    except Exception as e:
        print(f"  FAILED: {e}")
        continue

    all_coef_long.append(build_coef_long(res, col_map, name))
    all_fit_rows.append(build_fit_row(res, nobs, n_ctries, regime_dist, name))
    paper_blocks[name] = build_paper_block(res, col_map)

coef_long_all = pd.concat(all_coef_long, ignore_index=True)
fit_stats_df  = pd.DataFrame(all_fit_rows)
wide_table    = build_wide_comparison(paper_blocks)

print("\n\nFit statistics summary:")
print(fit_stats_df[["subgroup", "nobs", "countries", "n_explosive",
                     "mcfadden_R2", "bic_per_obs"]].to_string(index=False))


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
    fit_stats_df.to_excel(  writer, sheet_name="fit_stats",        index=False)
    wide_table.to_excel(    writer, sheet_name="comparison_wide",   index=False)
    coef_long_all.to_excel( writer, sheet_name="coef_all_long",     index=False)
    for name, blk in paper_blocks.items():
        sheet = name.lower().replace(" ", "_").replace("-", "")[:31]
        blk.to_excel(writer, sheet_name=sheet, index=False)

print(f"\nSaved: {EXCEL_OUT}")
print("Sheets: fit_stats | comparison_wide | coef_all_long | "
      + " | ".join(n.lower().replace(" ", "_").replace("-", "")[:31]
                   for n in paper_blocks))
