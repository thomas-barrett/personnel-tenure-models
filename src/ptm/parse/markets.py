"""Parse raw ``/markets`` and ``/historical/markets`` responses into flat rows.

One row per market per capture. Prices are kept as Decimal-safe strings converted to
float only at the end; every row carries the capture timestamp of the response it
came from, which is what makes the information set time-respecting.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterable
from dataclasses import asdict, dataclass
from typing import Any

from ptm.parse.rules import classify

_ROLE_RE = re.compile(r"\b(?:leaves|retires|resigns)\s+as\s+(.+?)\s+before\b", re.IGNORECASE)


def _f(x: Any) -> float | None:
    if x is None or x == "":
        return None
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


@dataclass(frozen=True)
class MarketRow:
    capture_ts: str
    run_id: str
    series_ticker: str
    event_ticker: str | None
    ticker: str
    title: str
    person: str | None
    role: str | None
    status: str | None
    result: str | None
    open_time: str | None
    close_time: str | None
    expiration_time: str | None
    settlement_ts: str | None
    can_close_early: bool | None
    yes_bid: float | None
    yes_ask: float | None
    yes_bid_size: float | None
    yes_ask_size: float | None
    last_price: float | None
    previous_price: float | None
    volume: float | None
    volume_24h: float | None
    open_interest: float | None
    rules_primary: str
    rules_secondary: str
    rv_trigger: str | None
    rv_competing: bool
    rv_any_member: bool
    rv_death_not_yes: bool
    rv_death_scalar: bool
    rv_acting_excluded: bool
    rv_one_year_cap: bool
    rv_term_expiration_counts: bool
    rv_tie_break: str | None
    rv_window_start: str | None
    rv_window_end: str | None
    rules_sha256: str

    @property
    def mid(self) -> float | None:
        if self.yes_bid is None or self.yes_ask is None:
            return None
        return 0.5 * (self.yes_bid + self.yes_ask)


def person_of(m: dict[str, Any]) -> str | None:
    cs = m.get("custom_strike") or {}
    if isinstance(cs, dict):
        for k in ("Person", "person", "Leader", "Justice", "Name"):
            if cs.get(k):
                return str(cs[k])
    for k in ("yes_sub_title", "subtitle"):
        if m.get(k):
            return str(m[k])
    return None


def role_of(m: dict[str, Any]) -> str | None:
    mm = _ROLE_RE.search(m.get("rules_primary") or "")
    return mm.group(1).strip() if mm else None


def rows_from_markets_body(body: bytes, *, capture_ts: str, run_id: str, series_ticker: str) -> list[MarketRow]:
    payload = json.loads(body)
    out: list[MarketRow] = []
    for m in payload.get("markets", []):
        rv = classify(m.get("rules_primary") or "", m.get("rules_secondary") or "")
        out.append(MarketRow(
            capture_ts=capture_ts,
            run_id=run_id,
            series_ticker=series_ticker,
            event_ticker=m.get("event_ticker"),
            ticker=m["ticker"],
            title=m.get("title") or "",
            person=person_of(m),
            role=role_of(m),
            status=m.get("status"),
            result=m.get("result") or None,
            open_time=m.get("open_time"),
            close_time=m.get("close_time"),
            expiration_time=m.get("expiration_time"),
            settlement_ts=m.get("settlement_ts"),
            can_close_early=m.get("can_close_early"),
            yes_bid=_f(m.get("yes_bid_dollars")),
            yes_ask=_f(m.get("yes_ask_dollars")),
            yes_bid_size=_f(m.get("yes_bid_size_fp")),
            yes_ask_size=_f(m.get("yes_ask_size_fp")),
            last_price=_f(m.get("last_price_dollars")),
            previous_price=_f(m.get("previous_price_dollars")),
            volume=_f(m.get("volume_fp")),
            volume_24h=_f(m.get("volume_24h_fp")),
            open_interest=_f(m.get("open_interest_fp")),
            rules_primary=m.get("rules_primary") or "",
            rules_secondary=m.get("rules_secondary") or "",
            rv_trigger=rv.trigger,
            rv_competing=rv.competing,
            rv_any_member=rv.any_member,
            rv_death_not_yes=rv.death_not_yes,
            rv_death_scalar=rv.death_scalar,
            rv_acting_excluded=rv.acting_excluded,
            rv_one_year_cap=rv.one_year_cap,
            rv_term_expiration_counts=rv.term_expiration_counts,
            rv_tie_break=rv.tie_break,
            rv_window_start=rv.window_start,
            rv_window_end=rv.window_end,
            rules_sha256=rv.rules_sha256,
        ))
    return out


def rows_to_records(rows: Iterable[MarketRow]) -> list[dict[str, Any]]:
    return [asdict(r) | {"mid": r.mid} for r in rows]
