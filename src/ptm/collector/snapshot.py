"""The snapshot collector. Highest-priority artifact in the program: Kalshi archives
price history when a market settles, so anything not captured here is gone.

Two modes, both idempotent and safe to re-run:

``hourly``  For every series in the family (registry + current candidates):
            ``/series/{t}`` and every page of ``/markets?series_ticker=t&status=open``.
            ~2 calls per series; ~1 minute wall-clock for ~40 series at 4 req/s.

``daily``   Everything in ``hourly`` plus, per series, ``/markets?status=settled``
            and ``/historical/markets``; per open or recently-settled market, hourly
            candlesticks for the trailing ``candle_days`` days; and a full crawl of
            the ``/series`` catalogue to discover new candidate series.

Every response body is stored verbatim through ``RawStore``. A run record is appended
to ``<root>/runs.jsonl``; the process exits non-zero if any *registry* series failed,
so the scheduler (GitHub Actions) surfaces the failure.

Usage:
    ptm-collect --mode hourly --root data/raw
    ptm-collect --mode daily  --root data/raw --candle-days 3
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
import uuid
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from ptm.collector.family import REGISTRY_TICKERS, is_candidate
from ptm.collector.kalshi_client import KalshiClient, Response
from ptm.collector.rawstore import RawStore, utcnow

log = logging.getLogger("ptm.collector")


@dataclass
class RunRecord:
    run_id: str
    mode: str
    started_ts: str
    finished_ts: str | None = None
    series_attempted: list[str] = field(default_factory=list)
    series_failed: list[str] = field(default_factory=list)
    n_requests: int = 0
    n_non200: int = 0
    n_candles_requested: int = 0
    n_candles_empty: int = 0
    notes: list[str] = field(default_factory=list)


class Collector:
    def __init__(self, client: KalshiClient, store: RawStore, mode: str):
        self.client = client
        self.store = store
        self.mode = mode
        self.run = RunRecord(run_id=uuid.uuid4().hex[:12], mode=mode, started_ts=utcnow().isoformat())

    # -- helpers -------------------------------------------------------------------
    def _save(self, resp: Response, kind: str, slug: str, note: str = "") -> None:
        self.run.n_requests += 1
        if resp.status_code != 200:
            self.run.n_non200 += 1
        self.store.write(kind=kind, slug=slug, url=resp.url, params=resp.params,
                         status_code=resp.status_code, body=resp.body, run_id=self.run.run_id, note=note)

    def candidates_path(self) -> Path:
        return self.store.root / "candidates_latest.json"

    def load_candidates(self) -> list[str]:
        p = self.candidates_path()
        if not p.exists():
            return []
        try:
            return sorted(set(json.loads(p.read_text(encoding="utf-8")).get("tickers", [])))
        except json.JSONDecodeError:
            log.warning("candidates_latest.json unreadable; ignoring")
            return []

    def family_tickers(self) -> list[str]:
        return sorted(REGISTRY_TICKERS | set(self.load_candidates()))

    # -- per-series capture ------------------------------------------------------------
    def capture_series(self, ticker: str, *, include_settled: bool) -> list[dict[str, Any]]:
        """Capture metadata and open markets (and settled/historical if daily).
        Returns the list of open-market objects for candlestick follow-up."""
        open_markets: list[dict[str, Any]] = []
        resp = self.client.series(ticker)
        self._save(resp, "series", ticker)
        if resp.status_code == 404:
            self.run.notes.append(f"{ticker}: series 404")
            return open_markets
        for page in self.client.markets_pages(ticker, status="open"):
            self._save(page, "markets_open", ticker)
            if page.status_code == 200:
                open_markets.extend(page.json().get("markets", []))
        if include_settled:
            for page in self.client.markets_pages(ticker, status="settled"):
                self._save(page, "markets_settled", ticker)
            for page in self.client.historical_pages(ticker):
                self._save(page, "historical", ticker)
        return open_markets

    def capture_candles(self, series_ticker: str, market_ticker: str, days: int, period_minutes: int = 60) -> None:
        end = int(time.time())
        start = end - days * 86400
        resp = self.client.candlesticks(series_ticker, market_ticker, start, end, period_minutes)
        self._save(resp, f"candles{period_minutes}", market_ticker)
        self.run.n_candles_requested += 1
        if resp.status_code == 200 and not resp.json().get("candlesticks"):
            self.run.n_candles_empty += 1

    def discover(self) -> list[str]:
        """Crawl the whole catalogue; store it; return new candidate tickers."""
        found: dict[str, str] = {}
        for i, page in enumerate(self.client.catalog_pages()):
            self._save(page, "catalog", f"page{i:03d}")
            if page.status_code != 200:
                break
            for s in page.json().get("series", []):
                t, title = s.get("ticker", ""), s.get("title", "")
                if is_candidate(t, title):
                    found[t] = title
        prev = set(self.load_candidates())
        merged = sorted(prev | set(found))
        out = {"as_of": utcnow().isoformat(), "tickers": merged,
               "titles": {t: found.get(t, "") for t in merged}}
        self.candidates_path().write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        new = sorted(set(found) - prev)
        if new:
            self.run.notes.append(f"new candidates: {new}")
        return new

    # -- orchestration ---------------------------------------------------------------
    def run_all(self, candle_days: int = 3, settled_lookback_days: int = 30) -> RunRecord:
        daily = self.mode == "daily"
        if daily:
            try:
                self.discover()
            except Exception as e:  # discovery failure must not block capture
                log.exception("discovery failed")
                self.run.notes.append(f"discovery failed: {e}")
        candle_targets: list[tuple[str, str]] = []
        for t in self.family_tickers():
            self.run.series_attempted.append(t)
            try:
                open_markets = self.capture_series(t, include_settled=daily)
                if daily:
                    candle_targets.extend((t, m["ticker"]) for m in open_markets)
                    candle_targets.extend(self._recently_settled_targets(t, settled_lookback_days))
            except Exception as e:
                log.exception("series %s failed", t)
                self.run.series_failed.append(t)
                self.run.notes.append(f"{t}: {e}")
        if daily:
            seen: set[tuple[str, str]] = set()
            for s, m in candle_targets:
                if (s, m) in seen:
                    continue
                seen.add((s, m))
                try:
                    self.capture_candles(s, m, candle_days)
                except Exception as e:
                    log.exception("candles %s failed", m)
                    self.run.notes.append(f"candles {m}: {e}")
        self.run.finished_ts = utcnow().isoformat()
        with (self.store.root / "runs.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(asdict(self.run), ensure_ascii=False) + "\n")
        return self.run

    def _recently_settled_targets(self, series_ticker: str, lookback_days: int) -> list[tuple[str, str]]:
        """Markets settled within the lookback window still have candlesticks; grab them."""
        cutoff = utcnow() - timedelta(days=lookback_days)
        out: list[tuple[str, str]] = []
        for page in self.client.markets_pages(series_ticker, status="settled"):
            if page.status_code != 200:
                break
            for m in page.json().get("markets", []):
                ts = m.get("settlement_ts") or m.get("close_time")
                if not ts:
                    continue
                try:
                    when = datetime.fromisoformat(ts)  # py3.11+ accepts trailing Z
                except ValueError:
                    continue
                if when.tzinfo is None:
                    when = when.replace(tzinfo=UTC)
                if when >= cutoff:
                    out.append((series_ticker, m["ticker"]))
        return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Kalshi personnel-tenure snapshot collector")
    ap.add_argument("--mode", choices=["hourly", "daily"], required=True)
    ap.add_argument("--root", default="data/raw")
    ap.add_argument("--candle-days", type=int, default=3)
    ap.add_argument("--max-rps", type=float, default=4.0)
    ap.add_argument("--log-level", default="INFO")
    args = ap.parse_args(argv)
    logging.basicConfig(level=args.log_level, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    client = KalshiClient(max_rps=args.max_rps)
    store = RawStore(args.root)
    col = Collector(client, store, args.mode)
    try:
        run = col.run_all(candle_days=args.candle_days)
    finally:
        client.close()
    log.info("run %s: %d requests, %d non-200, failed series=%s, candles=%d (empty %d)",
             run.run_id, run.n_requests, run.n_non200, run.series_failed,
             run.n_candles_requested, run.n_candles_empty)
    failed_registry = [t for t in run.series_failed if t in REGISTRY_TICKERS]
    if failed_registry:
        log.error("registry series failed: %s", failed_registry)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
