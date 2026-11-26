"""Live status and latest VODs (archives) of a Twitch channel.

usage:  python3 -I tools/vods.py <login>
Output: VOD id, length in seconds, start (UTC), game, title. VOD time 0 is the stream start (UTC).
Convert to your own time zone yourself (for example Europe/Berlin is UTC+1 in winter, UTC+2 in summer).
"""
import json, os, sys

_G = os.environ.get("GTAVI") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(_G, "scripts"))
import twitch  # noqa: E402

Q = """query($login:String!){ user(login:$login){ displayName stream{ id createdAt viewersCount game{ displayName } }
 videos(first:6, type:ARCHIVE, sort:TIME){ edges{ node{ id title lengthSeconds createdAt game{ displayName } } } } } }"""

d = twitch.gql(Q, {"login": sys.argv[1].lower()})
if d.get("errors"):
    print("ERROR", json.dumps(d["errors"])[:300])
u = (d.get("data") or {}).get("user") or {}
print(u.get("displayName"), "| live:", u.get("stream"))
for e in ((u.get("videos") or {}).get("edges") or []):
    n = e["node"]
    print(n["id"], n["lengthSeconds"], n["createdAt"], (n.get("game") or {}).get("displayName"), "|", n["title"][:70])
