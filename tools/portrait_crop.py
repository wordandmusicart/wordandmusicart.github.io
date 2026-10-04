#!/usr/bin/env python3
"""Measure and propose circle crops for artist portraits (design-system §6).

Crops are computed from the detected face, not guessed:

    python3 tools/portrait_crop.py                 # measure every circle
    python3 tools/portrait_crop.py polina-burakova # propose a crop for one artist

The proposal puts the face in the middle (cx 0.50), the eye line at 0.42 of
the circle and the face at 0.46 of the diameter — the scale of the circles the
owner approved (Skrynnyk, Popovych, Burakova, Povazhna). The circle is then
pulled back inside the photograph; if that moves the face, the photo itself
has no room and the report says so. Judge the result on the contact sheet
(`tools/portrait_sheet.cjs`) next to all other portraits before publishing.

Needs pillow and opencv-python-headless.
"""
import json
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
TARGET = {'width': 0.46, 'cx': 0.50, 'eye': 0.42}
CASCADE = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')


def artists():
    return json.loads((ROOT / 'assets/artists.json').read_text())


def photo(p):
    return ImageOps.exif_transpose(Image.open(ROOT / p['src'].lstrip('/'))).convert('L')


def largest_face(gray, min_size):
    faces = CASCADE.detectMultiScale(np.array(gray), 1.05, 6, minSize=(min_size, min_size))
    return max(faces, key=lambda f: f[2]) if len(faces) else None


def tilted_face(p):
    """Detect inside the known portrait, rotating only a temporary analysis copy.

    Coordinates return to the original photo; the displayed portrait never
    rotates. Restricting detection to the portrait avoids background faces
    (the sculpture in Hlinska's photograph).
    """
    c = p.get('circle_crop', p['crop'])
    image = photo(p)
    scale = image.width / p['width']
    box = [round(v * scale) for v in (c['x'], c['y'], c['x'] + c['size'], c['y'] + c['size'])]
    gray = np.array(image.crop(box).resize((600, 600)))
    rotation = cv2.getRotationMatrix2D((300, 300), p['face_rotation'], 1)
    face = largest_face(cv2.warpAffine(gray, rotation, (600, 600)), 120)
    if face is None:
        return None
    x, y, w, h = face
    inverse = cv2.invertAffineTransform(rotation)
    points = np.array([[x + w / 2, y + h / 2, 1],
                       [x + w / 2, y + 0.4 * h, 1]]) @ inverse.T
    points = points * c['size'] / 600 + np.array([c['x'], c['y']])
    return {'width': w * c['size'] / 600, 'cx': points[0, 0], 'eye': points[1, 1]}


def measure(p):
    """Face width, centre and eye line as fractions of the circle; None if no frontal face."""
    c = p.get('circle_crop', p['crop'])
    if p.get('face_rotation'):
        face = tilted_face(p)
        return None if face is None else {
            'width': face['width'] / c['size'],
            'cx': (face['cx'] - c['x']) / c['size'],
            'eye': (face['eye'] - c['y']) / c['size'],
        }
    image = photo(p)
    scale = image.width / p['width']
    box = [round(v * scale) for v in (c['x'], c['y'], c['x'] + c['size'], c['y'] + c['size'])]
    face = largest_face(image.crop(box).resize((600, 600)), 120)
    if face is None:
        return None
    x, y, w, h = face
    return {'width': w / 600, 'cx': (x + w / 2) / 600, 'eye': (y + 0.4 * h) / 600}


def propose(p):
    if p.get('face_rotation'):
        face = tilted_face(p)
        if face is None:
            return None
        size = min(face['width'] / TARGET['width'], p['width'], p['height'])
        left = min(max(face['cx'] - TARGET['cx'] * size, 0), p['width'] - size)
        top = min(max(face['eye'] - TARGET['eye'] * size, 0), p['height'] - size)
        return {'x': round(left), 'y': round(top), 'size': round(size)}
    image = photo(p)
    scale = 1200 / max(image.size)
    face = largest_face(image.resize((round(image.width * scale), round(image.height * scale))), 40)
    if face is None:
        return None
    x, y, w, h = (v / scale * p['width'] / image.width for v in face)
    size = min(w / TARGET['width'], p['width'], p['height'])
    left = x + w / 2 - TARGET['cx'] * size
    top = y + 0.4 * h - TARGET['eye'] * size
    left = min(max(left, 0), p['width'] - size)
    top = min(max(top, 0), p['height'] - size)
    return {'x': round(left), 'y': round(top), 'size': round(size)}


if __name__ == '__main__':
    wanted = set(sys.argv[1:])
    for a in artists():
        p = a.get('portrait')
        if not p or 'crop' not in p or (wanted and a['id'] not in wanted):
            continue
        m = measure(p)
        now = 'no frontal face' if m is None else ' '.join(f'{k}={v:.2f}' for k, v in m.items())
        line = f"{a['id']:24} {now}"
        if wanted:
            line += f"\n  current  {p.get('circle_crop', p['crop'])}\n  proposed {propose(p)}"
        print(line)
