"""Build a manifest of travel trips (non-Americas) from a COPY of the digiKam DB.

usage: python manifest.py <dk.db copy> <out.json> [--album "<yyyy/MM-DD - Name>"] [--color <label>]

--album limits it to that one digiKam album (no Travel tag or skip list needed);
--color keeps only photos with that colour label (Purple = digiKam's Magenta).
Son-tagged, Rejected and non-still files are always left out.
"""
import sqlite3, sys, json, re, collections

DB, OUT = sys.argv[1], sys.argv[2]
def _opt(name):
    return sys.argv[sys.argv.index(name) + 1] if name in sys.argv else None
ONLY_ALBUM = (_opt("--album") or "").strip("/") or None
COLOR = _opt("--color")
if COLOR and COLOR.lower() in ("purple", "violet"):
    COLOR = "Magenta"
LIB = "Z:/Photos"
SON_TAG = "People/Jon Meinte Van Lew"
CUTOFF = "2023-01-01"           # nothing dated on/after this goes out
STILLS = {"jpg", "jpeg", "png", "tif", "tiff", "heic", "nef", "orf"}
RAW = {"nef", "orf"}
SKIP_ALBUMS = {                 # already posted / not a trip / privacy
    "2022/06-23 - Udine with VBC", "2022/07-02 - Austria",
    "2013/09-20 - Switzerland", "2015/09-07 - South Korea",
    "2025/10-24 - Taiwan Family Vacation",
    "2013/08-11 - El Capitan Camp",
}
MIN_PHOTOS = 15

db = sqlite3.connect(DB)
tags = {r[0]: (r[1], r[2]) for r in db.execute("select id,pid,name from Tags")}
def tpath(t):
    p = []
    while t and t in tags:
        p.append(tags[t][1]); t = tags[t][0]
    return "/".join(reversed(p))
TP = {t: tpath(t) for t in tags}
haschild = {p for (p, n) in tags.values()}
travel = {t for t in tags if TP[t].startswith("Travel/") and "/Americas" not in TP[t]}
son = {t for t in tags if TP[t] == SON_TAG}
assert son, "son tag not found"
pick = {t: tags[t][1].replace("Pick Label ", "") for t in tags if tags[t][1].startswith("Pick Label")}
color_tag = None
if COLOR:
    color_tag = next((t for t in tags if tags[t][1].lower() == f"color label {COLOR}".lower()), None)
    assert color_tag, f"no digiKam colour label called {COLOR!r}"

img_tags = collections.defaultdict(set)
for iid, tid in db.execute("select imageid,tagid from ImageTags"):
    img_tags[iid].add(tid)
captions = {}
for iid, c in db.execute("select imageid,comment from ImageComments where type=1 and (language='x-default' or language is null)"):
    if c and c.strip(): captions[iid] = " ".join(c.split())

rows = db.execute("""select i.id, a.relativePath, i.name, ii.creationDate, ii.orientation, ii.rating
  from Images i join Albums a on a.id=i.album join ImageInformation ii on ii.imageid=i.id
  where i.status=1""").fetchall()

def trip_key(rp):
    parts = rp.strip("/").split("/")
    return "/".join(parts[:2]) if len(parts) >= 2 and re.match(r"\d{4}$", parts[0]) else None

trips = collections.defaultdict(list)
stats = collections.Counter()
for iid, rp, name, cd, orient, rating in rows:
    tset = img_tags.get(iid, set())
    if ONLY_ALBUM:
        if rp.strip("/") != ONLY_ALBUM:
            continue
    elif not (tset & travel):
        continue
    if color_tag and color_tag not in tset:
        stats["no_color_label"] += 1; continue
    key = trip_key(rp)
    if not key or (key in SKIP_ALBUMS and not ONLY_ALBUM):
        stats["skip_album"] += 1; continue
    ext = name.rsplit(".", 1)[-1].lower()
    if ext not in STILLS:
        stats["video_or_other"] += 1; continue
    p = next((pick[t] for t in tset if t in pick), "None")
    if p == "Rejected":
        stats["rejected"] += 1; continue
    if tset & son:
        stats["son"] += 1; continue
    if not cd or cd[:10] >= CUTOFF:
        stats["date_cutoff"] += 1; continue
    leaf = sorted({TP[t] for t in tset if t in travel})
    trips[key].append(dict(id=iid, src=f"{LIB}/{rp.strip('/')}/{name}", rel=rp.strip("/"), name=name,
                           ext=ext, dt=cd[:19], pick=p, travel=leaf, orient=orient or 1, rating=rating if rating is not None else -1,
                           caption=captions.get(iid, "")))

# merge albums that share year + MM-DD (e.g. two Cinque Terre albums)
merged = collections.defaultdict(list)
names = collections.defaultdict(list)
for key, imgs in trips.items():
    y, rest = key.split("/", 1)
    md = rest.split(" - ", 1)[0]
    merged[(y, md)].extend(imgs)
    names[(y, md)].append(rest.split(" - ", 1)[1] if " - " in rest else rest)

out = []
for (y, md), imgs in sorted(merged.items()):
    # RAW+JPEG pairs: keep the JPEG
    # RAW+JPEG pairs and digiKam edit versions (X.NEF, X.jpg, X_v1.jpg, X_v2.jpg): keep newest JPEG
    by_base = collections.defaultdict(list)
    for im in imgs:
        stem = im["name"].rsplit(".", 1)[0].lower()
        m = re.match(r"(.*)_v(\d+)$", stem)
        im["_ver"] = int(m.group(2)) if m else 0
        by_base[(im["rel"], m.group(1) if m else stem)].append(im)
    keep = []
    for group in by_base.values():
        nonraw = [g for g in group if g["ext"] not in RAW]
        chosen = max(nonraw, key=lambda g: g["_ver"]) if nonraw else group[0]
        if len(group) > 1:
            stats["raw_pair_dropped"] += len(group) - 1
            # carry caption / pick from any member
            chosen["caption"] = chosen["caption"] or next((g["caption"] for g in group if g["caption"]), "")
            if any(g["pick"] == "Accepted" for g in group): chosen["pick"] = "Accepted"
            chosen["rating"] = max(g.get("rating", -1) for g in group)
        keep.append(chosen)
    if len(keep) < MIN_PHOTOS and not ONLY_ALBUM:
        stats["small_trip_photos"] += len(keep); continue
    keep.sort(key=lambda im: (im["dt"], im["name"].lower()))
    title = " / ".join(sorted(set(names[(y, md)]), key=len, reverse=True)[:1])
    selection = (f"{COLOR if COLOR != 'Magenta' else 'purple'} colour label" if COLOR
                 else "everything not marked Rejected")
    out.append(dict(year=y, md=md, albums=sorted(set(im["rel"] for im in keep)), title=title, images=keep,
                    selection=selection))

json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for t in out:
    days = sorted({im["dt"][:10] for im in t["images"]})
    acc = sum(im["pick"] == "Accepted" for im in t["images"])
    exts = collections.Counter(im["ext"] for im in t["images"])
    print(f"{t['year']}/{t['md']} {t['title']!r}: {len(t['images'])} photos ({acc} accepted), {days[0]}..{days[-1]} ({len(days)} days) {dict(exts)}")
print("TOTAL", sum(len(t["images"]) for t in out), dict(stats))
