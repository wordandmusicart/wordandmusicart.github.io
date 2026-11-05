"""Independent acceptance for owner-confirmed 22 November announcement.

22.11.2026, 14:00, Будинок вчених / House of Scientists, 250 UAH. No end time
supplied; confirmed ticket sales are available; programme features Bizet, Ravel (with Rigaudon) and Poulenc
(without invented work titles), replacing Falla; canonical 7-paragraph #about.
"""
import unittest
from urllib.parse import urlsplit

if __package__:
    from .test_event_end_date import events
    from .structured_data import event
    from .test_landing_artists import Document, ROOT, ORIGIN, links
    from .test_october_rollover import facts, section, normalized
else:
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from test_event_end_date import events
    from structured_data import event
    from test_landing_artists import Document, ROOT, ORIGIN, links
    from test_october_rollover import facts, section, normalized

SLUG = 'concerts/vivre-aimer-rever-22112026.html'

UK_ABOUT_PARAGRAPHS = [
    (
        'Запрошуємо поринути у вишуканий світ французької музики, де елегантність '
        'звучання поєднується з силою поетичного слова та неповторною чаруючою '
        'атмосферою. Мелодії, у яких час завмирає, і почуття, що залишаються назавжди.'
    ),
    (
        'Витончені французькі mélodies Жоржа Бізе, грецькі народні пісні та '
        'пристрасна «Циганка» у художньому прочитанні Моріса Равеля, іронічний '
        'шарм та ніжність музики Франсіса Пуленка.'
    ),
    (
        'Віртуозна стихія скрипки та фортепіано переплітається з голосом і '
        'поетичним словом. Музика і поезія складаються в єдину розповідь, що '
        'відкривається кожному крізь призму власного світовідчуття.'
    ),
    (
        'Історії кохання і мрій, ніжності й пристрасті, іронії та щирості — '
        'у почуттях, над якими не владний час.'
    ),
    'Три композитори. Три художні світи. Одна музична подорож поза часом.',
    'Вечір, у якому музика торкається серця, а кожна мить наповнюється сенсом.',
    'Vivre, Aimer, rêver… Жити. Кохати. Мріяти.',
]

UK_BIZET_SONGS = (
    'Квітнева пісня',
    'Лагідне море',
    'Пісня божевільного',
    'Прощання арабської жінки',
    'Я про це нічого не скажу',
)

UK_RAVEL_GREEK_SONGS = (
    'Весільна пісня',
    'Там, біля церкви',
    'Який галант може зрівнятись зі мною?',
    'Пісня збирачів мастики',
    'Так весело!',
)

FORBIDDEN_FALLA_STRINGS = (
    'Мануель де Фалья',
    'Manuel de Falla',
    'Фалья',
    'Falla',
    '7 іспанських',
    'Seven Popular Spanish',
    '7 Spanish',
    'Мавританська шаль',
    'Сегідилья',
    'Астуріана',
    'Хота',
    'Колискова',
    'Поло',
    'Moorish',
    'Seguidilla',
    'Asturiana',
    'Jota',
    'Polo',
)


class November22Acceptance(unittest.TestCase):
    def test_paired_announcement_and_alias_use_only_confirmed_facts(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            poulenc = 'Франсіс Пуленк' if lang == 'uk' else 'Francis Poulenc'
            for route in (SLUG, 'concert.html'):
                with self.subTest(page=prefix + route):
                    path = ROOT / prefix / route
                    self.assertTrue(path.is_file(), 'New concert requires paired stable routes')
                    doc = Document(path).root
                    hero = next(doc.find('section', 'c-hero'))
                    self.assertEqual(normalized(next(doc.find('h1'))), 'Vivre, Aimer, Rêver…')
                    fact_values = [v for _, v in facts(doc)]
                    self.assertEqual(fact_values[:2], ['22.11.2026', '14:00'])
                    self.assertIn(fact_values[2], {'250 ₴'} if lang == 'uk' else {'250 ₴', 'UAH 250'})
                    self.assertNotIn('16:00', hero.text())
                    self.assertNotIn('Додаткова інформація', hero.text())
                    self.assertNotIn('More information', hero.text())
                    self.assertIn('Будинок вчених' if lang == 'uk' else 'House of Scientists', hero.text())
                    self.assertIn('Володимирська' if lang == 'uk' else 'Volodymyrska', hero.text())
                    self.assertFalse(list(hero.find(cls='poster-placeholder')))
                    poster, = hero.find('img')
                    self.assertIn('/assets/img/vivre-aimer-rever-22112026-poster-night.jpg', poster.attrs.get('src', ''))
                    self.assertEqual(int(poster.attrs['width']) / int(poster.attrs['height']), 4 / 5)
                    self.assertTrue(poster.attrs.get('alt'))
                    self.assertNotIn('16:00', poster.attrs.get('alt', ''))
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
                    self.assertIn('https://eventmate.app/events/share/93e50cf4-75cd-4418-b20c-254c7db657b7?locale=' + lang, links(hero))
                    self.assertFalse(list(doc.find(cls='sticky-buy')))
                    self.assertFalse(list(doc.find(cls='status-pending')))

                    meta = {n.attrs.get('name', n.attrs.get('property')): n.attrs.get('content', '') for n in doc.find('meta')}
                    self.assertEqual(meta['og:url'], ORIGIN + '/' + prefix + SLUG)
                    self.assertIn('vivre-aimer-rever-22112026-banner-night.jpg', meta.get('og:image', ''))
                    for meta_field in ('description', 'og:description'):
                        desc = meta.get(meta_field, '')
                        self.assertTrue(desc, f'Missing {meta_field}')
                        self.assertIn('14:00', desc)
                        self.assertIn(poulenc, desc)
                        self.assertIn('250', desc)
                        for forbidden in ('16:00', 'Фалья', 'Falla'):
                            self.assertNotIn(forbidden, desc)

                    subnav = next(doc.find('nav', 'subnav'))
                    subnav_text = normalized(subnav)
                    self.assertIn('14:00', subnav_text)
                    for forbidden in ('16:00', 'Фалья', 'Falla'):
                        self.assertNotIn(forbidden, subnav_text)

                    canonical = [n.attrs.get('href') for n in doc.find('link') if n.attrs.get('rel') == 'canonical']
                    self.assertEqual(canonical, [ORIGIN + '/' + prefix + SLUG])
                    schema = events(path.read_text(encoding='utf-8'))
                    self.assertEqual(len(schema), 1)
                    self.assertEqual(schema[0]['startDate'], '2026-11-22T14:00:00+02:00')
                    self.assertNotIn('endDate', schema[0], 'Never infer duration from October concert')
                    self.assertEqual(schema[0]['offers']['url'], 'https://eventmate.app/events/share/93e50cf4-75cd-4418-b20c-254c7db657b7?locale=' + lang)
                    self.assertEqual(len(schema[0].get('performer', [])), 4)
                    schema_desc = schema[0].get('description', '')
                    self.assertIn('14:00', schema_desc)
                    self.assertIn(poulenc, schema_desc)
                    for forbidden in ('16:00', 'Фалья', 'Falla'):
                        self.assertNotIn(forbidden, schema_desc)

    def test_start_only_generator_preserves_confirmed_clock_time_without_offer(self):
        for lang, labels, price in (
            ('uk', ('Дата', 'Час', 'Ціна'), '250 ₴'),
            ('en', ('Date', 'Time', 'Price'), 'UAH 250'),
        ):
            source = '<section class="c-hero"><h1>Confirmed start only</h1><dl>'
            source += ''.join(f'<dt class="meta muted">{label}</dt><dd>{value}</dd>'
                              for label, value in zip(labels, ('22.11.2026', '14:00', price)))
            source += '</dl></section>'
            generated = event(source, lang, 'https://wordandmusic.art/concert.html')[0]
            self.assertEqual(generated['startDate'], '2026-11-22T14:00:00+02:00')
            self.assertNotIn('endDate', generated)
            self.assertNotIn('offers', generated)

    def test_programme_replaces_falla_with_uninvented_poulenc_and_preserves_cycles(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            expected_composers = (
                ['Жорж Бізе', 'Моріс Равель', 'Франсіс Пуленк']
                if lang == 'uk'
                else ['Georges Bizet', 'Maurice Ravel', 'Francis Poulenc']
            )
            poulenc = expected_composers[-1]
            for route in (SLUG, 'concert.html'):
                with self.subTest(page=prefix + route):
                    doc = Document(ROOT / prefix / route).root
                    prog_sec = section(doc, 'program')
                    programme = normalized(prog_sec)

                    who_order = list(dict.fromkeys(normalized(w) for w in prog_sec.find(cls='who')))
                    self.assertEqual(who_order, expected_composers)
                    for composer in expected_composers:
                        self.assertIn(composer, programme)

                    for forbidden in FORBIDDEN_FALLA_STRINGS:
                        self.assertNotIn(forbidden, programme)

                    self.assertRegex(programme, r'op\.\s*21')
                    self.assertIn('Ригодон' if lang == 'uk' else 'Rigaudon', programme)
                    self.assertRegex(programme, r'грецьк' if lang == 'uk' else r'Greek')
                    self.assertIn('Циганка' if lang == 'uk' else 'Tzigane', programme)
                    if lang == 'uk':
                        for title in (*UK_BIZET_SONGS, *UK_RAVEL_GREEK_SONGS):
                            self.assertIn(title, programme, 'Every supplied Bizet and Ravel song remains visible')

                    poulenc_rows = [li for li in prog_sec.find('li') if poulenc in normalized(li)]
                    self.assertEqual(len(poulenc_rows), 1)
                    self.assertEqual(
                        [normalized(w) for w in poulenc_rows[0].find(cls='what') if normalized(w)],
                        [],
                        'Nothing is invented: Poulenc work titles are not specified in source',
                    )
                    self.assertEqual(normalized(poulenc_rows[0]), poulenc)

                    self.assertFalse(
                        [n for n in prog_sec.find(cls='n') if normalized(n)],
                        'No numbered 01/02/03 design labels',
                    )
                    self.assertNotRegex(programme, r'\b0[1-9]\b')

                    names = [normalized(n) for n in section(doc, 'artists').find('h3')]
                    self.assertEqual(
                        names,
                        ['Марія Попович', 'Микола Чикаренко', 'Дмитро Терентьєв', 'Геннадій Таранюк']
                        if lang == 'uk'
                        else ['Mariia Popovych', 'Mykola Chykarenko', 'Dmytro Terentiev', 'Hennadii Taraniuk'],
                    )

            named = Document(ROOT / prefix / SLUG).root
            current = Document(ROOT / prefix / 'concert.html').root
            for identity in ('about', 'program', 'artists', 'venue'):
                self.assertEqual(normalized(section(current, identity)), normalized(section(named, identity)))

    def test_about_section_matches_canonical_seven_paragraphs(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            for route in (SLUG, 'concert.html'):
                with self.subTest(page=prefix + route):
                    doc = Document(ROOT / prefix / route).root
                    about = section(doc, 'about')
                    paragraphs = [normalized(p) for p in about.find('p')]
                    self.assertEqual(len(paragraphs), 7)
                    about_text = ' '.join(paragraphs)
                    if lang == 'uk':
                        self.assertEqual(paragraphs, UK_ABOUT_PARAGRAPHS)
                        for stale in (
                            'Є музика, здатна зупинити мить',
                            'Мануеля де Фальї',
                            'Фалья',
                            'свободи й самотності',
                        ):
                            self.assertNotIn(stale, about_text)
                    else:
                        self.assertIn('french music', about_text.lower())
                        for required in (
                            'Georges Bizet',
                            'Maurice Ravel',
                            'Tzigane',
                            'Francis Poulenc',
                            'Three composers. Three artistic worlds.',
                            'Vivre, Aimer, rêver…',
                        ):
                            self.assertIn(required, about_text)
                        for forbidden in ('Manuel de Falla', 'Falla', 'Spanish'):
                            self.assertNotIn(forbidden, about_text)

    def test_home_has_confirmed_tickets_and_listing_links_new_event(self):
        for prefix in ('', 'en/'):
            with self.subTest(prefix=prefix or 'uk'):
                home = Document(ROOT / prefix / 'index.html').root
                aside = next(home.find('aside'))
                self.assertIn('22.11', aside.text())
                self.assertIn('14:00', aside.text())
                self.assertNotIn('16:00', aside.text())
                for img in aside.find('img'):
                    self.assertNotIn('16:00', img.attrs.get('alt', ''))
                self.assertIn('Vivre, Aimer, Rêver', aside.text())
                self.assertIn('/' + prefix + SLUG, links(aside))
                self.assertIn('https://eventmate.app/events/share/93e50cf4-75cd-4418-b20c-254c7db657b7?locale=' + ('en' if prefix else 'uk'), links(aside))
                self.assertFalse(list(aside.find(cls='concert-announcement')))
                self.assertNotIn('Квитки незабаром', aside.text())
                self.assertNotIn('Tickets coming soon', aside.text())

                listing = Document(ROOT / prefix / 'concerts.html').root
                upcoming = list(listing.find('article', 'upc'))
                self.assertEqual(len(upcoming), 1)
                self.assertIn('22.11', upcoming[0].text())
                self.assertIn('14:00', upcoming[0].text())
                self.assertNotIn('16:00', upcoming[0].text())
                for img in upcoming[0].find('img'):
                    self.assertNotIn('16:00', img.attrs.get('alt', ''))
                self.assertIn('/' + prefix + SLUG, links(upcoming[0]))
                self.assertFalse([h for h in links(upcoming[0]) if urlsplit(h).hostname == 'eventmate.app'])

                archive = section(listing, 'archive')
                self.assertNotIn('/' + prefix + SLUG, links(archive))
                for previous in ('vivre-aimer-rever', 'on-the-wings-of-love', 'on-the-wings-of-love-24102026'):
                    self.assertIn('/' + prefix + 'concerts/' + previous + '.html', links(archive))

    def test_vivre_hero_omits_uninvented_more_information_line(self):
        for page in (
            SLUG,
            'concert.html',
            'en/' + SLUG,
            'en/concert.html',
            'concerts/vivre-aimer-rever.html',
            'en/concerts/vivre-aimer-rever.html',
        ):
            with self.subTest(page=page):
                doc = Document(ROOT / page).root
                hero_text = normalized(next(doc.find('section', 'c-hero')))
                self.assertNotIn('Додаткова інформація', hero_text)
                self.assertNotIn('More information', hero_text)


if __name__ == '__main__':
    unittest.main()
