"""Measure detection rate, false-alarm rate and precision on a held-out test set."""
import csv
import random
from pathlib import Path
from sklearn.ensemble import IsolationForest

random.seed(42)
BASE = Path(__file__).resolve().parent.parent
DATA_DIR = BASE / "data"

# 1) Load real normal movement steps
real = []
with open(DATA_DIR / "features.csv", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        real.append([float(r["speed_kmh"]), float(r["climb_rate_fps"]), float(r["dist_km"])])

random.shuffle(real)
split = int(len(real) * 0.8)
train, test_normal = real[:split], real[split:]

# 2) Train on the 80% of NORMAL data only
model = IsolationForest(n_estimators=200, contamination=0.02, random_state=42)
model.fit(train)

# 3) Generate many fake ATTACK steps of several spoofing types
def make_attacks(n):
    out = []
    for _ in range(n):
        kind = random.choice(["teleport", "alt_teleport", "ghost_jump", "hypersonic"])
        if kind == "teleport":
            out.append([random.uniform(2000, 8000), random.uniform(0, 5), random.uniform(20, 120)])
        elif kind == "alt_teleport":
            out.append([random.uniform(600, 950), random.uniform(300, 2000), random.uniform(1, 4)])
        elif kind == "ghost_jump":
            out.append([random.uniform(4000, 15000), random.uniform(0, 5), random.uniform(80, 400)])
        else:
            out.append([random.uniform(9000, 20000), random.uniform(0, 10), random.uniform(60, 300)])
    return out

attacks = make_attacks(len(test_normal))

# 4) Labeled test set:  1 = real/normal , -1 = attack  (matches model output)
X_test = test_normal + attacks
y_true = [1] * len(test_normal) + [-1] * len(attacks)
y_pred = model.predict(X_test)

# 5) Score it
TP = sum(1 for t, p in zip(y_true, y_pred) if t == -1 and p == -1)  # attack caught
FN = sum(1 for t, p in zip(y_true, y_pred) if t == -1 and p == 1)   # attack missed
TN = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1)    # real ok
FP = sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == -1)   # false alarm

detection = TP / (TP + FN) * 100
false_alarm = FP / (FP + TN) * 100
precision = TP / (TP + FP) * 100 if (TP + FP) else 0

print("=" * 46)
print("   EVALUATION - spoof detector")
print("=" * 46)
print(f"Tested on {len(test_normal)} real + {len(attacks)} fake (unseen)\n")
print(f"Attacks caught (detection rate): {detection:5.1f}%   ({TP}/{TP+FN})")
print(f"False alarms on real flights   : {false_alarm:5.1f}%   ({FP}/{FP+TN})")
print(f"Precision of its alarms        : {precision:5.1f}%")
print()
print("Confusion matrix (scoreboard):")
print("                    said ATTACK    said normal")
print(f"  really ATTACK        {TP:5d}          {FN:5d}")
print(f"  really normal        {FP:5d}          {TN:5d}")
print("=" * 46)