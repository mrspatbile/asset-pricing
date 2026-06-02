def base():
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt

    pd.set_option("display.float_format", "{:.6f}".format)

    plt.rcParams.update({
        'font.size': 8,
        'axes.titlesize': 10,
        'axes.labelsize': 8,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'legend.fontsize': 7,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.spines.left': False,
        'axes.linewidth': 1.5,
        'axes.grid': True,
        'axes.grid.axis': 'y',
        'grid.color': '#e0e0e0',
        'grid.linewidth': 0.6,
    })

    return np, pd, plt


def asset_pricing(date: str = None):
    """
    Load OIS and NSS curves for the given date.

    Parameters
    ----------
    date : str, optional
        ISO date string, e.g. '2025-12-31'. Defaults to today.
        - Cache hit  → loaded from data/processed/ instantly.
        - Cache miss → fetched live from ECB, saved to cache,
                       oldest unpinned entry evicted if cache is full.

    Returns
    -------
    ois_curve, nss_curve, valuation_date, calendar, ql

    Examples
    --------
    # use today (or nearest available ECB date)
    ois, nss, val_date, cal, ql = asset_pricing()

    # specific historical date (must be in cache or fetchable from ECB)
    ois, nss, val_date, cal, ql = asset_pricing("2025-12-31")
    """
    import QuantLib as ql
    from datetime import date as _date
    from nb_utils.cache import DataCache

    if date is None:
        date = str(_date.today())

    cache = DataCache()

    if cache.has(date):
        ois_curve, nss_curve = cache.load(date)
        print(f"Loaded from cache  : {date}")
    else:
        from quant_risk.curves.ois import OISCurve
        from quant_risk.curves.nss import NSSCurve

        ois_curve = OISCurve.from_ecb()
        nss_curve = NSSCurve.from_ecb(rating="AAA", date=date)

        actual = ois_curve.valuation_date
        cache.save(actual, ois_curve, nss_curve)

        if actual != date:
            print(f"Note: requested {date}, nearest ECB date is {actual}")
        else:
            print(f"Fetched and cached : {actual}")

    val_parts      = ois_curve.valuation_date.split("-")
    valuation_date = ql.Date(int(val_parts[2]), int(val_parts[1]), int(val_parts[0]))
    ql.Settings.instance().evaluationDate = valuation_date
    calendar       = ql.TARGET()

    cache.list_dates()
    return ois_curve, nss_curve, valuation_date, calendar, ql


def macro():
    from quant_risk.config import FRED_API_KEY
    from quant_risk.data.fed import FedClient
    from quant_risk.data.fed_store import FREDStore
    from quant_risk.data.external_store import ExternalStore

    if FRED_API_KEY is None:
        raise ValueError("FRED_API_KEY missing in config")

    fed_client     = FedClient(api_key=FRED_API_KEY)
    store          = FREDStore(FRED_API_KEY)
    external_store = ExternalStore()

    return fed_client, store, external_store
