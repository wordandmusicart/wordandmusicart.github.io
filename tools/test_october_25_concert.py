#!/usr/bin/env python3
"""Owner acceptance contract for On the Wings of Love, 25 October 2026.

Facts: docs/on-the-wings-of-love-25102026-source.md. Visual theme/responsive acceptance is a
separate browser gate; this suite checks public content and navigation.
"""
import unittest
import xml.etree.ElementTree as ET
from datetime import datetime
from urllib.parse import parse_qs, urlsplit
from zoneinfo import ZoneInfo

if __package__:
    from .test_event_end_date import events
    from .test_landing_artists import Document, ROOT, ORIGIN, links
else:
    from test_event_end_date import events
    from test_landing_artists import Document, ROOT, ORIGIN, links

SLUG = "concerts/on-the-wings-of-love-25102026.html"
REFERENCE = "concerts/on-the-wings-of-love.html"
TICKET = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki"
LANGUAGES = (("", "uk", "На крилах кохання", "Будинок вчених · Біла вітальня", "Скоро у продажу"),
             ("en/", "en", "On the Wings of Love", "House of Scientists · White Salon", "Coming soon"))


def section(doc, identity):
    return next(n for n in doc.find("section") if n.attrs.get("id") == identity)


def text(node):
    return " ".join(node.text().split())


def tree(node):
    """Semantic/crop equality includes all approved performer markup."""
    if isinstance(node, str):
        return " ".join(node.split())
    return (node.tag, tuple(sorted(node.attrs.items())),
            tuple(tree(child) for child in node.children if not isinstance(child, str) or child.strip()))


def ticket_links(node):
    return [href for href in links(node) if urlsplit(href).hostname == "eventmate.app"]


def contains_offer(value):
    if isinstance(value, dict):
        kind = value.get("@type", [])
        if "offers" in value or "Offer" in (kind if isinstance(kind, list) else [kind]):
            return True
        return any(contains_offer(child) for child in value.values())
    if isinstance(value, list):
        return any(contains_offer(child) for child in value)
    return False


class October25ConcertAcceptance(unittest.TestCase):
    def test_language_metadata_routes_and_sitemap(self):
        urls = {n.text for n in ET.parse(ROOT / "sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        for prefix, lang, title, venue, _ in LANGUAGES:
            with self.subTest(language=lang):
                path = ROOT / prefix / SLUG
                self.assertTrue(path.is_file(), f"Missing {prefix}{SLUG}")
                doc = Document(path).root
                self.assertEqual(next(doc.find("html")).attrs.get("lang"), lang)
                self.assertEqual(text(next(doc.find("h1"))), title)
                page_title = text(next(doc.find("title")))
                self.assertIn(title, page_title)
                self.assertIn("2026", page_title)
                metadata = {n.attrs.get("name", n.attrs.get("property")): n.attrs.get("content") for n in doc.find("meta")}
                self.assertEqual(metadata.get("og:title"), page_title)
                self.assertEqual(metadata.get("og:url"), f"{ORIGIN}/{prefix}{SLUG}")
                self.assertEqual(metadata.get("og:description"), metadata.get("description"))
                self.assertIn(venue, metadata.get("description", ""))
                self.assertIn("18:00–19:30", metadata.get("description", ""))
                self.assertEqual(metadata.get("og:image"), f"{ORIGIN}/assets/img/og-image.jpg")
                canonicals = [n.attrs.get("href") for n in doc.find("link") if n.attrs.get("rel") == "canonical"]
                self.assertEqual(canonicals, [f"{ORIGIN}/{prefix}{SLUG}"])
                self.assertIn(canonicals[0], urls)
                alternates = {n.attrs.get("hreflang"): n.attrs.get("href") for n in doc.find("link") if n.attrs.get("rel") == "alternate"}
                self.assertEqual(alternates.get("uk"), f"{ORIGIN}/{SLUG}")
                self.assertEqual(alternates.get("en"), f"{ORIGIN}/en/{SLUG}")
                twin = f"/{'en/' if lang == 'uk' else ''}{SLUG}"
                for control in doc.find(cls="lang"):
                    self.assertIn(twin, links(control))
                ids = {n.attrs.get("id") for n in doc.find()}
                for href in links(doc):
                    if href.startswith("#"):
                        self.assertIn(href[1:], ids)

    def test_facts_venue_address_and_maps_are_for_the_new_event(self):
        for prefix, lang, _, venue, _ in LANGUAGES:
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / SLUG).root
                hero = next(doc.find("section", cls="c-hero"))
                facts = next(hero.find("dl", cls="facts"))
                labels = [text(n) for n in facts.find("dt")]
                values = [text(n) for n in facts.find("dd")]
                expected_labels = ["Дата", "Час", "Ціна", "Локація", "Адреса"] if lang == "uk" else ["Date", "Time", "Price", "Location", "Address"]
                self.assertEqual(labels, expected_labels)
                self.assertEqual(values[:4], ["25.10.2026", "18:00–19:30", "300 грн" if lang == "uk" else "UAH 300", venue])
                address = "вул. Володимирська, 45А" if lang == "uk" else "45A Volodymyrska St"
                self.assertIn(address, values[4])
                block = section(doc, "venue")
                self.assertEqual(text(next(block.find("h3"))), venue)
                self.assertIn(address, text(block))
                self.assertIn("https://kbvnanu.kiev.ua/", links(block))
                map_urls = [href for href in links(hero) + links(block) if "google.com/maps" in href]
                iframe = list(block.find("iframe"))
                self.assertEqual(len(iframe), 1)
                map_urls.append(iframe[0].attrs["src"])
                self.assertGreaterEqual(len(map_urls), 3)
                for href in map_urls:
                    query = parse_qs(urlsplit(href).query)
                    query_text = " ".join(query.get("query", query.get("q", [])))
                    self.assertIn("Володимирська", query_text)
                    self.assertIn("45А", query_text)
                self.assertEqual(iframe[0].attrs.get("loading"), "lazy")
                self.assertTrue(iframe[0].attrs.get("title"))
                self.assertIn("allowfullscreen", iframe[0].attrs)
                self.assertIn("#venue", links(next(doc.find("nav", cls="subnav"))))

    def test_programme_performers_roles_and_crops_match_october_15(self):
        for prefix, lang, *_ in LANGUAGES:
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / SLUG).root
                reference = Document(ROOT / prefix / REFERENCE).root
                self.assertEqual(tree(section(doc, "program")), tree(section(reference, "program")))
                self.assertEqual(tree(section(doc, "artists")), tree(section(reference, "artists")))
                self.assertEqual(len(list(section(doc, "artists").find("h3"))), 13)
                new_event = events((ROOT / prefix / SLUG).read_text())[0]
                old_event = events((ROOT / prefix / REFERENCE).read_text())[0]
                self.assertEqual(new_event["performer"], old_event["performer"])

    def test_music_event_has_kyiv_dates_and_no_ticket_offer(self):
        for prefix, lang, title, venue, _ in LANGUAGES:
            with self.subTest(language=lang):
                found = events((ROOT / prefix / SLUG).read_text())
                self.assertEqual(len(found), 1)
                event = found[0]
                self.assertEqual(event["name"], title)
                self.assertEqual(event["url"], f"{ORIGIN}/{prefix}{SLUG}")
                self.assertEqual(event["inLanguage"], lang)
                self.assertEqual(event["eventStatus"], "https://schema.org/EventScheduled")
                self.assertEqual(event["eventAttendanceMode"], "https://schema.org/OfflineEventAttendanceMode")
                for key, hour, minute in (("startDate", 18, 0), ("endDate", 19, 30)):
                    expected = datetime(2026, 10, 25, hour, minute, tzinfo=ZoneInfo("Europe/Kyiv"))
                    self.assertEqual(expected.strftime("%z"), "+0200", "Kyiv has changed to winter time before this event")
                    self.assertEqual(event[key], expected.isoformat())
                self.assertEqual(event["location"]["name"], venue)
                self.assertEqual(event["location"]["address"]["streetAddress"], "вул. Володимирська, 45А" if lang == "uk" else "45A Volodymyrska St")
                self.assertEqual(event["location"]["address"]["addressCountry"], "UA")
                self.assertFalse(contains_offer(event), "Sales are not confirmed for this concert")
                self.assertEqual(event["image"], [f"{ORIGIN}/assets/img/og-image.jpg"])

    def test_pending_placeholder_no_old_copy_and_header_keeps_nearest_tickets(self):
        stale = ("15.10", "15 October", "15 жовтня", "Біла вітальна", "Будинок актора", "Actor’s House", "actorhall", "Ярославів", "Yaroslaviv", "on-the-wings-of-love-poster")
        for prefix, lang, _, _, pending in LANGUAGES:
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / SLUG).root
                main = next(doc.find("main"))
                self.assertFalse(ticket_links(main), "No event-specific sales CTA is permitted in main")
                self.assertFalse(list(main.find(cls="sticky-buy")))
                for old in stale:
                    self.assertNotIn(old, text(main))
                    for node in main.find():
                        self.assertFalse(any(old in str(value) for value in node.attrs.values()), old)
                statuses = list(main.find(cls="status-pending"))
                self.assertGreaterEqual(len(statuses), 1)
                self.assertTrue(all(text(node) == pending for node in statuses))
                poster = list(next(doc.find("section", cls="c-hero")).find(cls="poster-placeholder"))
                self.assertEqual(len(poster), 1)
                self.assertEqual(poster[0].attrs.get("role"), "img")
                self.assertTrue(poster[0].attrs.get("aria-label"))
                self.assertFalse(list(poster[0].find("img")) + list(poster[0].find("picture")))
                header = next(n for n in doc.find("header") if list(n.find("nav")))
                self.assertEqual(ticket_links(header), [f"{TICKET}?locale={lang}"] * 2)

    def test_listing_has_two_ordered_cards_with_pending_sales_and_nearest_unchanged(self):
        for prefix, lang, title, venue, pending in LANGUAGES:
            with self.subTest(language=lang):
                listing = Document(ROOT / prefix / "concerts.html").root
                upcoming = next(n for n in listing.find("section") if n.attrs.get("data-sec") == "up")
                cards = list(upcoming.find("article", cls="upc"))
                self.assertEqual(len(cards), 2)
                self.assertIn(f"/{prefix}{REFERENCE}", links(cards[0]))
                self.assertIn(f"{TICKET}?locale={lang}", links(cards[0]))
                new = cards[1]
                self.assertIn(f"/{prefix}{SLUG}", links(new))
                self.assertIn(title, text(new))
                self.assertIn(venue, text(new))
                self.assertIn("25.10", text(new))
                self.assertIn("18:00–19:30", text(new))
                self.assertIn("Нд" if lang == "uk" else "Sun", text(new))
                self.assertIn("2 концерти" if lang == "uk" else "2 concerts", text(upcoming))
                self.assertEqual([text(n) for n in new.find(cls="status-pending")], [pending])
                self.assertFalse(ticket_links(new))
                self.assertEqual(len(list(new.find(cls="poster-placeholder"))), 1)
                self.assertFalse(list(new.find("img")))
                for anchor in new.find("a"):
                    self.assertFalse(list(anchor.find("a")))
                nearest = events((ROOT / prefix / "concert.html").read_text())[0]
                self.assertEqual(nearest["startDate"], "2026-10-15T18:00:00+03:00")
                self.assertEqual(nearest["offers"]["url"], f"{TICKET}?locale={lang}")
                home = Document(ROOT / prefix / "index.html").root
                self.assertNotIn(f"/{prefix}{SLUG}", links(home))
                intro = next(n for n in home.find() if n.attrs.get("id") == "intro")
                self.assertIn(f"/{prefix}concert.html", links(intro))
                self.assertIn(f"{TICKET}?locale={lang}", ticket_links(intro))


if __name__ == "__main__":
    unittest.main()
