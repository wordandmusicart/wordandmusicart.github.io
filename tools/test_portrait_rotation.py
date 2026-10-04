#!/usr/bin/env python3
"""Tilted-head detection keeps Lidiia Hlinska's circle on the real face.

Detection may rotate a temporary copy. Measurements and proposed crops use
the original photograph's coordinates; the large statue outside the current
crop must never become the detected performer.
"""
import unittest

from portrait_crop import artists, measure, propose
from test_portrait_crops import BANDS


class TiltedPortrait(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portrait = next(a['portrait'] for a in artists()
                            if a['id'] == 'lidiia-hlinska')

    def test_lidiia_face_is_measured_inside_shared_bands(self):
        measured = measure(self.portrait)
        self.assertIsNotNone(measured, 'the tilted real face must be detected')
        for key, (low, high) in BANDS.items():
            with self.subTest(measurement=key):
                self.assertGreaterEqual(measured[key], low)
                self.assertLessEqual(measured[key], high)

    def test_proposal_stays_on_lidiia_instead_of_the_statue(self):
        crop = propose(self.portrait)
        self.assertIsNotNone(crop, 'a circle for the tilted real face must be proposed')
        # Relative source coordinates survive a change in derivative size.
        # The statue on the right can fool a frontal-face detector.
        centre_x = (crop['x'] + crop['size'] / 2) / self.portrait['width']
        centre_y = (crop['y'] + crop['size'] / 2) / self.portrait['height']
        self.assertGreaterEqual(centre_x, 0.35)
        self.assertLessEqual(centre_x, 0.55)
        self.assertGreaterEqual(centre_y, 0.22)
        self.assertLessEqual(centre_y, 0.42)


if __name__ == '__main__':
    unittest.main()
