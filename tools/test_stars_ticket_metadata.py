#!/usr/bin/env python3
"""Acceptance checks for November ticket sales and both winter MusicEvents."""
import unittest

if __package__:
    from .test_event_end_date import events
    from .test_landing_artists import Document, ROOT, ORIGIN, links
else:
    from test_event_end_date import events
    from test_landing_artists import Document, ROOT, ORIGIN, links

TICKET = 'https://eventmate.app/events/share/koncert-zirkam-nazustric'
DATES = {'29112026': '2026-11-29', '20122026': '2026-12-20'}


class StarsTicketMetadataAcceptance(unittest.TestCase):
    def test_detail_metadata_and_ticket_availability(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            for suffix, date in DATES.items():
                with self.subTest(language=lang, date=date):
                    relative = f'{prefix}concerts/towards-the-stars-{suffix}.html'
                    path = ROOT / relative
                    doc = Document(path).root
                    found = events(path.read_text())
                    self.assertEqual(len(found), 1, 'Each announced concert needs one MusicEvent')
                    event = found[0]
                    self.assertEqual(event['startDate'], date + 'T14:00:00+02:00')
                    self.assertNotIn('endDate', event, 'No confirmed end time is available')
                    canonical = next(n.attrs['href'] for n in doc.find('link') if n.attrs.get('rel') == 'canonical')
                    self.assertEqual(event['url'], canonical)
                    self.assertEqual(canonical, ORIGIN + '/' + relative)
                    og_image = next(n.attrs['content'] for n in doc.find('meta') if n.attrs.get('property') == 'og:image')
                    self.assertEqual(event['image'], [og_image])
                    self.assertIn(f'towards-the-stars-{suffix}-poster-', og_image)
                    self.assertEqual(event['eventStatus'], 'https://schema.org/EventScheduled')
                    self.assertEqual(event['eventAttendanceMode'], 'https://schema.org/OfflineEventAttendanceMode')
                    self.assertEqual(event['inLanguage'], lang)
                    self.assertEqual(event['location']['address']['addressCountry'], 'UA')
                    self.assertEqual(event['location']['address']['addressLocality'], 'Київ' if lang == 'uk' else 'Kyiv')
                    self.assertIn('45', event['location']['address']['streetAddress'])
                    self.assertIn('Будинок вчених' if lang == 'uk' else 'House of Scientists', event['location']['name'])
                    artists = next(n for n in doc.find('section') if n.attrs.get('id') == 'artists')
                    visible_names = [n.text().strip() for n in artists.find('h3')]
                    self.assertTrue(visible_names)
                    self.assertEqual([p['name'] for p in event['performer']], visible_names)
                    purchase_links = [href for href in links(doc) if 'eventmate.app/events/' in href]
                    if suffix == '29112026':
                        expected = TICKET + '?locale=' + lang
                        self.assertIn(expected, purchase_links)
                        self.assertTrue(all(href == expected for href in purchase_links))
                        offer = event['offers']
                        self.assertEqual(offer['url'], expected)
                        self.assertEqual(str(offer['price']), '250')
                        self.assertEqual(offer['priceCurrency'], 'UAH')
                        self.assertEqual(offer['availability'], 'https://schema.org/InStock')
                        self.assertTrue(any(('Продаж триває' if lang == 'uk' else 'On sale') in n.text() for n in doc.find(cls='status')))
                        sticky = list(doc.find(cls='sticky-buy'))
                        self.assertEqual(len(sticky), 1, 'Ticketed concert must include mobile .sticky-buy')
                        self.assertEqual(links(sticky[0]), [expected])
                    else:
                        self.assertNotIn('offers', event)
                        self.assertFalse(purchase_links, 'December has no confirmed event purchase URL')
                        self.assertFalse(list(doc.find(cls='sticky-buy')))

    def test_listing_cards_link_to_the_correct_event_only(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            for listing in ('index.html', 'concerts.html'):
                doc = Document(ROOT / prefix / listing).root
                for suffix in DATES:
                    with self.subTest(language=lang, listing=listing, date=suffix):
                        detail = f'/{prefix}concerts/towards-the-stars-{suffix}.html'
                        cards = [card for card in doc.find('article') if detail in links(card)]
                        self.assertEqual(len(cards), 1)
                        purchases = [href for href in links(cards[0]) if 'eventmate.app/events/' in href]
                        self.assertEqual(purchases, [TICKET + '?locale=' + lang] if suffix == '29112026' else [])


if __name__ == '__main__':
    unittest.main()
