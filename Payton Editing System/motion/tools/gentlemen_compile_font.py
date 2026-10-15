#!/usr/bin/env python3
"""Compile an OFL handwriting font into exact outlines and pen-reveal routes.

Requires fontTools, Pillow, numpy and opencv-contrib-python. Routes are a
deterministic approximation of pen order, not the font designer's original pen
recording. Font outlines remain the final visible lettering.
"""
from pathlib import Path
import argparse
import json
import math
import string

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen


def routes_for(mask, char):
    thin = cv2.ximgproc.thinning(mask)
    pixels = {tuple(p) for p in np.argwhere(thin > 0)}
    adjacent = {}
    for y, x in pixels:
        neighbors = []
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                q = (y + dy, x + dx)
                if (dy or dx) and q in pixels:
                    # Do not make a triangular shortcut around a right angle.
                    if dy and dx and ((y, x + dx) in pixels or (y + dy, x) in pixels):
                        continue
                    neighbors.append(q)
        adjacent[(y, x)] = neighbors
    edges = {tuple(sorted((p, q))) for p, qs in adjacent.items() for q in qs}
    paths = []
    while edges:
        active = {p for e in edges for p in e}
        degree = {p: sum(tuple(sorted((p, q))) in edges for q in adjacent[p]) for p in active}
        ends = [p for p in active if degree[p] == 1]
        prefer_left = char in 'MNUVWXYZKacemnrsvwz'
        p = min(ends or active, key=lambda v: (v[1] + .1 * v[0], v[0]) if prefer_left and ends else (v[0] + v[1] * .12, v[1]))
        line = [p]
        previous = None
        while True:
            options = [q for q in adjacent[p] if tuple(sorted((p, q))) in edges]
            if not options:
                break
            if previous is None:
                q = min(options)
            else:
                back = line[max(0, len(line) - 12)]
                vy, vx = p[0] - back[0], p[1] - back[1]
                def heading(v):
                    before, after = p, v
                    for _ in range(8):
                        ns = [a for a in adjacent[after] if a != before and tuple(sorted((after, a))) in edges]
                        if len(ns) != 1:
                            break
                        before, after = after, ns[0]
                    dy, dx = after[0] - p[0], after[1] - p[1]
                    return (dy * vy + dx * vx) / max(math.hypot(dy, dx), .01)
                q = max(options, key=heading)
            edges.remove(tuple(sorted((p, q))))
            line.append(q)
            previous, p = p, q
        if len(line) > 2:
            points = np.array([(x, y) for y, x in line], dtype=np.float32)
            points = cv2.approxPolyDP(points, 1.25, False).reshape(-1, 2)
            paths.append(points)
    # Tiny dots sometimes thin to a single point, which has no edge.
    n, labels, stats, centroids = cv2.connectedComponentsWithStats(mask)
    for i in range(1, n):
        if not any(labels[round(p[0, 1]), round(p[0, 0])] == i for p in paths):
            x, y = centroids[i]
            paths.append(np.array([[x, y], [x + .2, y]], dtype=np.float32))
    # Long body strokes first; a detached dot is the last pen contact.
    # Trace order is already the chosen pen order. Only defer detached dots.
    paths.sort(key=lambda p: len(p) < 3)
    return paths


def compile_font(font_path, destination):
    ft = TTFont(font_path)
    upem = ft['head'].unitsPerEm
    gs, cmap = ft.getGlyphSet(), ft.getBestCmap()
    font = ImageFont.truetype(str(font_path), upem)
    chars = string.ascii_letters + string.digits + string.punctuation + ' £€×÷→–’“”éÉ'
    output = {'font': 'Reenie Beanie', 'unitsPerEm': upem, 'license': 'SIL OFL 1.1', 'glyphs': {}}
    minimum_coverage = 1
    for char in dict.fromkeys(chars):
        name = cmap.get(ord(char))
        if not name:
            continue
        pen = SVGPathPen(gs)
        gs[name].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))
        advance = ft['hmtx'][name][0]
        d = pen.getCommands()
        if not d:
            output['glyphs'][char] = {'d': '', 'advance': advance, 'strokes': []}
            continue
        bbox = font.getbbox(char, anchor='ls')
        margin = 70
        ox, oy = margin - bbox[0], margin - bbox[1]
        im = Image.new('L', (bbox[2] - bbox[0] + 2 * margin, bbox[3] - bbox[1] + 2 * margin))
        ImageDraw.Draw(im).text((ox, oy), char, font=font, anchor='ls', fill=255)
        binary = (np.asarray(im) > 100).astype('uint8') * 255
        paths = routes_for(binary, char)
        distance = cv2.distanceTransform(binary, cv2.DIST_L2, 5)
        cover = np.zeros_like(binary)
        strokes = []
        for p in paths:
            radii = [distance[min(round(y), distance.shape[0]-1), min(round(x), distance.shape[1]-1)] for x, y in p]
            width = float(max(12, max(radii) * 2 + 14))
            cv2.polylines(cover, [p.astype('int32')], False, 255, round(width))
            for xy in (p[0], p[-1]):
                cv2.circle(cover, tuple(xy.astype(int)), math.ceil(width / 2), 255, -1)
            local = p - [ox, oy]
            path = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in local)
            length = float(np.linalg.norm(np.diff(p, axis=0), axis=1).sum())
            strokes.append({'d': path, 'length': round(max(length, 8), 2), 'width': round(width, 1)})
        coverage = float(np.count_nonzero((cover > 0) & (binary > 0)) / np.count_nonzero(binary))
        # Broadening the mask only reveals original outline pixels. It cannot
        # fatten the output or introduce a second visible line.
        if coverage < .995:
            for stroke in strokes:
                stroke['width'] *= 1.5
        minimum_coverage = min(minimum_coverage, coverage)
        output['glyphs'][char] = {'d': d, 'advance': advance, 'strokes': strokes, 'coverageBeforeMargin': round(coverage, 4)}
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(output, separators=(',', ':')))
    print(json.dumps({'glyphs': len(output['glyphs']), 'initialMinimumCoverage': minimum_coverage, 'output': str(destination)}))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('font', type=Path)
    ap.add_argument('output', type=Path)
    a = ap.parse_args()
    if a.output.exists(): ap.error("Refusing existing output; use a new file.")
    compile_font(a.font, a.output)
