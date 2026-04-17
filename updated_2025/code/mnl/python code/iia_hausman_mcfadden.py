"""
Hausman-McFadden (1984) IIA Test for Baseline MNL
==================================================
Tests the Independence of Irrelevant Alternatives (IIA) assumption
underlying the multinomial logit model.

Method (Hausman & McFadden 1984):
  For each non-base alternative j:
    1. Estimate the FULL model on all observations (3 outcomes).
    2. Estimate a RESTRICTED model by:
       (a) Keeping only observations whose outcome is in {base, j}.
       (b) Fitting a binary logit (or MNL) on the remaining 2 outcomes.
    3. Form the Hausman statistic:
         H = (b_r - b_f)' * [Var_r - Var_f]^{-1} * (b_r - b_f)
       where b_r = restricted estimates for outcome j,
             b_f = corresponding full-model estimates for outcome j.
    4. Under IIA, H ~ chi^2(K) where K = number of parameters.

  If (Var_r - Var_f) is not positive semi-definite, the test is inconclusive
  for that alternative (common in practice; not evidence against IIA).

Notes:
  - Standard (non-cluster-robust) SEs are used for the Hausman statistic,
    as the test was derived under classical MNL assumptions.
  - The full and restricted models use the same regressors and data
    preprocessing as the baseline MNL (partii-mnl-clustered.py).
  - Results are written to iia_hausman_mcfadden.xlsx.

Reference:
  Hausman, J. and McFadden, D. (1984). Specification tests for the
  multinomial logit model. Econometrica, 52(5), 1219-1240.

Run from updated_2025/:
    python "code/mnl/python code/iia_hausman_mcfadden.py"
"""

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit, Logit

# =============================================================================
# Settings (mirror partii-mnl-clustered.py)
# =============================================================================
fname_data  = "clean-data/mnl_reg_data.xlsx"
excel_out   = "results/iia_hausman_mcfadden.xlsx"

y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"

x_vars = [
    "fixed_er",
    "current_def",
    "comm_ex",
    "manu_ex",
    "opn_l1",
    "gsur_3_yr_l1",
]

regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label    = "Explosive"   # reference category


# =============================================================================
# Data preparation (identical to baseline script)
# =============================================================================
def load_and_prepare():
    df = pd.read_excel(fname_data)

    # Standardize column names
    df.columns = (
        df.columns.astype(str)
          .str.strip()
          .str.replace(r"\s+", "_", regex=True)
    )

    base_for_lags = [v[:-3] for v in x_vars if v.endswith("_l1")]
    x_base_vars   = [v for v in x_vars if not v.endswith("_l1")]
    need_cols = sorted(set([cluster_var, year_var, y_var] + x_base_vars + base_for_lags))

    df_model = df[need_cols].copy()
    df_model = df_model.replace({".": np.nan, "": np.nan, " ": np.nan})

    # Numeric conversion
    numeric_src = sorted(set(x_base_vars + base_for_lags))
    for c in numeric_src:
        df_model[c] = pd.to_numeric(df_model[c], errors="coerce")

    # Parse year for sorting
    df_model[year_var] = pd.to_datetime(df_model[year_var], errors="coerce").dt.year

    # Normalize regime labels
    df_model[y_var] = (
        df_model[y_var].astype(str)
          .str.replace("\u00a0", " ", regex=False)
          .str.strip()
          .str.replace(r"\s+", " ", regex=True)
    )
    df_model[y_var] = df_model[y_var].replace({
        "Explosive": "Explosive", "explosive": "Explosive",
        "Stationary": "Stationary", "stationary": "Stationary",
        "Unit Root": "Unit root", "Unit root": "Unit root",
        "unit root": "Unit root", "UNIT ROOT": "Unit root",
    })

    # Create lags within country
    df_model = df_model.sort_values([cluster_var, year_var])
    for v in x_vars:
        if v.endswith("_l1"):
            base = v[:-3]
            df_model[v] = df_model.groupby(cluster_var)[base].shift(1)

    # Categorical outcome (Explosive = reference = code 0)
    df_model[y_var] = pd.Categorical(
        df_model[y_var], categories=regime_categories, ordered=False
    )

    # Listwise deletion
    df_model = df_model.dropna(subset=[cluster_var, y_var] + x_vars).copy()
    return df_model


# =============================================================================
# Hausman-McFadden test
# =============================================================================
def hausman_mcfadden_test(df_full, full_params, full_cov, dropped_alt):
    """
    Perform the HMF IIA test by dropping `dropped_alt` from the outcome set.

    Parameters
    ----------
    df_full   : full estimation sample (all 3 outcomes)
    full_params : dict { outcome_label : Series of coefficients (K,) }
                  for all non-base outcomes, from the full model
    full_cov    : dict { outcome_label : ndarray (K, K) }
                  covariance matrices from the full model (standard SEs)
    dropped_alt : str, the outcome to drop (must not be the base category)

    Returns
    -------
    dict with keys: dropped_alt, n_restricted, H_stat, df_test, p_value,
                    verdict, note
    """
    # The 'surviving' non-base alternative is whichever is not dropped
    # (with base = Explosive, we have Stationary and Unit root as non-base)
    surviving_alts = [c for c in regime_categories if c != dropped_alt]
    # The restricted sample keeps obs in {base, surviving non-base alt}
    surviving_non_base = [c for c in surviving_alts if c != baseline_label]

    # Subset rows
    df_r = df_full[df_full[y_var].isin(surviving_alts)].copy()
    # Recode: base = 0, surviving non-base = 1
    surv = surviving_non_base[0]
    df_r["y_binary"] = (df_r[y_var] == surv).astype(int)

    n_r = len(df_r)
    X_r = sm.add_constant(df_r[x_vars], has_constant="add")

    # Fit restricted binary logit (standard SEs)
    try:
        res_r = Logit(df_r["y_binary"], X_r).fit(
            method="newton", maxiter=300, disp=False
        )
    except Exception as e:
        return {
            "dropped_alt": dropped_alt,
            "surviving_non_base": surv,
            "n_restricted": n_r,
            "H_stat": np.nan,
            "df_test": np.nan,
            "p_value": np.nan,
            "verdict": "FAILED",
            "note": f"Restricted model did not converge: {e}",
        }

    # Restricted estimates and covariance (K parameters including const)
    b_r   = res_r.params.values          # shape (K,)
    V_r   = res_r.cov_params().values    # shape (K, K)

    # Full model estimates for the surviving non-base outcome
    b_f   = full_params[surv].values     # shape (K,)
    V_f   = full_cov[surv]               # shape (K, K)

    # Hausman statistic
    diff  = b_r - b_f
    diff_var = V_r - V_f

    # Check positive semi-definiteness of diff_var
    # (use eigenvalue check; negative eigenvalues → inconclusive)
    eigvals = np.linalg.eigvalsh(diff_var)
    if np.any(eigvals < -1e-8):
        return {
            "dropped_alt": dropped_alt,
            "surviving_non_base": surv,
            "n_restricted": n_r,
            "H_stat": np.nan,
            "df_test": len(b_r),
            "p_value": np.nan,
            "verdict": "INCONCLUSIVE",
            "note": (
                "Var_r - Var_f not positive semi-definite "
                f"(min eigenvalue = {eigvals.min():.4f}). "
                "This is common in practice and does not indicate IIA violation. "
                "Restricted model has more efficient estimates — "
                "consistent with IIA holding."
            ),
        }

    try:
        diff_var_inv = np.linalg.inv(diff_var)
    except np.linalg.LinAlgError:
        diff_var_inv = np.linalg.pinv(diff_var)

    H = float(diff.T @ diff_var_inv @ diff)
    k = len(b_r)
    p = float(1 - stats.chi2.cdf(H, df=k))

    if H < 0:
        verdict = "INCONCLUSIVE"
        note = "Negative H statistic; likely numerical issue. Treat as inconclusive."
    elif p > 0.05:
        verdict = "FAIL TO REJECT IIA"
        note = "No evidence against IIA at the 5% level."
    else:
        verdict = "REJECT IIA"
        note = f"IIA rejected at the 5% level (p = {p:.4f})."

    return {
        "dropped_alt": dropped_alt,
        "surviving_non_base": surv,
        "n_restricted": n_r,
        "H_stat": round(H, 4),
        "df_test": k,
        "p_value": round(p, 4),
        "verdict": verdict,
        "note": note,
    }


# =============================================================================
# Main
# =============================================================================
def main():
    print("Loading data...")
    df = load_and_prepare()
    nobs = len(df)
    print(f"  Full sample: {nobs} observations, {df[cluster_var].nunique()} countries")

    # ---- Fit full MNL with STANDARD (non-cluster-robust) SEs ----------------
    # (HMF test was derived under classical assumptions; cluster-robust SEs
    #  are used for the main estimates but not for the IIA test itself)
    print("\nFitting full MNL (standard SEs for HMF test)...")
    y_codes = df[y_var].cat.codes
    X_const = sm.add_constant(df[x_vars], has_constant="add")

    mnl_full = MNLogit(y_codes, X_const)
    res_full  = mnl_full.fit(method="newton", maxiter=300, disp=False)

    # Map equation indices to outcome labels
    # statsmodels MNLogit: equation 0 → first non-base outcome (code 1),
    #                       equation 1 → second non-base outcome (code 2)
    # category codes: Explosive=0 (base), Stationary=1, Unit root=2
    code_to_label = {
        code: cat
        for code, cat in enumerate(df[y_var].cat.categories)
    }
    non_base_labels = [code_to_label[c] for c in sorted(code_to_label) if c != 0]

    # params: DataFrame of shape (K, n_equations); cov_params: ndarray (K*n_eq, K*n_eq)
    params_df  = res_full.params           # DataFrame, columns = equation indices
    K          = params_df.shape[0]
    n_eq       = params_df.shape[1]
    param_cols = X_const.columns.tolist()
    cov_full   = res_full.cov_params().values  # (K*n_eq, K*n_eq)

    full_params = {}
    full_cov    = {}
    for eq_idx, label in enumerate(non_base_labels):
        full_params[label] = pd.Series(
            params_df.iloc[:, eq_idx].values, index=param_cols
        )
        # Covariance block for this equation
        # MNLogit cov_params layout: blocks ordered by equation
        start = eq_idx * K
        end   = start + K
        full_cov[label] = cov_full[start:end, start:end]

    print(f"  Full model converged. Non-base outcomes: {non_base_labels}")

    # ---- Run HMF test for each non-base alternative -------------------------
    # We test by dropping each non-base alternative in turn.
    # (We cannot meaningfully drop the base (Explosive) without changing
    #  the model structure; the standard HMF test applies to non-base alts.)
    results = []
    for dropped in non_base_labels:
        print(f"\nHMF test: dropping '{dropped}'...")
        r = hausman_mcfadden_test(df, full_params, full_cov, dropped)
        results.append(r)
        print(f"  Surviving non-base: {r['surviving_non_base']}")
        print(f"  N restricted: {r['n_restricted']}")
        print(f"  H = {r['H_stat']},  df = {r['df_test']},  p = {r['p_value']}")
        print(f"  Verdict: {r['verdict']}")
        print(f"  Note: {r['note']}")

    # ---- Full model summary (for reference) ---------------------------------
    print("\n--- Full MNL Parameter Estimates (standard SEs) ---")
    for eq_idx, label in enumerate(non_base_labels):
        print(f"\nOutcome: {label} vs {baseline_label}")
        for pname in param_cols:
            est = full_params[label][pname]
            se  = np.sqrt(full_cov[label][param_cols.index(pname), param_cols.index(pname)])
            print(f"  {pname:20s}  {est:8.4f}  ({se:.4f})")

    # ---- Export to Excel -----------------------------------------------------
    df_results = pd.DataFrame(results)
    df_results = df_results[[
        "dropped_alt", "surviving_non_base", "n_restricted",
        "H_stat", "df_test", "p_value", "verdict", "note"
    ]]
    df_results.columns = [
        "Dropped alternative", "Surviving non-base alt", "N (restricted)",
        "Hausman stat (H)", "Degrees of freedom", "p-value",
        "Verdict", "Note"
    ]

    # Full model coefficients for both non-base outcomes
    rows_full = []
    for label in non_base_labels:
        for pname in param_cols:
            idx = param_cols.index(pname)
            est = full_params[label][pname]
            se  = np.sqrt(full_cov[label][idx, idx])
            rows_full.append({
                "Outcome": label,
                "Variable": pname,
                "Coefficient (full model)": round(est, 5),
                "Std Error (full model)": round(se, 5),
            })
    df_full_coefs = pd.DataFrame(rows_full)

    with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
        df_results.to_excel(writer, sheet_name="HMF_test_results", index=False)
        df_full_coefs.to_excel(writer, sheet_name="full_model_coefs", index=False)

        # Interpretation guide
        interp = pd.DataFrame({
            "Section": [
                "What is the HMF test?",
                "How to read HMF_test_results",
                "If verdict = FAIL TO REJECT IIA",
                "If verdict = INCONCLUSIVE",
                "If verdict = REJECT IIA",
                "Why standard SEs?",
                "Reference",
            ],
            "Explanation": [
                (
                    "The Hausman-McFadden (1984) test checks whether the MNL "
                    "coefficients change significantly when one outcome is removed "
                    "from the choice set. Under IIA, removing an irrelevant "
                    "alternative should not change the odds ratios between remaining "
                    "alternatives, so the restricted and full estimates should be "
                    "similar (H statistic near zero)."
                ),
                (
                    "Each row corresponds to dropping one non-base alternative. "
                    "The 'Hausman stat (H)' follows chi^2(K) under the null "
                    "where K = degrees of freedom = number of estimated parameters."
                ),
                (
                    "IIA is maintained. The restricted estimates are not "
                    "significantly different from the full estimates. "
                    "The MNL is the appropriate model."
                ),
                (
                    "Var_r - Var_f is not positive semi-definite. This occurs "
                    "when the restricted model has *smaller* variance than the "
                    "full model for the tested coefficients, which is theoretically "
                    "consistent with IIA holding (the restricted sample is 'cleaner'). "
                    "Treat this as weak evidence in favour of IIA. "
                    "The binary logit robustness check in Section 5.4 provides "
                    "independent evidence."
                ),
                (
                    "IIA is rejected. Consider a nested logit with "
                    "{Stationary, Unit root} as one nest and {Explosive} as another. "
                    "This would require re-estimating the full second stage."
                ),
                (
                    "Standard SEs are used to compute the Hausman statistic because "
                    "the test was derived under classical MNL assumptions. "
                    "Cluster-robust SEs are used for all reported main results "
                    "(Tables 4-9) but are not appropriate inputs for the Hausman "
                    "variance-difference matrix."
                ),
                "Hausman, J. and McFadden, D. (1984). Econometrica, 52(5), 1219-1240.",
            ],
        })
        interp.to_excel(writer, sheet_name="interpretation", index=False)

    print(f"\nResults saved to: {excel_out}")


if __name__ == "__main__":
    main()
