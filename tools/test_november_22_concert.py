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
NEXT = 'concerts/towards-the-stars-29112026.html'

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
    def test_archived_concert_retains_confirmed_facts_assets_and_canonical_urls(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            poulenc = 'Франсіса Пуленка' if lang == 'uk' else 'Francis Poulenc'
            with self.subTest(page=prefix + SLUG):
                path = ROOT / prefix / SLUG
                self.assertTrue(path.is_file(), 'Archived concert requires paired stable routes')
                doc = Document(path).root
                hero = next(doc.find('section', 'c-hero'))
                self.assertEqual(normalized(next(doc.find('h1'))), 'Vivre, Aimer, Rêver…')
                fact_values = [v for _, v in facts(doc)]
                self.assertEqual(fact_values[:2], ['22.11.2026', '14:00'])
                self.assertNotIn('250 ₴', fact_values)
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
                self.assertFalse([href for href in links(next(doc.find('main'))) if urlsplit(href).hostname == 'eventmate.app'])
                self.assertFalse(list(doc.find(cls='sticky-buy')))
                self.assertFalse(list(doc.find(cls='status')))
                self.assertIn('Past concert' if lang == 'en' else 'Архівний концерт', next(doc.find(cls='crumbs')).text())

                meta = {n.attrs.get('name', n.attrs.get('property')): n.attrs.get('content', '') for n in doc.find('meta')}
                self.assertEqual(meta['og:url'], ORIGIN + '/' + prefix + SLUG)
                self.assertIn('vivre-aimer-rever-22112026-banner-night.jpg', meta.get('og:image', ''))
                for meta_field in ('description', 'og:description'):
                    desc = meta.get(meta_field, '')
                    self.assertTrue(desc, f'Missing {meta_field}')
                    self.assertIn(poulenc, desc)
                    self.assertNotIn('250', desc)
                    for forbidden in ('16:00', 'Фалья', 'Falla'):
                        self.assertNotIn(forbidden, desc)

                subnav = next(doc.find('nav', 'subnav'))
                subnav_text = normalized(subnav)
                self.assertFalse(list(subnav.find(cls='r')))
                for forbidden in ('16:00', 'Фалья', 'Falla'):
                    self.assertNotIn(forbidden, subnav_text)

                canonical = [n.attrs.get('href') for n in doc.find('link') if n.attrs.get('rel') == 'canonical']
                self.assertEqual(canonical, [ORIGIN + '/' + prefix + SLUG])
                self.assertFalse(events(path.read_text(encoding='utf-8')))

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
            with self.subTest(page=prefix + SLUG):
                doc = Document(ROOT / prefix / SLUG).root
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

    def test_about_section_matches_canonical_seven_paragraphs(self):
        for prefix, lang in (('', 'uk'), ('en/', 'en')):
            with self.subTest(page=prefix + SLUG):
                doc = Document(ROOT / prefix / SLUG).root
                about = section(doc, 'about')
                paragraphs = [normalized(p) for p in about.find('p')]
                self.assertEqual(len(paragraphs), 7)
                about_text = ' '.join(paragraphs)
                if lang == 'uk':
                    self.assertEqual(paragraphs[1:5], UK_ABOUT_PARAGRAPHS[1:5])
                    self.assertEqual(paragraphs[-1], UK_ABOUT_PARAGRAPHS[-1])
                    self.assertEqual(paragraphs[0], UK_ABOUT_PARAGRAPHS[0].replace(
                        'Запрошуємо поринути у', 'Програма відкрила'))
                    self.assertEqual(paragraphs[5], UK_ABOUT_PARAGRAPHS[5].replace('Вечір', 'Концерт'))
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

    def test_home_promotes_november_29_and_listing_archives_november_22(self):
        for prefix in ('', 'en/'):
            with self.subTest(prefix=prefix or 'uk'):
                home = Document(ROOT / prefix / 'index.html').root
                aside = next(home.find('aside'))
                self.assertIn('29.11', aside.text())
                self.assertIn('14:00', aside.text())
                self.assertIn('Towards the Stars' if prefix else 'Зіркам назустріч', aside.text())
                self.assertIn('/' + prefix + NEXT, links(aside))
                self.assertIn('https://eventmate.app/events/share/koncert-zirkam-nazustric?locale=' + ('en' if prefix else 'uk'), links(aside))
                self.assertNotIn('/' + prefix + SLUG, links(aside))

                listing = Document(ROOT / prefix / 'concerts.html').root
                upcoming, = listing.find('article', 'upc')
                self.assertIn('/' + prefix + NEXT, links(upcoming))
                self.assertNotIn('/' + prefix + SLUG, links(upcoming))

                archive = section(listing, 'archive')
                first = next(archive.find(cls='arow'))
                self.assertIn('22.11', first.text())
                self.assertIn('/' + prefix + SLUG, links(first))
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
