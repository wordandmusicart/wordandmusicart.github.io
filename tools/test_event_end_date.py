#!/usr/bin/env python3
"""Ticketed current event, announced event without Offer, and historical pages."""

import html
import json
import os
import re
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo


ROOT = Path(os.environ.get("SITE_ROOT", Path(__file__).resolve().parents[1]))
KYIV = ZoneInfo("Europe/Kyiv")
LABELS = {"uk": ("Початок", "Дата", "Завершення"), "en": ("Start", "Date", "End")}
KNOWN_ARCHIVE_STARTS = {
    "autumn-rendezvous": "17:00",
    "melodies-eternelles": "16:00",
    "melodies-of-enchanting-june": "15:00",
    "music-of-soul-and-heart": "15:00",
    "roads-of-love": "16:00",
    "soul-wanderings": "16:00",
    "stabat-mater": "18:00",
    "winter-extravaganza": "14:00",
}
UNKNOWN_ARCHIVE_STARTS = {"amore-eterno", "christmas-kaleidoscope", "heartstrings"}
ANNOUNCED_CONCERTS = {"on-the-wings-of-love"}


def fact(hero, label):
    match = re.search(
        rf'<dt class="meta muted">{label}</dt><dd[^>]*>(.*?)</dd>', hero, re.S
    )
    return re.sub(r"<[^>]+>", "", match.group(1)).strip() if match else None


def music_events(value):
    if isinstance(value, list):
        for item in value:
            yield from music_events(item)
    elif isinstance(value, dict):
        types = value.get("@type", [])
        if "MusicEvent" in (types if isinstance(types, list) else [types]):
            yield value
        for nested in value.values():
            yield from music_events(nested)


def events(page):
    scripts = re.findall(
        r"""<script\b(?=[^>]*\btype\s*=\s*["']application/ld\+json["'])[^>]*>(.*?)</script\s*>""",
        page,
        re.S | re.I,
    )
    return [event for source in scripts for event in music_events(json.loads(source))]


class EventSchemaTest(unittest.TestCase):
    def test_current_concert_has_one_hour_end_and_ticket_offer(self):
        for relative, lang in (("concert.html", "uk"), ("en/concert.html", "en")):
            with self.subTest(page=relative):
                page = (ROOT / relative).read_text(encoding="utf-8")
                hero = re.search(r'<section class="c-hero.*?</section>', page, re.S)
                self.assertIsNotNone(hero)
                hero = hero.group(0)
                found = events(page)
                self.assertEqual(len(found), 1)
                event = found[0]

                start_label, date_label, end_label = LABELS[lang]
                year = re.search(r'<div class="meta muted">[^<]*?(\d{4})</div>', hero)
                self.assertIsNotNone(year)
                day, month = map(int, fact(hero, date_label).split("."))
                hour, minute = map(int, fact(hero, start_label).split(":"))
                start = datetime(int(year.group(1)), month, day, hour, minute, tzinfo=KYIV)
                self.assertEqual(event["startDate"], start.isoformat())
                self.assertEqual(event.get("endDate"), (start + timedelta(hours=1)).isoformat())
                self.assertEqual(fact(hero, end_label), (start + timedelta(hours=1)).strftime("%H:%M"))

                ticket = re.search(
                    r'<div class="c-cta"[^>]*><a class="btn" href="([^"]+)"', hero
                )
                self.assertIsNotNone(ticket)
                offer = event.get("offers")
                self.assertIsInstance(offer, dict)
                self.assertEqual(offer.get("@type"), "Offer")
                self.assertEqual(offer.get("url"), html.unescape(ticket.group(1)))
                self.assertTrue(offer["url"].startswith("https://"))
                price_label = "Ціна" if lang == "uk" else "Price"
                self.assertEqual(offer.get("price"), re.search(r"\d+", fact(hero, price_label)).group())
                self.assertEqual(offer.get("priceCurrency"), "UAH")
                status = re.search(
                    r'class="status meta" data-sales-start="([\d-]+)"><i></i>([^<]+)<', page
                )
                self.assertIsNotNone(status)
                self.assertEqual(status.group(2), "Продаж триває" if lang == "uk" else "On sale")
                self.assertEqual(offer.get("availability"), "https://schema.org/InStock")
                self.assertEqual(
                    offer.get("validFrom"),
                    datetime.fromisoformat(status.group(1)).replace(tzinfo=KYIV).isoformat(),
                )

    def historical_pages(self):
        ua = sorted((ROOT / "concerts").glob("*.html"))
        en = sorted((ROOT / "en/concerts").glob("*.html"))
        self.assertTrue(ua)
        self.assertEqual([path.name for path in ua], [path.name for path in en])
        self.assertEqual(
            {path.stem for path in ua},
            set(KNOWN_ARCHIVE_STARTS) | UNKNOWN_ARCHIVE_STARTS | ANNOUNCED_CONCERTS,
        )
        return [path for path in ua + en if path.stem not in ANNOUNCED_CONCERTS]

    def test_announced_concert_has_truthful_event_without_offer(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                page = (ROOT / prefix / "concerts/on-the-wings-of-love.html").read_text(encoding="utf-8")
                found = events(page)
                self.assertEqual(len(found), 1)
                event = found[0]
                self.assertEqual(event["startDate"], "2026-10-15T18:00:00+03:00")
                self.assertEqual(event["endDate"], "2026-10-15T19:00:00+03:00")
                self.assertEqual(event["eventStatus"], "https://schema.org/EventScheduled")
                self.assertEqual(event["inLanguage"], lang)
                self.assertNotIn("offers", event)
                self.assertEqual(len(event["performer"]), 13)
                self.assertEqual(len({p["name"] for p in event["performer"]}), 13)
                self.assertNotIn("eventmate.app", page)
                self.assertNotIn("03.10", page)
                hero = re.search(r'<section class="c-hero.*?</section>', page, re.S).group(0)
                start_label, date_label, end_label = LABELS[lang]
                self.assertEqual(fact(hero, date_label), "15.10")
                self.assertEqual(fact(hero, start_label), "18:00")
                self.assertEqual(fact(hero, end_label), "19:00")
                self.assertIsNone(fact(hero, "Ціна" if lang == "uk" else "Price"))

    def test_historical_concerts_have_no_music_event(self):
        for path in self.historical_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                page = path.read_text(encoding="utf-8")
                self.assertFalse(
                    events(page),
                    f"{path.relative_to(ROOT)} must not contain MusicEvent",
                )

    def test_historical_visible_end_is_one_hour_after_start(self):
        for path in self.historical_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                page = path.read_text(encoding="utf-8")
                hero = re.search(r'<section class="c-hero.*?</section>', page, re.S)
                self.assertIsNotNone(hero)
                lang = "en" if "en" in path.relative_to(ROOT).parts else "uk"
                start_label, _, end_label = LABELS[lang]
                visible_start = fact(hero.group(0), start_label)
                visible_end = fact(hero.group(0), end_label)
                expected_start = KNOWN_ARCHIVE_STARTS.get(path.stem)
                self.assertEqual(visible_start, expected_start)
                if expected_start is None:
                    self.assertIsNone(visible_end, "Unknown start must have no invented end")
                else:
                    hour, minute = map(int, expected_start.split(":"))
                    expected_end = (
                        datetime(2000, 1, 1, hour, minute) + timedelta(hours=1)
                    ).strftime("%H:%M")
                    self.assertEqual(visible_end, expected_end)


if __name__ == "__main__":
    unittest.main()
