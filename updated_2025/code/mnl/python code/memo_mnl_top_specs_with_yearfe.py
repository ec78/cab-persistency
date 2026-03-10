import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit

# =============================================================================
# USER SETTINGS
# =============================================================================
data_xlsx = "clean-data/mnl_reg_data.xlsx"  # your estimation dataset
cluster_var = "cn"
year_var = "year"

# After standardizing column names: "Regime Type" -> "Regime_Type"
y_var = "Regime_Type"

# Regime categories and baseline
regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label = "Explosive"

# Output
excel_out = "memo_mnl_coeff_table_top_specs_with_yearfe.xlsx"

# -------------------------------------------------------------------------
# Spec definitions from your ranked_candidates output
# Note: lags (_l1) are created inside this script.
# -------------------------------------------------------------------------
SPECS = {
    "C00004": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","opn"],
        "add_year_fe": False
    },
    "C00004_yearFE": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","opn"],
        "add_year_fe": True
    },
    "C00058": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","opn_l1","gsur_3_yr_l1"],
        "add_year_fe": False
    },
    "C00058_yearFE": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","opn_l1","gsur_3_yr_l1"],
        "add_year_fe": True
    },
    "C00342_fdgap": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","gsur_3_yr_l1","gsur_def_l1","fd_gap","ir_r_lmf_l1"],
        "add_year_fe": False
    },
    # Robustness: replace broad commodity exporter dummy with oil exporter dummy
    "C00058_oil": {
        "x_list": ["fixed_er","current_def","oil","manu_ex","opn_l1","gsur_3_yr_l1"],
        "add_year_fe": False
    },
    # Robustness: targeted crisis-year dummies instead of full year FE
    "C00058_crisis": {
        "x_list": ["fixed_er","current_def","comm_ex","manu_ex","opn_l1","gsur_3_yr_l1","d_gfc","d_covid"],
        "add_year_fe": False
    }
}

# =============================================================================
# Helpers
# =============================================================================
def star_from_p(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""

def ensure_numeric_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out

def clean_regime_labels(s: pd.Series) -> pd.Series:
    x = (s.astype(str)
           .str.replace("\u00a0", " ", regex=False)
           .str.strip()
           .str.replace(r"\s+", " ", regex=True))
    # normalize known labels exactly
    x = x.replace({
        "Explosive": "Explosive",
        "explosive": "Explosive",
        "Stationary": "Stationary",
        "stationary": "Stationary",
        "Unit root": "Unit root",
        "unit root": "Unit root",
        "Unit Root": "Unit root",
        "UNIT ROOT": "Unit root",
    })
    return x

def add_lags(df: pd.DataFrame, group_col: str, time_col: str, lag_specs: list[str]) -> pd.DataFrame:
    """
    Create any *_l1 columns needed by specs.
    For each required var ending in _l1, create lag1 of the base var within group_col sorted by time_col.
    """
    out = df.copy()
    # Ensure sorted before shift
    out = out.sort_values([group_col, time_col]).copy()

    # Which lag columns are required
    lag_cols = sorted({v for v in lag_specs if v.endswith("_l1")})

    for lag_col in lag_cols:
        base = lag_col[:-3]  # strip "_l1"
        if base not in out.columns:
            raise KeyError(f"To create {lag_col}, base column '{base}' is missing from data.")
        out[lag_col] = out.groupby(group_col)[base].shift(1)

    return out

def fit_mnlogit_cluster(df_model: pd.DataFrame, x_vars: list[str], add_year_fe: bool, model_name: str):
    """
    Fit MNLogit with cluster-robust SEs (cluster on cn).
    - Baseline category is 'Explosive' (code 0) via fixed category ordering.
    - If add_year_fe=True, include year dummies (drop_first=True) and use a more stable optimizer.
    Returns:
        res, X, y_codes, col_to_label, nobs, n_countries
    """

    # ---------------------------------------------------------------------
    # 1) Subset and listwise delete for this specific model
    # ---------------------------------------------------------------------
    needed = [cluster_var, year_var, y_var] + x_vars
    d = df_model[needed].copy()
    d = d.dropna(subset=needed).copy()

    # Country count after listwise deletion (this matches the estimation sample)
    n_countries = int(d[cluster_var].nunique())

    # ---------------------------------------------------------------------
    # 2) Ensure Y is categorical with fixed ordering (baseline is index 0)
    # ---------------------------------------------------------------------
    d[y_var] = pd.Categorical(d[y_var], categories=regime_categories, ordered=False)
    y_codes = d[y_var].cat.codes

    # ---------------------------------------------------------------------
    # 3) Build X (core covariates + optional year FE)
    # ---------------------------------------------------------------------
    X_base = d[x_vars].copy()

    if add_year_fe:
        # Force year numeric -> int before dummies
        yr = pd.to_numeric(d[year_var], errors="coerce")
        keep = yr.notna()
        if not keep.all():
            d = d.loc[keep].copy()
            y_codes = d[y_var].cat.codes
            X_base = d[x_vars].copy()
            yr = yr.loc[keep]

        yr = yr.astype(int)

        # Dummies: drop_first avoids collinearity; dtype=int avoids bools
        year_dummies = pd.get_dummies(yr, prefix="year", drop_first=True, dtype=int)
        X_base = pd.concat([X_base, year_dummies], axis=1)

    # Add intercept
    X = sm.add_constant(X_base, has_constant="add")

    # ---------------------------------------------------------------------
    # 4) CRITICAL: force a pure numeric float matrix for statsmodels
    # ---------------------------------------------------------------------
    X = X.apply(pd.to_numeric, errors="coerce")

    # Drop any rows that became NaN due to coercion
    bad = X.isna().any(axis=1)
    if bad.any():
        d = d.loc[~bad].copy()
        X = X.loc[~bad].copy()
        y_codes = d[y_var].cat.codes

    X = X.astype(float)

    # Debug print (optional; keep while you’re still stabilizing)
    print(f"\n{model_name} X dtypes summary:")
    print(X.dtypes.value_counts())

    # ---------------------------------------------------------------------
    # 5) Fit with clustered SE; fall back to BFGS if Newton hits a singular
    #    Hessian (can occur with sparse binary dummies like crisis-year indicators)
    # ---------------------------------------------------------------------
    fit_method = "newton" if not add_year_fe else "bfgs"
    fit_maxiter = 200 if not add_year_fe else 500

    model = MNLogit(y_codes, X)
    try:
        res = model.fit(
            method=fit_method,
            maxiter=fit_maxiter,
            disp=False,
            cov_type="cluster",
            cov_kwds={"groups": d[cluster_var]}
        )
    except np.linalg.LinAlgError:
        print(f"{model_name}: Newton singular Hessian — retrying with BFGS")
        res = model.fit(
            method="bfgs",
            maxiter=500,
            disp=False,
            cov_type="cluster",
            cov_kwds={"groups": d[cluster_var]}
        )

    converged = getattr(res, "mle_retvals", {}).get("converged", None)
    print(f"{model_name}: method={fit_method}, converged={converged}")

    # ---------------------------------------------------------------------
    # 6) Map params columns -> outcome labels (non-baseline equations)
    # ---------------------------------------------------------------------
    categories = list(d[y_var].cat.categories)
    nonbase = categories[1:]  # ["Stationary","Unit root"]
    col_to_label = {int(col): nonbase[int(col)] for col in res.params.columns}

    nobs = int(X.shape[0])
    print(f"{model_name}: nobs={nobs}, countries={int(d[cluster_var].nunique())}, yearFE={add_year_fe}, cov_type={getattr(res,'cov_type','?')}")

    return res, X, y_codes, col_to_label, nobs, int(d[cluster_var].nunique())


def build_coef_table_for_memo(
    res,
    col_to_label,
    core_vars,
    model_label: str,
    include_year_fe_flag: bool,
    outcomes=("Stationary", "Unit root")
) -> pd.DataFrame:
    """
    Memo-ready coefficient block for ONE model.

    Output columns:
      model, term, row_type, Stationary, Unit root

    Notes:
    - Produces exactly two rows per term: coef and se
    - Keeps term on both rows (important for merging/pivoting)
    - Excludes year FE coefficients from the memo table (best practice for memos)
    """

    def star_from_p(p):
        if p < 0.001: return "***"
        if p < 0.05:  return "**"
        if p < 0.1:   return "*"
        return ""

    params = res.params
    bse    = res.bse
    pvals  = res.pvalues

    # We show constant + the "core" regressors only (no year dummy rows)
    terms = ["const"] + list(core_vars)

    rows = []
    for t in terms:
        # coef row
        r_coef = {"model": model_label, "term": t, "row_type": "coef"}
        # se row
        r_se   = {"model": model_label, "term": t, "row_type": "se"}

        for col in params.columns:
            oc = col_to_label[int(col)]
            if oc not in outcomes:
                continue

            b  = float(params.loc[t, col])
            se = float(bse.loc[t, col])
            pv = float(pvals.loc[t, col])
            stars = star_from_p(pv)

            r_coef[oc] = f"{b:.3f}{stars}"
            r_se[oc]   = f"({se:.3f})"

        rows.append(r_coef)
        rows.append(r_se)

    out = pd.DataFrame(rows)

    # Ensure both outcome columns exist
    for oc in outcomes:
        if oc not in out.columns:
            out[oc] = ""

    return out[["model", "term", "row_type", outcomes[0], outcomes[1]]]

def make_memo_wide_table(coef_blocks: list[pd.DataFrame]) -> pd.DataFrame:
    """
    Combine memo blocks into one wide memo table.

    Each block must have columns:
      model, term, row_type, Stationary, Unit root

    Output:
      Variable, row_type, Stationary (modelA), Unit root (modelA), Stationary (modelB), ...
    """

    outcomes = ["Stationary", "Unit root"]

    # Pretty labels for memo readability (optional)
    def pretty_term(t):
        mapping = {
            "const": "Constant",
            "fixed_er": "Fixed exchange rate",
            "current_def": "Current deficit",
            "comm_ex": "Commodity exporter",
            "oil":     "Oil exporter",
            "manu_ex": "Manufacturing exporter",
            "d_gfc":   "GFC period (2008-09)",
            "d_covid": "COVID period (2020-21)",
            "opn": "Trade openness",
            "opn_l1": "Trade openness (t-1)",
            "ka_open": "Capital account openness",
            "ka_open_l1": "Capital account openness (t-1)",
            "gsur_3_yr": "Fiscal balance (3-yr)",
            "gsur_3_yr_l1": "Fiscal balance (3-yr, t-1)",
            "gsur_def": "Fiscal balance dummy",
            "gsur_def_l1": "Fiscal balance dummy (t-1)",
            "ir_r_lmf": "Real interest rate",
            "ir_r_lmf_l1": "Real interest rate (t-1)",
            "fd_gap": "Financial development gap",
        }
        return mapping.get(t, t)

    # 1) Build a master skeleton of all (term,row_type) pairs in stable order
    keys = []
    for b in coef_blocks:
        keys.extend(list(zip(b["term"], b["row_type"])))
    keys = list(dict.fromkeys(keys))  # unique preserve order

    master = pd.DataFrame(keys, columns=["term", "row_type"])
    master["Variable"] = master["term"].apply(pretty_term)

    out = master[["term", "row_type", "Variable"]].copy()

    # 2) Merge each model's block in wide columns
    for b in coef_blocks:
        m = b["model"].iloc[0]

        tmp = b[["term", "row_type"] + outcomes].copy()
        tmp = tmp.rename(columns={
            "Stationary": f"Stationary ({m})",
            "Unit root":  f"Unit root ({m})",
        })

        out = out.merge(tmp, on=["term", "row_type"], how="left")

    # 3) Final formatting
    # Put Variable first; keep row_type so coauthors can see coef/se lines
    final_cols = ["Variable", "row_type"] + [c for c in out.columns if c not in ("term", "Variable", "row_type")]
    out = out[final_cols]

    # (Optional) Replace row_type values to look nicer
    out["row_type"] = out["row_type"].map({"coef": "coef", "se": "se"}).fillna(out["row_type"])

    return out

# =============================================================================
# Load + standardize + clean
# =============================================================================
df = pd.read_excel(data_xlsx)

df.columns = (
    df.columns.astype(str)
      .str.strip()
      .str.replace(r"\s+", "_", regex=True)
)

df = df.replace({".": np.nan, "": np.nan, " ": np.nan})

# Targeted crisis-year dummies (created here so need_cols check can find them).
# Year column is stored as dates (e.g. 1985-01-01), so extract the integer year
# with dt.year rather than pd.to_numeric which would coerce dates to NaN.
_yr = pd.to_datetime(df[year_var], errors="coerce").dt.year
df["d_gfc"]   = (_yr.isin([2008, 2009])).astype(int)
df["d_covid"] = (_yr.isin([2020, 2021])).astype(int)

# Determine all vars required, including bases for lags
all_x_vars = sorted(set(v for spec in SPECS.values() for v in spec["x_list"]))
lag_needed = [v for v in all_x_vars if v.endswith("_l1")]
base_needed = sorted({v[:-3] for v in lag_needed})

need_cols = [cluster_var, year_var, y_var] + sorted(set([v for v in all_x_vars if not v.endswith("_l1")] + base_needed))

missing = [c for c in need_cols if c not in df.columns]
if missing:
    raise KeyError(f"Missing columns in data after name standardization: {missing}\nAvailable: {df.columns.tolist()}")

df_model = df[need_cols].copy()

df_model[y_var] = clean_regime_labels(df_model[y_var])
df_model[y_var] = pd.Categorical(df_model[y_var], categories=regime_categories, ordered=False)

# Convert numeric columns (bases and non-lags)
numeric_cols = sorted(set([c for c in df_model.columns if c not in [cluster_var, year_var, y_var]]))
df_model = ensure_numeric_columns(df_model, numeric_cols)

# Create lag columns needed by the specs
df_model = add_lags(df_model, group_col=cluster_var, time_col=year_var, lag_specs=all_x_vars)

# =============================================================================
# Fit models + build memo tables
# =============================================================================
results = {}
coef_blocks = []
meta_rows = []

for model_name, spec in SPECS.items():
    x_list = spec["x_list"]
    add_year_fe_flag = spec["add_year_fe"]

    res, X, y_codes, col_to_label, nobs, n_countries = fit_mnlogit_cluster(
        df_model=df_model,
        x_vars=x_list,
        add_year_fe=add_year_fe_flag,
        model_name=model_name
    )

    block = build_coef_table_for_memo(
        res=res,
        col_to_label=col_to_label,
        core_vars=x_list,
        model_label=model_name,
        include_year_fe_flag=add_year_fe_flag
    )
    coef_blocks.append(block)

    llf = float(res.llf)
    llnull = float(res.llnull)
    mcfadden = 1 - (llf / llnull) if llnull != 0 else np.nan
    meta_rows.append({
        "model": model_name,
        "nobs": nobs,
        "countries": n_countries,
        "year_fe": "Yes" if add_year_fe_flag else "No",
        "loglik": llf,
        "mcfadden_R2": mcfadden,
        "bic": float(res.bic),
        "bic_per_obs": float(res.bic) / nobs
    })

meta_df = pd.DataFrame(meta_rows)
memo_table = make_memo_wide_table(coef_blocks)

memo_meta = meta_df[["model","nobs","countries","year_fe","bic_per_obs","mcfadden_R2"]].copy()
memo_meta["bic_per_obs"] = memo_meta["bic_per_obs"].map(lambda x: f"{x:.4f}")
memo_meta["mcfadden_R2"] = memo_meta["mcfadden_R2"].map(lambda x: f"{x:.4f}")

# =============================================================================
# Export
# =============================================================================
with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    memo_table.to_excel(writer, sheet_name="memo_coef_table", index=False)
    memo_meta.to_excel(writer, sheet_name="memo_model_info", index=False)
    meta_df.to_excel(writer, sheet_name="fit_stats_raw", index=False)

print()
print(f"Wrote memo tables to: {excel_out}")
