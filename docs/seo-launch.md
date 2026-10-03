# SEO handoff for word&music

Production site: `https://wordandmusic.art/`, open to indexing. Run
`python3 tools/check_seo.py` and `python3 tools/sitemap.py --check` before every
release. Metadata checks cover every public page; the sitemap is generated
from their canonical and reciprocal language links. After adding a page, run
`python3 tools/sitemap.py` and include the resulting sitemap in the release.

The current programme aliases use the named concert's canonical URL; see
`sitemap-indexing.md` for the current production contract. `404.html` remains
excluded with noindex. Search Console is the source for observed indexing
status; a deployment or sitemap submission does not prove indexing.

The following is the historical staging-to-production checklist:

Before publishing this site through `wordandmusicart` at `wordandmusic.art`:

1. Replace `test.rusanivsky.com` with the production host in `og:url`,
   `og:image` and both `hreflang` links. Keep the UA and EN pairs reciprocal.
2. Add a self-referencing canonical URL to each indexable page. Use `/` and
   `/en/` for the two home pages.
3. Remove staging `noindex,nofollow` from the HTML pages and replace the
   staging `robots.txt` rule `Disallow: /` with production rules.
4. Add a production `sitemap.xml` with only canonical, indexable URLs.
5. Verify the deployed HTML and assets over HTTPS, then submit the sitemap
   and inspect key URLs in Google Search Console. A successful deploy does
   not prove indexing.

Do not change image files or metadata as part of this handoff.
