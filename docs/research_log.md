# Research log

Dated observations, labelled **F** (sourced fact), **E** (estimate with uncertainty), **I** (inference), **S** (speculation). Exploratory observations here are never promoted to confirmatory findings.

## 2026-09-15

**F — Archived YES markets carry the event timestamp.** On `/markets?status=settled` and `/historical/markets`, a market that settled YES has `close_time` equal to the early-close moment: Bongino 2026-01-04T23:26:09Z, Bovino 2026-02-03T17:16:49Z, Noem 2026-03-24T18:25:07Z, Sacks 2026-03-26T21:15:44Z, Bondi 2026-04-07T18:17:20Z, Chavez-DeRemer 2026-04-21T20:13:42Z, Gabbard 2026-06-19T14:08:45Z, Blanche 2026-08-10T19:06:35Z, Leavitt 2026-08-28T16:50:07Z, with `settlement_ts` about 30 minutes later. This is the Exchange's own determination of when the settlement-defined event occurred, to the second, and it survives archiving. It is the natural ground truth for the *market's* event and can be compared with primary-source effective dates to measure how the Exchange reads "actual departure date".

**F — Two issue cohorts in KXTRUMPADMINLEAVE.** Event tickers `KXTRUMPADMINLEAVE-26DEC31` (opened around the start of the year) and `KXTRUMPADMINLEAVE-26JUN` (e.g. Cheung, `open_time` 2026-06-20) coexist. Exposure for any roster hazard must start at each market's `open_time`. The memo's 39-names-for-8.5-months denominator is therefore too large (I): the true 2026 roster hazard is above 0.33/yr by an amount to be computed from the captured `open_time`s.

**F — KXCABLEAVE carves out Tulsi Gabbard** ("Any action related to Tulsi Gabbard will not qualify"), although the series' `last_updated_ts` is 2026-06-01 and Gabbard's KXTRUMPADMINLEAVE market closed YES on 2026-06-19. Reading (I): Kalshi excludes a member whose departure was already announced or expected at issuance, so the "any member" contract is an announce-or-vacate contract on the *not-yet-announced* roster. This matters for S3.

**E — Term structures on 15 Sep 2026 (mids; days to window end from today).** Implied constant hazards $-\log(1-p)/\tau$, annualized:

| Market | Window end | Days | Mid | Implied hazard /yr |
|---|---|---:|---:|---:|
| KXHEGSETHOUT | 1 Oct 2026 | 16 | 0.035 | 0.81 |
| KXHEGSETHOUT | 1 Nov 2026 | 47 | 0.115 | 0.95 |
| KXHEGSETHOUT | 1 Dec 2026 | 77 | 0.245 | 1.33 |
| KXKASHOUT | 1 Nov 2026 | 47 | 0.055 | 0.44 |
| KXKASHOUT | 1 Dec 2026 | 77 | 0.110 | 0.55 |
| KXCABLEAVE (any of ~25, announce-or-vacate) | 1 Oct 2026 | 16 | 0.195 | 4.95 (aggregate) |
| KXCABLEAVE | 1 Nov 2026 | 47 | 0.340 | 3.23 (aggregate) |
| KXCABLEAVE | 1 Jan 2027 | 108 | 0.560 | 2.78 (aggregate) |
| KXTRUMPADMINLEAVE Cheung | 1 Jan 2027 | 108 | 0.125 | 0.45 |
| KXTRUMPADMINLEAVE R. Scott | 1 Jan 2027 | 108 | 0.160 | 0.59 |

Hegseth's forward hazards are 0.81/yr (now–1 Oct), 1.02/yr (1 Oct–1 Nov) and 1.93/yr (1 Nov–1 Dec): the market prices a hazard that roughly doubles after the 3 November midterm. This is directly relevant to assumption 1 in document 04: the flat annual prices the memo interpreted as stickiness are consistent with a deliberate late-window belief. Whether that belief is *right* is a separate question (Phase 1 seasonal profile).

**I — Cross-contract tension.** KXCABLEAVE "before 1 Jan 2027" at 0.56 says the probability that none of ~25 Cabinet-defined offices sees a qualifying announcement or departure by year-end is 0.44. Four cabinet-level names in KXTRUMPADMINLEAVE (Ratcliffe, Burgum, Collins, Loeffler per the memo) at roughly 0.17 each give, under independence, a probability of no *vacating* among just those four of $0.83^4=0.47$, under a *narrower* rule (vacate only) and a smaller set. Reconciling the two requires either strong positive dependence (a shake-up either happens to several at once or not at all) or one side being mispriced. This is the seed of hypothesis S3 and is exploratory; the full roster mapping to Cabinet-defined offices is needed before it is quantified, and the captures from today onward are the confirmatory sample. Note the direction: if the individual YES prices are too high (the memo's story), KXCABLEAVE is the contract whose price is closer to the truth, and a NO basket on individuals is partly hedged by YES on the any-member contract only if the dependence structure is what makes them coherent.

**F — API coverage.** KXSTARMERCABLEAVE returns no open and no settled markets (archived; the UK cabinet field is now `KXUKCABOUT-BURNN28JAN01-*`, "the Burnham Cabinet"). KXG7LEADEROUT and KXAFRICALEADEROUT expire 2045 and 2035 respectively; their sums of mids are near 1 by construction and they are competing-risk fields with a death-voids-all clause.

**F — Fee schedule.** See decision D008. Taker 0.07·C·P(1−P) rounded up to the next cent; maker 0.0175·C·P(1−P) only on an enumerated list that contains no tenure series.

**S — Collector priorities.** The two individual monthly series (Hegseth, Kash) give a term structure every day; combined with the annual contract they let us read the market's implied calendar hazard profile continuously. That is the cheapest possible test of the stickiness story and needs no outcome data at all; it should be the first exploratory figure once a month of captures exists.
