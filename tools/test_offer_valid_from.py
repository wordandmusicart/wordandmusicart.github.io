#!/usr/bin/env python3
"""Offer opening dates preserve the precision supplied by the owner.

The 15 October concert went on sale on 2 October 2026; no opening time was
supplied. Pages and generated JSON-LD use that ISO date. An event without a
source opening date continues to omit validFrom.
"""
import unittest

from structured_data import event
from test_event_end_date import ROOT, events


class OfferOpeningDate(unittest.TestCase):
    def test_named_and_alias_pages_have_confirmed_date_without_fabricated_time(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            for name in ('concert.html', 'concerts/on-the-wings-of-love.html'):
                path = ROOT / prefix / name
                with self.subTest(page=str(path.relative_to(ROOT))):
                    found = events(path.read_text())
                    self.assertEqual(len(found), 1)
                    self.assertEqual(found[0]['offers'].get('validFrom'), '2026-10-02')

    def source(self, lang, opening_date=None):
        date = 'Дата' if lang == 'uk' else 'Date'
        sales = 'Продаж триває' if lang == 'uk' else 'On sale'
        attribute = f' data-sales-start="{opening_date}"' if opening_date else ''
        return f'''<section class="c-hero">
<h1>Offer acceptance fixture</h1><div class="meta muted">2026</div>
<dl><dt class="meta muted">{date}</dt><dd>15.10</dd></dl>
<div class="c-cta"><a class="btn" href="https://example.com/ticket">Ticket</a></div>
<div class="status meta"{attribute}><i></i>{sales}</div>
</section>'''

    def test_generator_preserves_source_date_without_inventing_midnight(self):
        for lang in ('uk', 'en'):
            with self.subTest(language=lang):
                offer = event(self.source(lang, '2026-10-02'), lang,
                              'https://example.com/concert.html')[0]['offers']
                self.assertEqual(offer.get('validFrom'), '2026-10-02')

    def test_generator_omits_date_when_source_does_not_supply_it(self):
        for lang in ('uk', 'en'):
            with self.subTest(language=lang):
                offer = event(self.source(lang), lang,
                              'https://example.com/concert.html')[0]['offers']
                self.assertNotIn('validFrom', offer)


if __name__ == '__main__':
    unittest.main()
