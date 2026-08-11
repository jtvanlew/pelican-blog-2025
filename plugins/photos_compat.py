"""Compatibility shims for pelican.plugins.photos behavior used by this site.

This keeps custom behavior in-repo (configurable and versioned) instead of
patching third-party files under site-packages.
"""

from __future__ import annotations

import datetime
import os
import re
from functools import lru_cache
from typing import Any, Dict, List

from pelican import signals


def _parse_exif_datetime(value):
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="ignore")
    if not isinstance(value, str):
        return None

    value = value.strip()
    if not value:
        return None

    try:
        return datetime.datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except ValueError:
        return None


def _normalize_sort_mode(value, default="capture"):
    if value is None:
        return default

    mode = str(value).strip().lower()
    if mode in {"filename", "name", "alpha", "alphabetical"}:
        return "filename"
    if mode in {"capture", "date", "exif"}:
        return "capture"
    return default


def _content_gallery_sort_default(content):
    metadata = getattr(content, "metadata", {}) or {}

    sort_keys = {"gallery_sort", "photo_gallery_sort", "gallerysort"}

    for raw_key, raw_val in metadata.items():
        norm_key = str(raw_key).strip().lower().replace("-", "_").replace(" ", "_")
        if norm_key in sort_keys:
            return _normalize_sort_mode(raw_val, default="capture")

    for key in sort_keys:
        attr_val = getattr(content, key, None)
        if attr_val is not None:
            return _normalize_sort_mode(attr_val, default="capture")

    return "capture"


@lru_cache(maxsize=4096)
def _image_taken_sort_key(file_path, photos_module):
    file_name = os.path.basename(file_path).lower()

    filename_dt = None
    # Fallback to datetime hints in common camera/export filename formats.
    filename_patterns = (
        r"img[_-]?(?P<date>\d{8})[_-]?(?P<time>\d{6})",
        r"(?P<date>\d{8})[_-](?P<time>\d{6})",
        r"(?P<date>\d{8})[-_](?:dsc|img|pxl|marin)",
        r"(?P<date>\d{8})",
    )
    for pattern in filename_patterns:
        match = re.search(pattern, file_name)
        if not match:
            continue

        date_part = match.groupdict().get("date")
        time_part = match.groupdict().get("time") or "000000"
        if not date_part:
            continue

        try:
            filename_dt = datetime.datetime.strptime(
                f"{date_part}{time_part}", "%Y%m%d%H%M%S"
            )
            break
        except ValueError:
            continue

    try:
        with photos_module.PILImage.open(file_path) as image:
            exif_data = image.getexif()
            if exif_data:
                for tag_name in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                    tag_code = photos_module.EXIF_TAGS_NAME_CODE.get(tag_name)
                    if tag_code is None:
                        continue
                    parsed = _parse_exif_datetime(exif_data.get(tag_code))
                    if parsed is not None:
                        if filename_dt is not None:
                            # Re-exports can overwrite EXIF with import-time values.
                            # If EXIF and filename disagree heavily, trust filename date.
                            if abs((parsed - filename_dt).days) > 365:
                                return (0, filename_dt, file_name)
                        return (0, parsed, file_name)
    except Exception:
        pass

    if filename_dt is not None:
        return (0, filename_dt, file_name)

    return (1, file_name)


def _gallery_init_sorted_by_capture_time(self, content, location_parsed, profile_name=None, profile=None, photos_module=None):
    self.content = content

    if profile is None:
        if profile_name is None:
            profile_name = "default"
        self.profile = photos_module.get_profile(profile_name)
    else:
        self.profile = profile

    if location_parsed["type"] == "{photo}":
        dir_gallery = os.path.join(
            os.path.expanduser(photos_module.pelican_settings["PHOTO_LIBRARY"]),
            location_parsed["location"],
        )
        rel_gallery = location_parsed["location"]
    elif location_parsed["type"] == "{filename}":
        base_path = os.path.join(photos_module.pelican_settings["PATH"], content.relative_dir)
        dir_gallery = os.path.join(base_path, location_parsed["location"])
        rel_gallery = os.path.join(content.relative_dir, location_parsed["location"])
    else:
        raise photos_module.GalleryNotFound(
            f"Unsupported gallery type: {location_parsed['type']}"
        )

    if not os.path.isdir(dir_gallery):
        raise photos_module.GalleryNotFound(
            "Gallery does not exist: {} at {}".format(
                location_parsed["location"], dir_gallery
            )
        )

    image_filenames = []
    photos_module.logger.info(f"photos: Gallery detected: {rel_gallery}")

    gallery_entries = []
    for pic in os.listdir(dir_gallery):
        pic_path = os.path.join(dir_gallery, pic)
        if pic.startswith("."):
            continue
        if pic.endswith(".txt"):
            continue
        if not os.path.isfile(pic_path):
            continue
        gallery_entries.append(pic)

    sort_mode = _normalize_sort_mode(location_parsed.get("sort"), default="capture")
    if sort_mode == "filename":
        sorted_entries = sorted(gallery_entries, key=lambda name: name.lower())
    else:
        sorted_entries = sorted(
            gallery_entries,
            key=lambda name: _image_taken_sort_key(os.path.join(dir_gallery, name), photos_module),
        )

    for pic in sorted_entries:
        image_filename = os.path.join(location_parsed["location"], pic)
        image_filenames.append(f"{location_parsed['type']}{image_filename}")

    self.dst_dir = os.path.join("photos", rel_gallery.lower())
    self.images = []

    self.title = location_parsed["title"]
    for pic in image_filenames:
        try:
            self.images.append(
                photos_module.GalleryImage(
                    filename=pic,
                    gallery=self,
                    profile=self.profile,
                )
            )
        except photos_module.ImageExcluded:
            photos_module.logger.debug(f"photos: Image {pic} excluded")
        except photos_module.FileExcluded as exc:
            photos_module.logger.debug(f"photos: File {pic} excluded: {exc!s}")


def _galleries_string_decompose_with_slice(gallery_string, photos_module):
    """Parse gallery strings with optional Python-like slice suffix.

    Supports values like:
    - {photo}2025/09-12-Trip[0:10]
    - {photo}2025/09-12-Trip[3]
    - {photo}2025/09-12-Trip[1:9:2]
    - {photo}2025/09-12-Trip|sort=filename
    - {photo}2025/09-12-Trip[10:20]|sort=capture
    """
    splitter_regex = re.compile(r"[\s,]*?({photo}|{filename})")
    title_regex = re.compile(r"{(.+)}")
    slice_regex = re.compile(r"(?P<base>.*?)(?:\[(?P<slice>[-,\d:\s]+)\])?$")

    galleries = map(str.strip, filter(None, splitter_regex.split(gallery_string)))
    galleries = [g[1:] if g.startswith("/") else g for g in galleries]

    if len(galleries) % 2 != 0 or " " in galleries:
        photos_module.logger.error(
            "Unexpected gallery location format! \n%s", galleries
        )
        return []

    pairs = zip(
        zip(["type"] * len(galleries[0::2]), galleries[0::2]),
        zip(["location"] * len(galleries[0::2]), galleries[1::2]),
    )
    parsed = [dict(p) for p in pairs]

    for gallery in parsed:
        title = re.search(title_regex, gallery["location"])
        if title:
            gallery["title"] = title.group(1)
            gallery["location"] = re.sub(title_regex, "", gallery["location"]).strip()
        else:
            gallery["title"] = photos_module.DEFAULT_CONFIG["PHOTO_GALLERY_TITLE"]

        options = []
        location_and_options = [part.strip() for part in gallery["location"].split("|") if part.strip()]
        if location_and_options:
            gallery["location"] = location_and_options[0]
            options = location_and_options[1:]

        gallery["sort"] = None
        for option in options:
            key, sep, value = option.partition("=")
            if sep and key.strip().lower() == "sort":
                gallery["sort"] = _normalize_sort_mode(value, default=None)

        match = re.search(slice_regex, gallery["location"])
        gallery["slice"] = None
        if not match:
            continue

        gallery["location"] = match.group("base")
        slice_spec = match.group("slice")
        if not slice_spec:
            continue

        parts = [p.strip() for p in slice_spec.split(":")]
        try:
            if len(parts) == 1:
                start = int(parts[0])
                gallery["slice"] = slice(start, start + 1, None)
            elif len(parts) == 2:
                start = int(parts[0]) if parts[0] else None
                stop = int(parts[1]) if parts[1] else None
                gallery["slice"] = slice(start, stop, None)
            elif len(parts) == 3:
                start = int(parts[0]) if parts[0] else None
                stop = int(parts[1]) if parts[1] else None
                step = int(parts[2]) if parts[2] else None
                gallery["slice"] = slice(start, stop, step)
        except ValueError:
            photos_module.logger.warning(
                "photos: Invalid slice specification '%s' for gallery '%s'",
                slice_spec,
                gallery["location"],
            )

    return parsed


def _process_content_galleries_with_slice(content, location, profile_name, photos_module):
    photo_galleries = []
    galleries = photos_module.galleries_string_decompose(location)
    content_sort_default = _content_gallery_sort_default(content)

    for gallery_name in galleries:
        try:
            if not gallery_name.get("sort"):
                gallery_name["sort"] = content_sort_default
            gallery = photos_module.Gallery(content, gallery_name, profile_name=profile_name)
            gallery_slice = gallery_name.get("slice")
            if gallery_slice:
                gallery.images = gallery.images[gallery_slice]
            photo_galleries.append(gallery)
        except photos_module.GalleryNotFound as exc:
            photos_module.logger.error("photos: %s", exc)

    return photo_galleries


def _apply_photos_patches(_pelican):
    from pelican.plugins import photos as photos_pkg
    from pelican.plugins.photos import photos as photos_module

    # Broaden inline gallery regex via config default so [start:stop] is captured.
    _pelican.settings.setdefault(
        "PHOTO_INLINE_GALLERY_PATTERN",
        r"gallery::(?P<gallery_name>[/{}\w\[\]:,._\-=|]+)",
    )

    patched_galleries_string_decompose = (
        lambda gallery_string: _galleries_string_decompose_with_slice(gallery_string, photos_module)
    )
    patched_process_content_galleries = (
        lambda content, location, profile_name=None: _process_content_galleries_with_slice(
            content, location, profile_name, photos_module
        )
    )

    photos_module.galleries_string_decompose = patched_galleries_string_decompose
    photos_module.process_content_galleries = patched_process_content_galleries

    # Also mirror these hooks to the package namespace for compatibility with
    # import styles that reference `pelican.plugins.photos` directly.
    photos_pkg.galleries_string_decompose = patched_galleries_string_decompose
    photos_pkg.process_content_galleries = patched_process_content_galleries

    # Ignore sidecar/non-image files (e.g. .xmp) without patching site-packages.
    original_source_image_init = photos_module.SourceImage.__init__
    original_image_process = photos_module.Image.process

    def _source_image_init_compat(self, filename, *args, **kwargs):
        filename_lower = str(filename).lower()
        if filename_lower.endswith((".heic", ".heif")):
            photos_module.logger.warning(
                "photos: Skipping unsupported HEIC image '%s'",
                filename,
            )
            raise photos_module.FileExcluded("Unsupported HEIC image format")

        try:
            original_source_image_init(self, filename, *args, **kwargs)
        except photos_module.InternalError as exc:
            if filename_lower.endswith((".xmp", ".-iptc")):
                raise photos_module.FileExcluded("Sidecar metadata file") from exc
            if "unable to get mime type" in str(exc).lower():
                photos_module.logger.warning(
                    "photos: Skipping non-image file with unknown MIME '%s'",
                    filename,
                )
                raise photos_module.FileExcluded("Unknown MIME/non-image file") from exc
            raise

    def _image_process_compat(self, *args, **kwargs):
        try:
            return original_image_process(self, *args, **kwargs)
        except Exception as exc:
            filename = str(getattr(self.source_image, "filename", "")).lower()
            is_heic = filename.endswith((".heic", ".heif"))
            is_unidentified = exc.__class__.__name__ == "UnidentifiedImageError"
            if is_heic and is_unidentified:
                photos_module.logger.warning(
                    "photos: Skipping unsupported HEIC image '%s'",
                    getattr(self.source_image, "filename", filename),
                )
                return None
            raise

    photos_module.SourceImage.__init__ = _source_image_init_compat
    photos_module.Image.process = _image_process_compat
    photos_module.Gallery.__init__ = (
        lambda self, content, location_parsed, profile_name=None, profile=None: _gallery_init_sorted_by_capture_time(
            self,
            content,
            location_parsed,
            profile_name=profile_name,
            profile=profile,
            photos_module=photos_module,
        )
    )
    photos_pkg.Gallery = photos_module.Gallery


def register():
    signals.initialized.connect(_apply_photos_patches)
