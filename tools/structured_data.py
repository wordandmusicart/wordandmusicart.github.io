#!/usr/bin/env python3
"""Structured data (schema.org JSON-LD) for word&music.

JSON-LD values are read from the page itself.
- Home pages (/ and /en/): Organization + WebSite, from the contacts block.
- Gallery pages (photo/*.html): ImageGallery with the photographer.
- Current concert pages (concert.html and its EN twin): MusicEvent,
  from the H1, the date line, the facts block (date, start, end, price,
  location, address), the performers, the ticket link, og:image and the description.
- Announced concert pages also carry MusicEvent, without an Offer until a ticket URL is supplied.
- Past concert pages have no Event markup because they have no current ticket
  offers; their visible facts are kept on the pages.
A fact missing on the page is left out of the JSON-LD.

    python3 tools/structured_data.py          # write JSON-LD into pages
    python3 tools/structured_data.py --check  # fail if a page is out of date
"""
import glob, html, json, os, re, sys
from datetime import datetime
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KYIV = ZoneInfo('Europe/Kyiv')
BLOCK = re.compile(r'\n?<script type="application/ld\+json">.*?</script>', re.S)
LABELS = {'Дата': 'date', 'Час': 'time', 'Початок': 'start', 'Завершення': 'end', 'Ціна': 'price', 'Локація': 'venue', 'Адреса': 'address',
          'Date': 'date', 'Time': 'time', 'Start': 'start', 'End': 'end', 'Price': 'price', 'Location': 'venue', 'Address': 'address'}
CITY = {'uk': 'Київ', 'en': 'Kyiv'}
ON_SALE = ('Продаж триває', 'On sale')
# Other spellings people search for (from the people themselves), keyed by
# the name as the site shows it. Only these go into alternateName/sameAs.
PEOPLE = [
    {'names': ('Геннадій Таранюк', 'Hennadii Taraniuk', 'Gennadiy Taraniuk',
               'Gennadiy Taranyuk', 'Hennadii Taranyuk')},
    {'names': ('Кирило Русанівський', 'Kyrylo Rusanivsky', 'Kyrylo Rusanivskyi'),
     'sameAs': ['https://rusanivsky.com/']},
]


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def meta(s, attr, name):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ''


def person(name):
    p = {'@type': 'Person', 'name': name}
    for known in PEOPLE:
        if name in known['names']:
            p['alternateName'] = [n for n in known['names'] if n != name]
            if known.get('sameAs'):
                p['sameAs'] = known['sameAs']
    return p


def home_url(page_url, lang):
    u = urlparse(page_url)
    return f'{u.scheme}://{u.netloc}' + ('/en/' if lang == 'en' else '/')


def organization(s, lang, url):
    contacts = re.search(r'<section\b[^>]*\bid="contacts"[^>]*>(.*?)</section>', s, re.S)
    c = contacts.group(1) if contacts else ''
    org = {'@type': 'Organization', '@id': home_url(url, 'uk') + '#organization',
           'name': 'word&music', 'url': home_url(url, 'uk'),
           'logo': home_url(url, 'uk') + 'icon-512.png'}
    email = re.search(r'href="mailto:([^"]+)"', c)
    if email:
        org['email'] = email.group(1)
    same = sorted(set(re.findall(r'href="(https://(?:www\.)?(?:instagram|youtube)\.com/[^"]+)"', c)))
    if same:
        org['sameAs'] = same
    return org


def home(s, lang, url):
    return [organization(s, lang, url),
            {'@type': 'WebSite', 'name': 'word&music', 'url': url, 'inLanguage': lang,
             'publisher': {'@id': home_url(url, 'uk') + '#organization'}}]


def event(s, lang, url):
    hero = re.search(r'<section class="c-hero.*?</section>', s, re.S)
    if not hero:
        return None
    hero = hero.group(0)
    facts = {LABELS[k]: text(v) for k, v in
             re.findall(r'<dt class="meta muted">([^<]+)</dt><dd[^>]*>(.*?)</dd>', hero) if k in LABELS}
    if 'time' in facts:
        interval = re.fullmatch(r'(\d{2}:\d{2})\s*[–—-]\s*(\d{2}:\d{2})', facts['time'])
        if interval:
            facts['start'], facts['end'] = interval.groups()
    if 'date' not in facts:
        return None
    parts = facts['date'].split('.')
    if len(parts) == 3:
        day, month, yr = parts
    else:
        day, month = parts
        year = re.search(r'<div class="meta muted">[^<]*?(\d{4})</div>', hero)
        yr = year.group(1) if year else None
        if not yr:
            return None

    def when(hm):
        d = datetime(int(yr), int(month), int(day))
        if not hm:
            return d.date().isoformat()
        h, m = hm.split(':')
        return d.replace(hour=int(h), minute=int(m), tzinfo=KYIV).isoformat()

    ev = {'@type': 'MusicEvent', 'name': text(re.search(r'<h1[^>]*>(.*?)</h1>', hero, re.S).group(1)),
          'url': url, 'inLanguage': lang, 'startDate': when(facts.get('start'))}
    if facts.get('end') and facts.get('start'):
        ev['endDate'] = when(facts['end'])
    ev['eventStatus'] = 'https://schema.org/EventScheduled'
    ev['eventAttendanceMode'] = 'https://schema.org/OfflineEventAttendanceMode'
    desc = meta(s, 'name', 'description')
    if desc:
        ev['description'] = desc
    img = meta(s, 'property', 'og:image')
    if img:
        ev['image'] = [img]
    if facts.get('venue'):
        place = {'@type': 'Place', 'name': facts['venue']}
        if facts.get('address'):
            city = CITY[lang]
            street = re.sub(rf'^{city},\s*|,\s*{city}$', '', facts['address'])
            place['address'] = {'@type': 'PostalAddress', 'streetAddress': street,
                                'addressLocality': city, 'addressCountry': 'UA'}
        ev['location'] = place
    people = re.search(r'<section\b[^>]*class="[^"]*\bartists\b[^"]*"[^>]*>(.*?)</section>', s, re.S)
    if people:
        names = [text(n) for n in re.findall(r'<h3[^>]*>(.*?)</h3>', people.group(1), re.S)]
        if names:
            ev['performer'] = [person(n) for n in names]
    ev['organizer'] = {'@type': 'Organization', 'name': 'word&music', 'url': home_url(url, 'uk')}
    tickets = re.search(r'<div class="c-cta"[^>]*><a class="btn" href="([^"]+)"', hero)
    if tickets:
        offer = {'@type': 'Offer', 'url': html.unescape(tickets.group(1))}
        price = re.fullmatch(
            r'(?:(\d+)(?:\s*[–—-]\s*(\d+))?\s*(?:грн|₴|UAH)|₴\s*(\d+)(?:\s*[–—-]\s*(\d+))?)',
            facts.get('price', ''))
        if price:
            low = price.group(1) or price.group(3)
            high = price.group(2) or price.group(4)
            if high is None or int(low) <= int(high):
                offer['price'] = low
                offer['priceCurrency'] = 'UAH'
        status = re.search(r'class="status meta"(?: data-sales-start="([\d-]+)")?><i></i>([^<]+)<', s)
        if status and status.group(2).strip() in ON_SALE:
            offer['availability'] = 'https://schema.org/InStock'
        if status and status.group(1):
            # The owner supplied a date only; do not invent a midnight opening.
            offer['validFrom'] = datetime.fromisoformat(status.group(1)).date().isoformat()
        ev['offers'] = offer
    return [ev]


def gallery(s, lang, url):
    head = re.search(r'<div class="list-head".*?<div class="meta muted">(.*?)</div><h1[^>]*>(.*?)</h1>', s, re.S)
    if not head:
        return None
    g = {'@type': 'ImageGallery', 'name': meta(s, 'property', 'og:title'), 'url': url, 'inLanguage': lang}
    desc = meta(s, 'name', 'description')
    if desc:
        g['description'] = desc
    by = re.search(r'(?:фотограф|by) (.+)$', text(head.group(1)))
    if by:
        g['author'] = person(by.group(1).strip())
    return [g]


def data(path, s):
    lang = re.search(r'<html lang="(\w+)"', s).group(1)
    url = meta(s, 'property', 'og:url')
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel in ('index.html', 'en/index.html'):
        return home(s, lang, url)
    if rel in ('concert.html', 'en/concert.html',
               'concerts/on-the-wings-of-love.html', 'en/concerts/on-the-wings-of-love.html',
               'concerts/on-the-wings-of-love-25102026.html', 'en/concerts/on-the-wings-of-love-25102026.html'):
        return event(s, lang, url)
    if re.fullmatch(r'(en/)?photo/[\w-]+\.html', rel):
        return gallery(s, lang, url)
    return None


def render(items):
    doc = items[0] if len(items) == 1 else {'@graph': items}
    doc = {'@context': 'https://schema.org', **doc}
    body = json.dumps(doc, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'\n<script type="application/ld+json">\n{body}\n</script>'


def main(check):
    problems = []
    pages = sorted(glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, 'en', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'concerts', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'en', 'concerts', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'photo', '*.html'))
                   + glob.glob(os.path.join(ROOT, 'en', 'photo', '*.html')))
    for p in pages:
        s = open(p, encoding='utf-8').read()
        items = data(p, s)
        new = BLOCK.sub('', s)
        if items:
            new = new.replace('\n</head>', render(items) + '\n</head>', 1) if '\n</head>' in new \
                else new.replace('</head>', render(items) + '\n</head>', 1)
        if new != s:
            if check:
                problems.append(f'{os.path.relpath(p, ROOT)}: JSON-LD out of date')
            else:
                open(p, 'w', encoding='utf-8').write(new)
    return problems


if __name__ == '__main__':
    probs = main('--check' in sys.argv)
    print('\n'.join(probs) or 'structured data ok')
    sys.exit(1 if probs else 0)
