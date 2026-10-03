#!/usr/bin/env python3
"""Source-backed visible ticket ranges yield the lowest Google Event offer price."""

import html
import json
import re
import unittest
from pathlib import Path

from structured_data import event


ROOT = Path(__file__).resolve().parents[1]
TICKET = "https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki"


def fixture(price, lang="uk", on_sale=True):
    """Minimal event page: inputs are public facts, not parser implementation."""
    labels = (
        ("Дата", "Початок", "Ціна", "Продаж триває")
        if lang == "uk"
        else ("Date", "Start", "Price", "On sale")
    )
    date, start, price_label, status = labels
    price_fact = (
        f'<div><dt class="meta muted">{price_label}</dt><dd>{html.escape(price)}</dd></div>'
        if price is not None else ""
    )
    sale_status = f'<span class="status meta"><i></i>{status}</span>' if on_sale else ""
    return f'''<html lang="{lang}"><body>{sale_status}
<section class="c-hero wrap g12"><div class="meta muted">15 October 2026</div>
<h1>Ticketed concert</h1><dl class="facts">
<div><dt class="meta muted">{date}</dt><dd>15.10</dd></div>
<div><dt class="meta muted">{start}</dt><dd>18:00</dd></div>{price_fact}</dl>
<div class="c-cta"><a class="btn" href="{TICKET}?locale={lang}">Tickets</a></div>
</section></body></html>'''


class TicketPriceRangeTest(unittest.TestCase):
    def offer(self, price, lang="uk", on_sale=True):
        generated = event(fixture(price, lang, on_sale), lang, "https://wordandmusic.art/concert.html")
        self.assertEqual(len(generated), 1)
        self.assertEqual(generated[0]["@type"], "MusicEvent")
        return generated[0]["offers"]

    def test_closed_ranges_use_lowest_numeric_price_and_keep_ticket_context(self):
        examples = (
            ("uk", "250–400 грн"),
            ("uk", "250-400 грн"),
            ("uk", "250 – 400 грн"),
            ("uk", "250–400 ₴"),
            ("uk", "₴250–400"),
            ("en", "250–400 UAH"),
            ("en", "250-400 UAH"),
            ("en", "250 – 400 UAH"),
        )
        for lang, visible in examples:
            with self.subTest(language=lang, visible=visible):
                offer = self.offer(visible, lang)
                self.assertEqual(offer.get("price"), "250")
                self.assertEqual(offer.get("priceCurrency"), "UAH")
                self.assertEqual(offer.get("@type"), "Offer")
                self.assertEqual(offer.get("url"), f"{TICKET}?locale={lang}")
                self.assertEqual(offer.get("availability"), "https://schema.org/InStock")
                self.assertNotIn("validFrom", offer, "No sales opening date was supplied")
                self.assertNotIn("lowPrice", offer)
                self.assertNotIn("highPrice", offer)

    def test_existing_single_prices_remain_unchanged(self):
        for lang in ("uk", "en"):
            for visible in ("450 грн", "450₴", "₴450", "₴ 450"):
                with self.subTest(language=lang, visible=visible):
                    offer = self.offer(visible, lang)
                    self.assertEqual(offer.get("price"), "450")
                    self.assertEqual(offer.get("priceCurrency"), "UAH")

    def test_missing_or_malformed_prices_have_no_fabricated_price(self):
        examples = (
            None, "", "Ціну уточнюють", "250– грн", "–400 грн", "250–400", 
            "400–250 грн", "250–400–500 грн", "250–four hundred грн",
            "250–400 EUR", "250–400 грн + комісія", "250–400 грн приблизно",
        )
        for visible in examples:
            with self.subTest(visible=visible):
                offer = self.offer(visible)
                for field in ("price", "priceCurrency", "lowPrice", "highPrice", "priceSpecification"):
                    self.assertNotIn(field, offer)
                self.assertEqual(offer.get("url"), f"{TICKET}?locale=uk")

    def test_price_does_not_invent_availability(self):
        offer = self.offer("250–400 грн", on_sale=False)
        self.assertEqual(offer.get("price"), "250")
        self.assertNotIn("availability", offer)

    def test_published_october_15_facts_and_json_ld_agree_in_both_languages(self):
        for prefix, lang, label, visible in (
            ("", "uk", "Ціна", "250–400 грн"),
            ("en/", "en", "Price", "250–400 UAH"),
        ):
            with self.subTest(language=lang):
                page = (ROOT / prefix / "concerts/on-the-wings-of-love.html").read_text(encoding="utf-8")
                hero = re.search(r'<section class="c-hero.*?</section>', page, re.S).group(0)
                fact = re.search(rf'<dt class="meta muted">{label}</dt><dd[^>]*>(.*?)</dd>', hero, re.S)
                self.assertIsNotNone(fact, "The ticket range must be visible in the event facts")
                displayed = html.unescape(re.sub(r"<[^>]+>", "", fact.group(1))).strip()
                self.assertEqual(displayed, visible)
                generated = event(page, lang, f"https://wordandmusic.art/{prefix}concerts/on-the-wings-of-love.html")
                scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page, re.S)
                self.assertEqual(len(scripts), 1)
                stored = json.loads(scripts[0])
                self.assertEqual(stored["@type"], "MusicEvent")
                self.assertEqual(stored["offers"], generated[0]["offers"])
                self.assertEqual(stored["offers"].get("price"), "250")
                self.assertEqual(stored["offers"].get("priceCurrency"), "UAH")
                self.assertEqual(stored["offers"].get("url"), f"{TICKET}?locale={lang}")
                self.assertEqual(stored["offers"].get("availability"), "https://schema.org/InStock")


if __name__ == "__main__":
    unittest.main()
