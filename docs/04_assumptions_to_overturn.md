# 04 — Assumptions in the preliminary evidence that the program must be able to overturn

Version 0.1, 15 September 2026. Source: the memo *Two Kalshi Families Most Likely to Be Mispriced* (15 Sep 2026), section 1. Each item names the assumption, why it might be false, and which part of the program tests it. Labels: **F** sourced fact, **E** estimate, **I** inference, **S** speculation.

**Plain-language summary.** The memo's case that departure markets overprice YES rests on about fifteen things being true that we have not checked: that departures arrive at a steady rate rather than in a year-end burst, that one year of one administration is a fair sample, that a quoted mid is what the crowd believes, that the counterparty is a hobbyist rather than a journalist, and so on. Each one is listed here with the test that could knock it down.

1. **Stationary hazard within the window (I).** The claim "implied hazard rose while the clock ran down" converts prices to hazards under a constant-hazard model. If the market believes the hazard is concentrated in November–January (post-midterm reshuffle), a flat price is rational and the "rising implied hazard" is an artefact of the wrong null. Today's KXHEGSETHOUT term structure shows a rising forward hazard (0.8, 1.0, 1.9 per year across the 1 Oct, 1 Nov, 1 Dec horizons), which is evidence the market holds such a belief. Tested by S2 against a calendar-varying benchmark and by Phase 1's estimate of the seasonal hazard profile from Reagan onward.

2. **The 2026 realized roster hazard of ~0.33/yr is the right comparator (E, biased).** The denominator counted 39 names for 8.5 months, but the roster grew during the year (the `-26JUN-` event cohort, e.g. Cheung, opened mid-year) so exposure is overstated and the hazard understated; conversely the early departures may have been the most exposed names. Tested by rebuilding exposure from each market's `open_time` on the data branch and by comparing with the population hazard in Phase 1.

3. **2018 is an analogue for 2026 (I/S).** One post-midterm window from one administration, with different personnel norms, is n = 1. Phase 1 estimates the post-midterm effect across all administrations since Reagan, separately for announcement and vacating.

4. **Survivorship in the price table (E, acknowledged in the memo).** The month-by-month mean-price table changes composition (29, 31, 32, 30 names). The analysis must be redone on a fixed cohort with per-name exposure; the seven early-2026 departures have outcomes and event times in `/historical/markets` even without prices.

5. **Mid-price equals crowd probability (I).** Spreads of 4–7¢ on 13–20¢ contracts, thin books (ask sizes of 1 contract were observed today), and last-trade fallbacks make the mid a noisy and possibly maker-set number. Sensitivity: mid versus last trade versus a size-weighted microprice; volume filters; and the maker-versus-taker question in Phase 6.

6. **Two departures priced gradually generalize (I, n = 2).** Blanche and Leavitt were repriced over weeks. Fired officials are repriced overnight. The realized-loss-path distribution needs every departure with price history from the data branch onward, split by exit cause.

7. **The YES buyer is a hobbyist, not a journalist (S).** The longshot mechanism presumes uninformed YES demand. Volume and open-interest dynamics before departures (tested by an event study on captured hourly data) can distinguish informed accumulation from noise; the additional-prohibitions clause is not enforcement.

8. **Sum-of-mids above one is longshot evidence (I).** Overround on a competing field is the maker's spread as much as the crowd's error; the memo itself notes there is no book arbitrage. The diagnostic is retained but is not evidence for H1.

9. **Departures are independent enough to diversify (S).** Administration-wide shake-ups are the common shock. S5 estimates the frailty variance; Phase 6 uses it, not an independence assumption.

10. **Fee model (F, dated).** Taker fee of 7% × P(1−P) per contract, rounded up to the cent, from the schedule PDF read on 15 Sep 2026; maker fees apply to an enumerated list that excludes this family. The PDF's own header says "effective July 1, 2025" while its filename and search title say July 2026, so the date must be confirmed by opening the file. Any economics uses the schedule in force on the trade date.

11. **The rule gap recurs (I).** December announcements with January effective dates are two historical cases. Phase 1 estimates the announce-to-vacate lag distribution by month and role class.

12. **The Exchange settles per the text (F with discretion).** "May resolve to the last fair price" and "may settle on the initial vacation" are discretionary. The data branch will accumulate settled examples; voided and disputed settlements are tracked as an outcome category.

13. **The window and the trading window coincide (F, they do not).** Trading closes one day before the window ends. A departure on 31 December settles YES with no one able to trade it. Small, but it belongs in the horizon arithmetic.

14. **Vacate and announce rules are the only two variants (F, false).** The live family has at least four (vacate; announce-or-vacate; announce; competing/any-member forms with tie-breaks, carve-outs and voiding clauses). Document 01 fixes them; the classifier pins them.

15. **The market's prices are the same object over time (I).** Kalshi added names mid-year, carved out Gabbard from KXCABLEAVE, and may edit rules text. `rules_sha256` and per-market `open_time` on every row make roster and rule changes visible.

16. **The counterparty is on the other side of the same rule (S).** A YES buyer reacting to a December headline may be hedging an announce-rule position elsewhere (KXCABLEAVE, KXLEADERSOUT-style) rather than misreading the vacate rule. Cross-series holdings are unobservable, but S3 tests whether the two contract types are priced coherently.

17. **The family will still exist in a year (S).** Kalshi retires and renames series. Discovery in the daily job and the candidate registry exist because the population of markets is itself non-stationary.
