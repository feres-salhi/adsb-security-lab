"""Fire hand-crafted spoofing attacks (teleport, impossible speed, ghost jump) at the trained detector and report which are caught."""
import joblib
from pathlib import Path

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"
model = joblib.load(MODELS_DIR / "detector.joblib")

# (name, [speed_kmh, climb_rate_fps, dist_km])
cases = [
    ("Normal cruise (control)",          [830,     0.0,   2.0]),
    ("Normal climb 20 ft/s (control)",   [780,    20.0,   1.5]),
    ("Teleport: impossible speed",       [5000,    0.0,  60.0]),
    ("Ghost jump: 200 km in 1 step",     [9000,    0.0, 200.0]),
    ("Altitude teleport: 1000 ft/s",     [800,  1000.0,   2.0]),
    ("Hypersonic fake",                  [12000,   0.0, 120.0]),
    ("Subtle: a bit too fast",           [1500,    0.0,  20.0]),
]

print(f"{'CASE':<34}{'SPEED':>7}{'CLIMB':>8}{'DIST':>8}   VERDICT")
print("-" * 80)
for name, feat in cases:
    pred = model.predict([feat])[0]
    score = model.decision_function([feat])[0]
    verdict = "NORMAL" if pred == 1 else ">>> FLAGGED (attack) <<<"
    print(f"{name:<34}{feat[0]:>7}{feat[1]:>8}{feat[2]:>8}   {verdict}  (score {score:+.3f})")