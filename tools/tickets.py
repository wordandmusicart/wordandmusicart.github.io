#!/usr/bin/env python3
"""Header «Квитки»/«Tickets» always opens the nearest concert with ticket sales.

Concerts come from the MusicEvent JSON-LD already on `concerts/*.html` (start,
end, offer URL). This writes that list into `assets/header.js`, which switches
the header buttons in the browser once a concert has ended, and sets the
static href (for no-JS visitors and crawlers) to the next concert as of today.
UA pages use ?locale=uk, EN pages ?locale=en. With no upcoming sale the
buttons open the organiser profile on Eventmate.

    python3 tools/tickets.py           # rebuild data and static links
    python3 tools/tickets.py --check   # CI: data block and link shape
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
HEADER_JS = ROOT / 'assets/header.js'
PROFILE = 'https://eventmate.app/users/share/wordmusic'
START, END = '/* tickets:start (tools/tickets.py) */', '/* tickets:end */'
BUTTON = re.compile(r'(<a class="btn btn-acc(?: mobile-ticket)?" href=")([^"]*)(")')


def strip_query(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


def concerts():
    found = []
    for page in sorted((ROOT / 'concerts').glob('*.html')):
        for block in re.findall(r'<script type="application/ld\+json">(.*?)</script>', page.read_text(), re.S):
            data = json.loads(block)
            items = data.get('@graph', [data]) if isinstance(data, dict) else data
            for item in items:
                offer = item.get('offers') if item.get('@type') == 'MusicEvent' else None
                if isinstance(offer, dict) and offer.get('url') and item.get('endDate'):
                    found.append({'end': item['endDate'], 'url': strip_query(offer['url'])})
    return sorted(found, key=lambda c: datetime.fromisoformat(c['end']))


def data_block(events):
    return f'{START}\nconst TICKET_EVENTS = {json.dumps(events, ensure_ascii=False)};\nconst TICKET_PROFILE = {json.dumps(PROFILE)};\n{END}'


def next_url(events, now):
    for event in events:
        if datetime.fromisoformat(event['end']) > now:
            return event['url']
    return PROFILE


def pages():
    return [p for p in sorted(ROOT.rglob('*.html')) if not set(p.relative_to(ROOT).parts) & {'tools', 'docs', 'node_modules', '_site'}]


def language(path):
    return 'en' if path.relative_to(ROOT).parts[0] == 'en' else 'uk'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    events = concerts()
    script = HEADER_JS.read_text()
    current = re.search(re.escape(START) + r'.*?' + re.escape(END), script, re.S)
    if not current:
        sys.exit('assets/header.js: tickets data markers missing')
    allowed = {e['url'] for e in events} | {PROFILE}
    errors = []
    if args.check:
        if current[0] != data_block(events):
            errors.append('assets/header.js: ticket data out of date, run tools/tickets.py')
        for page in pages():
            for _, href, _ in BUTTON.findall(page.read_text()):
                if strip_query(href) not in allowed or urlsplit(href).query != f'locale={language(page)}':
                    errors.append(f'{page.relative_to(ROOT)}: header ticket link {href}')
        if errors:
            sys.exit('\n'.join(errors))
        print('ticket links ok')
        return
    HEADER_JS.write_text(script.replace(current[0], data_block(events)))
    target = next_url(events, datetime.now(timezone.utc))
    changed = 0
    for page in pages():
        source = page.read_text()
        updated = BUTTON.sub(lambda m: f'{m[1]}{target}?locale={language(page)}{m[3]}', source)
        if updated != source:
            page.write_text(updated)
            changed += 1
    print(f'next concert tickets: {target} ({changed} pages updated)')


if __name__ == '__main__':
    main()
