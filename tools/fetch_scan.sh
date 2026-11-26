#!/bin/bash
# Download a scan window in 160p (small and fast) to look for loudness peaks.
# usage: bash tools/fetch_scan.sh <vod_id> <start_s> <end_s> <out.mp4>
# Note: the yt-dlp warning "Unable to download JSON metadata: HTTP Error 403" is harmless, the download still works.
set -u
vod=$1; s=$2; e=$3; out=$4
yt-dlp -q -N 2 -f 160p --download-sections "*${s}-${e}" -o "$out" "https://www.twitch.tv/videos/${vod}" 2>&1 | grep -v "JSON metadata" || true
if [ -f "$out" ]; then echo "ok $out $(du -h "$out" | cut -f1)"; else echo "MISSING $out"; exit 1; fi
