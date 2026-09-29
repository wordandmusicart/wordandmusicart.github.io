#!/usr/bin/env python3
"""Structural acceptance gates for docs/landing-artists.md (stdlib only).

Behaviour, responsive layout and portrait identity still require browser/source
review; these checks deliberately do not assert CSS values or JS implementation.
"""
import json
import os
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(os.environ.get("SITE_ROOT", Path(__file__).resolve().parents[1]))
ORIGIN = "https://wordandmusic.art"
VOID = set("area base br col embed hr img input link meta param source track wbr".split())


class Node:
    def __init__(self, tag, attrs=(), parent=None):
        self.tag, self.attrs, self.parent = tag, dict(attrs), parent
        self.children = []

    def find(self, tag=None, cls=None):
        for child in self.children:
            if isinstance(child, Node):
                if (tag is None or child.tag == tag) and (cls is None or cls in child.attrs.get("class", "").split()):
                    yield child
                yield from child.find(tag, cls)

    def text(self):
        return " ".join(child.text() if isinstance(child, Node) else child for child in self.children)


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.root = Node("document")
        self.current = self.root
        self.feed(path.read_text(encoding="utf-8"))

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        node = self.current
        while node.parent is not None:
            if node.tag == tag:
                self.current = node.parent
                return
            node = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def links(node):
    return [a.attrs.get("href", "") for a in node.find("a")]


def primary_links(nav):
    """A mobile dropdown may also contain language and ticket controls."""
    result = []
    for anchor in nav.find("a"):
        if "mobile-ticket" in anchor.attrs.get("class", "").split():
            continue
        ancestor = anchor.parent
        in_language_control = False
        while ancestor is not nav and ancestor is not None:
            if "lang" in ancestor.attrs.get("class", "").split():
                in_language_control = True
            ancestor = ancestor.parent
        if not in_language_control:
            result.append(anchor)
    return result


def normalized_name(value):
    return " ".join(value.translate(str.maketrans({"’": "'", "ʼ": "'", "`": "'"})).split())


def public_pages():
    return sorted(set(ROOT.glob("*.html")) | set((ROOT / "en").rglob("*.html"))
                  | set((ROOT / "concerts").glob("*.html")) | set((ROOT / "photo").glob("*.html")))


class LandingArtistsAcceptance(unittest.TestCase):
    def test_public_footers_have_three_accessible_theme_choices(self):
        for path in public_pages():
            with self.subTest(page=str(path.relative_to(ROOT))):
                doc = Document(path).root
                footers = list(doc.find("footer"))
                self.assertEqual(len(footers), 1)
                controls = [node for node in footers[0].find("button") if "data-theme-mode" in node.attrs]
                self.assertEqual([node.attrs.get("data-theme-mode") for node in controls], ["auto", "light", "dark"])
                for control in controls:
                    self.assertTrue(control.attrs.get("aria-label") or control.text().strip(), "Theme buttons need accessible names")
                    self.assertEqual(control.attrs.get("aria-pressed"), str(control.attrs["data-theme-mode"] == "auto").lower())
                self.assertTrue(any(urlsplit(href).path.endswith("/privacy.html") for href in links(footers[0])), "Theme controls must share the footer with Privacy")

    def test_artist_records_are_bilingual_source_backed_and_rendered(self):
        data_path = ROOT / "assets/artists.json"
        self.assertTrue(data_path.is_file(), "The artist evidence register must exist")
        records = json.loads(data_path.read_text(encoding="utf-8"))
        self.assertIsInstance(records, list)
        self.assertTrue(records)
        ids = [record.get("id") for record in records]
        self.assertTrue(all(isinstance(value, str) and value for value in ids))
        self.assertEqual(len(ids), len(set(ids)), "Artist identities must be unique")
        archive_names = set()
        for path in sorted((ROOT / "concerts").glob("*.html")):
            for people in Document(path).root.find(cls="people"):
                archive_names.update(normalized_name(name.text()) for name in people.find("h3"))
        self.assertTrue(archive_names, "The archive must provide a performer evidence baseline")
        directory_names = {normalized_name(record.get("name", {}).get("uk", "")) for record in records}
        self.assertFalse(archive_names - directory_names,
                         f"Archive performers omitted: {sorted(archive_names - directory_names)}")
        author = [r for r in records if normalized_name(r.get("name", {}).get("uk", "")) == "Геннадій Таранюк"]
        self.assertEqual(len(author), 1, "Include the project author once")
        self.assertEqual(author[0].get("group"), "author")
        rendered = {language: Document(ROOT / prefix / "artists.html").root.text()
                    for language, prefix in (("uk", ""), ("en", "en/"))}
        for record in records:
            with self.subTest(artist=record.get("id")):
                for field in ("name", "role"):
                    for language in ("uk", "en"):
                        value = record.get(field, {}).get(language)
                        self.assertTrue(isinstance(value, str) and value.strip(), f"Missing {field}.{language}")
                        self.assertIn(value, rendered[language], f"{field}.{language} must appear in the indexable directory")
                self.assertTrue(record.get("group"))
                sources = record.get("sources")
                self.assertIsInstance(sources, list)
                self.assertTrue(sources, "Every identity/role requires an archive source")
                for source in sources:
                    parsed = urlsplit(source)
                    self.assertFalse(parsed.scheme or parsed.netloc)
                    # The register stores site-relative URLs, with or without
                    # a leading slash; both resolve from the public site root.
                    route = "/" + parsed.path.lstrip("/")
                    self.assertNotIn("..", Path(route).parts)
                    self.assertTrue(route == "/video.html" or route == "/concert.html" or route.startswith("/concerts/"))
                    source_path = ROOT / route.lstrip("/")
                    self.assertTrue(source_path.is_file(), f"Source route does not exist: {source}")
                    if parsed.fragment:
                        source_doc = Document(source_path).root
                        self.assertTrue(any(node.attrs.get("id") == parsed.fragment for node in source_doc.find()), f"Source fragment does not exist: {source}")
                portrait = record.get("portrait")
                if portrait is not None:
                    self.assertIsInstance(portrait, dict)
                    self.assertTrue(portrait.get("source"), "A portrait requires explicit image attribution")
                    src = portrait.get("src", "")
                    self.assertTrue(src.startswith("/"), "Portrait must use a preserved local asset")
                    self.assertTrue((ROOT / src.lstrip("/")).is_file(), f"Missing portrait asset: {src}")

    def test_home_has_five_ordered_scenes_and_footer_in_contacts(self):
        for prefix in ("", "en/"):
            with self.subTest(language=prefix or "uk"):
                doc = Document(ROOT / prefix / "index.html").root
                scenes = list(doc.find(cls="home-scene"))
                self.assertEqual([s.attrs.get("id") for s in scenes],
                                 ["intro", "about", "past-concerts", "media", "contacts"])
                self.assertEqual(len(list(scenes[-1].find("footer"))), 1,
                                 "The footer must belong to the last scene")
                self.assertFalse(any(n.attrs.get("id") == "repertoire" for n in doc.find()))
                self.assertFalse(any(urlsplit(href).fragment == "repertoire" for href in links(doc)))

    def test_home_preserves_ticket_programme_and_combined_media_access(self):
        for prefix, locale in (("", "uk"), ("en/", "en")):
            with self.subTest(language=locale):
                doc = Document(ROOT / prefix / "index.html").root
                scenes = {n.attrs.get("id"): n for n in doc.find(cls="home-scene")}
                self.assertIn("intro", scenes)
                intro_links = links(scenes["intro"])
                self.assertIn(f"/{prefix}concert.html", intro_links)
                self.assertTrue(any(urlsplit(href).hostname == "eventmate.app" and f"locale={locale}" in href for href in intro_links))
                self.assertIn("media", scenes)
                self.assertIn(f"/{prefix}photo.html", links(scenes["media"]))
                self.assertIn(f"/{prefix}video.html", links(scenes["media"]))

    def test_every_public_header_has_ordered_navigation_and_controls(self):
        self.assertGreater(len(public_pages()), 2)
        for path in public_pages():
            with self.subTest(page=str(path.relative_to(ROOT))):
                doc = Document(path).root
                # A section may have its own semantic header. The site header
                # is the one containing the primary navigation.
                headers = [node for node in doc.find("header")
                           if any(nav.attrs.get("id") == "nav" for nav in node.find("nav"))]
                self.assertEqual(len(headers), 1)
                header = headers[0]
                primary = list(header.find("nav"))
                self.assertEqual(len(primary), 1)
                prefix = "en/" if path.relative_to(ROOT).parts[0] == "en" else ""
                navigation_links = primary_links(primary[0])
                hrefs = [a.attrs.get("href", "") for a in navigation_links]
                self.assertEqual(hrefs[:4], [f"/{prefix}{name}.html" for name in ("concerts", "artists", "photo", "video")])
                self.assertEqual([urlsplit(href).fragment for href in hrefs[4:]], ["about", "contacts"])
                self.assertFalse(any(urlsplit(href).fragment == "repertoire" for href in links(header)))
                self.assertTrue(list(header.find(cls="lang")), "Language choice must remain in header")
                locale = "en" if prefix else "uk"
                self.assertTrue(any(urlsplit(href).hostname == "eventmate.app" and f"locale={locale}" in href for href in links(header)), "Header ticket link must retain page language")
                route = path.relative_to(ROOT).as_posix()
                leaf = path.name
                expected = leaf.removesuffix(".html") if leaf in {"artists.html", "concerts.html", "photo.html", "video.html"} else None
                current = [a.attrs.get("href") for a in navigation_links if a.attrs.get("aria-current", "false") != "false"]
                if expected:
                    self.assertEqual(current, [f"/{prefix}{expected}.html"])
                    selected = next(a for a in navigation_links if a.attrs.get("href") == current[0])
                    self.assertEqual(selected.attrs.get("aria-current"), "page")
                elif leaf == "concert.html" or "/concerts/" in "/" + route:
                    self.assertTrue(not current or current == [f"/{prefix}concerts.html"])
                elif "/photo/" in "/" + route:
                    self.assertTrue(not current or current == [f"/{prefix}photo.html"])
                else:
                    self.assertEqual(current, [], "Home/privacy must not mark another page current")

    def test_artist_routes_have_paired_metadata_language_links_and_sitemap(self):
        sitemap = ET.parse(ROOT / "sitemap.xml")
        urls = {n.text for n in sitemap.iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        for prefix, language, twin in (("", "uk", "/en/artists.html"), ("en/", "en", "/artists.html")):
            with self.subTest(language=language):
                path = ROOT / prefix / "artists.html"
                self.assertTrue(path.is_file(), f"Missing public artist route: {path.relative_to(ROOT)}")
                doc = Document(path).root
                self.assertEqual(next(doc.find("html")).attrs.get("lang"), language)
                metadata = list(doc.find("link"))
                canonical = [n.attrs.get("href") for n in metadata if n.attrs.get("rel") == "canonical"]
                self.assertEqual(canonical, [f"{ORIGIN}/{prefix}artists.html"])
                alternatives = {n.attrs.get("hreflang"): n.attrs.get("href") for n in metadata if n.attrs.get("rel") == "alternate"}
                self.assertEqual(alternatives.get("uk"), f"{ORIGIN}/artists.html")
                self.assertEqual(alternatives.get("en"), f"{ORIGIN}/en/artists.html")
                self.assertIn(canonical[0], urls)
                language_control = next(doc.find(cls="lang"), None)
                self.assertIsNotNone(language_control)
                self.assertIn(twin, links(language_control))
                self.assertTrue(list(doc.find("h1")), "Artists page must be indexable without JavaScript")


if __name__ == "__main__":
    unittest.main()
