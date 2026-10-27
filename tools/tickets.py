#!/usr/bin/env python3
"""Keep header Tickets controls consistent with the current concert state.

There are currently no upcoming concerts, so static ticket controls are removed.
Run without --check to update shared header data and static header links.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEADER_JS = ROOT / 'assets/header.js'
PROFILE = None  # No upcoming concerts (owner request, 27 Oct 2026).
START, END = '/* tickets:start (tools/tickets.py) */', '/* tickets:end */'
BUTTON = re.compile(r'<a class="btn btn-acc(?: mobile-ticket)?"[^>]*>.*?</a>', re.S)


def data_block():
    return f'{START}\nconst TICKET_PROFILE = {json.dumps(PROFILE)};\n{END}'


def pages():
    return [p for p in sorted(ROOT.rglob('*.html')) if not set(p.relative_to(ROOT).parts) & {'tools', 'docs', 'node_modules', '_site'}]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    script = HEADER_JS.read_text()
    current = re.search(re.escape(START) + r'.*?' + re.escape(END), script, re.S)
    if not current:
        sys.exit('assets/header.js: tickets data markers missing')
    errors = []
    if args.check:
        if current[0] != data_block():
            errors.append('assets/header.js: ticket data out of date, run tools/tickets.py')
        for page in pages():
            if BUTTON.search(page.read_text()):
                errors.append(f'{page.relative_to(ROOT)}: header tickets present without an upcoming concert')
        if errors:
            sys.exit('\n'.join(errors))
        print('ticket links ok')
        return
    HEADER_JS.write_text(script.replace(current[0], data_block()))
    changed = 0
    for page in pages():
        source = page.read_text()
        updated = BUTTON.sub('', source)
        if updated != source:
            page.write_text(updated)
            changed += 1
    print(f'header tickets hidden: no upcoming concerts ({changed} pages updated)')


if __name__ == '__main__':
    main()
