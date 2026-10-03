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

Full optical pass and archive hierarchy — 3 October 2026

Owner identified remaining imbalance in Dariia Pohorila and requested a complete
pass, plus rectangular principal-performer tiles on old concert pages following
the new programmes. This supersedes the earlier instruction to preserve all
existing programme circle shapes. Text, photographs, colours and typography
remain unchanged; added dependencies and database/API contracts are N/A.

All 25 unique photographic/artwork views and 156 pre-change repeated circles
were inventoried. Ten additional photographic crops were refined together,
including Dariia: comparable facial scale, full available hair, eye placement
and useful headroom, verified beside the retained portraits rather than alone.
Poster-derived Hanna Semets, Makar Rusanivsky and Taras Kapran remain constrained
by their original printed circular artwork; no surrounding pixels are invented.

All 12 archive programmes now use equal 4:5 principal cards, in both languages.
Chamber ensembles of up to four retain a shared row including spoken word.
Christmas Kaleidoscope and Heartstrings separate existing principal singers
and accompanists from supporting singers; Heartstrings correctly features
Vostriakov, who is named among the teachers in its existing description. Winter
Extravaganza's eight equally credited soloists and accompanist receive equal
tiles. Unknown photographs retain neutral rectangular spaces and equal billing.
The three poster-only principals retain authentic circular artwork inside their
equal-height rectangular cards; full rectangular originals are unavailable.

`tools/sync_programme_portraits.py` records this source-based presentation and
the separate rectangular views. Its `--check` runs in CI. The new programme's
existing rectangular views are preserved; repeated circles share the directory
views. After editing crops, run both `tools/build_artists.py` and this synchronizer.
Independent circle review covered all 25 views; programme readback confirmed all
headings, roles and notes preserved. CSS references advance to artists.css?v=6.

Final independent review found no blockers after inspecting all 25 circle
views, all 18 distinct rectangle/poster-card views, and actual chamber/mixed
programmes at desktop and 396px mobile, UA/EN and dark theme. Existing tests,
responsive assets, metadata, structured data, crop bounds, exact programme
text readback, deterministic directory build and synchronization checks pass.

Owner correction — 3 October 2026 (evening): Makar Rusanivsky's circle sat
too loose, with the head high and the dark suit weighting the lower left.
His source view is now (1000,540,2150): face centred, eyes near the
upper-middle and head-and-shoulders scale matching the neighbouring
portraits. The original JPEG and his rectangular programme view are
unchanged. The 404 page's «Контакти» link now points to `/index.html#contacts`
(the 404 page has no contacts section of its own).

Owner-confirmed portraits — 3 October 2026 (evening): Nataliia Skrynnyk
(`20250416-190508-A`) and Polina Burakova (`20250416-190636-A`) from the
Stabat Mater post-concert portrait set, and Iryna Lytvynenko
(`20240608-162236-A`, at the piano) from Roads of Love. Originals are copied
byte-for-byte (no GPS present) as `assets/img/<id>-portrait-20261003.jpg`;
circle and 4:5 programme views are crops only. Directory total: 31 of 36
with photographs; Mramornova and Terentiev remain neutral placeholders.
