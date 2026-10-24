import csv
from pathlib import Path
import joblib
from sklearn.ensemble import IsolationForest

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
feat_path = DATA_DIR / "features.csv"
if not feat_path.exists():
    print("features.csv not found. Run features.py first.")
    raise SystemExit

# Now using: speed, CLIMB RATE (per second), distance
X = []
with open(feat_path, encoding="utf-8") as f:
    for r in csv.DictReader(f):
        X.append([float(r["speed_kmh"]), float(r["climb_rate_fps"]), float(r["dist_km"])])

print(f"Training on {len(X)} normal movement steps...\n")

model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
model.fit(X)

preds = model.predict(X)
n_norm = sum(1 for p in preds if p == 1)
n_anom = sum(1 for p in preds if p == -1)
print(f"  judged normal : {n_norm}")
print(f"  judged weird  : {n_anom}")

MODELS_DIR = DATA_DIR.parent / "models"
MODELS_DIR.mkdir(exist_ok=True)
out = MODELS_DIR / "detector.joblib"
joblib.dump(model, out)
print(f"\nSaved updated detector to: models/{out.name}")