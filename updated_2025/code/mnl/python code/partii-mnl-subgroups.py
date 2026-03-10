import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit

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
excel_out         = "mnlogit_subgroups.xlsx"

# Warn when explosive obs in a subgroup fall below this threshold
MIN_EXPLOSIVE = 15


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
    """
    Create lag-1 columns for any variable in lag_specs ending in '_l1'.
    NOTE: call this on the FULL dataset before subsetting so that time-period
    subsets (e.g. Post-GFC) retain correct lagged values from the prior year.
    """
    out = df.sort_values([group_col, time_col]).copy()
    for lag_col in sorted({v for v in lag_specs if v.endswith("_l1")}):
        base = lag_col[:-3]
        if base not in out.columns:
            raise KeyError(f"Base column '{base}' missing for lag '{lag_col}'")
        out[lag_col] = out.groupby(group_col)[base].shift(1)
    return out


TERM_LABELS = {
    "const":        "Constant",
    "fixed_er":     "Fixed exchange rate",
    "current_def":  "Current deficit",
    "comm_ex":      "Commodity exporter",
    "manu_ex":      "Manufacturing exporter",
    "opn_l1":       "Trade openness (t-1)",
    "gsur_3_yr_l1": "Fiscal balance (3-yr, t-1)",
}


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
        print(f"  WARNING {name}: only {n_explosive} explosive obs — "
              "explosive-equation coefficients will be unreliable.")

    d[y_var] = pd.Categorical(d[y_var], categories=regime_categories, ordered=False)
    y_codes  = d[y_var].cat.codes
    X        = sm.add_constant(d[x_vars].astype(float), has_constant="add")

    model = MNLogit(y_codes, X)
    try:
        res = model.fit(method="newton", maxiter=300, disp=False,
                        cov_type="cluster", cov_kwds={"groups": d[cluster_var]})
    except np.linalg.LinAlgError:
        print(f"  {name}: Newton singular Hessian — retrying with BFGS")
        res = model.fit(method="bfgs", maxiter=500, disp=False,
                        cov_type="cluster", cov_kwds={"groups": d[cluster_var]})

    converged = getattr(res, "mle_retvals", {}).get("converged", None)
    nobs      = int(X.shape[0])
    n_ctries  = int(d[cluster_var].nunique())
    print(f"  {name}: nobs={nobs}, countries={n_ctries}, converged={converged}, "
          f"explosive={n_explosive}")

    categories   = list(d[y_var].cat.categories)
    nonbase      = categories[1:]
    col_to_label = {int(col): nonbase[int(col)] for col in res.params.columns}

    return res, col_to_label, nobs, n_ctries, regime_dist


def build_coef_long(res, col_to_label: dict, name: str) -> pd.DataFrame:
    rows = []
    for t in ["const"] + x_vars:
        for col in res.params.columns:
            oc = col_to_label[int(col)]
            pv = float(res.pvalues.loc[t, col])
            rows.append({
                "subgroup": name,
                "outcome":  oc,
                "term":     t,
                "label":    TERM_LABELS.get(t, t),
                "coef":     float(res.params.loc[t, col]),
                "se":       float(res.bse.loc[t, col]),
                "z":        float(res.params.loc[t, col] / res.bse.loc[t, col]),
                "p":        pv,
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
        "loglik":       round(llf,    2),
        "mcfadden_R2":  round(1 - llf / llnull, 4) if llnull else np.nan,
        "bic_per_obs":  round(float(res.bic) / nobs, 4),
        "converged":    getattr(res, "mle_retvals", {}).get("converged", None),
    }


def build_paper_block(res, col_to_label: dict,
                      outcomes: tuple = ("Stationary", "Unit root")) -> pd.DataFrame:
    """
    Coef + SE rows for one subgroup in paper-table format.
    Columns: label | row_type | Stationary | Unit root
    """
    rows = []
    for t in ["const"] + x_vars:
        lab    = TERM_LABELS.get(t, t)
        r_coef = {"label": lab, "row_type": "coef"}
        r_se   = {"label": "",  "row_type": "se"}
        for col in res.params.columns:
            oc = col_to_label[int(col)]
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
    """
    Stitch per-subgroup paper blocks side by side.
    Columns: label | row_type | Stationary (Advanced) | Unit root (Advanced) | ...
    """
    master = None
    for name, blk in paper_blocks.items():
        renamed = blk.rename(columns={oc: f"{oc} ({name})" for oc in outcomes})
        if master is None:
            master = renamed
        else:
            master = master.merge(renamed, on=["label", "row_type"], how="outer")
    return master


# =============================================================================
# Load + standardize + clean
# =============================================================================
df = pd.read_excel(fname_regimes)
df.columns = df.columns.astype(str).str.strip().str.replace(r"\s+", "_", regex=True)
df = df.replace({".": np.nan, "": np.nan, " ": np.nan})

# Regime label normalization
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

# Numeric conversion for X source columns
base_for_lags = sorted({v[:-3] for v in x_vars if v.endswith("_l1")})
x_base_vars   = [v for v in x_vars if not v.endswith("_l1")]
df = ensure_numeric_columns(df, sorted(set(x_base_vars + base_for_lags)))

# Integer year for subgroup time filters
yr_int = pd.to_datetime(df[year_var], errors="coerce").dt.year

# Create lags on FULL dataset before any subsetting
df = add_lags(df, group_col=cluster_var, time_col=year_var, lag_specs=x_vars)


# =============================================================================
# Define subgroups
# =============================================================================
# idc=1  → Advanced (Industrial Developed Countries)
# emg=1  → Emerging markets
# ldc=1 & emg=0  → Low income / frontier (non-emerging developing)
SUBGROUPS = {
    "Advanced":   df["idc"] == 1,
    "Emerging":   df["emg"] == 1,
    "Low income": (df["ldc"] == 1) & (df["emg"] == 0),
    "Pre-GFC":    yr_int < 2008,
    "Post-GFC":   yr_int >= 2008,
}


# =============================================================================
# Run subgroup regressions
# =============================================================================
all_coef_long = []
all_fit_rows  = []
paper_blocks  = {}

for name, mask in SUBGROUPS.items():
    print(f"\n--- {name} ---")
    df_sub = df[mask].copy()
    try:
        res, col_to_label, nobs, n_ctries, regime_dist = fit_subgroup(df_sub, name)
    except Exception as e:
        print(f"  FAILED: {e}")
        continue

    all_coef_long.append(build_coef_long(res, col_to_label, name))
    all_fit_rows.append(build_fit_row(res, nobs, n_ctries, regime_dist, name))
    paper_blocks[name] = build_paper_block(res, col_to_label)

coef_long_all = pd.concat(all_coef_long, ignore_index=True)
fit_stats_df  = pd.DataFrame(all_fit_rows)
wide_table    = build_wide_comparison(paper_blocks)


# =============================================================================
# Export
# =============================================================================
with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    # Side-by-side comparison of all subgroups (most useful for the paper)
    wide_table.to_excel(writer, sheet_name="comparison_wide", index=False)
    # Fit statistics and sample sizes for all subgroups
    fit_stats_df.to_excel(writer, sheet_name="fit_stats", index=False)
    # Full long-form coefficient table (useful for custom analysis)
    coef_long_all.to_excel(writer, sheet_name="coef_all_long", index=False)
    # Individual subgroup sheets
    for name, blk in paper_blocks.items():
        sheet = name.lower().replace(" ", "_").replace("-", "")[:31]
        blk.to_excel(writer, sheet_name=sheet, index=False)

print(f"\nWrote subgroup results to: {excel_out}")
