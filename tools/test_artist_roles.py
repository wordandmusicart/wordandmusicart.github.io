#!/usr/bin/env python3
"""One caption per artist, everywhere (owner decision, 3 October 2026).

The line under a performer's name repeats the role in assets/artists.json on
every page: the artists directory, each concert programme (UA and EN).
Format follows the 15 October concert page: voice or instrument in lower
case, then « · » and the title with a capital («мецо-сопрано · Солістка
Національної опери України, …»); functions such as «Концертмейстер» start
with a capital. Never «партія …», never «лауреат…» under a name.

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
    'daria-pohorila': {'сопрано · Ведуча', 'soprano · Host'},
}
CAPTION = re.compile(r'<h3[^>]*>([^<]*)</h3>\s*<p[^>]*>([^<]*)</p>')


def pages():
    yield from sorted(ROOT.glob('concerts/*.html'))
    yield from sorted(ROOT.glob('en/concerts/*.html'))
    yield from (ROOT / p for p in ('concert.html', 'en/concert.html', 'artists.html', 'en/artists.html'))


class ArtistRoles(unittest.TestCase):
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

    def test_no_part_or_laureate_under_names(self):
        for artist in ARTISTS:
            for lang in ('uk', 'en'):
                role = artist['role'][lang].lower()
                with self.subTest(artist=artist['id'], lang=lang):
                    self.assertNotRegex(role, r'парті[яїю]|лауреат|laureate|співавтор|co-author|меццо')


if __name__ == '__main__':
    unittest.main()
