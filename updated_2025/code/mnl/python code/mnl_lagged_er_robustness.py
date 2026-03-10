"""
mnl_lagged_er_robustness.py
===========================
Robustness check for C00058 baseline:
  - Baseline (C00058): fixed_er (contemporaneous) + current_def + comm_ex + manu_ex + opn_l1 + gsur_3_yr_l1
  - Lagged ER (C00058_er_lag): replace fixed_er with fixed_er_l1 (lagged one period within country)

Outputs:
  - Fit comparison (McFadden R2, BIC/obs, nobs, countries)
  - Coefficient tables with cluster-robust SEs and significance stars
  - Average marginal effects via get_margeff(at='overall')
  - 5-fold cross-validation log-loss (country-grouped folds)
  - Confusion matrix + predictive accuracy for baseline model only
  - All saved to mnl_lagged_er_robustness.xlsx in updated_2025/

Data conventions followed:
  - year column is date string (e.g. 1985-01-01) -> extract int with pd.to_datetime(...).dt.year
  - All lags computed within country group using groupby('cn').shift(1) before any subsetting
  - Cluster-robust SEs clustered at country level (cov_type='cluster', groups=df['cn'])
  - Reference category: Explosive (code 0)
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
import warnings

# =============================================================================
# SETTINGS
# =============================================================================
data_xlsx = "c:/Users/eclow/Documents/GitHub/cab-persistency/updated_2025/clean-data/mnl_reg_data.xlsx"
excel_out = "c:/Users/eclow/Documents/GitHub/cab-persistency/updated_2025/mnl_lagged_er_robustness.xlsx"

cluster_var = "cn"
year_var    = "year"
y_var       = "Regime_Type"

regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label    = "Explosive"

# Baseline (C00058): fixed_er is contemporaneous
BASELINE_X = ["fixed_er", "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]

# Lagged ER: replace fixed_er with fixed_er_l1
LAGGED_ER_X = ["fixed_er_l1", "current_def", "comm_ex", "manu_ex", "opn_l1", "gsur_3_yr_l1"]

# =============================================================================
# HELPERS
# =============================================================================
def star_from_p(p: float) -> str:
    """Return significance stars matching project convention."""
    if p < 0.001:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def ensure_numeric(df: pd.DataFrame, cols: list) -> pd.DataFrame:
    """Convert specified columns to numeric, coercing errors to NaN."""
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


def clean_regime_labels(s: pd.Series) -> pd.Series:
    """Normalize regime label strings (handles non-breaking spaces, casing)."""
    x = (s.astype(str)
          .str.replace("\u00a0", " ", regex=False)
          .str.strip()
          .str.replace(r"\s+", " ", regex=True))
    x = x.replace({
        "explosive":  "Explosive",
        "Stationary": "Stationary",
        "stationary": "Stationary",
        "Unit root":  "Unit root",
        "unit root":  "Unit root",
        "Unit Root":  "Unit root",
        "UNIT ROOT":  "Unit root",
    })
    return x


# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("=" * 70)
print("Loading data from:", data_xlsx)
print("=" * 70)

df_raw = pd.read_excel(data_xlsx, sheet_name=0)

# Standardize column names: strip whitespace, replace spaces with underscores
df_raw.columns = (
    df_raw.columns.astype(str)
          .str.strip()
          .str.replace(r"\s+", "_", regex=True)
)

print("\nAll columns in dataset:")
print(df_raw.columns.tolist())
print(f"\nShape: {df_raw.shape[0]} rows x {df_raw.shape[1]} columns")

# Replace common missing-value placeholders
df_raw = df_raw.replace({"." : np.nan, "": np.nan, " ": np.nan})

# =============================================================================
# 2. VARIABLE CONSTRUCTION (lags computed within country group BEFORE subsetting)
# =============================================================================
# Clean regime labels
df_raw[y_var] = clean_regime_labels(df_raw[y_var])

# Extract integer year (IMPORTANT: year stored as date string, not numeric)
df_raw["_year_int"] = pd.to_datetime(df_raw[year_var], errors="coerce").dt.year

# Sort by country and year before lagging
df_raw = df_raw.sort_values([cluster_var, "_year_int"]).copy()

# Identify all base columns needed (some lags already exist in data, others we create)
# Columns needed for baseline: fixed_er, current_def, comm_ex, manu_ex, opn, gsur_3_yr
# opn_l1 and gsur_3_yr_l1 may already be pre-lagged in the dataset; if so, use them directly.
# We also create fixed_er_l1 for the robustness model.
# Per project convention: create all lags via groupby('cn').shift(1)

# Create fixed_er_l1 within country group
if "fixed_er" in df_raw.columns:
    df_raw["fixed_er_l1"] = df_raw.groupby(cluster_var)["fixed_er"].shift(1)
    print("\nCreated fixed_er_l1 as one-period within-country lag of fixed_er.")
else:
    raise KeyError("'fixed_er' column not found in dataset. Cannot create fixed_er_l1.")

# If opn_l1 / gsur_3_yr_l1 are NOT already in the dataset, create them.
# (The dataset likely already has them pre-computed, but we guard both cases.)
for col_l1, base in [("opn_l1", "opn"), ("gsur_3_yr_l1", "gsur_3_yr")]:
    if col_l1 not in df_raw.columns:
        if base in df_raw.columns:
            df_raw[col_l1] = df_raw.groupby(cluster_var)[base].shift(1)
            print(f"Created {col_l1} from {base} via within-country shift(1).")
        else:
            raise KeyError(
                f"Neither '{col_l1}' nor its base '{base}' found in dataset."
            )
    else:
        print(f"Using pre-existing '{col_l1}' from dataset (not re-computing).")

# Convert all analysis variables to numeric (EXCEPT cluster, year, and outcome)
numeric_cols = [
    "fixed_er", "fixed_er_l1", "current_def", "comm_ex", "manu_ex",
    "opn_l1", "gsur_3_yr_l1"
]
df_raw = ensure_numeric(df_raw, numeric_cols)

# Enforce categorical ordering on outcome
df_raw[y_var] = pd.Categorical(df_raw[y_var], categories=regime_categories, ordered=False)

print(f"\nRegime_Type distribution (full dataset, before listwise deletion):")
print(df_raw[y_var].value_counts(dropna=False))


# =============================================================================
# 3. FIT FUNCTION
# =============================================================================
def fit_mnlogit_cluster(df_full: pd.DataFrame, x_vars: list, model_name: str):
    """
    Fit MNLogit with cluster-robust SEs clustered at the country level.

    Parameters
    ----------
    df_full   : full DataFrame (lags already computed)
    x_vars    : list of regressor names (not including intercept)
    model_name: string label used for printing

    Returns
    -------
    res, X, y_codes, col_to_label, df_est, nobs, n_countries
    """
    # Listwise deletion on the columns needed for this model
    needed = [cluster_var, y_var] + x_vars
    df_est = df_full[needed].dropna(subset=needed).copy()

    nobs       = len(df_est)
    n_countries = int(df_est[cluster_var].nunique())

    # Categorical outcome with fixed ordering (Explosive = 0)
    df_est[y_var] = pd.Categorical(df_est[y_var], categories=regime_categories, ordered=False)
    y_codes = df_est[y_var].cat.codes

    if (y_codes < 0).any():
        raise ValueError(f"Unexpected regime codes < 0 in {model_name}.")

    # Build X with intercept
    X_base = df_est[x_vars].copy().astype(float)
    X = sm.add_constant(X_base, has_constant="add")
    X = X.astype(float)

    print(f"\n--- {model_name} ---")
    print(f"  nobs={nobs}, countries={n_countries}")
    print(f"  X columns: {list(X.columns)}")

    # Fit with cluster-robust SEs
    model = MNLogit(y_codes, X)
    try:
        res = model.fit(
            method="newton",
            maxiter=300,
            disp=False,
            cov_type="cluster",
            cov_kwds={"groups": df_est[cluster_var]}
        )
    except np.linalg.LinAlgError:
        print(f"  WARNING: Newton singular Hessian — falling back to BFGS for {model_name}")
        res = model.fit(
            method="bfgs",
            maxiter=500,
            disp=False,
            cov_type="cluster",
            cov_kwds={"groups": df_est[cluster_var]}
        )

    converged = getattr(res, "mle_retvals", {}).get("converged", None)
    print(f"  Converged: {converged}  |  cov_type: {getattr(res, 'cov_type', '?')}")

    # Map params columns -> outcome labels (non-baseline equations only)
    categories = list(df_est[y_var].cat.categories)  # ['Explosive','Stationary','Unit root']
    nonbase = categories[1:]                           # ['Stationary','Unit root']
    col_to_label = {int(col): nonbase[int(col) - 1] for col in res.params.columns}
    # statsmodels MNLogit: params.columns are 1-indexed integers for non-baseline classes
    # (baseline class 0 is omitted). Map col index 1->'Stationary', 2->'Unit root'.

    return res, X, y_codes, col_to_label, df_est, nobs, n_countries


# =============================================================================
# 4. COMPUTE FIT STATISTICS
# =============================================================================
def compute_fit_stats(res, nobs: int, n_countries: int, model_name: str) -> dict:
    """Compute McFadden R2, BIC/obs, log-likelihood, nobs, countries."""
    llf    = float(res.llf)
    llnull = float(res.llnull)
    mcfadden = 1 - (llf / llnull) if llnull != 0 else np.nan
    bic      = float(res.bic)
    aic      = float(res.aic)
    return {
        "model":        model_name,
        "nobs":         nobs,
        "countries":    n_countries,
        "log_lik":      llf,
        "log_lik_null": llnull,
        "mcfadden_R2":  mcfadden,
        "bic":          bic,
        "bic_per_obs":  bic / nobs,
        "aic":          aic,
        "aic_per_obs":  aic / nobs,
    }


# =============================================================================
# 5. BUILD COEFFICIENT TABLE
# =============================================================================
def build_coef_table(res, col_to_label: dict, x_vars: list, model_name: str) -> pd.DataFrame:
    """
    Build a tidy coefficient table with coef, SE, z-stat, p-value, and stars.
    Returns a DataFrame with one row per (term, outcome equation).
    """
    params  = res.params    # DataFrame: index=regressors, columns=non-baseline outcome codes
    bse     = res.bse       # cluster-robust SEs
    pvals   = res.pvalues

    rows = []
    all_terms = ["const"] + list(x_vars)
    for term in all_terms:
        for col in params.columns:
            outcome = col_to_label[int(col)]
            b   = float(params.loc[term, col])
            se  = float(bse.loc[term, col])
            z   = b / se if se != 0 else np.nan
            pv  = float(pvals.loc[term, col])
            rows.append({
                "model":   model_name,
                "term":    term,
                "outcome": outcome,
                "coef":    round(b, 4),
                "se":      round(se, 4),
                "z_stat":  round(z, 3),
                "p_value": round(pv, 4),
                "stars":   star_from_p(pv),
                "coef_str": f"{b:.3f}{star_from_p(pv)}",
                "se_str":   f"({se:.3f})",
            })
    return pd.DataFrame(rows)


# =============================================================================
# 6. MARGINAL EFFECTS
# =============================================================================
def compute_marginal_effects(res, x_vars: list, model_name: str) -> pd.DataFrame:
    """
    Compute average marginal effects via get_margeff(at='overall').
    Falls back to get_margeff() without 'overall' if the first call fails.
    Returns a tidy DataFrame.
    """
    print(f"\n  Computing marginal effects for {model_name}...")
    mfx = None
    try:
        mfx = res.get_margeff(at="overall")
    except Exception as e:
        print(f"  WARNING: get_margeff(at='overall') failed ({e}). Trying fallback get_margeff().")
        try:
            mfx = res.get_margeff()
        except Exception as e2:
            print(f"  WARNING: Fallback get_margeff() also failed ({e2}). Skipping marginal effects.")
            return pd.DataFrame()

    # Align marginal effects row names with regressors
    # statsmodels typically excludes the intercept from margeff arrays
    k_me   = mfx.margeff.shape[0]
    x_with_const = ["const"] + list(x_vars)
    if k_me == len(x_vars):
        me_names = list(x_vars)
    elif k_me == len(x_with_const):
        me_names = x_with_const
    else:
        # Use as many names as we can
        me_names = list(x_vars)[:k_me]
        print(f"  WARNING: margeff array length ({k_me}) doesn't match expected. Using first {k_me} regressor names.")

    # Build tidy output
    rows = []
    for i, name in enumerate(me_names):
        for j, outcome in enumerate(regime_categories):
            dy  = float(mfx.margeff[i, j])
            se  = float(mfx.margeff_se[i, j])
            z   = dy / se if se != 0 else np.nan
            pv  = float(2 * (1 - stats.norm.cdf(abs(z)))) if not np.isnan(z) else np.nan
            rows.append({
                "model":   model_name,
                "term":    name,
                "outcome": outcome,
                "ame":     round(dy, 4),
                "se":      round(se, 4),
                "z_stat":  round(z, 3),
                "p_value": round(pv, 4),
                "stars":   star_from_p(pv),
            })
    return pd.DataFrame(rows)


# =============================================================================
# 7. 5-FOLD CROSS-VALIDATION (country-grouped folds)
# =============================================================================
def cv_log_loss(df_full: pd.DataFrame, x_vars: list, n_folds: int = 5,
                model_name: str = "") -> pd.DataFrame:
    """
    5-fold cross-validation with country-grouped folds.

    Countries are assigned to folds (not individual observations), so the
    train/test split is clean with no data leakage across country time series.

    For each fold: fit MNLogit on train, predict on test, compute log-loss.
    Returns DataFrame with one row per fold + a mean row.
    """
    # Listwise deletion for this model
    needed = [cluster_var, y_var] + x_vars
    df_cv = df_full[needed].dropna(subset=needed).copy()
    df_cv[y_var] = pd.Categorical(df_cv[y_var], categories=regime_categories, ordered=False)

    # Assign countries to folds
    countries = df_cv[cluster_var].unique()
    rng = np.random.default_rng(seed=42)   # fixed seed for reproducibility
    shuffled = rng.permutation(countries)
    fold_assignment = {cn: (i % n_folds) for i, cn in enumerate(shuffled)}
    df_cv["_fold"] = df_cv[cluster_var].map(fold_assignment)

    fold_losses = []
    print(f"\n  5-fold CV for {model_name}:")

    for fold in range(n_folds):
        train = df_cv[df_cv["_fold"] != fold].copy()
        test  = df_cv[df_cv["_fold"] == fold].copy()

        # Encode y
        y_train = pd.Categorical(train[y_var], categories=regime_categories, ordered=False).codes
        y_test  = pd.Categorical(test[y_var],  categories=regime_categories, ordered=False).codes

        # Build X
        X_train = sm.add_constant(train[x_vars].astype(float), has_constant="add")
        X_test  = sm.add_constant(test[x_vars].astype(float),  has_constant="add")
        # Ensure test has same columns (in same order) as train
        X_test  = X_test.reindex(columns=X_train.columns, fill_value=0)

        # Fit (no cluster SEs in CV to avoid degenerate train folds)
        try:
            model = MNLogit(y_train, X_train.astype(float))
            res_cv = model.fit(method="newton", maxiter=300, disp=False)
        except Exception:
            try:
                res_cv = model.fit(method="bfgs", maxiter=500, disp=False)
            except Exception as e:
                print(f"    Fold {fold+1}: fit failed ({e}), recording NaN.")
                fold_losses.append({"model": model_name, "fold": fold + 1, "log_loss": np.nan})
                continue

        # Predict probabilities on test set
        pred_probs = np.array(res_cv.predict(X_test.astype(float)))  # shape (n_test, 3)

        # Clip probabilities away from 0 to avoid log(0)
        pred_probs = np.clip(pred_probs, 1e-12, 1.0)

        # Log-loss: -mean over obs of log(predicted prob of true class)
        n_test = len(y_test)
        log_loss_val = -np.mean([
            np.log(pred_probs[i, int(y_test.iloc[i] if hasattr(y_test, "iloc") else y_test[i])])
            for i in range(n_test)
        ])

        print(f"    Fold {fold+1}: n_train={len(y_train)}, n_test={n_test}, log_loss={log_loss_val:.4f}")
        fold_losses.append({"model": model_name, "fold": fold + 1, "log_loss": round(log_loss_val, 4)})

    # Mean row
    mean_loss = np.nanmean([r["log_loss"] for r in fold_losses])
    fold_losses.append({"model": model_name, "fold": "mean", "log_loss": round(mean_loss, 4)})
    print(f"    Mean CV log-loss: {mean_loss:.4f}")

    return pd.DataFrame(fold_losses)


# =============================================================================
# 8. CONFUSION MATRIX + PREDICTIVE ACCURACY (baseline only)
# =============================================================================
def compute_confusion_and_accuracy(res, X, y_codes, model_name: str):
    """
    Compute confusion matrix, overall accuracy, base-rate accuracy,
    and per-class precision/recall for a fitted MNLogit model.

    Returns:
        cm_df            : confusion matrix as DataFrame
        accuracy_df      : summary accuracy stats
        perclass_df      : per-class precision and recall
    """
    pred_probs = res.predict(X)           # shape (N, 3): probabilities for all 3 classes
    pred_class = pred_probs.values.argmax(axis=1)
    obs_class  = y_codes.values

    # Confusion matrix (rows=observed, cols=predicted)
    cm = pd.crosstab(
        pd.Series([regime_categories[i] for i in obs_class],  name="Observed"),
        pd.Series([regime_categories[i] for i in pred_class], name="Predicted")
    ).reindex(index=regime_categories, columns=regime_categories, fill_value=0)

    print(f"\n  Confusion matrix for {model_name}:")
    print(cm)

    # Overall accuracy
    overall_acc = (pred_class == obs_class).mean()

    # Base-rate accuracy = fraction in modal category
    modal_frac = (obs_class == np.bincount(obs_class).argmax()).mean()

    print(f"  Overall accuracy:   {overall_acc:.4f}")
    print(f"  Base-rate accuracy: {modal_frac:.4f}")

    # Per-class precision and recall
    perclass_rows = []
    for j, cat in enumerate(regime_categories):
        tp = int(((obs_class == j) & (pred_class == j)).sum())
        fp = int(((obs_class != j) & (pred_class == j)).sum())
        fn = int(((obs_class == j) & (pred_class != j)).sum())
        precision = tp / (tp + fp) if (tp + fp) > 0 else np.nan
        recall    = tp / (tp + fn) if (tp + fn) > 0 else np.nan
        perclass_rows.append({
            "category": cat,
            "n_actual":   int((obs_class == j).sum()),
            "n_predicted": int((pred_class == j).sum()),
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall":    round(recall, 4),
        })
        print(f"    {cat}: precision={precision:.4f}, recall={recall:.4f}")

    accuracy_df = pd.DataFrame([{
        "model":              model_name,
        "overall_accuracy":   round(overall_acc, 4),
        "base_rate_accuracy": round(modal_frac, 4),
        "accuracy_gain":      round(overall_acc - modal_frac, 4),
        "nobs":               len(obs_class),
    }])

    perclass_df = pd.DataFrame(perclass_rows)
    return cm, accuracy_df, perclass_df


# =============================================================================
# MAIN: FIT BOTH MODELS
# =============================================================================
print("\n" + "=" * 70)
print("FITTING BASELINE MODEL (C00058)")
print("  Regressors:", BASELINE_X)
print("=" * 70)

res_base, X_base, y_base, col_to_label_base, df_base, nobs_base, nc_base = \
    fit_mnlogit_cluster(df_raw, BASELINE_X, "C00058 (Baseline)")

print("\n" + "=" * 70)
print("FITTING LAGGED ER MODEL (C00058_er_lag)")
print("  Regressors:", LAGGED_ER_X)
print("=" * 70)

res_lag, X_lag, y_lag, col_to_label_lag, df_lag, nobs_lag, nc_lag = \
    fit_mnlogit_cluster(df_raw, LAGGED_ER_X, "C00058_er_lag")


# =============================================================================
# FIT STATISTICS
# =============================================================================
print("\n" + "=" * 70)
print("FIT STATISTICS")
print("=" * 70)

fit_base = compute_fit_stats(res_base, nobs_base, nc_base, "C00058 (Baseline)")
fit_lag  = compute_fit_stats(res_lag,  nobs_lag,  nc_lag,  "C00058_er_lag")

for fs in [fit_base, fit_lag]:
    print(f"\n  {fs['model']}:")
    print(f"    nobs={fs['nobs']}, countries={fs['countries']}")
    print(f"    McFadden R2 = {fs['mcfadden_R2']:.4f}")
    print(f"    BIC/obs     = {fs['bic_per_obs']:.4f}")
    print(f"    AIC/obs     = {fs['aic_per_obs']:.4f}")
    print(f"    Log-lik     = {fs['log_lik']:.4f}")

comparison_df = pd.DataFrame([fit_base, fit_lag])
print("\nComparison table:")
print(comparison_df[["model", "nobs", "countries", "mcfadden_R2", "bic_per_obs", "aic_per_obs", "log_lik"]].to_string(index=False))


# =============================================================================
# COEFFICIENT TABLES
# =============================================================================
print("\n" + "=" * 70)
print("COEFFICIENT TABLES")
print("=" * 70)

coef_base = build_coef_table(res_base, col_to_label_base, BASELINE_X,  "C00058 (Baseline)")
coef_lag  = build_coef_table(res_lag,  col_to_label_lag,  LAGGED_ER_X, "C00058_er_lag")

for label, ctab in [("BASELINE", coef_base), ("LAGGED ER", coef_lag)]:
    print(f"\n  {label} coefficients (cluster-robust SEs):")
    print(f"  {'Term':<20} {'Outcome':<12} {'Coef':>8} {'SE':>8} {'z':>7} {'p':>8} {'Stars'}")
    print("  " + "-" * 72)
    for _, row in ctab.iterrows():
        print(f"  {row['term']:<20} {row['outcome']:<12} {row['coef']:>8.3f} "
              f"{row['se']:>8.3f} {row['z_stat']:>7.2f} {row['p_value']:>8.4f}  {row['stars']}")


# =============================================================================
# MARGINAL EFFECTS
# =============================================================================
print("\n" + "=" * 70)
print("AVERAGE MARGINAL EFFECTS")
print("=" * 70)

ame_base = compute_marginal_effects(res_base, BASELINE_X,  "C00058 (Baseline)")
ame_lag  = compute_marginal_effects(res_lag,  LAGGED_ER_X, "C00058_er_lag")

for label, ame in [("BASELINE", ame_base), ("LAGGED ER", ame_lag)]:
    if ame.empty:
        print(f"\n  {label}: marginal effects not available.")
        continue
    print(f"\n  {label} average marginal effects:")
    print(f"  {'Term':<20} {'Outcome':<12} {'AME':>8} {'SE':>8} {'z':>7} {'p':>8} {'Stars'}")
    print("  " + "-" * 72)
    for _, row in ame.iterrows():
        print(f"  {row['term']:<20} {row['outcome']:<12} {row['ame']:>8.4f} "
              f"{row['se']:>8.4f} {row['z_stat']:>7.2f} {row['p_value']:>8.4f}  {row['stars']}")


# =============================================================================
# CROSS-VALIDATION
# =============================================================================
print("\n" + "=" * 70)
print("5-FOLD CROSS-VALIDATION (country-grouped folds)")
print("=" * 70)

cv_base = cv_log_loss(df_raw, BASELINE_X,  n_folds=5, model_name="C00058 (Baseline)")
cv_lag  = cv_log_loss(df_raw, LAGGED_ER_X, n_folds=5, model_name="C00058_er_lag")

cv_results = pd.concat([cv_base, cv_lag], ignore_index=True)
print("\n  CV results summary:")
print(cv_results.to_string(index=False))


# =============================================================================
# CONFUSION MATRIX + ACCURACY (baseline only)
# =============================================================================
print("\n" + "=" * 70)
print("CONFUSION MATRIX & PREDICTIVE ACCURACY (Baseline C00058 only)")
print("=" * 70)

cm_df, accuracy_df, perclass_df = compute_confusion_and_accuracy(
    res_base, X_base, y_base, "C00058 (Baseline)"
)


# =============================================================================
# EXPORT TO EXCEL
# =============================================================================
print("\n" + "=" * 70)
print(f"Saving results to: {excel_out}")
print("=" * 70)

with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:

    # Sheet 1: side-by-side fit statistics
    comparison_df.to_excel(writer, sheet_name="comparison", index=False)

    # Sheet 2: baseline coefficient table
    coef_base.to_excel(writer, sheet_name="baseline_coefs", index=False)

    # Sheet 3: lagged ER coefficient table
    coef_lag.to_excel(writer, sheet_name="lagged_er_coefs", index=False)

    # Sheet 4: CV log-loss results
    cv_results.to_excel(writer, sheet_name="cv_results", index=False)

    # Sheet 5: confusion matrix
    cm_df.to_excel(writer, sheet_name="confusion_matrix")

    # Sheet 6: predictive accuracy
    # Combine overall accuracy and per-class stats in one sheet
    # Write overall accuracy block first, then per-class
    accuracy_df.to_excel(writer, sheet_name="predictive_accuracy", index=False, startrow=0)
    startrow_perclass = len(accuracy_df) + 2
    perclass_df.to_excel(writer, sheet_name="predictive_accuracy", index=False,
                          startrow=startrow_perclass)

    # Also write marginal effects if available
    if not ame_base.empty or not ame_lag.empty:
        pd.concat([ame_base, ame_lag], ignore_index=True).to_excel(
            writer, sheet_name="marginal_effects", index=False
        )

print("\nDone. All results saved.")
print("\nSheets written:")
print("  comparison         — fit statistics for both models")
print("  baseline_coefs     — C00058 coefficient table")
print("  lagged_er_coefs    — C00058_er_lag coefficient table")
print("  cv_results         — 5-fold CV log-loss by fold and mean")
print("  confusion_matrix   — baseline predicted vs actual")
print("  predictive_accuracy— overall accuracy, base rate, per-class precision/recall")
if not (ame_base.empty and ame_lag.empty):
    print("  marginal_effects   — average marginal effects for both models")
