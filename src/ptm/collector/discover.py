"""Stand-alone catalogue discovery (also run inside ``ptm-collect --mode daily``).

    ptm-discover --root data/raw
"""

from __future__ import annotations

import argparse
import logging
import sys

from ptm.collector.kalshi_client import KalshiClient
from ptm.collector.rawstore import RawStore
from ptm.collector.snapshot import Collector


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="data/raw")
    args = ap.parse_args(argv)
    logging.basicConfig(level="INFO")
    client = KalshiClient()
    try:
        col = Collector(client, RawStore(args.root), "discover")
        new = col.discover()
    finally:
        client.close()
    print("new candidates:", new)
    return 0


if __name__ == "__main__":
    sys.exit(main())
