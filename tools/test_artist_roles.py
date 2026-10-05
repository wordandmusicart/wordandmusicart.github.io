#!/usr/bin/env python3
"""One capitalised caption per artist, everywhere (owner decision, 4 October 2026).

The line under a performer's name repeats the role in assets/artists.json on
every page: the artists directory, each concert programme (UA and EN).
Every UA and EN role and card caption starts with a capital: «Сопрано»,
«Soprano», «Солістка Національної опери України, … · Мецо-сопрано».
The owner's 5 October 2026 order puts existing credits before the voice type.
Never «партія …», never unapproved «лауреат…» under a name.
The owner's 5 October 2026 exception is Shvachka's exact Shevchenko Prize credit.

A role that genuinely belongs to one concert is listed in PER_CONCERT.
"""
import html
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ARTISTS = json.loads((ROOT / 'assets/artists.json').read_text())
NAMES = {a['name'][lang]: (a, lang) for a in ARTISTS for lang in ('uk', 'en')}
NAMES['Дарія Погоріла'] = NAMES['Дарʼя Погоріла']
NAMES['Dariia Pohorila'] = NAMES['Daria Pohorila']
# Hennadii Taraniuk's part differs by concert; Dariia Pohorila also hosted one.
PER_CONCERT = {
    'hennadii-taraniuk': {'Художнє слово', 'Ведучий', 'Художнє слово та ведучий',
                          'Spoken word', 'Host', 'Spoken word and host'},
    'daria-pohorila': {'Сопрано · Ведуча', 'Soprano · Host'},
}
CAPTION = re.compile(r'<h3[^>]*>([^<]*)</h3>\s*<p[^>]*>([^<]*)</p>')
SHVACHKA_AWARD_SUFFIXES = {
    'uk': ', лауреатка Національної премії України імені Тараса Шевченка',
    'en': ', laureate of the Taras Shevchenko National Prize of Ukraine',
}
SHVACHKA_ROLES = {
    'uk': 'Солістка Національної опери України, народна артистка України'
          + SHVACHKA_AWARD_SUFFIXES['uk'] + ' · Мецо-сопрано',
    'en': 'Soloist of the National Opera of Ukraine, People’s Artist of Ukraine'
          + SHVACHKA_AWARD_SUFFIXES['en'] + ' · Mezzo-soprano',
}


def pages():
    yield from sorted(ROOT.glob('concerts/*.html'))
    yield from sorted(ROOT.glob('en/concerts/*.html'))
    yield from (ROOT / p for p in ('concert.html', 'en/concert.html', 'artists.html', 'en/artists.html'))


class ArtistRoles(unittest.TestCase):
    def assert_starts_with_capital(self, caption):
        initial = next((char for char in caption if char.isalpha()), '')
        self.assertTrue(initial and initial.isupper(),
                        f'caption must start with a capital: {caption!r}')

    def test_artist_roles_start_with_capitals(self):
        for artist in ARTISTS:
            for lang in ('uk', 'en'):
                with self.subTest(artist=artist['id'], lang=lang):
                    self.assert_starts_with_capital(artist['role'][lang])

    def test_known_card_captions_start_with_capitals(self):
        for page in pages():
            for name, caption in CAPTION.findall(page.read_text()):
                name, caption = html.unescape(name).strip(), html.unescape(caption).strip()
                if name in NAMES:
                    with self.subTest(page=str(page.relative_to(ROOT)), name=name):
                        self.assert_starts_with_capital(caption)

    def test_captions_repeat_the_artist_record(self):
        for page in pages():
            for name, caption in CAPTION.findall(page.read_text()):
                name, caption = html.unescape(name).strip(), html.unescape(caption).strip()
                if name not in NAMES:
                    continue
                artist, lang = NAMES[name]
                allowed = {artist['role'][lang]} | PER_CONCERT.get(artist['id'], set())
                with self.subTest(page=str(page.relative_to(ROOT)), name=name):
                    self.assertIn(caption, allowed)

    def test_shvachka_has_exact_approved_shevchenko_prize_credit(self):
        artist = next(a for a in ARTISTS if a['id'] == 'anzhelina-shvachka')
        for lang in ('uk', 'en'):
            with self.subTest(lang=lang):
                self.assertEqual(artist['role'][lang], SHVACHKA_ROLES[lang])

    def test_no_part_or_laureate_under_names(self):
        for artist in ARTISTS:
            for lang in ('uk', 'en'):
                role = artist['role'][lang].lower()
                if (artist['id'] == 'anzhelina-shvachka'
                        and artist['role'][lang] == SHVACHKA_ROLES[lang]):
                    role = role.replace(SHVACHKA_AWARD_SUFFIXES[lang].lower(), '', 1)
                with self.subTest(artist=artist['id'], lang=lang):
                    self.assertNotRegex(role, r'парті[яїю]|лауреат|laureate|співавтор|co-author|меццо')


if __name__ == '__main__':
    unittest.main()
