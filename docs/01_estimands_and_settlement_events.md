# 01 — Estimands and settlement-defined events

Version 0.1, 15 September 2026. Rules text was read from the live API (`rules_primary`, `rules_secondary` on each market object) and from the contract-terms PDFs linked by `contract_terms_url` on the series object, on 15 Sep 2026 (UTC). Every rules string quoted or classified here is pinned verbatim in `tests/fixtures_rules.py`, and `ptm.parse.rules.classify` reproduces the classification in the table below; a wording change on Kalshi's side fails a test rather than silently changing an estimand.

**Plain-language summary.** A Kalshi departure contract does not pay on "the person is out" in the everyday sense; it pays on a rule-specific event that differs across series. Some series pay when the person actually vacates the role (an announced departure with a later effective date does not count until that date), some pay on the earlier of an official announcement or the departure, and some pay on the announcement alone regardless of effective date. Death is excluded in every series, but in some it voids the contract at a discretionary price rather than paying NO. The "next to leave" and "any member leaves" contracts are functions of the whole roster, not of one person. This document fixes, per series, what the event is and what probability we are trying to estimate.

## 1. Notation

Index persons by $i$, roles by $r$, and a person–role spell by $(i,r)$ with start date $s_{ir}$. Each spell has up to three latent exit times, measured in calendar days:

$$T^{\mathrm{ann}}_{ir},\qquad T^{\mathrm{vac}}_{ir},\qquad T^{\mathrm{die}}_{ir},$$

the first qualifying official announcement of departure, the effective date of vacating the role, and death in office. Always $T^{\mathrm{ann}}_{ir}\le T^{\mathrm{vac}}_{ir}$, with equality when the departure is immediate (fired, resigned effective immediately). The lag $L_{ir}=T^{\mathrm{vac}}_{ir}-T^{\mathrm{ann}}_{ir}$ is a modeled quantity with an atom at zero.

A market $m$ is a tuple (series $s$, person or roster $R_m$, window $(a_m,b_m]$, rule variant $v_s$). Its settlement is a random variable $Y_m\in\{0,1\}$ or, for death and Exchange-discretion outcomes, a scalar $Y_m\in[0,1]$ that we treat as a third outcome category $\varnothing$ ("voided"). Prices are observed at capture times $t$; $p_{m,t}$ denotes the YES mid, $p^{b}_{m,t}$ and $p^{a}_{m,t}$ the best bid and ask, and $\tau_{m,t}=b_m-t$ the remaining horizon.

Two hazards are distinguished throughout: $\lambda^{\mathrm{ann}}_{ir}(u)$ and $\lambda^{\mathrm{vac}}_{ir}(u)$, the instantaneous rates of announcement and of vacating at calendar time $u$. Death is a competing risk with its own hazard $\lambda^{\mathrm{die}}$; it is never dropped from the panel.

## 2. Settlement event by series

The rule variant $v_s$ has the fields defined in `ptm.parse.rules.RuleVariant`. The table gives the classification of the live text; the prose that follows gives the event as a formula.

| Series | Trigger | Roster type | Death | Acting excluded | 1-yr cap | Term expiry counts | Window (live example) | Terms PDF |
|---|---|---|---|---|---|---|---|---|
| KXTRUMPADMINLEAVE | vacate | individual | scalar (Exchange discretion) | n/a | no | yes | before 2027 | EFFECTIVELEAVE |
| KXHEGSETHOUT, KXKASHOUT | vacate | individual | scalar | n/a | no | yes | before 1 Oct / 1 Nov / 1 Dec 2026 | EFFECTIVELEAVE (by text) |
| KXWARSHOUT | vacate | individual | scalar | n/a | no | yes | before 1 Jan 2030 / 2031 | EFFECTIVELEAVE (by text) |
| KXALITOOUT | vacate ("effective date of the resignation") | individual | scalar | n/a | no | not stated | before 1 Jan 2027 / 1 Jul 2027 | EFFECTIVELEAVE |
| KXTHOMASANNOUNCERETIRE | announce ("regardless of the effective date") | individual | scalar | n/a | no | yes | before 1 Jul 2027 / 1 Jan 2028 | not fetched |
| KXSCOTUSRESIGN | announce-or-vacate | individual | not YES | n/a | no | not stated | before 20 Jan 2029 | not fetched |
| KXLEADERSOUT | announce-or-vacate | individual | not YES (market text); PDF: last fair price | n/a | yes | yes; term-limit acknowledgement excluded | before 1 Jan 2027 | LEAVEOFFICE |
| KXLEAVEPOWELLGOV | announce-or-vacate | individual | not YES | n/a | yes | yes; term-limit acknowledgement excluded | before 1 Jun 2027 / 31 Jan 2028 | LEAVEOFFICE |
| KXLEAVELISACOOK | announce-or-vacate | individual | not YES | n/a | yes | not stated | before 1 Jan 2027 | not fetched |
| KXCABOUT | announce-or-vacate, first in set | competing (25 defined offices) | not YES | yes | no | not stated | after 22 May 2026, expires 20 Jan 2029 | CABOUT |
| KXCABLEAVE | announce-or-vacate, any in set; President's announcement counts | any-member (same 25 offices); Gabbard carved out | not YES (market text); PDF: last traded price at discretion | yes | no | not stated | before 1 Oct 2026 / 1 Nov 2026 / 1 Jan 2027 | CABLEAVE |
| KXUKCABOUT | announce ("upon the qualifying announcement") | competing (Burnham Cabinet) | not stated | not stated | no | not stated | before 1 Jan 2028; all NO if PM leaves | not fetched |
| KXG7LEADEROUT | vacate, first in set | competing (G7 incumbents at issuance) | scalar for all markets | n/a | no | not stated | until 1 Jan 2045 | not fetched |
| KXAFRICALEADEROUT | vacate, first in set | competing | scalar for all markets | n/a | no | not stated | until 1 Jan 2035 | not fetched |

Two discrepancies between the API market text and the PDF are recorded and must be carried as a data field rather than resolved by assumption. For KXLEADERSOUT the market text says "Death does NOT satisfy the Payout Criterion" while LEAVEOFFICE.pdf says that upon death "all Contracts on <person> will resolve to the last fair price"; the two are consistent only under the reading that death never produces YES but does produce a discretionary scalar settlement, which is also what the prior survey observed (one death-settled "scalar" market in KXLEADERSOUT). The same pattern holds for KXCABLEAVE (market text: not encompassed; PDF: Kalshi "may, in its sole discretion, settle the Contract at the last traded price"). Until a settled example confirms which applies, both flags are stored (`death_not_yes`, `death_scalar`) and death outcomes are excluded from the binary calibration sample as a pre-specified rule.

**Individual, vacate rule (EFFECTIVELEAVE family).** With window $(a_m,b_m]$,
$$Y_m=\mathbf 1\{T^{\mathrm{vac}}_{ir}\in(a_m,b_m],\ T^{\mathrm{die}}_{ir}>T^{\mathrm{vac}}_{ir}\},\qquad Y_m=\varnothing \text{ if } T^{\mathrm{die}}_{ir}\le \min(T^{\mathrm{vac}}_{ir},b_m).$$
Natural expiration of a term counts as vacating (this is why KXWARSHOUT "before 2031" trades at 76–82¢: a four-year chair term beginning in 2026 ends before that date). Temporary leave, suspension and recusal are not exits. The market closes for trading one day before the window ends (e.g. `close_time` 2026-12-31T04:59Z for "before 2027"), so a departure on the last calendar day of the window settles YES but cannot be traded on.

**Individual, announce-or-vacate rule (LEAVEOFFICE family).** Define the qualifying announcement time $T^{\mathrm{ann}*}_{ir}$ as the first announcement by the person, an authorized representative, or the governing body, reported by a Source Agency, that names a departure not more than one year out and is not merely an acknowledgement of a scheduled term-limit expiry. Then
$$Y_m=\mathbf 1\{\min(T^{\mathrm{ann}*}_{ir},T^{\mathrm{vac}}_{ir})\in(a_m,b_m]\},$$
with death producing NO-or-scalar as flagged. The gap between this and the vacate rule is exactly the event $\{T^{\mathrm{ann}*}\le b_m<T^{\mathrm{vac}}\}$, an announcement inside the window with an effective date outside it. That event is the object of the rule-gap hypothesis.

**Individual, announce rule (KXTHOMASANNOUNCERETIRE, KXUKCABOUT).** $Y_m=\mathbf 1\{T^{\mathrm{ann}}_{ir}\in(a_m,b_m]\}$ regardless of effective date; note that Thomas's `rules_primary` says "retires" while `rules_secondary` says the announcement governs, so the title and primary text would mislead.

**Competing "first to leave" fields (KXCABOUT, KXG7LEADEROUT, KXAFRICALEADEROUT, KXUKCABOUT).** For roster $R$ and per-member event times $T_j$ under the series' trigger, $Y_{m_j}=\mathbf 1\{T_j=\min_{k\in R}T_k,\ T_j\le b\}$, with the stated tie-break (leave-first then alphabetical for KXCABOUT; split settlement for KXUKCABOUT). The roster is defined by office, not by name: KXCABOUT and KXCABLEAVE list 15 department heads plus ten further offices, exclude acting holders, and (for KXCABOUT) a successor who later leaves is not the "first" if a predecessor already triggered. The field is mutually exclusive by construction, so $\sum_j P(Y_{m_j}=1)\le 1$ with equality when some member leaves before $b$; for the G7 and Africa fields with 2035–2045 horizons the sum is essentially 1 and a member's death voids every market in the set at a discretionary price.

**Any-member contracts (KXCABLEAVE).** $Y_m=\mathbf 1\{\min_{k\in R\setminus E}\min(T^{\mathrm{ann}*}_k,T^{\mathrm{vac}}_k)\in(a_m,b_m]\}$ where $E$ is the carve-out set (currently Tulsi Gabbard) and an announcement by the President about member $k$ counts as $k$'s announcement. This contract is a function of the joint distribution of the roster's event times and is where dependence across names is directly priced.

## 3. Estimands

The program estimates four kinds of quantity. Each is defined here before any estimator is chosen.

**E1 (calibration).** For a rule variant $v$, horizon bin $h$ and price bin $B$,
$$\pi(v,h,B)=\mathbb E\big[Y_m\ \big|\ p_{m,t}\in B,\ \tau_{m,t}\in h,\ v_s=v,\ Y_m\ne\varnothing\big],\qquad \delta(v,h,B)=\pi(v,h,B)-\mathbb E[p_{m,t}\mid \cdot].$$
The expectation is over market–capture pairs in a declared evaluation period; the sampling unit for inference is the market (one capture per market per horizon bin, chosen by a fixed rule, e.g. the first capture with $\tau\in h$), and standard errors respect dependence through blocks by calendar quarter and by administration. Voided outcomes are excluded; that exclusion is itself reported.

**E2 (hazards).** For role class $c$ and calendar covariates $x$,
$$\lambda^{\mathrm{vac}}_c(u\mid x),\quad \lambda^{\mathrm{ann}}_c(u\mid x),\quad F_L(\ell\mid c,\text{month of announcement}),$$
the cause-specific vacate and announcement hazards and the announce-to-vacate lag distribution. From these, the model-implied probability of the settlement event for any market is a functional: for the vacate rule, $P(Y_m=1)=\int_{a_m}^{b_m}\lambda^{\mathrm{vac}}(u)\,S(u)\,du$ where $S$ is the all-cause survival; for the announce-or-vacate rule the integrand uses the announcement hazard plus the immediate-departure component. Two populations are distinguished: the Kalshi roster (names Kalshi chose to list) and the population of office-holders. Selection into the roster, $\Pr(i\in R_s\mid x_i)$, is a modeled quantity; the traded estimand is the roster hazard, and the population hazard is its prior.

**E3 (market implied hazard and its dynamics).** Under a constant-hazard reading, $\hat\lambda_{m,t}=-\log(1-p_{m,t})/\tau_{m,t}$. The stickiness estimand is the slope $\beta$ in $\mathbb E[\log\hat\lambda_{m,t}\mid \tau_{m,t}]$ as a function of $\log\tau_{m,t}$ within a market, compared with the slope implied by a calibrated model that allows calendar-varying hazard. The comparison against a calendar-varying benchmark, not against a constant, is essential: a flat price against a shrinking horizon is rational if the market believes the hazard is concentrated late in the window (the post-midterm reshuffle), and today's KXHEGSETHOUT term structure shows exactly that belief (forward hazards of roughly 0.8, 1.0 and 1.9 per year over the 1 Oct, 1 Nov and 1 Dec horizons; see the research log for the arithmetic).

**E4 (after-cost economics).** For a pre-specified rule $\rho$ mapping the information set at $t$ to a position, the expected log growth per unit time under a stated dependence model and the quoted side of the book plus fee, with the loss path (slow repricing on public news) and the tail (overnight jump) reported separately. Fee model as of the schedule read on 15 Sep 2026: taker fee $\lceil 0.07\,C\,P(1-P)\rceil$ rounded up to the next cent; maker fees $\lceil 0.0175\,C\,P(1-P)\rceil$ apply only to an enumerated list of series on which none of this family appears, so resting orders in this family currently pay no fee (to be confirmed by a live fill; see the decision log for the date discrepancy on the schedule).

## 4. What is deliberately not an estimand

"Whether the person will be out" in the colloquial sense; the probability that a name appears in the news; anything conditioned on information not public at $t$. The information set at capture time $t$ is the set of raw captures with `capture_ts` $\le t$ plus ground-truth sources with publication dates $\le t$; every feature must be computable from that set alone.
