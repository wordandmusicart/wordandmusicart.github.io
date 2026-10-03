#!/usr/bin/env python3
"""Acceptance test for random 3 past concerts on the homepage."""
import os
import re
import unittest
from pathlib import Path

from test_landing_artists import Document, ROOT

class HomeArchiveRandomTest(unittest.TestCase):
    def test_static_markup_has_exactly_three_cards(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / "index.html").root
                archive = next(s for s in doc.find("section") if s.attrs.get("id") == "past-concerts")
                cards_container = next(c for c in archive.find("div", "cards3"))
                cards = list(cards_container.find("article", "card"))
                self.assertEqual(len(cards), 3, f"Expected exactly 3 cards in static HTML, got {len(cards)}")
                for card in cards:
                    links = [a.attrs.get("href", "") for a in card.find("a") if a.attrs.get("href")]
                    self.assertTrue(len(links) >= 1)
                    for href in links:
                        # Ensure link points to valid concert page
                        target = ROOT / href.lstrip("/")
                        self.assertTrue(target.is_file(), f"Concert link {href} not found on disk: {target}")

    def test_home_archive_script_included_on_both_homepages(self):
        for prefix in ("", "en/"):
            html = (ROOT / prefix / "index.html").read_text(encoding="utf-8")
            self.assertIn('<script src="/assets/home-archive.js?v=1" defer></script>', html)

    def test_archive_pool_slugs_exist_on_disk(self):
        js = (ROOT / "assets/home-archive.js").read_text(encoding="utf-8")
        slugs = re.findall(r"slug:\s*'([^']+)'", js)
        self.assertGreaterEqual(len(slugs), 10, "Expected at least 10 concerts in the archive pool")
        self.assertEqual(len(slugs), len(set(slugs)), "Slugs must be unique")
        for slug in slugs:
            ua_file = ROOT / "concerts" / f"{slug}.html"
            en_file = ROOT / "en/concerts" / f"{slug}.html"
            self.assertTrue(ua_file.is_file(), f"Missing UA concert page for slug: {slug}")
            self.assertTrue(en_file.is_file(), f"Missing EN concert page for slug: {slug}")


if __name__ == "__main__":
    unittest.main()
