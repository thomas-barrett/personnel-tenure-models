"""The personnel-tenure family: which series the collector captures, and how new
series are discovered.

Two tiers:

* ``REGISTRY``   — series known on 2026-09-15 (from the niche-selection survey and
                   a targeted catalogue query), with a hand-assigned sub-family and
                   the contract-terms template we observed. Always captured.
* discovery     — the daily job scans the whole ``/series`` catalogue and flags any
                   ticker or title matching ``CANDIDATE_RE`` that is not in the
                   registry. Candidates are captured too (capture is cheap and history
                   is lost otherwise) but are tagged ``tier="candidate"`` until a human
                   promotes them into the registry with a sub-family label.

Sub-family labels (used later as strata / role classes):

  us_admin_individual   "X out as Y before date" (vacate rule)      e.g. KXTRUMPADMINLEAVE
  us_admin_next         competing "next Cabinet member to leave"    e.g. KXCABOUT
  us_admin_any          "any Cabinet member leaves before date"     e.g. KXCABLEAVE
  us_admin_successor    "next Secretary of X" (who replaces)        e.g. KXNEXTDEF
  world_leader          heads of government/state, annual           e.g. KXLEADERSOUT
  world_leader_next     competing fields (G7, Africa, LatAm)        e.g. KXG7LEADEROUT
  uk_cabinet            UK cabinet next-to-leave / any-leave         e.g. KXUKCABOUT
  scotus                justices                                    e.g. KXALITOOUT
  fed                   Federal Reserve governors/chair              e.g. KXLEAVEPOWELLGOV
  corporate_ceo         CEO change markets                           e.g. TESLACEOCHANGE
  other_official        other named officials                        e.g. KXLEAVETISCH
"""

from __future__ import annotations

import re
from dataclasses import dataclass


@dataclass(frozen=True)
class SeriesSpec:
    ticker: str
    subfamily: str
    terms_template: str | None = None  # basename of contract_terms_url observed, if known
    note: str = ""


REGISTRY: tuple[SeriesSpec, ...] = (
    # US administration
    SeriesSpec("KXTRUMPADMINLEAVE", "us_admin_individual", "EFFECTIVELEAVE.pdf", "annual roster; vacate rule"),
    SeriesSpec("KXHEGSETHOUT", "us_admin_individual", "EFFECTIVELEAVE.pdf", "monthly horizons"),
    SeriesSpec("KXKASHOUT", "us_admin_individual", "EFFECTIVELEAVE.pdf", "monthly horizons"),
    SeriesSpec("KXMILLEROUT", "us_admin_individual", None, "found in catalogue 2026-09-15; rules unread"),
    SeriesSpec("KXCABOUT", "us_admin_next", "CABOUT.pdf", "first to leave or announce after 22 May 2026"),
    SeriesSpec("KXCABCHANGE", "us_admin_any", None, "found in catalogue 2026-09-15; rules unread"),
    SeriesSpec("KXCABLEAVE", "us_admin_any", "CABLEAVE.pdf", "any member leaves/announces before month"),
    SeriesSpec("KXNEXTDEF", "us_admin_successor", None),
    SeriesSpec("KXNEXTLABORSEC", "us_admin_successor", None),
    SeriesSpec("KXNEXTPRESSEC", "us_admin_successor", None),
    SeriesSpec("KXNEXTLEGAFFAIRS", "us_admin_successor", None),
    SeriesSpec("KXNEXTSECARMY", "us_admin_successor", None),
    SeriesSpec("KXNEXTJUDICIARYCHAIR", "us_admin_successor", None),
    SeriesSpec("KXOSTP", "us_admin_successor", None),
    SeriesSpec("KXDIROSTP", "us_admin_successor", None),
    SeriesSpec("CEA", "us_admin_successor", None),
    SeriesSpec("KXSECCHAIR", "us_admin_successor", None),
    # World leaders
    SeriesSpec("KXLEADERSOUT", "world_leader", "LEAVEOFFICE.pdf", "announce-or-leave rule; death not YES"),
    SeriesSpec("KXG7LEADEROUT", "world_leader_next", None, "vacate rule; death -> scalar for all"),
    SeriesSpec("KXAFRICALEADEROUT", "world_leader_next", None, "vacate rule; death -> scalar for all"),
    SeriesSpec("KXLALEADEROUT", "world_leader_next", None, "found in catalogue 2026-09-15; rules unread"),
    # UK
    SeriesSpec("KXUKCABOUT", "uk_cabinet", None, "announcement-triggered; all NO if PM leaves"),
    SeriesSpec("KXSTARMERCABLEAVE", "uk_cabinet", None, "no open or settled markets on 2026-09-15; likely archived"),
    # SCOTUS
    SeriesSpec("KXALITOOUT", "scotus", "EFFECTIVELEAVE.pdf", "effective date of resignation governs"),
    SeriesSpec("KXTHOMASANNOUNCERETIRE", "scotus", None, "announcement date governs"),
    SeriesSpec("KXSCOTUSRESIGN", "scotus", None, "resign or announce before 20 Jan 2029"),
    # Fed
    SeriesSpec("KXLEAVEPOWELLGOV", "fed", "LEAVEOFFICE.pdf", "announce-or-leave; term-limit acknowledgement excluded"),
    SeriesSpec("KXLEAVELISACOOK", "fed", None, "announce-or-leave"),
    SeriesSpec("KXWARSHOUT", "fed", None, "vacate rule; natural term expiration counts"),
    # Corporate
    SeriesSpec("TESLACEOCHANGE", "corporate_ceo", None),
    SeriesSpec("OPENAICEOCHANGE", "corporate_ceo", None),
    SeriesSpec("KXOPENAICEO", "corporate_ceo", None),
    SeriesSpec("XCEOCHANGE", "corporate_ceo", None),
    SeriesSpec("NPRCEOCHANGE", "corporate_ceo", None),
    # Other officials
    SeriesSpec("KXLEAVETISCH", "other_official", None),
)

REGISTRY_TICKERS: frozenset[str] = frozenset(s.ticker for s in REGISTRY)

# Discovery pattern applied to ticker and title (case-insensitive). Deliberately broad;
# false positives cost a few API calls, false negatives cost history.
CANDIDATE_RE = re.compile(
    r"(OUT\b|LEAVE|LEAVING|RESIGN|RETIRE|DEPART|FIRED|IMPEACH|REMOV|STEP\s*DOWN|STEPDOWN|"
    r"CEO|CHANGE|NEXT\s+(SEC|CHAIR|DIRECTOR|PRIME|PRESIDENT|LEADER|MEMBER)|CABINET|CABOUT|LEADEROUT)",
    re.IGNORECASE,
)

# Tickers that match the pattern but are known NOT to be tenure markets. Keep short and
# justified; everything else that matches gets captured as a candidate.
EXCLUDE_TICKERS: frozenset[str] = frozenset({
    "FEMALECEO",       # count/threshold market on female CEOs, not a departure market
})


def is_candidate(ticker: str, title: str) -> bool:
    if ticker in REGISTRY_TICKERS or ticker in EXCLUDE_TICKERS:
        return False
    return bool(CANDIDATE_RE.search(ticker) or CANDIDATE_RE.search(title or ""))


def subfamily_of(ticker: str) -> str:
    for s in REGISTRY:
        if s.ticker == ticker:
            return s.subfamily
    return "candidate"
