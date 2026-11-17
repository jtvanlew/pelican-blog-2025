"""Write draft RST posts for each trip in the manifest. Never overwrites an existing post.

usage: python posts.py <manifest.json> <content/blog dir>
"""
import sys, os, json, datetime, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from export import slug, out_name, trip_dir

CHUNK, MIN_TAIL = 20, 6
PUBLISH = r"C:\Users\jtvan\Pictures\website-publishing-repository"
PROMPTS = [
    "What was the plan for this part of the day?",
    "Where are we here, and how did we get there?",
    "Who was along for this stretch?",
    "Best thing eaten or drunk around here?",
    "Anything go sideways here?",
    "What's the story behind these shots?",
    "What did this place smell / sound like?",
    "Something you'd tell a friend going here.",
]

def heading(text, ch):
    return f"{text}\n{ch * max(len(text), 3)}\n"

def nice_date(d):
    dt = datetime.date.fromisoformat(d)
    return f"{dt:%a} {dt:%B} {dt.day}, {dt.year}"

def chunks(n):
    out, start = [], 0
    while start < n:
        end = min(start + CHUNK, n)
        if n - end < MIN_TAIL:
            end = n
        out.append((start, end)); start = end
    return out

def place_names(paths):
    names = []
    for p in paths:
        parts = p.split("/")[2:]          # drop Travel/<continent>
        for x in parts:
            if x not in names: names.append(x)
    return names

def main():
    manifest, blog = sys.argv[1:3]
    trips = json.load(open(manifest, encoding="utf-8"))
    for t in trips:
        d = trip_dir(t)
        uniq = {}
        for im in t["images"]:      # same photo copied into two albums -> one file on disk
            if os.path.exists(os.path.join(PUBLISH, d, out_name(im))):   # skip failed exports
                uniq.setdefault(out_name(im), im)
        imgs = sorted(uniq.values(), key=lambda im: (im["dt"], out_name(im).lower()))
        post_date = f"{t['year']}-{t['md']}"
        fname = os.path.join(blog, f"{post_date}-{slug(t['title'])}.rst")
        if os.path.exists(fname):
            print("exists, skipped:", fname); continue

        all_places = place_names(sorted({p for im in imgs for p in im["travel"]}))
        cover = next((im for im in imgs[len(imgs)//3:] if im["pick"] == "Accepted"), imgs[len(imgs)//3])
        title = f"{t['title']} ({post_date})"
        lines = [heading(title, "#"),
                 f":date: {post_date}",
                 f":tags: {', '.join(all_places + ['Travel'])}",
                 f":image: {{photo}}{d}/{out_name(cover)}",
                 f":gallery: {{photo}}{d}",
                 f":summary: TODO one-line summary of {t['title']}",
                 ":status: draft",
                 "",
                 f"TODO: intro for {t['title']}. Auto-generated draft from digiKam "
                 f"({len(imgs)} photos, {t.get('selection', 'everything not marked Rejected')}).",
                 ""]
        by_day = collections.OrderedDict()
        for i, im in enumerate(imgs):
            by_day.setdefault(im["dt"][:10], []).append(i)
        k = 0
        for n_day, (day, idx) in enumerate(by_day.items(), 1):
            day_places = place_names(sorted({p for i in idx for p in imgs[i]["travel"]}))
            lines.append(heading(f"Day {n_day}: {nice_date(day)}" + (f" - {', '.join(day_places)}" if day_places else ""), "-"))
            first, count = idx[0], len(idx)
            for a, b in chunks(count):
                lines.append(f"TODO ({', '.join(day_places) or t['title']}, photos {a+1}-{b} of {count} this day): "
                             f"{PROMPTS[k % len(PROMPTS)]}")
                lines.append("")
                lines.append(f"gallery::{{photo}}{d}[{first+a}:{first+b}]")
                lines.append("")
                k += 1
        with open(fname, "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines))
        print(f"wrote {os.path.basename(fname)}: {len(imgs)} photos, {len(by_day)} days, {k} galleries")

if __name__ == "__main__":
    main()
