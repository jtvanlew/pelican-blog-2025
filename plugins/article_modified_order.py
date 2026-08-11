"""Sort article collections by modified date when available.

This keeps index and paginated article listings fresh when older posts are
updated, while preserving published date as a fallback.
"""

from __future__ import annotations

from pelican import signals


def _effective_article_datetime(article):
    modified = getattr(article, "modified", None)
    date = getattr(article, "date", None)
    return modified or date


def _article_sort_key(article):
    effective = _effective_article_datetime(article)
    date = getattr(article, "date", None)
    # Tie-break on published date so ordering is deterministic.
    return (effective, date)


def _sort_article_list(items):
    if not items:
        return items
    return sorted(items, key=_article_sort_key, reverse=True)


def apply_modified_ordering(generator):
    for attr in ("articles", "dates", "translations"):
        values = getattr(generator, attr, None)
        if values is not None:
            setattr(generator, attr, _sort_article_list(values))


def register():
    signals.article_generator_finalized.connect(apply_modified_ordering)
