#!/usr/bin/env python3
"""Style guard: keeps new pages inside the design system (docs/design-system.md).

Fails when a change
  - adds a hand-written inline style (generated portrait/photo crops are exempt),
  - uses a colour outside the :root tokens,
  - gives a hover/interactive transition its own timing instead of the
    --hover / --zoom / --ease tokens,
  - leaves pages on different site.css / header.js / lang.js versions,
  - adds a UA page without its EN twin (or the reverse).
Inline styles are a ratchet: the count may only go down (update BASELINE when it does).

    python3 tools/check_style.py
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
# Hand-written inline styles that existed on 3 Oct 2026. Lower it, never raise it.
BASELINE = 147
GENERATED = [
    re.compile(r'^width:-?[\d.]+%;(?:max-width:none;height:auto|height:auto;max-width:none);left:-?[\d.]+%;top:-?[\d.]+%$'),  # build_artists / sync_programme_portraits crops
    re.compile(r'^object-position:[^;]+$'),        # photo preview framing (heads never cut)
    re.compile(r'^container-type:size$'),
    re.compile(r'^--[\w-]+:[^;]+$'),               # data-driven custom properties
]
# Motion that is not a hover: header hide/show, burger, menu reveal, logo breathing.
MOTION_ALLOWED = re.compile(r'(700ms cubic-bezier\(\.4,0,\.2,1\)|2[48]0ms cubic-bezier\(\.22,1,\.36,1\)|200ms cubic-bezier\(\.22,1,\.36,1\)|2400ms|1400ms)')


def pages():
    return [p for p in sorted(ROOT.rglob('*.html'))
            if not set(p.relative_to(ROOT).parts) & {'tools', 'docs', 'node_modules', '_site'}]


def main():
    errors = []
    inline = []
    versions = {name: Counter() for name in ('site.css', 'header.js', 'lang.js')}
    for page in pages():
        text = page.read_text()
        rel = page.relative_to(ROOT).as_posix()
        for style in re.findall(r'style="([^"]*)"', text):
            if not any(g.match(style.strip().rstrip(';')) for g in GENERATED):
                inline.append(f'{rel}: style="{style}"')
        for name in versions:
            for v in re.findall(re.escape(name) + r'\?v=(\d+)', text):
                versions[name][v] += 1
        if rel != '404.html':
            twin = ROOT / (rel[3:] if rel.startswith('en/') else 'en/' + rel)
            if not twin.exists():
                errors.append(f'{rel}: missing {"UA" if rel.startswith("en/") else "EN"} twin {twin.relative_to(ROOT)}')
    if len(inline) > BASELINE:
        errors.append(f'{len(inline)} hand-written inline styles (baseline {BASELINE}). Use a class from '
                      'docs/design-system.md instead; newest:\n  ' + '\n  '.join(inline[-(len(inline) - BASELINE):][:10]))
    for name, counter in versions.items():
        if len(counter) > 1:
            errors.append(f'{name}: pages use different versions {dict(counter)}; bump it on every page')
    for css in sorted((ROOT / 'assets').glob('*.css')):
        source = re.sub(r'/\*.*?\*/', '', css.read_text(), flags=re.S)
        outside_tokens = re.sub(r':root[^{]*\{[^}]*\}', '', source)
        for colour in sorted(set(re.findall(r'#[0-9A-Fa-f]{3,8}\b', outside_tokens))):
            errors.append(f'{css.name}: colour {colour} outside the :root tokens')
        for value in re.findall(r'transition:([^;}]+)', source):
            if value.strip() in ('none', 'none !important') or 'var(--' in value or MOTION_ALLOWED.search(value):
                continue
            errors.append(f'{css.name}: transition "{value}" — use var(--hover)/var(--zoom) var(--ease)')
    if errors:
        sys.exit('\n'.join(errors))
    print(f'style ok ({len(inline)}/{BASELINE} hand-written inline styles)')


if __name__ == '__main__':
    main()
