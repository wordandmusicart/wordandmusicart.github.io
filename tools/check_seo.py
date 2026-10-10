"""Check page metadata and Ukrainian/English SEO links before deployment."""

from collections import defaultdict
from html.parser import HTMLParser
import os
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(os.environ.get("SITE_ROOT", Path(__file__).resolve().parent.parent))
ORIGIN = "https://wordandmusic.art"
# Current-programme aliases share the stable named concert's SEO identity.
ALIASES = {"concerts/on-the-wings-of-love-25102026.html": "concerts/on-the-wings-of-love-24102026.html",
           "en/concerts/on-the-wings-of-love-25102026.html": "en/concerts/on-the-wings-of-love-24102026.html",
           "concert.html": "concerts/on-the-wings-of-love.html",
           "en/concert.html": "en/concerts/on-the-wings-of-love.html"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = ""
        self.title = ""
        self.h1 = ""
        self.in_head = False
        self.in_title = False
        self.in_h1 = False
        self.meta = {}
        self.og = {}
        self.alternates = {}
        self.alternate_entries = []
        self.canonicals = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "html":
            self.lang = attrs.get("lang", "")
        elif tag == "head":
            self.in_head = True
        elif tag == "title" and self.in_head:
            self.in_title = True
        elif tag == "h1":
            self.in_h1 = True
        elif tag == "meta":
            if attrs.get("name"):
                self.meta[attrs["name"]] = attrs.get("content", "")
            if attrs.get("property"):
                self.og[attrs["property"]] = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel") == "alternate":
            self.alternates[attrs.get("hreflang", "")] = attrs.get("href", "")
            self.alternate_entries.append(attrs)
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonicals.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False
        elif tag == "title":
            self.in_title = False
        elif tag == "h1":
            self.in_h1 = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if self.in_h1:
            self.h1 += data


def page_url(path):
    return "/" + path.relative_to(ROOT).as_posix()


def canonical_url(path):
    relative = path.relative_to(ROOT).as_posix()
    relative = ALIASES.get(relative, relative)
    if relative == "index.html":
        relative = ""
    elif relative == "en/index.html":
        relative = "en/"
    return ORIGIN + "/" + relative


def public_pages():
    return sorted(path for path in ROOT.rglob("*.html")
                  if not any(part.startswith(".") or part in {"_site", "node_modules", "tools"}
                             for part in path.relative_to(ROOT).parts))


def main():
    pages = public_pages()
    parsed = {}
    errors = []
    for path in pages:
        page = PageParser()
        page.feed(path.read_text(encoding="utf-8"))
        parsed[path] = page
        label = path.relative_to(ROOT).as_posix()
        description = page.meta.get("description", "")
        for name, value in (("language", page.lang), ("title", page.title),
                            ("description", description), ("h1", page.h1)):
            if not value.strip():
                errors.append(f"{label}: missing {name}")
        if page.lang not in ("uk", "en"):
            errors.append(f"{label}: unexpected language {page.lang!r}")
        if page.og.get("og:title") != page.title:
            errors.append(f"{label}: og:title differs from title")
        if page.og.get("og:description") != description:
            errors.append(f"{label}: og:description differs from description")
        image_url = urlparse(page.og.get("og:image", ""))
        if not image_url.netloc or not (ROOT / image_url.path.lstrip("/")).is_file():
            errors.append(f"{label}: missing Open Graph image")
        if path.name == "404.html":
            continue
        target = ALIASES.get(label, label)
        expected_uk = page_url(ROOT / target.removeprefix("en/"))
        expected_en = "/en" + expected_uk
        if path.name == "index.html":
            expected_uk, expected_en = "/", "/en/"
        for lang, expected in (("uk", expected_uk), ("en", expected_en)):
            actual = urlparse(page.alternates.get(lang, ""))
            if actual.path != expected or not actual.netloc:
                errors.append(f"{label}: invalid {lang} alternate")
            if not (ROOT / expected.lstrip("/") / "index.html" if expected.endswith("/")
                    else ROOT / expected.lstrip("/")).is_file():
                errors.append(f"{label}: missing {lang} page")
        if len(page.alternate_entries) != 3 or set(page.alternates) != {"uk", "en", "x-default"}:
            errors.append(f"{label}: expected exactly three language alternates")
        if page.alternates.get("x-default") != page.alternates.get("en"):
            errors.append(f"{label}: x-default alternate must point to the en page")
        expected = canonical_url(path)
        if page.canonicals != [expected]:
            errors.append(f"{label}: canonical must be {expected}")
        if page.og.get("og:url") != expected:
            errors.append(f"{label}: invalid og:url")
        for lang, href in page.alternates.items():
            if not href.startswith(ORIGIN + "/"):
                errors.append(f"{label}: wrong production host for {lang}")
        if any("noindex" in page.meta.get(name, "").lower() for name in ("robots", "googlebot", "bingbot")):
            errors.append(f"{label}: indexable page contains noindex")
    for field, getter in (("title", lambda p: p.title),
                          ("description", lambda p: p.meta.get("description", ""))):
        values = defaultdict(list)
        for path, page in parsed.items():
            if path.name != "404.html" and path.relative_to(ROOT).as_posix() not in ALIASES:
                values[(page.lang, getter(page))].append(path.relative_to(ROOT).as_posix())
        for (lang, value), matches in values.items():
            if value and len(matches) > 1:
                errors.append(f"duplicate {lang} {field}: {', '.join(matches)}")
    if errors:
        raise SystemExit("\n".join(errors))
    print(f"SEO metadata OK on {len(pages)} pages")


if __name__ == "__main__":
    main()
