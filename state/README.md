# state/

The autopilot's memory between runs. Every run reads these files first and writes to them at the end, then commits.

| File | What it holds |
|---|---|
| `watchlist.md` | block list, allow list, campaign streamers, facecam positions, notes |
| `campaigns.md` | campaign rules in a format `scripts/check.py` understands |
| `runs.jsonl` | one JSON line per run: which streamer, VOD, scanned windows and peaks were used |
| `log.md` | a short human-readable log, 3 to 5 lines per run |

These are templates. Your own copies will contain the streamers you clip and your campaign links,
so think twice before you push them to a **public** fork. A private repo for your state is the safer setup.
