# Mobile concert actions, 2026-10-03

Owner's screenshots show a missing fixed ticket bar on the upcoming concert, an oversized date, and hero Programme/Performers buttons duplicating the section navigation.

Acceptance:

- Upcoming current and named programme pages, UA/EN: the existing glass ticket bar stays fixed at the viewport bottom on mobile, including after scrolling to the footer. It uses the source-backed October 15 ticket URL with the matching locale and displays 15.10 and 18:00–19:30. Stack the date and time in two lines to fit narrow screens. Keep the bar outside main so page motion does not create its fixed containing block.
- Archive pages retain no event-specific purchase bar. Desktop retains its existing ticket/section controls and hides the mobile bar.
- Date, Time and Price in every concert facts block share one responsive font rule. Values and currency remain unchanged; no line wrapping or overflow is introduced.
- At the existing mobile breakpoint (900px), hide hero Programme/Performers buttons that duplicate subnav links. Keep the subnav and hero ticket button. Hide a programme-only CTA container entirely on mobile so it leaves no empty margin. Desktop controls remain unchanged.
- Retain mobile footer clearance for the fixed bar and safe-area inset. Bump shared CSS on all public pages.

This is a reversible presentation correction; database/API contracts and backend health checks are N/A. Independently authored acceptance checks cover fixed positioning, ticket URL, facts sizing, duplicate controls and archive exclusions. Chromium and WebKit visual checks and production verification follow review and deployment.
