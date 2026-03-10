# Replication Archive — CAB Persistency (MNL Section)

This archive replicates Tables 4–9 of the paper using multinomial logit (MNL)
and binary logit models estimated in Python.

---

## Contents

```
replication/
├── README.md               This file
├── requirements.txt        Python package dependencies
├── run_all.py              Single entry point — runs all four scripts in order
├── data/
│   └── mnl_reg_data.xlsx   Analysis-ready country-year panel (~74 countries, 1985–2023)
├── code/
│   ├── 01_baseline_mnl.py          Tables 4, 5, 6  — Baseline MNLogit
│   ├── 02_binary_logit.py          Table 7         — Binary logit robustness
│   ├── 03_subgroups.py             Tables 8, 9     — Income & time-period subgroups
│   └── 04_lagged_er_robustness.py  Table 6 (CV) + Table 4a — Lagged ER robustness
└── output/                 Created automatically; populated by running the scripts
```

---

## Requirements

- Python 3.10 or later
- Package versions listed in `requirements.txt`

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## Running the replication

**Option A — run all scripts at once (recommended):**

```bash
cd replication
python run_all.py
```

**Option B — run individual scripts:**

```bash
cd replication
python code/01_baseline_mnl.py
python code/02_binary_logit.py
python code/03_subgroups.py
python code/04_lagged_er_robustness.py
```

All scripts use paths relative to their own location, so they can be run
from any working directory.

---

## Expected output

After running, the `output/` directory will contain:

| File | Contents |
|---|---|
| `01_baseline_mnl.xlsx` | Coefficients (Table 4), AMEs (Table 5), fit stats (Table 6) |
| `02_binary_logit.xlsx` | Binary logit results (Table 7) |
| `03_subgroups.xlsx` | Income and time-period subgroup results (Tables 8, 9) |
| `04_lagged_er_robustness.xlsx` | Lagged ER comparison, CV log-loss, confusion matrix |

Expected runtime: 2–5 minutes on a standard laptop.

---

## Data description

`data/mnl_reg_data.xlsx` is an unbalanced annual country-year panel covering
approximately 74 countries from 1985 to 2023.

Key variables:

| Variable | Description |
|---|---|
| `cn` | Country code (cluster identifier) |
| `year` | Year (stored as date string, e.g. `1985-01-01`) |
| `Regime_Type` | CAB regime: `Explosive`, `Stationary`, or `Unit root` |
| `fixed_er` | Fixed exchange rate dummy |
| `current_def` | Current account deficit dummy |
| `comm_ex` | Commodity exporter dummy |
| `manu_ex` | Manufacturing exporter dummy |
| `opn` | Trade openness (% GDP); lagged one period as `opn_l1` |
| `gsur_3_yr` | Fiscal balance, 3-year moving average; lagged as `gsur_3_yr_l1` |
| `idc` | Advanced (industrial developed) country indicator |
| `emg` | Emerging market indicator |
| `ldc` | Less-developed country indicator |

Lags are computed within country groups using `groupby('cn').shift(1)` on the
full dataset before any subsetting. This ensures that time-period subgroups
(Pre/Post-GFC) carry correct lagged values for the first observation in each
sub-period.

---

## Model specification (baseline C00058)

- **Outcome:** `Regime_Type` (three categories)
- **Reference category:** Explosive
- **Regressors:** `fixed_er`, `current_def`, `comm_ex`, `manu_ex`, `opn_l1`, `gsur_3_yr_l1`
- **Standard errors:** Cluster-robust, clustered at the country level (`cn`)
- **Estimator:** `statsmodels.discrete.discrete_model.MNLogit`, Newton method

---

## Replication notes

- **Pre-GFC BIC/obs:** The paper reports 1.692 in Table 9; the correct computed
  value is 1.691 (a transcription rounding error in the paper). All other
  statistics in Tables 4–9 replicate exactly to within rounding tolerance.

- **Subgroup identification:** The Low income subgroup has only 3 explosive
  observations and is skipped (model not identified). The Advanced subgroup has
  15 explosive observations; the model runs but McFadden R² is unreliable and
  is marked 'n/a' in the paper.

- **Cross-validation:** Country-grouped 5-fold CV is used (countries, not
  individual observations, are assigned to folds) to prevent data leakage
  across country time series. Random seed = 42 for reproducibility.
