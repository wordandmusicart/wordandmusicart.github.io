# SEO handoff for word&music

Current site: `test.rusanivsky.com`, intentionally excluded from indexing.
Run `python3 tools/check_seo.py` before every release. It checks titles,
descriptions, H1, Open Graph and both language URLs on all 35 pages.

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
