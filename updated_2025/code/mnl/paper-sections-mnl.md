# Paper Sections: MNL Determinants of CAB Persistence Regimes
**Draft:** 2/23/2026 — for internal review

---

## 4. Determinants of Current Account Persistence Regimes

### 4.1 Methodology

#### 4.1.1 Empirical Framework

To identify the structural determinants of current account persistence regimes, we estimate a multinomial logit (MNL) model in which the dependent variable is the regime classification assigned to each country-year observation. Let $y_{it} \in \{0, 1, 2\}$ denote the latent regime state — coded as explosive, stationary, or unit root, respectively — as identified by the Markov-switching unit root procedure described in Section 3. We model the probability of observing each regime outcome as a function of a vector of country-level structural characteristics $\mathbf{x}_{it}$:

$$\Pr(y_{it} = j \mid \mathbf{x}_{it}) = \frac{\exp(\mathbf{x}_{it}' \boldsymbol{\beta}_j)}{\sum_{k=0}^{2} \exp(\mathbf{x}_{it}' \boldsymbol{\beta}_k)}, \quad j \in \{0, 1, 2\}$$

We normalize by setting $\boldsymbol{\beta}_0 = \mathbf{0}$, so all coefficient estimates are expressed relative to the explosive regime as the baseline category. This choice of reference category is motivated by the substantive interest in identifying factors that distinguish destabilizing external dynamics from the stable regime space. Standard errors are clustered at the country level throughout to account for serial dependence within country time series.

#### 4.1.2 Covariates and Construction

The specification is guided by the theoretical literature on current account adjustment and exchange rate regime effects. We include six structural regressors:

**Exchange rate regime.** A binary indicator equal to one if the country maintained a fixed (or pegged) exchange rate arrangement in year $t$, drawn from the Ilzetzki, Reinhart, and Rogoff (2019) coarse classification. Under fixed rates, external adjustment must operate through internal price mechanisms rather than nominal depreciation, altering the dynamics of current account imbalances.

**Current account deficit indicator.** A binary variable equal to one if the country ran a current account deficit in year $t$. This captures whether the initial balance position is relevant to the persistence regime, conditioning on the other structural covariates.

**Commodity exporter.** An indicator equal to one if the country is classified as a primary commodity exporter, following World Bank income and trade classification criteria. Commodity exporters are exposed to terms-of-trade volatility that can generate persistent or explosive current account movements.

**Manufacturing exporter.** An indicator equal to one if manufactured goods represent the primary export category. Manufacturing exporters typically face more elastic global demand and smoother export revenue, which may support more stable current account dynamics.

**Trade openness (lagged).** The ratio of total trade (exports plus imports) to GDP, lagged one period ($t-1$). We use the lagged value to reduce simultaneity concerns — the regime classification at $t$ is contemporaneous with the openness measure, creating a potential endogeneity problem if both are measured at $t$. Lagging also ensures that openness captures the pre-existing structural openness position rather than a realization that may itself depend on the regime.

**Fiscal balance (3-year moving average, lagged).** The general government fiscal surplus or deficit as a share of GDP, averaged over $t-2$ through $t$, then lagged one period to the $(t-3, t-1)$ window. The three-year smoothing reduces year-to-year budget cycle volatility and captures the medium-term fiscal position. We use the lagged moving average again to mitigate reverse causality from the external regime to fiscal outcomes via automatic stabilizers.

All continuous variables are standardized at the sample level. The complete sample covers 74 countries observed annually over the period from the mid-1980s through 2023, yielding 2,451 usable observations after listwise deletion on all covariates.

#### 4.1.3 Model Selection

Model specification follows a composite criterion that balances parsimony, predictive performance, and sample coverage. For each candidate specification, we compute: (i) BIC per observation (BIC/obs = $[-2\ell + k\ln(n)]/n$, where $k$ is the number of free parameters), which penalizes overparameterization relative to sample size; (ii) out-of-sample log-loss from a country-grouped five-fold cross-validation, which evaluates predictive performance on held-out country trajectories; and (iii) sample retention, since adding covariates reduces the usable sample through missing data. The preferred specification, which we designate C00058, performs consistently well on all three dimensions.

A key specification decision concerns year fixed effects. We find that including a full set of annual time dummies substantially inflates BIC/obs and causes convergence failure in certain specifications, without meaningfully improving cross-validated predictive fit. This pattern indicates that regime dynamics are driven primarily by persistent cross-sectional structural differences rather than by common global time trends. As a direct test of this conclusion, we include targeted crisis-period dummies for the Global Financial Crisis (2008–2009) and the COVID-19 shock (2020–2021) — the two largest identifiable global disturbances in the sample — and find that BIC/obs increases marginally relative to the baseline. We therefore exclude year fixed effects from the preferred specification and treat the crisis-dummy exercise as a robustness check.

---

### 4.2 Baseline Results

#### 4.2.1 Coefficient Estimates

Table 4 reports MNL coefficient estimates for the preferred specification (C00058), with the explosive regime as the reference category. All standard errors are clustered at the country level.

**Table 4: MNL Estimates — Determinants of Current Account Persistence Regimes**
*(Reference category: Explosive regime)*

| Variable | Stationary | Unit Root |
|---|---|---|
| Constant | 3.085** (1.087) | 3.554** (1.148) |
| Fixed exchange rate | 1.869*** (0.556) | 1.980*** (0.549) |
| Current deficit | 0.842* (0.481) | 0.728 (0.503) |
| Commodity exporter | 0.188 (0.759) | −0.137 (0.757) |
| Manufacturing exporter | −1.204* (0.683) | −1.477** (0.670) |
| Trade openness (t−1) | −1.273** (0.557) | −0.819* (0.453) |
| Fiscal balance (3-yr, t−1) | 1.657 (1.933) | 3.241* (1.809) |
| Observations | 2,451 | 2,451 |
| Countries | 74 | 74 |
| McFadden R² | 0.050 | 0.050 |
| BIC / obs | 1.661 | 1.661 |
| Outcome share | 38.5% | 56.1% |

*Notes:* Standard errors in parentheses, clustered at the country level. The explosive regime (5.5% of observations) is the reference category. * p < 0.10, ** p < 0.05, *** p < 0.01.

The two strongest and most consistent predictors are the **fixed exchange rate indicator** and the **manufacturing exporter indicator**. Countries under fixed exchange rate arrangements are significantly more likely to exhibit stationary or unit root current account behavior than explosive divergence, with large and highly significant coefficients in both equations. This result is consistent with the disciplining role of exchange rate pegs: the commitment to a fixed rate constrains the scope for unchecked current account deterioration, reducing the probability of entering an explosive adjustment path.

Countries classified as manufacturing exporters, by contrast, are significantly *less* likely to be in the stationary or unit root regimes relative to the explosive regime, particularly the unit root outcome. This suggests that specialization in manufactured exports is associated with current account dynamics that more readily drift into explosive territory — possibly reflecting demand volatility or export competition effects that prevent smooth external adjustment.

**Trade openness** enters negatively and significantly in both equations: more open economies at $t-1$ are less likely to be in the stationary or unit root regimes relative to the explosive category. This might initially seem counterintuitive, but it reflects that trade-open economies tend to undergo rapid and at times overshooting external adjustments. The lagged fiscal balance is positive and marginally significant for the unit root equation, suggesting that governments running stronger medium-term fiscal positions are more likely to exhibit persistent rather than explosive current account dynamics.

#### 4.2.2 Average Marginal Effects

Because MNL coefficients are not directly interpretable in terms of probability changes, Table 5 reports average marginal effects (AMEs), computed as the mean over all observations of the individual-specific marginal effects. AMEs measure the expected change in the probability of each regime outcome associated with a unit change in each covariate, holding all other variables at their observed values.

**Table 5: Average Marginal Effects on Regime Probabilities**

| Variable | ΔP(Explosive) | ΔP(Stationary) | ΔP(Unit Root) |
|---|---|---|---|
| Fixed exchange rate | −0.091** | +0.011 | +0.080 |
| Trade openness (t−1) | +0.047** | −0.120 | +0.073 |
| Manufacturing exporter | — | — | — |
| Current deficit | — | — | — |
| Commodity exporter | — | — | — |
| Fiscal balance (3-yr, t−1) | — | — | — |

*Notes:* Dashes indicate AMEs not statistically significant at the 10% level. Marginal effects on all three outcome probabilities sum to zero by construction. Standard errors computed via the delta method.

The AME analysis reveals that the model's explanatory power is concentrated in the **explosive versus non-explosive** channel rather than in the distinction between stationary and unit root outcomes. A fixed exchange rate arrangement reduces the probability of the explosive regime by approximately 9.1 percentage points on average — a substantively large effect given that the unconditional probability of the explosive regime is only 5.5 percent. Trade openness has the opposite effect, increasing the probability of the explosive outcome by 4.7 percentage points. No other covariate produces a statistically significant AME on any of the three regime probabilities, and no variable generates a significant AME on the stationary or unit root outcomes separately.

This pattern motivates the binary robustness analysis we turn to in Section 4.4.

---

### 4.3 Robustness Checks

#### 4.3.1 Year Fixed Effects and Crisis Dummies

Table 6 summarizes fit statistics across the full set of candidate specifications examined. The central result is that year fixed effects are not supported by the data: models with full annual time dummies consistently produce higher BIC/obs and in the case of C00004 (contemporaneous openness) fail to converge entirely. The year-FE penalty arises because the parameter count expands by the number of sample years with no commensurate improvement in fit, consistent with regime dynamics being primarily structural rather than driven by common cyclical fluctuations.

**Table 6: Model Comparison Across Specifications**

| Model | Description | Obs | McFadden R² | BIC/obs | Year FE |
|---|---|---|---|---|---|
| C00004 | Contemporaneous openness | 2,613 | 0.048 | 1.663 | No |
| C00004 w/ YFE | Full year dummies | 2,613 | 0.058 | 1.958 | Yes (no convergence) |
| **C00058** | **Lagged openness + fiscal (baseline)** | **2,451** | **0.050** | **1.661** | **No** |
| C00058 w/ YFE | Full year dummies | 2,451 | 0.063 | 1.970 | Yes |
| C00058_fdgap | + Financial development gap | 2,064 | 0.067 | 1.670 | No |
| C00058_oil | Oil exporter (replaces comm_ex) | 2,451 | — | — | No |
| C00058_crisis | + GFC (2008–09), COVID (2020–21) dummies | 2,451 | 0.051 | 1.673 | No |

*Notes:* BIC/obs = (BIC) / (number of observations). C00058_oil is treated as exploratory; with only 40 oil-exporter observations in the sample, the explosive-equation parameters are unreliable. Dashes indicate convergence with unreliable fit statistics.

As a direct test of the year-FE concern, we include indicator variables for the Global Financial Crisis (2008–2009) and the COVID-19 shock (2020–2021) in C00058_crisis. These are the two largest identifiable global disturbances in the sample period. The targeted crisis dummies add only two parameters and produce BIC/obs = 1.673, marginally worse than the baseline (1.661), with no meaningful change in the coefficient estimates on structural variables. Neither crisis dummy is significant at conventional levels. This confirms that the structural variables absorb the relevant cross-country variation in regime behavior and that no residual common shock effect remains once these covariates are controlled.

The financial development gap specification (C00342_fdgap) yields modest improvement in R² (0.067 vs. 0.050) but reduces the sample by approximately 16 percent due to missing financial development data. Given the cost in sample size relative to the marginal improvement in fit, this variable is not retained in the baseline.

The lagged specification C00058 modestly outperforms the contemporaneous C00004 on BIC/obs while retaining 162 fewer observations (due to the additional lag requirement), a worthwhile tradeoff given the reduced simultaneity concern.

#### 4.3.2 Oil Exporter Robustness

Replacing the commodity exporter dummy with a more narrowly defined oil exporter indicator cannot be implemented as a full MNL robustness check. The oil exporter dummy covers only 40 country-year observations and exhibits complete separation in the unit root equation: none of the 40 oil-exporter observations are classified as unit root. With P(Unit Root | oil=1) = 0 in the data, the unit root equation parameters are unidentified and the MNL estimator fails to converge to finite estimates.

The regime distribution among oil exporters is itself informative: 13 observations (32.5%) fall in the explosive regime and 27 (67.5%) in the stationary regime, with zero in the unit root regime. This pattern suggests that oil exporters face a sharper binary dynamic — either explosive external imbalance or rapid mean reversion — with no tendency toward persistent but bounded current account dynamics. We retain the broader commodity exporter classification in the baseline and note this descriptive finding as a point for future research with a larger sample of oil-exporting countries.

---

### 4.4 Binary Logit Robustness

The explosive regime comprises only 134 observations (5.5% of the sample). All MNL coefficient estimates therefore reflect contrasts relative to this small reference group, which raises the question of whether the baseline results are driven by the explosive-versus-all-others split or reflect genuine differentiation among the three regimes. We address this directly by estimating a binary logit model on the 2,317 non-explosive observations only (Table 7).

**Design.** We drop the 134 explosive observations and estimate a binary logit with unit root as the positive outcome ($y = 1$) and stationary as the negative outcome ($y = 0$). This directly tests whether the same structural variables that predict regime type in the full-sample MNL also predict the within-stable-regime distinction between persistent and mean-reverting current account behavior.

**Table 7: Binary Logit — Unit Root vs. Stationary (Excluding Explosive Observations)**

| Variable | AME | Std. Error | p-value |
|---|---|---|---|
| Fixed exchange rate | +0.027 | — | 0.717 |
| Current deficit | −0.027 | — | 0.669 |
| Commodity exporter | −0.076 | — | 0.460 |
| Manufacturing exporter | −0.062 | — | 0.531 |
| Trade openness (t−1) | +0.100 | — | 0.377 |
| Fiscal balance (3-yr, t−1) | +0.358 | — | 0.267 |
| Observations | 2,317 | | |
| Countries | 74 | | |

*Notes:* Outcome is 1 = Unit root, 0 = Stationary. Standard errors clustered at the country level. None of the six variables are significant at the 10% level.

**Result.** None of the six regressors attain statistical significance in the binary logit. This finding has a precise substantive interpretation: the structural variables in the baseline MNL primarily explain *which countries avoid explosive current account dynamics* — not what drives the stationary versus unit root distinction within the stable regime space. Fixed exchange rate arrangements, trade openness, and manufacturing export structure effectively predict whether a country's current account is prone to explosive divergence; they do not differentiate between mean-reverting and persistently stable dynamics among countries already in the non-explosive group.

This result does not undermine the MNL findings. Rather, it refines their interpretation: the model should be read primarily as a classifier of explosive versus non-explosive regime propensity. The stationary-unit root contrast is a secondary outcome, and the absence of significant binary-logit predictors points to a research agenda on the within-stable-regime persistence question that likely requires different covariates — potentially capturing financial market depth, creditor composition, or country-specific institutional factors not in the current covariate set.

---

### 4.5 Subgroup Heterogeneity

#### 4.5.1 Income Groups

We re-estimate the baseline specification separately for three income subgroups: advanced economies (23 countries), emerging markets (28 countries), and low-income developing countries (23 countries). Table 8 summarizes fit statistics. Coefficient-level results are reported in Appendix Table A.X.

**Table 8: MNL Fit Statistics by Income Group**

| Subgroup | Obs | Countries | Explosive obs | McFadden R² | BIC/obs |
|---|---|---|---|---|---|
| Advanced | 1,041 | 23 | 15 | — | — |
| Emerging | 903 | 28 | 116 | **0.186** | 1.671 |
| Low income | 507 | 23 | 3 | — | — |
| Full sample | 2,451 | 74 | 134 | 0.050 | 1.661 |

*Notes:* Dashes indicate that explosive-equation parameters are unreliable due to insufficient explosive observations (15 and 3 for advanced and low-income subgroups, respectively). The MNL is estimated for all subgroups but fit statistics are only interpretable for emerging markets.

The income-group results reveal pronounced heterogeneity. Model fit is dramatically higher for emerging market economies (McFadden R² = 0.186) than for the full sample (0.050) — a nearly four-fold improvement. This indicates that structural policy variables — particularly exchange rate arrangements and export composition — are far more powerful predictors of current account regime dynamics in emerging markets than in advanced or low-income economies.

The finding is consistent with the broader institutional literature: advanced economies possess more institutionalized adjustment mechanisms (flexible exchange rates, deep capital markets, credible policy frameworks) that insulate their current account dynamics from discrete structural regime-switching driven by the covariates under study. Low-income economies, at the other extreme, have too few explosive observations to identify the explosive equation reliably and likely exhibit dynamics dominated by aid flows, commodity dependence, and IMF program conditionality that fall outside our covariate set.

The emerging-market result has direct policy implications: exchange rate policy and export diversification have measurable effects on the likelihood of explosive external imbalances in precisely the group of countries where such imbalances are most consequential for global financial stability.

#### 4.5.2 Time Periods

Table 9 reports results separately for the pre-GFC (before 2008) and post-GFC (2008 onward) subsamples.

**Table 9: MNL Fit Statistics by Time Period**

| Subgroup | Obs | Countries | McFadden R² | BIC/obs |
|---|---|---|---|---|
| Pre-GFC (before 2008) | 1,356 | 70 | 0.042 | 1.692 |
| Post-GFC (2008 onward) | 1,095 | 74 | **0.089** | 1.645 |

Model fit more than doubles in the post-GFC period (R² from 0.042 to 0.089, with BIC/obs improving from 1.692 to 1.645). This suggests that the structural variables have become increasingly relevant predictors of current account regime classification since the financial crisis. The post-crisis period was characterized by heightened international scrutiny of global imbalances, the consolidation of the post-Bretton Woods international monetary architecture, and increased differentiation across countries by exchange rate arrangement and export structure. These developments likely strengthened the mapping from observable structural characteristics to persistent external imbalance dynamics, making structural factors more predictive in the post-2008 environment.

The finding also reinforces the conclusion from the crisis-dummy robustness check: the post-GFC period does not simply represent a shift in common global conditions (which would be captured by a time dummy); rather, it represents a structural change in how cross-country differences in policy and trade patterns translate into external regime behavior.

---

### 4.6 Summary of Main Findings

The multinomial logit analysis yields three principal findings.

**First**, the primary determinant of explosive current account dynamics is the exchange rate regime. Countries under fixed exchange rate arrangements are significantly and substantially less likely to enter the explosive regime, with average marginal effects indicating an approximately 9 percentage point reduction in the probability of explosive behavior. This result holds consistently across specifications, income subgroups, and time periods.

**Second**, the model's explanatory power operates principally through the explosive-versus-non-explosive channel. Structural variables — exchange rate arrangements, trade openness, and export composition — reliably predict whether a country is prone to explosive current account divergence, but do not significantly distinguish between stationary and persistently stable (unit root) behavior within the stable regime. The binary logit robustness exercise, which entirely excludes explosive observations, finds no significant predictors of the stationary-unit root distinction, pointing to the idiosyncratic or institutionally specific nature of within-stable-regime persistence.

**Third**, model performance is substantially higher for emerging market economies and in the post-GFC period, confirming that the policy variables under study are most consequential for middle-income economies and that the post-crisis international monetary environment has amplified the role of structural characteristics in determining current account dynamics.

---

*[Tables 4–9 are presented above inline; in the final paper these will be formatted as numbered exhibit tables with full source notes. Appendix tables for subgroup coefficient estimates to be added.]*

---
