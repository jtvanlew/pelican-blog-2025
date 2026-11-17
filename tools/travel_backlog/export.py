"""Export web JPEGs for each trip in the manifest. Read-only on the library.

usage: python export.py <manifest.json> <publish root> <raw-preview cache dir> [--limit N] [--notes-only]
Writes <root>/<year>/<MM-DD>-<Slug>/<YYYYMMDD_HHMMSS>_<base>.jpg + captions.txt + ratings.txt.
ratings.txt holds digiKam star ratings (rated photos only); the site features photos at or
above PHOTO_FEATURED_RATING. --notes-only rewrites captions.txt / ratings.txt and exports nothing,
so after rating favourites in digiKam: rebuild the manifest, then rerun with --notes-only.
Only metadata kept: DateTimeOriginal/DateTime (+ ICC profile). Existing files are skipped.
"""
import sys, os, json, re, subprocess, unicodedata, hashlib, collections
from concurrent.futures import ProcessPoolExecutor

EXIFTOOL = r"C:\Program Files\digiKam\exiftool.exe"
MAXSIDE, QUALITY = 2048, 85
RAW = {"nef", "orf"}

def slug(title):
    t = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode()
    words = re.findall(r"[A-Za-z0-9]+", t)
    return "".join(w if w.isupper() else w[:1].upper() + w[1:] for w in words)

def out_name(im):
    dt = re.sub(r"\D", "", im["dt"])[:14]
    base = re.sub(r"[^A-Za-z0-9_-]", "_", im["name"].rsplit(".", 1)[0])
    return f"{dt[:8]}_{dt[8:14]}_{base}.jpg"

def trip_dir(t):
    return f"{t['year']}/{t['md'].replace(' ', '')}-{slug(t['title'])}"

def raw_cache_path(cache, src):
    return os.path.join(cache, hashlib.md5(src.lower().encode()).hexdigest() + ".jpg")

def extract_raw_previews(images, cache):
    os.makedirs(cache, exist_ok=True)
    todo = [im["src"] for im in images if im["ext"] in RAW and not os.path.exists(raw_cache_path(cache, im["src"]))]
    for src in todo:
        for tag in ("-JpgFromRaw", "-PreviewImage"):
            data = subprocess.run([EXIFTOOL, "-b", tag, src], capture_output=True).stdout
            if len(data) > 50000:
                with open(raw_cache_path(cache, src), "wb") as f: f.write(data)
                break

def work(args):
    im, dest, cache, pylib = args
    if os.path.exists(dest):
        return "exists"
    if pylib not in sys.path:
        sys.path.insert(0, pylib)
    from PIL import Image, ImageOps
    import pillow_heif; pillow_heif.register_heif_opener()
    try:
        if im["ext"] in RAW:
            p = raw_cache_path(cache, im["src"])
            if not os.path.exists(p): return "no_preview"
            img = Image.open(p)
            op = {2: Image.Transpose.FLIP_LEFT_RIGHT, 3: Image.Transpose.ROTATE_180, 4: Image.Transpose.FLIP_TOP_BOTTOM,
                  5: Image.Transpose.TRANSPOSE, 6: Image.Transpose.ROTATE_270, 7: Image.Transpose.TRANSVERSE,
                  8: Image.Transpose.ROTATE_90}.get(int(im.get("orient") or 1))
            img.load()
            if op: img = img.transpose(op)
        else:
            img = Image.open(im["src"]); img.load()
            img = ImageOps.exif_transpose(img)
        icc = img.info.get("icc_profile")
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")
        img.thumbnail((MAXSIDE, MAXSIDE), Image.Resampling.LANCZOS)
        exif = Image.Exif()
        stamp = im["dt"][:19].replace("-", ":").replace("T", " ")
        exif[0x0132] = stamp                       # DateTime
        exif.get_ifd(0x8769)[0x9003] = stamp       # DateTimeOriginal
        tmp = dest + ".part"
        kw = dict(quality=QUALITY, optimize=True, exif=exif.tobytes())
        if icc: kw["icc_profile"] = icc
        img.save(tmp, "JPEG", **kw)
        os.replace(tmp, dest)
        return "ok"
    except Exception as e:
        return f"error {type(e).__name__}: {e}"

def main():
    manifest, root, cache = sys.argv[1:4]
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    notes_only = "--notes-only" in sys.argv
    pylib = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylib")
    trips = json.load(open(manifest, encoding="utf-8"))
    jobs, results = [], collections.Counter()
    for t in trips:
        imgs = t["images"][:limit] if limit else t["images"]
        d = os.path.join(root, trip_dir(t))
        os.makedirs(d, exist_ok=True)
        if not notes_only:
            extract_raw_previews(imgs, cache)
        caps = [f"{out_name(im)}: {im['caption']}" for im in imgs if im["caption"]]
        if caps:
            with open(os.path.join(d, "captions.txt"), "w", encoding="utf-8") as f:
                f.write("# captions from digiKam\n" + "\n".join(caps) + "\n")
        rates = [f"{out_name(im)}: {im['rating']}" for im in imgs if im.get("rating", -1) > 0]
        rpath = os.path.join(d, "ratings.txt")
        if rates:
            with open(rpath, "w", encoding="utf-8") as f:
                f.write("# digiKam star ratings\n" + "\n".join(rates) + "\n")
        elif os.path.exists(rpath):
            os.remove(rpath)
        jobs += [(im, os.path.join(d, out_name(im)), cache, pylib) for im in imgs]
        print("prepared", trip_dir(t), len(imgs), f"{len(rates)} rated", flush=True)
    if notes_only:
        return
    with ProcessPoolExecutor(max_workers=max(2, (os.cpu_count() or 4) - 2)) as ex:
        for (im, dest, *_), r in zip(jobs, ex.map(work, jobs, chunksize=8)):
            results[r.split(":")[0]] += 1
            if r.startswith("error") or r == "no_preview":
                print(r, im["src"], flush=True)
    print(dict(results))

if __name__ == "__main__":
    main()
