#!/usr/bin/env python3
"""Render the bilingual artists directory from its attributed content manifest.

Portrait crops are fixed details of explicitly labelled artwork, never matches
between unlabelled faces. All original images remain unchanged. A null portrait
is intentionally a text-only entry, not an invented or anonymous replacement.
"""
from pathlib import Path
import html
import json
import re

ROOT = Path(__file__).resolve().parents[1]
ARTISTS = json.loads((ROOT / 'assets/artists.json').read_text())
ESC = html.escape
COPY = {
    'uk': {'title':'Артисти word&music — виконавці та автор проєкту', 'description':'Голоси, музиканти та автор word&music. Учасники концертів проєкту, фотографії та концертні програми.', 'heading':'Артисти', 'intro':'Вокалісти, інструменталісти й художнє слово в концертах word&music.', 'author':'Художнє слово', 'vocal':'Голоси', 'music':'Музиканти', 'concerts':'Концерти', 'author_text':'Художнє слово в концертних програмах word&music. У концерті «Музика душі і серця» — також переклад арій українською.', 'author_link':'Слово у концертних програмах', 'label':'Люди word&music', 'nav_label':'Розділи сторінки'},
    'en': {'title':'word&music Artists — Performers and Project Author', 'description':'The voices, musicians and author of word&music. Meet the concert performers through photographs and programmes.', 'heading':'Artists', 'intro':'Vocalists, instrumentalists and spoken word in word&music concerts.', 'author':'Spoken word', 'vocal':'Voices', 'music':'Musicians', 'concerts':'Concerts', 'author_text':'Spoken word in the concert programmes of word&music. For Music of Soul and Heart, he also translated arias into Ukrainian.', 'author_link':'Words in our concert programmes', 'label':'The people of word&music', 'nav_label':'Page sections'},
}

def local(source, lang):
    return '/' + ('en/' if lang == 'en' else '') + source.lstrip('/')

def photograph(a, lang, featured=False):
    p = a['portrait']
    if not p:
        return '<span class="artist-portrait artist-placeholder" aria-hidden="true"></span>'
    label = p.get('label', {}).get(lang, a['name'][lang])
    alt = a['name'][lang] + (' — ' + label if 'label' in p else '')
    style = ''
    crop_class = ''
    source_crop = p.get('crop') if featured else p.get('circle_crop', p.get('crop'))
    if source_crop:
        crop = dict(source_crop)
        # Inset the source's decorative rim without altering the original artwork.
        inset = crop['size'] * p.get('rim_inset', 0)
        crop['x'] += inset
        crop['y'] += inset
        crop['size'] -= 2 * inset
        style = f'width:{p["width"] / crop["size"] * 100:.5f}%;max-width:none;height:auto;left:{-crop["x"] / crop["size"] * 100:.5f}%;top:{-crop["y"] / crop["size"] * 100:.5f}%'
        crop_class = ' artwork-detail'
    else:
        style = 'object-position:' + p.get('position', '50% 25%')
    base = p['src'].rsplit('.', 1)[0]
    variants = [f'{base}-{width}.webp {width}w' for width in (320,480,720,960,1440,2400) if width < p['width'] and (ROOT / f'{base.lstrip(chr(47))}-{width}.webp').exists()]
    srcset = ', '.join(variants + [f'{p["src"]} {p["width"]}w'])
    rendered = p['width'] / crop['size'] * 168 if source_crop else 168
    sizes = '(max-width:720px) calc(100vw - 40px), 43vw' if featured else f'{rendered:.0f}px'
    image = f'<img src="{ESC(p["src"])}" srcset="{ESC(srcset)}" sizes="{sizes}" alt="{ESC(alt)}" width="{p["width"]}" height="{p["height"]}" loading="{"eager" if featured else "lazy"}" decoding="async" draggable="false" style="{style}">'
    if featured:
        return '<div class="artist-author-photo">' + image + '</div>'
    return f'<span class="artist-portrait{crop_class}">{image}</span>'

def concert_links(a, lang):
    sources = [s for s in a['sources'] if s.split('#')[0] != 'video.html']
    links=[]
    for source in sources:
        path = ROOT / ('en/' if lang == 'en' else '') / source.split('#')[0]
        title = re.search(r'<h1[^>]*>(.*?)</h1>', path.read_text(), re.S)
        title = re.sub('<[^>]+>', '', title[1]) if title else COPY[lang]['concerts']
        links.append(f'<a href="{local(source,lang)}">{title}</a>')
    return f'<details class="artist-concerts"><summary>{COPY[lang]["concerts"]} <span class="faint">{len(links)}</span></summary><div>{"".join(links)}</div></details>'

def artist_row(a, lang):
    return f'''<article class="artist-row{' with-portrait' if a['portrait'] else ''}" id="{a['id']}" data-artist="{a['id']}">
{photograph(a,lang)}<div class="artist-info"><h3 class="tem">{ESC(a['name'][lang])}</h3><p>{ESC(a['role'][lang])}</p>{concert_links(a,lang)}</div>
</article>'''

def render(lang):
    copy=COPY[lang]
    template=(ROOT / ('en/concerts.html' if lang == 'en' else 'concerts.html')).read_text()
    head=template.split('<main>')[0]
    head=re.sub(r'<title>.*?</title>', '<title>'+ESC(copy['title'])+'</title>',head)
    head=re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m:m[1]+ESC(copy['description']),head)
    head=re.sub(r'(<meta property="og:title" content=")[^"]*',lambda m:m[1]+ESC(copy['title']),head)
    # Only page metadata and language switch links change; shared navigation
    # is composed below so a rebuild never inherits an incorrect active item.
    head=head.replace('wordandmusic.art/concerts.html','wordandmusic.art/artists.html').replace('wordandmusic.art/en/concerts.html','wordandmusic.art/en/artists.html')
    head=head.replace('href="/en/concerts.html" hreflang','href="/en/artists.html" hreflang').replace('href="/concerts.html" hreflang','href="/artists.html" hreflang')
    nav=[('concerts.html','Концерти','Concerts'),('artists.html','Артисти','Artists'),('photo.html','Фото','Photo'),('video.html','Відео','Video'),('index.html#about','Про проєкт','About'),('index.html#contacts','Контакти','Contacts')]
    links=''.join(f'<a href="{local(path,lang)}"'+(' aria-current="page"' if path=='artists.html' else '')+'>'+ (en if lang=='en' else uk)+'</a>' for path,uk,en in nav)
    nav_match = re.search(r'(<nav id="nav"[^>]*>)(.*?)(</nav>)', head, re.S)
    mobile = nav_match[2][nav_match[2].index('<div class="mobile-lang'): ] if '<div class="mobile-lang' in nav_match[2] else ''
    head = head[:nav_match.start()] + nav_match[1] + links + mobile + nav_match[3] + head[nav_match.end():]
    head=head.replace('</head>','<link rel="stylesheet" href="/assets/artists.css?v=8">\n</head>')
    body=f'''<main class="artists-page">
<div class="list-head artists-intro wrap"><div><div class="meta muted">{copy['label']}</div><h1 class="tem">{copy['heading']}</h1></div><div class="artists-intro-bottom"><p>{copy['intro']}</p><nav aria-label="{copy['nav_label']}"><a href="#voices">{copy['vocal']}</a><a href="#musicians">{copy['music']}</a><a href="#author">{copy['author']}</a></nav></div></div>
'''
    for group,anchor in [('vocal','voices'),('music','musicians'),('author','author')]:
        people=[a for a in ARTISTS if a['group']==group]
        # Keep the source order: existing featured artists first, followed by
        # the archive roster. No ranking or fabricated biographical ordering.
        body+=f'<section class="artist-group wrap" id="{anchor}" aria-labelledby="{anchor}-title"><div class="artist-group-heading"><h2 class="tem" id="{anchor}-title">{copy[group]}</h2><span class="meta muted">{len(people)}</span></div><div class="artist-roster">'
        body+='\n'.join(artist_row(a,lang) for a in people)+'</div></section>\n'
    body+='</main>'
    tail=template.split('</main>',1)[1]
    # Directory uses native details for programme links; no filtering script.
    tail=re.sub(r'<script>.*?</script>', '', tail, flags=re.S)
    return head+body+tail

if __name__ == '__main__':
    for language in ('uk','en'):
        destination=ROOT / ('en/artists.html' if language=='en' else 'artists.html')
        destination.write_text(render(language))
        print(destination.relative_to(ROOT))
