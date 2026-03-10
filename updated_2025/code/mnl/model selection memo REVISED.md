# Model Selection Memo — Revised
**Date:** 2/23/2026
**Authors:** [co-author list]
**Re:** MNL determinants of current account persistence regimes — updated specification and robustness results

---

## Objective

We estimate a multinomial logit (MNL) model to identify the determinants of current account persistence regimes — classified as explosive, stationary, or unit root — using a panel of 74 countries observed annually. Regime classifications come from country-specific Markov-switching unit root models estimated on information available up to and including time t.

All models use country-clustered standard errors. Model selection uses a composite criterion balancing out-of-sample predictive performance (country-grouped cross-validation), parsimony (BIC per observation), and sample retention.

---

## Baseline Specification

**Preferred model (C00058):** No year fixed effects. Regressors: fixed exchange rate, current account deficit indicator, commodity exporter dummy, manufacturing exporter dummy, lagged trade openness (t−1), lagged 3-year fiscal balance (t−1).

**Sample:** 2,451 observations, 74 countries. Outcome distribution: 5.5% explosive, 38.5% stationary, 56.1% unit root.

### Coefficient Table (Cluster-Robust SEs, Reference = Explosive)

| Variable | Stationary | Unit root |
|---|---|---|
| Constant | 3.085** (1.087) | 3.554** (1.148) |
| Fixed exchange rate | 1.869*** (0.556) | 1.980*** (0.549) |
| Current deficit | 0.842* (0.481) | 0.728 (0.503) |
| Commodity exporter | 0.188 (0.759) | −0.137 (0.757) |
| Manufacturing exporter | −1.204* (0.683) | −1.477** (0.670) |
| Trade openness (t−1) | −1.273** (0.557) | −0.819* (0.453) |
| Fiscal balance (3-yr, t−1) | 1.657 (1.933) | 3.241* (1.809) |
| **nobs** | 2,451 | 2,451 |
| **Countries** | 74 | 74 |
| **McFadden R²** | 0.0504 | 0.0504 |
| **BIC/obs** | 1.6605 | 1.6605 |

*p < 0.10, **p < 0.05, ***p < 0.01. Standard errors in parentheses.

### Average Marginal Effects (AMEs)

The AME analysis reveals that most of the model's explanatory power operates through the **explosive vs. non-explosive** channel rather than through the stationary vs. unit root distinction:

| Variable | ΔP(Explosive) | ΔP(Stationary) | ΔP(Unit root) |
|---|---|---|---|
| Fixed exchange rate | −0.091** | +0.011 | +0.080 |
| Trade openness (t−1) | +0.047** | −0.120 | +0.073 |
| Others | not significant | not significant | not significant |

The fixed exchange rate dummy reduces the probability of the explosive regime by approximately 9 percentage points. Trade openness (lagged) increases explosive probability — a result that likely reflects how open economies experience faster external adjustment dynamics, whether corrective or destabilizing. Importantly, no variable produces a significant AME on the stationary or unit root categories separately, which motivates the binary robustness analysis below.

---

## Model Comparisons Across Specifications

| Model | Key features | nobs | McFadden R² | BIC/obs | Year FE |
|---|---|---|---|---|---|
| C00004 | Contemporaneous openness | 2,613 | 0.0478 | 1.663 | No |
| C00004 w/ YFE | Full year dummies | 2,613 | 0.0582 | 1.958 | **Yes (failed to converge)** |
| **C00058 (baseline)** | **Lagged openness + fiscal** | **2,451** | **0.0504** | **1.661** | **No** |
| C00058 w/ YFE | Full year dummies | 2,451 | 0.0633 | 1.970 | Yes |
| C00342_fdgap | + financial dev. gap | 2,064 | 0.0672 | 1.670 | No |
| C00058_crisis | + GFC (2008–09), COVID (2020–21) dummies | 2,451 | 0.0508 | 1.673 | No |

> **Note on oil exporter spec (C00058_oil):** This specification cannot be estimated. The oil dummy (n=40) exhibits complete separation in the unit root equation — zero oil-exporter observations fall in the unit root regime (cross-tab: 13 explosive / 27 stationary / 0 unit root). The MNLogit unit root equation is unidentified and all parameters return NaN. This is a data constraint, not a code error. The descriptive finding — that oil exporters are never classified as unit root — is itself substantively interesting and should be noted in the paper.

**Key observations:**

1. **Year fixed effects are not supported.** Models with full year FE consistently produce higher BIC per observation. C00004_yearFE failed to converge entirely. Year FE substantially inflates the parameter count without meaningful improvement in predictive fit. This confirms that regime dynamics are driven by cross-sectional structural differences, not common global time patterns.

2. **Lagged specification (C00058) dominates contemporaneous (C00004).** Lagged trade openness and fiscal balance reduce endogeneity concerns and marginally improve BIC.

3. **Financial development gap (C00342_fdgap) reduces sample by ~16%** (2,451 → 2,064 obs) with only modest R² improvement (0.050 → 0.067). Not retained in baseline.

4. **Targeted crisis dummies (C00058_crisis) confirm structural story.** Adding GFC (2008–09) and COVID (2020–21) period dummies yields BIC/obs = 1.673, marginally worse than baseline (1.661). This is the most direct test of the year-FE concern: even the two largest identified global shocks do not improve model fit once structural variables are controlled for.

5. **Oil exporter robustness (C00058_oil) cannot be estimated due to complete separation.** The oil exporter dummy (40 observations out of 2,451) exhibits complete separation in the unit root equation: zero oil-exporter observations appear in the unit root regime. The regime distribution for oil exporters is: 13 explosive, 27 stationary, 0 unit root. Because the MNLogit's unit root equation cannot be identified when one regressor perfectly predicts the outcome (P(Unit Root | oil=1) = 0), all model parameters return NaN. This is a data constraint, not a convergence failure. The substantive finding from the cross-tabulation is itself noteworthy: oil exporters appear to never exhibit unit root dynamics — they either adjust explosively or return to balance sharply. This should be reported as a descriptive finding. We retain comm_ex in the baseline and exclude the oil spec from the model comparison table.

---

## Binary Logit Robustness

**Motivation:** The explosive category has only 134 observations (5.5% of the sample). The MNL baseline uses explosive as the reference, meaning all coefficients reflect contrasts against this small group. The binary robustness check asks whether the baseline results survive when explosive observations are dropped entirely and the model reduces to a stationary vs. unit root comparison.

**Design:** Drop 134 explosive observations (2,451 → 2,317 obs, 74 countries). Estimate binary logit with unit root as the positive outcome (1 = unit root, 0 = stationary). Cluster-robust SEs throughout.

**Result:**

| Variable | Binary logit AME | p-value |
|---|---|---|
| Fixed exchange rate | +0.027 | 0.717 |
| Current deficit | −0.027 | 0.669 |
| Commodity exporter | −0.076 | 0.460 |
| Manufacturing exporter | −0.062 | 0.531 |
| Trade openness (t−1) | +0.100 | 0.377 |
| Fiscal balance (3-yr, t−1) | +0.358 | 0.267 |

**None of the six regressors are significant** in the binary logit. This finding has a precise substantive interpretation:

> *The structural variables in the baseline MNL primarily explain which countries avoid explosive CAB dynamics — not what drives stationary versus unit root behavior within the non-explosive group.*

This does not invalidate the MNL results. Rather, it refines their interpretation: fixed exchange rate regimes, trade openness, and manufacturing export structure predict whether a country's current account tends toward extreme divergence (explosive regime) or stays within the stable regime space. The stationary/persistent distinction within that stable space is not well-explained by the same observables and likely reflects idiosyncratic country-level dynamics or features not captured in the current covariate set.

**Implication for the paper:** The baseline MNL results should be interpreted primarily as a model of explosive vs. non-explosive regime classification. The stationary–unit root contrast is a secondary finding, and the absence of significant binary-logit predictors is a result to report, not a failure — it points to future research on the within-stable-regime persistence question.

---

## Subgroup Heterogeneity

### Income Groups

| Subgroup | nobs | Countries | Explosive | McFadden R² | BIC/obs | Notes |
|---|---|---|---|---|---|---|
| Advanced | 1,041 | 23 | 15 | n/a | n/a | Too few explosive for reliable MNL |
| Emerging | 903 | 28 | 116 | **0.1863** | 1.671 | Strong model fit |
| Low income | 507 | 23 | 3 | n/a | n/a | Explosive equation not identified |

**Key finding:** The model fits dramatically better for emerging markets (R² = 0.19 vs 0.05 for full sample). Structural variables — exchange rate regime, export composition, openness — are far more powerful predictors of regime classification for emerging economies than for the full panel. This is consistent with the interpretation that advanced economies have more institutionalized external adjustment mechanisms that are less sensitive to the policy variables under study, while emerging-market CAB dynamics are more directly shaped by these structural features.

The advanced and low-income subgroup fit statistics are not reported because the MNL cannot reliably identify the explosive equation with 15 and 3 explosive observations respectively. The stationary vs. unit root comparisons within these subgroups converged and can be discussed qualitatively, but should be treated with caution.

### Time Periods

| Subgroup | nobs | Countries | McFadden R² | BIC/obs |
|---|---|---|---|---|
| Pre-GFC (before 2008) | 1,356 | 70 | 0.0420 | 1.692 |
| Post-GFC (2008 onward) | 1,095 | 74 | **0.0893** | 1.645 |

**Key finding:** Model fit more than doubles post-GFC (R² 0.042 → 0.089, BIC/obs improves 1.692 → 1.645). This suggests that the structural variables have become increasingly relevant determinants of regime classification in the post-crisis period. Post-2008, the international monetary system became more differentiated by exchange rate arrangement and export structure as drivers of current account dynamics, likely reflecting the global rebalancing discussion following the crisis.

---

## Identification and Robustness Summary

| Check | Result | Implication |
|---|---|---|
| Year FE | Worsens fit, convergence failure | Confirmed: structural > cyclical |
| Lagged vs. contemporaneous openness | Lagged marginally preferred | Reduces simultaneity |
| Targeted crisis dummies (GFC, COVID) | Negligible fit improvement | No residual global shock effect |
| Oil vs. broad commodity dummy | Complete separation (zero oil obs in unit root regime) | Report cross-tab descriptively; retain comm_ex in baseline |
| Binary logit (drop explosive) | No significant predictors | Main story is explosive vs. non-explosive |
| Emerging vs. full sample | R² nearly 4× higher | Heterogeneity by income level confirmed |

---

## Conclusion and Preferred Specification

The preferred baseline is **C00058**: fixed exchange rate, current deficit, commodity exporter, manufacturing exporter, lagged trade openness, lagged 3-year fiscal balance; 74 countries; no year fixed effects; country-clustered standard errors.

The key substantive result is that **structural policy and adjustment features — principally exchange rate arrangements and export composition — are the primary determinants of whether a country's current account balance enters an explosive divergence regime**. Within the non-explosive regime space, the stationary vs. unit root classification is not reliably predicted by the same variables, pointing to idiosyncratic persistence dynamics that are orthogonal to observable structural characteristics.

The emerging-market heterogeneity finding suggests that the policy relevance of these results is concentrated among middle-income economies, where exchange rate and trade policy have the most direct impact on CAB regime dynamics.

---

*Next steps: paper write-up of methodology and results section.*
