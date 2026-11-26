"""Contact sheet from single frames, meant to be viewed with Claude's Read tool (check scenes, check the layout).

usage:   python3 -I tools/contact_sheet.py <out.jpg> <columns> <tile_width> <file@t1,t2,...> [<file@t1,t2,...> ...]
example: python3 -I tools/contact_sheet.py /tmp/sheet.jpg 4 270 clip.mp4@1,6,12,18
Each tile shows its file time in seconds in the top left corner. Times are seconds inside that file.
"""
import subprocess, sys
from PIL import Image, ImageDraw

out, cols, tw = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
tiles = []
for arg in sys.argv[4:]:
    path, times = arg.rsplit("@", 1)
    for t in times.split(","):
        tmp = f"/tmp/cs_{abs(hash((path, t)))}.png"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", t, "-i", path, "-frames:v", "1", "-vf", f"scale={tw}:-2", tmp], check=True)
        im = Image.open(tmp).convert("RGB")
        ImageDraw.Draw(im).text((6, 6), f"{t}s", fill=(255, 255, 0))
        tiles.append(im)
w, h = tiles[0].size
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (w * cols, h * rows))
for i, im in enumerate(tiles):
    sheet.paste(im.resize((w, h)), ((i % cols) * w, (i // cols) * h))
sheet.save(out, quality=88)
print(out, sheet.size)
