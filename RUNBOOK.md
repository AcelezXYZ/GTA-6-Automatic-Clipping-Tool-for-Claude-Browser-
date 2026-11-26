# RUNBOOK: GTA 6 clip autopilot

Written for **Claude in a fresh session** (Claude Code on the web, a scheduled task, or a local Claude Code).
Every run delivers **3 finished YouTube Shorts** (1080x1920, word-by-word captions, title, credit) plus a title and
description for each one to **the operator** (the person who owns the page). **The operator posts them by hand.**
Nothing is uploaded by the autopilot.

Fill in the placeholders in `<angle brackets>` once, in your own fork, before the first run.

## Parameters (given in the run's prompt)
- `LANG` = `EN`, `DE`, or another Twitch language code: language of the source, the captions, the title and the description.
- Arrival time (operator's time zone): the clips should be with the operator by then. A run takes about 30 to 35 minutes.
  If time runs short, deliver 2 good clips rather than 3 weak ones and say why.

Example schedule (arrival times): 09:00 EN, 14:00 EN, 19:00 EN. The operator posts the three clips of a run 20 minutes apart.

## Hard rules
1. **Every clip gets word-by-word captions** (`--captions word`). No exceptions.
2. You pick the streamer yourself (rules in phase 1).
3. Post nothing, upload nothing, send nothing to third parties. Deliver to the operator only.
4. Credit on every clip (`--credit @<twitch-login>`), source link with timestamp in the description.
5. Titles only contain what can be verified: what is said or seen in the clip. No "official", no claims about Rockstar.
   No story spoilers in the title. If a clip has story spoilers, put the word SPOILER in the description.
6. Never in a clip: club or strip-club scenes, nudity, gore, violence against children, hate, personal data
   (addresses, real names, payment details). Do not clip streamers who look like minors. Keep sub/donation
   shout-outs and sponsor reads out of the cut. Soften swear words in captions with asterisks, never put them in a title.
7. **Do not get around blocks.** On a 403, a bot check or a refused action: do not try another route, proxy or mirror.
   Report it briefly and carry on with the rest. Sources are Twitch VODs.
8. Rights: for most streamers no permission is documented. Every delivery says so honestly:
   "Campaign: yes/no, permission: unknown". Never claim that clipping is allowed.
9. Background processes die when the turn ends. Run everything in the foreground (at most 10 minutes per command).

## Phase 0: Setup (about 3 minutes)
1. Make the repo available (if it is not already in the working directory). In Claude Code on the web:
   `add_repo` with owner `<your-github-user>`, repo `<your-fork>`, access `push`, then run the
   `git clone --depth 1 ...` it names exactly once (generous timeout) and call `register_repo_root`.
   If that is refused: do not work around it. Tell the operator what is missing and stop.
2. `cd` into the repo and run `bash bootstrap.sh`. It must print `BOOTSTRAP OK`. Otherwise report the error and stop.
3. `export GTAVI="$PWD" CLIP_DESK_HOME="$HOME/clip-work"`
4. Read `state/watchlist.md`, `state/campaigns.md` and the last 12 lines of `state/runs.jsonl`.

## Phase 1: Pick the streamer
- Campaign streamers from `state/watchlist.md` first, **but only if** they have a GTA VI VOD with unused moments
  (`used_peaks` in `runs.jsonl`) or are live with GTA 6 again. Check the campaign first (fetch the campaign URL from
  `state/campaigns.md`): is it still active, does it have budget? If not, mention it in the report.
- Otherwise: `python3 -I tools/streams_lang.py <LANG> 20` and take the streamer with the most viewers who
  (a) is not on the block list, (b) was not the streamer of the last run in the same language in `runs.jsonl`, and
  (c) has a VOD of the GTA VI session (`python3 -I tools/vods.py <login>`, game "Grand Theft Auto VI", at least 1 hour long).
  Allow-list streamers come first. **Report "no campaign, permission unknown" explicitly.**
- Rotate: do not alternate between the same two streamers when others with good material are available.

Explain the choice in one sentence (for the message to the operator).

## Phase 2: Find moments
1. Scan windows: 3 windows of 40 minutes (2400 s) each in the material of the last 24 hours or so, spread evenly,
   preferably in the streamer's evening. Avoid windows listed under `scanned` for the same VOD in `runs.jsonl`.
   VOD time 0 is the stream start (UTC).
   `bash tools/fetch_scan.sh <vod_id> <start> <end> $CLIP_DESK_HOME/scan_<k>.mp4` (starting the 3 in parallel is fine, then `wait`).
   If yt-dlp hangs on a VOD of a stream that is still live: `python3 -I tools/hls_cut.py <vod_id> <start> <end> <out.mp4>`.
2. Loudness peaks: `python3 -I tools/peaks.py $CLIP_DESK_HOME/scan_<k>.mp4 <start> 8`.
   Discard peaks with a median below -45 dB or a file time below 5 s (music mutes and the start of the window).
   File time plus window start gives the VOD time.
3. Check the scenes: `python3 -I tools/contact_sheet.py /tmp/sheet.jpg 4 480 <scan_k.mp4>@<file-time>,...` and look at it with Read.
   Discard anything under rule 6. Pick **3 different moments** (at least 3 minutes apart), ideally a mix:
   action on screen, a strong reaction, a small story. No moments from `used_peaks` in `runs.jsonl`.
4. For each moment, a 70 s window in 720p60: `bash tools/fetch_window.sh <vod_id> <peak_s> $CLIP_DESK_HOME/media/raw`
   (start the 3 in parallel). Then
   `CLIP_LANG=en python3 -I $GTAVI/scripts/moments.py $CLIP_DESK_HOME/media/raw/v<vod>_<peak>.mp4 --top 3 --min 15 --max 30`
   (`CLIP_LANG` = the source language, e.g. `de`). This writes `jobs/<job>/candidates.md` and `transcript.json`
   (words with timestamps). Whisper on 2 CPUs needs about one minute per window.
5. Read the transcript and set start and end: 18 to 35 seconds, on sentence boundaries, with the punchline at the end.
   Sub/donation shout-outs and ads stay out. If the transcript is unusable, take another moment.

## Phase 3: Cut
1. **Find the facecam**: known positions are in `state/watchlist.md`. Otherwise grab a frame with `tools/frame.py`, look at it
   with Read, find the cam's border and give it as fractions `x:y:w:h` (2 to 3 pixels inside the border).
   `--cam auto` uses a face-detection model downloaded from GitHub on first use; if that download is blocked, set the box by hand.
   No cam at all: `--layout blur`. Add new cam positions to `state/watchlist.md`.
2. **Clean the captions** (only clear errors, merge numbers like "2" + ",000", soften swear words):
   `python3 -I tools/fix_transcript.py <job> fixes.json`
3. **Cut** (always with captions):
   ```
   python3 -I $GTAVI/scripts/cut.py <job> --pick 1 --layout react --cam <x:y:w:h> \
     --title '<hook, at most 2 lines of about 26 characters>' --title-style box --captions word \
     --credit @<twitch-login> --start <s> --end <e>
   ```
   The result is `<job>/edits/clip_1.mp4`. Copy it to `$CLIP_DESK_HOME/media/edits/<name>.mp4` together with its sidecar JSON
   (the `.json` next to it), and fill in `source_url` (VOD link with `?t=<h>h<m>m<s>s`, approximate) and `source_channel`.
4. **Check**: `ffprobe` (1080x1920, 30 fps, audio), `<job>/edits/clip_1.ass` must contain `Cap` lines, look at a contact sheet of the
   finished clips with Read (title box readable, cam visible, captions there, gameplay centred, nothing from rule 6),
   `python3 -I $GTAVI/scripts/check.py <clip> [--campaign state/campaigns.md]`. `RESULT: PASS` is required.

## Phase 4: Texts
**Title** (at most 95 characters, keyword first, only verifiable facts):
- `GTA 6: <streamer> <what happens> #GTA6`

**Description**:
```
Clip from <name>'s stream (twitch.tv/<login>). Source (approx. timestamp): <vod_url>?t=<h>h<m>m<s>s
Game: Grand Theft Auto VI (Rockstar Games). Fan page, not affiliated with Rockstar Games.
#GTA6 #GTAVI #<name> #Shorts
```
For other languages use the same structure, translated.

## Phase 5: Deliver (to the operator, in the operator's language)
1. `SendUserFile` with the 3 clips (status `proactive`) or, outside Claude Code on the web, leave them in `$CLIP_DESK_HOME/media/edits/`.
2. A short message that is easy to copy:
   - Run (language), streamer, why this streamer (one sentence), source (VOD link, approx. time).
   - **Rights:** campaign yes/no, permission unknown (honestly, as in rule 8).
   - Per clip: file name, suggested posting time (arrival +0, +20, +40 minutes), title, description.
   - Anything notable: fixed captions, softened words, doubts, skipped sources, errors during the run.

## Phase 6: Save state
1. Append one line to `state/runs.jsonl`: `ts`, `lang`, `streamer`, `vod`, `scanned` (windows), `used_peaks`, `clips` (names),
   `permission`, `note` (see `state/runs.example.jsonl`).
2. Add 3 to 5 lines to `state/log.md`. New findings (cam positions, notes on streamers) go into `state/watchlist.md`.
3. `git add -A`, commit, push to the branch the session allows.
   If the push is rejected: `git pull --rebase` once, then push again. If that fails, tell the operator and include the
   `runs.jsonl` line in the message so nothing is lost.

## Failure cases
- No suitable streams or VODs: take the next streamer. If there is none, report it with the reason.
- Fewer than 3 good clips: deliver what is good and say why.
- Bootstrap, repo or delivery fails: send a short message with the exact cause. Do not guess, do not work around it.
- Something takes unusually long (over 40 minutes in total): finish with what is done.
