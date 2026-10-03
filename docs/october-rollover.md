# October concert rollover — 3 October 2026

Owner request: group date, time and price into three columns; show known concert times as a range throughout the site; feature 15 October on home and archive 3 October now.

## Contract and acceptance

- A1: Home next concert is On the Wings of Love, 15 October 2026, 18:00–19:30, Actor's House, with its confirmed ticket URL. Both languages use existing approved artwork and content.
- A2: Current programme `/concert.html` and its EN twin feature the same 15 October concert; the existing named programme remains reachable.
- A3: Vivre, Aimer, Rêver… moves to `/concerts/vivre-aimer-rever.html` and its EN twin, retains all programme/artists/venue/artwork, and appears in the archive rather than upcoming. It has no event ticket CTA, on-sale status, sticky purchase bar or MusicEvent/offers.
- A4: Ticketed facts top row has Date / Time / Price (three columns). Time is a single visible range, not separate start and end cells. Archived pages without supplied prices use Date / Time; unknown historical times stay omitted.
- A5: Known time ranges are used in home/list/related/subnav/sticky bars, text metadata and programme facts. Existing supported endpoints stay unchanged: 3 October 16:00–17:00; 15 October 18:00–19:30; historical known ends already supplied on pages. Embedded artwork remains the approved original.
- A6: JSON-LD reads startDate and endDate separately from the visible range. Both upcoming programme routes retain the confirmed 250–400 UAH range and minimum Offer price 250. Archived concerts carry no MusicEvent.
- A7: UA/EN links, artist source references, sitemap, responsive assets and site CSS cache version are synchronized. No fabricated dates, prices or historical times; no unrelated layout/content redesign.
- A8: Browser checks verify readable non-overflowing facts at desktop and mobile widths; live site checks follow deployment.

Implementation: static HTML rollover and shared facts CSS; extend structured-data fact parser to Time. No API/database change (N/A). Existing CI checks plus independent rollover acceptance tests gate publication. Preserve previous pages and assets in Git history. Success is deployed bilingual site with correct next/archived separation and readable time ranges. Supersedes AGENTS.md start-only display rule for this authorized task; rules file itself is not edited.
