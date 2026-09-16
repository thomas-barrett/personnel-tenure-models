# personnel-tenure-models

Statistical models and a calibration study for Kalshi personnel-tenure markets
("Will X be out as Y before date?", "next to leave", "any member leaves"). The
program's standard is a publishable methods paper with a full replication package.
This repository holds the code, the pre-analysis plans, the decision and research
logs, and the reports. Raw market captures live on the orphan `data` branch, written
only by the GitHub Actions collector.

## Layout

```
.github/workflows/collect.yml   hourly/daily snapshot collector (GitHub Actions)
src/ptm/collector/              Kalshi client, immutable raw store, family registry, collector
src/ptm/parse/                  rule-variant classifier, market-row parser
src/ptm/panel/                  schemas for the person-role-period panel
scripts/                        anything that produces a reported number (never notebooks)
tests/                          unit tests: parsers, raw store, collector end-to-end (mocked API)
docs/                           estimands, collector design, pre-analysis plan, decision/research logs
data/raw/, data/derived/        empty on main; populated on the `data` branch / locally
```

## Environment (Windows, PowerShell)

The project is pinned with [uv](https://docs.astral.sh/uv/). One-time setup:

```powershell
winget install --id=astral-sh.uv -e        # or: powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
cd C:\Users\stick\personnel-tenure-models
uv sync --frozen --all-extras              # creates .venv from uv.lock, Python 3.12 auto-installed
```

Everyday commands (always through `uv run`, which uses the pinned environment):

```powershell
uv run pytest                              # the gate
uv run ptm-collect --mode hourly           # one local capture into data\raw (optional; Actions is primary)
uv run python scripts\build_snapshot_table.py --root data\raw
```

## Reproducibility rules

Raw responses are stored verbatim with capture timestamps and SHA-256 hashes before
any parsing; derived tables are rebuilt from raw by scripts. Every reported number is
produced by a command written down next to it. Hypotheses used for decisions are
pre-registered in `docs/pap/` and git-tagged before the outcome data are examined.
