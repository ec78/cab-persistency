# CLAUDE.md — updated_2025 (Paper-Specific Context)

## Paper Identity

**Title:** What Drives the Persistence in Current Account Imbalances?
**Authors:** Eric Clower (Aptech Systems), Hiro Ito (Portland State), Jamel Saadaoui (Paris 8)
**Target journal:** Journal of International Economics (JIE)
**Current draft:** `working_draft_ec_2025_v4_Mar2026.docx`
**Status:** Post-revision; ready for final pass before submission.

---

## What the Paper Does

Two-stage empirical design:
1. **Stage 1 (GAUSS):** Country-specific Markov-switching AR(1) models classify each country-quarter into one of three regimes — explosive, unit root, or stationary — with persistence, mean, and volatility switching independently (Morita et al. 2024 specification).
2. **Stage 2 (Python):** Quarterly regime labels are aggregated to annual prevailing regimes, then a multinomial logit (MNL) explains regime membership using six structural covariates.

**Key findings:**
- Fixed exchange rate arrangements reduce the probability of explosive CAB dynamics by ~9pp (AME = −0.091, p = 0.044)
- Manufacturing export specialization and trade openness *increase* explosive probability
- Model explanatory power is concentrated in the **explosive vs. non-explosive** channel; binary logit on non-explosive obs finds zero significant predictors
- Emerging markets: McFadden R² = 0.186 vs. 0.050 full sample (≈ 4× improvement)
- Post-GFC: R² doubles from 0.042 to 0.089

**Sample:** 74 countries (MNL), 77 countries (unit root stage), annual 1985–2023, 2,451 MNL obs after listwise deletion.

---

## Revision History

| Draft | Key additions |
|---|---|
| v1–v2 | Original drafts |
| v3 (Pass 1) | Lagged ER robustness (Section 5.3.3); mechanism paragraph (peg-defense channel); IIA + two-step limitations; confusion matrix; CV log-loss in Table 6; Chinn-Wei reconciliation; mfg exporter prior fixed |
| v4 (Pass 2) | EM R² finding moved to abstract + intro; 77→74 country explanation added; post-GFC institutional anchors (G20 MAP, IMF Article IV, Basel III); country examples for explosive episodes; two-step and IIA split into separate paragraphs; small-cluster caveat (advanced economies); MS model homogeneity statement |

---

## Persona Scorecard (v4 baseline)

| Persona | v2 score | v4 score | Target |
|---|---|---|---|
| Maria (JIE referee) | 7/10 | ~7/10 | 8/10 |
| Henrik (CB macro) | 7/10 | ~7/10 | 8/10 |
| Rachel (econometrician) | 7/10 | ~7.5/10 | 8/10 |
| David (statistician) | 6/10 | ~6.5/10 | 7/10 |
| James (JIE editor) | 6/10 | ~6.5/10 | 7.5/10 |

---

## Remaining Open Issues (as of v4 → v5 pass)

Issues identified in `paper_review.md` (external review of v4) that are **not yet addressed:**

| # | Issue | Source | Priority |
|---|---|---|---|
| R1 | Title/framing overstates step 2 — claims "persistence" but explains "explosive vs non-explosive" | paper_review | High |
| R2 | Novelty relative to Clower & Ito (2012) not made explicit | paper_review | High |
| R3 | Rare events / inference fragility — 134 obs in few countries; needs leave-one-country-out or rare-events logit acknowledgment | paper_review | **Critical** |
| R4 | First-stage uncertainty — acknowledged but not addressed; posterior probabilities or two-step bootstrap needed (or fuller discussion) | paper_review | High |
| R5 | Causal language needs softening throughout ("reduce" → "are associated with lower probability of") | paper_review | Medium |
| R6 | Post-GFC institutional interpretation is over-stated — not a tested mechanism | paper_review | Medium |
| R7 | Annual aggregation (quarterly → annual modal regime) not defended | paper_review | Medium |
| R8 | Section 3.1 is scaffolding — compress to 2 paragraphs (James) | DOCUMENTATION | Low |
| R9 | "3% explosive recall" framing — clarify that coefficient significance ≠ predictive accuracy | DOCUMENTATION (David) | Medium |
| R10 | BIC footnote for different sample sizes (C00342_fdgap n=2064 vs baseline n=2451) | DOCUMENTATION (Rachel) | Low |

---

## Key Structural Variables (Stage 2)

| Variable | Description | Construction |
|---|---|---|
| `fixed_er` | Fixed/pegged ER indicator | Ilzetzki, Reinhart, Rogoff (2019) coarse classification |
| `ca_deficit` | Current account deficit indicator | Binary: 1 if CAB < 0 |
| `comm_ex` | Primary commodity exporter | World Bank classification |
| `mfg_ex` | Manufacturing exporter | Primary export = manufactured goods |
| `trade_open_l1` | Trade/GDP ratio, lagged 1 year | Reduces simultaneity |
| `fiscal_l1` | Fiscal balance (3-yr MA), lagged | Window t−3 to t−1 |

**Reference category:** Explosive regime. All other outcomes expressed relative to explosive.

---

## Key Analysis Files

| File | Purpose |
|---|---|
| `code/mnl/python code/` | All MNL Python scripts |
| `code/mnl/python code/mnl_lagged_er_robustness.py` | Lagged ER robustness (C1); generates mnl_lagged_er_robustness.xlsx |
| `code/mnl/python code/apply_pass2_edits_v2.py` | Pass 2 edits script |
| `results/mnl_lagged_er_robustness.xlsx` | Confusion matrix, CV results, comparison table |
| `clean-data/mnl_reg_data.xlsx` | MNL input data — do not modify |
| `clean-data/reg_2_data.csv` | Unit root analysis input — do not modify |

---

## Paper Sections (v4 structure)

1. Introduction
2. Current account persistency: facts and theory
   - 2.1 Facts: CAB Divergence and Persistency
   - 2.2 External balance and the intertemporal approach
3. Stationarity of current account balances and regime shifts
   - 3.1 Linear unit root tests (motivational; not a standalone contribution)
   - 3.2 Markov-Switching Estimation
   - 3.3 Regime identification
   - 3.4 Global stationarity
4. Results from the Markov-Switching Unit Root Model
   - 4.1–4.4 Distribution, heterogeneity, time evolution, implications
5. Determinants of Current Account Persistence
   - 5.1 Methodology (Framework, Covariates, Model selection)
   - 5.2 Baseline Results (Coefficients, AMEs)
   - 5.3 Robustness Checks (YFE/Crisis, Oil exporter, Lagged ER)
   - 5.4 Binary Logit Robustness
   - 5.5 Subgroup Heterogeneity (Income groups, Time periods)
   - 5.6 Summary
6. Concluding remarks
References + Appendices

---

## Coding Notes for Paper Edits

- Paper is a `.docx` file; edit with `python-docx`
- To add a paragraph after a specific paragraph: use `para._element.addnext(new_para._element)`
- To insert before: use `para._element.addprevious(new_para._element)`
- Always save as a new version (e.g., `v5`) — never overwrite `v4`
- When modifying paragraph text with runs, clear existing runs or iterate through them to replace text

---

## Editorial Notes

- **Do not** present results as causal; use association language throughout
- Fixed ER finding is robust to lagging (marginally stronger when lagged — this is the strongest robustness argument)
- Chinn-Wei (2013) reconciliation is already present in Section 5 (conclusion para) and paras 15, 169
- The 77→74 country drop is explained in para [121] of v4
- Confusion matrix is in Appendix Table C1; CV log-loss in Table 6

---

## Reviewer Personas

Defined in `REVIEWER_PERSONAS.md`. Used in `DOCUMENTATION_PERSONA_FEEDBACK.md` to simulate pre-submission review.
Personas: Maria (JIE referee), Henrik (CB macro), Rachel (econometrician), David (statistician), James (AER/JIE editor).
