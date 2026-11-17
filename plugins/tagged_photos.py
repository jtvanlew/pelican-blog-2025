"""Collect photos by their embedded keyword tags and attach them to pages.

A page opts in with a ``photo_tag`` metadata field, e.g. on a bike page::

    :photo_tag: Homer

At build time every image in every article/page gallery (both ``:gallery:``
metadata and inline ``gallery::`` blocks) is scanned for keywords written by
digiKam / ansel / darktable / Lightroom:

- XMP ``dc:subject``, ``lr:hierarchicalSubject``, ``digiKam:TagsList``
  (embedded in the JPEG or in a ``photo.jpg.xmp`` / ``photo.xmp`` sidecar)
- IPTC Keywords

A keyword matches when it equals the tag, or when the last level of a
hierarchical keyword does (``Bikes|Homer`` and ``Bikes/Homer`` both match
``Homer``). Matching is case-insensitive. Several tags can be given separated
by commas.

Matches are exposed to templates as ``page.tagged_photos``: a list of
``{"content": <Article|Page>, "photos": [GalleryImage, ...]}`` groups, newest
content first. The page's own galleries are excluded.

Must be listed after ``photos`` (and ``photos_compat``) in PLUGINS.
"""

from __future__ import annotations

import logging
import os
import re
import xml.etree.ElementTree as ET
from functools import lru_cache

from pelican import signals

logger = logging.getLogger(__name__)

_KEYWORD_FIELDS = {"subject", "hierarchicalSubject", "TagsList"}
_RDF_LI = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li"

# content object -> list of Gallery objects seen while it was processed
_content_galleries: dict[int, tuple[object, list]] = {}


def _keywords_from_xmp(xmp) -> set[str]:
    if isinstance(xmp, bytes):
        xmp = xmp.decode("utf-8", errors="ignore")
    start, end = xmp.find("<x:xmpmeta"), xmp.rfind("</x:xmpmeta>")
    if start == -1 or end == -1:
        return set()
    try:
        root = ET.fromstring(xmp[start : end + len("</x:xmpmeta>")])
    except ET.ParseError:
        return set()

    keywords = set()
    for elem in root.iter():
        if elem.tag.rsplit("}", 1)[-1] in _KEYWORD_FIELDS:
            keywords.update(li.text.strip() for li in elem.iter(_RDF_LI) if li.text)
    return keywords


@lru_cache(maxsize=None)
def _read_keywords(path: str, mtime: float) -> frozenset[str]:
    from PIL import Image, IptcImagePlugin

    keywords: set[str] = set()
    try:
        with Image.open(path) as im:
            if im.info.get("xmp"):
                keywords |= _keywords_from_xmp(im.info["xmp"])
            iptc = IptcImagePlugin.getiptcinfo(im) or {}
            raw = iptc.get((2, 25), [])
            for kw in raw if isinstance(raw, list) else [raw]:
                keywords.add(kw.decode("utf-8", errors="ignore").strip())
    except Exception as exc:  # unreadable/unsupported image: just no tags
        logger.debug("tagged_photos: could not read %s: %s", path, exc)

    for sidecar in (path + ".xmp", os.path.splitext(path)[0] + ".xmp"):
        if os.path.isfile(sidecar):
            with open(sidecar, "rb") as fh:
                keywords |= _keywords_from_xmp(fh.read())

    return frozenset(keywords)


def _keywords(path: str) -> frozenset[str]:
    try:
        return _read_keywords(path, os.path.getmtime(path))
    except OSError:
        return frozenset()


def _normalize(keyword: str) -> set[str]:
    """A keyword plus the leaf of its hierarchy, lowercased."""
    keyword = keyword.strip().lower()
    return {keyword, re.split(r"[|/]", keyword)[-1].strip()}


def _record_galleries(generator):
    # Wrap at generator_init (not initialized) so we sit on top of the
    # photos_compat patch regardless of signal receiver order.
    from pelican.plugins.photos import photos as photos_module

    original = photos_module.process_content_galleries
    if getattr(original, "_tagged_photos", False):
        return

    def recording(content, location, *args, **kwargs):
        galleries = original(content, location, *args, **kwargs)
        _content_galleries.setdefault(id(content), (content, []))[1].extend(galleries)
        return galleries

    recording._tagged_photos = True
    photos_module.process_content_galleries = recording


def _attach_tagged_photos(generators):
    tagged_pages = []
    for generator in generators:
        for page in getattr(generator, "pages", []) + getattr(generator, "hidden_pages", []):
            tag_value = page.metadata.get("photo_tag")
            if tag_value:
                tags = {t.strip().lower() for t in str(tag_value).split(",") if t.strip()}
                tagged_pages.append((page, tags))
    if not tagged_pages:
        return

    # src path -> (content, GalleryImage); first content to use a photo wins,
    # preferring dated articles over pages.
    by_source: dict[str, tuple[object, object]] = {}
    contents = sorted(
        (c for c, _ in _content_galleries.values()),
        key=lambda c: (type(c).__name__ != "Article", getattr(c, "date", None) is None),
    )
    for content in contents:
        for gallery in _content_galleries[id(content)][1]:
            for image in gallery.images:
                by_source.setdefault(image.src_filename, (content, image))

    leaf_index: dict[str, list[tuple[object, object]]] = {}
    for src, (content, image) in by_source.items():
        for keyword in _keywords(src):
            for norm in _normalize(keyword):
                leaf_index.setdefault(norm, []).append((content, image))

    for page, tags in tagged_pages:
        groups: dict[int, dict] = {}
        seen = set()
        for tag in tags:
            for content, image in leaf_index.get(tag, []):
                if content is page or image.src_filename in seen:
                    continue
                seen.add(image.src_filename)
                groups.setdefault(id(content), {"content": content, "photos": []})["photos"].append(image)

        page.tagged_photos = sorted(
            groups.values(),
            key=lambda g: g["content"].date.timestamp() if getattr(g["content"], "date", None) else 0,
            reverse=True,
        )
        logger.info(
            "tagged_photos: %s -> %d photos in %d posts",
            page.title, sum(len(g["photos"]) for g in page.tagged_photos), len(page.tagged_photos),
        )


def register():
    signals.generator_init.connect(_record_galleries)
    signals.all_generators_finalized.connect(_attach_tagged_photos)
