#!/usr/bin/env python3
"""Snapshot the Prior Lake market numbers for the homepage into src/data/market.json.

Reads the public metrics endpoint on priorlake.realestate (the same numbers
that site shows), keeps only what the homepage displays, and writes JSON the
build imports. The homepage never fetches at build or view time, so a bad
response can't break a deploy.

Definitions come from PriorLake.RealEstate/scripts/compute-metrics.ts:
  medianSalePrice / medianDOM: closed sales in the last 6 months, compared
    with the same 6 months a year earlier.
  monthlyTrend[].closedCount: closed residential sales per calendar month.
  activeListings / pendingListings: residential listings for sale / under
    contract that the feed still shows. Before the Sept 25 2026 fix these
    also counted listings the feed had withdrawn, about double the real number.
  absorptionRate.value: months of supply, activeListings over the monthly
    pace of residential sales in the last 6 months.

Stdlib only so the weekly GitHub Action needs no installs. Fails loudly
(nonzero exit, no file written) if the response shape changes or the
numbers fail sanity checks.
"""

import json
import sys
import urllib.request
from pathlib import Path

SOURCE_URL = "https://www.priorlake.realestate/api/metrics"
OUT_PATH = Path(__file__).resolve().parent.parent / "src" / "data" / "market.json"


def fail(msg: str) -> None:
    sys.exit(f"refresh_market: {msg}; market.json left unchanged")


def main() -> None:
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "markgores.com market snapshot"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.load(r)
    except Exception as e:  # network error, non-JSON body, bot wall
        fail(f"could not read {SOURCE_URL} ({e})")

    try:
        price = data["medianSalePrice"]
        dom = data["medianDOM"]
        updated = str(data["lastUpdated"])[:10]  # YYYY-MM-DD
        trend = data["monthlyTrend"]
        snapshot = {
            "source": SOURCE_URL,
            "asOf": updated,
            "medianSalePrice": {"value": int(price["value"]), "prior": int(price["prior"]), "delta": float(price["delta"])},
            "medianDOM": {"value": int(dom["value"]), "prior": int(dom["prior"])},
            "forSale": int(data["activeListings"]),
            "underContract": int(data["pendingListings"]),
            "monthsOfSupply": float(data["absorptionRate"]["value"]),
            # Full months only: the current month is partial and would read as a drop.
            "monthly": [
                {"month": m["month"], "closed": int(m["closedCount"])}
                for m in trend
                if m["month"] < updated[:7]
            ][-12:],
        }
    except (KeyError, TypeError, ValueError) as e:
        fail(f"unexpected response shape ({e!r})")

    p = snapshot["medianSalePrice"]["value"]
    if not 150_000 <= p <= 2_000_000:
        fail(f"median sale price {p} out of range")
    if not 0 <= snapshot["medianDOM"]["value"] <= 365:
        fail(f"median days on market {snapshot['medianDOM']['value']} out of range")
    if not 20 <= snapshot["forSale"] <= 600 or not 0 <= snapshot["underContract"] <= 300:
        fail(f"inventory {snapshot['forSale']} for sale / {snapshot['underContract']} under contract out of range")
    if not 0 < snapshot["monthsOfSupply"] <= 24:
        fail(f"months of supply {snapshot['monthsOfSupply']} out of range")
    if len(snapshot["monthly"]) != 12 or sum(m["closed"] for m in snapshot["monthly"]) < 100:
        fail(f"monthly trend looks wrong: {snapshot['monthly']}")

    OUT_PATH.write_text(json.dumps(snapshot, indent=2) + "\n")
    print(f"wrote {OUT_PATH.name}: median ${p:,} as of {updated}")


if __name__ == "__main__":
    main()
