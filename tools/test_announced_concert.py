#!/usr/bin/env python3
"""Independent acceptance checks for the 15 October announcement (stdlib only)."""
import unittest
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit

if __package__:
    from .test_event_end_date import events
    from .test_landing_artists import Document, ROOT, ORIGIN, links, public_pages
else:
    from test_event_end_date import events
    from test_landing_artists import Document, ROOT, ORIGIN, links, public_pages

SLUG = "concerts/on-the-wings-of-love.html"
TICKET = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki"
NAMES = {
    "uk": ["Анжеліна Швачка", "Лілія Гревцова", "Максим Гара", "Дарія Погоріла",
           "Олександр Пономаренко", "Анастасія Довбіус", "Ірина Шелест", "Юлія Павловська",
           "Каріна Лисак", "Лідія Глінська", "Олексій Мальований", "Наталія Шмельова", "Геннадій Таранюк"],
    "en": ["Anzhelina Shvachka", "Liliia Hrevtsova", "Maksym Hara", "Dariia Pohorila",
           "Oleksandr Ponomarenko", "Anastasiia Dovbius", "Iryna Shelest", "Yuliia Pavlovska",
           "Karina Lysak", "Lidiia Hlinska", "Oleksii Maliovanyi", "Nataliia Shmelova", "Hennadii Taraniuk"],
}
COMPOSERS = ["Wolfgang Amadeus Mozart", "Robert Schumann", "Gaetano Donizetti", "Georges Bizet",
             "Jacques Offenbach", "Henri Duparc", "Vincenzo Di Chiara", "Claude Debussy", "Francesco Cilea", "George Gershwin"]
COMPOSERS_UK = ["Вольфганга Амадея Моцарта", "Роберта Шумана", "Гаетано Доніцетті", "Жоржа Бізе",
                "Жака Оффенбаха", "Анрі Дюпарка", "Вінченцо ді К’яри", "Клода Дебюссі", "Франческо Чілеа", "Джорджа Гершвіна"]


class AnnouncedConcertAcceptance(unittest.TestCase):
    def test_confirmed_ticket_access_and_sales_status_on_detail_and_listing(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                expected = f"{TICKET}?locale={lang}"
                doc = Document(ROOT / prefix / SLUG).root
                ticket_links = [href for href in links(doc) if urlsplit(href).hostname == "eventmate.app"]
                self.assertTrue(ticket_links)
                self.assertEqual(set(ticket_links), {expected, f"{TICKET}?locale=en"})
                header = next(n for n in doc.find("header") if list(n.find("nav")))
                header_tickets = [href for href in links(header) if urlsplit(href).hostname == "eventmate.app"]
                self.assertEqual(len(header_tickets), 2)
                self.assertEqual(set(header_tickets), {f"{TICKET}?locale=en"})
                hero = next(doc.find("section", cls="c-hero"))
                cta = next(hero.find(cls="c-cta"))
                self.assertIn(expected, links(cta))
                self.assertIn("#program", links(cta))
                self.assertIn(expected, links(next(doc.find("nav", cls="subnav"))))
                status = next(doc.find(cls="status"), None)
                self.assertIsNotNone(status)
                self.assertEqual(status.text().strip(), "Продаж триває" if lang == "uk" else "On sale")
                self.assertFalse(status.attrs.get("data-sales-start"), "No sales opening date was provided")
                listing = Document(ROOT / prefix / "concerts.html").root
                card = next(n for n in listing.find("article", cls="upc") if "/" + prefix + SLUG in links(n))
                self.assertIn(expected, links(card))
                self.assertEqual(next(card.find(cls="status")).text().strip(), "Продаж триває" if lang == "uk" else "On sale")
                self.assertIn("/" + prefix + SLUG, links(card))

    def test_paired_metadata_assets_and_language_controls(self):
        urls = {n.text for n in ET.parse(ROOT / "sitemap.xml").iter("{http://www.sitemaps.org/schemas/sitemap/0.9}loc")}
        for prefix, lang, twin in (("", "uk", "/en/" + SLUG), ("en/", "en", "/" + SLUG)):
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / SLUG).root
                self.assertEqual(next(doc.find("html")).attrs["lang"], lang)
                self.assertTrue(next(doc.find("title")).text().strip())
                metadata = list(doc.find("link"))
                canonical = [n.attrs.get("href") for n in metadata if n.attrs.get("rel") == "canonical"]
                self.assertEqual(canonical, [ORIGIN + "/" + prefix + SLUG])
                self.assertIn(canonical[0], urls)
                alternates = {n.attrs.get("hreflang"): n.attrs.get("href") for n in metadata if n.attrs.get("rel") == "alternate"}
                self.assertEqual(alternates.get("uk"), ORIGIN + "/" + SLUG)
                self.assertEqual(alternates.get("en"), ORIGIN + "/en/" + SLUG)
                meta = {n.attrs.get("name", n.attrs.get("property")): n.attrs.get("content") for n in doc.find("meta")}
                self.assertTrue(meta.get("description"))
                self.assertEqual(meta.get("og:url"), canonical[0])
                self.assertEqual(meta.get("og:description"), meta["description"])
                self.assertIn(twin, links(next(doc.find(cls="lang"))))
                self.assertTrue(any(n.attrs.get("href", "").startswith("/assets/site.css?") for n in metadata))
                script_paths = [n.attrs.get("src", "").split("?")[0] for n in doc.find("script")]
                for script in ("/assets/lang.js", "/assets/theme.js", "/assets/header.js"):
                    self.assertIn(script, script_paths)
                ids = {n.attrs.get("id") for n in doc.find()}
                for href in links(doc):
                    if href.startswith("#"):
                        self.assertIn(href[1:], ids)

    def test_complete_visible_and_structured_performers_with_roles(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                path = ROOT / prefix / SLUG
                doc = Document(path).root
                people = next(n for n in doc.find("section") if n.attrs.get("id") == "artists")
                self.assertEqual([n.text().strip() for n in people.find("h3")], NAMES[lang])
                principals = list(people.find(cls="people-wings"))
                self.assertEqual(len(principals), 1)
                self.assertEqual([n.text().strip() for n in principals[0].find("h3")], NAMES[lang][:3])
                supporting = list(people.find(cls="people-students"))
                self.assertEqual(len(supporting), 1)
                self.assertEqual([n.text().strip() for n in supporting[0].find("h3")], NAMES[lang][3:11])
                secondary = list(people.find(cls="people-wings-secondary"))
                self.assertEqual(len(secondary), 1)
                self.assertEqual([n.text().strip() for n in secondary[0].find("h3")], NAMES[lang][11:])
                self.assertEqual(list(people.find(cls="people")), [principals[0], supporting[0], secondary[0]],
                                 "The centered accompanist/host pair must follow the supporting circles")
                self.assertFalse(list(people.find(cls="people-host")), "The host now belongs beside the accompanist")
                self.assertEqual([p["name"] for p in events(path.read_text())[0]["performer"]], NAMES[lang])
                roles = [n.text().strip() for n in people.find("p")]
                vocal_words = ("сопрано", "баритон", "тенор") if lang == "uk" else ("soprano", "baritone", "tenor")
                self.assertEqual(sum(any(word in role for word in vocal_words) for role in roles), 11)
                self.assertEqual(roles[11], "Концертмейстер" if lang == "uk" else "Accompanist")
                self.assertEqual(roles[12], "Художнє слово та ведучий" if lang == "uk" else "Spoken word and host")
                img_sources = [img.attrs.get("src") for img in people.find("img")]
                self.assertIn("/assets/img/iryna-shelest.jpg", img_sources)
                self.assertIn("/assets/img/yuliia-pavlovska.jpg", img_sources)

    def test_venue_section_facts_and_subnav_link(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                doc = Document(ROOT / prefix / SLUG).root
                subnav = next(doc.find("nav", cls="subnav"))
                self.assertIn("#venue", links(subnav))
                hero = next(doc.find("section", cls="c-hero"))
                plc_links = [a.attrs.get("href") for a in hero.find("a", cls="plc")]
                self.assertIn("https://www.actorhall.com/", plc_links)
                self.assertTrue(any("google.com/maps" in href for href in plc_links))
                venues = [n for n in doc.find("section", cls="venue") if n.attrs.get("id") == "venue"]
                self.assertEqual(len(venues), 1)
                venue = venues[0]
                expected_venue_name = "Будинок актора" if lang == "uk" else "Actor’s House"
                h3 = next(venue.find("h3"))
                self.assertEqual(h3.text().strip(), expected_venue_name)
                h3_a = next(h3.find("a", cls="plc"))
                self.assertEqual(h3_a.attrs.get("href"), "https://www.actorhall.com/")
                map_link = next(a for a in venue.find("a", cls="lnk"))
                self.assertIn("google.com/maps", map_link.attrs.get("href", ""))
                iframe = next(venue.find("iframe"))
                self.assertIn("maps.google.com/maps", iframe.attrs.get("src", ""))
                self.assertEqual(iframe.attrs.get("loading"), "lazy")
                self.assertIn("allowfullscreen", iframe.attrs)

    def test_programme_has_full_composer_names_and_no_invented_work_list(self):
        for prefix in ("", "en/"):
            doc = Document(ROOT / prefix / SLUG).root
            program = next(n for n in doc.find("section") if n.attrs.get("id") == "program")
            self.assertEqual(len(list(program.find("p"))), 1)
            self.assertFalse(list(program.find("ol")) + list(program.find("table")))
            self.assertNotIn("Curtis", program.text())
            self.assertNotIn("Куртіс", program.text())
            for composer in COMPOSERS if prefix else COMPOSERS_UK:
                self.assertIn(composer, program.text())

    def test_all_announcement_cards_link_detail_without_nested_anchors(self):
        for path in public_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                doc = Document(path).root
                for anchor in doc.find("a"):
                    self.assertFalse(list(anchor.find("a")), "Nested links break the concert card")
                for card in list(doc.find("article", "upc")) + list(doc.find(cls="related")):
                    title = "On the Wings of Love" if path.relative_to(ROOT).parts[0] == "en" else "На крилах кохання"
                    if title in card.text():
                        prefix = "en/" if path.relative_to(ROOT).parts[0] == "en" else ""
                        self.assertIn("/" + prefix + SLUG, links(card))


if __name__ == "__main__":
    unittest.main()
