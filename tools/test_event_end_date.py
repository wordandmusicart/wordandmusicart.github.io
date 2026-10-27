#!/usr/bin/env python3
"""Ticketed upcoming events with source-backed offers, and historical pages."""

import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(os.environ.get("SITE_ROOT", Path(__file__).resolve().parents[1]))
LABELS = {"uk": ("Час", "Дата"), "en": ("Time", "Date")}
# Existing supplied endpoints, rather than a newly inferred duration.
KNOWN_ARCHIVE_RANGES = {
    "autumn-rendezvous": "17:00–18:00",
    "melodies-eternelles": "16:00–17:00",
    "melodies-of-enchanting-june": "15:00–16:00",
    "music-of-soul-and-heart": "15:00–16:00",
    "roads-of-love": "16:00–17:00",
    "soul-wanderings": "16:00–17:00",
    "stabat-mater": "18:00–19:00",
    "winter-extravaganza": "14:00–15:00",
    "vivre-aimer-rever": "16:00–17:00",
    "on-the-wings-of-love": "18:00–19:30",
}
UNKNOWN_ARCHIVE_STARTS = {"amore-eterno", "christmas-kaleidoscope", "heartstrings"}
ANNOUNCED_CONCERTS = {"on-the-wings-of-love-24102026"}
CONCERT_ALIASES = {"on-the-wings-of-love-25102026"}
OCTOBER_24_TICKET = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki-v-budinku-vcenih"


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
    def test_current_alias_preserves_october_24_facts_without_event_offer(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                page = (ROOT / prefix / "concert.html").read_text(encoding="utf-8")
                self.assert_october_24(page, lang)

    def assert_october_24(self, page, lang):
        self.assertFalse(events(page), "Completed concert must not advertise a current event or offer")
        self.assertNotIn("koncert-ziti-kohati-mriati", page)
        hero = re.search(r'<section class="c-hero.*?</section>', page, re.S).group(0)
        time_label, date_label = LABELS[lang]
        self.assertEqual(fact(hero, date_label), "24.10.2026")
        visible_time = fact(hero, time_label)
        self.assertIsNotNone(visible_time, "The facts must show a single Time range")
        self.assertEqual(visible_time.replace(" ", ""), "16:00–17:10")
        self.assertIsNone(fact(hero, "Ціна" if lang == "uk" else "Price"))

    def historical_pages(self):
        ua = sorted((ROOT / "concerts").glob("*.html"))
        en = sorted((ROOT / "en/concerts").glob("*.html"))
        self.assertTrue(ua)
        self.assertEqual([path.name for path in ua], [path.name for path in en])
        self.assertEqual(
            {path.stem for path in ua},
            set(KNOWN_ARCHIVE_RANGES) | UNKNOWN_ARCHIVE_STARTS | ANNOUNCED_CONCERTS | CONCERT_ALIASES,
        )
        return [path for path in ua + en if path.stem not in ANNOUNCED_CONCERTS | CONCERT_ALIASES]

    def test_archived_programme_preserves_source_backed_range_without_offer(self):
        for prefix, lang in (("", "uk"), ("en/", "en")):
            with self.subTest(language=lang):
                page = (ROOT / prefix / "concerts/on-the-wings-of-love-24102026.html").read_text(encoding="utf-8")
                self.assert_october_24(page, lang)

    def test_historical_concerts_have_no_music_event(self):
        for path in self.historical_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                page = path.read_text(encoding="utf-8")
                self.assertFalse(
                    events(page),
                    f"{path.relative_to(ROOT)} must not contain MusicEvent",
                )

    def test_historical_visible_ranges_preserve_supplied_endpoints(self):
        for path in self.historical_pages():
            with self.subTest(page=path.relative_to(ROOT)):
                page = path.read_text(encoding="utf-8")
                hero = re.search(r'<section class="c-hero.*?</section>', page, re.S)
                self.assertIsNotNone(hero)
                lang = "en" if "en" in path.relative_to(ROOT).parts else "uk"
                time_label, _ = LABELS[lang]
                visible_range = fact(hero.group(0), time_label)
                expected_range = KNOWN_ARCHIVE_RANGES.get(path.stem)
                self.assertEqual(visible_range.replace(" ", "") if visible_range else None,
                                 expected_range, "Unknown start must have no invented range")
                for label in ("Початок", "Завершення", "Start", "End"):
                    self.assertIsNone(fact(hero.group(0), label), "Time replaces separate endpoints")


if __name__ == "__main__":
    unittest.main()
