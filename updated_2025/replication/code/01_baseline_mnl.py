"""
01_baseline_mnl.py
==================
Replicates Table 4 (coefficient estimates), Table 5 (average marginal effects),
and the baseline fit statistics reported in Table 6.

Baseline specification C00058:
  y  = Regime_Type  (Explosive / Stationary / Unit root)
  X  = fixed_er, current_def, comm_ex, manu_ex, opn_l1, gsur_3_yr_l1

Reference category: Explosive
Standard errors:    cluster-robust, clustered at the country level (cn)

Output: output/01_baseline_mnl.xlsx
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
EXCEL_OUT  = OUTPUT_DIR / "01_baseline_mnl.xlsx"

# ---------------------------------------------------------------------------
# Model settings
# ---------------------------------------------------------------------------
y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"

# Baseline specification (C00058)
x_vars = ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]

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
    """Return significance stars. Convention: * p<0.10, ** p<0.05, *** p<0.01."""
    if p < 0.01:  return "***"
    if p < 0.05:  return "**"
    if p < 0.10:  return "*"
    return ""


def load_and_prepare(data_path: Path) -> pd.DataFrame:
    """Load data, standardize column names, clean regime labels, create lags."""
    df = pd.read_excel(data_path)
    df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
    df = df.replace({"." : np.nan, "": np.nan, " ": np.nan})

    # Normalize regime labels (handles mixed case and non-breaking spaces)
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

    # Convert continuous source columns to numeric
    source_cols = ["opn", "gsur_3_yr"]
    for c in source_cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["fixed_er", "current_def", "comm_ex", "manu_ex"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Create lags within country group BEFORE any subsetting.
    # IMPORTANT: year is stored as a date string (e.g. "1985-01-01").
    # Use pd.to_datetime().dt.year — never pd.to_numeric() — to extract the year.
    df = df.sort_values([cluster_var, year_var]).copy()
    df["opn_l1"]       = df.groupby(cluster_var)["opn"].shift(1)
    df["gsur_3_yr_l1"] = df.groupby(cluster_var)["gsur_3_yr"].shift(1)

    return df


def col_to_label_map(res, categories: list) -> dict:
    """
    Robust mapping: params.columns -> outcome labels.
    Handles both 0-indexed [0,1] and 1-indexed [1,2] column labels.
    """
    nonbase    = categories[1:]      # ['Stationary', 'Unit root']
    param_cols = sorted(res.params.columns)
    return {int(c): nonbase[i] for i, c in enumerate(param_cols)}


# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading data from:", DATA_FILE)
df = load_and_prepare(DATA_FILE)

# Apply categorical encoding and listwise deletion
needed   = [cluster_var, year_var, y_var] + x_vars
df_model = df[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()
df_model[y_var] = pd.Categorical(df_model[y_var],
                                 categories=regime_categories, ordered=False)

nobs        = len(df_model)
n_countries = df_model[cluster_var].nunique()
vc          = df_model[y_var].value_counts()

print(f"\nSample: {nobs} observations, {n_countries} countries")
print("Regime distribution:")
for cat in regime_categories:
    cnt = int(vc.get(cat, 0))
    print(f"  {cat}: {cnt}  ({100*cnt/nobs:.1f}%)")


# ---------------------------------------------------------------------------
# Fit model
# ---------------------------------------------------------------------------
y_codes = df_model[y_var].cat.codes
X       = sm.add_constant(df_model[x_vars].astype(float), has_constant="add")

print("\nFitting MNLogit (cluster-robust SEs) ...")
model = MNLogit(y_codes, X)
res   = model.fit(
    method="newton", maxiter=300, disp=False,
    cov_type="cluster", cov_kwds={"groups": df_model[cluster_var]}
)

converged = getattr(res, "mle_retvals", {}).get("converged", None)
print(f"Converged: {converged}   cov_type: {res.cov_type}")

col_map = col_to_label_map(res, regime_categories)


# ---------------------------------------------------------------------------
# Fit statistics
# ---------------------------------------------------------------------------
llf      = float(res.llf)
llnull   = float(res.llnull)
mcf_r2   = 1 - llf / llnull
bic_po   = float(res.bic) / nobs
aic_po   = float(res.aic) / nobs

print(f"\nFit statistics:")
print(f"  McFadden R²  = {mcf_r2:.4f}")
print(f"  BIC / obs    = {bic_po:.4f}")
print(f"  AIC / obs    = {aic_po:.4f}")
print(f"  Log-lik      = {llf:.4f}")
print(f"  Log-lik null = {llnull:.4f}")

fit_df = pd.DataFrame([{
    "model":        "C00058",
    "nobs":         nobs,
    "countries":    n_countries,
    "log_lik":      round(llf, 4),
    "log_lik_null": round(llnull, 4),
    "mcfadden_R2":  round(mcf_r2, 4),
    "bic_per_obs":  round(bic_po, 4),
    "aic_per_obs":  round(aic_po, 4),
}])


# ---------------------------------------------------------------------------
# Coefficient table
# ---------------------------------------------------------------------------
coef_rows = []
for term in ["const"] + x_vars:
    for col in sorted(res.params.columns):
        outcome = col_map[int(col)]
        b   = float(res.params.loc[term, col])
        se  = float(res.bse.loc[term, col])
        pv  = float(res.pvalues.loc[term, col])
        z   = b / se if se != 0 else np.nan
        coef_rows.append({
            "term":      term,
            "label":     TERM_LABELS.get(term, term),
            "outcome":   outcome,
            "coef":      round(b, 4),
            "se":        round(se, 4),
            "z":         round(z, 3),
            "p_value":   round(pv, 4),
            "stars":     star_from_p(pv),
            "coef_str":  f"{b:.3f}{star_from_p(pv)}",
            "se_str":    f"({se:.3f})",
        })

coef_df = pd.DataFrame(coef_rows)

# Paper-format table (Table 4 layout)
def paper_table(coef_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for term in ["const"] + x_vars:
        label = TERM_LABELS.get(term, term)
        sub   = coef_df[coef_df["term"] == term]
        row_c = {"variable": label, "row_type": "coef"}
        row_s = {"variable": "",    "row_type": "se"}
        for eq in ["Stationary", "Unit root"]:
            match = sub[sub["outcome"] == eq]
            if len(match):
                row_c[eq] = match.iloc[0]["coef_str"]
                row_s[eq] = match.iloc[0]["se_str"]
            else:
                row_c[eq] = row_s[eq] = ""
        rows += [row_c, row_s]
    return pd.DataFrame(rows)[["variable", "row_type", "Stationary", "Unit root"]]

paper_df = paper_table(coef_df)

print("\nTable 4 — Baseline Coefficients (cluster-robust SEs):")
print(paper_df.to_string(index=False))


# ---------------------------------------------------------------------------
# Average marginal effects
# ---------------------------------------------------------------------------
print("\nComputing average marginal effects ...")
mfx     = res.get_margeff(at="overall")
me_arr  = mfx.margeff     # shape (k_regressors, 3)
me_se   = mfx.margeff_se

# Align row names (intercept excluded from mfx by statsmodels)
x_no_const = [c for c in X.columns if c != "const"]
assert me_arr.shape[0] == len(x_no_const), (
    f"Margeff rows ({me_arr.shape[0]}) != regressors ({len(x_no_const)})")

ame_rows = []
for i, var in enumerate(x_no_const):
    for j, outcome in enumerate(regime_categories):
        dy = float(me_arr[i, j])
        se = float(me_se[i, j])
        z  = dy / se if se != 0 else np.nan
        pv = float(2 * (1 - stats.norm.cdf(abs(z)))) if not np.isnan(z) else np.nan
        ame_rows.append({
            "variable": TERM_LABELS.get(var, var),
            "term":     var,
            "outcome":  outcome,
            "ame":      round(dy, 4),
            "se":       round(se, 4),
            "z":        round(z, 3),
            "p_value":  round(pv, 4),
            "stars":    star_from_p(pv),
        })

ame_df = pd.DataFrame(ame_rows)

print("\nTable 5 — Average Marginal Effects:")
pivot = ame_df.pivot(index="variable", columns="outcome", values="ame")
print(pivot[regime_categories].to_string())


# ---------------------------------------------------------------------------
# Outcome distribution
# ---------------------------------------------------------------------------
dist_df = pd.DataFrame({
    "outcome":    regime_categories,
    "count":      [int(vc.get(c, 0)) for c in regime_categories],
    "proportion": [vc.get(c, 0) / nobs for c in regime_categories],
})


# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
    paper_df.to_excel(writer, sheet_name="Table4_coefficients", index=False)
    ame_df.to_excel(  writer, sheet_name="Table5_AMEs",         index=False)
    fit_df.to_excel(  writer, sheet_name="fit_stats",           index=False)
    coef_df.to_excel( writer, sheet_name="coef_long",           index=False)
    dist_df.to_excel( writer, sheet_name="regime_distribution", index=False)

print(f"\nSaved: {EXCEL_OUT}")
print("Sheets: Table4_coefficients | Table5_AMEs | fit_stats | coef_long | regime_distribution")
