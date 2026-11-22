#!/usr/bin/env python3
"""Sync the header ticket buttons with the current concert in each language."""
import argparse
import re
import sys
from urllib.parse import urlsplit

from check_seo import ROOT, canonical_url, public_pages

BUTTON = re.compile(r'(<a class="btn btn-acc(?: mobile-ticket)?") href="[^"]*"(?: target="_blank" rel="noopener")?>')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    errors = []
    for page in public_pages():
        prefix = 'en/' if page.relative_to(ROOT).parts[0] == 'en' else ''
        href = urlsplit(canonical_url(ROOT / prefix / 'concert.html')).path
        source = page.read_text()
        updated, count = BUTTON.subn(lambda match: f'{match[1]} href="{href}">', source)
        if count != 2:
            errors.append(f'{page.relative_to(ROOT)}: expected desktop and mobile header ticket buttons')
        elif updated != source:
            if args.check:
                errors.append(f'{page.relative_to(ROOT)}: run tools/tickets.py to update header links')
            else:
                page.write_text(updated)
    if errors:
        sys.exit('\n'.join(errors))
    print('header ticket links ok')


if __name__ == '__main__':
    main()
