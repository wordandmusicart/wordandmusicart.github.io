#!/usr/bin/env python3
"""Responsive images for word&music.

Rule: every raster <img>/<source> on the site is served through srcset.
The master file assets/img/<name>.jpg is kept at its original resolution;
this script writes <name>-320/-480/-720/-960/-1440/-2400.webp next to it (only
the widths smaller than the master) and rewrites srcset in every page.
Concert photos (assets/photo/<slug>/<name>.webp, the top step) get the
same smaller steps, made from the top step, and their srcset is rewritten.
Each <img> must carry a hand-written `sizes` that matches its layout.
Variants keep the master's colour profile, EXIF and XMP; only GPS is removed.

    python3 tools/images.py          # build variants + update HTML
    python3 tools/images.py --check  # fail if anything is missing
"""
import glob, os, re, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, 'assets', 'img')
WIDTHS = (320, 480, 720, 960, 1440, 2400)  # rusanivsky.com ladder + 320, 720
SKIP = ('og-',)  # social previews: fixed 1200x630, not shown on pages

def masters():
    for f in sorted(glob.glob(os.path.join(IMG, '*.jpg'))):
        name = os.path.basename(f)[:-4]
        if not name.startswith(SKIP):
            yield name, f

def variants(name, f):
    w, h = Image.open(f).size
    return w, h, [x for x in WIDTHS if x < w]

GPS_IFD = 34853

def strip_gps_xmp(x):
    s = x.decode('utf-8', 'ignore') if isinstance(x, bytes) else x
    s = re.sub(r'\s+exif:GPS\w+="[^"]*"', '', s)
    s = re.sub(r'<exif:GPS(\w+)[^>]*/>', '', s)
    s = re.sub(r'<exif:GPS(\w+)\b[^>]*>.*?</exif:GPS\1>', '', s, flags=re.S)
    return s.encode('utf-8')

def meta(im):
    """Metadata carried into every variant: colour profile, EXIF and XMP, without GPS."""
    out = {}
    if im.info.get('icc_profile'):
        out['icc_profile'] = im.info['icc_profile']
    ex = im.getexif()
    if len(ex):
        if GPS_IFD in ex:
            del ex[GPS_IFD]
        out['exif'] = ex.tobytes()
    if im.info.get('xmp'):
        out['xmp'] = strip_gps_xmp(im.info['xmp'])
    return out

def has_meta(path, want):
    info = Image.open(path).info
    return all(k in info for k in want)

def build():
    for name, f in masters():
        w, h, ws = variants(name, f)
        src = Image.open(f)
        m = meta(src)
        im = None
        for x in ws:
            out = os.path.join(IMG, f'{name}-{x}.webp')
            if (os.path.exists(out) and os.path.getmtime(out) >= os.path.getmtime(f)
                    and has_meta(out, m)):
                continue
            im = im or src.convert('RGB')
            im.resize((x, round(h * x / w)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6, **m)

PHOTO = os.path.join(ROOT, 'assets', 'photo')

def photos():
    """Concert photos: top step <name>.webp; yields (url base, path, width, smaller steps)."""
    for f in sorted(glob.glob(os.path.join(PHOTO, '*', '*.webp'))):
        if re.search(r'-\d+\.webp$', f):
            continue
        w = Image.open(f).size[0]
        yield '/' + os.path.relpath(f, ROOT)[:-5].replace(os.sep, '/'), f, w, [x for x in WIDTHS if x < w]

def build_photos():
    for url, f, w, ws in photos():
        src = None
        for x in ws:
            out = f[:-5] + f'-{x}.webp'
            if os.path.exists(out):
                continue
            src = src or Image.open(f)
            m = meta(src)
            h = src.size[1]
            src.convert('RGB').resize((x, round(h * x / w)), Image.LANCZOS).save(out, 'WEBP', quality=80, method=6, **m)

def srcset(name, f):
    w, _, ws = variants(name, f)
    return ', '.join([f'/assets/img/{name}-{x}.webp {x}w' for x in ws] + [f'/assets/img/{name}.jpg {w}w'])

TAG = re.compile(r'<(img|source)\b[^>]*>')
PHOTO_TAG = re.compile(r'<img\b[^>]*\ssrc="/assets/photo/[^"]*"[^>]*>')

def photo_srcsets():
    return {url: ', '.join([f'{url}-{x}.webp {x}w' for x in ws] + [f'{url}.webp {w}w'])
            for url, f, w, ws in photos()}

def fix_photo(m, _cache={}):
    t = m.group(0)
    if not _cache:
        _cache.update(photo_srcsets())
    u = re.search(r' src="(/assets/photo/[^"]*?)(?:-\d+)?\.webp"', t)
    if not u or u.group(1) not in _cache or ' srcset="' not in t:
        return t
    return re.sub(r' srcset="[^"]*"', f' srcset="{_cache[u.group(1)]}"', t)
def pages():
    return sorted(glob.glob(os.path.join(ROOT, '*.html')) + glob.glob(os.path.join(ROOT, '*', '*.html')) + glob.glob(os.path.join(ROOT, 'en', '*', '*.html')))

def rewrite(check):
    info = {n: f for n, f in masters()}
    problems = []
    for p in pages():
        s = open(p, encoding='utf-8').read()
        def fix(m):
            t = m.group(0)
            attr = 'src' if m.group(1) == 'img' else 'srcset'
            u = re.search(attr + r'="/assets/img/([\w-]+)\.jpg', t)
            if not u or u.group(1) not in info:
                return t
            name = u.group(1)
            want = srcset(name, info[name])
            if m.group(1) == 'img':
                t = re.sub(r' srcset="[^"]*"', '', t)
                t = t.replace(f'src="/assets/img/{name}.jpg"', f'src="/assets/img/{name}.jpg" srcset="{want}"')
            else:
                t = re.sub(r'srcset="[^"]*"', f'srcset="{want}"', t)
            if ' sizes="' not in t:
                problems.append(f'{os.path.relpath(p, ROOT)}: {name} has no sizes')
            return t
        new = TAG.sub(fix, s)
        new = PHOTO_TAG.sub(fix_photo, new)
        if new != s:
            if check:
                problems.append(f'{os.path.relpath(p, ROOT)}: srcset out of date')
            else:
                open(p, 'w', encoding='utf-8').write(new)
    if check:
        for url, f, w, ws in photos():
            for x in ws:
                v = f[:-5] + f'-{x}.webp'
                if not os.path.exists(v):
                    problems.append(f'missing {os.path.relpath(v, ROOT)}')
                elif not has_meta(v, meta(Image.open(f))):
                    problems.append(f'{os.path.relpath(v, ROOT)} lost metadata')
        for name, f in masters():
            for x in variants(name, f)[2]:
                v = os.path.join(IMG, f'{name}-{x}.webp')
                if not os.path.exists(v):
                    problems.append(f'missing {name}-{x}.webp')
                elif not has_meta(v, meta(Image.open(f))):
                    problems.append(f'{name}-{x}.webp lost metadata')
    return problems

if __name__ == '__main__':
    check = '--check' in sys.argv
    if not check:
        build()
        build_photos()
    probs = rewrite(check)
    print('\n'.join(probs) or 'images ok')
    sys.exit(1 if probs else 0)
