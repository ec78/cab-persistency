import itertools
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit
from sklearn.model_selection import GroupKFold

# =============================================================================
# USER SETTINGS (edit here)
# =============================================================================
fname_regimes = "clean-data/mnl_reg_data.xlsx"
excel_out = "mnlogit_aggressive_search.xlsx"

country_id = "cn"
year_var = "year"
y_var = "Regime_Type"

regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label = "Explosive"

# Base regressors you started with
base_x = [
    "fixed_er", "opn", "ka_open", "current_def",
    "gsur_3_yr", "gsur_def", "fd_gap", "ir_r_lmf",
    "comm_ex", "manu_ex"
]

# For endogeneity / timing: define variables we strongly prefer lagged
lag_policy = ["gsur_3_yr", "gsur_def", "ir_r_lmf"]
lag_robust = ["opn", "ka_open", "fd_gap"]  # optional lagging in search

# Controls: dummies vs continuous (used for optional standardization or diagnostics)
dummy_vars = ["fixed_er", "current_def", "comm_ex", "manu_ex"]

# Search controls (aggressive)
USE_YEAR_FE_GRID = [True, False]
LAG_OPENNESS_GRID = [False, True]   # try both
INCLUDE_FD_GAP_GRID = [False, True] # try both

# Subset search:
# We'll treat a "core block" as always included (structural dummies + openness)
# and allow aggressive subset selection within the "candidate block"
core_always = ["fixed_er", "current_def", "comm_ex", "manu_ex"]
candidate_block = ["opn", "ka_open", "gsur_3_yr", "gsur_def", "fd_gap", "ir_r_lmf"]

# Guardrails
MIN_COUNTRIES = 50
MIN_NOBS_RATIO = 0.65  # relative to baseline sample
MAX_SUBSET_SIZE = 6    # maximum number of variables chosen from candidate_block

# CV settings
N_SPLITS = 5
RANDOM_SEED = 123

# Score weights (you can tweak)
W_LOGLOSS = 1.0
W_BIC = 0.05  # small tie-breaker

# =============================================================================
# Helpers
# =============================================================================
def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = (
        out.columns.astype(str)
           .str.strip()
           .str.replace(r"\s+", "_", regex=True)
    )
    return out

def ensure_numeric(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out

def normalize_regime(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out[y_var] = (
        out[y_var].astype(str)
          .str.replace("\u00a0", " ", regex=False)
          .str.strip()
          .str.replace(r"\s+", " ", regex=True)
    )
    # canonical mapping
    out[y_var] = out[y_var].replace({
        "Unit Root": "Unit root",
        "UNIT ROOT": "Unit root",
        "unit root": "Unit root",
    })
    out[y_var] = pd.Categorical(out[y_var], categories=regime_categories, ordered=False)
    return out

def make_lag(df: pd.DataFrame, var: str, lag: int = 1) -> str:
    return f"{var}_l{lag}"

def add_lags(df: pd.DataFrame, vars_to_lag: list[str], lag: int = 1) -> pd.DataFrame:
    out = df.sort_values([country_id, year_var]).copy()
    for v in vars_to_lag:
        out[make_lag(out, v, lag)] = out.groupby(country_id)[v].shift(lag)
    return out

def build_X(df: pd.DataFrame, x_list: list[str], year_fe: bool) -> pd.DataFrame:
    X = df[x_list].copy()
    if year_fe:
        ydum = pd.get_dummies(df[year_var].astype(int), prefix="year", drop_first=True)
        X = pd.concat([X, ydum], axis=1)
    X = sm.add_constant(X, has_constant="add")
    return X

def fit_mnlogit(y_codes: pd.Series, X: pd.DataFrame):
    model = MNLogit(y_codes, X)
    res = model.fit(method="newton", maxiter=200, disp=False)
    return res

def predict_probs(res, X: pd.DataFrame) -> np.ndarray:
    p = res.predict(X)
    return np.asarray(p)

def log_loss_multiclass(y_true: np.ndarray, p: np.ndarray, eps: float = 1e-15) -> float:
    # y_true in {0,1,2}; p is N x 3
    p = np.clip(p, eps, 1 - eps)
    ll = -np.mean(np.log(p[np.arange(len(y_true)), y_true]))
    return float(ll)

def bic_per_obs(res, nobs: int) -> float:
    return float(res.bic) / nobs

# =============================================================================
# Load + prep
# =============================================================================
df = pd.read_excel(fname_regimes)
df = standardize_columns(df)

need = [country_id, year_var, y_var] + base_x
missing = [c for c in need if c not in df.columns]
if missing:
    raise KeyError(f"Missing columns after standardization: {missing}")

df = df[need].copy()

# missing tokens
df = df.replace({".": np.nan, "": np.nan, " ": np.nan})

df = ensure_numeric(df, base_x)
df = normalize_regime(df)

# Create lagged columns (policy vars always lagged in at least some specs)
df = df.sort_values([country_id, year_var]).copy()
df = add_lags(df, lag_policy, lag=1)
df = add_lags(df, lag_robust, lag=1)

# Baseline sample size used for MIN_NOBS_RATIO guardrail
baseline_cols = [country_id, year_var, y_var] + core_always + [make_lag(df, v, 1) for v in lag_policy]
df_baseline = df.dropna(subset=baseline_cols).copy()
BASELINE_N = df_baseline.shape[0]
BASELINE_C = df_baseline[country_id].nunique()

print(f"Baseline N={BASELINE_N}, countries={BASELINE_C}")

# =============================================================================
# Candidate generator
# =============================================================================
def candidate_specs():
    """
    Yields dicts describing candidate specifications.
    We enforce: policy vars are lagged (t-1) in all main candidates.
    Openness/finance can be lagged or contemporaneous depending on grid.
    fd_gap inclusion is toggled.
    """
    # all subsets of candidate_block up to MAX_SUBSET_SIZE
    for k in range(1, MAX_SUBSET_SIZE + 1):
        for subset in itertools.combinations(candidate_block, k):
            subset = list(subset)

            for year_fe in USE_YEAR_FE_GRID:
                for lag_open in LAG_OPENNESS_GRID:
                    for include_fd in INCLUDE_FD_GAP_GRID:

                        if (not include_fd) and ("fd_gap" in subset):
                            continue
                        if include_fd is False:
                            # fine, just skip it if present
                            subset_use = [v for v in subset if v != "fd_gap"]
                        else:
                            subset_use = subset.copy()

                        # Build regressor list with policy vars forced (lagged)
                        x_list = core_always.copy()

                        # Add subset variables, applying lagging rules
                        for v in subset_use:
                            if v in lag_policy:
                                x_list.append(make_lag(df, v, 1))
                            elif v in lag_robust:
                                x_list.append(make_lag(df, v, 1) if lag_open else v)
                            else:
                                x_list.append(v)

                        # Ensure uniqueness
                        x_list = list(dict.fromkeys(x_list))

                        # Must contain at least one non-core variable
                        if len([v for v in x_list if v not in core_always]) == 0:
                            continue

                        yield {
                            "year_fe": year_fe,
                            "lag_open": lag_open,
                            "include_fd_gap": include_fd,
                            "x_list": x_list,
                            "subset_raw": subset
                        }

# =============================================================================
# Evaluate candidates with group CV by country
# =============================================================================
gkf = GroupKFold(n_splits=N_SPLITS)

results = []
seen = set()

for i, spec in enumerate(candidate_specs()):
    # de-dup identical x_list/year_fe combos
    key = (tuple(spec["x_list"]), spec["year_fe"])
    if key in seen:
        continue
    seen.add(key)

    required = [country_id, year_var, y_var] + spec["x_list"]
    d = df.dropna(subset=required).copy()

    nobs = d.shape[0]
    nc = d[country_id].nunique()

    # guardrails
    if nc < MIN_COUNTRIES:
        continue
    if nobs < MIN_NOBS_RATIO * BASELINE_N:
        continue

    y_codes = d[y_var].cat.codes
    groups = d[country_id].values

    # Build X
    X = build_X(d, spec["x_list"], year_fe=spec["year_fe"])

    # CV log loss by country folds
    fold_ll = []
    ok = True
    for train_idx, test_idx in gkf.split(X, y_codes, groups=groups):
        Xtr, Xte = X.iloc[train_idx], X.iloc[test_idx]
        ytr, yte = y_codes.iloc[train_idx], y_codes.iloc[test_idx]

        # Fit (non-robust inside CV for speed; we are ranking models)
        try:
            res = fit_mnlogit(ytr, Xtr)
            pte = predict_probs(res, Xte)
            if pte.shape[1] != len(regime_categories):
                ok = False
                break
            fold_ll.append(log_loss_multiclass(yte.values, pte))
        except Exception:
            ok = False
            break

    if not ok or len(fold_ll) == 0:
        continue

    cv_logloss = float(np.mean(fold_ll))

    # Fit full sample for BIC (still non-robust for ranking)
    try:
        res_full = fit_mnlogit(y_codes, X)
        bic = bic_per_obs(res_full, nobs)
    except Exception:
        continue

    score = W_LOGLOSS * cv_logloss + W_BIC * bic

    results.append({
        "spec_id": f"C{i:05d}",
        "nobs": int(nobs),
        "countries": int(nc),
        "year_fe": bool(spec["year_fe"]),
        "lag_open": bool(spec["lag_open"]),
        "include_fd_gap": bool(spec["include_fd_gap"]),
        "subset_raw": ",".join(spec["subset_raw"]),
        "x_list": ",".join(spec["x_list"]),
        "cv_logloss": cv_logloss,
        "bic_per_obs": bic,
        "score": score,
    })

res_df = pd.DataFrame(results).sort_values("score").reset_index(drop=True)
print(res_df.head(10)[["spec_id","nobs","countries","year_fe","cv_logloss","bic_per_obs","score"]])

# =============================================================================
# Refit TOP specs with country-clustered SEs and export outputs
# =============================================================================
TOP_K = 10
top = res_df.head(TOP_K).copy()

coef_rows = []
fit_rows = []

for _, row in top.iterrows():
    spec_id = row["spec_id"]
    year_fe = bool(row["year_fe"])
    x_list = row["x_list"].split(",")

    required = [country_id, year_var, y_var] + x_list
    d = df.dropna(subset=required).copy()

    y_codes = d[y_var].cat.codes
    X = build_X(d, x_list, year_fe=year_fe)

    # cluster robust fit for inference (publication-relevant)
    model = MNLogit(y_codes, X)
    res = model.fit(
        method="newton", maxiter=200, disp=False,
        cov_type="cluster", cov_kwds={"groups": d[country_id]}
    )

    # Fit stats
    fit_rows.append({
        "spec_id": spec_id,
        "nobs": int(d.shape[0]),
        "countries": int(d[country_id].nunique()),
        "-2Ln(Lu)": float(-2 * res.llf),
        "-2Ln(Lnull)": float(-2 * res.llnull),
        "AIC_per_obs": float(res.aic) / d.shape[0],
        "BIC_per_obs": float(res.bic) / d.shape[0],
        "McFadden_R2": float(1 - res.llf / res.llnull) if res.llnull != 0 else np.nan,
        "cov_type": getattr(res, "cov_type", "unknown"),
    })

    # Correct equation label mapping (baseline excluded)
    cats = regime_categories
    cols = [int(c) for c in res.params.columns]
    # if cols are 0..J-2, they correspond to cats[1..]
    if sorted(cols) == list(range(len(cats)-1)):
        col_to_out = {c: cats[c+1] for c in cols}
    else:
        col_to_out = {c: cats[c] for c in cols}

    # Coefs long
    params = res.params
    bse = res.bse
    z = params / bse
    pvals = res.pvalues

    for term in params.index:
        for col in params.columns:
            out = col_to_out[int(col)]
            pv = float(pvals.loc[term, col])
            coef_rows.append({
                "spec_id": spec_id,
                "outcome": out,
                "term": term,
                "coef": float(params.loc[term, col]),
                "se": float(bse.loc[term, col]),
                "z": float(z.loc[term, col]),
                "p": pv,
            })

coef_df = pd.DataFrame(coef_rows)
fit_df = pd.DataFrame(fit_rows)

# =============================================================================
# Export Excel
# =============================================================================
with pd.ExcelWriter(excel_out, engine="openpyxl") as w:
    res_df.to_excel(w, sheet_name="ranked_candidates", index=False)
    top.to_excel(w, sheet_name="top_candidates", index=False)
    fit_df.to_excel(w, sheet_name="top_fit_stats_cluster", index=False)
    coef_df.to_excel(w, sheet_name="top_coef_long_cluster", index=False)

print(f"Wrote: {excel_out}")
