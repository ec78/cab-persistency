# MNL Section — Code Review Replication Report
**Date:** 2026-03-02
**Reviewer role:** Code review panel (replication audit)
**Script:** `code/mnl/python code/replication_audit.py`
**Data:** `clean-data/mnl_reg_data.xlsx`
**Baseline spec:** C00058 (fixed_er, current_def, comm_ex, manu_ex, opn_l1, gsur_3_yr_l1)

---

## Summary Verdict

**53 / 54 checks PASS.** The MNL results are fully replicable from the current code and data. Every coefficient, standard error, marginal effect, and fit statistic in Tables 4–9 matches the paper to within rounding tolerance. The single failing check is a rounding transcription error in the paper itself (Pre-GFC BIC/obs reported as 1.692, correct value is 1.691).

---

## Check-by-Check Results

### Section 1 — Sample Composition

| Check | Computed | Paper | Status |
|---|---|---|---|
| N observations | 2,451 | 2,451 | ✅ |
| Countries | 74 | 74 | ✅ |
| N explosive | 134 | 134 | ✅ |
| N stationary | 943 | 943 | ✅ |
| N unit root | 1,374 | 1,374 | ✅ |
| % explosive | 5.47% | 5.5% | ✅ |

The 77→74 country reduction is confirmed: the raw data has 77 unique country codes (`cn`), but 3 countries have no usable observations after listwise deletion on the full covariate set. This is a data constraint, not a code error.

---

### Section 2 — Baseline Fit Statistics (Table 6)

| Statistic | Computed | Paper | Diff | Status |
|---|---|---|---|---|
| McFadden R² | 0.050396 | 0.0504 | 0.000004 | ✅ |
| BIC / obs | 1.66051 | 1.661 | 0.000485 | ✅ |

Both fit stats replicate cleanly. The model converged in Newton optimization.

---

### Section 3 — Coefficient Estimates (Table 4, cluster-robust SEs)

All 28 checks (14 coefficients × 2 equations) pass within tolerance (|diff| < 0.001).

**Stationary equation:**

| Variable | Coef (computed) | Coef (paper) | SE (computed) | SE (paper) |
|---|---|---|---|---|
| Constant | 3.085 | 3.085 | 1.087 | 1.087 |
| Fixed ER | 1.869 | 1.869 | 0.556 | 0.556 |
| Current deficit | 0.842 | 0.842 | 0.481 | 0.481 |
| Commodity exporter | 0.188 | 0.188 | 0.759 | 0.759 |
| Manufacturing exporter | −1.204 | −1.204 | 0.683 | 0.683 |
| Trade openness (t−1) | −1.273 | −1.273 | 0.557 | 0.557 |
| Fiscal balance (t−1) | 1.657 | 1.657 | 1.933 | 1.933 |

**Unit root equation:**

| Variable | Coef (computed) | Coef (paper) | SE (computed) | SE (paper) |
|---|---|---|---|---|
| Constant | 3.554 | 3.554 | 1.148 | 1.148 |
| Fixed ER | 1.980 | 1.980 | 0.549 | 0.549 |
| Current deficit | 0.728 | 0.728 | 0.503 | 0.503 |
| Commodity exporter | −0.137 | −0.137 | 0.757 | 0.757 |
| Manufacturing exporter | −1.477 | −1.477 | 0.670 | 0.670 |
| Trade openness (t−1) | −0.819 | −0.819 | 0.453 | 0.453 |
| Fiscal balance (t−1) | 3.241 | 3.241 | 1.809 | 1.809 |

---

### Section 4 — Average Marginal Effects (Table 5)

| Variable | Outcome | Computed | Paper | Status |
|---|---|---|---|---|
| Fixed ER | Explosive | −0.0912 | −0.091 | ✅ |
| Trade openness (t−1) | Explosive | +0.0470 | +0.047 | ✅ |

**Complete AME matrix (for the record):**

| Variable | ΔP(Explosive) | ΔP(Stationary) | ΔP(Unit root) |
|---|---|---|---|
| Fixed ER | **−0.091** | +0.011 | +0.080 |
| Current deficit | −0.036 | +0.040 | −0.003 |
| Commodity exporter | +0.000 | +0.072 | −0.073 |
| Manufacturing exporter | +0.064 | +0.035 | −0.100 |
| Trade openness (t−1) | **+0.047** | −0.120 | +0.073 |
| Fiscal balance (t−1) | −0.123 | −0.305 | +0.428 |

Note: the paper reports AMEs only for statistically significant effects. The full matrix is computed; the paper's selective reporting is accurate.

---

### Section 5 — Binary Logit Robustness (Table 7)

| Variable | p-value | Significant (p<0.10)? |
|---|---|---|
| Fixed ER | 0.718 | No |
| Current deficit | 0.671 | No |
| Commodity exporter | 0.464 | No |
| Manufacturing exporter | 0.533 | No |
| Trade openness (t−1) | 0.385 | No |
| Fiscal balance (t−1) | 0.273 | No |

**Paper claim: "None of the six regressors attain statistical significance" — CONFIRMED.** ✅

Binary sample: 2,317 obs (2,451 − 134 explosive), 74 countries. Convergence confirmed.

---

### Section 6 — Income Subgroup Fit Statistics (Table 8)

| Subgroup | nobs | Countries | N explosive | McFadden R² | BIC/obs | Status |
|---|---|---|---|---|---|---|
| Advanced | 1,041 | 23 | 15 | n/a* | n/a* | ✅ (counts) |
| Emerging | 903 | 28 | 116 | 0.1863 | 1.671 | ✅ |
| Low income | 507 | 23 | 3 | n/a† | n/a† | ✅ (counts) |

*Advanced: McFadden R² returns NaN. Root cause: with only 15 explosive observations, the log-null likelihood equals the log-likelihood (the explosive equation is near-unidentified), producing 1 − 1 = 0 / 0. The paper correctly marks this "n/a".

†Low income: model skipped entirely (3 explosive obs — explosive equation not identified). Paper marks "n/a". ✅

**Emerging market finding confirmed:** R² = 0.1863 vs 0.050 full sample — approximately a 3.7× improvement. This is the paper's headline heterogeneity result and it replicates exactly.

---

### Section 7 — Time-Period Subgroup Fit Statistics (Table 9)

| Period | nobs | Countries | N explosive | McFadden R² | BIC/obs | Status |
|---|---|---|---|---|---|---|
| Pre-GFC (<2008) | 1,356 | 70 | 65 | 0.0420 | **1.691** | ⚠️ see below |
| Post-GFC (≥2008) | 1,095 | 74 | 69 | 0.0893 | 1.645 | ✅ |

---

## Single Discrepancy: Pre-GFC BIC/obs

**Paper reports:** 1.692
**Code computes:** 1.69147
**Difference:** 0.00053 (just above the 0.0005 rounding tolerance)

**Diagnosis:** The computed value 1.69147 rounds to **1.691** at three decimal places, not 1.692. This is a transcription rounding error in the paper — the author or typist rounded 1.6915 to 1.692 rather than 1.691. The underlying BIC (2,293.63) and log-likelihood (−1,096.33) are correct and consistent with all other reported statistics.

**Implication:** No code or data problem. Fix: change "1.692" to "1.691" in Table 9 of the paper.

---

## Code Quality Observations

### What works well

1. **Lag construction is correct.** Lags are computed within country group using `groupby('cn').shift(1)` on the full dataset before any subsetting. The time subgroups (Pre/Post-GFC) therefore carry correct lagged values even for the first post-2008 year (the lag comes from the pre-2008 row for that country). This is the right approach.

2. **Year variable handling.** The `year` column is stored as date strings (`1985-01-01`). All scripts use `pd.to_datetime().dt.year` — not `pd.to_numeric()` — to extract integer years. This is documented in CLAUDE.md and correctly implemented. A `pd.to_numeric()` call here would produce NaN and silently break subgroup filters.

3. **Regime label normalization is robust.** The code handles mixed case, non-breaking spaces, and common variants ("Unit Root", "unit root", "UNIT ROOT") before encoding as Categorical.

4. **Reference category is consistent.** Explosive is always position 0 in the Categorical (confirmed: `categories=['Explosive','Stationary','Unit root']`). The MNLogit baseline is therefore always Explosive across all scripts. Paper's claim "reference = Explosive" is correct throughout.

5. **Cluster-robust SEs are correctly specified.** `cov_type="cluster"`, `cov_kwds={"groups": df[cluster_var]}` where `cluster_var = "cn"`. Country-level clustering applied to all models including subgroups. ✅

6. **Binary logit is correctly specified.** The binary sample drops explosive rows, then codes unit root = 1, stationary = 0. This matches the paper's description ("positive outcome = unit root"). ✅

### Issues found

1. **`partii-mnl-clustered.py` has a namespace bug in `build_margeff_long`.** Lines 194–195 reference `df_model[y_var]` (a module-level variable) inside a function. This works only because the function is always called in the same module scope. If the function were imported or reused elsewhere, it would silently use the wrong data. Should be passed as a parameter.

2. **`star_from_p` thresholds are inconsistent across scripts.** `partii-mnl-clustered.py` uses `p < 0.001` for `***`, while `partii-mnl-binary.py` and `partii-mnl-subgroups.py` use `p < 0.01` for `***`. The paper and memo use `p < 0.01` convention. The clustered script's `***` threshold is therefore non-standard and could mislabel borderline results.

3. **`search_mnl_aggressive.py` and `memo_mnl_top_specs_with_yearfe.py` are not integrated into the replication chain.** It is unclear whether the spec search was the actual source of C00058 or whether C00058 was chosen by hand. The path from search → baseline → paper should be documented.

4. **No single entry-point script.** Running all MNL results requires calling five separate scripts in an unspecified order. A `run_all_mnl.py` wrapper (or Makefile) would make the replication chain unambiguous for external replicators.

---

## Recommended Fixes (in priority order)

| Priority | Issue | File | Fix |
|---|---|---|---|
| 1 (paper) | Pre-GFC BIC/obs: 1.692 → 1.691 | paper Table 9 | Correct transcription |
| 2 (code) | `star_from_p` inconsistency (`0.001` vs `0.01`) | `partii-mnl-clustered.py` line 43 | Change to `p < 0.01` |
| 3 (code) | `df_model` namespace leak in `build_margeff_long` | `partii-mnl-clustered.py` lines 194–195 | Pass `df_model` as parameter |
| 4 (docs) | No replication entry point | — | Add `run_all_mnl.py` with ordered calls |
| 5 (docs) | Spec search → baseline path undocumented | `model selection memo REVISED.md` | Add one paragraph explaining C00058 selection |

---

## Conclusion

The MNL results are **fully replicable** from the existing code and data. The audit found no errors in the analysis itself — every estimate in Tables 4–9 is recoverable to within rounding precision. The emerging market heterogeneity finding (R² = 0.186 vs 0.050), the binary logit null result (all p > 0.25), and the baseline fixed-ER AME (−0.091) are all confirmed.

The single paper-level error (Pre-GFC BIC/obs 1.692 → 1.691) and the two minor code issues (star threshold, namespace leak) do not affect any substantive conclusion in the paper.
