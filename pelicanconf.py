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

PLUGINS = ['sub_parts', 'photos', 'photos_compat', 'article_modified_order']
THEME = "themes/clean-blog"
TIMEZONE = 'America/Los_Angeles'
DEFAULT_LANG = 'En'
JINJA_GLOBALS = {
    '_': lambda text: text,
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
PHOTO_LIBRARY = r"C:\Users\jtvan\Proton Drive\jtvanlew\My files\Pictures\website-publishing-repository"
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
##

PAGE_ORDER_BY = 'reversed-date'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
##

DISQUS_SITENAME = 'jonnyvlreport'

# Optional palette selection. Leave empty to use the default palette defined in
# `clean-blog.css`. Valid values correspond to the CSS classes defined there,
# e.g. 'forest', 'coastal', 'warmbeige', 'rose'. If set, the template will add
# a `palette-<name>` class to the <body> element so you can preview palettes.
PALETTE = 'coastal'

# Theme version for cache-busting static assets. Set this to a short token
# (date, semantic version, or git commit hash) when you deploy to force
# browsers/CDNs to fetch updated static files, e.g. '20251125' or 'v1.2.0'.
THEME_VERSION = '20260512'