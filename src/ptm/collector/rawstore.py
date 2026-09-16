"""Immutable raw storage for API responses.

Design rules (see docs/02_phase0_collector_design.md):

* Every HTTP response body is written exactly as received (bytes), gzip-compressed,
  under ``<root>/<YYYY>/<MM>/<DD>/<HHMMSS>Z_<kind>_<slug>_<sha12>.json.gz``.
* A line is appended to ``<root>/manifest.jsonl`` for every write: capture time,
  request URL and params, HTTP status, byte length, SHA-256 of the *uncompressed* body,
  and the relative path. The manifest is the index; the files are the evidence.
* Nothing in this module ever modifies or deletes an existing file. If a path
  already exists (same second, same content hash) the write is a no-op and the
  manifest still records the capture.
"""

from __future__ import annotations

import gzip
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def slugify(s: str, max_len: int = 80) -> str:
    """Make a filesystem-safe slug from an arbitrary string (ticker, endpoint)."""
    out = _SLUG_RE.sub("-", s).strip("-")
    return out[:max_len] if out else "x"


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utcnow() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True)
class CaptureRecord:
    capture_ts: str          # ISO-8601 UTC, microsecond precision
    run_id: str              # one id per collector invocation (groups a snapshot)
    kind: str                # e.g. "series", "markets", "candles", "historical", "catalog"
    slug: str                # e.g. series ticker or market ticker
    url: str
    params: dict[str, Any]
    status_code: int
    n_bytes: int
    sha256: str
    path: str                # relative to store root, POSIX separators
    note: str = ""

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, ensure_ascii=False)


class RawStore:
    """Append-only store of raw response bodies plus a JSON-lines manifest."""

    def __init__(self, root: Path | str):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.root / "manifest.jsonl"

    def write(
        self,
        *,
        kind: str,
        slug: str,
        url: str,
        params: dict[str, Any],
        status_code: int,
        body: bytes,
        run_id: str,
        capture_ts: datetime | None = None,
        note: str = "",
    ) -> CaptureRecord:
        ts = capture_ts or utcnow()
        if ts.tzinfo is None:
            raise ValueError("capture_ts must be timezone-aware (UTC)")
        ts = ts.astimezone(UTC)
        digest = sha256_hex(body)
        day_dir = self.root / f"{ts:%Y}" / f"{ts:%m}" / f"{ts:%d}"
        day_dir.mkdir(parents=True, exist_ok=True)
        fname = f"{ts:%H%M%S}Z_{slugify(kind)}_{slugify(slug)}_{digest[:12]}.json.gz"
        fpath = day_dir / fname
        if not fpath.exists():
            # Write to a temp name then rename so a crash never leaves a half file.
            tmp = fpath.with_suffix(".tmp")
            with gzip.open(tmp, "wb", compresslevel=6) as fh:
                fh.write(body)
            tmp.replace(fpath)
        rec = CaptureRecord(
            capture_ts=ts.isoformat(timespec="microseconds"),
            run_id=run_id,
            kind=kind,
            slug=slug,
            url=url,
            params={k: str(v) for k, v in sorted(params.items())},
            status_code=status_code,
            n_bytes=len(body),
            sha256=digest,
            path=fpath.relative_to(self.root).as_posix(),
            note=note,
        )
        with self.manifest_path.open("a", encoding="utf-8") as fh:
            fh.write(rec.to_json() + "\n")
        return rec

    def read(self, rec_or_path: CaptureRecord | str) -> bytes:
        rel = rec_or_path.path if isinstance(rec_or_path, CaptureRecord) else rec_or_path
        with gzip.open(self.root / rel, "rb") as fh:
            return fh.read()

    def verify(self, rec: CaptureRecord) -> bool:
        """Recompute the hash of a stored body and compare with the manifest."""
        return sha256_hex(self.read(rec)) == rec.sha256

    def iter_manifest(self):
        if not self.manifest_path.exists():
            return
        with self.manifest_path.open("r", encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if line:
                    yield CaptureRecord(**json.loads(line))
