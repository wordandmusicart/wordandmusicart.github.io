#!/usr/bin/env python3
"""Structured data (schema.org JSON-LD) for word&music.

Nothing is typed by hand: every value is read from the page itself.
- Home pages (/ and /en/): Organization + WebSite, from the contacts block.
- Concert pages (concert.html, concerts/*.html and EN twins): MusicEvent,
  from the H1, the date line, the facts block (date, start, end, venue,
  address), the performers, the ticket link, og:image and the description.
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
LABELS = {'Дата': 'date', 'Початок': 'start', 'Завершення': 'end', 'Місце': 'venue', 'Адреса': 'address',
          'Date': 'date', 'Start': 'start', 'End': 'end', 'Venue': 'venue', 'Address': 'address'}
CITY = {'uk': 'Київ', 'en': 'Kyiv'}
ON_SALE = ('Продаж триває', 'On sale')


def text(s):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', '', s))).strip()


def meta(s, attr, name):
    m = re.search(rf'<meta {attr}="{re.escape(name)}" content="([^"]*)"', s)
    return html.unescape(m.group(1)) if m else ''


def home_url(page_url, lang):
    u = urlparse(page_url)
    return f'{u.scheme}://{u.netloc}' + ('/en/' if lang == 'en' else '/')


def organization(s, lang, url):
    contacts = re.search(r'<section class="news" id="contacts">(.*?)</section>', s, re.S)
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
    year = re.search(r'<div class="meta muted">[^<]*?(\d{4})</div>', hero)
    if not (year and 'date' in facts):
        return None
    day, month = facts['date'].split('.')

    def when(hm):
        d = datetime(int(year.group(1)), int(month), int(day))
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
    people = re.search(r'<div class="people">(.*?)</div></div>', s, re.S)
    if people:
        names = [text(n) for n in re.findall(r'<h3[^>]*>(.*?)</h3>', people.group(1), re.S)]
        if names:
            ev['performer'] = [{'@type': 'Person', 'name': n} for n in names]
    ev['organizer'] = {'@type': 'Organization', 'name': 'word&music', 'url': home_url(url, 'uk')}
    tickets = re.search(r'<div class="c-cta"[^>]*><a class="btn" href="([^"]+)"', hero)
    if tickets:
        offer = {'@type': 'Offer', 'url': html.unescape(tickets.group(1))}
        status = re.search(r'class="status meta"><i></i>([^<]+)<', s)
        if status and status.group(1).strip() in ON_SALE:
            offer['availability'] = 'https://schema.org/InStock'
        ev['offers'] = offer
    return [ev]


def data(path, s):
    lang = re.search(r'<html lang="(\w+)"', s).group(1)
    url = meta(s, 'property', 'og:url')
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel in ('index.html', 'en/index.html'):
        return home(s, lang, url)
    if re.fullmatch(r'(en/)?(concert\.html|concerts/[\w-]+\.html)', rel):
        return event(s, lang, url)
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
                   + glob.glob(os.path.join(ROOT, 'en', 'concerts', '*.html')))
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
