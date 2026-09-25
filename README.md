# word&music

Static website for word&music, published with GitHub Pages.

## Preview locally

```sh
python3 -m http.server 4173
```

Then open <http://localhost:4173>.

## Images

Every photo on the site loads at the size the screen needs, the same way
rusanivsky.com does:

- Keep one master per image in `assets/img/<name>.jpg` at its original
  resolution. Never upscale.
- `python3 tools/images.py` (needs `pip install pillow`) writes
  `<name>-480/-720/-960/-1440/-2400.webp`, only for widths smaller than the
  master, and fills `srcset` in every page. Variants keep the master's
  colour profile, EXIF and XMP; only GPS is removed.
- Every `<img>` (and `<source>`) gets a hand-written `sizes` that matches
  its layout, e.g. `sizes="(max-width:900px) 100vw, 40vw"`.
- `python3 tools/images.py --check` fails if a variant, `srcset` or `sizes`
  is missing, or a variant has lost the master's metadata. The deploy workflow runs it, so a broken image blocks the
  deploy.

### Concert photos

Photos from concerts live in `assets/photo/<concert-slug>/`, one folder per
concert with an English slug (e.g. `autumn-rendezvous`). Each file keeps its
original Drive name: `<name>.webp` is the top step (2400 px or the original
width if smaller) and `<name>-480/-720/-960/-1440.webp` are the smaller
steps; `tools/images.py` makes missing steps from the top step.
One frame per shot; byte-identical copies (e.g. `… 1.jpg`) are skipped.
All metadata (EXIF, XMP, colour profile, author/copyright) is kept except
GPS, which is removed from EXIF and XMP. Originals stay on Google Drive
(KR/Production/Photography). The media page shows five frames per concert;
«Усі фото · N» and every frame open the full set in the lightbox
(`assets/lightbox.js`). Right-click on a frame copies its file link.
