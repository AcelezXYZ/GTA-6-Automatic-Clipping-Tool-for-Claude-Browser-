import subprocess, sys
import numpy as np

"""Loudness peaks in a scan window: the moments where the streamer (or the game) suddenly gets loud.

usage: python3 -I tools/peaks.py <file> <offset_in_vod_seconds> [count]
File time + offset = VOD time. Discard peaks with a median below -45 dB or a file time below 5 s
(muted parts because of music, and the start of the window).
"""
src, off = sys.argv[1], int(sys.argv[2])
top = int(sys.argv[3]) if len(sys.argv) > 3 else 8

raw = subprocess.run(["ffmpeg", "-v", "error", "-i", src, "-ac", "1", "-ar", "8000", "-f", "s16le", "-"],
                     capture_output=True, check=True).stdout
x = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768
n = len(x) // 8000
rms = np.sqrt((x[: n * 8000].reshape(n, 8000) ** 2).mean(1) + 1e-9)
db = 20 * np.log10(rms)
print("audio level: min %.0f, median %.0f, max %.0f dB; share of silence (< -60 dB): %.1f %%" % (db.min(), np.median(db), db.max(), 100*(db < -60).mean()))
db = np.maximum(db, -60)

# loudness relative to a moving median (300 s), then smoothed over 3 s
win = 300
med = np.array([np.median(db[max(0, i - win // 2): i + win // 2 + 1]) for i in range(n)])
d = db - med
d = np.convolve(d, np.ones(3) / 3, mode="same")

order = np.argsort(d)[::-1]
picked = []
for i in order:
    if all(abs(i - j) >= 90 for j in picked):
        picked.append(int(i))
    if len(picked) >= top:
        break
print(f"{src}: {n} s of audio")
for i in picked:
    t = off + i
    hh, mm, ss = t // 3600, (t % 3600) // 60, t % 60
    print(f"VOD {t:>6} s  ({hh}:{mm:02d}:{ss:02d})  file time {i:>5} s  peak {d[i]:+.1f} dB  abs {db[i]:.0f} dB  median {med[i]:.0f} dB")
