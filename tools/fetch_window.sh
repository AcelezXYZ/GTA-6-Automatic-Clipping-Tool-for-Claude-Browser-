#!/bin/bash
# Download a 70-second window (peak +/- 35 s) in 720p60 and normalise it to a constant 30 fps.
# usage:  bash tools/fetch_window.sh <vod_id> <peak_s> <out_dir>
# result: <out_dir>/v<vod_id>_<peak_s>.mp4   (file time 35 s = VOD time <peak_s>)
# The normalisation (-vf fps=30) matters: without it timestamps and seeking drift.
set -u
vod=$1; p=$2; dir=$3
mkdir -p "$dir"; cd "$dir" || exit 1
s=$((p-35)); e=$((p+35)); [ $s -lt 0 ] && s=0
src="v${vod}_${p}.src.mp4"; out="v${vod}_${p}.mp4"
yt-dlp -q -N 2 -f "720p60/720p" --download-sections "*${s}-${e}" -o "$src" "https://www.twitch.tv/videos/${vod}" >/dev/null 2>&1
if [ -f "$src" ]; then
  ffmpeg -y -loglevel error -i "$src" -vf fps=30 -c:v libx264 -preset veryfast -crf 22 -pix_fmt yuv420p \
    -c:a aac -ar 48000 -b:a 160k "$out" && rm -f "$src"
  echo "ok $dir/$out $(ffprobe -v error -show_entries format=duration -of csv=p=0 "$out") s (window starts at VOD ${s} s)"
else
  echo "MISSING v${vod}_${p}"; exit 1
fi
