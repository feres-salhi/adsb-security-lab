\# ADS-B Spoofing Detector



A proof-of-concept that captures \*\*live aircraft signals\*\* with a low-cost software-defined radio, trains a machine-learning model to recognise normal flight, and detects \*\*spoofed (fake) aircraft\*\* — then red-teams itself to find where it breaks.



Built end-to-end on self-captured data with a \~€27 RTL-SDR dongle.



\---



\## The problem



Aircraft continuously broadcast their identity, position, speed and altitude over an open radio protocol called \*\*ADS-B\*\* (1090 MHz). These broadcasts are \*\*unauthenticated and unencrypted\*\* — anyone can forge them, injecting "ghost" aircraft or faking a plane's position. This is a well-known, still-unsolved weakness in aviation. This project builds a \*\*detection layer\*\*: it can't stop fake signals, but it can flag when the data defies physics.



\## What it does



```

Capture live radio  ->  Decode to messages  ->  Build flight tracks

&#x20;  ->  Extract movement features  ->  Train anomaly detector

&#x20;  ->  Attack it with fakes  ->  Harden it  ->  Evaluate \& stress-test

```



The detector learns what \*normal\* movement looks like (speed, climb rate, step distance) and flags any movement that falls far outside it.



\## Results



Measured on a \*\*held-out test set\*\* the model never saw during training:



| Metric | Result |

|---|---|

| Detection rate (blatant synthetic attacks) | \*\*100%\*\* (310/310) |

| False-alarm rate on real flights | \*\*1.6%\*\* (5/310) |

| Precision | \*\*98.4%\*\* |



\*\*Red-team hardening:\*\* an early version wrongly flagged a normal \*climbing\* plane. Root cause: the altitude feature used the raw altitude change and ignored the time gap. Switching to \*\*climb rate (ft/s)\*\* fixed the false alarm while keeping all attack catches.



\*\*Stress test — where it breaks (honest limits):\*\*



\- \*\*Speed:\*\* fakes below \~1100 km/h (within the real speed range observed) \*\*evade\*\* detection; detection ramps up above \~1200 km/h and is reliable by \~1800 km/h.

\- \*\*Altitude:\*\* over-sensitive — flags even mild climbs (\~50 ft/s), so it would false-alarm on real climbing/descending aircraft.



Both weaknesses trace to the \*\*training data\*\*: captures were dominated by high-altitude \*cruise\* traffic, so the model knows cruise speed well but rarely saw altitude changes.



\## How it works



\- \*\*Data:\*\* a short live capture in the Rhine-Main area (near Frankfurt, Germany) produced tens of thousands of raw ADS-B messages. After decoding and cleaning: \~35 aircraft trajectories and \*\*1,549 movement-steps\*\* used to train and evaluate.

\- \*\*Features per movement-step:\*\* ground speed (km/h), climb rate (ft/s), step distance (km).

\- \*\*Observed "normal" ranges:\*\* cruise speed median \~834 km/h (max \~1,088); climb rate median 0, 95th percentile \~27 ft/s (max \~99).

\- \*\*Model:\*\* Isolation Forest (unsupervised anomaly detection), 200 trees, 2% contamination. No labelled attacks needed — it learns normal and flags outliers.

\- \*\*Simulated attacks (software only, never transmitted):\*\* teleport / impossible speed, ghost jump, altitude teleport, hypersonic, and graduated \*subtle\* speed/altitude spoofs.



\## Project structure



```

adsb-security-lab/

|- data/      captured messages, flight tracks, features

|- models/    trained detector (detector.joblib)

|- proof/     result screenshots

|- src/

|  |- capture.py           tap live decoded data, save to file

|  |- build\_tracks.py      group messages into per-plane tracks

|  |- explore.py           summarise a capture

|  |- features.py          turn tracks into movement features

|  |- train.py             train the Isolation Forest detector

|  |- attack\_test.py       fire hand-crafted fake planes at it

|  |- evaluate.py          held-out test: detection / false-alarm / precision

|  |- subtle\_test.py       ramp up subtle attacks to find breaking points

|  |- viz\_plot.py          plot real vs spoofed flight path

|  |- detector\_overlay.py  colour each path segment by the detector's verdict

```



\## How to run



Prerequisites: a genuine RTL-SDR dongle (RTL2832U + R820T2), the Zadig driver, `dump1090` for decoding, and Python with `scikit-learn`, `matplotlib`, `folium`, `joblib`.



```

\# 1) Start the decoder (serves live data on port 30003)

dump1090.exe --interactive --net --device-index 1



\# 2) Capture, process, train

python src/capture.py          # let it run, Ctrl+C to stop

python src/build\_tracks.py

python src/features.py

python src/train.py



\# 3) Attack, evaluate, stress-test

python src/attack\_test.py

python src/evaluate.py

python src/subtle\_test.py



\# 4) Visualise

python src/viz\_plot.py

python src/detector\_overlay.py

```



\## Screenshots



\- `proof/01\_first\_planes\_decoded.png` — live aircraft decoded from the stick

\- `proof/spoof\_plot.png` — real flight vs a spoofed teleport

\- `proof/detector\_overlay.png` — the detector's verdict painted onto a spoofed flight (green = normal, red = flagged)



\## Limitations \& future work



\- Single receiver = local, line-of-sight coverage only; tracks are partial segments, not whole flights.

\- Speed evasion gap below \~1100 km/h and altitude over-sensitivity, both from cruise-heavy data.

\- Synthetic attacks are generated by rule, not replayed from real incidents.

\- Next: capture varied flight phases (climb/descent, lower altitudes) to broaden "normal"; try a sequence model (per-track, not per-step); add a physics/plausibility cross-check.



\## Ethical \& legal note



Fully \*\*receive-only\*\* — the radio cannot transmit, and all spoofing is simulated in software and \*\*never broadcast\*\*. Passive reception of open ADS-B broadcasts for research is legal in Germany; transmitting on these bands is not.



\## Author



Fares Salhi — B.Sc. Computer Science, TU Darmstadt. Focus on AI and AI security.

