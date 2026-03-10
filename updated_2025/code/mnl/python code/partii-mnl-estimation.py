import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit


# =============================================================================
# Settings (update these)
# =============================================================================
fname_regimes = "clean-data/mnl_reg_data.xlsx"

y_var = "Regime_Type"
x_vars = [
    "fixed_er",        # dummy
    "opn",
    "ka_open",
    "current_def",     # dummy
    "gsur_3_yr",
    "gsur_def",
    "fd_gap",
    "ir_r_lmf",
    "comm_ex",         # dummy
    "manu_ex",         # dummy
]

dummy_vars = {"comm_ex", "manu_ex", "fixed_er", "current_def"}

# Category labels and baseline must match GAUSS:
# y_labels = "Explosive"$|"Stationary"$|"Unit root";
# reference = y_labels[1] => Explosive
regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label = "Explosive"


# =============================================================================
# Helper formatting functions (GAUSS-like)
# =============================================================================
def star_from_p(p: float) -> str:
    if p < 0.001:
        return "***"
    if p < 0.05:
        return "**"
    if p < 0.1:
        return "*"
    return ""


def fmt_p(p: float) -> str:
    # GAUSS prints either scientific or decimals depending on size
    if p < 1e-4:
        return f"{p:.3g}"
    return f"{p:.6f}".rstrip("0").rstrip(".")


def fmt_num(x: float, nd: int = 3) -> str:
    return f"{x:.{nd}f}"


def ensure_numeric_columns(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    """
    Convert X columns to numeric where possible. This is important when Excel
    may have numbers stored as strings.
    """
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
    return out


# =============================================================================
# Load + clean data (GAUSS packr behavior)
# =============================================================================
df = pd.read_excel(fname_regimes)

# Normalize column names: strip whitespace and replace spaces with underscores
df.columns = (
    df.columns
      .astype(str)
      .str.strip()
      .str.replace(r"\s+", "_", regex=True)
)

print(df.columns.tolist())  # sanity check

# Keep only variables used
df_model = df[[y_var] + x_vars].copy()

# Treat "." as missing (as GAUSS would) + common blank cases
df_model = df_model.replace({".": np.nan, "": np.nan, " ": np.nan})

# Make X numeric (dummies, continuous vars)
df_model = ensure_numeric_columns(df_model, x_vars)

# Enforce Y categories and ordering (baseline = Explosive)
df_model[y_var] = pd.Categorical(df_model[y_var], categories=regime_categories, ordered=False)

# Listwise deletion across Y and X (packr-like)
df_model = df_model.dropna(axis=0, how="any").copy()

# Build y codes: Explosive=0, Stationary=1, Unit root=2
y_codes = df_model[y_var].cat.codes
if (y_codes < 0).any():
    raise ValueError(f"Found regime labels not in {regime_categories} after cleaning.")

nobs = int(df_model.shape[0])

# =============================================================================
# 1) Show the first few rows to confirm everything looks right
print("\nHead of df_model:")
print(df_model.head())

# 2) Confirm no missing values remain
print("\nMissing values per column (should all be 0):")
print(df_model.isna().sum())

# 3) Regime category counts / proportions (should match GAUSS proportions)
print("\nRegime Type distribution (counts):")
print(df_model[y_var].value_counts(dropna=False))

print("\nRegime Type distribution (proportions):")
print(df_model[y_var].value_counts(normalize=True, dropna=False))

# =============================================================================
# Descriptive output: category distribution + descriptive stats
# =============================================================================
print("-------------------------------------")
print("Multinomial Logit Results")
print(pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"))
print()
print(f"Number of Observations:   {nobs}")

# We'll compute DF after fitting (depends on intercept/no-intercept)
print()

# Category listing (match GAUSS)
for i, lab in enumerate(regime_categories, start=1):
    print(f"  {i} - {lab}")
print()

# Distribution among categories
props = df_model[y_var].value_counts(normalize=True).reindex(regime_categories)
print("\nDistribution Among Outcome Categories For Regime Type\n")
print(f"{'Dependent Variable':<22} {'Proportion':>10}")
for lab, pr in props.items():
    print(f"{lab:<22} {pr:>10.4f}")
print()

# Descriptive stats for X
desc = pd.DataFrame({
    "Mean": df_model[x_vars].mean(),
    "Std Dev": df_model[x_vars].std(ddof=1),
    "Minimum": df_model[x_vars].min(),
    "Maximum": df_model[x_vars].max()
})
print("\nDescriptive Statistics (N={}):\n".format(nobs))
print(f"{'Independent Vars.':<18} {'Mean':>12} {'Std Dev':>16} {'Minimum':>16} {'Maximum':>16}")
for v in x_vars:
    print(f"{v:<18} {desc.loc[v,'Mean']:>12.4f} {desc.loc[v,'Std Dev']:>16.4f} "
          f"{desc.loc[v,'Minimum']:>16.4f} {desc.loc[v,'Maximum']:>16.4f}")
    
# =============================================================================
# Fit models
# =============================================================================

# ---- WITH intercept (matches your GAUSS output) ----
X_with_const = sm.add_constant(df_model[x_vars], has_constant="add")

model_const = MNLogit(y_codes, X_with_const)
res_const = model_const.fit(method="newton", maxiter=200, disp=False)

df_model_const = int(res_const.df_model)  # number of estimated parameters overall
df_resid_const = int(res_const.df_resid)

# ---- NO intercept (GAUSS default, but not what your printed output shows) ----
X_no_const = df_model[x_vars]
model_no_const = MNLogit(y_codes, X_no_const)
res_no_const = model_no_const.fit(method="newton", maxiter=200, disp=False)

# Now we can print DF in GAUSS-like way (for the intercept model since that's what you showed)
print(f"\nDegrees of Freedom:       {df_resid_const}\n")
# =============================================================================
# =============================================================================
# GAUSS-like coefficient table (WITH intercept)
# =============================================================================
print("\n\n                           COEFFICIENTS\n")
print("Coefficient Estimates")
print("-" * 140)
print(f"{'Variables':<28} {'Coefficient':>12} {'se':>14} {'tstat':>14} {'pval':>16}")

params = res_const.params   # DataFrame: rows=regressors, cols=categories (1..J-1)
bse = res_const.bse
z = params / bse
pvals = res_const.pvalues

# Robust mapping from MNLogit columns to regime labels
categories = list(df_model[y_var].cat.categories)
col_to_label = {int(col): categories[int(col)] for col in params.columns}

# Print intercepts first in GAUSS style
for col in params.columns:
    lab = col_to_label[int(col)]
    coef = params.loc["const", col]
    se = bse.loc["const", col]
    tstat = z.loc["const", col]
    pv = pvals.loc["const", col]
    stars = star_from_p(pv)
    print(f"{('Constant: ' + lab):<28} {coef:>12.3f}{stars:<3} {se:>14.3f} {tstat:>14.2f} {pv:>16.3g}")

# Then each variable, for each outcome equation
for v in x_vars:
    for col in params.columns:
        lab = col_to_label[int(col)]
        coef = params.loc[v, col]
        se = bse.loc[v, col]
        tstat = z.loc[v, col]
        pv = pvals.loc[v, col]
        stars = star_from_p(pv)
        print(f"{(v + ' : ' + lab):<28} {coef:>12.3f}{stars:<3} {se:>14.3f} {tstat:>14.2f} {pv:>16.3g}")

print("-" * 140)
print("*p-val<0.1 **p-val<0.05 ***p-val<0.001\n")

# =============================================================================
# Odds ratios with 95% CI (exclude intercept, like GAUSS)
# =============================================================================
print("\n\n                           ODDS RATIO\n")
print("Odds Ratio")
print("-" * 112)
print(f"{'Variables':<28} {'Odds Ratio':>12} {'95% Lower Bound':>18} {'95% Upper Bound':>18}")

for v in x_vars:
    for col in params.columns:
        lab = col_to_label[int(col)]

        b = params.loc[v, col]
        se = bse.loc[v, col]

        or_ = np.exp(b)
        lo = np.exp(b - 1.96 * se)
        hi = np.exp(b + 1.96 * se)

        print(f"{(v + ' : ' + lab):<28} {or_:>12.5g} {lo:>18.5g} {hi:>18.5g}")

print("-" * 112)
print()

# =============================================================================
# Marginal effects: "Average partial probability w.r.t x"
# GAUSS prints marginal effects for EACH category, one table per category.
# Statsmodels get_margeff() gives AME by default with standard errors.
# =============================================================================
mfx = res_const.get_margeff(at="overall")  # average marginal effects
mfx_summary = mfx.summary_frame()  # index = variables, columns include dy/dx for each outcome

# =============================================================================
# Marginal effects: "Average partial probability w.r.t x"
# =============================================================================
mfx = res_const.get_margeff(at="overall")  # average marginal effects

# ---- Robust alignment of marginal effects rows to regressor names ----
k_me = mfx.margeff.shape[0]          # number of regressors in marginal effects arrays
x_cols = list(X_with_const.columns)  # must match what you used to fit res_const

if len(x_cols) == k_me:
    me_names = x_cols
elif (len(x_cols) - 1 == k_me) and ("const" in x_cols):
    # Many statsmodels versions exclude the intercept from marginal effects arrays
    me_names = [c for c in x_cols if c != "const"]
else:
    raise ValueError(
        "Cannot align marginal effects with regressors.\n"
        f"X has {len(x_cols)} columns: {x_cols}\n"
        f"mfx.margeff has {k_me} rows."
    )

# Build DataFrames using the aligned names
margeff = pd.DataFrame(mfx.margeff, index=me_names, columns=regime_categories)
margeff_se = pd.DataFrame(mfx.margeff_se, index=me_names, columns=regime_categories)

# z-stats and p-values (normal approximation)
margeff_z = margeff / margeff_se

# Ensure p-values stay as a DataFrame (not a numpy array)
margeff_p = pd.DataFrame(
    2 * (1 - stats.norm.cdf(np.abs(margeff_z.values))),
    index=margeff_z.index,
    columns=margeff_z.columns
)

print("\n\n                           MARGINAL EFFECTS")
print("           Average partial probability with respect to x")

for cat in regime_categories:
    print(f"\nMarginal Effects for X Variables in {cat} category")
    print("-" * 75)
    print(f"{'Variables':<14} {'Coefficient':>12} {'se':>14} {'tstat':>14} {'pval':>14}")

    for v in me_names:   # IMPORTANT: iterate over me_names (aligned to mfx arrays)
        dy = float(margeff.loc[v, cat])
        se = float(margeff_se.loc[v, cat])
        zt = float(margeff_z.loc[v, cat])
        pv = float(margeff_p.loc[v, cat])
        stars = star_from_p(pv)

        print(f"{v:<14} {dy:>12.4f}{stars:<3} ({se:>8.4f}) {zt:>14.2f} {fmt_p(pv):>14}")

    print("-" * 75)
    print("Estimate se in parentheses.")
    print("*p-val<0.1 **p-val<0.05 ***p-val<0.001")

    # =============================================================================
# Fit statistics section (match GAUSS concepts as closely as possible)
# =============================================================================
print("\n\n********************SUMMARY STATISTICS********************\n")
print("MEASURES OF FIT:\n")

llf = res_const.llf
llnull = res_const.llnull

# GAUSS shows: -2 Ln(Lu): (unrestricted model) = -2*llf
# and -2 Ln(Lr): all coeffs equal zero = -2*llnull (null / intercept-only)
print(f"  -2 Ln(Lu):{'':34} {(-2*llf):>10.4f}")
print(f"  -2 Ln(Lr): All coeffs equal zero{'':12} {(-2*llnull):>10.4f}")

# AIC/BIC
print(f"  Akaike Information Criterion:{'':16} {res_const.aic/nobs:>10.4f}")
print(f"  Bayesian Information Criterion:{'':14} {res_const.bic/nobs:>10.4f}")


# HQIC (not available on some statsmodels MNLogit results; compute manually)
k_params = int(res_const.params.size)
hqic = (-2 * llf) + (2 * k_params * np.log(np.log(nobs)))
print(f"  Hannan-Quinn Information Criterion:{'':10} {hqic/nobs:>10.4f}")

# McFadden pseudo R^2
mcfadden = 1 - (llf / llnull) if llnull != 0 else np.nan
print(f"  McFadden's pseudo R-square:{'':18} {mcfadden:>10.4f}")

# LR test vs null
lr_stat = 2 * (llf - llnull)
lr_df = int(res_const.df_model)
lr_p = 1 - stats.chi2.cdf(lr_stat, lr_df)
print(f"  LR Chi-Square (coeffs equal zero):{'':10} {lr_stat:>10.4f}")
print(f"       d.f.{'' :33} {lr_df:>10.4f}")
print(f"       p-value ={'':25} {lr_p:>10.4f}")

# NOTE:
# GAUSS prints additional pseudo-R2 measures (Madalla, Cragg-Uhler, Ben-Akiva & Lerman adjusted),
# plus LR test for "J-1 intercepts".
# Statsmodels does not compute those directly. If you *need* them, I can add exact formulas,
# but they require clarifying which definitions GAUSS uses in dc library.
print("\n  Note: Additional pseudo-R² measures shown in GAUSS (Madalla, Cragg-Uhler, Ben-Akiva & Lerman)")
print("        are not reported by statsmodels by default. They can be computed if you want exact matching.")


# =============================================================================
# Observed vs predicted outcomes (confusion matrix like GAUSS)
# =============================================================================
pred_probs = res_const.predict(X_with_const)  # N x 2? Actually returns probs for non-baseline? Statsmodels returns full J?
# Ensure we have full probabilities for all 3 classes.
# MNLogit predict typically returns N x J probabilities.
if pred_probs.shape[1] != 3:
    raise RuntimeError("Unexpected predicted probability shape. Expected N x 3 probabilities.")

pred_class = pred_probs.values.argmax(axis=1)
obs_class = y_codes.values

labels = regime_categories
cm = pd.crosstab(
    pd.Series(obs_class, name="Observed"),
    pd.Series(pred_class, name="Predicted"),
    rownames=["Observed"],
    colnames=["Predicted"],
    dropna=False
).reindex(index=[0,1,2], columns=[0,1,2], fill_value=0)

cm.index = labels
cm.columns = labels

print("\n\nOBSERVED AND PREDICTED OUTCOMES\n")
print("           |            Predicted")
print(f"  Observed |{labels[0][:7]:>7} {labels[1][:7]:>8} {labels[2][:7]:>8}    Total")
print("  " + "-"*58)

for rlab in labels:
    row = cm.loc[rlab]
    tot = int(row.sum())
    print(f"  {rlab[:7]:<7} |{int(row[labels[0]]):>7} {int(row[labels[1]]):>8} {int(row[labels[2]]):>8} {tot:>8}")

print("\n  " + "-"*58)
col_tot = cm.sum(axis=0)
grand_tot = int(col_tot.sum())
print(f"     Total |{int(col_tot[labels[0]]):>7} {int(col_tot[labels[1]]):>8} {int(col_tot[labels[2]]):>8} {grand_tot:>8}")
print()

# Count R^2 (Percent Correctly Predicted)
pct_correct = (pred_class == obs_class).mean()
print(f"Count R2, Percent Correctly Predicted:{'':6} {pct_correct*nobs:>10.4f}")
print(f"Percent Correctly Predicted:{'':18} {pct_correct:>10.4f}")