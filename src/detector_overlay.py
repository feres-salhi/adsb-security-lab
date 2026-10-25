"""Draw a flight path and colour each segment by the detector's verdict: green = normal, red = flagged."""
import json
import math
from pathlib import Path
from datetime import datetime
import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"
PROOF_DIR = BASE / "proof"
PROOF_DIR.mkdir(exist_ok=True)

model = joblib.load(BASE / "models" / "detector.joblib")

files = sorted(DATA_DIR.glob("flights_*_tracks.json"))
data = json.loads(files[-1].read_text(encoding="utf-8"))
hex_id, info = max(data.items(), key=lambda kv: len(kv[1]["points"]))
pts = info["points"]
flight = info.get("callsign") or hex_id

# spoofed track: positions teleport halfway; times & altitudes kept real
jump = len(pts) // 2
LAT_OFF, LON_OFF = 0.45, 0.65
fake = [{"lat": p["lat"] + (LAT_OFF if i >= jump else 0),
         "lon": p["lon"] + (LON_OFF if i >= jump else 0),
         "alt": p["alt"], "time": p["time"]} for i, p in enumerate(pts)]

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
    dphi = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2 * R * math.asin(math.sqrt(a))

plt.figure(figsize=(9, 9))
normal = flagged = 0
for a, b in zip(fake, fake[1:]):
    t1, t2 = parse_time(a["time"]), parse_time(b["time"])
    if not t1 or not t2:
        continue
    dt = (t2 - t1).total_seconds()
    if dt <= 0:
        continue
    dist = haversine_km(a["lat"], a["lon"], b["lat"], b["lon"])
    speed = dist / dt * 3600
    climb = abs(b["alt"] - a["alt"]) / dt if (a["alt"] is not None and b["alt"] is not None) else 0.0
    pred = model.predict([[speed, climb, dist]])[0]
    if pred == 1:
        color, normal = "#2E7D32", normal + 1
    else:
        color, flagged = "#D32F2F", flagged + 1
    plt.plot([a["lon"], b["lon"]], [a["lat"], b["lat"]], "-", color=color, linewidth=2.5)

plt.scatter([fake[0]["lon"]], [fake[0]["lat"]], color="green", s=90, zorder=5)

legend = [
    Line2D([0], [0], color="#2E7D32", lw=3, label=f"Passed as normal ({normal})"),
    Line2D([0], [0], color="#D32F2F", lw=3, label=f"FLAGGED by AI ({flagged})"),
]
plt.legend(handles=legend)
plt.title(f"Detector verdict on a spoofed flight - {flight}")
plt.xlabel("Longitude"); plt.ylabel("Latitude")
plt.grid(True, alpha=0.3)
plt.gca().set_aspect("equal", adjustable="datalim")

out = PROOF_DIR / "detector_overlay.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print(f"Normal segments : {normal}")
print(f"Flagged segments: {flagged}")
print(f"Saved image to: proof/{out.name}")