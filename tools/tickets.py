#!/usr/bin/env python3
"""Keep header Tickets controls on the organiser profile in each page language.

Event-specific purchase buttons retain their own concert links.
Run without --check to update shared header data and static header links.
"""
import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
HEADER_JS = ROOT / 'assets/header.js'
PROFILE = 'https://eventmate.app/events/share/na-krilah-kohanna-koncert-vokalnoi-muziki-v-budinku-vcenih'
START, END = '/* tickets:start (tools/tickets.py) */', '/* tickets:end */'
BUTTON = re.compile(r'(<a class="btn btn-acc(?: mobile-ticket)?" href=")([^"]*)(")')


def strip_query(url):
    parts = urlsplit(url)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, '', ''))


def data_block():
    return f'{START}\nconst TICKET_PROFILE = {json.dumps(PROFILE)};\n{END}'


def pages():
    return [p for p in sorted(ROOT.rglob('*.html')) if not set(p.relative_to(ROOT).parts) & {'tools', 'docs', 'node_modules', '_site'}]


def language(path):
    return 'en' if path.relative_to(ROOT).parts[0] == 'en' else 'uk'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    script = HEADER_JS.read_text()
    current = re.search(re.escape(START) + r'.*?' + re.escape(END), script, re.S)
    if not current:
        sys.exit('assets/header.js: tickets data markers missing')
    allowed = {PROFILE}
    errors = []
    if args.check:
        if current[0] != data_block():
            errors.append('assets/header.js: ticket data out of date, run tools/tickets.py')
        for page in pages():
            for _, href, _ in BUTTON.findall(page.read_text()):
                if strip_query(href) not in allowed or urlsplit(href).query != f'locale={language(page)}':
                    errors.append(f'{page.relative_to(ROOT)}: header ticket link {href}')
        if errors:
            sys.exit('\n'.join(errors))
        print('ticket links ok')
        return
    HEADER_JS.write_text(script.replace(current[0], data_block()))
    target = PROFILE
    changed = 0
    for page in pages():
        source = page.read_text()
        updated = BUTTON.sub(lambda m: f'{m[1]}{target}?locale={language(page)}{m[3]}', source)
        if updated != source:
            page.write_text(updated)
            changed += 1
    print(f'header tickets: {target} ({changed} pages updated)')


if __name__ == '__main__':
    main()
