AUTHOR = 'Jon'
SITENAME = 'jonvanlew.com'
SITEURL = ""
RELATIVE_URLS = False

# PATHS
PATH = "content"
PAGE_PATHS = ['pages']
ARTICLE_PATHS = ['blog']
STATIC_PATHS = ["images"]
PLUGIN_PATHS = ["E:\\GitHub\\pelican\\pelican-plugins"]
##

PLUGINS = ['sub_parts','photos']
THEME = "themes/clean-blog"
TIMEZONE = 'America/Los_Angeles'
DEFAULT_LANG = 'En'

DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
DEFAULT_PAGINATION = 9

MENUITEMS = (
    ("Categories", "/categories.html"),
    ("Tags", "/tags.html"),
    ("Bikes", "/pages/my-bikes.html"),
)

SUMMARY_MAX_LENGTH = 50

# PHOTOS plugin settings
PHOTO_LIBRARY = "E:\Pictures\website-publishing-repository"
PHOTO_THUMB = (540, 360, 70)
PHOTO_GALLERY = (2048, 2048, 80)
PHOTO_ARTICLE = (1170, 1024, 80)
PHOTO_INLINE_GALLERY_ENABLED = True
FILENAME_METADATA = '(?P<slug>(?P<date>\d{4}-\d{2}-\d{2})-[^.]+)'
##

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
##