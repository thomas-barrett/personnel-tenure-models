# 02 — Phase 0: collector design and repository layout

Version 0.1, 15 September 2026.

**Plain-language summary.** Kalshi's API only serves price history for markets that are open or recently settled; once a market is archived, the history is gone. So the first thing the program needs is a robot that, every hour, downloads the current state of every market in the family and files it away unchanged, and that keeps doing so whether or not the laptop is on. This document says what the robot fetches, where it puts it, how we know it ran, and how the code is organized around it.

## 1. What is captured, and why each piece

The API facts that drive the design, verified against live responses on 15 Sep 2026:

- `GET /markets?series_ticker=…&status=open` returns every open market with its quotes (`yes_bid_dollars`, `yes_ask_dollars`, sizes, `last_price_dollars`, `volume_fp`, `open_interest_fp`) and its full rules text. This is the only endpoint that gives the book, so it is the hourly payload.
- `GET /markets?status=settled` returns recently settled markets with `result`, `settlement_ts`, and — importantly — a `close_time` equal to the moment of early close, which for a YES settlement is the Exchange's own timestamp of the settlement-defined event (Blanche 2026-08-10T19:06:35Z; Leavitt 2026-08-28T16:50:07Z). Markets migrate from here to `/historical/markets` after some weeks.
- `GET /historical/markets?series_ticker=…` returns archived markets with `result` and `close_time` but no prices. It preserves the event timestamp and the outcome for names whose price history we missed.
- `GET /series/{s}/markets/{m}/candlesticks?period_interval=60` returns hourly bid/ask/price OHLC with volume and open interest for open and recently settled markets, and an empty list for archived ones. It is the backfill: an hourly snapshot that fails for two hours is repaired by the next daily candlestick pull.
- `GET /series/{t}` gives `contract_terms_url` and metadata; `GET /series` (paginated, ~14k rows) is the catalogue used to discover new series.

Two cadences. The **hourly** job (`ptm-collect --mode hourly`) fetches, for each series in the family, the series object and every page of open markets: about two requests per series, roughly 80 requests and well under a minute. The **daily** job (`--mode daily`, 04:20 UTC) additionally fetches settled and historical markets per series, hourly candlesticks over the trailing three days for every open market and every market settled in the last 30 days, and the full catalogue for discovery: roughly 500 requests and a few minutes at four requests per second. The three-day candlestick window overlaps, so any single missed run is covered twice.

The family is defined in `src/ptm/collector/family.py`: a hand-maintained registry of 35 series with sub-family labels, plus a discovery rule (`CANDIDATE_RE`) applied to the whole catalogue daily. Matches not in the registry are written to `data/raw/candidates_latest.json` and captured from the next run onward, tagged as candidates. Promotion into the registry, with a sub-family label and a rules reading, is a human decision recorded in the decision log. The asymmetry is intentional: a false positive costs a few requests, a false negative costs history.

## 2. Immutable raw storage

Every response body is written as received, gzip-compressed, to

```
data/raw/YYYY/MM/DD/HHMMSSZ_<kind>_<slug>_<sha12>.json.gz
```

and one line is appended to `data/raw/manifest.jsonl` with the capture time (UTC, microseconds), run id, kind (`series`, `markets_open`, `markets_settled`, `historical`, `candles60`, `catalog`), slug (series or market ticker), URL and parameters, HTTP status, byte length, SHA-256 of the uncompressed body, and the relative path. `RawStore.write` never overwrites: identical bytes in the same second map to the same path and the write is a no-op, but the manifest still records that the capture happened. `RawStore.verify` recomputes a hash from disk. Non-200 responses are stored too, because "the API said 404 for this series on this date" is evidence about roster changes.

Each run appends a record to `data/raw/runs.jsonl` (mode, start and end time, series attempted and failed, request counts, number of empty candlestick responses, free-text notes). The process exits non-zero if any registry series failed, which turns the GitHub Actions run red and triggers GitHub's failure email to the repository owner. A candidate series failing is logged but does not fail the run.

Storage arithmetic. An hourly capture of ~40 series is on the order of 1 MB of JSON before compression, ~100 KB after, so ~2.5 MB per day and roughly 1 GB per year of git history on the data branch. That is within GitHub's comfortable range for a public repository but not negligible; the mitigation, if it becomes necessary, is to pack each completed month into a release asset and keep only the manifest in git. Rules text is the bulk of every market object and repeats every hour; it is kept because immutability of the raw record is the point, and the compression ratio on repeated text is high.

## 3. Where it runs

Decision (15 Sep 2026): GitHub Actions, public repository. The schedule is `7 * * * *` (hourly at :07, to avoid the top-of-hour congestion on GitHub's cron, which is documented to delay and occasionally skip runs) and `20 4 * * *` for the daily mode. The workflow checks out `main` for the code and the orphan branch `data` for storage, installs the pinned environment with `uv sync --frozen`, runs the collector, commits, and pushes with a fetch-and-rebase retry in case two runs overlap. A `concurrency` group serializes runs. Your own commits go to `main`; the collector never touches `main`, so there is nothing to merge on your side.

Known failure modes and what covers them: GitHub cron delays of 5–30 minutes are common and skipped hours happen under load, which is why the daily candlestick pull backfills three days; a GitHub-wide outage of more than three days would lose intra-day history but not outcomes (historical markets keep `result` and `close_time`); a Kalshi API change that breaks pagination or renames a field would show up as a failed run or as a parser test failure, and the raw bytes would still be stored because storage happens before parsing; Kalshi silently changing rules text would be caught by `rules_sha256` changing on a market and by the pinned fixture tests. What is not covered: an unannounced rate-limit change that turns every request into a 429. The client backs off exponentially and honours `Retry-After`, and the run fails visibly rather than partially.

Rate limits. The prior survey found that market data endpoints answer without authentication, which today's calls confirm. Kalshi's documentation page on rate limits could not be fetched from this session; third-party summaries dated July 2026 report a basic tier of 200 read tokens per second. The collector uses four requests per second, two orders of magnitude below that, and the client is written so the ceiling is one number to change.

An optional second collector on the laptop (Windows Task Scheduler running `uv run ptm-collect --mode hourly --root data\raw`) is supported by the same code and writes to the same layout; it is not required and is not set up in this milestone.

## 4. Tests

`uv run pytest` is the gate. It covers: rule-variant classification of every rules text captured on 15 Sep 2026 (14 tests, one per series or property, including a "wording change changes the hash" test and an "unknown text yields None, not a guess" test); the raw store's immutability, hashing, gzip fidelity for non-ASCII bytes, rejection of naive timestamps, and manifest behaviour; parsing of open and settled market objects into rows with rule fields, including missing quotes on settled markets; and an end-to-end daily and hourly run of the collector against a mocked API with pagination, a 404 series, a discovered candidate, an excluded ticker, recent versus old settled markets for candlestick targeting, and an empty candlestick response. The client's retry-then-raise behaviour is tested separately. There is no test that touches the network.

## 5. Repository layout

```
personnel-tenure-models/
├── .github/workflows/collect.yml     collector schedule; commits to the `data` branch
├── pyproject.toml, uv.lock           pinned environment (uv; Python 3.12)
├── src/ptm/
│   ├── collector/
│   │   ├── kalshi_client.py          throttled, retrying GET client; pagination helpers
│   │   ├── rawstore.py               append-only gzip store + manifest.jsonl
│   │   ├── family.py                 series registry, sub-family labels, discovery regex
│   │   ├── snapshot.py               hourly/daily orchestration; runs.jsonl; exit codes
│   │   └── discover.py               stand-alone catalogue discovery
│   ├── parse/
│   │   ├── rules.py                  RuleVariant classifier (trigger, death, window, ...)
│   │   └── markets.py                raw /markets body -> one row per market per capture
│   └── panel/schema.py               Arrow schemas: persons, roles, spells, exposure panel, snapshots
├── scripts/build_snapshot_table.py   rebuilds data/derived/market_snapshots.parquet from raw
├── tests/                            fixtures_rules.py + unit and end-to-end tests
├── docs/
│   ├── 01_estimands_and_settlement_events.md
│   ├── 02_phase0_collector_design.md
│   ├── 03_pre_analysis_plan_skeleton.md
│   ├── 04_assumptions_to_overturn.md
│   ├── decision_log.md, research_log.md
│   └── pap/                          dated, tagged pre-analysis plans (Phase 2)
└── data/raw, data/derived            empty on main; the `data` branch holds captures
```

Later phases add `src/ptm/groundtruth/` (spell construction from Brookings, Federal Register, Senate.gov, EDGAR), `src/ptm/models/` (M0–M5), `src/ptm/eval/` (scoring, reliability, block bootstrap, SBC) and `reports/`. Nothing that produces a reported number lives in a notebook.

## 6. Environment mechanics (Windows)

`uv` is the one tool: it installs the pinned Python, creates `.venv`, and resolves exactly the versions in `uv.lock`. `uv sync --frozen --all-extras` builds the environment; `uv run <command>` runs anything inside it without activating a shell. `uv.lock` is committed; regenerating it (`uv lock`) is a deliberate act recorded in the decision log. The GitHub Actions job uses the same lock file with `--frozen`, so the collector runs the same code with the same libraries as your laptop.
