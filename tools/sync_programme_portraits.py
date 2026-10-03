#!/usr/bin/env python3
"""Synchronize programme portrait presentation without changing credited text.

Principal billing follows each existing programme. Poster-only portraits retain
their authentic circular artwork within an equal-size rectangular card.
"""
import argparse
import html
import json
import re
from pathlib import Path

from build_artists import ROOT, photograph

RECORDS = json.loads((ROOT / 'assets/artists.json').read_text())
NAMES = {a['name'][lang]: a for a in RECORDS for lang in ('uk', 'en')}
NAMES['Дарія Погоріла'] = NAMES['Дарʼя Погоріла']
NAMES['Dariia Pohorila'] = NAMES['Daria Pohorila']
HOST = 'hennadii-taraniuk'
SUPPORTING = {
    'christmas-kaleidoscope': {'valentyna-frolova', 'yelyzaveta-bielous',
        'oleksandr-ponomarenko', 'oleksandr-vostriakov', 'daria-pohorila',
        'lidiia-hlinska', 'miao-xinyue'},
    'heartstrings': {'anastasiia-dovbius', 'nykyta-naumov',
        'valentyna-frolova', 'hanna-semets'},
}
# Separate 4:5 views; circle refinement never changes approved new-page tiles.
TILES = {
    'anzhelina-shvachka': (0, 40, 740),
    'liliia-hrevtsova': (1080, 900, 1400),
    'serhii-mahera': (0, 0, 300),
    'mariia-popovych': (300, 450, 1800),
    'mykola-chykarenko': (270, 0, 1960),
    'hennadii-taraniuk': (750, 1300, 3000),
    'nataliia-shmelova': (0, 0, 2400),
    'anastasiia-povazhna': (420, 480, 1500),
    'ihor-povazhnyi': (295, 0, 1900),
    'oleksandr-ponomarenko': (380, 440, 1700),
    'oleksandr-vostriakov': (360, 260, 1600),
    'kateryna-yasenchuk': (0, 0, 2400),
    'albina-holenach': (150, 510, 1450),
    'yelyzaveta-bielous': (300, 240, 1800),
    'daria-pohorila': (400, 350, 1600),
}


def tile(a, lang):
    p = a['portrait']
    if not p:
        return '<div class="ph performer-placeholder" aria-hidden="true"></div>'
    if 'label' in p:
        circle = photograph(a, lang)
        crop = p.get('circle_crop', p['crop'])
        scale = p['width'] / (crop['size'] * (1 - 2*p.get('rim_inset', 0)))
        sizes = f'(max-width:900px) {45*scale:.1f}vw, {23*scale:.1f}vw'
        circle = re.sub(r'sizes="[^"]*"', f'sizes="{sizes}"', circle)
        return '<div class="ph performer-poster-detail">' + circle + '</div>'
    x, y, width = TILES[a['id']]
    image = re.search(r'<img .*?>', photograph(a, lang))[0]
    style = (f'width:{p["width"]/width*100:.5f}%;height:auto;max-width:none;'
             f'left:{-x/width*100:.5f}%;top:{-y/(width*1.25)*100:.5f}%')
    image = re.sub(r'style="[^"]*"', f'style="{style}"', image)
    # At <900px the programme has two columns, otherwise four.
    scale = p['width']/width
    sizes = f'(max-width:900px) {45*scale:.1f}vw, {23*scale:.1f}vw'
    image = re.sub(r'sizes="[^"]*"', f'sizes="{sizes}"', image)
    return f'<div class="ph performer-portrait" data-crop="{x},{y},{width}">{image}</div>'


def div_end(source, start):
    depth = 0
    for tag in re.finditer(r'</?div\b[^>]*>', source[start:]):
        depth += -1 if tag[0].startswith('</') else 1
        if depth == 0:
            return start + tag.end()
    raise ValueError('Unclosed performer div')


def cards(source):
    result = []
    for group in re.finditer(r'<div class="people(?: [^"]*)?">', source):
        end = div_end(source, group.start())
        offset = group.end()
        while offset < end - 6:
            start = source.find('<div', offset, end - 6)
            if start == -1:
                break
            card_end = div_end(source, start)
            result.append(source[start:card_end])
            offset = card_end
    return result


def sync(path):
    source = path.read_text()
    language = 'en' if path.relative_to(ROOT).parts[0] == 'en' else 'uk'
    # The approved new layout already separates featured, supporting and host.
    if path.stem == 'on-the-wings-of-love':
        def refresh(match):
            alt = re.search(r'alt="([^"]*)"', match[0])
            if not alt:
                return match[0]
            a = NAMES[html.unescape(alt[1]).split(' — ')[0]]
            return re.sub(r'alt="[^"]*"', f'alt="{alt[1]}"', photograph(a, language))
        return re.sub(r'<span class="artist-portrait[^\"]*">.*?</span>', refresh, source, flags=re.S)
    match = re.search(r'<section class="artists" id="artists">.*?</section>', source, re.S)
    if not match:
        return source
    grouped = {'featured': [], 'supporting': [], 'host': []}
    programme_cards = cards(match[0])
    separate_host = len(programme_cards) > 4 or path.stem in SUPPORTING
    for card in programme_cards:
        heading = re.search(r'<h3\b[^>]*>(.*?)</h3>', card, re.S)
        if not heading:
            raise ValueError(f'{path}: performer without heading')
        name = html.unescape(re.sub('<[^>]+>', '', heading[1]))
        a = NAMES[name]
        group = ('host' if a['id'] == HOST and separate_host else 'supporting'
                 if a['id'] in SUPPORTING.get(path.stem, set()) else 'featured')
        # Retain the exact existing heading, role and all text after it.
        contents = card[heading.start():-6]
        photo = photograph(a, language) if group == 'supporting' else tile(a, language)
        grouped[group].append('<div>' + photo + contents + '</div>')
    old_groups = list(re.finditer(r'<div class="people(?: [^"]*)?">', match[0]))
    prefix = match[0][:old_groups[0].start()]
    suffix = match[0][div_end(match[0], old_groups[-1].start()):]
    groups = ''.join(f'<div class="people people-{group}">{"".join(values)}</div>'
                     for group, values in grouped.items() if values)
    new = prefix + groups + suffix
    return source[:match.start()] + new + source[match.end():]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    stale = []
    for path in sorted([*(ROOT / 'concerts').glob('*.html'),
                        *(ROOT / 'en/concerts').glob('*.html')]):
        result = sync(path)
        if result != path.read_text():
            stale.append(str(path.relative_to(ROOT)))
            if not args.check:
                path.write_text(result)
    if args.check and stale:
        raise SystemExit('Stale programme portraits: ' + ', '.join(stale))
    print('Programme portraits ' + ('consistent' if args.check else f'updated: {len(stale)} pages'))
