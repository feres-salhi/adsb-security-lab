"""Turn per-aircraft tracks into movement features: ground speed (km/h), climb rate (ft/s) and step distance (km)."""
import json
import csv
import math
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
files = sorted(DATA_DIR.glob("flights_*_tracks.json"))
if not files:
    print("No tracks file found. Run build_tracks.py first.")
    raise SystemExit

tracks_path = files[-1]
print(f"Reading tracks: {tracks_path.name}\n")
data = json.loads(tracks_path.read_text(encoding="utf-8"))

def parse_time(s):
    for fmt in ("%Y/%m/%d %H:%M:%S.%f", "%Y/%m/%d %H:%M:%S"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            continue
    return None

def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

rows = []
for hex_id, info in data.items():
    pts = info["points"]
    for a, b in zip(pts, pts[1:]):
        t1, t2 = parse_time(a["time"]), parse_time(b["time"])
        if not t1 or not t2:
            continue
        dt = (t2 - t1).total_seconds()
        if dt < 0.5 or dt > 120:
            continue
        dist = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
        speed_kmh = dist / dt * 3600
        if a["alt"] is not None and b["alt"] is not None:
            climb_rate_fps = abs(b["alt"] - a["alt"]) / dt   # feet per SECOND
        else:
            climb_rate_fps = 0.0
        rows.append({
            "hex": hex_id,
            "flight": info.get("callsign", ""),
            "dt_s": round(dt, 1),
            "dist_km": round(dist, 3),
            "speed_kmh": round(speed_kmh, 1),
            "climb_rate_fps": round(climb_rate_fps, 2),
        })

out = DATA_DIR / "features.csv"
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["hex", "flight", "dt_s", "dist_km", "speed_kmh", "climb_rate_fps"])
    w.writeheader()
    w.writerows(rows)

print(f"Feature rows: {len(rows)}\n")
if rows:
    sp = sorted(r["speed_kmh"] for r in rows)
    cr = sorted(r["climb_rate_fps"] for r in rows)
    def pct(a, p): return a[min(len(a) - 1, int(len(a) * p))]
    print("Ground speed (km/h):   median {:.0f}   95th {:.0f}   max {:.0f}".format(pct(sp,0.5), pct(sp,0.95), sp[-1]))
    print("Climb rate (ft/sec):   median {:.1f}   95th {:.1f}   max {:.1f}".format(pct(cr,0.5), pct(cr,0.95), cr[-1]))
print(f"\nSaved features to: {out.name}")