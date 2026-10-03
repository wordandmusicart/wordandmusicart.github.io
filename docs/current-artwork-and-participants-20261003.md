# Current artwork and programme corrections, 2026-10-03

Acceptance: use the current top-level October exports, preserve artwork and source files; site dark uses LIGHT artwork, site light uses NIGHT artwork, including manual theme overrides and both languages. Date/time/price remain three equal columns; visible currency is ₴; time and price share the same font size and stay on one line. On Heartstrings only, Oleksandr Vostriakov's identified portrait uses a circular crop.

The eight source files, hashes, modification times and dimensions are recorded in `current-poster-sources-20261003.json`. Earlier masters remain available. JPEG masters retain the available PNG metadata and dimensions; responsive WebP variants are generated through `tools/images.py`.

## Participant source audit

Public YouTube descriptions were read as text from `ytInitialPlayerResponse.videoDetails.shortDescription`; faces were not used to infer identity.

- [Winter Extravaganza](https://www.youtube.com/watch?v=bpz1jSrtFMA): the description explicitly credits “ВЕДУЧІ”, Дар’я Погоріла and Геннадій Таранюк. Add Hennadii as host and retain Daria's soloist credit while adding host. All eight vocalists and Nataliia Shmelova were already present. Add this programme to Hennadii's directory source links.
- The descriptions of [Christmas Kaleidoscope](https://www.youtube.com/watch?v=JAMDscAMvQA), [Heartstrings](https://www.youtube.com/watch?v=UaWqVU8fUw4), [Music of Soul and Heart](https://www.youtube.com/watch?v=474f5Yrp5-o) and [Amore Eterno](https://www.youtube.com/watch?v=qU1Jl_9ZuGQ) agree with their named participant lists.
- June poster: `02_Концерти_та_події/20250602_Мелодії_чарівного_червня/03_Експорт/Афіша концерту 20250602.jpg`. It names the two teachers, two concertmasters and Hennadii, already credited. Students are identified only as a group, without individual names.
- Autumn poster: `02_Концерти_та_події/20251115_Осінній_концерт/03_Експорт/Афіша концерту 20251511 v2.jpg`. It credits the student classes of Anzhelina Shvachka, Serhii Mahera and Liliia Hrevtsova; this does not establish that those teachers performed. Two concertmasters and Hennadii are already credited; student names are absent.

June and Autumn have no recording linked on the current programme/video pages. Inspected public word&music, Kyrylo Rusanivsky and Hennadii Taraniuk channel listings did not supply their student names. This is a source limitation, not evidence that no recording exists. The owner has no name list. These two individual student lists remain unresolved and are not filled with guesses.

Validation: independent updated event/price/theme tests; unchanged-text rollover fixture with only current poster references refreshed; image/metadata/structured-data checks; Chromium and WebKit desktop/mobile rendering; independent artifact review; production check after deployment. Backend/service checks are N/A for this static content and presentation change.
