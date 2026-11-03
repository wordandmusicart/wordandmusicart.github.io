"""Independent acceptance for owner-confirmed 22 November announcement.

22.11.2026, 16:00, Будинок вчених / House of Scientists, 250 UAH. No end,
ticket URL supplied; owner-approved November artwork was subsequently supplied. Source Word programme adds Ravel's Rigaudon.
"""
import unittest
from urllib.parse import urlsplit

from .test_event_end_date import events
from .structured_data import event
from .test_landing_artists import Document, ROOT, ORIGIN, links
from .test_october_rollover import facts, section, normalized

SLUG = 'concerts/vivre-aimer-rever-22112026.html'


class November22Acceptance(unittest.TestCase):
    def test_paired_announcement_and_alias_use_only_confirmed_facts(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            for route in (SLUG, 'concert.html'):
                with self.subTest(page=prefix + route):
                    path = ROOT / prefix / route
                    self.assertTrue(path.is_file(), 'New concert requires paired stable routes')
                    doc = Document(path).root
                    hero = next(doc.find('section', 'c-hero'))
                    self.assertEqual(normalized(next(doc.find('h1'))), 'Vivre, Aimer, Rêver…')
                    self.assertEqual([v for _, v in facts(doc)][:3], ['22.11.2026', '16:00', '250 ₴'])
                    self.assertIn('Будинок вчених' if lang == 'uk' else 'House of Scientists', hero.text())
                    self.assertIn('Володимирська' if lang == 'uk' else 'Volodymyrska', hero.text())
                    self.assertFalse(list(hero.find(cls='poster-placeholder')))
                    poster, = hero.find('img')
                    self.assertIn('/assets/img/vivre-aimer-rever-22112026-poster-night.jpg', poster.attrs.get('src', ''))
                    self.assertEqual(int(poster.attrs['width']) / int(poster.attrs['height']), 4 / 5)
                    self.assertTrue(poster.attrs.get('alt'))
                    sources = list(hero.find('source'))
                    self.assertEqual(len(sources), 1)
                    self.assertIn('vivre-aimer-rever-22112026-poster-light', sources[0].attrs.get('srcset', ''))
                    for image in [poster, *sources]:
                        candidates = image.attrs.get('srcset', '').split(',')
                        self.assertGreater(len(candidates), 1)
                        for candidate in candidates:
                            asset = urlsplit(candidate.strip().split()[0]).path
                            self.assertTrue((ROOT / asset.lstrip('/')).is_file(), asset)
                    self.assertFalse(any('20261003' in value for node in hero.find() for value in node.attrs.values()))
                    self.assertFalse([h for h in links(doc) if urlsplit(h).hostname == 'eventmate.app'])
                    self.assertFalse(list(doc.find(cls='sticky-buy')))
                    status = list(doc.find(cls='status-pending'))
                    self.assertTrue(status, 'Announcement must show pending sale state')
                    self.assertNotIn('Продаж триває' if lang == 'uk' else 'On sale', status[0].text())
                    meta = {n.attrs.get('name', n.attrs.get('property')): n.attrs.get('content', '') for n in doc.find('meta')}
                    self.assertEqual(meta['og:url'], ORIGIN + '/' + prefix + SLUG)
                    self.assertIn('vivre-aimer-rever-22112026-banner-night.jpg', meta.get('og:image', ''))
                    canonical = [n.attrs.get('href') for n in doc.find('link') if n.attrs.get('rel') == 'canonical']
                    self.assertEqual(canonical, [ORIGIN + '/' + prefix + SLUG])
                    schema = events(path.read_text())
                    self.assertEqual(len(schema), 1)
                    self.assertEqual(schema[0]['startDate'], '2026-11-22T16:00:00+02:00')
                    self.assertNotIn('endDate', schema[0], 'Never infer duration from October concert')
                    self.assertNotIn('offers', schema[0], 'Price alone does not create a ticket offer')
                    self.assertEqual(len(schema[0].get('performer', [])), 4)

    def test_start_only_generator_preserves_confirmed_clock_time_without_offer(self):
        for lang, labels in (('uk', ('Дата', 'Час', 'Ціна')), ('en', ('Date', 'Time', 'Price'))):
            source = '<section class="c-hero"><h1>Confirmed start only</h1><dl>'
            source += ''.join(f'<dt class="meta muted">{label}</dt><dd>{value}</dd>'
                              for label, value in zip(labels, ('22.11.2026', '16:00', '250 ₴')))
            source += '</dl></section>'
            generated = event(source, lang, 'https://wordandmusic.art/concert.html')[0]
            self.assertEqual(generated['startDate'], '2026-11-22T16:00:00+02:00')
            self.assertNotIn('endDate', generated)
            self.assertNotIn('offers', generated)

    def test_programme_preserves_all_source_cycles_and_adds_rigaudon(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            doc = Document(ROOT / prefix / SLUG).root
            programme = section(doc, 'program').text()
            for composer in (['Жорж Бізе', 'Моріс Равель', 'Мануель де Фалья'] if lang == 'uk'
                             else ['Georges Bizet', 'Maurice Ravel', 'Manuel de Falla']):
                self.assertIn(composer, programme)
            self.assertRegex(programme, r'Ригодон|Rigaudon')
            self.assertRegex(programme, r'Циганка|Tzigane')
            self.assertRegex(programme, r'21')
            if lang == 'uk':
                for title in ('Квітнева пісня', 'Лагідне море', 'Пісня божевільного',
                              'Прощання арабської жінки', 'Я про це нічого не скажу',
                              'Весільна пісня', 'Там, біля церкви', 'Який галант може зрівнятись зі мною?',
                              'Пісня збирачів мастики', 'Так весело!', 'Мавританська шаль',
                              'Сегідилья', 'Астуріана', 'Хота', 'Колискова', 'Пісня', 'Поло'):
                    self.assertIn(title, programme, 'Every supplied song remains visible')
            self.assertFalse([n for n in section(doc, 'program').find(cls='n') if n.text().strip()],
                             'No new numbered design labels')
            names = [n.text().strip() for n in section(doc, 'artists').find('h3')]
            self.assertEqual(names, ['Марія Попович', 'Микола Чикаренко', 'Дмитро Терентьєв', 'Геннадій Таранюк'] if lang == 'uk'
                             else ['Mariia Popovych', 'Mykola Chykarenko', 'Dmytro Terentiev', 'Hennadii Taraniuk'])
            current = Document(ROOT / prefix / 'concert.html').root
            for identity in ('about', 'program', 'artists', 'venue'):
                self.assertEqual(normalized(section(current, identity)), normalized(section(doc, identity)))

    def test_home_and_upcoming_listing_link_new_event_without_ticket_actions(self):
        for prefix in ('', 'en/'):
            home = Document(ROOT / prefix / 'index.html').root
            aside = next(home.find('aside'))
            self.assertIn('22.11', aside.text())
            self.assertIn('Vivre, Aimer, Rêver', aside.text())
            self.assertIn('/' + prefix + SLUG, links(aside))
            listing = Document(ROOT / prefix / 'concerts.html').root
            upcoming = list(listing.find('article', 'upc'))
            self.assertEqual(len(upcoming), 1)
            self.assertIn('22.11', upcoming[0].text())
            self.assertIn('/' + prefix + SLUG, links(upcoming[0]))
            archive = section(listing, 'archive')
            self.assertNotIn('/' + prefix + SLUG, links(archive))
            for previous in ('vivre-aimer-rever', 'on-the-wings-of-love', 'on-the-wings-of-love-24102026'):
                self.assertIn('/' + prefix + 'concerts/' + previous + '.html', links(archive))


if __name__ == '__main__':
    unittest.main()
