"""
Date-keyed local data cache for asset-pricing notebooks.

manifest.json  → committed to git  (records what dates are available)
*.parquet/json → gitignored         (actual data, never in the repo)

Quick reference
---------------
from nb_utils.cache import DataCache
cache = DataCache()
cache.list_dates()          # show what's available
cache.pin("2025-12-31")     # never evict this date
cache.unpin("2026-01-15")
cache.clean(keep=3)         # manual eviction
"""

import json
from pathlib import Path
from typing import Optional

_DEFAULT_MAX_UNPINNED = 3
_MANIFEST = "manifest.json"


class DataCache:
    def __init__(self, processed_dir: Optional[Path] = None):
        if processed_dir is None:
            processed_dir = Path(__file__).parent.parent / "data" / "processed"
        self.dir = Path(processed_dir)
        self.dir.mkdir(parents=True, exist_ok=True)
        self._path = self.dir / _MANIFEST
        self._m = self._load()

    # ── public ────────────────────────────────────────────────────────

    def has(self, date: str) -> bool:
        """True if all files for this date exist on disk."""
        entry = self._m["dates"].get(date)
        if not entry:
            return False
        return all((self.dir / f).exists() for f in entry.get("files", []))

    def list_dates(self) -> list[str]:
        dates = sorted(self._m["dates"])
        if not dates:
            print("Cache is empty.")
            return dates
        print("Cached dates:")
        for d in dates:
            tag = "  [pinned]" if self._m["dates"][d].get("pinned") else ""
            print(f"  {d}{tag}")
        return dates

    def pin(self, date: str):
        if date in self._m["dates"]:
            self._m["dates"][date]["pinned"] = True
            self._save()
            print(f"Pinned {date}.")
        else:
            print(f"{date} not in cache.")

    def unpin(self, date: str):
        if date in self._m["dates"]:
            self._m["dates"][date]["pinned"] = False
            self._save()

    def clean(self, keep: Optional[int] = None):
        """Delete oldest unpinned entries until count <= keep."""
        if keep is None:
            keep = self._m.get("max_unpinned", _DEFAULT_MAX_UNPINNED)
        unpinned = sorted(
            d for d, v in self._m["dates"].items() if not v.get("pinned")
        )
        while len(unpinned) > keep:
            oldest = unpinned.pop(0)
            self._delete(oldest)
            print(f"Cache: evicted {oldest}.")

    # ── save / load (called by nb_utils.setup) ────────────────────────

    def save(self, date: str, ois_curve, nss_curve):
        """Save both curves and run eviction. Atomic from the manifest's POV."""
        ois_file = f"ois_curve_{date}.parquet"
        nss_file = f"nss_params_{date}.json"

        ois_curve._ois_data.to_parquet(self.dir / ois_file)

        nss_payload = {**nss_curve.parameters, "valuation_date": nss_curve.valuation_date}
        (self.dir / nss_file).write_text(json.dumps(nss_payload, indent=2))

        self._m["dates"][date] = {
            "pinned": False,
            "files": [ois_file, nss_file],
        }
        self._save()
        self.clean()

    def load(self, date: str):
        """Return (ois_curve, nss_curve) for a cached date."""
        import pandas as pd
        from quant_risk.curves.ois import OISCurve
        from quant_risk.curves.nss import NSSCurve

        ois_data = pd.read_parquet(self.dir / f"ois_curve_{date}.parquet")
        ois_curve = OISCurve(ois_data)

        nss_raw = json.loads((self.dir / f"nss_params_{date}.json").read_text())
        val_date = nss_raw.pop("valuation_date")
        nss_curve = NSSCurve(nss_raw, valuation_date=val_date)

        return ois_curve, nss_curve

    # ── internal ──────────────────────────────────────────────────────

    def _delete(self, date: str):
        for f in self._m["dates"].pop(date, {}).get("files", []):
            p = self.dir / f
            if p.exists():
                p.unlink()
        self._save()

    def _load(self) -> dict:
        if self._path.exists():
            return json.loads(self._path.read_text())
        return {"max_unpinned": _DEFAULT_MAX_UNPINNED, "dates": {}}

    def _save(self):
        self._path.write_text(json.dumps(self._m, indent=2) + "\n")
