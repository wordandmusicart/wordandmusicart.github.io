#!/usr/bin/env python3
"""Independent sitemap/canonical acceptance for the production static site.

Expected URLs come from the public HTML inventory and the explicit concert
alias contract, not the sitemap generator. Checker corruption tests use copies.
"""
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit

from test_landing_artists import Document

ROOT = Path(os.environ.get("SITE_ROOT", Path(__file__).resolve().parents[1]))
ORIGIN = "https://wordandmusic.art"
SM = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
XHTML = "{http://www.w3.org/1999/xhtml}"
ALIASES = {
    "concert.html": "concerts/on-the-wings-of-love.html",
    "en/concert.html": "en/concerts/on-the-wings-of-love.html",
}


def production_pages():
    return sorted(path for path in ROOT.rglob("*.html")
                  if not any(part.startswith(".") or part in {"_site", "node_modules", "tools"}
                             for part in path.relative_to(ROOT).parts))


def canonical_url(relative):
    target = ALIASES.get(relative, relative)
    if target == "index.html":
        target = ""
    elif target == "en/index.html":
        target = "en/"
    return ORIGIN + "/" + target


def language_urls(relative):
    target = ALIASES.get(relative, relative).removeprefix("en/")
    return {"uk": canonical_url(target), "en": canonical_url("en/" + target),
            "x-default": canonical_url("en/" + target)}


def expected_urls():
    return {canonical_url(path.relative_to(ROOT).as_posix())
            for path in production_pages() if path.name != "404.html"}


class SitemapAcceptance(unittest.TestCase):
    def test_every_indexable_page_has_production_canonical_og_url_and_reciprocal_head_languages(self):
        for path in production_pages():
            if path.name == "404.html":
                continue
            relative = path.relative_to(ROOT).as_posix()
            with self.subTest(page=relative):
                head = next(Document(path).root.find("head"))
                canonical = [node.attrs.get("href") for node in head.find("link")
                             if "canonical" in node.attrs.get("rel", "").lower().split()]
                self.assertEqual(canonical, [canonical_url(relative)])
                metas = list(head.find("meta"))
                self.assertEqual([node.attrs.get("content") for node in metas
                                  if node.attrs.get("property") == "og:url"], canonical)
                alternatives = [node for node in head.find("link")
                                if "alternate" in node.attrs.get("rel", "").lower().split()
                                and "hreflang" in node.attrs]
                self.assertEqual(len(alternatives), 3, "One uk/en/x-default link each")
                self.assertEqual({node.attrs["hreflang"]: node.attrs.get("href")
                                  for node in alternatives}, language_urls(relative))
                for node in metas:
                    if node.attrs.get("name", "").lower() in {"robots", "googlebot", "bingbot"}:
                        self.assertNotIn("noindex", node.attrs.get("content", "").lower())

    def test_sitemap_covers_all_unique_canonical_urls_without_404_or_aliases(self):
        tree = ET.parse(ROOT / "sitemap.xml")
        self.assertEqual(tree.getroot().tag, SM + "urlset")
        entries = tree.getroot().findall(SM + "url")
        locations = []
        for entry in entries:
            self.assertEqual(len(entry.findall(SM + "loc")), 1)
            locations.append(entry.findtext(SM + "loc"))
        self.assertEqual(len(locations), len(set(locations)), "Canonical URLs must appear once")
        self.assertEqual(set(locations), expected_urls())
        self.assertIn(ORIGIN + "/", locations)
        self.assertIn(ORIGIN + "/en/", locations)
        for relative in ("404.html", *ALIASES):
            self.assertNotIn(ORIGIN + "/" + relative, locations)
        for url in locations:
            parsed = urlsplit(url)
            self.assertEqual((parsed.scheme, parsed.netloc), ("https", "wordandmusic.art"))
            self.assertFalse(parsed.query or parsed.fragment)
        self.assertFalse(list(tree.iter(SM + "lastmod")), "No source-backed modification dates were supplied")

    def test_sitemap_has_reciprocal_uk_en_x_default_links_for_every_url(self):
        entries = ET.parse(ROOT / "sitemap.xml").getroot().findall(SM + "url")
        by_url = {entry.findtext(SM + "loc"): entry for entry in entries}
        for url, entry in by_url.items():
            with self.subTest(url=url):
                relative = url.removeprefix(ORIGIN + "/")
                if not relative or relative == "en/":
                    relative += "index.html"
                wanted = language_urls(relative)
                links = entry.findall(XHTML + "link")
                self.assertEqual(len(links), 3)
                self.assertTrue(all(link.get("rel") == "alternate" for link in links))
                actual = {link.get("hreflang"): link.get("href") for link in links}
                self.assertEqual(actual, wanted)
                for twin in (actual["uk"], actual["en"]):
                    self.assertIn(twin, by_url)
                    reverse = {link.get("hreflang"): link.get("href")
                               for link in by_url[twin].findall(XHTML + "link")}
                    self.assertEqual(reverse, wanted)

    def test_robots_allows_site_and_names_exact_production_sitemap(self):
        lines = [line.split("#", 1)[0].strip() for line in (ROOT / "robots.txt").read_text().splitlines()]
        directives = [line for line in lines if line]
        self.assertIn("User-agent: *", directives)
        self.assertIn("Allow: /", directives)
        self.assertFalse(any(line.lower().startswith("disallow:") and line.split(":", 1)[1].strip()
                             for line in directives))
        sitemaps = [line.split(":", 1)[1].strip() for line in directives if line.lower().startswith("sitemap:")]
        self.assertEqual(sitemaps, [ORIGIN + "/sitemap.xml"])

    def test_generator_check_passes_without_writing_the_published_sitemap(self):
        script = ROOT / "tools/sitemap.py"
        self.assertTrue(script.is_file(), "The generated sitemap needs a repeatable --check gate")
        before = (ROOT / "sitemap.xml").read_bytes()
        result = subprocess.run([sys.executable, str(script), "--check"], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((ROOT / "sitemap.xml").read_bytes(), before, "--check is read-only")

    def test_generator_check_rejects_stale_entries_and_unsupported_canonical_duplicates(self):
        script = ROOT / "tools/sitemap.py"
        self.assertTrue(script.is_file())
        with tempfile.TemporaryDirectory(prefix="wordmusic-sitemap-test-") as folder:
            temporary = Path(folder)
            # Copy only the public sources and scripts; the checker needs no
            # image binaries, browser storage or production access.
            for source in production_pages():
                destination = temporary / source.relative_to(ROOT)
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            shutil.copytree(ROOT / "tools", temporary / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(ROOT / "robots.txt", temporary / "robots.txt")
            original = (ROOT / "sitemap.xml").read_text()
            target = temporary / "sitemap.xml"
            target.write_text(original)
            command = [sys.executable, str(temporary / "tools/sitemap.py"), "--check"]
            fixture_environment = dict(os.environ, SITE_ROOT=str(temporary))
            baseline = subprocess.run(command, cwd=temporary, env=fixture_environment,
                                      capture_output=True, text=True)
            self.assertEqual(baseline.returncode, 0, baseline.stdout + baseline.stderr)
            first = re.search(r"<url(?:\s[^>]*)?>.*?</url>", original, re.S)
            self.assertIsNotNone(first)
            corruptions = {
                "missing": original[:first.start()] + original[first.end():],
                "duplicate": original[:first.end()] + first.group() + original[first.end():],
            }
            for kind, corrupted in corruptions.items():
                with self.subTest(corruption=kind):
                    target.write_text(corrupted)
                    result = subprocess.run(command, cwd=temporary, env=fixture_environment,
                                            capture_output=True, text=True)
                    self.assertNotEqual(result.returncode, 0, "A stale sitemap must fail --check")
                    self.assertEqual(target.read_text(), corrupted, "--check must report, not repair")
            target.write_text(original)
            artist_page = temporary / "artists.html"
            artist_source = artist_page.read_text()
            bad_canonical = re.sub(
                r'(<link\b[^>]*\brel="canonical"[^>]*\bhref=")[^"]+("[^>]*>)',
                rf'\g<1>{ORIGIN}/privacy.html\g<2>', artist_source, count=1)
            self.assertNotEqual(bad_canonical, artist_source)
            artist_page.write_text(bad_canonical)
            result = subprocess.run(command, cwd=temporary, env=fixture_environment,
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0,
                                "Only the two supplied programme aliases may share another page's canonical")
            self.assertEqual(artist_page.read_text(), bad_canonical, "--check must not repair page metadata")


if __name__ == "__main__":
    unittest.main()
