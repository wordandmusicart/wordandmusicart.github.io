#!/usr/bin/env python3
"""Independent structural acceptance for docs/october-rollover.md A1–A7.

CSS geometry, artwork crops and live deployment remain browser gates (A8).
"""
import json
import re
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

if __package__:
    from .test_event_end_date import events, KNOWN_ARCHIVE_RANGES, UNKNOWN_ARCHIVE_STARTS
    from .test_landing_artists import Document, ROOT, ORIGIN, links, public_pages
else:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from test_event_end_date import events, KNOWN_ARCHIVE_RANGES, UNKNOWN_ARCHIVE_STARTS
    from test_landing_artists import Document, ROOT, ORIGIN, links, public_pages

WINGS = "concerts/on-the-wings-of-love.html"
WINGS_OCTOBER_24 = "concerts/on-the-wings-of-love-24102026.html"
VIVRE = "concerts/vivre-aimer-rever.html"
NOVEMBER_22 = "concerts/vivre-aimer-rever-22112026.html"
TICKET = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki"
TICKET_24 = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki-v-budinku-vcenih"
RANGE = re.compile(r"\d{2}:\d{2}\s*[–—-]\s*\d{2}:\d{2}")


def normalized(node):
    return " ".join(node.text().split())


def section(doc, identity):
    return next(n for n in doc.find("section") if n.attrs.get("id") == identity)


def facts(doc):
    hero = next(doc.find("section", "c-hero"))
    block = next(hero.find("dl", "facts"))
    return [(normalized(dt), normalized(dd))
            for dt, dd in zip(block.find("dt"), block.find("dd"))]


class OctoberRolloverAcceptance(unittest.TestCase):
    def test_home_announces_november_22_with_tickets_and_retains_latest_archive(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            doc = Document(ROOT / prefix / "index.html").root
            announced = next(doc.find("aside"))
            self.assertIn('22.11', announced.text())
            self.assertIn('Vivre, Aimer, Rêver', announced.text())
            self.assertIn('https://eventmate.app/events/share/93e50cf4-75cd-4418-b20c-254c7db657b7?locale=' + lang, links(announced))
            self.assertIn('/' + prefix + NOVEMBER_22, links(announced))
            archive = section(doc, 'past-concerts')
            self.assertIn('/' + prefix + WINGS_OCTOBER_24, links(archive))

    def test_current_and_named_routes_show_identical_confirmed_programme(self):
        for prefix in ('', 'en/'):
            current = Document(ROOT / prefix / 'concert.html').root
            named = Document(ROOT / prefix / NOVEMBER_22).root
            self.assertEqual([normalized(n) for n in current.find('h1')], [normalized(n) for n in named.find('h1')])
            self.assertEqual(facts(current), facts(named))
            for identity in ('program', 'artists', 'venue'):
                self.assertEqual(normalized(section(current, identity)), normalized(section(named, identity)))
            for doc in (current, named):
                hero = next(doc.find('section', 'c-hero'))
                self.assertFalse(list(hero.find(cls='poster-placeholder')))
                self.assertEqual(len(list(hero.find('img'))), 1)
                self.assertIn('vivre-aimer-rever-22112026-poster-night.jpg', next(hero.find('img')).attrs['src'])

    def test_vivre_archive_preserves_approved_content_without_ticket_or_sales_markup(self):
        baseline = json.loads((ROOT / "tools/fixtures/october_rollover_content.json").read_text())
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                path = ROOT / prefix / VIVRE
                self.assertTrue(path.is_file(), "The October 3 programme needs its own archive URL")
                doc = Document(path).root
                page = path.read_text()
                self.assertEqual(normalized(next(doc.find("h1"))), "Vivre, Aimer, Rêver…")
                for identity in ("program", "artists", "venue"):
                    self.assertEqual(normalized(section(doc, identity)), baseline[lang][identity])
                hero = next(doc.find("section", "c-hero"))
                self.assertEqual([n.attrs["src"] for n in hero.find("img")], baseline[lang]["hero_images"])
                self.assertEqual([n.attrs["srcset"] for n in hero.find("source")], baseline[lang]["hero_sources"])
                self.assertFalse(events(page))
                self.assertFalse(list(doc.find(cls="status")))
                self.assertFalse(list(doc.find(cls="sticky-buy")))
                # The shared header may sell the next concert; the archive content must not.
                self.assertFalse([href for href in links(next(doc.find("main"))) if urlsplit(href).hostname == "eventmate.app"
                                  and urlsplit(href).path.startswith("/events/")])

    def test_upcoming_and_archive_listing_are_separated(self):
        for prefix in ("", "en/"):
            doc = Document(ROOT / prefix / "concerts.html").root
            upcoming = list(doc.find("article", "upc"))
            self.assertEqual(len(upcoming), 3, 'Upcoming concerts include November 22, November 29, and December 20')
            self.assertIn('/' + prefix + NOVEMBER_22, links(upcoming[0]))
            archive = section(doc, "archive")
            archive_routes = {urlsplit(href).path for href in links(archive)
                              if urlsplit(href).path.startswith("/" + prefix + "concerts/")}
            expected_archive = {"/" + prefix + "concerts/" + slug + ".html"
                                for slug in set(KNOWN_ARCHIVE_RANGES) | UNKNOWN_ARCHIVE_STARTS} | {"/" + prefix + WINGS_OCTOBER_24}
            self.assertEqual(archive_routes, expected_archive,
                             "Adding a future date must preserve the exact archived concert set")
            self.assertIn("/" + prefix + VIVRE, archive_routes)
            self.assertIn("/" + prefix + WINGS, archive_routes)
            self.assertIn("/" + prefix + WINGS_OCTOBER_24, archive_routes)
            self.assertEqual([list(n.find(cls='d'))[0].text().strip() for n in upcoming], ['22.11', '29.11', '20.12'])

    def test_facts_have_one_time_range_and_no_separate_endpoint_cells(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            labels = ("Дата", "Час", "Ціна") if lang == "uk" else ("Date", "Time", "Price")
            for relative in (WINGS_OCTOBER_24,):
                with self.subTest(page=prefix + relative):
                    pairs = facts(Document(ROOT / prefix / relative).root)
                    self.assertEqual([label for label, _ in pairs[:2]], list(labels[:2]))
                    self.assertNotIn(labels[2], [label for label, _ in pairs])
                    self.assertRegex(pairs[1][1], r"^16:00\s*[–—-]\s*17:10$")
                    self.assertFalse(set(label for label, _ in pairs) & {"Початок", "Завершення", "Start", "End"})
            with self.subTest(page=prefix + WINGS):
                pairs = facts(Document(ROOT / prefix / WINGS).root)
                self.assertEqual([label for label, _ in pairs[:3]], list(labels))
                self.assertRegex(pairs[1][1], r"^18:00\s*[–—-]\s*19:30$")
                self.assertFalse(set(label for label, _ in pairs) & {"Початок", "Завершення", "Start", "End"})
            for slug in set(KNOWN_ARCHIVE_RANGES) | UNKNOWN_ARCHIVE_STARTS:
                with self.subTest(page=prefix + slug):
                    path = ROOT / prefix / "concerts" / (slug + ".html")
                    self.assertTrue(path.is_file())
                    pairs = facts(Document(path).root)
                    if slug not in UNKNOWN_ARCHIVE_STARTS:
                        self.assertEqual([label for label, _ in pairs[:2]], list(labels[:2]))
                    self.assertFalse(set(label for label, _ in pairs) & {"Початок", "Завершення", "Start", "End"})

    def test_present_known_times_in_navigation_related_and_metadata_are_ranges(self):
        for path in public_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                doc = Document(path).root
                candidates = list(doc.find(cls="subnav")) + list(doc.find(cls="sticky-buy")) + list(doc.find(cls="related"))
                texts = [n.text() for n in candidates]
                texts += [n.attrs.get("content", "") for n in doc.find("meta")
                          if n.attrs.get("name") == "description" or n.attrs.get("property") == "og:description"]
                for text in texts:
                    without_ranges = RANGE.sub("", text)
                    # November 22 has only a confirmed start; all older supplied
                    # ranges must still retain their confirmed ends.
                    relative = path.relative_to(ROOT).as_posix()
                    if relative in {'concert.html', 'en/concert.html', NOVEMBER_22, 'en/' + NOVEMBER_22}:
                        self.assertNotRegex(without_ranges, r"\b18:00\b")
                    else:
                        self.assertNotRegex(without_ranges, r"\b(?:16|18):00\b",
                                            "A known visible or metadata time must include its supplied end")

    def test_paired_routes_metadata_sitemap_and_artist_sources_follow_rollover(self):
        urls = {n.text for n in ET.parse(ROOT / "sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        for relative in ("concert.html", WINGS, WINGS_OCTOBER_24, VIVRE, NOVEMBER_22):
            for prefix, lang in (("", "uk"), ("en/", "en")):
                with self.subTest(page=prefix + relative):
                    path = ROOT / prefix / relative
                    self.assertTrue(path.is_file())
                    doc = Document(path).root
                    canonical = [n.attrs.get("href") for n in doc.find("link") if n.attrs.get("rel") == "canonical"]
                    canonical_relative = NOVEMBER_22 if relative == "concert.html" else relative
                    self.assertEqual(canonical, [ORIGIN + "/" + prefix + canonical_relative])
                    self.assertIn(canonical[0], urls)
                    alternates = {n.attrs.get("hreflang"): n.attrs.get("href") for n in doc.find("link") if n.attrs.get("rel") == "alternate"}
                    for code, twin in (("uk", ""), ("en", "en/")):
                        self.assertEqual(alternates.get(code), ORIGIN + "/" + twin + canonical_relative)
                    twin = "/" + ("en/" if lang == "uk" else "") + relative
                    self.assertIn(twin, links(next(doc.find(cls="lang"))))
        records = json.loads((ROOT / "assets/artists.json").read_text())
        for identity in ("hennadii-taraniuk", "mariia-popovych", "mykola-chykarenko", "dmytro-terentiev"):
            record = next(r for r in records if r["id"] == identity)
            self.assertIn(VIVRE + "#artists", record["sources"])

    def test_public_pages_share_bumped_css_cache_version(self):
        versions = set()
        for path in public_pages():
            doc = Document(path).root
            css = [n.attrs.get("href", "") for n in doc.find("link")
                   if n.attrs.get("href", "").startswith("/assets/site.css?")]
            self.assertEqual(len(css), 1, str(path.relative_to(ROOT)))
            versions.add(css[0])
        self.assertEqual(len(versions), 1, "UA/EN pages must use the same CSS revision")
        self.assertGreater(int(re.search(r"\?v=(\d+)$", versions.pop()).group(1)), 57)


if __name__ == "__main__":
    unittest.main()
