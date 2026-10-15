#!/usr/bin/env python3
"""Make local XML copies that point to this folder's unchanged source.mp4."""
from pathlib import Path
from xml.etree import ElementTree as ET

folder = Path(__file__).resolve().parent
source = folder / 'source.mp4'
if not source.is_file():
    raise SystemExit('Keep relink.py beside source.mp4 and the two XML files.')
out = folder / 'local-timelines'
if out.exists():
    raise SystemExit('local-timelines already exists. Preserve it or move it before running again.')
inputs = [folder / 'lamp-practice-corrected.fcpxml', folder / 'lamp-practice-corrected.premiere.xml']
trees = [ET.parse(path) for path in inputs]
out.mkdir()
for path, tree in zip(inputs, trees):
    for node in tree.findall('.//media-rep'):
        node.set('src', source.as_uri())
    for node in tree.findall('.//file/pathurl'):
        node.text = source.as_uri()
    tree.write(out / path.name, encoding='utf-8', xml_declaration=True)
print('Created local-timelines with this folder’s media path. Original XML and video preserved.')
