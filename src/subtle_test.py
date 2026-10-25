"""Ramp up progressively subtler spoofs to find where the detector starts to miss them."""
import random
from pathlib import Path
import joblib

random.seed(1)
BASE = Path(__file__).resolve().parent.parent
model = joblib.load(BASE / "models" / "detector.joblib")

DT = 10.0  # seconds between position reports (typical)

def rate_speed(speed_kmh, n=300):
    caught = 0
    for _ in range(n):
        s = speed_kmh + random.uniform(-20, 20)
        dist = s * DT / 3600.0           # distance moved at that speed
        feat = [s, random.uniform(0, 3), dist]
        if model.predict([feat])[0] == -1:
            caught += 1
    return caught / n * 100

def rate_climb(climb_fps, n=300):
    caught = 0
    for _ in range(n):
        c = max(climb_fps + random.uniform(-2, 2), 0)
        feat = [random.uniform(820, 860), c, random.uniform(1.5, 3.0)]
        if model.predict([feat])[0] == -1:
            caught += 1
    return caught / n * 100

print("SUBTLE SPEED SPOOFING  (normal cruise ~850, real max seen ~1090)\n")
print(f"{'fake speed km/h':>16}   {'caught %':>9}")
print("-" * 30)
for speed in [900, 1000, 1100, 1200, 1300, 1500, 1800, 2200, 3000]:
    print(f"{speed:>16}   {rate_speed(speed):>8.1f}%")

print("\nSUBTLE ALTITUDE SPOOFING  (normal climbs up to ~100 ft/s)\n")
print(f"{'fake climb ft/s':>16}   {'caught %':>9}")
print("-" * 30)
for climb in [50, 100, 150, 200, 300, 500, 1000]:
    print(f"{climb:>16}   {rate_climb(climb):>8.1f}%")