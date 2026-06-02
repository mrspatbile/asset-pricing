"""Unit tests for nb_utils.cache.DataCache."""

import json
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from nb_utils.cache import DataCache


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def cache(tmp_path):
    return DataCache(processed_dir=tmp_path)


def _make_ois(date: str = "2026-01-15"):
    curve = MagicMock()
    curve.valuation_date = date
    curve._ois_data = pd.DataFrame({
        "zero_rate_pct": [3.0, 3.1, 3.2],
        "years": [1.0, 2.0, 5.0],
        "valuation_date": [date, date, date],
    }, index=pd.Index(["1Y", "2Y", "5Y"], name="maturity"))
    return curve


def _make_nss(date: str = "2026-01-15"):
    curve = MagicMock()
    curve.valuation_date = date
    curve.parameters = {
        "beta0": 3.5, "beta1": -1.2, "beta2": 0.8,
        "beta3": 0.3, "tau1": 1.5, "tau2": 5.0,
    }
    return curve


# ── save / has / load ─────────────────────────────────────────────────────────

def test_save_creates_files(cache, tmp_path):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    assert (tmp_path / "ois_curve_2026-01-15.parquet").exists()
    assert (tmp_path / "nss_params_2026-01-15.json").exists()


def test_save_updates_manifest(cache, tmp_path):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert "2026-01-15" in manifest["dates"]
    assert set(manifest["dates"]["2026-01-15"]["files"]) == {
        "ois_curve_2026-01-15.parquet",
        "nss_params_2026-01-15.json",
    }


def test_has_returns_true_after_save(cache):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    assert cache.has("2026-01-15") is True


def test_has_returns_false_for_unknown_date(cache):
    assert cache.has("1999-01-01") is False


def test_has_returns_false_when_file_missing(cache, tmp_path):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    (tmp_path / "ois_curve_2026-01-15.parquet").unlink()
    assert cache.has("2026-01-15") is False


def test_load_reconstructs_ois_data(cache):
    ois = _make_ois("2026-01-15")
    cache.save("2026-01-15", ois, _make_nss("2026-01-15"))

    with patch("quant_risk.curves.ois.OISCurve") as MockOIS:
        MockOIS.return_value = MagicMock()
        cache.load("2026-01-15")
        call_df = MockOIS.call_args[0][0]
        pd.testing.assert_frame_equal(call_df, ois._ois_data)


def test_load_reconstructs_nss_params(cache):
    nss = _make_nss("2026-01-15")
    cache.save("2026-01-15", _make_ois("2026-01-15"), nss)

    with patch("quant_risk.curves.ois.OISCurve"), \
         patch("quant_risk.curves.nss.NSSCurve") as MockNSS:
        MockNSS.return_value = MagicMock()
        cache.load("2026-01-15")
        call_params = MockNSS.call_args[0][0]
        assert call_params == nss.parameters
        assert MockNSS.call_args[1]["valuation_date"] == "2026-01-15"


# ── pin / unpin ───────────────────────────────────────────────────────────────

def test_pin_persists_to_manifest(cache, tmp_path):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    cache.pin("2026-01-15")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["dates"]["2026-01-15"]["pinned"] is True


def test_unpin_persists_to_manifest(cache, tmp_path):
    cache.save("2026-01-15", _make_ois(), _make_nss())
    cache.pin("2026-01-15")
    cache.unpin("2026-01-15")
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    assert manifest["dates"]["2026-01-15"]["pinned"] is False


def test_pin_unknown_date_does_not_raise(cache, capsys):
    cache.pin("1999-01-01")
    assert "not in cache" in capsys.readouterr().out


# ── eviction ──────────────────────────────────────────────────────────────────

def test_clean_evicts_oldest_unpinned(cache, tmp_path):
    dates = ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]
    for d in dates:
        cache.save(d, _make_ois(d), _make_nss(d))
        cache._m["max_unpinned"] = 10  # disable auto-evict during setup

    cache.clean(keep=2)
    assert not cache.has("2026-01-01")
    assert not cache.has("2026-02-01")
    assert cache.has("2026-03-01")
    assert cache.has("2026-04-01")


def test_clean_never_evicts_pinned(cache, tmp_path):
    dates = ["2026-01-01", "2026-02-01", "2026-03-01", "2026-04-01"]
    for d in dates:
        cache.save(d, _make_ois(d), _make_nss(d))
        cache._m["max_unpinned"] = 10

    cache.pin("2026-01-01")
    cache.clean(keep=1)

    assert cache.has("2026-01-01"), "pinned date must not be evicted"


def test_auto_eviction_on_save(cache):
    cache._m["max_unpinned"] = 2
    cache._save()

    for d in ["2026-01-01", "2026-02-01", "2026-03-01"]:
        cache.save(d, _make_ois(d), _make_nss(d))

    unpinned = [d for d, v in cache._m["dates"].items() if not v.get("pinned")]
    assert len(unpinned) <= 2


def test_eviction_deletes_files_from_disk(cache, tmp_path):
    cache._m["max_unpinned"] = 1
    cache._save()

    cache.save("2026-01-01", _make_ois("2026-01-01"), _make_nss("2026-01-01"))
    cache.save("2026-02-01", _make_ois("2026-02-01"), _make_nss("2026-02-01"))

    assert not (tmp_path / "ois_curve_2026-01-01.parquet").exists()
    assert not (tmp_path / "nss_params_2026-01-01.json").exists()


# ── manifest persistence ──────────────────────────────────────────────────────

def test_manifest_survives_reload(tmp_path):
    cache1 = DataCache(processed_dir=tmp_path)
    cache1.save("2026-01-15", _make_ois(), _make_nss())
    cache1.pin("2026-01-15")

    cache2 = DataCache(processed_dir=tmp_path)
    assert cache2.has("2026-01-15")
    assert cache2._m["dates"]["2026-01-15"]["pinned"] is True
