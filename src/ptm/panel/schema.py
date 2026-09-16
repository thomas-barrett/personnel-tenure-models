"""Schemas for the person–role–period panel (Phase 1) and the market snapshot table.

Definitions (fixed here so every later script agrees):

A *spell* is one continuous holding of one role by one person. A spell has a start
(``start_date``: the date the person began to hold the role, acting or confirmed as
recorded), and up to two exit times which are modeled as separate event times:

  ``announce_date``  first qualifying public announcement that the person will leave
                     (by the person, an authorized representative, or the appointing
                     authority), or the same date as ``vacate_date`` when the departure
                     was immediate (fired, resigned effective immediately). Null if the
                     spell is still open or no announcement preceded vacating.
  ``vacate_date``    the effective date on which the person ceased to hold the role.
                     Null if right-censored (still in role at ``censor_date``).

The lag ``vacate_date - announce_date`` is a modeled quantity (it has an atom at 0).
``exit_cause`` is a coded reason (resigned, fired, promoted/moved, term_expired,
died, other); death is kept as a competing risk, not dropped.

The *exposure panel* expands spells into person-role-period rows (period = ISO week by
default) with time-varying covariates; the piecewise-exponential model is a Poisson
GLM on this table with ``log(exposure_days)`` as offset.

Every ground-truth row cites a primary source (``source_url``, ``source_kind``) and
carries ``captured_ts`` (when we recorded it) so the information set is auditable.
"""

from __future__ import annotations

import pyarrow as pa

PERSONS = pa.schema([
    ("person_id", pa.string()),        # stable slug: lastname-firstname-birthyear
    ("full_name", pa.string()),
    ("birth_year", pa.int32()),         # nullable; used only for justices/leaders age covariate
    ("aliases", pa.list_(pa.string())),
])

ROLES = pa.schema([
    ("role_id", pa.string()),           # e.g. us-sec-defense, us-wh-chief-of-staff, fr-pm
    ("role_name", pa.string()),
    ("body", pa.string()),              # us_admin | world_leader | uk_cabinet | scotus | fed | corporate
    ("role_class", pa.string()),        # cabinet_secretary | senate_confirmed_subcabinet | wh_staff |
                                        # head_of_government | head_of_state | justice | fed_governor | ceo
    ("senate_confirmed", pa.bool_()),
    ("country", pa.string()),
])

SPELLS = pa.schema([
    ("spell_id", pa.string()),
    ("person_id", pa.string()),
    ("role_id", pa.string()),
    ("administration_id", pa.string()),  # e.g. us-trump-2, us-biden-1, uk-burnham-1; null for justices/CEOs
    ("acting", pa.bool_()),
    ("start_date", pa.date32()),
    ("announce_date", pa.date32()),      # nullable
    ("vacate_date", pa.date32()),        # nullable => right-censored at censor_date
    ("censor_date", pa.date32()),
    ("exit_cause", pa.string()),         # resigned | fired | moved | term_expired | died | other | null
    ("source_kind", pa.string()),        # federal_register | agency_release | senate_gov | court_record | 8k | brookings | wikipedia_index
    ("source_url", pa.string()),
    ("source_note", pa.string()),
    ("captured_ts", pa.timestamp("us", tz="UTC")),
])

EXPOSURE_PANEL = pa.schema([
    ("spell_id", pa.string()),
    ("person_id", pa.string()),
    ("role_id", pa.string()),
    ("role_class", pa.string()),
    ("administration_id", pa.string()),
    ("period_start", pa.date32()),
    ("period_end", pa.date32()),
    ("exposure_days", pa.int16()),
    ("tenure_days_at_start", pa.int32()),
    ("event_announce", pa.int8()),       # 1 if announce_date in period
    ("event_vacate", pa.int8()),         # 1 if vacate_date in period
    ("event_death", pa.int8()),
    ("term_year", pa.int8()),            # 1..4 within a presidential term
    ("days_to_midterm", pa.int32()),
    ("post_midterm_window", pa.int8()),  # 1 if within [election day, Jan 31]
    ("approval_pct", pa.float32()),      # nullable; time-respecting (as of period_start)
    ("news_intensity", pa.float32()),    # nullable; defined in Phase 1 PAP
])

MARKET_SNAPSHOTS = pa.schema([
    ("capture_ts", pa.timestamp("us", tz="UTC")),
    ("run_id", pa.string()),
    ("series_ticker", pa.string()),
    ("ticker", pa.string()),
    ("person", pa.string()),
    ("role", pa.string()),
    ("status", pa.string()),
    ("result", pa.string()),
    ("close_time", pa.timestamp("us", tz="UTC")),
    ("expiration_time", pa.timestamp("us", tz="UTC")),
    ("yes_bid", pa.float32()),
    ("yes_ask", pa.float32()),
    ("mid", pa.float32()),
    ("last_price", pa.float32()),
    ("volume", pa.float32()),
    ("open_interest", pa.float32()),
    ("rv_trigger", pa.string()),
    ("rv_competing", pa.bool_()),
    ("rv_any_member", pa.bool_()),
    ("rv_death_not_yes", pa.bool_()),
    ("rv_death_scalar", pa.bool_()),
    ("rv_window_end", pa.date32()),
    ("rules_sha256", pa.string()),
])
