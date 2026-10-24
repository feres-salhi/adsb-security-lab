import json
from pathlib import Path
import folium

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
PROOF_DIR = DATA_DIR.parent / "proof"
PROOF_DIR.mkdir(exist_ok=True)

files = sorted(DATA_DIR.glob("flights_*_tracks.json"))
if not files:
    print("No tracks file found. Run build_tracks.py first.")
    raise SystemExit
data = json.loads(files[-1].read_text(encoding="utf-8"))

# richest real track = plane with the most position points
hex_id, info = max(data.items(), key=lambda kv: len(kv[1]["points"]))
pts = info["points"]
real = [[p["lat"], p["lon"]] for p in pts]
flight = info.get("callsign") or hex_id
print(f"Real flight: {flight}  ({len(real)} points)")

# spoofed version: follow the real path, then TELEPORT halfway
jump = len(real) // 2
LAT_OFF, LON_OFF = 0.45, 0.65   # ~60-70 km sudden jump
fake = [[la, lo] if i < jump else [la + LAT_OFF, lo + LON_OFF]
        for i, (la, lo) in enumerate(real)]
teleport_from = real[jump - 1]
teleport_to = [real[jump][0] + LAT_OFF, real[jump][1] + LON_OFF]

clat = sum(p[0] for p in real) / len(real)
clon = sum(p[1] for p in real) / len(real)
m = folium.Map(location=[clat, clon], tiles="CartoDB positron")

folium.PolyLine(real, color="#1565C0", weight=4, opacity=0.9,
                tooltip=f"REAL flight {flight}").add_to(m)
folium.PolyLine(fake, color="#D32F2F", weight=3, opacity=0.9, dash_array="8",
                tooltip="SPOOFED flight (teleport attack)").add_to(m)
folium.PolyLine([teleport_from, teleport_to], color="#D32F2F", weight=2,
                dash_array="2").add_to(m)

folium.Marker(real[0], tooltip="Start",
              icon=folium.Icon(color="green", icon="play")).add_to(m)
folium.Marker(real[-1], tooltip=f"REAL end — {flight}",
              icon=folium.Icon(color="blue", icon="stop")).add_to(m)
folium.Marker(teleport_to, tooltip="Ghost teleport! (impossible jump)",
              icon=folium.Icon(color="red", icon="warning-sign")).add_to(m)

lats = [p[0] for p in real + fake]
lons = [p[1] for p in real + fake]
m.fit_bounds([[min(lats), min(lons)], [max(lats), max(lons)]])

out = PROOF_DIR / "spoof_map.html"
m.save(str(out))
print(f"Saved map to: proof/{out.name}")