"""Rule-variant classification from a market's ``rules_primary`` / ``rules_secondary``.

The settlement criterion is never inferred from the title. This module reads the
rules text and emits a ``RuleVariant`` record that becomes a field on every market
row in the panel. The classifier is deliberately phrase-based and conservative:
when a phrase is absent the field is ``None`` (unknown), never a guess. Unit tests in
``tests/test_rules.py`` pin the classification of every rules text captured on
2026-09-15, so a wording change on Kalshi's side breaks a test instead of silently
changing an estimand.

Fields
------
trigger              "vacate" | "announce_or_vacate" | "announce" | None
competing            True for "first / next to leave" fields (mutually exclusive names)
any_member           True for "any member of X leaves" contracts
death_not_yes        death does not satisfy the payout criterion
death_scalar         death -> contracts settle at last fair/traded price (Exchange discretion)
acting_excluded      acting office-holders are not in the set
temp_absence_excluded
one_year_cap         announcement must not name a date > 1 year out
term_expiration_counts   natural expiry of a term counts as leaving
term_limit_ack_excluded  acknowledging a term-limit expiry does not count (LEAVEOFFICE)
forced_departure_counts  forced departures count without announcement
reoccupy_settles_initial re-occupying after vacating: settles on initial vacation
president_announcement_counts  President's announcement about a member counts
tie_break            "leave_first_then_alpha" | "split_settlement" | None
field_void_on_head_change  all member markets NO if PM leaves / cabinet reconstituted
excluded_persons     tuple of names carved out ("Any action related to X will not qualify")
window_start / window_end   ISO dates parsed from rules_primary ("after May 22, 2026",
                     "before Jan 1, 2027", "before 2027"); None if not found
rules_sha256         hash of primary + "\n" + secondary, to detect wording changes
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import asdict, dataclass
from datetime import date

_MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], start=1)}

_DATE_RE = re.compile(r"\b([A-Za-z]{3,9})\.?\s+(\d{1,2}),\s*(\d{4})\b")
_YEAR_ONLY_RE = re.compile(r"\bbefore\s+(\d{4})\b")


def _parse_date(s: str) -> date | None:
    m = _DATE_RE.search(s)
    if not m:
        return None
    mon = _MONTHS.get(m.group(1)[:3].lower())
    if not mon:
        return None
    try:
        return date(int(m.group(3)), mon, int(m.group(2)))
    except ValueError:
        return None


def _has(text: str, *phrases: str) -> bool:
    t = text.lower()
    return any(p.lower() in t for p in phrases)


@dataclass(frozen=True)
class RuleVariant:
    trigger: str | None
    competing: bool
    any_member: bool
    death_not_yes: bool
    death_scalar: bool
    acting_excluded: bool
    temp_absence_excluded: bool
    one_year_cap: bool
    term_expiration_counts: bool
    term_limit_ack_excluded: bool
    forced_departure_counts: bool
    reoccupy_settles_initial: bool
    president_announcement_counts: bool
    tie_break: str | None
    field_void_on_head_change: bool
    excluded_persons: tuple[str, ...]
    window_start: str | None
    window_end: str | None
    rules_sha256: str

    def as_dict(self) -> dict:
        d = asdict(self)
        d["excluded_persons"] = list(self.excluded_persons)
        return d


def classify(rules_primary: str, rules_secondary: str) -> RuleVariant:
    p = rules_primary or ""
    s = rules_secondary or ""
    both = p + "\n" + s

    # --- trigger ---------------------------------------------------------------
    trigger: str | None = None
    if _has(s, "based on when the departure is publicly announced",
            "upon the qualifying announcement of their resignation"):
        trigger = "announce"
    elif _has(p, "either officially announced", "leaves or announces", "leave or announce",
              "resigns or announces", "announces they will leave", "or announces they will leave",
              "or announce they will leave", "announce their intent"):
        trigger = "announce_or_vacate"
    elif _has(s, "must have an actual departure date", "must actually leave office",
              "individual must actually leave", "based on the effective date",
              "announcement of resignation or intention to leave is not sufficient",
              "announcement that a leader will leave their position is not sufficient"):
        trigger = "vacate"
    elif _has(s, "an announcement that they will leave office is sufficient"):
        trigger = "announce_or_vacate"

    competing = _has(p, "is the first", "is the next to leave", "first to leave", "leave office next",
                     "the first within", "first leader among")
    any_member = _has(p, "any member")

    # --- death -----------------------------------------------------------------
    death_not_yes = _has(both, "death does not satisfy", "death is not resignation",
                         "death is not encompassed", "as a result of death will not count",
                         "as a result of death is not encompassed")
    death_scalar = _has(both, "resolve to the last fair price", "last traded price prior to death",
                        "last traded price (prior to the death)", "settle the contract at the last traded price")

    acting_excluded = _has(both, "acting roles are not included")
    temp_absence_excluded = _has(both, "temporary leaves of absence", "temporary absences",
                                 "temporary absence or leave", "leave of absence does not constitute")
    one_year_cap = _has(both, "more than a year from the statement", "more than one year from the statement")
    term_expiration_counts = _has(both, "natural expiration of a term", "expiration of term without renewal",
                                  "expiration of their term without renewal", "term expiration without renewal")
    term_limit_ack_excluded = _has(both, "due solely to the scheduled expiration",
                                   "solely to the scheduled expiration of")
    forced_departure_counts = _has(both, "forced departures satisfy", "forced departures (termination")
    reoccupy_settles_initial = _has(both, "re-occupies the role")
    president_announcement_counts = _has(both, "the president announcing that a member")

    tie_break: str | None = None
    if _has(s, "alphabetically first"):
        tie_break = "leave_first_then_alpha"
    elif _has(s, "split-settlement", "split settlement"):
        tie_break = "split_settlement"

    field_void_on_head_change = _has(s, "all listed individual-member markets resolve to no")

    excluded_persons = tuple(
        m.group(1).strip() for m in re.finditer(r"any action related to ([A-Z][A-Za-z.'\- ]+?) will not qualify", s, re.IGNORECASE)
    )

    # --- window ------------------------------------------------------------------
    window_start: str | None = None
    window_end: str | None = None
    m_after = re.search(r"\bafter\s+([A-Za-z]{3,9}\.?\s+\d{1,2},\s*\d{4})", p)
    if m_after:
        d = _parse_date(m_after.group(1))
        window_start = d.isoformat() if d else None
    m_before = re.search(r"\bbefore\s+([A-Za-z]{3,9}\.?\s+\d{1,2},\s*\d{4})", p)
    if m_before:
        d = _parse_date(m_before.group(1))
        window_end = d.isoformat() if d else None
    else:
        m_year = _YEAR_ONLY_RE.search(p)
        if m_year:
            window_end = date(int(m_year.group(1)), 1, 1).isoformat()

    digest = hashlib.sha256(both.encode("utf-8")).hexdigest()

    return RuleVariant(
        trigger=trigger,
        competing=competing,
        any_member=any_member,
        death_not_yes=death_not_yes,
        death_scalar=death_scalar,
        acting_excluded=acting_excluded,
        temp_absence_excluded=temp_absence_excluded,
        one_year_cap=one_year_cap,
        term_expiration_counts=term_expiration_counts,
        term_limit_ack_excluded=term_limit_ack_excluded,
        forced_departure_counts=forced_departure_counts,
        reoccupy_settles_initial=reoccupy_settles_initial,
        president_announcement_counts=president_announcement_counts,
        tie_break=tie_break,
        field_void_on_head_change=field_void_on_head_change,
        excluded_persons=excluded_persons,
        window_start=window_start,
        window_end=window_end,
        rules_sha256=digest,
    )
