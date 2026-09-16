import json

from ptm.parse.markets import rows_from_markets_body
from tests import fixtures_rules as F


def _market(**over):
    base = {
        "ticker": "KXTRUMPADMINLEAVE-26JUN-SCHE",
        "event_ticker": "KXTRUMPADMINLEAVE-26JUN",
        "title": "Will Steven Cheung be out as White House Communications Director before 2027?",
        "custom_strike": {"Person": "Steven Cheung"},
        "status": "active",
        "result": "",
        "open_time": "2026-06-20T18:00:00Z",
        "close_time": "2026-12-31T04:59:00Z",
        "expiration_time": "2027-01-07T15:00:00Z",
        "can_close_early": True,
        "yes_bid_dollars": "0.1100",
        "yes_ask_dollars": "0.1400",
        "yes_bid_size_fp": "180.83",
        "yes_ask_size_fp": "1.00",
        "last_price_dollars": "0.1100",
        "previous_price_dollars": "0.1100",
        "volume_fp": "6546.89",
        "volume_24h_fp": "0.00",
        "open_interest_fp": "2735.59",
        **F.EFFECTIVELEAVE_ADMIN,
    }
    base.update(over)
    return base


def test_parse_open_market_row():
    body = json.dumps({"markets": [_market()], "cursor": ""}).encode()
    rows = rows_from_markets_body(body, capture_ts="2026-09-15T12:00:00+00:00", run_id="r",
                                  series_ticker="KXTRUMPADMINLEAVE")
    assert len(rows) == 1
    r = rows[0]
    assert r.person == "Steven Cheung"
    assert r.role == "White House Communications Director"
    assert r.yes_bid == 0.11 and r.yes_ask == 0.14
    assert abs(r.mid - 0.125) < 1e-9
    assert r.rv_trigger == "vacate"
    assert r.rv_window_end == "2027-01-01"
    assert r.result is None
    assert r.capture_ts == "2026-09-15T12:00:00+00:00"


def test_parse_settled_market_keeps_result_and_close_time():
    m = _market(ticker="KXTRUMPADMINLEAVE-26DEC31-TBLA", status="finalized", result="yes",
                close_time="2026-08-10T19:06:35Z", settlement_ts="2026-08-10T19:36:35.461419Z",
                yes_bid_dollars="", yes_ask_dollars="", last_price_dollars="0.9780")
    body = json.dumps({"markets": [m]}).encode()
    r = rows_from_markets_body(body, capture_ts="t", run_id="r", series_ticker="KXTRUMPADMINLEAVE")[0]
    assert r.result == "yes"
    assert r.close_time == "2026-08-10T19:06:35Z"
    assert r.yes_bid is None and r.mid is None
    assert r.last_price == 0.978


def test_person_fallback_to_subtitle():
    m = _market(custom_strike=None, yes_sub_title="Rodney Scott")
    body = json.dumps({"markets": [m]}).encode()
    r = rows_from_markets_body(body, capture_ts="t", run_id="r", series_ticker="X")[0]
    assert r.person == "Rodney Scott"
