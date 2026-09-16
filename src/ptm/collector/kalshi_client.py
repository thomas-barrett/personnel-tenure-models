"""Thin, polite client for the Kalshi public trade API (market data only, no auth).

Base URL and endpoints used (all GET):

* ``/series/{ticker}``                       series metadata incl. contract_terms_url
* ``/series``                                full catalogue (paginated, for discovery)
* ``/markets?series_ticker=&status=``        market objects incl. rules text and quotes
* ``/historical/markets?series_ticker=``     archived settled markets (result, no prices)
* ``/series/{s}/markets/{m}/candlesticks``   OHLC bid/ask/price, volume, OI

Rate limiting: a simple token bucket at ``max_rps`` requests per second, plus
exponential back-off on 429/5xx. Kalshi's published limits are per-tier and can
change; the collector stays far below the lowest published read tier.

This module never parses beyond ``json.loads`` for pagination; the raw bytes are
what the collector stores.
"""

from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from dataclasses import dataclass
from typing import Any

import httpx

log = logging.getLogger(__name__)

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


@dataclass
class Response:
    url: str
    params: dict[str, Any]
    status_code: int
    body: bytes

    def json(self) -> Any:
        return json.loads(self.body)


class KalshiClient:
    def __init__(
        self,
        base_url: str = BASE_URL,
        max_rps: float = 4.0,
        timeout_s: float = 30.0,
        max_retries: int = 5,
        user_agent: str = "ptm-collector/0.0.1 (+research; contact via GitHub repo)",
        transport: httpx.BaseTransport | None = None,
    ):
        self.base_url = base_url.rstrip("/")
        self.min_interval = 1.0 / max_rps
        self.max_retries = max_retries
        self._last_call = 0.0
        self._client = httpx.Client(
            timeout=timeout_s,
            headers={"User-Agent": user_agent, "Accept": "application/json"},
            transport=transport,
        )

    # -- low level -----------------------------------------------------------------
    def _throttle(self) -> None:
        now = time.monotonic()
        wait = self.min_interval - (now - self._last_call)
        if wait > 0:
            time.sleep(wait)
        self._last_call = time.monotonic()

    def get(self, path: str, params: dict[str, Any] | None = None) -> Response:
        params = {k: v for k, v in (params or {}).items() if v is not None}
        url = f"{self.base_url}{path}"
        backoff = 1.0
        for attempt in range(1, self.max_retries + 1):
            self._throttle()
            try:
                r = self._client.get(url, params=params)
            except httpx.HTTPError as e:
                log.warning("GET %s params=%s attempt %d transport error: %s", path, params, attempt, e)
                time.sleep(backoff)
                backoff = min(backoff * 2, 30)
                continue
            if r.status_code == 429 or r.status_code >= 500:
                retry_after = r.headers.get("Retry-After")
                sleep_s = float(retry_after) if retry_after else backoff
                log.warning("GET %s -> %d; sleeping %.1fs (attempt %d)", path, r.status_code, sleep_s, attempt)
                time.sleep(sleep_s)
                backoff = min(backoff * 2, 30)
                continue
            return Response(url=url, params=params, status_code=r.status_code, body=r.content)
        raise RuntimeError(f"GET {path} failed after {self.max_retries} attempts")

    # -- endpoints -----------------------------------------------------------------
    def series(self, ticker: str) -> Response:
        return self.get(f"/series/{ticker}")

    def catalog_pages(self, limit: int = 1000, **filters: Any) -> Iterator[Response]:
        """Iterate over /series pages (whole catalogue unless filtered)."""
        cursor: str | None = None
        while True:
            resp = self.get("/series", {"limit": limit, "cursor": cursor, **filters})
            yield resp
            if resp.status_code != 200:
                return
            cursor = resp.json().get("cursor") or None
            if not cursor:
                return

    def markets_pages(
        self, series_ticker: str, status: str | None = None, limit: int = 1000, mve_filter: str = "exclude"
    ) -> Iterator[Response]:
        cursor: str | None = None
        while True:
            resp = self.get(
                "/markets",
                {"series_ticker": series_ticker, "status": status, "limit": limit,
                 "cursor": cursor, "mve_filter": mve_filter},
            )
            yield resp
            if resp.status_code != 200:
                return
            cursor = resp.json().get("cursor") or None
            if not cursor:
                return

    def historical_pages(self, series_ticker: str, limit: int = 1000) -> Iterator[Response]:
        cursor: str | None = None
        while True:
            resp = self.get("/historical/markets", {"series_ticker": series_ticker, "limit": limit, "cursor": cursor})
            yield resp
            if resp.status_code != 200:
                return
            cursor = resp.json().get("cursor") or None
            if not cursor:
                return

    def candlesticks(self, series_ticker: str, market_ticker: str, start_ts: int, end_ts: int, period_minutes: int) -> Response:
        return self.get(
            f"/series/{series_ticker}/markets/{market_ticker}/candlesticks",
            {"start_ts": start_ts, "end_ts": end_ts, "period_interval": period_minutes},
        )

    def close(self) -> None:
        self._client.close()
