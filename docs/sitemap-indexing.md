# Production sitemap and indexing

Scope: make all public canonical Ukrainian/English pages discoverable in an automatically checked sitemap; submit it through the existing verified Google Search Console property. Actual crawling, canonical selection and indexing remain Google's decisions.

Acceptance:

1. Generate `sitemap.xml` from public HTML metadata, containing every unique indexable canonical URL on `https://wordandmusic.art/`. Exclude 404 and canonical aliases. Root home URLs are `/` and `/en/`.
2. Each listed URL has reciprocal `uk`, `en` and `x-default` XHTML alternate links matching the page head. Every canonical resolves to a public source page, is self-canonical there, and has no `noindex` directive.
3. Canonical contract v2: `concert.html` and its English twin remain usable current-programme aliases, but their canonical, Open Graph URL, structured event URL and SEO language links point to the stable named programme. This replaces the previous self-canonical contract for these two aliases only, because their programme content duplicates the named concert. Visible content and navigation are preserved.
4. `robots.txt` permits public crawling and declares the production sitemap. No invented `lastmod`, `priority` or `changefreq` values.
5. CI rejects missing/stale/duplicate sitemap entries, wrong hosts, invalid canonical targets and broken language pairs before deploy. Check all sitemap URLs and metadata over live HTTPS after release.
6. Resubmit the sitemap in Search Console, inspect key new concert URLs and request indexing when available. Record the observed submission result and indexing status without claiming that submission guarantees indexing.
7. Google-InspectionTool and GoogleOther retain the requested language URL and schema language, as Googlebot already does. Human location/device-language defaults and remembered language choices continue to work. The script cache version is updated on every public page. The artist generator copies the current page head, including this version.

Implementation: a standard-library Python generator/checker and existing static HTML; no database/API or backend health checks are applicable. Independent acceptance tests precede implementation; the final artifact is independently reviewed.

Primary documentation: [Google sitemap guidance](https://developers.google.com/search/docs/crawling-indexing/sitemaps/build-sitemap), [canonical consolidation](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [localized versions](https://developers.google.com/search/docs/specialty/international/localized-versions).

Live verification on 2026-10-03 revealed that Google-InspectionTool was redirected from Ukrainian to English by the device-language script. The tool's official user-agent has no `bot` substring. Its token and GoogleOther are now explicit crawler exceptions; [Google's official crawler list](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) confirms both. The event passed Google's live validation with only the optional `offers.validFrom` warning; no sales-opening date was supplied, so no date is invented.
