"""Rules texts from the Kalshi API on 2026-09-15 (UTC), used by tests/test_rules.py.

PROVENANCE CAVEAT (see docs/decision_log.md D010): these strings were transcribed through
a summarizing fetch tool, not copied from raw bytes, so they may differ from the API by
punctuation or a word. Re-pin them from the collector's first genuine raw capture with
`scripts/refresh_rules_fixtures.py`, then re-run the tests. If Kalshi later changes
wording, update here *and* record the change in the decision log; never loosen the
classifier to paper over it."""

EFFECTIVELEAVE_ADMIN = {
    "rules_primary": "If Steven Cheung leaves as White House Communications Director before 2027, then the market resolves to Yes.",
    "rules_secondary": ("Steven Cheung must have an actual departure date by vacating the role within the time period. "
        "If the person leaves the role due to death (i.e., if the person dies while holding the role), all contracts on the person may resolve to the last fair price as determined in the sole discretion of the Exchange. "
        "Temporary leaves of absence, suspensions, or recusals do not constitute leaving, resigning from, or retiring from the role unless the individual formally and permanently ceases to hold the position. "
        "If the person vacates the role and then re-occupies the role, the contract may settle on the initial vacation of the role. "
        "For 'leave,' cessation of holding the role qualifies, including resignation, retirement, removal, expiration of term without renewal, recall, or other means by which the individual no longer occupies the role—this includes both voluntary early departure AND the natural expiration of a term."),
}

HEGSETH = {
    "rules_primary": "If Pete Hegseth leaves as Secretary of Defense before Dec 1, 2026, then the market resolves to Yes.",
    "rules_secondary": ("Pete Hegseth must have an actual departure date and vacate the role within the time period. "
        "If the person leaves the role due to death (i.e., if the person dies while holding the role), all contracts on the person may resolve to the last fair price as determined in the sole discretion of the Exchange. "
        "Temporary leaves of absence, suspensions, or recusals do not constitute leaving, resigning from, or retiring from the role unless the individual formally and permanently ceases to hold the position. "
        "If the person vacates the role and then re-occupies the role, the contract may settle on the initial vacation of the role. "
        "For \"leave,\" cessation of holding the role qualifies, including resignation, retirement, removal, expulsion, expiration of term without renewal, recall, or other means by which the individual no longer occupies the role—this includes both voluntary and involuntary early departure AND the natural expiration of a term."),
}

LEADERSOUT = {
    "rules_primary": "If Sébastien Lecornu has either officially announced their intention to leave as Prime Minister of France or has actually left Prime Minister of France before Jan 1, 2027, then the market resolves to Yes.",
    "rules_secondary": ("An 'official announcement' means a statement by the person themselves, their authorized representative, or the official body governing the office that the person will be departing from the office. "
        "Such announcements must be reported by at least one Source Agency to be considered official. "
        "The announcement must not specify they are leaving in more than a year from the statement, in which case the market does not resolve to Yes. "
        "'Leaving office' means the person no longer holds the office in any capacity, including but not limited to: resignation (effective), termination, removal, impeachment and removal, recall, or the expiration of their term without renewal. "
        "Temporary absences such as medical leave, suspension with possibility of return, or delegation of duties while retaining the office do NOT constitute leaving office. "
        "Death does NOT satisfy the Payout Criterion for this Contract. Forced departures satisfy the Payout Criterion even without a prior announcement."),
}

CABOUT = {
    "rules_primary": "If Susie Wiles is the first member of the Cabinet of Donald Trump to leave or announce they will leave (such as by quitting, being fired, or being impeached) after May 22, 2026, then the market resolves to Yes.",
    "rules_secondary": ("If two persons announce they intend to leave at the same time, then the one who leaves first will resolve to Yes and all others will resolve to No. "
        "If multiple persons both announce they intend to leave and leave at the same time as other members, then the one whose last name is alphabetically first will resolve to Yes and all others will resolve to No. "
        "A leave of absence does not constitute leaving the position. "
        "For purposes of this Contract, the Cabinet includes the heads of the 15 government agencies in the Cabinet as of Issuance, as well the Administrator of the EPA, the President's Chief of Staff, Director of National Intelligence, Director of OMB, Director of CIA, United States Trade Representative, Ambassador to the UN, Chair of the Council of Economic Advisers, Administrator of the SBA, and Director of OSTP. "
        "Acting roles are not included. Leaving office as a result of death is not encompassed by the Payout Criterion."),
}

CABLEAVE = {
    "rules_primary": "If any member of Trump's Cabinet leaves their office, or announces they will leave their office, from before Jan 1, 2027, then the market resolves to Yes.",
    "rules_secondary": ("Any action related to Tulsi Gabbard will not qualify. The President announcing that a member of the Cabinet will leave the Cabinet also qualifies. "
        "For purposes of this Contract, the Cabinet includes the heads of the 15 government agencies in the Cabinet as of Issuance, as well the Administrator of the EPA, the President's Chief of Staff, Director of National Intelligence, Director of OMB, Director of CIA, United States Trade Representative, Ambassador to the UN, Chair of the Council of Economic Advisers, Administrator of the SBA, and Director of OSTP. "
        "Acting roles are not included. Leaving office as a result of death is not encompassed by the Payout Criterion."),
}

UKCABOUT = {
    "rules_primary": "If Yvette Cooper is the next to leave the Burnham Cabinet before Jan 1, 2028, then the market resolves to Yes.",
    "rules_secondary": ("A member leaves the Cabinet upon the qualifying announcement of their resignation, dismissal, removal, non-reappointment, or other formal cessation of Cabinet membership. "
        "A change of portfolio or position within the Cabinet alone does not count. "
        "If two or more members leave on the same calendar date and the Source Agencies do not establish a clear chronological order, the tied member markets settle according to the Contract's split-settlement provisions. "
        "If no eligible member leaves during the specified period, all member markets resolve to No. "
        "A temporary absence or leave where the member is expected to resume their Cabinet position does not count. "
        "Speculative or unconfirmed reports of a departure do not count. "
        "If the Prime Minister leaves office or the Cabinet is otherwise dissolved or wholly reconstituted before an individual member satisfies the Payout Criterion, all listed individual-member markets resolve to No."),
}

G7 = {
    "rules_primary": "If the individual holding the title of Prime Minister of Japan at the time of Issuance is the first within G7 leaders to leave their position, then the market resolves to Yes.",
    "rules_secondary": ("The individual must actually leave office and no longer hold their title. An announcement of resignation or intention to leave is not sufficient. "
        "In the event of death, the market will resolve to the last traded price prior to death, unless such a price is not available, not logically consistent, or not representative of a fair settlement value, in which case the Exchange may determine a fair value in its sole discretion."),
}

AFRICA = {
    "rules_primary": "If the President of Ghana is the first leader among the above to leave office, then the market resolves to Yes.",
    "rules_secondary": ("An announcement that a leader will leave their position is not sufficient to resolve the Payout Criterion; the individual must actually leave and no longer hold the title. "
        "If any leader leaves solely because they have died, then all markets will resolve and the Exchange will determine the payouts to the holders of long and short positions based upon the last traded price (prior to the death) or another fair price."),
}

ALITO = {
    "rules_primary": "If Samuel Alito retires as Supreme Court Justice before Jul 1, 2027, then the market resolves to Yes.",
    "rules_secondary": ("The resolution is based on the effective date of the resignation. If the person leaves the role due to death, all contracts may resolve to the last fair price as determined in the sole discretion of the Exchange. "
        "Temporary leaves of absence, suspensions, or recusals do not constitute leaving unless formally and permanently ceasing the position."),
}

THOMAS_ANNOUNCE = {
    "rules_primary": "If Clarence Thomas retires as Supreme Court justice before Jan 1, 2028, then the market resolves to Yes.",
    "rules_secondary": ("This market resolves based on when the departure is publicly announced or officially communicated, regardless of the effective date. "
        "If the person leaves the role due to death, all contracts on the person may resolve to the last fair price as determined in the sole discretion of the Exchange. "
        "Temporary leaves of absence, suspensions, or recusals do not constitute leaving, resigning from, or retiring from the role unless the individual formally and permanently ceases to hold the position. "
        "If the person vacates the role and then re-occupies the role, the contract may settle on the initial vacation of the role. "
        "For 'leave,' cessation of holding the role qualifies, including resignation, retirement, removal, expulsion, expiration of term without renewal, recall, or other means by which the individual no longer occupies the role—this includes both voluntary and involuntary early departure AND the natural expiration of a term."),
}

SCOTUSRESIGN = {
    "rules_primary": "If Ketanji Brown Jackson resigns or announces their intent to resign from the Supreme Court before Jan 20, 2029, then the market resolves to Yes.",
    "rules_secondary": "Death is not resignation and will not resolve a market to Yes.",
}

POWELL = {
    "rules_primary": "If Jerome Powell has either officially announced their intention to leave as Member of the Board of Governors of the Federal Reserve System or has actually left as Member of the Board of Governors of the Federal Reserve System before Jan 31, 2028, then the market resolves to Yes.",
    "rules_secondary": ("An acknowledgment that Jerome Powell will leave office due solely to the scheduled expiration of his legally mandated term limit does not resolve to Yes. "
        "The market resolves to Yes upon either an official announcement of departure or actual departure from office. "
        "An announcement must be made by the person themselves, their authorized representative, or the governing body of the office and reported by at least one Source Agency. "
        "Announcements of leaving more than one year from the statement do not resolve the market to Yes. "
        "Leaving office includes resignation, termination, removal, impeachment and removal, recall, or term expiration without renewal. "
        "Temporary absences such as medical leave, suspension with possibility of return, or delegation of duties while retaining office do NOT qualify. "
        "Death does NOT satisfy the Payout Criterion. Forced departures satisfy the criterion even without prior announcement."),
}

COOK = {
    "rules_primary": "If Lisa DeNell Cook leaves or announces that they will leave their position as Federal Reserve Governor before Jan 1, 2027, then the market resolves to Yes.",
    "rules_secondary": ("An announcement that they will leave office is sufficient to immediately resolve the market to Yes. "
        "However, the announcement must not specify they are leaving in more than a year from the statement, in which case the market does not resolve to Yes. "
        "Temporary absences such as medical leave, suspension with possibility of return, or delegation of duties while retaining the office do not count. "
        "Leaving office as a result of death will not count. Forced departures (termination, impeachment and removal, etc.) will count even without a prior announcement."),
}

WARSH = {
    "rules_primary": "If Kevin Warsh leaves as chairman of the Board of Governors of the Federal Reserve System before Jan 1, 2031, then the market resolves to Yes.",
    "rules_secondary": HEGSETH["rules_secondary"].replace("Pete Hegseth", "Kevin Warsh"),
}
