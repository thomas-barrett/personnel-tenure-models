"""Re-pin tests/fixtures_rules.py from genuine raw captures.

The fixtures committed on 2026-09-15 were transcribed through a summarizing fetch and
may differ from the API bytes by punctuation or a word. Once the collector has run,
this script reads the latest ``markets_open`` capture per series from the raw store
and prints, for each series, the first market's rules_primary / rules_secondary as
Python literals, so the fixtures can be replaced with verbatim text.

    uv run python scripts/refresh_rules_fixtures.py --root ..\\data\\raw   (data branch checkout)

It prints; it does not edit the test file. Replacing fixtures is a human step recorded
in docs/decision_log.md, and the classifier tests must still pass afterwards.
"""

from __future__ import annotations

import argparse
import json

from ptm.collector.rawstore import RawStore


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/raw")
    ap.add_argument("--series", nargs="*", help="restrict to these series tickers")
    args = ap.parse_args()
    store = RawStore(args.root)
    latest: dict[str, object] = {}
    for rec in store.iter_manifest():
        if rec.kind == "markets_open" and rec.status_code == 200:
            if args.series and rec.slug not in args.series:
                continue
            latest[rec.slug] = rec  # manifest is chronological; last wins
    for slug, rec in sorted(latest.items()):
        markets = json.loads(store.read(rec)).get("markets", [])
        if not markets:
            print(f"# {slug}: no open markets in capture {rec.path}")
            continue
        m = markets[0]
        print(f"# {slug}  (capture {rec.capture_ts}, {rec.path})")
        print(f"{slug} = {{")
        print(f"    \"rules_primary\": {json.dumps(m.get('rules_primary', ''), ensure_ascii=False)},")
        print(f"    \"rules_secondary\": {json.dumps(m.get('rules_secondary', ''), ensure_ascii=False)},")
        print("}\n")


if __name__ == "__main__":
    main()
