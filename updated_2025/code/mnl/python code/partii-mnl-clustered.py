import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.discrete.discrete_model import MNLogit


# =============================================================================
# Settings
# =============================================================================
fname_regimes = "clean-data/mnl_reg_data.xlsx"

# After standardizing column names (spaces -> underscores),
# "Regime Type" becomes "Regime_Type"
y_var = "Regime_Type"

# Baseline specification (Model C00058, memo 2.6.2026):
# fixed exchange rate, current deficit, exporter composition,
# lagged trade openness, lagged 3-yr fiscal balance.
x_vars = [
    "fixed_er",
    "current_def",
    "comm_ex",
    "manu_ex",
    "opn_l1",
    "gsur_3_yr_l1",
]

cluster_var = "cn"    # cluster on cn
year_var    = "year"  # needed for lag creation

# IMPORTANT: use exact label you want in outputs
regime_categories = ["Explosive", "Stationary", "Unit root"]
baseline_label = "Explosive"

excel_out = "mnlogit_baseline_clustered.xlsx"


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


def add_lags(df: pd.DataFrame, group_col: str, time_col: str, lag_specs: list[str]) -> pd.DataFrame:
    """
    Create lag-1 columns for any variable in lag_specs ending in '_l1'.
    Lags are computed within group_col, sorted by time_col.
    The base column (e.g. 'opn' for 'opn_l1') must already exist in df.
    """
    out = df.sort_values([group_col, time_col]).copy()
    lag_cols = sorted({v for v in lag_specs if v.endswith("_l1")})
    for lag_col in lag_cols:
        base = lag_col[:-3]  # strip '_l1'
        if base not in out.columns:
            raise KeyError(f"To create '{lag_col}', base column '{base}' is missing from data.")
        out[lag_col] = out.groupby(group_col)[base].shift(1)
    return out


def build_col_to_label(df_model: pd.DataFrame, y_var: str, params_columns) -> dict[int, str]:
    """
    Robust mapping from statsmodels MNLogit equation columns -> outcome labels.

    Typical MNLogit behavior:
      - baseline category (code 0) is not estimated
      - res.params has J-1 columns, often labeled 0..J-2
      - those correspond to categories 1..J-1 (non-baseline outcomes)

    This function handles:
      A) params.columns = [0, 1, ..., J-2]   -> map to categories[1], categories[2], ...
      B) params.columns = [1, 2, ..., J-1]   -> map directly to categories[1], categories[2], ...
    """
    categories = list(df_model[y_var].cat.categories)
    J = len(categories)
    cols = [int(c) for c in params_columns]
    cols_sorted = sorted(cols)

    # Case A: columns are 0..J-2 (most common) -> shift by +1
    if cols_sorted == list(range(J - 1)):
        return {c: categories[c + 1] for c in cols}

    # Case B: columns are 1..J-1 -> direct mapping
    if cols_sorted == list(range(1, J)):
        return {c: categories[c] for c in cols}

    raise ValueError(
        "Unexpected MNLogit params column labels.\n"
        f"params.columns: {cols}\n"
        f"categories: {categories}\n"
        "Expected either 0..J-2 (for categories 1..J-1) or 1..J-1."
    )



def build_coef_long(res, x_vars, col_to_label, model_label: str) -> pd.DataFrame:
    """
    Long-form coefficient table:
    term, outcome, coef, se, z, p, stars, model
    """
    params = res.params
    bse = res.bse
    z = params / bse
    pvals = res.pvalues

    rows = []

    # intercepts first
    for col in params.columns:
        out_lab = col_to_label[int(col)]
        pv = float(pvals.loc["const", col])
        rows.append({
            "model": model_label,
            "outcome": out_lab,
            "term": "const",
            "term_label": f"Constant: {out_lab}",
            "coef": float(params.loc["const", col]),
            "se": float(bse.loc["const", col]),
            "z": float(z.loc["const", col]),
            "p": pv,
            "stars": star_from_p(pv),
        })

    # slopes
    for v in x_vars:
        for col in params.columns:
            out_lab = col_to_label[int(col)]
            pv = float(pvals.loc[v, col])
            rows.append({
                "model": model_label,
                "outcome": out_lab,
                "term": v,
                "term_label": f"{v} : {out_lab}",
                "coef": float(params.loc[v, col]),
                "se": float(bse.loc[v, col]),
                "z": float(z.loc[v, col]),
                "p": pv,
                "stars": star_from_p(pv),
            })

    return pd.DataFrame(rows)


def build_odds_ratio_long(res, x_vars, col_to_label, model_label: str) -> pd.DataFrame:
    """
    Long-form odds ratio table:
    term, outcome, OR, CI low/high, model
    (Excludes intercept like GAUSS)
    """
    params = res.params
    bse = res.bse
    rows = []

    for v in x_vars:
        for col in params.columns:
            out_lab = col_to_label[int(col)]
            b = float(params.loc[v, col])
            se = float(bse.loc[v, col])
            rows.append({
                "model": model_label,
                "outcome": out_lab,
                "term": v,
                "term_label": f"{v} : {out_lab}",
                "odds_ratio": float(np.exp(b)),
                "ci_low": float(np.exp(b - 1.96 * se)),
                "ci_high": float(np.exp(b + 1.96 * se)),
            })

    return pd.DataFrame(rows)


def build_margeff_long(res, X_with_const, regime_categories, model_label: str) -> pd.DataFrame:
    """
    Long-form marginal effects:
    var, category, dy_dx, se, z, p, stars, model

    Robust to statsmodels returning marginal effects for J outcomes or only J-1 outcomes.
    """
    # Debug prints (keep while testing; you can remove later)
    print("Categories:", df_model[y_var].cat.categories.tolist())
    print("Value counts:", df_model[y_var].value_counts().to_dict())

    mfx = res.get_margeff(at="overall")
    print("mfx.margeff shape:", mfx.margeff.shape)

    # Align rows robustly to regressor names (some versions omit const)
    k_me = mfx.margeff.shape[0]
    x_cols = list(X_with_const.columns)

    if len(x_cols) == k_me:
        me_names = x_cols
    elif (len(x_cols) - 1 == k_me) and ("const" in x_cols):
        me_names = [c for c in x_cols if c != "const"]
    else:
        raise ValueError(
            "Could not align marginal effects with X columns.\n"
            f"X columns ({len(x_cols)}): {x_cols}\n"
            f"mfx.margeff rows: {k_me}"
        )

    # Align outcome columns robustly (some versions return J, others return J-1)
    n_out = mfx.margeff.shape[1]
    if n_out == len(regime_categories):
        out_labels = regime_categories
    elif n_out == (len(regime_categories) - 1):
        out_labels = regime_categories[1:]  # non-baseline outcomes only
    else:
        raise ValueError(
            "Unexpected number of outcome columns in marginal effects.\n"
            f"mfx.margeff shape: {mfx.margeff.shape}\n"
            f"regime_categories: {regime_categories}"
        )

    dy = pd.DataFrame(mfx.margeff, index=me_names, columns=out_labels)
    se = pd.DataFrame(mfx.margeff_se, index=me_names, columns=out_labels)
    z = dy / se
    p = pd.DataFrame(
        2 * (1 - stats.norm.cdf(np.abs(z.values))),
        index=z.index,
        columns=z.columns
    )

    rows = []
    for v in dy.index:
        for cat in out_labels:
            pv = float(p.loc[v, cat])
            rows.append({
                "model": model_label,
                "var": v,
                "category": cat,
                "dy_dx": float(dy.loc[v, cat]),
                "se": float(se.loc[v, cat]),
                "z": float(z.loc[v, cat]),
                "p": pv,
                "stars": star_from_p(pv),
            })

    return pd.DataFrame(rows)


def build_fit_stats(res, nobs: int, model_label: str) -> pd.DataFrame:
    llf = float(res.llf)
    llnull = float(res.llnull)
    k_params = int(res.params.size)

    # per-observation (to match GAUSS output scale)
    aic_per_obs = float(res.aic) / nobs
    bic_per_obs = float(res.bic) / nobs
    hqic = (-2 * llf) + (2 * k_params * np.log(np.log(nobs)))
    hqic_per_obs = float(hqic) / nobs

    mcfadden = 1 - (llf / llnull) if llnull != 0 else np.nan
    lr_stat = 2 * (llf - llnull)
    lr_df = int(res.df_model)
    lr_p = 1 - stats.chi2.cdf(lr_stat, lr_df)

    return pd.DataFrame([{
        "model": model_label,
        "-2Ln(Lu)": -2 * llf,
        "-2Ln(Lnull)": -2 * llnull,
        "AIC_per_obs": aic_per_obs,
        "BIC_per_obs": bic_per_obs,
        "HQIC_per_obs": hqic_per_obs,
        "McFadden_R2": mcfadden,
        "LR_stat": lr_stat,
        "LR_df": lr_df,
        "LR_p": lr_p,
        "k_params": k_params,
        "nobs": nobs,
        "cov_type": getattr(res, "cov_type", "unknown"),
    }])


def build_confusion_matrix(res, X_with_const, y_codes, regime_categories, model_label: str) -> pd.DataFrame:
    pred_probs = res.predict(X_with_const)
    if pred_probs.shape[1] != len(regime_categories):
        raise RuntimeError(
            f"Expected N x {len(regime_categories)} probabilities, got {pred_probs.shape}."
        )

    pred_class = pred_probs.values.argmax(axis=1)
    obs_class = y_codes.values

    cm = pd.crosstab(
        pd.Series(obs_class, name="Observed"),
        pd.Series(pred_class, name="Predicted"),
        dropna=False
    ).reindex(
        index=list(range(len(regime_categories))),
        columns=list(range(len(regime_categories))),
        fill_value=0
    )

    cm.index = regime_categories
    cm.columns = regime_categories
    cm = cm.reset_index().rename(columns={"index": "Observed"})
    cm.insert(0, "model", model_label)
    return cm


TERM_LABELS = {
    "const":          "Constant",
    "fixed_er":       "Fixed exchange rate",
    "current_def":    "Current deficit",
    "comm_ex":        "Commodity exporter",
    "manu_ex":        "Manufacturing exporter",
    "opn":            "Trade openness",
    "opn_l1":         "Trade openness (t-1)",
    "ka_open":        "Capital account openness",
    "ka_open_l1":     "Capital account openness (t-1)",
    "gsur_3_yr":      "Fiscal balance (3-yr)",
    "gsur_3_yr_l1":   "Fiscal balance (3-yr, t-1)",
    "gsur_def":       "Fiscal balance dummy",
    "gsur_def_l1":    "Fiscal balance dummy (t-1)",
    "ir_r_lmf":       "Real interest rate",
    "ir_r_lmf_l1":    "Real interest rate (t-1)",
    "fd_gap":         "Financial development gap",
}


def build_paper_table(coef_long: pd.DataFrame) -> pd.DataFrame:
    """
    Paper-style 2-column layout:
    Rows = terms (const + x_vars)
    Columns = outcome equations (Stationary, Unit root) with coef+stars and (se)
    """
    # Keep only Stationary + Unit root equations (non-baseline)
    eqs = ["Stationary", "Unit root"]

    base = coef_long.copy()
    base = base[base["outcome"].isin(eqs)].copy()

    term_order = ["const"] + [t for t in base["term"].tolist() if t != "const"]
    term_order = list(dict.fromkeys(term_order))

    coef_piv = base.pivot(index="term", columns="outcome", values="coef")
    se_piv = base.pivot(index="term", columns="outcome", values="se")
    stars_piv = base.pivot(index="term", columns="outcome", values="stars")

    rows = []
    for term in term_order:
        if term not in coef_piv.index:
            continue

        label = TERM_LABELS.get(term, term)
        row_coef = {"term": label}
        for eq in eqs:
            if eq in coef_piv.columns:
                c = coef_piv.loc[term, eq]
                s = stars_piv.loc[term, eq]
                row_coef[eq] = ("" if pd.isna(c) else f"{c:.3f}{s}")
            else:
                row_coef[eq] = ""
        row_coef["row_type"] = "coef"
        rows.append(row_coef)

        row_se = {"term": ""}
        for eq in eqs:
            if eq in se_piv.columns:
                se_val = se_piv.loc[term, eq]
                row_se[eq] = ("" if pd.isna(se_val) else f"({se_val:.3f})")
            else:
                row_se[eq] = ""
        row_se["row_type"] = "se"
        rows.append(row_se)

    out = pd.DataFrame(rows)
    return out[["term", "row_type"] + eqs]


def build_se_comparison(coef_long_std: pd.DataFrame, coef_long_clu: pd.DataFrame) -> pd.DataFrame:
    """
    Compare standard vs cluster SEs for each term/outcome.
    """
    a = coef_long_std.copy()
    b = coef_long_clu.copy()

    keep_cols = ["term", "outcome", "coef", "se", "p"]
    a = a[keep_cols].rename(columns={"coef": "coef_std", "se": "se_std", "p": "p_std"})
    b = b[keep_cols].rename(columns={"coef": "coef_cluster", "se": "se_cluster", "p": "p_cluster"})

    merged = pd.merge(a, b, on=["term", "outcome"], how="outer")
    merged["se_ratio_cluster_to_std"] = merged["se_cluster"] / merged["se_std"]

    merged["term_sort"] = merged["term"].apply(lambda t: (0 if t == "const" else 1, t))
    merged = merged.sort_values(["outcome", "term_sort"]).drop(columns=["term_sort"])
    return merged


# =============================================================================
# Load + standardize column names + clean
# =============================================================================
df = pd.read_excel(fname_regimes)

df.columns = (
    df.columns.astype(str)
      .str.strip()
      .str.replace(r"\s+", "_", regex=True)
)

# Determine base columns needed to construct any lagged x_vars
base_for_lags = sorted({v[:-3] for v in x_vars if v.endswith("_l1")})
x_base_vars   = [v for v in x_vars if not v.endswith("_l1")]

need_cols = sorted(set([cluster_var, year_var, y_var] + x_base_vars + base_for_lags))
missing = [c for c in need_cols if c not in df.columns]
if missing:
    raise KeyError(
        f"Missing columns in Excel after name standardization: {missing}\n"
        f"Available columns: {df.columns.tolist()}"
    )

df_model = df[need_cols].copy()

# Treat '.' and blanks as missing
df_model = df_model.replace({".": np.nan, "": np.nan, " ": np.nan})

# Numeric conversion for all potential X source columns
numeric_src = sorted(set(x_base_vars + base_for_lags))
df_model = ensure_numeric_columns(df_model, numeric_src)

# --- FIX: robust label normalization + mapping to ensure Unit root rows match ---
df_model[y_var] = (
    df_model[y_var].astype(str)
      .str.replace("\u00a0", " ", regex=False)   # NBSP -> space
      .str.strip()
      .str.replace(r"\s+", " ", regex=True)      # collapse spaces
)

# Map common variants to your chosen display labels
df_model[y_var] = df_model[y_var].replace({
    "Explosive": "Explosive",
    "explosive": "Explosive",
    "Stationary": "Stationary",
    "stationary": "Stationary",
    "Unit Root": "Unit root",
    "Unit root": "Unit root",
    "unit root": "Unit root",
    "UNIT ROOT": "Unit root",
})

# Enforce categories (baseline is position 0)
df_model[y_var] = pd.Categorical(df_model[y_var], categories=regime_categories, ordered=False)

# Create any required lag columns (first obs per country becomes NaN automatically)
df_model = add_lags(df_model, group_col=cluster_var, time_col=year_var, lag_specs=x_vars)

# Listwise delete across cluster id + Y + all X (lags drop first obs per country)
df_model = df_model.dropna(subset=[cluster_var, y_var] + x_vars).copy()

nobs = int(df_model.shape[0])
y_codes = df_model[y_var].cat.codes

# X with intercept
X_with_const = sm.add_constant(df_model[x_vars], has_constant="add")


# =============================================================================
# Fit BOTH models: standard SE and cluster-robust SE (cluster on cn)
# =============================================================================
model = MNLogit(y_codes, X_with_const)

res_std = model.fit(method="newton", maxiter=200, disp=False)

res_cluster = model.fit(
    method="newton",
    maxiter=200,
    disp=False,
    cov_type="cluster",
    cov_kwds={"groups": df_model[cluster_var]}
)

print("Fitted both models.")
print("Standard cov_type:", getattr(res_std, "cov_type", "unknown"))
print("Cluster cov_type:", getattr(res_cluster, "cov_type", "unknown"))
print()
print("params.columns:", list(res_cluster.params.columns))
print("mapped labels:", build_col_to_label(df_model, y_var, res_cluster.params.columns))

# =============================================================================
# Build export tables for BOTH models
# =============================================================================
col_to_label_std = build_col_to_label(df_model, y_var, res_std.params.columns)
col_to_label_clu = build_col_to_label(df_model, y_var, res_cluster.params.columns)

coef_long_std = build_coef_long(res_std, x_vars, col_to_label_std, model_label="standard")
coef_long_clu = build_coef_long(res_cluster, x_vars, col_to_label_clu, model_label="cluster_cn")

or_long_std = build_odds_ratio_long(res_std, x_vars, col_to_label_std, model_label="standard")
or_long_clu = build_odds_ratio_long(res_cluster, x_vars, col_to_label_clu, model_label="cluster_cn")

mfx_long_std = build_margeff_long(res_std, X_with_const, regime_categories, model_label="standard")
mfx_long_clu = build_margeff_long(res_cluster, X_with_const, regime_categories, model_label="cluster_cn")

fit_std = build_fit_stats(res_std, nobs=nobs, model_label="standard")
fit_clu = build_fit_stats(res_cluster, nobs=nobs, model_label="cluster_cn")
fit_all = pd.concat([fit_std, fit_clu], ignore_index=True)

cm_std = build_confusion_matrix(res_std, X_with_const, y_codes, regime_categories, model_label="standard")
cm_clu = build_confusion_matrix(res_cluster, X_with_const, y_codes, regime_categories, model_label="cluster_cn")
cm_all = pd.concat([cm_std, cm_clu], ignore_index=True)

desc_df = pd.DataFrame({
    "Mean": df_model[x_vars].mean(),
    "Std Dev": df_model[x_vars].std(ddof=1),
    "Minimum": df_model[x_vars].min(),
    "Maximum": df_model[x_vars].max(),
})

cat_counts = df_model[y_var].value_counts(dropna=False).reindex(regime_categories)
cat_props = df_model[y_var].value_counts(normalize=True, dropna=False).reindex(regime_categories)
cat_df = pd.DataFrame({"count": cat_counts, "proportion": cat_props})

paper_std = build_paper_table(coef_long_std[coef_long_std["model"] == "standard"])
paper_clu = build_paper_table(coef_long_clu[coef_long_clu["model"] == "cluster_cn"])

se_compare = build_se_comparison(coef_long_std, coef_long_clu)


# =============================================================================
# Export to Excel (Option B)
# =============================================================================
with pd.ExcelWriter(excel_out, engine="openpyxl") as writer:
    coef_long_std.to_excel(writer, sheet_name="coef_standard_long", index=False)
    coef_long_clu.to_excel(writer, sheet_name="coef_cluster_long", index=False)

    or_long_std.to_excel(writer, sheet_name="or_standard_long", index=False)
    or_long_clu.to_excel(writer, sheet_name="or_cluster_long", index=False)

    mfx_long_std.to_excel(writer, sheet_name="mfx_standard_long", index=False)
    mfx_long_clu.to_excel(writer, sheet_name="mfx_cluster_long", index=False)

    fit_all.to_excel(writer, sheet_name="fit_stats", index=False)
    cm_all.to_excel(writer, sheet_name="confusion_matrix", index=False)

    desc_df.to_excel(writer, sheet_name="descriptives")
    cat_df.to_excel(writer, sheet_name="category_dist")

    paper_std.to_excel(writer, sheet_name="paper_table_standard", index=False)
    paper_clu.to_excel(writer, sheet_name="paper_table_cluster", index=False)

    se_compare.to_excel(writer, sheet_name="se_compare", index=False)

print(f"Wrote Excel output to: {excel_out}")
