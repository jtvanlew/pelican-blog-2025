AUTHOR = 'Jon'
SITENAME = 'jonvanlew.com'
SITEURL = ""

PATH = "content"

THEME = "themes/clean-blog"
TIMEZONE = 'America/Los_Angeles'
STATIC_PATHS = [
    "images",
]

DEFAULT_LANG = 'English'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None


# Blogroll
# LINKS = (
#     ("Pelican", "https://getpelican.com/"),
#     ("Python.org", "https://www.python.org/"),
#     ("Jinja2", "https://palletsprojects.com/p/jinja/"),
#     ("You can modify those links in your config file", "#"),
# )

PLUGIN_PATHS = ["E:\\GitHub\\pelican\\pelican-plugins"]
PLUGINS = ['sub_parts','photos']
# Social widget
# SOCIAL = (
#     ("You can add links in your config file", "#"),
#     ("Another social link", "#"),
# )


PHOTO_LIBRARY = "E:\Pictures\website-publishing-repository"
PHOTO_THUMB = (540, 360, 70)
PHOTO_GALLERY = (2048, 1024, 80)
PHOTO_ARTICLE = (1170, 1024, 80)


DISPLAY_CATEGORIES_ON_MENU = False
DISPLAY_PAGES_ON_MENU = False
DEFAULT_PAGINATION = 9

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

PHOTO_INLINE_GALLERY_ENABLED = True
FILENAME_METADATA = '(?P<slug>(?P<date>\d{4}-\d{2}-\d{2})-[^.]+)'

OUTPUT_PATH = "../jtvanlew.github.io"

SUMMARY_MAX_LENGTH = 50