# Watchlist (streamers, sources, rules)

The autopilot reads this file on every run and adds to it (new facecam positions, notes on permissions).
Keep it short and factual. Write dates as YYYY-MM-DD.

## Block list (never clip without explicit permission from the operator)
- `<login>`: reason (for example: the creator has said publicly that they take down re-uploads).

## Allow list (permission or a clipping campaign is documented)
- `<login>` (EN): link to the campaign or the written permission, date checked.

## Campaign streamers (pick these first)
- `<login>`: what the campaign pays for, where its rules are, last checked YYYY-MM-DD.

## Facecam positions (fractions x:y:w:h of the 16:9 frame, for `cut.py --cam`)
| login | cam | checked | note |
|---|---|---|---|
| `example_streamer` | `0.7656:0.0278:0.2266:0.3056` | 2026-11-20 | cam top right; use `--layout blur` when the cam is hidden |

## Notes per streamer
- `<login>`: language, typical stream times (UTC), what kind of moments work, anything to avoid.
