"""Unit tests for nb_utils.setup."""

import matplotlib
matplotlib.use("Agg")  # headless — no display needed

import matplotlib.pyplot as plt
import pandas as pd
import pytest
from unittest.mock import MagicMock, patch

from nb_utils.setup import base, asset_pricing


# ── base() ────────────────────────────────────────────────────────────────────

def test_base_returns_numpy_pandas_matplotlib():
    import numpy as np
    result = base()
    assert len(result) == 3
    np_out, pd_out, plt_out = result
    assert np_out is np
    assert pd_out is pd
    assert plt_out is plt


def test_base_applies_pandas_float_format():
    base()
    fmt = pd.get_option("display.float_format")
    assert fmt(3.14159) == "3.141590"


def test_base_applies_rcparams():
    base()
    assert plt.rcParams["axes.grid"] is True
    assert plt.rcParams["axes.spines.top"] is False
    assert plt.rcParams["axes.spines.right"] is False


# ── asset_pricing() — cache hit path ─────────────────────────────────────────

def test_asset_pricing_uses_cache_on_hit(tmp_path):
    """Cache hit must not call OISCurve.from_ecb or NSSCurve.from_ecb."""
    import QuantLib as ql

    mock_ois = MagicMock()
    mock_ois.valuation_date = "2026-01-15"
    mock_nss = MagicMock()
    mock_nss.valuation_date = "2026-01-15"

    mock_cache = MagicMock()
    mock_cache.has.return_value = True
    mock_cache.load.return_value = (mock_ois, mock_nss)

    with patch("nb_utils.cache.DataCache", return_value=mock_cache), \
         patch("quant_risk.curves.ois.OISCurve") as MockOIS, \
         patch("quant_risk.curves.nss.NSSCurve") as MockNSS:

        asset_pricing("2026-01-15")

        mock_cache.load.assert_called_once_with("2026-01-15")
        MockOIS.from_ecb.assert_not_called()
        MockNSS.from_ecb.assert_not_called()


def test_asset_pricing_returns_five_values():
    mock_ois = MagicMock()
    mock_ois.valuation_date = "2026-01-15"
    mock_nss = MagicMock()

    mock_cache = MagicMock()
    mock_cache.has.return_value = True
    mock_cache.load.return_value = (mock_ois, mock_nss)

    with patch("nb_utils.cache.DataCache", return_value=mock_cache):
        result = asset_pricing("2026-01-15")

    assert len(result) == 5
    ois, nss, val_date, calendar, ql_mod = result
    assert ois is mock_ois
    assert nss is mock_nss


def test_asset_pricing_defaults_to_today():
    from datetime import date
    mock_ois = MagicMock()
    mock_ois.valuation_date = str(date.today())
    mock_cache = MagicMock()
    mock_cache.has.return_value = True
    mock_cache.load.return_value = (mock_ois, MagicMock())

    with patch("nb_utils.cache.DataCache", return_value=mock_cache):
        asset_pricing()

    mock_cache.has.assert_called_once_with(str(date.today()))
