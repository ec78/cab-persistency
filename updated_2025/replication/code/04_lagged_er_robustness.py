"""
04_lagged_er_robustness.py
==========================
Robustness check: replace the contemporaneous fixed exchange rate dummy
(fixed_er) with its one-period lag (fixed_er_l1).

Models compared:
  Baseline  (C00058):       fixed_er, current_def, comm_ex, manu_ex, opn_l1, gsur_3_yr_l1
  Lagged ER (C00058_er_lag): fixed_er_l1, current_def, comm_ex, manu_ex, opn_l1, gsur_3_yr_l1

For each model:
  - Coefficient table with cluster-robust SEs (Table 4a equivalent)
  - Fit statistics: McFadden R², BIC/obs, log-likelihood (Table 6 equivalent)
  - Average marginal effects
  - 5-fold cross-validation log-loss (country-grouped folds, seed=42)
  - Confusion matrix and predictive accuracy (baseline only)

Output: output/04_lagged_er_robustness.xlsx
Sheets: comparison | baseline_coefs | lagged_er_coefs | marginal_effects |
        cv_results | confusion_matrix | predictive_accuracy
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
EXCEL_OUT  = OUTPUT_DIR / "04_lagged_er_robustness.xlsx"

# ---------------------------------------------------------------------------
# Settings
# ---------------------------------------------------------------------------
y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"

regime_categories = ["Explosive", "Stationary", "Unit root"]

BASELINE_X  = ["fixed_er",   "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]
LAGGED_ER_X = ["fixed_er_l1","current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]

TERM_LABELS = {
    "const":          "Constant",
    "fixed_er":       "Fixed exchange rate",
    "fixed_er_l1":    "Fixed exchange rate (t-1)",
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
    nonbase    = categories[1:]
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

# Numeric conversion
for c in ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn", "gsur_3_yr"]:
    if c in df.columns:
        df[c] = pd.to_numeric(df[c], errors="coerce")

# Create lags on FULL dataset before any subsetting
df = df.sort_values([cluster_var, year_var]).copy()
df["opn_l1"]       = df.groupby(cluster_var)["opn"].shift(1)
df["gsur_3_yr_l1"] = df.groupby(cluster_var)["gsur_3_yr"].shift(1)
df["fixed_er_l1"]  = df.groupby(cluster_var)["fixed_er"].shift(1)

# Enforce categorical ordering
df[y_var] = pd.Categorical(df[y_var], categories=regime_categories, ordered=False)

print(f"Dataset: {len(df)} rows, {df[cluster_var].nunique()} countries")
print(f"Regime distribution (before listwise deletion):")
print(df[y_var].value_counts(dropna=False))


# ---------------------------------------------------------------------------
# Fit function
# ---------------------------------------------------------------------------
def fit_mnlogit(df_full: pd.DataFrame, x_vars: list, model_name: str):
    """
    Fit MNLogit with cluster-robust SEs. Falls back to BFGS on singular Hessian.
    Returns: res, X, y_codes, col_map, df_est, nobs, n_countries
    """
    needed = [cluster_var, y_var] + x_vars
    df_est = df_full[needed].dropna(subset=needed).copy()

    nobs        = len(df_est)
    n_countries = int(df_est[cluster_var].nunique())

    df_est[y_var] = pd.Categorical(df_est[y_var],
                                   categories=regime_categories, ordered=False)
    y_codes = df_est[y_var].cat.codes
    X = sm.add_constant(df_est[x_vars].astype(float), has_constant="add")

    print(f"\n--- {model_name} ---")
    print(f"  nobs={nobs}, countries={n_countries}")

    model = MNLogit(y_codes, X)
    try:
        res = model.fit(
            method="newton", maxiter=300, disp=False,
            cov_type="cluster", cov_kwds={"groups": df_est[cluster_var]}
        )
    except np.linalg.LinAlgError:
        print(f"  Newton singular Hessian — falling back to BFGS")
        res = model.fit(
            method="bfgs", maxiter=500, disp=False,
            cov_type="cluster", cov_kwds={"groups": df_est[cluster_var]}
        )

    converged = getattr(res, "mle_retvals", {}).get("converged", None)
    col_map   = col_to_label_map(res, regime_categories)
    print(f"  Converged: {converged}")

    return res, X, y_codes, col_map, df_est, nobs, n_countries


# ---------------------------------------------------------------------------
# Build tables
# ---------------------------------------------------------------------------
def build_coef_table(res, col_map: dict, x_vars: list, model_name: str) -> pd.DataFrame:
    rows = []
    for term in ["const"] + x_vars:
        for col in res.params.columns:
            outcome = col_map[int(col)]
            b  = float(res.params.loc[term, col])
            se = float(res.bse.loc[term, col])
            pv = float(res.pvalues.loc[term, col])
            z  = b / se if se != 0 else np.nan
            rows.append({
                "model":    model_name,
                "term":     term,
                "label":    TERM_LABELS.get(term, term),
                "outcome":  outcome,
                "coef":     round(b, 4),
                "se":       round(se, 4),
                "z":        round(z, 3),
                "p_value":  round(pv, 4),
                "stars":    star_from_p(pv),
                "coef_str": f"{b:.3f}{star_from_p(pv)}",
                "se_str":   f"({se:.3f})",
            })
    return pd.DataFrame(rows)


def build_fit_row(res, nobs: int, n_countries: int, model_name: str) -> dict:
    llf    = float(res.llf)
    llnull = float(res.llnull)
    return {
        "model":       model_name,
        "nobs":        nobs,
        "countries":   n_countries,
        "log_lik":     round(llf, 4),
        "mcfadden_R2": round(1 - llf / llnull, 4),
        "bic_per_obs": round(float(res.bic) / nobs, 4),
        "aic_per_obs": round(float(res.aic) / nobs, 4),
    }


def build_ame_table(res, x_vars: list, model_name: str) -> pd.DataFrame:
    mfx     = res.get_margeff(at="overall")
    me_arr  = mfx.margeff
    me_se   = mfx.margeff_se
    # statsmodels excludes the intercept from margeff arrays
    assert me_arr.shape[0] == len(x_vars), (
        f"Margeff rows ({me_arr.shape[0]}) != regressors ({len(x_vars)})")

    rows = []
    for i, var in enumerate(x_vars):
        for j, outcome in enumerate(regime_categories):
            dy = float(me_arr[i, j])
            se = float(me_se[i, j])
            z  = dy / se if se != 0 else np.nan
            pv = float(2 * (1 - stats.norm.cdf(abs(z)))) if not np.isnan(z) else np.nan
            rows.append({
                "model":   model_name,
                "term":    var,
                "label":   TERM_LABELS.get(var, var),
                "outcome": outcome,
                "ame":     round(dy, 4),
                "se":      round(se, 4),
                "z":       round(z, 3),
                "p_value": round(pv, 4),
                "stars":   star_from_p(pv),
            })
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 5-fold cross-validation (country-grouped folds)
# ---------------------------------------------------------------------------
def cv_log_loss(df_full: pd.DataFrame, x_vars: list,
                n_folds: int = 5, model_name: str = "") -> pd.DataFrame:
    """
    5-fold CV with country-grouped folds to prevent data leakage across
    country time series. Uses seed=42 for reproducibility.
    Standard (non-cluster) SEs used within each fold fit.
    """
    needed = [cluster_var, y_var] + x_vars
    df_cv  = df_full[needed].dropna(subset=needed).copy()
    df_cv[y_var] = pd.Categorical(df_cv[y_var],
                                  categories=regime_categories, ordered=False)

    countries = df_cv[cluster_var].unique()
    rng       = np.random.default_rng(seed=42)
    shuffled  = rng.permutation(countries)
    fold_map  = {cn: (i % n_folds) for i, cn in enumerate(shuffled)}
    df_cv["_fold"] = df_cv[cluster_var].map(fold_map)

    print(f"\n  5-fold CV for {model_name}:")
    fold_results = []

    for fold in range(n_folds):
        train = df_cv[df_cv["_fold"] != fold].copy()
        test  = df_cv[df_cv["_fold"] == fold].copy()

        y_train = pd.Categorical(train[y_var], categories=regime_categories).codes
        y_test  = pd.Categorical(test[y_var],  categories=regime_categories).codes

        X_train = sm.add_constant(train[x_vars].astype(float), has_constant="add")
        X_test  = sm.add_constant(test[x_vars].astype(float),  has_constant="add")
        X_test  = X_test.reindex(columns=X_train.columns, fill_value=0)

        try:
            res_cv = MNLogit(y_train, X_train.astype(float)).fit(
                method="newton", maxiter=300, disp=False)
        except Exception:
            try:
                res_cv = MNLogit(y_train, X_train.astype(float)).fit(
                    method="bfgs", maxiter=500, disp=False)
            except Exception as e:
                print(f"    Fold {fold+1}: fit failed ({e}), recording NaN.")
                fold_results.append({"model": model_name, "fold": fold + 1,
                                     "log_loss": np.nan})
                continue

        pred_probs = np.clip(np.array(res_cv.predict(X_test.astype(float))), 1e-12, 1.0)
        n_test     = len(y_test)
        log_loss   = -np.mean([
            np.log(pred_probs[i, int(y_test.iloc[i])])
            for i in range(n_test)
        ])
        print(f"    Fold {fold+1}: n_train={len(y_train)}, "
              f"n_test={n_test}, log_loss={log_loss:.4f}")
        fold_results.append({"model": model_name, "fold": fold + 1,
                              "log_loss": round(log_loss, 4)})

    mean_loss = np.nanmean([r["log_loss"] for r in fold_results])
    fold_results.append({"model": model_name, "fold": "mean",
                          "log_loss": round(mean_loss, 4)})
    print(f"    Mean CV log-loss: {mean_loss:.4f}")
    return pd.DataFrame(fold_results)


# ---------------------------------------------------------------------------
# Confusion matrix + accuracy (baseline only)
# ---------------------------------------------------------------------------
def build_confusion(res, X, y_codes, model_name: str):
    pred_probs = res.predict(X)
    pred_class = pred_probs.values.argmax(axis=1)
    obs_class  = y_codes.values

    cm = pd.crosstab(
        pd.Series([regime_categories[i] for i in obs_class],  name="Observed"),
        pd.Series([regime_categories[i] for i in pred_class], name="Predicted")
    ).reindex(index=regime_categories, columns=regime_categories, fill_value=0)

    overall_acc = (pred_class == obs_class).mean()
    modal_frac  = (obs_class == np.bincount(obs_class).argmax()).mean()
    print(f"\n  Confusion matrix ({model_name}):")
    print(cm)
    print(f"  Overall accuracy:   {overall_acc:.4f}")
    print(f"  Base-rate accuracy: {modal_frac:.4f}")

    perclass_rows = []
    for j, cat in enumerate(regime_categories):
        tp = int(((obs_class == j) & (pred_class == j)).sum())
        fp = int(((obs_class != j) & (pred_class == j)).sum())
        fn = int(((obs_class == j) & (pred_class != j)).sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
        recall    = tp / (tp + fn) if (tp + fn) > 0 else np.nan
        perclass_rows.append({
            "category": cat, "n_actual": int((obs_class == j).sum()),
            "n_predicted": int((pred_class == j).sum()),
            "true_positives": tp, "false_positives": fp, "false_negatives": fn,
            "precision": round(precision, 4), "recall": round(recall, 4),
        })

    accuracy_df  = pd.DataFrame([{
        "model": model_name, "overall_accuracy": round(overall_acc, 4),
        "base_rate_accuracy": round(modal_frac, 4),
        "accuracy_gain": round(overall_acc - modal_frac, 4),
        "nobs": len(obs_class),
    }])
    perclass_df  = pd.DataFrame(perclass_rows)
    return cm, accuracy_df, perclass_df


# ---------------------------------------------------------------------------
# Fit both models
# ---------------------------------------------------------------------------
print("\n" + "=" * 60)
print("FITTING BASELINE MODEL (C00058)")
res_base, X_base, y_base, col_base, df_base, nobs_base, nc_base = \
    fit_mnlogit(df, BASELINE_X, "C00058 (Baseline)")

print("\n" + "=" * 60)
print("FITTING LAGGED ER MODEL (C00058_er_lag)")
res_lag, X_lag, y_lag, col_lag, df_lag, nobs_lag, nc_lag = \
    fit_mnlogit(df, LAGGED_ER_X, "C00058_er_lag")

# ---------------------------------------------------------------------------
# Fit statistics
# ---------------------------------------------------------------------------
fit_base = build_fit_row(res_base, nobs_base, nc_base, "C00058 (Baseline)")
fit_lag  = build_fit_row(res_lag,  nobs_lag,  nc_lag,  "C00058_er_lag")
comparison_df = pd.DataFrame([fit_base, fit_lag])

print("\nFit statistics:")
print(comparison_df[["model", "nobs", "countries",
                      "mcfadden_R2", "bic_per_obs", "log_lik"]].to_string(index=False))

# ---------------------------------------------------------------------------
# Coefficient tables
# ---------------------------------------------------------------------------
coef_base = build_coef_table(res_base, col_base, BASELINE_X,  "C00058 (Baseline)")
coef_lag  = build_coef_table(res_lag,  col_lag,  LAGGED_ER_X, "C00058_er_lag")

# ---------------------------------------------------------------------------
# Average marginal effects
# ---------------------------------------------------------------------------
print("\nComputing average marginal effects ...")
ame_base = build_ame_table(res_base, BASELINE_X,  "C00058 (Baseline)")
ame_lag  = build_ame_table(res_lag,  LAGGED_ER_X, "C00058_er_lag")
ame_all  = pd.concat([ame_base, ame_lag], ignore_index=True)

# ---------------------------------------------------------------------------
# Cross-validation
# ---------------------------------------------------------------------------
cv_base    = cv_log_loss(df, BASELINE_X,  model_name="C00058 (Baseline)")
cv_lag     = cv_log_loss(df, LAGGED_ER_X, model_name="C00058_er_lag")
cv_results = pd.concat([cv_base, cv_lag], ignore_index=True)

# ---------------------------------------------------------------------------
# Confusion matrix (baseline only)
# ---------------------------------------------------------------------------
cm_df, accuracy_df, perclass_df = build_confusion(
    res_base, X_base, y_base, "C00058 (Baseline)"
)

# ---------------------------------------------------------------------------
# Export
# ---------------------------------------------------------------------------
with pd.ExcelWriter(EXCEL_OUT, engine="openpyxl") as writer:
    comparison_df.to_excel(writer, sheet_name="comparison",          index=False)
    coef_base.to_excel(    writer, sheet_name="baseline_coefs",      index=False)
    coef_lag.to_excel(     writer, sheet_name="lagged_er_coefs",     index=False)
    ame_all.to_excel(      writer, sheet_name="marginal_effects",     index=False)
    cv_results.to_excel(   writer, sheet_name="cv_results",          index=False)
    cm_df.to_excel(        writer, sheet_name="confusion_matrix")
    accuracy_df.to_excel(  writer, sheet_name="predictive_accuracy",  index=False)
    perclass_df.to_excel(  writer, sheet_name="predictive_accuracy",  index=False,
                           startrow=len(accuracy_df) + 2)

print(f"\nSaved: {EXCEL_OUT}")
print("Sheets: comparison | baseline_coefs | lagged_er_coefs | "
      "marginal_effects | cv_results | confusion_matrix | predictive_accuracy")
