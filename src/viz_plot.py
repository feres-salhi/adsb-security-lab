"""Plot a real flight against a spoofed (teleporting) copy."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROOF_DIR = DATA_DIR.parent / "proof"
PROOF_DIR.mkdir(exist_ok=True)

files = sorted(DATA_DIR.glob("flights_*_tracks.json"))
if not files:
    print("No tracks file found. Run build_tracks.py first.")
    raise SystemExit
data = json.loads(files[-1].read_text(encoding="utf-8"))

hex_id, info = max(data.items(), key=lambda kv: len(kv[1]["points"]))
pts = info["points"]
real_lat = [p["lat"] for p in pts]
real_lon = [p["lon"] for p in pts]
flight = info.get("callsign") or hex_id

jump = len(pts) // 2
LAT_OFF, LON_OFF = 0.45, 0.65
fake_lat = [la if i < jump else la + LAT_OFF for i, la in enumerate(real_lat)]
fake_lon = [lo if i < jump else lo + LON_OFF for i, lo in enumerate(real_lon)]

plt.figure(figsize=(9, 9))
plt.plot(real_lon, real_lat, "-", color="#1565C0", linewidth=2.5, label=f"REAL flight {flight}")
plt.plot(fake_lon, fake_lat, "--", color="#D32F2F", linewidth=2.0, label="SPOOFED (teleport attack)")
plt.plot([real_lon[jump-1], fake_lon[jump]], [real_lat[jump-1], fake_lat[jump]],
         ":", color="#D32F2F", linewidth=1.5)
plt.scatter([real_lon[0]], [real_lat[0]], color="green", s=90, zorder=5, label="Start")
plt.scatter([fake_lon[jump]], [fake_lat[jump]], color="red", s=130, marker="X", zorder=5, label="Ghost teleport")

plt.title(f"Real flight vs spoofed (teleport) - {flight}")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.legend()
plt.grid(True, alpha=0.3)
plt.gca().set_aspect("equal", adjustable="datalim")

out = PROOF_DIR / "spoof_plot.png"
plt.savefig(out, dpi=130, bbox_inches="tight")
print(f"Saved image to: proof/{out.name}")