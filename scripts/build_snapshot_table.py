"""Rebuild the derived market-snapshot table from raw captures. Never edited by hand.

    python scripts/build_snapshot_table.py --root data/raw --out data/derived/market_snapshots.parquet

Reads every ``markets_open`` / ``markets_settled`` / ``historical`` capture in the
manifest, parses rows (one per market per capture) with the rule-variant fields, and
writes a Parquet file plus a CSV of the latest open quotes per market for eyeballing.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ptm.collector.rawstore import RawStore
from ptm.parse.markets import rows_from_markets_body, rows_to_records


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/raw")
    ap.add_argument("--out", default="data/derived/market_snapshots.parquet")
    args = ap.parse_args()
    store = RawStore(args.root)
    records = []
    for rec in store.iter_manifest():
        if rec.kind not in {"markets_open", "markets_settled", "historical"} or rec.status_code != 200:
            continue
        rows = rows_from_markets_body(store.read(rec), capture_ts=rec.capture_ts, run_id=rec.run_id,
                                      series_ticker=rec.slug)
        for r in rows_to_records(rows):
            r["capture_kind"] = rec.kind
            records.append(r)
    df = pd.DataFrame.from_records(records)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(out, index=False)
    if not df.empty:
        latest = (df[df.capture_kind == "markets_open"]
                  .sort_values("capture_ts")
                  .groupby("ticker", as_index=False).tail(1)
                  [["capture_ts", "series_ticker", "ticker", "person", "role", "yes_bid", "yes_ask", "mid",
                    "volume", "open_interest", "close_time", "rv_trigger", "rv_window_end"]])
        latest.to_csv(out.with_name("latest_open_quotes.csv"), index=False)
    print(f"{len(df)} rows -> {out}")


if __name__ == "__main__":
    main()
