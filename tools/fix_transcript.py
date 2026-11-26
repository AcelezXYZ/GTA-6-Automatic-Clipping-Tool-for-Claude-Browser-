"""Fix obvious recognition errors in a job's Whisper transcript (affects the captions only).

usage:  python3 -I tools/fix_transcript.py <job_dir> <fixes.json>
fixes.json: list of [time_from, time_to, old_word, new_word]; new_word "" removes the word.
example: [[26.7,26.9,"2","2,000"],[27.0,27.1,",000",""],[27.3,27.5,"euro","dollars"],[43.9,44.3,"fucking","f***ing"]]
The original is kept as transcript.orig.json. Only fix what was clearly misheard, and soften swear words
with asterisks. Never invent anything that was not said.
"""
import json, os, shutil, sys

job, fixes = sys.argv[1], json.load(open(sys.argv[2], encoding="utf-8"))
p = os.path.join(job, "transcript.json")
orig = os.path.join(job, "transcript.orig.json")
if not os.path.exists(orig):
    shutil.copy(p, orig)
words = json.load(open(p, encoding="utf-8"))
n = 0
for x in words:
    for t0, t1, old, new in fixes:
        if t0 <= x["s"] <= t1 and x["w"] == old:
            x["w"] = new
            n += 1
json.dump(words, open(p, "w", encoding="utf-8"), ensure_ascii=False)
print(n, "fixes applied,", len(fixes), "planned")
