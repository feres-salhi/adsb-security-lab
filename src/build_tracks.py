"""Group raw decoded ADS-B messages into per-aircraft tracks, ordered by time."""
import csv
import json
from pathlib import Path
from collections import defaultdict

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
files = sorted(DATA_DIR.glob("flights_*.csv"))
if not files:
    print("No capture files found. Run capture.py first.")
    raise SystemExit

path = files[-1]
print(f"Reading: {path.name}\n")

tracks = defaultdict(list)
callsigns = {}

with open(path, encoding="utf-8") as f:
    for row in csv.reader(f):
        if not row or row[0] != "MSG" or len(row) < 16:
            continue
        hex_id = row[4].strip()
        if not hex_id:
            continue
        if row[10].strip():
            callsigns[hex_id] = row[10].strip()
        lat, lon, alt = row[14].strip(), row[15].strip(), row[11].strip()
        if lat and lon:
            tracks[hex_id].append({
                "time": row[6].strip() + " " + row[7].strip(),
                "lat": float(lat),
                "lon": float(lon),
                "alt": int(alt) if alt else None,
            })

for hex_id in tracks:
    tracks[hex_id].sort(key=lambda p: p["time"])

out = DATA_DIR / (path.stem + "_tracks.json")
dataset = {h: {"callsign": callsigns.get(h, ""), "points": pts} for h, pts in tracks.items()}
with open(out, "w", encoding="utf-8") as f:
    json.dump(dataset, f, indent=2)

print(f"{'HEX':<8} {'FLIGHT':<9} {'POINTS':>6}")
print("-" * 26)
for hex_id, pts in sorted(tracks.items(), key=lambda kv: len(kv[1]), reverse=True):
    print(f"{hex_id:<8} {callsigns.get(hex_id, ''):<9} {len(pts):>6}")

n30 = sum(1 for pts in tracks.values() if len(pts) >= 30)
n10 = sum(1 for pts in tracks.values() if len(pts) >= 10)
print("\n" + "=" * 34)
print(f"Planes with 30+ points : {n30}")
print(f"Planes with 10+ points : {n10}")
print(f"Total planes with a path: {len(tracks)}")
print("=" * 34)
print("Ready to build the model when 30+ points reaches ~15-20.")