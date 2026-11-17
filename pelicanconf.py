from pathlib import Path

AUTHOR = 'Jon'
SITENAME = 'jonvanlew.com'
SITEURL = ""
RELATIVE_URLS = False

BASE_DIR = Path(__file__).resolve().parent
PLUGIN_REPO = BASE_DIR.parent / 'pelican-dev' / 'pelican-plugins'
LOCAL_PLUGIN_DIR = BASE_DIR / 'plugins'

# PATHS
PATH = "content"
PAGE_PATHS = ['pages']
ARTICLE_PATHS = ['blog']
STATIC_PATHS = ["images"]
PLUGIN_PATHS = [str(LOCAL_PLUGIN_DIR), str(PLUGIN_REPO)]
##

PLUGINS = ['sub_parts', 'photos', 'photos_compat', 'tagged_photos', 'article_modified_order']
THEME = "themes/clean-blog"
TIMEZONE = 'America/Los_Angeles'
DEFAULT_LANG = 'En'
JINJA_GLOBALS = {
    '_': lambda text: text,
}
JINJA_FILTERS = {
    # tags.html: most-used tags first, then alphabetical
    'by_article_count': lambda tags: sorted(tags, key=lambda t: (-len(t[1]), t[0].name.lower())),
}

# LOAD_CONTENT_CACHE = False

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
DEFAULT_PAGINATION = 9

MENUITEMS = (
    # ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
    ("Bikes", "/pages/my-bikes.html"),
)

SUMMARY_MAX_LENGTH = 50

# PHOTOS plugin settings
PHOTO_LIBRARY = r"C:\Users\jtvan\Pictures\website-publishing-repository"
PHOTO_THUMB = (600, 600, 70)
PHOTO_GALLERY = (2048, 2048, 80)
PHOTO_ARTICLE = (1170, 1024, 80)
PHOTO_INLINE_ENABLED = True
PHOTO_INLINE_GALLERY_ENABLED = True
PHOTO_INLINE_GALLERY_PATTERN = r'gallery::(?P<gallery_name>[/{}\w\[\]:,._\-=|]+)'
PHOTO_RESIZE_JOBS = -1
# INLINE_GALLERY = 'inline_gallery_carousel'
FILENAME_METADATA = r'(?P<slug>(?P<date>\d{4}-\d{2}-\d{2})-[^.]+)'
PHOTO_SQUARE_THUMB = True
# Gallery photos with at least this many digiKam stars get their own full-width,
# uncropped row (see plugins/photos_compat.py for where ratings are read from).
# 2 matches the old exif.txt rule; set to 0 / None to turn featuring off.
PHOTO_FEATURED_RATING = 2
##

PAGE_ORDER_BY = 'reversed-date'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
##

# Comments: self-hosted Remark42 (replaced Disqus 2026-11). The settings live in
# publishconf.py so local builds don't try to load the comment server.
# Old Disqus forum shortname, kept for exporting/importing comments: 'jonnyvlreport'
REMARK42_URL = ''
REMARK42_SITE_ID = 'jonvanlew'

# Optional palette selection. Leave empty to use the default palette defined in
# `clean-blog.css`. Valid values correspond to the CSS classes defined there,
# e.g. 'forest', 'coastal', 'warmbeige', 'rose'. If set, the template will add
# a `palette-<name>` class to the <body> element so you can preview palettes.
PALETTE = 'coastal'

# Optional layout variant layered on top of the palette. 'scrapbook' = taped
# polaroid cards, luggage-tag tags, stamp dates, trail-sign pager
# (static/css/variant-scrapbook.css). Leave empty for the plain layout.
THEME_VARIANT = 'scrapbook'

# Footer line (replaces the old "powered by Pelican"). Paste the lyric you want
# between the quotes; leave FOOTER_QUOTE empty for no footer text.
# For several lines use triple quotes; each line break shows in the footer:
#   FOOTER_QUOTE = '''first line
#   second line'''
FOOTER_QUOTE = """If dogs run free, why not me
Across the swamp of time?
My mind weaves a symphony
And tapestry of rhyme"""
FOOTER_QUOTE_CITE = 'Bob Dylan, "If Dogs Run Free"'

# Theme version for cache-busting static assets. Set this to a short token
# (date, semantic version, or git commit hash) when you deploy to force
# browsers/CDNs to fetch updated static files, e.g. '20251125' or 'v1.2.0'.
THEME_VERSION = '20261013'