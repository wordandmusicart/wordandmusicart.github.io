#!/usr/bin/env python3
"""Render the «Команда» / "Team" scene of both home pages from assets/team.json.

An entry is either {"artist": "<id>"} — name, role and circle crop come from
assets/artists.json, so a caption or crop never differs from the Artists page —
or a full record (id, name, role, portrait) for people who do not perform.

    python3 tools/build_team.py          # rewrite index.html and en/index.html
    python3 tools/build_team.py --check  # fail if a page is out of date
"""
from pathlib import Path
import html
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ESC = html.escape
HEADING = {'uk': 'Команда', 'en': 'Team'}
PAGES = {'uk': ROOT / 'index.html', 'en': ROOT / 'en/index.html'}
SECTION = re.compile(r'<section\b[^>]*\bid="team"[^>]*>.*?</section>\n', re.S)
CIRCLE = 200   # .team-portrait on desktop; smaller on phones (assets/team.css)
WIDTHS = (320, 480, 720, 960, 1440, 2400)


def people():
    artists = {a['id']: a for a in json.loads((ROOT / 'assets/artists.json').read_text())}
    return [artists[t['artist']] if 'artist' in t else t
            for t in json.loads((ROOT / 'assets/team.json').read_text())]


def role(text):
    """A hyphenated word («Мецо-сопрано») stays on one line."""
    return re.sub(r'[\w’]+-[\w’]+', r'<span class="nb">\g<0></span>', ESC(text, quote=False))


def portrait(person, lang):
    p = person['portrait']
    crop = p.get('circle_crop') or p['crop']
    base = p['src'].rsplit('.', 1)[0]
    variants = [f'{base}-{w}.webp {w}w' for w in WIDTHS
                if w < p['width'] and (ROOT / f'{base.lstrip("/")}-{w}.webp').exists()]
    srcset = ', '.join(variants + [f'{p["src"]} {p["width"]}w'])
    style = (f'width:{p["width"] / crop["size"] * 100:.5f}%;max-width:none;height:auto;'
             f'left:{-crop["x"] / crop["size"] * 100:.5f}%;top:{-crop["y"] / crop["size"] * 100:.5f}%')
    return (f'<span class="team-portrait"><img src="{ESC(p["src"])}" srcset="{ESC(srcset)}" '
            f'sizes="{p["width"] / crop["size"] * CIRCLE:.0f}px" alt="{ESC(person["name"][lang])}" '
            f'width="{p["width"]}" height="{p["height"]}" loading="lazy" decoding="async" '
            f'draggable="false" style="{style}"></span>')


def section(lang):
    items = '\n'.join(
        f'<li data-person="{p["id"]}">{portrait(p, lang)}<div class="team-info">'
        f'<h3 class="tem">{ESC(p["name"][lang])}</h3><p>{role(p["role"][lang])}</p></div></li>'
        for p in people())
    return ('<section class="wrap home-scene home-team" id="team" aria-labelledby="team-title">'
            f'<div class="sec-head"><h2 class="h2 tem" id="team-title">{HEADING[lang]}</h2></div>\n'
            f'<ul class="team">\n{items}\n</ul></section>\n')


def render(page, lang):
    page = SECTION.sub('', page)
    marker = '<section class="home-scene home-contact" id="contacts">'
    assert page.count(marker) == 1, 'The team scene stands before the contacts scene'
    return page.replace(marker, section(lang) + marker)


def main():
    stale = []
    for lang, path in PAGES.items():
        before = path.read_text()
        after = render(before, lang)
        if before != after:
            stale.append(path.relative_to(ROOT).as_posix())
            if '--check' not in sys.argv:
                path.write_text(after)
    if '--check' in sys.argv and stale:
        sys.exit('Run python3 tools/build_team.py: out of date ' + ', '.join(stale))
    print('team ok' if not stale else 'updated ' + ', '.join(stale))


if __name__ == '__main__':
    main()
