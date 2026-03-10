import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import Logit, MNLogit

# =============================================================================
# Settings
# =============================================================================
fname_regimes = "clean-data/mnl_reg_data.xlsx"

y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"

# Baseline specification (C00058, memo 2.6.2026)
x_vars = [
    "fixed_er",
    "current_def",
    "comm_ex",
    "manu_ex",
    "opn_l1",
    "gsur_3_yr_l1",
]

regime_categories = ["Explosive", "Stationary", "Unit root"]
excel_out         = "mnlogit_binary_robustness.xlsx"

TERM_LABELS = {
    "const":        "Constant",
    "fixed_er":     "Fixed exchange rate",
    "current_def":  "Current deficit",
    "comm_ex":      "Commodity exporter",
    "manu_ex":      "Manufacturing exporter",
    "opn_l1":       "Trade openness (t-1)",
    "gsur_3_yr_l1": "Fiscal balance (3-yr, t-1)",
}


# =============================================================================
# Helpers
# =============================================================================
def star_from_p(p: float) -> str:
    if p < 0.001: return "***"
    if p < 0.05:  return "**"
    if p < 0.1:   return "*"
    return ""


def ensure_numeric_columns(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def add_lags(df: pd.DataFrame, group_col: str, time_col: str, lag_specs: list) -> pd.DataFrame:
    out = df.sort_values([group_col, time_col]).copy()
    for lag_col in sorted({v for v in lag_specs if v.endswith("_l1")}):
        base = lag_col[:-3]
        if base not in out.columns:
            raise KeyError(f"Base column '{base}' missing for lag '{lag_col}'")
        out[lag_col] = out.groupby(group_col)[base].shift(1)
    return out


def build_coef_table(params, bse, pvalues, terms, model_label: str,
                     outcome_label: str) -> pd.DataFrame:
    """Generic long-form coefficient table for any single-equation model."""
    rows = []
    for t in terms:
        pv = float(pvalues.loc[t]) if hasattr(pvalues, "loc") else float(pvalues[t])
        rows.append({
            "model":   model_label,
            "outcome": outcome_label,
            "term":    t,
            "label":   TERM_LABELS.get(t, t),
            "coef":    float(params.loc[t]) if hasattr(params, "loc") else float(params[t]),
            "se":      float(bse.loc[t])    if hasattr(bse, "loc")    else float(bse[t]),
            "p":       pv,
            "stars":   star_from_p(pv),
        })
    return pd.DataFrame(rows)


def build_paper_col(coef_df: pd.DataFrame, model_label: str,
                    outcome_label: str) -> pd.DataFrame:
    """
    Single-column paper format for one equation:
    label | row_type | <model_label: outcome_label>
    """
    col_name = f"{outcome_label} ({model_label})"
    rows = []
    for _, r in coef_df.iterrows():
        rows.append({"label": r["label"], "row_type": "coef",
                     col_name: f"{r['coef']:.3f}{r['stars']}"})
        rows.append({"label": "",          "row_type": "se",
                     col_name: f"({r['se']:.3f})"})
    return pd.DataFrame(rows)


def build_fit_stats(res, nobs: int, n_ctries: int, model_label: str) -> dict:
    llf    = float(res.llf)
    llnull = float(res.llnull)
    k      = int(res.df_model) + 1  # +1 for intercept
    bic    = -2 * llf + k * np.log(nobs)
    return {
        "model":        model_label,
        "nobs":         nobs,
        "countries":    n_ctries,
        "loglik":       round(llf, 2),
        "mcfadden_R2":  round(1 - llf / llnull, 4) if llnull else np.nan,
        "bic":          round(bic, 2),
        "bic_per_obs":  round(bic / nobs, 4),
        "converged":    getattr(res, "mle_retvals", {}).get("converged", None),
    }


# =============================================================================
# Load + standardize + clean
# =============================================================================
df = pd.read_excel(fname_regimes)
df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
df = df.replace({".": np.nan, "": np.nan, " ": np.nan})

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

base_for_lags = sorted({v[:-3] for v in x_vars if v.endswith("_l1")})
x_base_vars   = [v for v in x_vars if not v.endswith("_l1")]
df = ensure_numeric_columns(df, sorted(set(x_base_vars + base_for_lags)))
df = add_lags(df, group_col=cluster_var, time_col=year_var, lag_specs=x_vars)

# =============================================================================
# Sample construction
# =============================================================================
needed = [cluster_var, year_var, y_var] + x_vars

# Full baseline sample (stationary + unit root + explosive)
df_full = df[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()
df_full[y_var] = pd.Categorical(df_full[y_var], categories=regime_categories, ordered=False)

n_explosive = int((df_full[y_var] == "Explosive").sum())
n_full      = len(df_full)

print(f"Full baseline sample:        {n_full} obs, {df_full[cluster_var].nunique()} countries")
print(f"  of which explosive:        {n_explosive}")

# Binary sample: drop explosive observations
df_bin = df_full[df_full[y_var] != "Explosive"].copy()
n_bin  = len(df_bin)
print(f"Binary sample (no explosive): {n_bin} obs, {df_bin[cluster_var].nunique()} countries")
print(f"  Stationary: {(df_bin[y_var]=='Stationary').sum()}, "
      f"Unit root: {(df_bin[y_var]=='Unit root').sum()}")

# Binary outcome: 1 = Unit root, 0 = Stationary
# (unit root = persistent CAB = the phenomenon of interest)
y_binary = (df_bin[y_var] == "Unit root").astype(int)
X_bin    = sm.add_constant(df_bin[x_vars].astype(float), has_constant="add")

# =============================================================================
# Model 1: Binary logit on non-explosive sample (cluster-robust SEs)
# =============================================================================
print("\n--- Binary Logit (Unit root vs Stationary, no explosive) ---")
logit_model = Logit(y_binary, X_bin)
try:
    res_logit = logit_model.fit(method="newton", maxiter=300, disp=False,
                                cov_type="cluster",
                                cov_kwds={"groups": df_bin[cluster_var]})
except np.linalg.LinAlgError:
    print("Newton singular — retrying with BFGS")
    res_logit = logit_model.fit(method="bfgs", maxiter=500, disp=False,
                                cov_type="cluster",
                                cov_kwds={"groups": df_bin[cluster_var]})

converged_logit = getattr(res_logit, "mle_retvals", {}).get("converged", None)
print(f"Converged: {converged_logit}, nobs={n_bin}")

terms_with_const = ["const"] + x_vars
coef_logit = build_coef_table(
    res_logit.params, res_logit.bse, res_logit.pvalues,
    terms_with_const, "Binary logit", "Unit root"
)

# Average marginal effects for binary logit
mfx_logit  = res_logit.get_margeff(at="overall")
mfx_df = pd.DataFrame({
    "term":    x_vars,
    "label":   [TERM_LABELS.get(v, v) for v in x_vars],
    "dy_dx":   mfx_logit.margeff.flatten(),
    "se":      mfx_logit.margeff_se.flatten(),
})
mfx_df["z"]     = mfx_df["dy_dx"] / mfx_df["se"]
mfx_df["p"]     = 2 * (1 - stats.norm.cdf(np.abs(mfx_df["z"])))
mfx_df["stars"] = mfx_df["p"].apply(star_from_p)

# =============================================================================
# Model 2: MNLogit on same non-explosive sample (for clean comparison)
# =============================================================================
print("\n--- MNLogit on non-explosive sample (Stationary vs Unit root, no explosive) ---")
bin_cats   = ["Stationary", "Unit root"]
y_mnl_bin  = pd.Categorical(df_bin[y_var].astype(str), categories=bin_cats, ordered=False).codes
X_mnl_bin  = sm.add_constant(df_bin[x_vars].astype(float), has_constant="add")

mnl_bin_model = MNLogit(y_mnl_bin, X_mnl_bin)
try:
    res_mnl_bin = mnl_bin_model.fit(method="newton", maxiter=300, disp=False,
                                    cov_type="cluster",
                                    cov_kwds={"groups": df_bin[cluster_var]})
except np.linalg.LinAlgError:
    print("Newton singular — retrying with BFGS")
    res_mnl_bin = mnl_bin_model.fit(method="bfgs", maxiter=500, disp=False,
                                    cov_type="cluster",
                                    cov_kwds={"groups": df_bin[cluster_var]})

converged_mnl = getattr(res_mnl_bin, "mle_retvals", {}).get("converged", None)
print(f"Converged: {converged_mnl}")

# MNLogit with 2 categories has 1 equation (Unit root vs Stationary baseline)
col = list(res_mnl_bin.params.columns)[0]
coef_mnl_bin = build_coef_table(
    res_mnl_bin.params[col], res_mnl_bin.bse[col], res_mnl_bin.pvalues[col],
    terms_with_const, "MNLogit (no explosive)", "Unit root"
)

# =============================================================================
# Build comparison table
# =============================================================================
# Paper-format columns side by side: Binary logit | MNLogit (no explosive)
paper_logit   = build_paper_col(coef_logit,   "Binary logit",         "Unit root")
paper_mnl_bin = build_paper_col(coef_mnl_bin, "MNLogit (no explosive)", "Unit root")

comparison = paper_logit.merge(paper_mnl_bin, on=["label", "row_type"], how="outer")

# Fit stats for both models
fit_rows = [
    build_fit_stats(res_logit,   n_bin,  df_bin[cluster_var].nunique(), "Binary logit"),
    build_fit_stats(res_mnl_bin, n_bin,  df_bin[cluster_var].nunique(), "MNLogit (no explosive)"),
]
fit_df = pd.DataFrame(fit_rows)

# =============================================================================
# Export
# =============================================================================
with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    # Main comparison table
    comparison.to_excel(writer, sheet_name="comparison", index=False)
    # Fit statistics
    fit_df.to_excel(writer, sheet_name="fit_stats", index=False)
    # Average marginal effects (binary logit)
    mfx_df.to_excel(writer, sheet_name="marginal_effects", index=False)
    # Full long-form coefficient tables
    coef_logit.to_excel(writer, sheet_name="coef_binary_logit", index=False)
    coef_mnl_bin.to_excel(writer, sheet_name="coef_mnl_no_explosive", index=False)
    # Sample composition
    sample_info = pd.DataFrame([
        {"description": "Full baseline (incl. explosive)", "obs": n_full,
         "countries": df_full[cluster_var].nunique(), "explosive": n_explosive},
        {"description": "Binary sample (no explosive)", "obs": n_bin,
         "countries": df_bin[cluster_var].nunique(), "explosive": 0},
    ])
    sample_info.to_excel(writer, sheet_name="sample_info", index=False)

print(f"\nWrote binary robustness results to: {excel_out}")
