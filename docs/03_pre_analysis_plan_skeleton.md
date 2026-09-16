# 03 — Pre-analysis plan: skeleton and candidate hypotheses

Version 0.1 (skeleton, not yet registered), 15 September 2026. The registered plan will live at `docs/pap/PAP-v1_<date>.md`, be committed and tagged `pap-v1`, and be frozen before the Q4 2026 outcome data are examined. Everything below is a candidate; the point of writing it now is to fix wording before any outcome is known. Where the preliminary memo of 15 Sep 2026 already looked at 2026 prices and departures, the affected hypotheses are marked so that their confirmatory test uses only data captured after registration.

**Plain-language summary.** Before we look at how the Q4 2026 markets settle, we write down exactly which claims we are testing, on which markets, with which score, and what counts as a pass. A single primary claim carries the decision weight: that cheap YES contracts on individual vacate-rule departure markets are priced above their realized frequency by more than the cost of trading. Everything else is secondary, and we say up front how many secondary tests there are.

## 1. Hypotheses

Notation follows document 01. $\delta(v,h,B)$ is realized frequency minus mean price in a cell.

### Primary

**H1 (YES overpricing in the tradable bin).** For individual markets under the vacate rule ($v=$ EFFECTIVELEAVE-type), captures with price $p_{m,t}\in[0.05,0.30)$ and horizon $\tau_{m,t}\in[60,200]$ days,
$$\delta_1=\pi(v,h,B)-\bar p<0,\qquad\text{decision threshold }\ \delta_1\le-0.04 .$$
The threshold is the approximate round-trip cost for a NO position at these prices (half-spread of 2–3¢ plus taker fee of 0.7–1.5¢); a smaller miscalibration is real but not actionable. One capture per market per horizon bin, chosen as the first capture with $\tau$ in the bin. Test: one-sided; interval by block bootstrap with blocks defined by (administration or body) × calendar quarter; also reported as a two-sided 95% interval. *Contaminated by the 15 Sep memo?* Partly: the memo compared 2026 prices with the 2026 realized hazard, but no settled NO outcomes exist yet for the 2026 roster. The confirmatory sample for H1 is markets settling on or after the registration date.

### Secondary (multiplicity reported; Holm adjustment across S1–S5 for any claim of "significant")

**S1 (rule-gap).** Among US-administration vacate-rule markets, the probability that a qualifying announcement occurs inside the window with an effective date after the window end is higher when the window ends 31 Dec than for other window ends, and the YES price in the five trading days after such an announcement exceeds 0.5. The first clause is a Phase 1 (historical) estimate of $P(T^{\mathrm{ann}}\le b<T^{\mathrm{vac}}\mid T^{\mathrm{ann}}\in[b-60,b])$ by month; the second is an event study on captured prices. The historical count is small (2018 gives two such cases, Zinke and Kelly); the plan states the count and does not report a p-value below n = 10 events.

**S2 (stickiness).** Within a market, the slope of $\log\hat\lambda_{m,t}$ on $\log\tau_{m,t}$ is more negative than the slope implied by the calendar-varying benchmark M1 fit on pre-2025 data. Estimand E3. This is the hypothesis most exposed to the objection that a flat price is rational under a late-window hazard spike; the benchmark comparison is what makes it testable, and the KXHEGSETHOUT and KXKASHOUT monthly term structures captured from today onward provide a direct read of the market's own calendar belief.

**S3 (cross-contract coherence).** The "any member leaves or announces before 1 Jan 2027" contract (KXCABLEAVE) and the individual vacate-rule contracts on the same offices are jointly inconsistent under any exchangeable dependence with frailty variance below a stated bound. Operationalized: let $q$ be the KXCABLEAVE mid and $p_1,\dots,p_k$ the individual mids for Cabinet-defined offices; under independence $1-\prod(1-p_j)$ versus $q$; under a gamma frailty with variance $\theta$, solve for the $\theta$ that reconciles them and compare with the Phase 1 estimate of $\theta$. On 15 Sep 2026 the two sides differ by a large factor (four cabinet-level names at ~17¢ alone give $1-0.83^4=0.53$ against $q=0.56$ for all 25 offices under a *broader* rule); this observation is exploratory and is recorded in the research log. The confirmatory version uses captures after registration.

**S4 (roster selection).** The vacate hazard of names on the Kalshi roster exceeds the population hazard of the same role classes in the same administration-year by a ratio of at least 1.5. Phase 1 quantity; requires the population panel.

**S5 (common shocks).** Departures in the US administration panel cluster: the administration-year frailty variance in M3 is bounded away from zero, and the distribution of 30-day departure counts is overdispersed relative to Poisson with the M1 rate. Determines the diversification haircut in Phase 6.

### Exploratory (labelled as such; never promoted)

Favorite–longshot shape across the whole price range; identity/"story" name effects using news intensity; maker-versus-taker fill economics; behaviour of prices after death-scalar settlements; the KXLEADERSOUT announce-or-vacate family, where the prior memo made no claim.

## 2. Sample definitions

Family, sub-families and rule variants are as in `family.py` and document 01. A market enters the calibration sample if it settled to YES or NO (not voided), was captured at least once in the relevant horizon bin, and its rule variant is classified (no `None` trigger). Markets whose rules text hash changed during their life are flagged and excluded from the primary test (reported separately). The evaluation period for the first confirmatory analysis is the set of markets settling between the registration date and 31 December 2027, examined at three fixed checkpoints (see §5).

## 3. Scoring rules and calibration diagnostics

Brier score $\mathrm{BS}=\frac1n\sum(p_m-Y_m)^2$ and log score $-\frac1n\sum[Y_m\log p_m+(1-Y_m)\log(1-p_m)]$ with prices clipped to $[0.01,0.99]$ (the exchange's own tick bounds), reported for the market mid, for each model rung, and for blends; Murphy decomposition of the Brier score into reliability, resolution and uncertainty with bins at the cut points $0.05,0.10,0.15,0.20,0.30,0.50,0.70$; reliability diagrams with block-bootstrap bands. Model-versus-market comparisons are paired differences on the same markets with dependence-aware standard errors (block bootstrap over administration × quarter blocks; 2,000 resamples; seed fixed in the script).

## 4. Holdout rules

Phase 1 hazard models are fit on administrations Reagan through Biden. The second Trump administration (from 20 Jan 2025) is the single holdout for the hazard-model ladder and is touched once, at the first checkpoint. For the market calibration study the holdout is temporal: nothing settling after the registration date is examined until a checkpoint. Exploratory work may use pre-registration captures freely.

## 5. Checkpoints and stopping rules

Analyses are run at 15 January 2027, 15 July 2027 and 15 January 2028, regardless of interim appearances. An interim look at H1 on 15 January 2027 (the 2026 annual cohort) uses an O'Brien–Fleming-type spending of α (0.005 at the first look, remainder at the final); the exact boundary is fixed in PAP-v1. No hypothesis is added or reworded after registration except by a dated amendment that explains why and is itself tagged. A negative result on H1 at the final checkpoint ends the "act on miscalibration" branch of the program; the modeling branch continues on its own merits.

## 6. Power

For H1 with $p_0=0.18$ (market) against $p_1=0.10$ (truth), a one-sample test of a proportion needs

$$n=\left[\frac{z_{1-\alpha/2}\sqrt{p_0(1-p_0)}+z_{1-\beta}\sqrt{p_1(1-p_1)}}{p_0-p_1}\right]^2 ,$$

which gives 158 markets two-sided (123 one-sided) at $\alpha=0.05$ and 80% power; at $p_0=0.15$ versus $0.09$ it is 246 (191). These are independent-observation counts. Names in the same administration-year share shocks; with $m$ names per cluster and intra-cluster correlation $\rho$ the design effect is $1+(m-1)\rho$, which is 1.6–2.5 for $m=30$ and $\rho\in[0.02,0.05]$, so the realistic requirement is roughly 250–400 market outcomes. The family currently yields on the order of 40 (KXTRUMPADMINLEAVE) + 35 (KXLEADERSOUT) + 10–15 (individual series) individual-market outcomes per year, of which only the vacate-rule subset (~55) enters H1. Consequences, stated now: H1 as written is underpowered for a single year and needs either three capture years or pooling across rule variants (which changes the estimand and must be pre-registered as such). The 15 January 2027 look is therefore an interim, not a decision.

| Cell | $p_0$ | $p_1$ | $n$ (two-sided) | $n$ (one-sided) | with design effect 2 |
|---|---:|---:|---:|---:|---:|
| Primary | 0.18 | 0.10 | 158 | 123 | 316 / 246 |
| Conservative | 0.15 | 0.09 | 246 | 191 | 492 / 382 |
| Alternative | 0.20 | 0.12 | 175 | 136 | 350 / 272 |

Replication: `uv run python scripts/power.py` (to be written in Phase 2; the numbers above were computed with the formula shown and the standard normal quantiles 1.960, 1.645, 0.842).

## 7. Sensitivity analyses (pre-specified)

Drop the current administration; drop scandal-driven events (coded ex ante by a rule on news intensity, not by hand); alternative role definitions (Brookings A-team versus Cabinet-only versus Senate-confirmed); mid versus last-trade versus microprice as the "market probability"; inclusion versus exclusion of markets with fewer than 500 contracts of volume; bins shifted by half a width.
