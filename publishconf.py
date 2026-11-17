# This file is only used if you use `make publish` or
# explicitly specify it as your config file.

import os
import sys

sys.path.append(os.curdir)
from pelicanconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
SITEURL = "https://www.jonvanlew.com"
RELATIVE_URLS = False

FEED_ALL_ATOM = "feeds/all.atom.xml"
CATEGORY_FEED_ATOM = "feeds/{slug}.atom.xml"

# Fresh cache-busting token on every publish: CSS/JS are linked as ...?v=<this>,
# so Cloudflare and browsers fetch the new files instead of a cached copy.
import time as _time

THEME_VERSION = _time.strftime("%Y%m%d%H%M")

# Build into its own folder so a publish build never wipes the `output/` folder
# the local livereload server is working in.
OUTPUT_PATH = "output-publish/"
DELETE_OUTPUT_DIRECTORY = True

# Leave drafts out of the public build entirely, so their pages AND their
# resized photos never end up on the server. A post is a draft when its
# metadata has ":status: draft".
import re as _re
from pathlib import Path as _Path

_DRAFT = _re.compile(r"^:status:\s*draft\s*$", _re.MULTILINE | _re.IGNORECASE)
IGNORE_FILES = list(globals().get("IGNORE_FILES", [".#*"])) + [
    _p.name
    for _p in (_Path(__file__).resolve().parent / PATH).rglob("*.rst")
    if _DRAFT.search(_p.read_text(encoding="utf-8", errors="ignore"))
]

# Following items are often useful when publishing

# Remark42 comments (self-hosted on the VPS, see tools/remark42/README.md).
REMARK42_URL = "https://comments.jonvanlew.com"

# GOOGLE_ANALYTICS = ""
