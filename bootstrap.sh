#!/usr/bin/env bash
# Sets up a fresh session for the clip autopilot. Usage: bash bootstrap.sh
# Checks the bundled scripts, system programs, Python packages and the Whisper model, and creates the work folder.
# Environment variables: GTAVI (default: this repo), WORK (default: $HOME/clip-work)
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
GTAVI="${GTAVI:-$HERE}"
WORK="${WORK:-$HOME/clip-work}"
ok=1

echo "== 1/5 Scripts"
for f in cut.py moments.py check.py common.py twitch.py; do
  [ -f "$GTAVI/scripts/$f" ] && echo "   $f: ok" || { echo "   $f: MISSING in $GTAVI/scripts"; ok=0; }
done

echo "== 2/5 Programs"
for t in ffmpeg ffprobe yt-dlp; do command -v "$t" >/dev/null 2>&1 && echo "   $t: ok" || { echo "   $t: MISSING"; ok=0; }; done

echo "== 3/5 Python packages"
need=""
for m in "yt_dlp:yt-dlp" "faster_whisper:faster-whisper" "numpy:numpy" "requests:requests" "truststore:truststore" "PIL:pillow" "cv2:opencv-python-headless"; do
  python3 -c "import ${m%%:*}" 2>/dev/null || need="$need ${m##*:}"
done
if [ -n "$need" ]; then
  echo "   installing:$need"
  pip install --break-system-packages -q $need 2>&1 | tail -2 || true
fi
python3 -c "import yt_dlp, faster_whisper, numpy, requests, PIL; print('   packages: ok')" 2>&1 | tail -1

echo "== 4/5 Whisper model (small, int8, CPU)"
python3 - <<'PY' 2>&1 | tail -3
try:
    from faster_whisper import WhisperModel
    WhisperModel("small", device="cpu", compute_type="int8")
    print("   model: ok")
except Exception as e:
    print("   model: ERROR", str(e)[:200])
PY

echo "== 5/5 Work folder"
mkdir -p "$WORK/media/raw" "$WORK/media/edits" "$WORK/jobs"
echo "   $WORK"
echo
echo "For the commands in RUNBOOK.md:  export GTAVI=$GTAVI CLIP_DESK_HOME=$WORK"
[ "$ok" = 1 ] && echo "BOOTSTRAP OK" || echo "BOOTSTRAP FAILED (see above)"
