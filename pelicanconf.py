AUTHOR = 'Jon'
SITENAME = 'jonvanlew.com'
SITEURL = ""

PATH = "content"

# STATIC_PATHS = ['images']
# THEME_STATIC_DIR = "E:\\GitHub\\pelican-blog-2025\\themes"
THEME = "themes/clean-blog"
TIMEZONE = 'America/Los_Angeles'

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
PHOTO_THUMB = (360, 360, 70)
PHOTO_GALLERY = (2048, 1024, 80)
PHOTO_ARTICLE = (1170, 1024, 80)

# IMAGE_PROCESS = {
#     "article-image": ["scale_in 300 300 True"],
#     "test-image": ["scale_in 800 800 True"],
#     "thumb": ["crop 0 0 50% 50%", "scale_out 150 150 True", "crop 0 0 150 150"],
# }

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
# RELATIVE_URLS = True

PHOTO_INLINE_GALLERY_ENABLED = True
FILENAME_METADATA = '(?P<slug>(?P<date>\d{4}-\d{2}-\d{2})-[^.]+)'