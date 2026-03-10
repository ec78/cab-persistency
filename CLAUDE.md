# CLAUDE.md — cab-persistency

## Project Overview
This project investigates the economic determinants of current account balance (CAB) dynamics across countries, measured as a percentage of GDP. Unit root and Markov-switching methods are used as diagnostic tools to characterize CAB dynamics — not to assess sustainability. The central research question is: what structural factors determine whether a country's CAB exhibits explosive, unit root, or stationary behavior? The project is in active write-up and is intended for journal submission.

## Repository Structure
All active work is in `updated_2025/`. This is the only directory that should be used or referenced. The root-level `code/`, `data/`, and `results/` folders contain older versions and are superseded. Do not read, run, or modify anything outside of `updated_2025/`.

- `updated_2025/data/` — raw and intermediate data files
- `updated_2025/clean-data/` — analysis-ready datasets
- `updated_2025/code/data-prep/` — GAUSS data preparation scripts
- `updated_2025/code/markov-switching/` — GAUSS Markov-switching estimation
- `updated_2025/code/unit-root/` — GAUSS unit root testing
- `updated_2025/code/mnl/python code/` — active Python MNL scripts
- `updated_2025/results/` — output tables, plots, Excel summaries
- `updated_2025/code/mnl/` — memos, paper drafts, model selection notes

## Current Status
**Done:** Data cleaning; standard and Markov-switching unit root tests; regime classification for ~74 countries (annual, ~1985–2023); baseline MNL estimation with cluster-robust SEs; model selection across 7+ specs; oil exporter, crisis dummy, year-FE robustness checks; subgroup analysis (income groups, pre/post-GFC); binary logit robustness.
**In progress:** Final robustness checks; methodology and results write-up for publication.
**Next:** Complete paper sections; assemble replication files.

## Languages and Tools
- **GAUSS** — data cleaning, Markov-switching AR estimation, unit root testing. Entry point: `updated_2025/code/cab_util.src` (shared utilities).
- **Python** — multinomial logit analysis. Scripts in `updated_2025/code/mnl/python code/`. Key libraries: `statsmodels` (MNLogit, Logit, get_margeff), `pandas`, `numpy`, `openpyxl`.

## Data Conventions
**Key datasets (do not modify — see below):**
- `reg_2_data.csv` — Part 1 analysis input
- `regimes_summary.csv` — compiled Markov-switching regime assignments (country × year)
- `mnl_reg_data.xlsx` — Part 2 MNL input; country-year panel, ~74 countries

**Panel structure:** Unbalanced panel, ~74 countries, annual frequency, ~1985–2023. All transformations (lags, differences, moving averages) must be computed within country groups using `groupby(cn)` before any subsetting or listwise deletion. Never compute lags on the pooled sorted dataset without grouping by country first.

**Identifiers:** `cn` = country code; `year` = year.

**Important quirk:** The `year` column is stored as date strings (e.g., `1985-01-01`). Always extract the integer year using `pd.to_datetime(df[year_var], errors="coerce").dt.year`. Never use `pd.to_numeric()` on this column — it returns NaN and causes rank-deficient model failures.

**Missing values:** Coded as blank. Use listwise deletion after lag creation.

**Outcome variable:** Regime label — `Explosive`, `Stationary`, or `Unit root` (string). Reference category in MNL is Explosive.

**Standard errors:** Always use cluster-robust standard errors clustered at the country level (`cov_type="cluster"`, `cov_kwds={"groups": df[cluster_var]}`). This applies to all regression models across the project.

## Coding Conventions
- Prioritize transparency and clarity. Keep code simple and readable.
- Annotate all scripts — code will be shared with co-authors and published as a replication archive.
- Balance efficiency with readability; avoid over-engineering.
- Use descriptive variable and function names. No enforced naming convention beyond clarity.
- Output results to Excel with named sheets. Keep one script per analytical task.

## Do Not Touch
- `updated_2025/clean-data/reg_2_data.csv`
- `updated_2025/clean-data/mnl_reg_data.xlsx`
- Any file outside of `updated_2025/`
