import csv
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

files = sorted(DATA_DIR.glob("flights_*.csv"))
if not files:
    print("No capture files found in data/. Run capture.py first.")
    raise SystemExit

path = files[-1]  # newest capture
print(f"Reading: {path.name}\n")

total = 0
planes = {}

with open(path, encoding="utf-8") as f:
    for row in csv.reader(f):
        if not row or row[0] != "MSG":
            continue
        total += 1
        hex_id = row[4].strip() if len(row) > 4 else ""
        if not hex_id:
            continue
        info = planes.setdefault(hex_id, {"flight": "", "alt": "", "lat": "", "lon": "", "msgs": 0})
        info["msgs"] += 1
        if len(row) > 10 and row[10].strip(): info["flight"] = row[10].strip()
        if len(row) > 11 and row[11].strip(): info["alt"]    = row[11].strip()
        if len(row) > 14 and row[14].strip(): info["lat"]    = row[14].strip()
        if len(row) > 15 and row[15].strip(): info["lon"]    = row[15].strip()

print(f"Total messages: {total}")
print(f"Unique aircraft: {len(planes)}\n")
print(f"{'HEX':<8} {'FLIGHT':<9} {'ALT':>7} {'LAT':>9} {'LON':>9} {'MSGS':>6}")
print("-" * 52)
for hex_id, info in list(planes.items())[:12]:
    print(f"{hex_id:<8} {info['flight']:<9} {info['alt']:>7} {info['lat']:>9} {info['lon']:>9} {info['msgs']:>6}")