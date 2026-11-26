"""Cut a time window out of a Twitch VOD by downloading the HLS segments directly.

Why: for VODs of streams that are still live (playlist type EVENT), `yt-dlp --download-sections` hangs in ffmpeg
(ffmpeg seeks inside the growing playlist and has written 0 bytes after 10 minutes). This script picks the segments
from the playlist by their real duration (EXTINF), downloads them in parallel and trims them exactly with ffmpeg.
It uses the same public CDN URLs that yt-dlp returns. No login, no bypassing of blocks.

usage:  python3 -I tools/hls_cut.py <vod_id> <start_s> <end_s> <out.mp4> [--quality 160p|720p60] [--norm30]
  --norm30: like fetch_window.sh, normalise to a constant 30 fps (libx264/aac). Without it: stream copy (for scan windows).
"""
import argparse, os, re, subprocess, sys, tempfile
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urljoin

import requests

# Optional custom CA bundle (for example behind a corporate or sandbox proxy); otherwise the system default is used.
CA = os.environ.get("REQUESTS_CA_BUNDLE") or "/root/.ccr/ca-bundle.crt"


def get(url, tries=4):
    last = None
    for _ in range(tries):
        try:
            r = requests.get(url, timeout=30, verify=CA if os.path.exists(CA) else True)
            if r.status_code == 200:
                return r.content
            last = "HTTP %s" % r.status_code
            if r.status_code in (403, 401):
                break  # blocked: do not try to get around it
        except requests.RequestException as e:
            last = str(e)[:120]
    raise RuntimeError("%s: %s" % (url.rsplit("/", 1)[-1], last))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vod")
    ap.add_argument("start", type=float)
    ap.add_argument("end", type=float)
    ap.add_argument("out")
    ap.add_argument("--quality", default="160p")
    ap.add_argument("--norm30", action="store_true")
    ap.add_argument("--threads", type=int, default=12)
    a = ap.parse_args()

    r = subprocess.run(["yt-dlp", "-q", "-f", a.quality, "-g", "https://www.twitch.tv/videos/" + a.vod],
                       capture_output=True, text=True, timeout=90)
    lines = [l for l in r.stdout.splitlines() if l.startswith("http")]
    if not lines:
        sys.exit("MISSING: no playlist URL (%s)" % r.stderr.strip()[-200:])
    m3u8 = lines[0]
    pl = get(m3u8).decode()

    segs, t, dur, init = [], 0.0, None, None
    for ln in pl.splitlines():
        if ln.startswith("#EXT-X-MAP:"):
            mm = re.search(r'URI="([^"]+)"', ln)
            if mm:
                init = urljoin(m3u8, mm.group(1))  # fMP4 VODs: put the init segment in front of the fragments
        elif ln.startswith("#EXTINF:"):
            dur = float(ln[8:].split(",")[0])
        elif ln and not ln.startswith("#") and dur is not None:
            segs.append((t, dur, urljoin(m3u8, ln)))
            t += dur
            dur = None
    pick = [s for s in segs if s[0] + s[1] > a.start and s[0] < a.end]
    if not pick:
        sys.exit("MISSING: no segments in window %s-%s (VOD is %.0f s long)" % (a.start, a.end, t))
    off = a.start - pick[0][0]

    with tempfile.TemporaryDirectory(dir=os.path.dirname(os.path.abspath(a.out))) as tmp:
        def dl(i_s):
            i, s = i_s
            p = os.path.join(tmp, "%06d.ts" % i)
            with open(p, "wb") as f:
                f.write(get(s[2]))
            return p
        with ThreadPoolExecutor(a.threads) as ex:
            files = list(ex.map(dl, enumerate(pick)))
        cat = os.path.join(tmp, "all.mp4" if init else "all.ts")
        with open(cat, "wb") as w:
            if init:
                w.write(get(init))
            for p in files:
                with open(p, "rb") as f:
                    w.write(f.read())
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-ss", "%.3f" % off, "-t", "%.3f" % (a.end - a.start), "-i", cat]
        if a.norm30:
            cmd += ["-vf", "fps=30", "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
                    "-c:a", "aac", "-ar", "48000", "-b:a", "160k"]
        else:
            cmd += ["-c", "copy"]
        cmd += [a.out]
        subprocess.run(cmd, check=True)
    d = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", a.out],
                       capture_output=True, text=True).stdout.strip()
    print("ok %s %s s (VOD %s-%s s, %d segments)" % (a.out, d, a.start, a.end, len(pick)))


if __name__ == "__main__":
    main()
