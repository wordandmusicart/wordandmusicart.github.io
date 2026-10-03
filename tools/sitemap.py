#!/usr/bin/env python3
"""Generate/check the canonical production sitemap from public page metadata."""
import argparse
import xml.etree.ElementTree as ET
from urllib.parse import urlsplit
from urllib.robotparser import RobotFileParser

from check_seo import ROOT, ORIGIN, ALIASES, PageParser, canonical_url, public_pages

SM = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML = "http://www.w3.org/1999/xhtml"
ET.register_namespace("", SM)
ET.register_namespace("xhtml", XHTML)


def build():
    pages = {}
    for path in public_pages():
        if path.name == "404.html":
            continue
        doc = PageParser()
        doc.feed(path.read_text(encoding="utf-8"))
        if doc.canonicals != [canonical_url(path)]:
            raise ValueError(f"{path.relative_to(ROOT)}: unexpected canonical")
        if any("noindex" in doc.meta.get(name, "").lower()
               for name in ("robots", "googlebot", "bingbot")):
            raise ValueError(f"{path.relative_to(ROOT)}: noindex on a public page")
        if len(doc.alternate_entries) != 3 or set(doc.alternates) != {"uk", "en", "x-default"}:
            raise ValueError(f"{path.relative_to(ROOT)}: invalid language links")
        pages[path] = doc
    if not pages:
        raise ValueError("No public pages found")
    unique = {}
    for path, doc in pages.items():
        url = doc.canonicals[0]
        parsed = urlsplit(url)
        target = ROOT / (parsed.path.lstrip("/") + "index.html" if parsed.path.endswith("/")
                         else parsed.path.lstrip("/"))
        if target not in pages or pages[target].canonicals != [url] or canonical_url(target) != url:
            raise ValueError(f"{path.relative_to(ROOT)}: canonical target is not self-canonical public HTML")
        if doc.alternates != pages[target].alternates or doc.og.get("og:url") != url:
            raise ValueError(f"{path.relative_to(ROOT)}: conflicting canonical metadata")
        if path != target and path.relative_to(ROOT).as_posix() not in ALIASES:
            raise ValueError(f"{path.relative_to(ROOT)}: undeclared canonical alias")
        for lang in ("uk", "en"):
            twin_url = doc.alternates[lang]
            u = urlsplit(twin_url)
            if (u.scheme, u.netloc) != ("https", "wordandmusic.art") or u.query or u.fragment:
                raise ValueError(f"{url}: invalid alternate URL")
            twin = ROOT / (u.path.lstrip("/") + "index.html" if u.path.endswith("/") else u.path.lstrip("/"))
            if twin not in pages or pages[twin].lang != lang or pages[twin].canonicals != [twin_url] or pages[twin].alternates != doc.alternates:
                raise ValueError(f"{url}: language links are not reciprocal canonical targets")
        if doc.alternates[doc.lang] != url or doc.alternates["x-default"] != doc.alternates["en"]:
            raise ValueError(f"{url}: incorrect self/default language link")
        unique[url] = doc.alternates
    robots = (ROOT / "robots.txt").read_text()
    declarations = [line.split(":", 1)[1].strip() for line in robots.splitlines()
                    if line.lower().startswith("sitemap:")]
    if declarations != [ORIGIN + "/sitemap.xml"]:
        raise ValueError("robots.txt must declare exactly the production sitemap")
    rules = RobotFileParser()
    rules.parse(robots.splitlines())
    if any(not rules.can_fetch(agent, url) for agent in ("*", "Googlebot") for url in unique):
        raise ValueError("robots.txt blocks a canonical page")
    tree = ET.Element(f"{{{SM}}}urlset")
    for url, alternates in sorted(unique.items()):
        entry = ET.SubElement(tree, f"{{{SM}}}url")
        ET.SubElement(entry, f"{{{SM}}}loc").text = url
        for lang in ("uk", "en", "x-default"):
            ET.SubElement(entry, f"{{{XHTML}}}link", rel="alternate", hreflang=lang, href=alternates[lang])
    ET.indent(tree, space="  ")
    return '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(tree, encoding="unicode") + "\n", len(unique)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report stale sitemap without writing")
    args = parser.parse_args()
    try:
        expected, count = build()
        target = ROOT / "sitemap.xml"
        if args.check:
            if not target.is_file() or target.read_text() != expected:
                raise ValueError("Sitemap is stale; run python3 tools/sitemap.py")
        else:
            target.write_text(expected, encoding="utf-8")
    except (ValueError, OSError) as error:
        raise SystemExit(str(error))
    print(f"Sitemap {'OK' if args.check else 'generated'}: {count} canonical URLs")


if __name__ == "__main__":
    main()
