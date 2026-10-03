# Circular portraits and complete artist catalogue — 3 October 2026

Scope: balance the existing circular photographs through presentation crops;
add the owner's identified Karina Lysak photograph; include every participant
already credited on current, announced and archive programme pages in both
artist directories. Preserve original photographs, spelling, programme roles,
order, rectangular programme portraits, typography and colours.

Framing: optically similar head-and-shoulders scale, full heads and useful
headroom where the source photograph permits, eyes around the upper-middle of
the circle. Existing poster details are constrained by their original circular
artwork; do not invent missing pixels or expose the printed rim.

The attributed catalogue remains `assets/artists.json`. `portrait.crop` defines
circle framing in displayed source pixels. The author's `circle_crop` is
separate from his existing rectangular directory image. Repeated programme
circles use these same views; featured rectangular programme images remain
unchanged. Database/API and additional dependencies: N/A.

Five additions: Maksym Hara, Iryna Shelest, Yuliia Pavlovska, Karina Lysak and
Oleksii Maliovanyi. Names and roles come from the existing bilingual programme
for On the Wings of Love. Its existing directory participants gain programme
links; Dariia Pohorila remains the same existing Daria Pohorila record, retaining
the catalogue's spelling. Catalogue total: 34 people, including the author.

Karina: owner-supplied `20260520_131322.jpg`; byte-identical copies are stored
as `assets/img/karina-lysak.jpg` and in the concert's existing Drive photograph
folder. SHA-256: `6bb48e5ce810e33b5aafe11e76ba77ebe32ac9a7e69bb833d134f33f12e6c5f8`.
Raw dimensions are 4080×3060 with EXIF orientation 6; displayed dimensions are
3060×4080. Responsive WebP derivatives bake in this rotation while retaining
other metadata; the original JPEG is unchanged. Four independent acceptance
tests first demonstrated three failures, then passed after the image-pipeline
fix. This gate also runs in the Pages deployment workflow.

Independent final review found no blockers: all identities and source links
are present, circle crops agree across pages, programme text and rectangles
are preserved, and all six upright derivatives retain the original's metadata.
Local gates passed: portrait/artist/announced-concert/date checks, archive and
venue checks, responsive images, fonts, structured data, SEO (47 pages),
deterministic catalogue rebuild and whitespace. Browser inspection covered
390px mobile and desktop, UA/EN, light/dark, with no horizontal overflow.

Owner correction — 3 October: Albina Holenach was still too distant and offset
to the right; Oleksii Maliovanyi sat too low with excessive space above his
head. Their source views are now (375,620,1000) and (175,50,300), respectively.
The same crops apply to the bilingual directory and their programme circles
in Winter Extravaganza and On the Wings of Love. Independent screenshot/diff
review found no blockers: balanced centring, full hair and no glove at Oleksii's
right edge. Original files, programme text and rectangular images are unchanged.
