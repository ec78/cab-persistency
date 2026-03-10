import pandas as pd

xlsx_path = "mnlogit_aggressive_search.xlsx"

# Load ranked candidates
df = pd.read_excel(xlsx_path, sheet_name="ranked_candidates")

print("\nAvailable columns:")
print(df.columns.tolist())

print("\nYear FE value counts:")
print(df["year_fe"].value_counts(dropna=False))

# ---- Best year FE spec ----
best_yearfe = (
    df[df["year_fe"] == True]
    .sort_values("score")
    .head(1)
)

print("\nBest year FE spec:")
print(best_yearfe[[
    "spec_id", "nobs", "countries",
    "year_fe", "cv_logloss", "bic_per_obs", "score"
]])

# ---- Identify how variables are recorded ----
possible_var_cols = [
    c for c in df.columns
    if any(k in c.lower() for k in ["var", "rhs", "feature", "regressor", "spec"])
]

print("\nPossible variable-list columns:")
print(possible_var_cols)

# ---- Best fd_gap spec (adjust column name once known) ----
if "fd_gap" in df.columns:
    best_fd = (
        df[df["fd_gap"] == True]
        .sort_values("score")
        .head(1)
    )
    print("\nBest fd_gap spec:")
    print(best_fd[[
        "spec_id", "nobs", "countries",
        "year_fe", "cv_logloss", "bic_per_obs", "score"
    ]])
else:
    print("\nfd_gap not found as boolean column.")
    print("Inspect variable-list column manually from above.")
