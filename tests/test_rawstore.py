import gzip
import json
from datetime import UTC, datetime

from ptm.collector.rawstore import RawStore, sha256_hex, slugify


def test_write_is_immutable_and_hashed(tmp_path):
    store = RawStore(tmp_path)
    body = b'{"markets": []}'
    ts = datetime(2026, 9, 15, 12, 0, 0, tzinfo=UTC)
    rec = store.write(kind="markets_open", slug="KXTEST", url="u", params={"a": 1},
                      status_code=200, body=body, run_id="r1", capture_ts=ts)
    assert rec.sha256 == sha256_hex(body)
    assert rec.path.startswith("2026/09/15/120000Z_markets_open_KXTEST_")
    assert store.read(rec) == body
    assert store.verify(rec)
    # Same content, same second -> same path, no rewrite, but manifest gets a second line.
    rec2 = store.write(kind="markets_open", slug="KXTEST", url="u", params={"a": 1},
                       status_code=200, body=body, run_id="r2", capture_ts=ts)
    assert rec2.path == rec.path
    lines = store.manifest_path.read_text().strip().splitlines()
    assert len(lines) == 2
    assert json.loads(lines[1])["run_id"] == "r2"


def test_different_content_gets_different_file(tmp_path):
    store = RawStore(tmp_path)
    ts = datetime(2026, 9, 15, 12, 0, 0, tzinfo=UTC)
    a = store.write(kind="k", slug="s", url="u", params={}, status_code=200, body=b"a", run_id="r", capture_ts=ts)
    b = store.write(kind="k", slug="s", url="u", params={}, status_code=200, body=b"b", run_id="r", capture_ts=ts)
    assert a.path != b.path
    assert (tmp_path / a.path).exists() and (tmp_path / b.path).exists()


def test_naive_timestamp_rejected(tmp_path):
    store = RawStore(tmp_path)
    try:
        store.write(kind="k", slug="s", url="u", params={}, status_code=200, body=b"x", run_id="r",
                    capture_ts=datetime(2026, 1, 1))  # noqa: DTZ001 (naive on purpose)
    except ValueError:
        return
    raise AssertionError("naive datetime should be rejected")


def test_stored_file_is_gzip_of_exact_bytes(tmp_path):
    store = RawStore(tmp_path)
    body = "{\"t\": \"Sébastien\"}".encode()
    rec = store.write(kind="k", slug="s", url="u", params={}, status_code=200, body=body, run_id="r")
    with gzip.open(tmp_path / rec.path, "rb") as fh:
        assert fh.read() == body


def test_slugify():
    assert slugify("KXTRUMPADMINLEAVE-26DEC31-RSCO") == "KXTRUMPADMINLEAVE-26DEC31-RSCO"
    assert slugify("a b/c") == "a-b-c"
    assert slugify("") == "x"
