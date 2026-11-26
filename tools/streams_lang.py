"""Live streams in the Twitch category "Grand Theft Auto VI" by broadcaster language, sorted by viewers.

usage:  python3 -I tools/streams_lang.py EN [count]     (any Twitch language code: EN, DE, ES, FR, ...; default 25 rows)
Uses scripts/twitch.py (or $GTAVI/scripts), see bootstrap.sh. No account, no API key.
"""
import json, os, sys

_G = os.environ.get("GTAVI") or os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(_G, "scripts"))
import twitch  # noqa: E402

Q = """query($name:String!,$n:Int!,$langs:[Language!]){ game(name:$name){ displayName
 streams(first:$n, options:{broadcasterLanguages:$langs, sort:VIEWER_COUNT}){ edges{ node{
 title viewersCount createdAt broadcaster{ login displayName } } } } } }"""

lang = (sys.argv[1] if len(sys.argv) > 1 else "EN").upper()
limit = int(sys.argv[2]) if len(sys.argv) > 2 else 25
d = twitch.gql(Q, {"name": "Grand Theft Auto VI", "n": 40, "langs": [lang]})
if d.get("errors"):
    print("ERROR", json.dumps(d["errors"])[:300])
g = (d.get("data") or {}).get("game")
if not g:
    sys.exit("category not found or no streams")
rows = []
for e in (g["streams"] or {}).get("edges") or []:
    n = e["node"]
    b = n["broadcaster"]
    rows.append((n["viewersCount"], b["login"], b["displayName"], n["title"], n.get("createdAt")))
print(f"GTA VI | language {lang} | {len(rows)} streams live")
for v, login, name, title, ts in sorted(rows, reverse=True)[:limit]:
    print(f"{v:>6}  {login:<22} https://twitch.tv/{login} | since {ts} | {title[:90]}")
