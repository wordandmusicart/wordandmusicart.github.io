#!/usr/bin/env python3
"""Acceptance contract for venue blocks on every archived concert page.

Run from any directory:
    python3 tools/test_concert_venues.py

The test intentionally uses only the Python standard library so it can run as
a small CI gate for this static site.
"""

from __future__ import annotations

import html
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
ANNOUNCED_SLUGS = ("on-the-wings-of-love", "on-the-wings-of-love-25102026")

CONCERT_SLUGS = (
    "amore-eterno",
    "autumn-rendezvous",
    "christmas-kaleidoscope",
    "heartstrings",
    "melodies-eternelles",
    "melodies-of-enchanting-june",
    "music-of-soul-and-heart",
    "roads-of-love",
    "soul-wanderings",
    "stabat-mater",
    "winter-extravaganza",
    "vivre-aimer-rever",
)

POSTER_SLUGS = (
    "soul-wanderings",
    "melodies-eternelles",
    "stabat-mater",
)


class Document(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: list[tuple[str, dict[str, str | None]]] = []
        self.nodes: list[dict[str, object]] = []
        self.sections: list[dict[str, object]] = []
        self.subnav_hrefs: list[str] = []
        self._node_stack: list[dict[str, object]] = []
        self._section_stack: list[dict[str, object]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        position = len(self.elements)
        self.elements.append((tag, values))
        node: dict[str, object] = {
            "tag": tag,
            "attrs": values,
            "text": [],
            "parent": self._node_stack[-1] if self._node_stack else None,
        }
        self.nodes.append(node)

        if tag == "a" and values.get("href") and any(
            ancestor["tag"] == "nav"
            and "subnav" in classes(ancestor["attrs"])
            for ancestor in self._node_stack
        ):
            self.subnav_hrefs.append(values["href"])
        self._node_stack.append(node)

        if tag == "section":
            section: dict[str, object] = {
                "attrs": values,
                "position": position,
                "text": [],
                "elements": [],
                "nodes": [],
            }
            self.sections.append(section)
            self._section_stack.append(section)

        for section in self._section_stack:
            section["elements"].append((tag, values))
            section["nodes"].append(node)

    def handle_startendtag(self, tag: str, attrs) -> None:
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "section" and self._section_stack:
            self._section_stack.pop()
        for index in range(len(self._node_stack) - 1, -1, -1):
            if self._node_stack[index]["tag"] == tag:
                del self._node_stack[index:]
                break

    def handle_data(self, data: str) -> None:
        value = data.strip()
        if value:
            for node in self._node_stack:
                node["text"].append(value)
            for section in self._section_stack:
                section["text"].append(value)


def parse(path: Path) -> Document:
    parser = Document()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def check(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def classes(attrs: dict[str, str | None]) -> set[str]:
    return set((attrs.get("class") or "").split())


def normalized(parts: list[str]) -> str:
    return " ".join(html.unescape(" ".join(parts)).split())


def is_google_maps_url(href: str) -> bool:
    parsed = urlparse(html.unescape(href))
    hostname = (parsed.hostname or "").lower()
    return hostname in {"google.com", "www.google.com", "maps.google.com"} and (
        parsed.path.startswith("/maps") or hostname == "maps.google.com"
    )


def check_page(path: Path, language: str, failures: list[str]) -> None:
    relative = path.relative_to(ROOT)
    check(path.is_file(), f"missing {language} concert page: {relative}", failures)
    if not path.is_file():
        return

    doc = parse(path)
    venues = [
        section
        for section in doc.sections
        if section["attrs"].get("id") == "venue"
        and "venue" in classes(section["attrs"])
    ]
    check(
        len(venues) == 1,
        f"{relative} must contain exactly one section.venue#venue (found {len(venues)})",
        failures,
    )
    if len(venues) != 1:
        return

    venue = venues[0]
    related = [
        section
        for section in doc.sections
        if "related" in classes(section["attrs"])
    ]
    check(bool(related), f"{relative} has no section.related", failures)
    if related:
        check(
            venue["position"] < related[0]["position"],
            f"{relative} venue section must appear before section.related",
            failures,
        )

    venue_text = normalized(venue["text"])
    label = "Локація" if language == "UA" else "Location"
    check(label in venue_text, f"{relative} venue has no {label!r} label", failures)

    venue_elements = venue["elements"]
    venue_nodes = venue["nodes"]
    names = [
        node
        for node in venue_nodes
        if node["tag"] == "h3" and normalized(node["text"])
    ]
    addresses = [
        node
        for node in venue_nodes
        if node["tag"] == "p" and normalized(node["text"])
    ]
    check(bool(names), f"{relative} venue has no non-empty name heading", failures)
    check(bool(addresses), f"{relative} venue has no non-empty address paragraph", failures)

    linked_names = [
        node
        for node in venue_nodes
        if node["tag"] == "a"
        and "plc" in classes(node["attrs"])
        and bool((node["attrs"].get("href") or "").strip())
        and isinstance(node["parent"], dict)
        and node["parent"]["tag"] == "h3"
    ]
    check(
        bool(linked_names),
        f"{relative} venue name must be an h3 containing a.plc[href]",
        failures,
    )

    map_links = [
        attrs
        for tag, attrs in venue_elements
        if tag == "a"
        and isinstance(attrs.get("href"), str)
        and is_google_maps_url(attrs["href"])
    ]
    check(bool(map_links), f"{relative} venue has no Google Maps link", failures)

    iframes = [attrs for tag, attrs in venue_elements if tag == "iframe"]
    check(len(iframes) == 1, f"{relative} venue must contain exactly one iframe", failures)
    if len(iframes) == 1:
        iframe = iframes[0]
        src = iframe.get("src") or ""
        check(is_google_maps_url(src), f"{relative} iframe is not a Google Maps embed", failures)
        check(iframe.get("loading") == "lazy", f"{relative} iframe must use loading=lazy", failures)
        check(bool((iframe.get("title") or "").strip()), f"{relative} iframe has no title", failures)
        check(
            bool((iframe.get("referrerpolicy") or "").strip()),
            f"{relative} iframe has no referrerpolicy",
            failures,
        )
        check("allowfullscreen" in iframe, f"{relative} iframe has no allowfullscreen", failures)

    check(
        doc.subnav_hrefs.count("#venue") == 1,
        f"{relative} must contain exactly one subnav link to #venue",
        failures,
    )


def check_no_figcaption(path: Path, failures: list[str]) -> None:
    relative = path.relative_to(ROOT)
    check(path.is_file(), f"missing concert detail page: {relative}", failures)
    if not path.is_file():
        return
    doc = parse(path)
    figcaptions = [attrs for tag, attrs in doc.elements if tag == "figcaption"]
    check(
        not figcaptions,
        f"{relative} must not contain poster figcaption (found {len(figcaptions)})",
        failures,
    )


def object_position(style: str) -> tuple[float, float] | None:
    match = re.search(
        r"(?:^|;)\s*object-position\s*:\s*([-+]?\d+(?:\.\d+)?)%\s+"
        r"([-+]?\d+(?:\.\d+)?)%\s*(?:;|$)",
        style,
        flags=re.IGNORECASE,
    )
    return (float(match.group(1)), float(match.group(2))) if match else None


def check_listing(path: Path, language: str, failures: list[str]) -> None:
    relative = path.relative_to(ROOT)
    check(path.is_file(), f"missing {language} listing: {relative}", failures)
    if not path.is_file():
        return

    doc = parse(path)
    positions: dict[str, tuple[float, float]] = {}
    for slug in POSTER_SLUGS:
        matches = [
            attrs
            for tag, attrs in doc.elements
            if tag == "img" and f"/{slug}-poster" in (attrs.get("src") or "")
        ]
        check(
            len(matches) == 1,
            f"{relative} must contain exactly one {slug} thumbnail (found {len(matches)})",
            failures,
        )
        if len(matches) != 1:
            continue
        style = matches[0].get("style") or ""
        position = object_position(style)
        check(
            position is not None,
            f"{relative} {slug} thumbnail needs inline object-position: X% Y%",
            failures,
        )
        if position is not None:
            positions[slug] = position

    if len(positions) != len(POSTER_SLUGS):
        return
    styles = [positions[slug] for slug in POSTER_SLUGS]
    check(
        len(set(styles)) == len(styles),
        f"{relative} three poster thumbnails must have distinct object-position values",
        failures,
    )
    stabat_y = positions["stabat-mater"][1]
    check(
        stabat_y == 44,
        f"{relative} stabat-mater Y must be 44% so the full title remains visible "
        f"(found {stabat_y:g}%)",
        failures,
    )
    melodies_y = positions["melodies-eternelles"][1]
    for slug in ("soul-wanderings", "stabat-mater"):
        check(
            melodies_y < positions[slug][1],
            f"{relative} melodies-eternelles Y ({melodies_y:g}%) must be smaller than "
            f"{slug} Y ({positions[slug][1]:g}%)",
            failures,
        )


def main() -> int:
    failures: list[str] = []

    ua_pages = sorted((ROOT / "concerts").glob("*.html"))
    en_pages = sorted((ROOT / "en/concerts").glob("*.html"))
    expected_ua = [ROOT / "concerts" / f"{slug}.html" for slug in CONCERT_SLUGS]
    expected_en = [ROOT / "en/concerts" / f"{slug}.html" for slug in CONCERT_SLUGS]
    announced_ua = [ROOT / "concerts" / f"{slug}.html" for slug in ANNOUNCED_SLUGS]
    announced_en = [ROOT / "en/concerts" / f"{slug}.html" for slug in ANNOUNCED_SLUGS]
    archive_ua = [path for path in ua_pages if path not in announced_ua]
    archive_en = [path for path in en_pages if path not in announced_en]
    check(len(archive_ua) == len(CONCERT_SLUGS), f"concerts/ must contain 12 archive pages (found {len(archive_ua)})", failures)
    check(len(archive_en) == len(CONCERT_SLUGS), f"en/concerts/ must contain 12 archive pages (found {len(archive_en)})", failures)
    check(ua_pages == sorted(expected_ua + announced_ua), "concerts/ page set differs from the 12-page archive plus known announcements", failures)
    check(en_pages == sorted(expected_en + announced_en), "en/concerts/ page set differs from the 12-page archive plus known announcements", failures)

    for path in expected_ua:
        check_page(path, "UA", failures)
    for path in expected_en:
        check_page(path, "EN", failures)

    for path in [ROOT / "concert.html", ROOT / "en/concert.html", *expected_ua, *expected_en]:
        check_no_figcaption(path, failures)

    check_listing(ROOT / "concerts.html", "UA", failures)
    check_listing(ROOT / "en/concerts.html", "EN", failures)

    if failures:
        print(f"FAIL: {len(failures)} venue acceptance check(s) failed", file=sys.stderr)
        for failure in failures:
            print(f" - {failure}", file=sys.stderr)
        return 1
    print("PASS: all 24 archive pages have complete venue blocks and poster crops")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
