#!/usr/bin/env python3
"""Acceptance contract for the three concert posters supplied in September 2026.

Run from any directory:
    python3 tools/test_concert_archive_2025_2026.py

The test intentionally uses only the Python standard library so it can also run
as a small CI gate for this static site.
"""

from __future__ import annotations

import html
import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ORIGIN = "https://wordandmusic.art"


CONCERTS = (
    {
        "slug": "soul-wanderings",
        "date": "14.02",
        "ua_listing": ("Де блукає душа", "Садиба на Кудрявці"),
        "en_listing": ("Where the Soul Wanders", "Kudriavka Manor"),
        "ua_text": (
            "Де блукає душа",
            "Мандрівка кохання",
            "Шуберт",
            "Шуман",
            "Брамс",
            "Марія Попович",
            "Микола Чикаренко",
            "Геннадій Таранюк",
            "Садиба на Кудрявці",
        ),
        "en_text": (
            "Where the Soul Wanders",
            "Mariia Popovych",
            "Mykola Chykarenko",
            "Hennadii Taraniuk",
            "Kudriavka Manor",
        ),
    },
    {
        "slug": "melodies-eternelles",
        "date": "03.08",
        "ua_listing": ("Mélodies éternelles", "Садиба на Кудрявці"),
        "en_listing": ("Mélodies éternelles", "Kudriavka Manor"),
        "ua_text": (
            "Mélodies éternelles",
            "Марія Попович",
            "Микола Чикаренко",
            "Геннадій Таранюк",
            "Ж. Бізе",
            "Ф. Пуленка",
            "М. Равеля",
            "Садиба на Кудрявці",
        ),
        "en_text": (
            "Mélodies éternelles",
            "Mariia Popovych",
            "Mykola Chykarenko",
            "Hennadii Taraniuk",
            "Kudriavka Manor",
        ),
    },
    {
        "slug": "stabat-mater",
        "date": "16.04",
        "ua_listing": ("Stabat Mater", "Софія Київська"),
        "en_listing": ("Stabat Mater", "Sophia of Kyiv"),
        "ua_text": (
            "Giovanni Battista Pergolesi",
            "Stabat Mater",
            "Наталія Скринник",
            "Марія Попович",
            "Поліна Буракова",
            "Геннадій Таранюк",
            "Софія Київська",
            "Хлібня",
        ),
        "en_text": (
            "Giovanni Battista Pergolesi",
            "Stabat Mater",
            "Nataliia Skrynnyk",
            "Mariia Popovych",
            "Polina Burakova",
            "Hennadii Taraniuk",
            "Sophia of Kyiv",
            "Khlibnia",
        ),
    },
)


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.text_parts: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str]] = []
        self.elements: list[tuple[str, dict[str, str]]] = []
        self.json_ld: list[str] = []
        self.rows: list[dict[str, object]] = []
        self._json_ld_parts: list[str] | None = None
        self._row_depth = 0
        self._row: dict[str, object] | None = None

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        self.elements.append((tag, values))
        if tag == "meta":
            self.metas.append(values)
        elif tag == "link":
            self.links.append(values)
        elif tag == "img":
            self.images.append(values)
        elif tag == "script" and values.get("type", "").lower() == "application/ld+json":
            self._json_ld_parts = []
        if tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])

        if tag == "div":
            classes = values.get("class", "").split()
            if self._row is None and "arow" in classes:
                self._row = {"text": [], "hrefs": [], "images": []}
                self._row_depth = 1
            elif self._row is not None:
                self._row_depth += 1

        if self._row is not None:
            if tag == "a" and values.get("href"):
                self._row["hrefs"].append(values["href"])
            elif tag == "img":
                self._row["images"].append(values)

    def handle_endtag(self, tag: str) -> None:
        if tag == "script" and self._json_ld_parts is not None:
            self.json_ld.append("".join(self._json_ld_parts))
            self._json_ld_parts = None
        if tag == "div" and self._row is not None:
            self._row_depth -= 1
            if self._row_depth == 0:
                self.rows.append(self._row)
                self._row = None

    def handle_data(self, data: str) -> None:
        if self._json_ld_parts is not None:
            self._json_ld_parts.append(data)
        value = data.strip()
        if value:
            self.text_parts.append(value)
            if self._row is not None:
                self._row["text"].append(value)

    @property
    def text(self) -> str:
        return " ".join(self.text_parts)


def parse(path: Path) -> Document:
    parser = Document()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def normalized(value: str) -> str:
    return " ".join(html.unescape(value).split())


def music_events(value: object):
    """Yield MusicEvent objects from either a direct object or an @graph."""
    if isinstance(value, list):
        for item in value:
            yield from music_events(item)
    elif isinstance(value, dict):
        event_type = value.get("@type")
        types = event_type if isinstance(event_type, list) else [event_type]
        if "MusicEvent" in types:
            yield value
        if "@graph" in value:
            yield from music_events(value["@graph"])


def check_listing(
    path: Path,
    language: str,
    href_prefix: str,
    failures: list[str],
) -> None:
    check(path.is_file(), f"missing {language} listing: {path.relative_to(ROOT)}", failures)
    if not path.is_file():
        return
    doc = parse(path)
    for concert in CONCERTS:
        href = f"{href_prefix}{concert['slug']}.html"
        row = next((row for row in doc.rows if href in row["hrefs"]), None)
        check(row is not None, f"{language} listing has no archive row linking to {href}", failures)
        if row is None:
            continue
        row_text = normalized(" ".join(row["text"]))
        title, venue = concert[f"{language}_listing"]
        for expected in (concert["date"], title, venue):
            check(
                expected in row_text,
                f"{language} row {href} does not preserve {expected!r}",
                failures,
            )

    chronological_slugs = (
        "soul-wanderings",
        "autumn-rendezvous",
        "melodies-eternelles",
        "melodies-of-enchanting-june",
        "stabat-mater",
    )
    chronological_hrefs = [f"{href_prefix}{slug}.html" for slug in chronological_slugs]
    if all(href in doc.hrefs for href in chronological_hrefs):
        positions = [doc.hrefs.index(href) for href in chronological_hrefs]
        check(
            positions == sorted(positions),
            f"{language} archive is not reverse chronological: "
            + " -> ".join(chronological_hrefs),
            failures,
        )


def check_detail(
    concert: dict[str, object], language: str, failures: list[str]
) -> None:
    slug = concert["slug"]
    relative = Path("concerts", f"{slug}.html")
    if language == "en":
        relative = Path("en") / relative
    path = ROOT / relative
    check(path.is_file(), f"missing {language.upper()} detail page: {relative}", failures)
    if not path.is_file():
        return

    doc = parse(path)
    page_text = normalized(doc.text)
    for expected in concert[f"{language}_text"]:
        check(
            expected in page_text,
            f"{relative} does not preserve poster text {expected!r}",
            failures,
        )

    ua_url = f"{ORIGIN}/concerts/{slug}.html"
    en_url = f"{ORIGIN}/en/concerts/{slug}.html"
    own_url = en_url if language == "en" else ua_url

    robots = " ".join(
        meta.get("content", "").lower()
        for meta in doc.metas
        if meta.get("name", "").lower() == "robots"
    )
    check("noindex" not in robots, f"{relative} must not contain noindex", failures)
    check("nofollow" not in robots, f"{relative} must not contain nofollow", failures)

    canonicals = [
        link.get("href")
        for link in doc.links
        if "canonical" in link.get("rel", "").lower().split()
    ]
    check(canonicals == [own_url], f"{relative} must have self-canonical {own_url}", failures)

    og_urls = [m.get("content") for m in doc.metas if m.get("property") == "og:url"]
    check(og_urls == [own_url], f"{relative} must have og:url {own_url}", failures)

    alternates = {
        link.get("hreflang"): link.get("href")
        for link in doc.links
        if "alternate" in link.get("rel", "").split()
    }
    check(alternates.get("uk") == ua_url, f"{relative} has wrong/missing UK hreflang", failures)
    check(alternates.get("en") == en_url, f"{relative} has wrong/missing EN hreflang", failures)

    events: list[dict[str, object]] = []
    for source in doc.json_ld:
        try:
            events.extend(music_events(json.loads(source)))
        except json.JSONDecodeError as error:
            failures.append(f"{relative} has invalid JSON-LD: {error}")
    check(not events, f"{relative} historical page must not contain MusicEvent", failures)

    forbidden_classes = {"c-cta", "sticky-buy"}
    found_forbidden = sorted(
        class_name
        for _, values in doc.elements
        for class_name in values.get("class", "").split()
        if class_name in forbidden_classes
    )
    check(
        not found_forbidden,
        f"{relative} historical page contains event-specific buy UI {found_forbidden}",
        failures,
    )

    poster = next(
        (image for image in doc.images if f"/{slug}-poster" in image.get("src", "")),
        None,
    )
    check(poster is not None, f"{relative} has no {slug} poster image", failures)
    if poster is None:
        return
    srcset = poster.get("srcset", "")
    check(bool(srcset), f"{relative} poster has no srcset", failures)
    for width in ("480w", "960w"):
        check(width in srcset, f"{relative} poster srcset has no {width} candidate", failures)
    for candidate in [poster.get("src", "")] + [part.strip().split()[0] for part in srcset.split(",") if part.strip()]:
        local_path = urlparse(candidate).path.lstrip("/")
        check(bool(local_path) and (ROOT / local_path).is_file(), f"{relative} references missing poster asset {candidate}", failures)


def main() -> int:
    failures: list[str] = []
    check_listing(ROOT / "concerts.html", "ua", "/concerts/", failures)
    check_listing(ROOT / "en/concerts.html", "en", "/en/concerts/", failures)
    for concert in CONCERTS:
        check_detail(concert, "ua", failures)
        check_detail(concert, "en", failures)

    if failures:
        print(f"FAIL: {len(failures)} archive acceptance check(s) failed", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("PASS: all three concerts have complete UA/EN archive coverage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
