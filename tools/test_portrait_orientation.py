#!/usr/bin/env python3
"""Acceptance tests for EXIF-oriented portrait masters and responsive images.

The original JPEG remains byte-identical. Width descriptors use its displayed
dimensions, and generated pixels are upright without a second EXIF rotation.
Run with: python3 tools/test_portrait_orientation.py
"""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image, ImageCms

import images


ORIENTATION = 274
METADATA = {270: "Portrait acceptance fixture", 315: "Fixture photographer",
            33432: "Copyright fixture photographer"}
XMP = (b'<x:xmpmeta xmlns:x="adobe:ns:meta/">'
       b'<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
       b'<rdf:Description xmlns:dc="http://purl.org/dc/elements/1.1/" '
       b'dc:description="Portrait metadata fixture"/>'
       b'</rdf:RDF></x:xmpmeta>')


class PortraitOrientationAcceptance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Distinct corners detect the direction of rotation, beyond dimensions.
        raw = Image.new("RGB", (4080, 3060))
        raw.paste((255, 0, 0), (0, 0, 2040, 1530))
        raw.paste((0, 255, 0), (2040, 0, 4080, 1530))
        raw.paste((0, 0, 255), (0, 1530, 2040, 3060))
        raw.paste((255, 255, 0), (2040, 1530, 4080, 3060))
        exif = Image.Exif()
        exif[ORIENTATION] = 6
        for tag, value in METADATA.items():
            exif[tag] = value
        cls.icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "portrait.jpg"
            raw.save(path, quality=95, exif=exif, icc_profile=cls.icc, xmp=XMP)
            cls.original = path.read_bytes()
        raw.close()

    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.master = Path(self.folder.name) / "portrait.jpg"
        self.master.write_bytes(self.original)
        self.img_patch = patch.object(images, "IMG", self.folder.name)
        self.img_patch.start()
        self.addCleanup(self.img_patch.stop)

    def build_320(self):
        # The acceptance gate needs one derivative; production keeps its ladder.
        with patch.object(images, "WIDTHS", (320,)):
            images.build()
        return Path(self.folder.name) / "portrait-320.webp"

    def test_variants_use_displayed_portrait_dimensions(self):
        width, height, steps = images.variants("portrait", str(self.master))
        self.assertEqual((width, height), (3060, 4080))
        self.assertEqual(steps, [320, 480, 720, 960, 1440, 2400])

    def test_original_srcset_descriptor_uses_displayed_width(self):
        entries = images.srcset("portrait", str(self.master)).split(", ")
        self.assertEqual(entries[-1], "/assets/img/portrait.jpg 3060w")
        self.assertEqual(entries[0], "/assets/img/portrait-320.webp 320w")

    def test_generated_webp_has_upright_pixels_and_no_extra_rotation(self):
        with Image.open(self.build_320()) as variant:
            self.assertEqual(variant.size, (320, 427))
            self.assertIn(variant.getexif().get(ORIENTATION, 1), (1,))
            # Orientation 6 is clockwise: blue/red across the top, yellow/green
            # across the bottom. Allow lossy WebP colour quantisation.
            for point, expected in [((40, 40), (0, 0, 255)),
                                    ((280, 40), (255, 0, 0)),
                                    ((40, 387), (255, 255, 0)),
                                    ((280, 387), (0, 255, 0))]:
                with self.subTest(corner=point):
                    actual = variant.getpixel(point)
                    self.assertLessEqual(max(abs(a - b) for a, b in zip(actual, expected)), 12)

    def test_build_preserves_source_bytes_and_other_metadata(self):
        derivative = self.build_320()
        self.assertEqual(self.master.read_bytes(), self.original)
        with Image.open(self.master) as master, Image.open(derivative) as variant:
            self.assertEqual(master.size, (4080, 3060))
            self.assertEqual(master.getexif()[ORIENTATION], 6)
            for tag, value in METADATA.items():
                with self.subTest(exif_tag=tag):
                    self.assertEqual(variant.getexif().get(tag), value)
            self.assertEqual(variant.info.get("icc_profile"), self.icc)
            self.assertEqual(variant.info.get("xmp"), XMP)


if __name__ == "__main__":
    unittest.main()
