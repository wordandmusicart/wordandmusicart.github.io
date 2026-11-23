#!/usr/bin/env python3
"""Render the «Команда» / "Team" pages (team.html, en/team.html) from assets/team.json.

An entry is either {"artist": "<id>"} — name, role and circle crop come from
assets/artists.json, so a caption or crop never differs from the Artists page —
or a full record (id, name, role, portrait) for people who do not perform.
The shell (head, header, footer) is taken from the Artists page.

    python3 tools/build_team.py          # write both pages
    python3 tools/build_team.py --check  # fail if a page is out of date
"""
import json
import re
import sys

from build_artists import ESC, ROOT, photograph

COPY = {
    'uk': {'title': 'Команда word&music', 'heading': 'Команда', 'label': 'Люди word&music',
           'description': 'Команда word&music: '},
    'en': {'title': 'The word&music Team', 'heading': 'Team', 'label': 'The people of word&music',
           'description': 'The word&music team: '},
}


def people():
    artists = {a['id']: a for a in json.loads((ROOT / 'assets/artists.json').read_text())}
    return [artists[t['artist']] if 'artist' in t else t
            for t in json.loads((ROOT / 'assets/team.json').read_text())]


def row(person, lang):
    return (f'<article class="artist-row with-portrait" id="{person["id"]}">\n'
            f'{photograph(person, lang)}<div class="artist-info"><h2 class="tem">{ESC(person["name"][lang])}</h2>'
            f'<p>{ESC(person["role"][lang], quote=False)}</p></div>\n</article>')


def render(lang):
    copy = COPY[lang]
    team = people()
    prefix = '/en' if lang == 'en' else ''
    shell = (ROOT / prefix.lstrip('/') / 'artists.html').read_text()
    head, rest = shell.split('<main class="artists-page">')
    tail = rest.split('</main>', 1)[1]
    description = copy['description'] + ', '.join(p['name'][lang] for p in team) + '.'
    current = f'<a href="{prefix}/artists.html" aria-current="page">'
    link = f'<a href="{prefix}/team.html">'
    assert head.count(current) == 1 and head.count(link) == 1, 'unexpected navigation on the Artists page'
    head = head.replace(link, f'<a href="{prefix}/team.html" aria-current="page">')
    head = head.replace(current, '<a href="@artists">').replace('artists.html', 'team.html')
    head = head.replace('@artists', f'{prefix}/artists.html')
    head = re.sub(r'<title>.*?</title>', lambda m: f'<title>{ESC(copy["title"])}</title>', head)
    head = re.sub(r'(<meta (?:name="description"|property="og:description") content=")[^"]*', lambda m: m[1] + ESC(description), head)
    head = re.sub(r'(<meta property="og:title" content=")[^"]*', lambda m: m[1] + ESC(copy['title']), head)
    body = (f'<main class="artists-page">\n<div class="list-head artists-intro wrap"><div><div class="meta muted">{ESC(copy["label"])}</div>'
            f'<h1 class="tem">{copy["heading"]}</h1></div></div>\n'
            '<section class="artist-group team-group wrap"><div class="artist-roster">'
            + '\n'.join(row(p, lang) for p in team) + '</div></section>\n</main>')
    return head + body + tail


def main():
    stale = []
    for lang, name in (('uk', 'team.html'), ('en', 'en/team.html')):
        path = ROOT / name
        page = render(lang)
        if not path.exists() or path.read_text() != page:
            stale.append(name)
            if '--check' not in sys.argv:
                path.write_text(page)
    if '--check' in sys.argv and stale:
        sys.exit('Run python3 tools/build_team.py: out of date ' + ', '.join(stale))
    print('team ok' if not stale else 'updated ' + ', '.join(stale))


if __name__ == '__main__':
    main()
