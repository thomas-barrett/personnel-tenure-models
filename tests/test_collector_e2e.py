"""End-to-end collector test against a mocked Kalshi API (no network)."""

import json
from urllib.parse import parse_qs, urlparse

import httpx

from ptm.collector import family
from ptm.collector.kalshi_client import KalshiClient
from ptm.collector.rawstore import RawStore
from ptm.collector.snapshot import Collector
from tests import fixtures_rules as F


def _handler_factory(calls: list[str]):
    def handler(request: httpx.Request) -> httpx.Response:
        u = urlparse(str(request.url))
        q = parse_qs(u.query)
        calls.append(u.path + ("?" + u.query if u.query else ""))
        if u.path.endswith("/series/KXA") or u.path.endswith("/series/KXNEWOUT"):
            return httpx.Response(200, json={"series": {"ticker": u.path.rsplit("/", 1)[1], "contract_terms_url": "x.pdf"}})
        if u.path.endswith("/series/KXB"):
            return httpx.Response(404, json={"error": "not found"})
        if u.path.endswith("/series"):
            # two-page catalogue
            if "cursor" not in q:
                return httpx.Response(200, json={"series": [{"ticker": "KXNEWOUT", "title": "Someone out?"},
                                                             {"ticker": "KXWEATHER", "title": "Rain in NYC"}],
                                                 "cursor": "c2"})
            return httpx.Response(200, json={"series": [{"ticker": "FEMALECEO", "title": "female ceo"}], "cursor": ""})
        if u.path.endswith("/markets"):
            st = q.get("status", [""])[0]
            if q["series_ticker"][0] == "KXA" and st == "open":
                # two pages of open markets
                if "cursor" not in q:
                    return httpx.Response(200, json={"markets": [{"ticker": "KXA-1", **F.HEGSETH}], "cursor": "p2"})
                return httpx.Response(200, json={"markets": [{"ticker": "KXA-2", **F.HEGSETH}], "cursor": ""})
            if q["series_ticker"][0] == "KXA" and st == "settled":
                return httpx.Response(200, json={"markets": [
                    {"ticker": "KXA-OLD", "settlement_ts": "2020-01-01T00:00:00Z", "result": "yes"},
                    {"ticker": "KXA-RECENT", "settlement_ts": "2999-01-01T00:00:00Z", "result": "no"}], "cursor": ""})
            return httpx.Response(200, json={"markets": [], "cursor": ""})
        if u.path.endswith("/historical/markets"):
            return httpx.Response(200, json={"markets": [], "cursor": ""})
        if "/candlesticks" in u.path:
            if u.path.endswith("KXA-2/candlesticks"):
                return httpx.Response(200, json={"candlesticks": [], "ticker": "KXA-2"})
            return httpx.Response(200, json={"candlesticks": [{"end_period_ts": 1}], "ticker": "x"})
        return httpx.Response(500, text="boom")
    return handler


def test_daily_run_captures_everything(tmp_path, monkeypatch):
    monkeypatch.setattr(family, "REGISTRY_TICKERS", frozenset({"KXA", "KXB"}))
    import ptm.collector.snapshot as snap
    monkeypatch.setattr(snap, "REGISTRY_TICKERS", frozenset({"KXA", "KXB"}))

    calls: list[str] = []
    client = KalshiClient(max_rps=1000, transport=httpx.MockTransport(_handler_factory(calls)), max_retries=1)
    store = RawStore(tmp_path)
    col = Collector(client, store, "daily")
    run = col.run_all(candle_days=1)

    kinds = [r.kind for r in store.iter_manifest()]
    assert kinds.count("catalog") == 2
    assert kinds.count("series") == 3            # KXA, KXB, plus the discovered KXNEWOUT
    assert kinds.count("markets_open") >= 3      # 2 pages for KXA, 1 each for the others
    assert "candles60" in kinds
    # candlesticks requested for both open markets and the recently-settled one, not the old one
    candle_slugs = sorted(r.slug for r in store.iter_manifest() if r.kind == "candles60")
    assert candle_slugs == ["KXA-1", "KXA-2", "KXA-RECENT"]
    assert run.n_candles_empty == 1
    assert run.series_failed == []               # a 404 is recorded, not a failure
    cands = json.loads((tmp_path / "candidates_latest.json").read_text())
    assert cands["tickers"] == ["KXNEWOUT"]       # FEMALECEO excluded, KXWEATHER not matched
    assert any("KXB: series 404" in n for n in run.notes)
    # every stored body verifies against its hash
    assert all(store.verify(r) for r in store.iter_manifest())


def test_hourly_run_skips_settled_and_candles(tmp_path, monkeypatch):
    import ptm.collector.snapshot as snap
    monkeypatch.setattr(snap, "REGISTRY_TICKERS", frozenset({"KXA"}))
    calls: list[str] = []
    client = KalshiClient(max_rps=1000, transport=httpx.MockTransport(_handler_factory(calls)), max_retries=1)
    col = Collector(client, RawStore(tmp_path), "hourly")
    col.run_all()
    assert not any("settled" in c or "candlesticks" in c or "/historical" in c for c in calls)
    assert sum("/markets?" in c for c in calls) == 2   # two open pages


def test_client_retries_on_5xx_then_raises():
    n = {"calls": 0}

    def handler(request):
        n["calls"] += 1
        return httpx.Response(503, text="down")

    client = KalshiClient(max_rps=1000, transport=httpx.MockTransport(handler), max_retries=2)
    import time
    orig = time.sleep
    time.sleep = lambda s: None
    try:
        try:
            client.series("KXA")
        except RuntimeError:
            pass
        else:
            raise AssertionError("expected RuntimeError")
    finally:
        time.sleep = orig
    assert n["calls"] == 2
