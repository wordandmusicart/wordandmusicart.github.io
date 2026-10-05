#!/usr/bin/env python3
"""Gate for circle and tile crops (design-system §6, owner request 3 October 2026).

Every crop stays inside its photograph, so a circle or 4:5 tile never shows an
empty edge. Every circle with a frontal face keeps it centred and at the scale
of its neighbours. The bands are wider than the target in tools/portrait_crop.py
so approved circles pass, and they catch what the owner has had to send back:
a small face lost in the background, a face pushed to the side, eyes low in
the circle.

A face the detector cannot see (profile, strong tilt, poster artwork) is listed
in NO_FRONTAL_FACE with the reason; those are judged on the contact sheet only.
"""
import json
import unittest
from pathlib import Path

from portrait_crop import ROOT, measure
from sync_programme_portraits import TILES

BANDS = {'width': (0.39, 0.60), 'cx': (0.38, 0.62), 'eye': (0.30, 0.48)}
NO_FRONTAL_FACE = {
    'iryna-lytvynenko': 'profile at the piano',
    'viktoriia-shvets': 'profile at the piano',
    'viktoriia-mramornova': 'profile at the piano',
}
ARTISTS = json.loads((ROOT / 'assets/artists.json').read_text())


class PortraitCrops(unittest.TestCase):
    def test_crops_stay_inside_the_photograph(self):
        for a in ARTISTS:
            p = a.get('portrait')
            if not p:
                continue
            boxes = [('circle', p.get('circle_crop', p.get('crop')), 1)]
            tile = p.get('programme_crop') or TILES.get(a['id'])
            if tile:
                boxes.append(('tile', {'x': tile[0], 'y': tile[1], 'size': tile[2]}, 1.25))
            for kind, c, ratio in boxes:
                if not c:
                    continue
                with self.subTest(artist=a['id'], crop=kind):
                    self.assertGreaterEqual(c['x'], 0)
                    self.assertGreaterEqual(c['y'], 0)
                    self.assertLessEqual(c['x'] + c['size'], p['width'] + 1)
                    self.assertLessEqual(c['y'] + c['size'] * ratio, p['height'] + 1)

    def test_faces_are_centred_and_at_the_shared_scale(self):
        for a in ARTISTS:
            p = a.get('portrait')
            if not p or not ('circle_crop' in p or 'crop' in p) or 'label' in p or a['id'] in NO_FRONTAL_FACE:
                continue
            m = measure(p)
            with self.subTest(artist=a['id']):
                self.assertIsNotNone(m, 'no frontal face found: fix the crop or list the reason in NO_FRONTAL_FACE')
                for key, (low, high) in BANDS.items():
                    self.assertTrue(low <= m[key] <= high, f'{key}={m[key]:.2f} outside {low}–{high}')


if __name__ == '__main__':
    unittest.main()
