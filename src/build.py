#!/usr/bin/env python3
"""Build index.html for Vercel from src/data.json and src/tpl-combined.html.

Edit src/data.json (times like "2:05 PM"), then run:
    python3 src/build.py                                  # local build
    python3 src/build.py https://your-site.vercel.app     # also sets absolute share-preview URLs
The build stops with a clear message on any data error, so a typo can never reach parents.
"""
import json, re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.dirname(HERE)
SITE = (sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "")

errors, warnings = [], []
d = json.load(open(os.path.join(HERE, "data.json")))


def minutes(s, ctx):
    m = re.fullmatch(r"\s*(\d{1,2}):(\d{2})\s*(AM|PM)\s*", s or "")
    if not m:
        errors.append(f"{ctx}: time '{s}' must look like 2:05 PM")
        return 0
    h, mm, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if not (1 <= h <= 12 and 0 <= mm < 60):
        errors.append(f"{ctx}: time '{s}' is out of range")
    return (h % 12) * 60 + mm + (720 if ap == "PM" else 0)


loc_ids = [l["id"] for l in d["locations"]]
if len(set(loc_ids)) != len(loc_ids):
    errors.append("duplicate location ids")
real_groups = [g["id"] for g in d["groups"] if not g.get("virtual")]
for l in d["locations"]:
    if l["map"] not in d["mapSize"]:
        errors.append(f"location {l['id']}: unknown map '{l['map']}'")
    if len(l["box"]) != 4:
        errors.append(f"location {l['id']}: box needs 4 numbers")
    if l.get("zone") and l["zone"] not in d["zones"]:
        errors.append(f"location {l['id']}: unknown zone")

acts, seen = [], set()
for a in d["activities"]:
    ctx = f"activity {a['id']}"
    if a["id"] in seen:
        errors.append(f"{ctx}: duplicate id")
    seen.add(a["id"])
    for g in a["groups"]:
        if g not in real_groups:
            errors.append(f"{ctx}: unknown group '{g}'")
    for x in a["locs"]:
        if x not in loc_ids:
            errors.append(f"{ctx}: unknown location '{x}'")
    s, e = minutes(a["start"], ctx), minutes(a["end"], ctx)
    if e <= s:
        errors.append(f"{ctx}: ends before it starts")
    if a.get("internal"):
        continue  # kept in data.json for the record, never shown to parents
    acts.append({"id": a["id"], "name": a["name"], "g": a["groups"], "locs": a["locs"],
                 "where": a["where"], "s": s, "e": e, "d": a["desc"]})

for g in ("bal", "balika"):
    items = sorted([a for a in acts if g in a["g"]], key=lambda a: a["s"])
    for p, q in zip(items, items[1:]):
        if q["s"] < p["e"]:
            warnings.append(f"overlap in {g}: {p['id']} and {q['id']}")

if errors:
    print("DATA ERRORS:\n  " + "\n  ".join(errors))
    sys.exit(1)
for w in warnings:
    print("warning:", w)

J = lambda x: json.dumps(x, ensure_ascii=False)
block = f"""/* ===== Data generated from src/data.json. Do not edit here. ===== */
const EVENT = {J(d['event'])};
const GROUPS = {J(d['groups'])};
const KIDS = ["bal","balika"];
const MAP_SIZE = {J(d['mapSize'])};
const ZONES = {J(d['zones'])};
const LOCATIONS = {J(d['locations'])};
const ACTIVITIES = {J(acts)};
const GROUP_NOTES = {J(d['groupNotes'])};
const INFO = {J(d['info'])};
/* ===== end data ===== */"""

t = open(os.path.join(HERE, "tpl-combined.html")).read()
assert "/*__DATA__*/" in t
t = t.replace("/*__DATA__*/", block)

# split the template into head pieces (up to </style>) and the page body
cut = t.index("</style>") + len("</style>")
head, body = t[:cut], t[cut:]
head = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\n?', "", head)
img = (SITE + "/" if SITE else "") + "assets/og.jpg"
head = re.sub(r'<meta property="og:image"[^>]*>', f'<meta property="og:image" content="{img}">', head)
extra = ('<meta property="og:type" content="website">\n'
         + (f'<meta property="og:url" content="{SITE}/">\n' if SITE else "")
         + '<meta name="twitter:card" content="summary_large_image">\n'
         '<link rel="icon" href="assets/favicon.png">\n'
         '<style>html{color-scheme:light}:root{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>\n')
page = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        + extra + head + '\n</head>\n<body>\n' + body.strip() + '\n</body>\n</html>\n')
open(os.path.join(OUT, "index.html"), "w").write(page)
print("built index.html", len(page), "bytes")
