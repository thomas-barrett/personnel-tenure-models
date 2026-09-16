# Decision log

Entries are dated and never deleted; a reversed decision gets a new entry that points at the old one.

## 2026-09-15 — D001: Collector runs on GitHub Actions in a public repository

Options considered: (a) GitHub Actions, public repo; (b) GitHub Actions, private repo (2,000 free minutes/month would cap the cadence at roughly one run per two hours); (c) Windows Task Scheduler on the laptop (misses runs when the machine sleeps); (d) both. Chosen: (a), with the laptop path kept working in code as an optional second collector. Reason: unattended operation from day one is the requirement; public visibility is consistent with a replication package. Consequence to revisit before a paper-trading period: whether live position logic should be visible.

## 2026-09-15 — D002: Capture the whole family, not only the US administration

Capture is ~80 requests per hour; history lost now is unrecoverable; the hierarchical model needs the leader, judge, central-banker and CEO strata. Modeling scope is narrowed later, capture scope is not.

## 2026-09-15 — D003: Raw captures live on an orphan `data` branch of the same repository

Options: separate data repository (cleaner, but needs a personal access token stored as a secret and rotated); Git LFS (1 GB free then paid); cloud object storage (extra account and credentials for a new programmer); same repo, `data` branch (uses the built-in `GITHUB_TOKEN`, no secrets, `main` untouched). Chosen: `data` branch. Estimated growth ~1 GB/year; mitigation if needed is monthly packing into release assets with the manifest kept in git.

## 2026-09-15 — D004: Store raw bodies gzip-compressed, verbatim, with SHA-256 of the uncompressed bytes

Compression keeps the branch manageable; hashing the uncompressed bytes means the manifest hash is independent of the compressor. Non-200 responses are stored too.

## 2026-09-15 — D005: Rule variants are classified by phrase matching with pinned fixtures, not by hand fields

A hand-maintained table would drift; a classifier that returns `None` on unknown text and whose fixtures are the verbatim API strings turns any wording change into a failing test. The classifier is conservative by design and will need new phrases when new series appear (a human step recorded here).

## 2026-09-15 — D006: Death outcomes are excluded from the binary calibration sample and tracked as a third category

Because the death treatment differs across series and involves Exchange discretion (document 01, §2).

## 2026-09-15 — D007: Environment pinned with uv (Python 3.12, `uv.lock` committed)

Alternatives: conda (heavier), pip + requirements.txt (no lock of transitive deps), poetry (slower resolver, second config format). uv installs the interpreter too, which removes the "which Python" class of Windows problems.

## 2026-09-15 — D008: Fee schedule date discrepancy is an open item

The schedule PDF at kalshi.com/docs/kalshi-fee-schedule.pdf read on 15 Sep 2026 states "Last updated and effective: July 1, 2025" in its text, while the file's search listing calls it the July 2026 (7.7.26) update. Taker 0.07·C·P(1−P) rounded up to the cent; maker 0.0175·C·P(1−P) on an enumerated list of series that does not include any tenure series. Action: open the PDF on the laptop and record the header date here; confirm the "no maker fee" reading with one small resting fill before any Phase 6 number is reported.

## 2026-09-15 — D009: Rate-limit ceiling set at 4 requests/second

Kalshi's own rate-limit page could not be fetched from this session (the fetch required an approval that timed out). Third-party summaries dated July 2026 report a basic tier of 200 read tokens/second. The client backs off on 429 and honours Retry-After. Action: read docs.kalshi.com/getting_started/rate_limits on the laptop and record the figure here.

## 2026-09-15 — D010: Rules fixtures are provisional until re-pinned from raw bytes

The 15 Sep fixtures in `tests/fixtures_rules.py` came through a summarizing fetch (the only route to the API from the build session), which was observed to paraphrase even when asked for verbatim JSON. The classifier tests therefore prove the classifier against the *transcribed* text. First action after the collector's first run: `uv run python scripts/refresh_rules_fixtures.py --root <data-branch>/raw`, replace the fixtures with the printed literals, re-run `uv run pytest`, and record any wording differences here. The CABOUT fixture is the exception: it was returned as raw JSON and is verbatim.
