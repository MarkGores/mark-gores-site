#!/usr/bin/env python3
"""Bake south-metro market evidence for the /how-i-sell marketing plan page."""
import json
import sqlite3
from statistics import median

DB = "/Users/markmini/Projects/prior-lake-ecosystem/PriorLake.RealEstate/data/listings.db"
CITIES = ["Prior Lake", "Savage", "Shakopee", "Lakeville", "Burnsville", "Apple Valley", "Eagan"]
TODAY = "2026-07-08"
CLOSE_12MO = "2025-07-08"
CLOSE_24MO = "2024-07-08"

con = sqlite3.connect(DB)
con.row_factory = sqlite3.Row

def is_new(v):
    return v in (1, "1", "true", "True", "Y", "yes")

BASE = """
  FROM listings
  WHERE City IN ({cities})
    AND PropertyType = 'Residential'
    AND PropertySubType IN ('Single Family Residence', 'Single Family')
""".format(cities=",".join("?" * len(CITIES)))

# ---- closed rows, last 24 months ----
rows = con.execute(
    "SELECT City, ClosePrice, ListPrice, DaysOnMarket, LivingArea, CloseDate, NewConstructionYN "
    + BASE
    + " AND StandardStatus='Closed' AND CloseDate >= ? AND ClosePrice > 50000 AND ListPrice > 50000",
    (*CITIES, CLOSE_24MO),
).fetchall()

closed = []
for r in rows:
    if is_new(r["NewConstructionYN"]):
        continue
    ratio = r["ClosePrice"] / r["ListPrice"]
    if not (0.5 <= ratio <= 1.5):
        continue
    closed.append(dict(city=r["City"], close=r["ClosePrice"], ratio=ratio,
                       dom=r["DaysOnMarket"], area=r["LivingArea"], date=r["CloseDate"]))

last12 = [c for c in closed if c["date"] >= CLOSE_12MO]

# ---- city pulse (last 12 months) ----
pulse = []
for city in CITIES:
    cc = [c for c in last12 if c["city"] == city]
    doms = [c["dom"] for c in cc if c["dom"] is not None]
    ppsf = [c["close"] / c["area"] for c in cc if c["area"] and c["area"] > 300]
    pulse.append(dict(
        city=city, n=len(cc),
        medClose=round(median(c["close"] for c in cc)) if cc else None,
        medDom=round(median(doms)) if doms else None,
        medPpsf=round(median(ppsf)) if ppsf else None,
    ))

# ---- monthly median close, per city + overall, 24 full months 2024-07..2026-06 ----
months = []
y, m = 2024, 7
for _ in range(24):
    months.append(f"{y:04d}-{m:02d}")
    m += 1
    if m == 13:
        y, m = y + 1, 1

def monthly_series(pred):
    out = []
    for mo in months:
        vals = [c["close"] for c in closed if c["date"][:7] == mo and pred(c)]
        out.append(round(median(vals)) if vals else None)
    return out

series = {city: monthly_series(lambda c, ct=city: c["city"] == ct) for city in CITIES}
series["South metro"] = monthly_series(lambda c: True)

# ---- DOM buckets x price band (last 24 months) ----
BUCKETS = [(0, 7, "0-7"), (8, 14, "8-14"), (15, 30, "15-30"), (31, 60, "31-60"), (61, 90, "61-90"), (91, 10**6, "91+")]
def band_of(c):
    if c["close"] < 400_000: return "under400"
    if c["close"] < 600_000: return "b400600"
    return "over600"

curve = {}
for band in ["all", "under400", "b400600", "over600"]:
    rows_b = [c for c in closed if c["dom"] is not None and (band == "all" or band_of(c) == band)]
    out = []
    for lo, hi, label in BUCKETS:
        vals = [c["ratio"] for c in rows_b if lo <= c["dom"] <= hi]
        over = [v for v in vals if v >= 1.0]
        out.append(dict(bucket=label, n=len(vals),
                        medRatio=round(100 * median(vals), 1) if vals else None,
                        pctAtOrOver=round(100 * len(over) / len(vals)) if vals else None))
    curve[band] = out

# headline pair
fast = [c["ratio"] for c in closed if c["dom"] is not None and c["dom"] <= 14]
slow = [c["ratio"] for c in closed if c["dom"] is not None and c["dom"] >= 91]
headline = dict(
    fastMed=round(100 * median(fast), 1), fastN=len(fast),
    slowMed=round(100 * median(slow), 1), slowN=len(slow),
    fastOver=round(100 * len([v for v in fast if v >= 1.0]) / len(fast)),
)

# ---- actives snapshot ----
arows = con.execute(
    "SELECT ListPrice, DaysOnMarket, NewConstructionYN " + BASE + " AND StandardStatus='Active' AND ListPrice > 50000",
    (*CITIES,),
).fetchall()
resale_actives = [r for r in arows if not is_new(r["NewConstructionYN"])]
new_actives = [r for r in arows if is_new(r["NewConstructionYN"])]
actives = dict(
    resale=len(resale_actives),
    newConstruction=len(new_actives),
    medList=round(median(r["ListPrice"] for r in resale_actives)) if resale_actives else None,
    medDom=round(median(r["DaysOnMarket"] for r in resale_actives if r["DaysOnMarket"] is not None)),
)

# sanity: total closes 12mo
result = dict(asOf=TODAY, cities=CITIES, pulse=pulse, months=months, series=series,
              curve=curve, headline=headline, actives=actives,
              n12=len(last12), n24=len(closed))
print(json.dumps(result, indent=1))
