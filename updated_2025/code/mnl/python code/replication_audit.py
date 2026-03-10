"""
replication_audit.py
====================
Code-reviewer replication check for the MNL section of the CAB persistency paper.

Checks every number reported in:
  - Table 4  (baseline MNL coefficients, cluster-robust SEs)
  - Table 5  (average marginal effects)
  - Table 6  (model comparison fit stats)
  - Table 7  (binary logit robustness)
  - Table 8  (income subgroup fit stats)
  - Table 9  (time-period subgroup fit stats)
  - Section 5.1.1 / 5.4 sample composition

Pass/Fail tolerance:
  - Coefficients / SEs: abs diff < 0.001  (rounding to 3 d.p. in paper)
  - Fit stats:          abs diff < 0.0005 (rounding to 4 d.p.)
  - Counts:             exact integer match

Output: console report + replication_audit_results.xlsx
"""

import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit, Logit

BASE       = "c:/Users/eclow/Documents/GitHub/cab-persistency/updated_2025/"
DATA_FILE  = BASE + "clean-data/mnl_reg_data.xlsx"
AUDIT_OUT  = BASE + "replication_audit_results.xlsx"

# ---------------------------------------------------------------------------
# Reported values from the paper / model-selection memo
# ---------------------------------------------------------------------------
PAPER = {
    # --- Sample ---
    "nobs_baseline":      2451,
    "n_countries":        74,
    "n_explosive":        134,
    "n_stationary":       943,
    "n_unit_root":        1374,
    "pct_explosive":      0.0547,   # 5.47%  (paper says 5.5%)
    "pct_stationary":     0.3850,
    "pct_unit_root":      0.5607,

    # --- Baseline fit (Table 6 / Section 5.2) ---
    "mcfadden_r2":        0.0504,
    "bic_per_obs":        1.661,

    # --- Baseline coefficients, Stationary equation (Table 4) ---
    "coef_const_S":       3.085,
    "se_const_S":         1.087,
    "coef_fixed_er_S":    1.869,
    "se_fixed_er_S":      0.556,
    "coef_current_def_S": 0.842,
    "se_current_def_S":   0.481,
    "coef_comm_ex_S":     0.188,
    "se_comm_ex_S":       0.759,
    "coef_manu_ex_S":    -1.204,
    "se_manu_ex_S":       0.683,
    "coef_opn_l1_S":     -1.273,
    "se_opn_l1_S":        0.557,
    "coef_gsur_S":        1.657,
    "se_gsur_S":          1.933,

    # --- Baseline coefficients, Unit root equation (Table 4) ---
    "coef_const_U":       3.554,
    "se_const_U":         1.148,
    "coef_fixed_er_U":    1.980,
    "se_fixed_er_U":      0.549,
    "coef_current_def_U": 0.728,
    "se_current_def_U":   0.503,
    "coef_comm_ex_U":    -0.137,
    "se_comm_ex_U":       0.757,
    "coef_manu_ex_U":    -1.477,
    "se_manu_ex_U":       0.670,
    "coef_opn_l1_U":     -0.819,
    "se_opn_l1_U":        0.453,
    "coef_gsur_U":        3.241,
    "se_gsur_U":          1.809,

    # --- AMEs (Table 5; significant ones only) ---
    "ame_fixed_er_explosive":   -0.091,
    "ame_opn_l1_explosive":      0.047,

    # --- Binary logit (Table 7): none significant ---
    # Report p-values > 0.25 for all 6 regressors
    "binary_logit_any_sig":     False,   # no p < 0.10

    # --- Income subgroups (Table 8) ---
    "emerging_nobs":            903,
    "emerging_countries":       28,
    "emerging_n_explosive":     116,
    "emerging_mcfadden":        0.1863,
    "emerging_bic_per_obs":     1.671,
    "advanced_nobs":            1041,
    "advanced_countries":       23,
    "advanced_n_explosive":     15,
    "low_income_nobs":          507,
    "low_income_countries":     23,
    "low_income_n_explosive":   3,

    # --- Time subgroups (Table 9) ---
    "pregfc_mcfadden":          0.0420,
    "pregfc_bic_per_obs":       1.692,
    "postgfc_mcfadden":         0.0893,
    "postgfc_bic_per_obs":      1.645,
}

TOL_COEF  = 0.001
TOL_FIT   = 0.0005
TOL_AME   = 0.001


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def star_from_p(p):
    if p < 0.01:  return "***"
    if p < 0.05:  return "**"
    if p < 0.10:  return "*"
    return ""


def chk(label, computed, expected, tol, unit=""):
    diff = abs(computed - expected)
    ok   = diff <= tol
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: computed={computed:.6g}  "
          f"expected={expected:.6g}  diff={diff:.6g}{unit}")
    return {"check": label, "status": status,
            "computed": computed, "expected": expected, "diff": diff}


def chk_exact(label, computed, expected):
    ok = (computed == expected)
    status = "PASS" if ok else "FAIL"
    print(f"  [{status}] {label}: computed={computed}  expected={expected}")
    return {"check": label, "status": status,
            "computed": computed, "expected": expected, "diff": abs(computed - expected)}


# ---------------------------------------------------------------------------
# Data loading (shared)
# ---------------------------------------------------------------------------
y_var       = "Regime_Type"
cluster_var = "cn"
year_var    = "year"
x_vars      = ["fixed_er", "current_def", "comm_ex", "manu_ex",
                "opn_l1", "gsur_3_yr_l1"]
regime_categories = ["Explosive", "Stationary", "Unit root"]

df_raw = pd.read_excel(DATA_FILE)
df_raw.columns = (df_raw.columns.astype(str).str.strip()
                  .str.replace(r"\s+", "_", regex=True))
df_raw = df_raw.replace({"." : np.nan, "": np.nan, " ": np.nan})

df_raw[y_var] = (
    df_raw[y_var].astype(str)
      .str.replace("\u00a0", " ", regex=False)
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)
      .replace({"explosive": "Explosive", "Stationary": "Stationary",
                "stationary": "Stationary", "Unit Root": "Unit root",
                "Unit root": "Unit root", "unit root": "Unit root",
                "UNIT ROOT": "Unit root"})
)

base_for_lags = sorted({v[:-3] for v in x_vars if v.endswith("_l1")})
x_base_vars   = [v for v in x_vars if not v.endswith("_l1")]
for c in sorted(set(x_base_vars + base_for_lags)):
    df_raw[c] = pd.to_numeric(df_raw[c], errors="coerce")

# Integer year (for subgroup time filters)
yr_int = pd.to_datetime(df_raw[year_var], errors="coerce").dt.year

# Create lags on full dataset BEFORE any subsetting
df_raw = df_raw.sort_values([cluster_var, year_var]).copy()
for lag_col in sorted({v for v in x_vars if v.endswith("_l1")}):
    base = lag_col[:-3]
    df_raw[lag_col] = df_raw.groupby(cluster_var)[base].shift(1)

df_raw[y_var] = pd.Categorical(df_raw[y_var],
                               categories=regime_categories, ordered=False)

results_all = []

# ===========================================================================
# SECTION 1 — Sample composition
# ===========================================================================
print("\n" + "="*70)
print("SECTION 1 — Sample composition (baseline spec C00058)")
print("="*70)

needed = [cluster_var, year_var, y_var] + x_vars
df_base = df_raw[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()
df_base[y_var] = pd.Categorical(df_base[y_var],
                                categories=regime_categories, ordered=False)

nobs        = len(df_base)
n_countries = df_base[cluster_var].nunique()
vc          = df_base[y_var].value_counts()
n_exp       = int(vc.get("Explosive",  0))
n_sta       = int(vc.get("Stationary", 0))
n_ur        = int(vc.get("Unit root",  0))

results_all += [
    chk_exact("nobs",          nobs,        PAPER["nobs_baseline"]),
    chk_exact("n_countries",   n_countries, PAPER["n_countries"]),
    chk_exact("n_explosive",   n_exp,       PAPER["n_explosive"]),
    chk_exact("n_stationary",  n_sta,       PAPER["n_stationary"]),
    chk_exact("n_unit_root",   n_ur,        PAPER["n_unit_root"]),
]
results_all.append(chk("pct_explosive", n_exp / nobs,
                        PAPER["pct_explosive"], 0.001))


# ===========================================================================
# SECTION 2 — Baseline MNL (cluster-robust SEs)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 2 — Baseline MNL fit stats (Table 6)")
print("="*70)

y_codes     = df_base[y_var].cat.codes
X_const     = sm.add_constant(df_base[x_vars].astype(float), has_constant="add")

model_base  = MNLogit(y_codes, X_const)
res_base    = model_base.fit(method="newton", maxiter=300, disp=False,
                             cov_type="cluster",
                             cov_kwds={"groups": df_base[cluster_var]})

llf    = float(res_base.llf)
llnull = float(res_base.llnull)
mcf    = 1 - llf / llnull
bic    = float(res_base.bic)
bic_po = bic / nobs

results_all += [
    chk("McFadden_R2", mcf,    PAPER["mcfadden_r2"],  TOL_FIT),
    chk("BIC_per_obs", bic_po, PAPER["bic_per_obs"],  TOL_FIT),
]

# Map params columns to outcome labels
categories   = list(df_base[y_var].cat.categories)   # [Explosive, Stationary, Unit root]
nonbase      = categories[1:]                          # [Stationary, Unit root]
param_cols   = list(res_base.params.columns)           # [0, 1] typically
col_to_label = {int(c): nonbase[i] for i, c in enumerate(sorted(param_cols))}

print(f"\n  Converged: {getattr(res_base, 'mle_retvals', {}).get('converged', '?')}")
print(f"  params.columns: {param_cols}  mapped: {col_to_label}")


# ===========================================================================
# SECTION 3 — Coefficient comparison (Table 4)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 3 — Baseline coefficients (Table 4, cluster-robust SEs)")
print("="*70)

P = res_base.params
B = res_base.bse

# Identify column for Stationary and Unit root
col_S = [c for c, lab in col_to_label.items() if lab == "Stationary"][0]
col_U = [c for c, lab in col_to_label.items() if lab == "Unit root"][0]

term_checks = [
    ("const",         "const",      "S", PAPER["coef_const_S"],       PAPER["se_const_S"]),
    ("const",         "const",      "U", PAPER["coef_const_U"],       PAPER["se_const_U"]),
    ("fixed_er",      "fixed_er",   "S", PAPER["coef_fixed_er_S"],    PAPER["se_fixed_er_S"]),
    ("fixed_er",      "fixed_er",   "U", PAPER["coef_fixed_er_U"],    PAPER["se_fixed_er_U"]),
    ("current_def",   "current_def","S", PAPER["coef_current_def_S"], PAPER["se_current_def_S"]),
    ("current_def",   "current_def","U", PAPER["coef_current_def_U"], PAPER["se_current_def_U"]),
    ("comm_ex",       "comm_ex",    "S", PAPER["coef_comm_ex_S"],     PAPER["se_comm_ex_S"]),
    ("comm_ex",       "comm_ex",    "U", PAPER["coef_comm_ex_U"],     PAPER["se_comm_ex_U"]),
    ("manu_ex",       "manu_ex",    "S", PAPER["coef_manu_ex_S"],     PAPER["se_manu_ex_S"]),
    ("manu_ex",       "manu_ex",    "U", PAPER["coef_manu_ex_U"],     PAPER["se_manu_ex_U"]),
    ("opn_l1",        "opn_l1",     "S", PAPER["coef_opn_l1_S"],      PAPER["se_opn_l1_S"]),
    ("opn_l1",        "opn_l1",     "U", PAPER["coef_opn_l1_U"],      PAPER["se_opn_l1_U"]),
    ("gsur_3_yr_l1",  "gsur_3_yr_l1","S",PAPER["coef_gsur_S"],        PAPER["se_gsur_S"]),
    ("gsur_3_yr_l1",  "gsur_3_yr_l1","U",PAPER["coef_gsur_U"],        PAPER["se_gsur_U"]),
]

for row_name, var, eq_code, exp_coef, exp_se in term_checks:
    col = col_S if eq_code == "S" else col_U
    eq  = "Stationary" if eq_code == "S" else "Unit root"
    comp_coef = float(P.loc[var, col])
    comp_se   = float(B.loc[var, col])
    results_all += [
        chk(f"coef_{row_name}_{eq_code}", comp_coef, exp_coef, TOL_COEF),
        chk(f"se_{row_name}_{eq_code}",   comp_se,   exp_se,   TOL_COEF),
    ]


# ===========================================================================
# SECTION 4 — Average Marginal Effects (Table 5)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 4 — Average Marginal Effects (Table 5)")
print("="*70)

mfx = res_base.get_margeff(at="overall")

# margeff shape: (k_vars, J) where J = 3 outcomes
# statsmodels at="overall" returns all 3 outcomes
mfx_arr = mfx.margeff        # shape (k, 3) — rows = regressors, cols = outcomes
mfx_se  = mfx.margeff_se

# Row indices correspond to x_vars (no const in mfx)
# Column indices correspond to regime_categories
print(f"  mfx.margeff shape: {mfx_arr.shape}")

# Find row index for fixed_er and opn_l1
x_cols_no_const = [c for c in X_const.columns if c != "const"]
idx_er  = x_cols_no_const.index("fixed_er")
idx_opn = x_cols_no_const.index("opn_l1")
# Explosive is category index 0
idx_exp = 0

ame_er_exp  = float(mfx_arr[idx_er,  idx_exp])
ame_opn_exp = float(mfx_arr[idx_opn, idx_exp])

results_all += [
    chk("AME_fixed_er_explosive",  ame_er_exp,  PAPER["ame_fixed_er_explosive"],  TOL_AME),
    chk("AME_opn_l1_explosive",    ame_opn_exp, PAPER["ame_opn_l1_explosive"],    TOL_AME),
]

# Report full AME table for the record
print("\n  Full AME table (dy/dx):")
ame_df = pd.DataFrame(mfx_arr, index=x_cols_no_const,
                      columns=regime_categories)
print(ame_df.to_string())


# ===========================================================================
# SECTION 5 — Binary logit robustness (Table 7)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 5 — Binary logit robustness (Table 7)")
print("="*70)

df_bin = df_base[df_base[y_var] != "Explosive"].copy()
n_bin  = len(df_bin)
y_bin  = (df_bin[y_var] == "Unit root").astype(int)
X_bin  = sm.add_constant(df_bin[x_vars].astype(float), has_constant="add")

res_logit = Logit(y_bin, X_bin).fit(
    method="newton", maxiter=300, disp=False,
    cov_type="cluster", cov_kwds={"groups": df_bin[cluster_var]})

print(f"  Binary sample: {n_bin} obs, "
      f"{df_bin[cluster_var].nunique()} countries")
print(f"  Converged: {getattr(res_logit, 'mle_retvals', {}).get('converged', '?')}")

any_sig = any(res_logit.pvalues[x_vars] < 0.10)
print("\n  p-values for each regressor:")
for v in x_vars:
    pv = float(res_logit.pvalues[v])
    print(f"    {v:20s}  p = {pv:.4f}  {star_from_p(pv)}")

result_bin = {"check": "binary_logit_any_sig",
              "status": "PASS" if (any_sig == PAPER["binary_logit_any_sig"]) else "FAIL",
              "computed": any_sig, "expected": PAPER["binary_logit_any_sig"], "diff": 0}
print(f"\n  [{result_bin['status']}] any_sig (p<0.10): {any_sig}  expected: {PAPER['binary_logit_any_sig']}")
results_all.append(result_bin)


# ===========================================================================
# SECTION 6 — Income subgroups (Table 8)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 6 — Income subgroups (Table 8)")
print("="*70)

def fit_subgroup_mnl(df_sub, name):
    needed = [cluster_var, y_var] + x_vars
    d = df_sub[needed].dropna(subset=[cluster_var, y_var] + x_vars).copy()
    d[y_var] = pd.Categorical(d[y_var], categories=regime_categories, ordered=False)
    vc_sub = d[y_var].value_counts()
    n_exp_sub = int(vc_sub.get("Explosive", 0))

    nobs_sub  = len(d)
    n_ctry    = d[cluster_var].nunique()

    if n_exp_sub < 10:
        print(f"  {name}: SKIPPING — only {n_exp_sub} explosive obs (< 10)")
        return None, None, nobs_sub, n_ctry, n_exp_sub

    y_c = d[y_var].cat.codes
    X   = sm.add_constant(d[x_vars].astype(float), has_constant="add")
    mdl = MNLogit(y_c, X)
    try:
        res = mdl.fit(method="newton", maxiter=300, disp=False,
                      cov_type="cluster", cov_kwds={"groups": d[cluster_var]})
    except Exception as e:
        print(f"  {name}: FAILED — {e}")
        return None, None, nobs_sub, n_ctry, n_exp_sub

    conv = getattr(res, "mle_retvals", {}).get("converged", "?")
    mcf_sub = 1 - res.llf / res.llnull
    bic_sub = res.bic / nobs_sub
    print(f"  {name}: nobs={nobs_sub}, countries={n_ctry}, explosive={n_exp_sub}, "
          f"McF R2={mcf_sub:.4f}, BIC/obs={bic_sub:.4f}, converged={conv}")
    return res, None, nobs_sub, n_ctry, n_exp_sub

# Subgroup masks (applied to df_raw which has all rows including lag NaN)
masks = {
    "Advanced":   df_raw["idc"] == 1,
    "Emerging":   df_raw["emg"] == 1,
    "Low income": (df_raw["ldc"] == 1) & (df_raw["emg"] == 0),
}

sub_results = {}
for name, mask in masks.items():
    print(f"\n  --- {name} ---")
    res_sub, _, nobs_sub, n_ctry_sub, n_exp_sub = fit_subgroup_mnl(
        df_raw[mask].copy(), name)
    sub_results[name] = (res_sub, nobs_sub, n_ctry_sub, n_exp_sub)

# Check Emerging market numbers
res_em, nobs_em, nctry_em, nexp_em = sub_results["Emerging"]
results_all += [
    chk_exact("emerging_nobs",         nobs_em,   PAPER["emerging_nobs"]),
    chk_exact("emerging_countries",    nctry_em,  PAPER["emerging_countries"]),
    chk_exact("emerging_n_explosive",  nexp_em,   PAPER["emerging_n_explosive"]),
]
if res_em is not None:
    mcf_em  = 1 - res_em.llf / res_em.llnull
    bic_em  = res_em.bic / nobs_em
    results_all += [
        chk("emerging_mcfadden",     mcf_em,  PAPER["emerging_mcfadden"],    TOL_FIT),
        chk("emerging_bic_per_obs",  bic_em,  PAPER["emerging_bic_per_obs"], TOL_FIT),
    ]

# Check Advanced and Low income counts only (models unreliable with few explosive)
_, nobs_adv, nctry_adv, nexp_adv = sub_results["Advanced"]
results_all += [
    chk_exact("advanced_nobs",         nobs_adv,  PAPER["advanced_nobs"]),
    chk_exact("advanced_countries",    nctry_adv, PAPER["advanced_countries"]),
    chk_exact("advanced_n_explosive",  nexp_adv,  PAPER["advanced_n_explosive"]),
]

_, nobs_li, nctry_li, nexp_li = sub_results["Low income"]
results_all += [
    chk_exact("low_income_nobs",         nobs_li,  PAPER["low_income_nobs"]),
    chk_exact("low_income_countries",    nctry_li, PAPER["low_income_countries"]),
    chk_exact("low_income_n_explosive",  nexp_li,  PAPER["low_income_n_explosive"]),
]


# ===========================================================================
# SECTION 7 — Time-period subgroups (Table 9)
# ===========================================================================
print("\n" + "="*70)
print("SECTION 7 — Time-period subgroups (Table 9)")
print("="*70)

time_masks = {
    "Pre-GFC":  yr_int < 2008,
    "Post-GFC": yr_int >= 2008,
}

for name, mask in time_masks.items():
    print(f"\n  --- {name} ---")
    res_t, _, nobs_t, nctry_t, nexp_t = fit_subgroup_mnl(
        df_raw[mask].copy(), name)
    if res_t is not None:
        mcf_t = 1 - res_t.llf / res_t.llnull
        bic_t = res_t.bic / nobs_t
        key_mcf = "pregfc_mcfadden"   if "Pre" in name else "postgfc_mcfadden"
        key_bic = "pregfc_bic_per_obs" if "Pre" in name else "postgfc_bic_per_obs"
        results_all += [
            chk(f"{name}_McFadden", mcf_t, PAPER[key_mcf], TOL_FIT),
            chk(f"{name}_BIC_per_obs", bic_t, PAPER[key_bic], TOL_FIT),
        ]


# ===========================================================================
# SUMMARY
# ===========================================================================
print("\n" + "="*70)
print("REPLICATION AUDIT SUMMARY")
print("="*70)

results_df = pd.DataFrame(results_all)
n_pass = (results_df["status"] == "PASS").sum()
n_fail = (results_df["status"] == "FAIL").sum()
n_tot  = len(results_df)

print(f"\n  Total checks: {n_tot}")
print(f"  PASS:  {n_pass}  ({100*n_pass/n_tot:.0f}%)")
print(f"  FAIL:  {n_fail}")

if n_fail > 0:
    print("\n  FAILING CHECKS:")
    for _, row in results_df[results_df["status"] == "FAIL"].iterrows():
        print(f"    {row['check']:45s}  "
              f"computed={row['computed']:.6g}  "
              f"expected={row['expected']:.6g}  "
              f"diff={row['diff']:.6g}")

# Save to Excel
results_df.to_excel(AUDIT_OUT, index=False)
print(f"\n  Detailed results saved to: {AUDIT_OUT}")
