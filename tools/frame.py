"""Single full-resolution frame, optionally an enlarged crop (to find the facecam position).

usage:   python3 -I tools/frame.py <video> <t_seconds> <out.png> [x0 y0 x1 y1 zoom]
example (facecam on the right, 1280x720 frame): python3 -I tools/frame.py v.mp4 36 /tmp/cam.png 880 180 1280 520 2
Coordinates are pixels in the original frame. Convert the facecam border to fractions: x=px/1280, y=px/720, w=width/1280, h=height/720.
"""
import subprocess, sys
from PIL import Image

video, t, out = sys.argv[1], sys.argv[2], sys.argv[3]
subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", t, "-i", video, "-frames:v", "1", out], check=True)
im = Image.open(out)
print("frame size", im.size)
if len(sys.argv) >= 8:
    x0, y0, x1, y1 = map(int, sys.argv[4:8])
    k = float(sys.argv[8]) if len(sys.argv) > 8 else 2
    c = im.crop((x0, y0, x1, y1))
    c.resize((int(c.size[0] * k), int(c.size[1] * k))).save(out)
    print("crop saved", out)
