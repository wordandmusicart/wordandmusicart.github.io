#!/usr/bin/env python3
"""Web subsets of Fixel Text for word&music.

The full fonts (SIL OFL, MacPaw) live in tools/fonts-src/ and are not
deployed. This script writes assets/fonts/FixelText-*.woff2 with only
the characters and OpenType features the site uses: Latin, Latin-1 and
Latin Extended-A (names in French, Spanish, Italian, Polish...),
Ukrainian and Russian Cyrillic, punctuation and a few symbols. The name
table (copyright, licence) is kept whole.

    pip install fonttools brotli
    python3 tools/fonts.py          # rebuild subsets
    python3 tools/fonts.py --check  # fail if a character on a page is missing
"""
import glob, html, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'tools', 'fonts-src')
OUT = os.path.join(ROOT, 'assets', 'fonts')
FONTS = ('FixelText-Regular', 'FixelText-SemiBold')
UNICODES = ('U+0000-017F,U+02BC,U+02C6,U+02DA,U+02DC,U+0300-0301,'
            'U+0400-045F,U+0490-0491,U+2000-206F,U+20AC,U+20B4,U+2116,'
            'U+2122,U+2190-2193,U+2197,U+2212')
FEATURES = 'kern,liga,locl,ccmp,case,tnum,lnum,pnum,frac,sups,dnom'

def build():
    for name in FONTS:
        subprocess.run([sys.executable, '-m', 'fontTools.subset',
                        os.path.join(SRC, name + '.woff2'),
                        '--unicodes=' + UNICODES, '--layout-features=' + FEATURES,
                        '--name-IDs=*', '--name-languages=*', '--name-legacy',
                        '--notdef-outline', '--flavor=woff2',
                        '--output-file=' + os.path.join(OUT, name + '.woff2')], check=True)

def page_chars():
    text = ''
    for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        if os.sep + '.' in os.path.relpath(p, ROOT):
            continue
        s = open(p, encoding='utf-8').read()
        s = re.sub(r'<script.*?</script>|<style.*?</style>', '', s, flags=re.S)
        text += html.unescape(re.sub(r'<[^>]+>', ' ', s))
    return {c for c in text if ord(c) > 32}

def check():
    from fontTools.ttLib import TTFont
    chars, problems = page_chars(), []
    for name in FONTS:
        full = TTFont(os.path.join(SRC, name + '.woff2')).getBestCmap()
        sub = TTFont(os.path.join(OUT, name + '.woff2')).getBestCmap()
        lost = ''.join(sorted(c for c in chars if ord(c) in full and ord(c) not in sub))
        if lost:
            problems.append(f'{name}: missing {lost!r} (add to UNICODES and rebuild)')
    return problems

if __name__ == '__main__':
    if '--check' not in sys.argv:
        build()
    probs = check()
    print('\n'.join(probs) or 'fonts ok')
    sys.exit(1 if probs else 0)
