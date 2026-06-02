"""
Pre-populate the local data cache without opening a notebook.

Usage
-----
# fetch today's data
python scripts/build_dataset.py

# fetch a specific date
python scripts/build_dataset.py --date 2025-12-31

# fetch and pin (never evict)
python scripts/build_dataset.py --date 2025-12-31 --pin

# show what's currently cached
python scripts/build_dataset.py --list
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


def main():
    parser = argparse.ArgumentParser(description="Build asset pricing dataset cache")
    parser.add_argument("--date", default=None, help="ISO date to fetch (default: today)")
    parser.add_argument("--pin", action="store_true", help="Pin this date (never evict)")
    parser.add_argument("--list", action="store_true", help="List cached dates and exit")
    args = parser.parse_args()

    from nb_utils.cache import DataCache
    cache = DataCache()

    if args.list:
        cache.list_dates()
        return

    from nb_utils.setup import asset_pricing
    asset_pricing(date=args.date)

    if args.pin and args.date:
        from datetime import date as _date
        cache.pin(args.date or str(_date.today()))


if __name__ == "__main__":
    main()
