import pandas as pd
import numpy as np

# =============================================================================
# SETTINGS
# =============================================================================
INFILE = r"C:\Users\eclow\Documents\GitHub\cab-persistency\updated_2025\results\results-summary-updated.xlsx"
SHEET = "MSUR results"

OUTFILE = r"C:\Users\eclow\Documents\GitHub\cab-persistency\updated_2025\results\msur_summary_tables.xlsx"

# =============================================================================
# HELPERS
# =============================================================================
def _norm(x) -> str:
    if pd.isna(x):
        return ""
    return (
        str(x)
        .replace("\u00a0", " ")
        .replace("\n", " ")
        .strip()
        .lower()
    )

def standardize_colname(c: str) -> str:
    return (
        str(c)
        .replace("\u00a0", " ")
        .replace("\n", " ")
        .strip()
        .replace("  ", " ")
    )

def to_bool_series(s: pd.Series) -> pd.Series:
    x = s.astype(str).str.strip().str.lower()
    return x.isin(["true", "t", "1", "yes", "y"])

def find_header_row(raw: pd.DataFrame, token: str = "country", max_rows: int = 40) -> int:
    for r in range(min(max_rows, raw.shape[0])):
        row_vals = [_norm(v) for v in raw.iloc[r, :].tolist()]
        if any(v == token for v in row_vals):
            return r
    return -1

def drop_unnamed_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Drop Excel 'Unnamed: x' columns robustly WITHOUT boolean-index alignment issues.
    """
    col_series = pd.Series(df.columns.astype(str))
    keep_mask = ~col_series.str.match(r"^Unnamed", case=False, na=False)
    # Use numpy mask to avoid index alignment problems
    return df.loc[:, keep_mask.to_numpy()].copy()

# =============================================================================
# ROBUST LOAD WITH HEADER DETECTION
# =============================================================================
raw = pd.read_excel(INFILE, sheet_name=SHEET, header=None)

header_row = find_header_row(raw, token="country", max_rows=50)
if header_row < 0:
    raise ValueError(
        "Couldn't locate a header row containing 'Country'. "
        "Open the sheet and identify the row with the true column names, "
        "then set header_row manually."
    )

df = pd.read_excel(INFILE, sheet_name=SHEET, header=header_row)

# Standardize col names, drop unnamed columns, reset index to avoid alignment surprises
df.columns = [standardize_colname(c) for c in df.columns]
df = drop_unnamed_columns(df)
df = df.reset_index(drop=True)

print(f"✅ Loaded '{SHEET}' with detected header_row={header_row}")
print("Detected columns:", df.columns.tolist())

# =============================================================================
# COLUMN NORMALIZATION / REQUIRED FIELDS
# =============================================================================
rename_map = {}
for c in df.columns:
    cl = c.strip().lower()
    if cl == "country":
        rename_map[c] = "Country"
    elif cl == "phi0":
        rename_map[c] = "Phi0"
    elif cl == "phi1":
        rename_map[c] = "Phi1"
    elif cl == "tstat0":
        rename_map[c] = "Tstat0"
    elif cl == "tstat1":
        rename_map[c] = "Tstat1"
    elif cl == "global stationarity":
        rename_map[c] = "Global Stationarity"

df = df.rename(columns=rename_map)

required = ["Country", "Phi0", "Phi1"]
missing_req = [c for c in required if c not in df.columns]
if missing_req:
    raise KeyError(
        f"Missing required columns: {missing_req}\n"
        f"Available columns: {df.columns.tolist()}\n\n"
        "If those variables exist under different names, update the rename_map logic."
    )

# =============================================================================
# TYPE CLEANING
# =============================================================================
ms = df.copy()
ms = ms.reset_index(drop=True)  # ensure clean RangeIndex

ms["Country"] = ms["Country"].astype(str).str.strip()

for col in ["Phi0", "Phi1", "Tstat0", "Tstat1"]:
    if col in ms.columns:
        ms[col] = pd.to_numeric(ms[col], errors="coerce")

# Detect reject columns by substring match
def find_col_contains(substr: str) -> list[str]:
    return [c for c in ms.columns if substr.lower() in c.lower()]

rej_stat_cols = find_col_contains("Reject Null for Alternative Stationary")
rej_expl_cols = find_col_contains("Reject Null for Alternative Explosiveness")

for c in rej_stat_cols + rej_expl_cols:
    ms[c] = to_bool_series(ms[c])

# Normalize overall classification column if it exists
total_category = "Global Stationarity" if "Global Stationarity" in ms.columns else None
if total_category is not None:
    ms[total_category] = ms[total_category].astype(str).str.strip()

# =============================================================================
# SUMMARY TABLES
# =============================================================================
summary_tables = {}

# 1) Classification counts
if total_category is not None:
    classification_counts = (
        ms[total_category]
        .value_counts(dropna=False)
        .rename_axis("category")
        .reset_index(name="countries")
    )
else:
    classification_counts = pd.DataFrame(
        {"note": ["No overall category column detected (e.g., 'Global Stationarity')."]}
    )
summary_tables["classification_counts"] = classification_counts

# 2) Phi summaries
phi_summary = pd.DataFrame({
    "stat": ["count", "mean", "std", "min", "p25", "median", "p75", "max"],
    "Phi0": [
        ms["Phi0"].count(),
        ms["Phi0"].mean(),
        ms["Phi0"].std(ddof=1),
        ms["Phi0"].min(),
        ms["Phi0"].quantile(0.25),
        ms["Phi0"].median(),
        ms["Phi0"].quantile(0.75),
        ms["Phi0"].max(),
    ],
    "Phi1": [
        ms["Phi1"].count(),
        ms["Phi1"].mean(),
        ms["Phi1"].std(ddof=1),
        ms["Phi1"].min(),
        ms["Phi1"].quantile(0.25),
        ms["Phi1"].median(),
        ms["Phi1"].quantile(0.75),
        ms["Phi1"].max(),
    ],
})
summary_tables["phi_summary"] = phi_summary

# 3) Rejection rates (if those columns exist)
rejection_rows = []
for c in rej_stat_cols:
    rejection_rows.append({
        "test": "Reject stationarity alternative",
        "column": c,
        "share_true": float(ms[c].mean()) if ms[c].notna().any() else np.nan,
        "n_nonmissing": int(ms[c].notna().sum())
    })
for c in rej_expl_cols:
    rejection_rows.append({
        "test": "Reject explosiveness alternative",
        "column": c,
        "share_true": float(ms[c].mean()) if ms[c].notna().any() else np.nan,
        "n_nonmissing": int(ms[c].notna().sum())
    })

rejection_rates = pd.DataFrame(rejection_rows)
summary_tables["rejection_rates"] = rejection_rates

# =============================================================================
# EXPORT
# =============================================================================
with pd.ExcelWriter(OUTFILE, engine="openpyxl") as writer:
    ms.to_excel(writer, sheet_name="msur_clean", index=False)
    for name, tab in summary_tables.items():
        tab.to_excel(writer, sheet_name=name[:31], index=False)

print(f"✅ Wrote summary workbook to:\n{OUTFILE}")
