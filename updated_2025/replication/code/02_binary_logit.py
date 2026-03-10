"""
02_binary_logit.py
==================
Replicates Table 7: binary logit robustness check.

Design:
  - Drop the 134 explosive observations from the baseline sample.
  - Estimate binary logit: y = 1 (Unit root), y = 0 (Stationary).
  - Same six regressors as baseline (C00058).
  - Cluster-robust SEs clustered at the country level.

Key finding: none of the six regressors are statistically significant (all p > 0.25).
This confirms that the baseline MNL's explanatory power operates through the
explosive-vs-non-explosive channel, not through the stationary/unit-root distinction.

Output: output/02_binary_logit.xlsx
"""

from pathlib import Path
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Logit

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT       = Path(__file__).resolve().parent.parent
DATA_FILE  = ROOT / "data" / "mnl_reg_data.xlsx"
OUTPUT_DIR = ROOT / "output"
OUTPUT_DIR.mkdir(exist_ok=True)
EXCEL_OUT  = OUTPUT_DIR / "02_binary_logit.xlsx"

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"
x_vars      = ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]
regime_categories = ["Explosive", "Stationary", "Unit root"]

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


def load_and_prepare(data_path: Path) -> pd.DataFrame:
    df = pd.read_excel(data_path)
    df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
    df = df.replace({"." : np.nan, "": np.nan, " ": np.nan})

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

    for c in ["opn", "gsur_3_yr"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["fixed_er", "current_def", "comm_ex", "manu_ex"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Create lags on full dataset before subsetting
    df = df.sort_values([cluster_var, year_var]).copy()
    df["opn_l1"]       = df.groupby(cluster_var)["opn"].shift(1)
    df["gsur_3_yr_l1"] = df.groupby(cluster_var)["gsur_3_yr"].shift(1)

    return df


# ---------------------------------------------------------------------------
# Load + build samples
# ---------------------------------------------------------------------------
print("Loading data from:", DATA_FILE)
df = load_and_prepare(DATA_FILE)

needed = [cluster_var, year_var, y_var] + x_vars

# Full baseline sample
df_full = df[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()
df_full[y_var] = pd.Categorical(df_full[y_var],
                                categories=regime_categories, ordered=False)
n_full      = len(df_full)
n_explosive = int((df_full[y_var] == "Explosive").sum())

print(f"\nFull baseline sample: {n_full} obs, "
      f"{df_full[cluster_var].nunique()} countries")
print(f"  of which explosive: {n_explosive}")

# Binary sample: drop explosive observations
df_bin = df_full[df_full[y_var] != "Explosive"].copy()
n_bin  = len(df_bin)
print(f"\nBinary sample (explosive dropped): {n_bin} obs, "
      f"{df_bin[cluster_var].nunique()} countries")
print(f"  Stationary: {(df_bin[y_var] == 'Stationary').sum()}  "
      f"Unit root: {(df_bin[y_var] == 'Unit root').sum()}")


# ---------------------------------------------------------------------------
# Fit binary logit
# ---------------------------------------------------------------------------
# y = 1 if Unit root, y = 0 if Stationary
y_bin = (df_bin[y_var] == "Unit root").astype(int)
X_bin = sm.add_constant(df_bin[x_vars].astype(float), has_constant="add")

print("\nFitting binary logit (cluster-robust SEs) ...")
res_logit = Logit(y_bin, X_bin).fit(
    method="newton", maxiter=300, disp=False,
    cov_type="cluster", cov_kwds={"groups": df_bin[cluster_var]}
)

converged = getattr(res_logit, "mle_retvals", {}).get("converged", None)
print(f"Converged: {converged}")


# ---------------------------------------------------------------------------
# Average marginal effects
# ---------------------------------------------------------------------------
mfx     = res_logit.get_margeff(at="overall")
ame_arr = mfx.margeff.flatten()
ame_se  = mfx.margeff_se.flatten()


# ---------------------------------------------------------------------------
# Build tables
# ---------------------------------------------------------------------------
coef_rows = []
for term in ["const"] + x_vars:
    b  = float(res_logit.params[term])
    se = float(res_logit.bse[term])
    pv = float(res_logit.pvalues[term])
    z  = b / se if se != 0 else np.nan
    coef_rows.append({
        "term":     term,
        "label":    TERM_LABELS.get(term, term),
        "coef":     round(b, 4),
        "se":       round(se, 4),
        "z":        round(z, 3),
        "p_value":  round(pv, 4),
        "stars":    star_from_p(pv),
        "coef_str": f"{b:.3f}{star_from_p(pv)}",
        "se_str":   f"({se:.3f})",
    })

coef_df = pd.DataFrame(coef_rows)

# AME table
ame_rows = []
for i, var in enumerate(x_vars):
    dy = float(ame_arr[i])
    se = float(ame_se[i])
    z  = dy / se if se != 0 else np.nan
    pv = float(2 * (1 - stats.norm.cdf(abs(z)))) if not np.isnan(z) else np.nan
    ame_rows.append({
        "variable": TERM_LABELS.get(var, var),
        "term":     var,
        "ame":      round(dy, 4),
        "se":       round(se, 4),
        "z":        round(z, 3),
        "p_value":  round(pv, 4),
        "stars":    star_from_p(pv),
    })

ame_df = pd.DataFrame(ame_rows)

# Fit statistics
llf    = float(res_logit.llf)
llnull = float(res_logit.llnull)
fit_df = pd.DataFrame([{
    "model":       "Binary logit",
    "sample":      "Stationary + Unit root (explosive dropped)",
    "nobs":        n_bin,
    "countries":   int(df_bin[cluster_var].nunique()),
    "log_lik":     round(llf, 4),
    "mcfadden_R2": round(1 - llf / llnull, 4),
    "bic_per_obs": round(res_logit.bic / n_bin, 4),
    "converged":   converged,
}])

# Paper-format table (Table 7)
paper_rows = []
for _, r in coef_df.iterrows():
    paper_rows.append({"variable": r["label"], "row_type": "coef",
                       "Unit root (vs Stationary)": r["coef_str"]})
    paper_rows.append({"variable": "",          "row_type": "se",
                       "Unit root (vs Stationary)": r["se_str"]})
paper_df = pd.DataFrame(paper_rows)

print("\nTable 7 — Binary Logit (Unit root vs Stationary):")
print(coef_df[["label", "coef", "se", "p_value", "stars"]].to_string(index=False))

print(f"\nAny significant regressor (p < 0.10)? "
      f"{any(coef_df['p_value'] < 0.10 for _, coef_df_row in coef_df.iterrows() if coef_df_row['term'] in x_vars)}")

# Recheck
any_sig = (coef_df[coef_df["term"].isin(x_vars)]["p_value"] < 0.10).any()
print(f"Any significant regressor (p < 0.10)? {any_sig}")
print("  (Paper reports: none significant — all p > 0.25)")

# Sample info
sample_df = pd.DataFrame([
    {"description": "Full baseline (incl. explosive)", "nobs": n_full,
     "countries": df_full[cluster_var].nunique(), "n_explosive": n_explosive},
    {"description": "Binary sample (explosive dropped)", "nobs": n_bin,
     "countries": df_bin[cluster_var].nunique(), "n_explosive": 0},
])


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
    paper_df.to_excel(writer, sheet_name="Table7_binary_logit",  index=False)
    ame_df.to_excel(  writer, sheet_name="AMEs",                 index=False)
    fit_df.to_excel(  writer, sheet_name="fit_stats",            index=False)
    coef_df.to_excel( writer, sheet_name="coef_long",            index=False)
    sample_df.to_excel(writer, sheet_name="sample_info",         index=False)

print(f"\nSaved: {EXCEL_OUT}")
print("Sheets: Table7_binary_logit | AMEs | fit_stats | coef_long | sample_info")
