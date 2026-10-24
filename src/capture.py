import socket
import time
from datetime import datetime
from pathlib import Path

# Save into the project's data/ folder (one level up from src/)
DATA_DIR = Path(__file__).resolve().parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

HOST, PORT = "127.0.0.1", 30003  # dump1090's live data channel

stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outfile = DATA_DIR / f"flights_{stamp}.csv"

print(f"Saving to: {outfile}")
print("Connecting to dump1090 (port 30003)...  Press Ctrl+C to stop.\n")

count = 0
try:
    with open(outfile, "w", encoding="utf-8", newline="") as f:
        while True:
            try:
                with socket.create_connection((HOST, PORT), timeout=10) as sock:
                    print("Connected! Saving plane messages...\n")
                    for raw in sock.makefile("r"):
                        line = raw.strip()
                        if not line:
                            continue
                        f.write(line + "\n")
                        count += 1
                        if count % 25 == 0:
                            f.flush()
                            print(f"  messages saved: {count}", end="\r")
            except (ConnectionRefusedError, socket.timeout, OSError) as e:
                print(f"\nWaiting for dump1090... ({e}). Retrying in 3s.")
                time.sleep(3)
except KeyboardInterrupt:
    pass

print(f"\n\nStopped. Total messages saved: {count}")
print(f"File: {outfile}")