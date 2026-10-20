#!/usr/bin/env python3
"""Track a textured planar object for a Remotion annotation.

The reference quad is TL, TR, BR, BL in source pixels. Each frame is matched
directly to the reference with SIFT + RANSAC, so errors do not accumulate.
Low-confidence frames are marked invalid and must be hidden or corrected.
"""
import argparse
import json
from pathlib import Path
import cv2
import numpy as np


def track(video, output, corners):
    cap = cv2.VideoCapture(str(video))
    fps = cap.get(cv2.CAP_PROP_FPS)
    ok, first = cap.read()
    if not ok:
        raise RuntimeError('Could not decode reference frame')
    h, w = first.shape[:2]
    quad = np.asarray(corners, np.float32).reshape(4, 1, 2)
    gray = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    region = np.zeros_like(gray)
    cv2.fillConvexPoly(region, quad.astype('int32'), 255)
    region = cv2.erode(region, np.ones((15, 15), np.uint8))
    sift = cv2.SIFT_create(nfeatures=4000, contrastThreshold=.025)
    k0, d0 = sift.detectAndCompute(gray, region)
    if d0 is None or len(k0) < 20:
        raise RuntimeError('The reference area needs more distinctive texture')
    matcher = cv2.BFMatcher()
    records = []
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        k, descriptors = sift.detectAndCompute(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY), None)
        pairs = matcher.knnMatch(d0, descriptors, k=2) if descriptors is not None else []
        good = [a for pair in pairs if len(pair) == 2 for a, b in [pair] if a.distance < .72 * b.distance]
        record = {'frame': len(records), 'valid': False, 'matches': len(good)}
        if len(good) >= 12:
            src = np.float32([k0[m.queryIdx].pt for m in good]).reshape(-1, 1, 2)
            dst = np.float32([k[m.trainIdx].pt for m in good]).reshape(-1, 1, 2)
            homography, inliers = cv2.findHomography(src, dst, cv2.RANSAC, 3)
            if homography is not None:
                points = cv2.perspectiveTransform(quad, homography).reshape(4, 2)
                residuals = np.linalg.norm(cv2.perspectiveTransform(src, homography) - dst, axis=2).ravel()
                accepted = inliers.ravel().astype(bool)
                median = float(np.median(residuals[accepted]))
                count = int(accepted.sum())
                ratio = count / len(good)
                area = abs(cv2.contourArea(points))
                valid = count >= 12 and ratio >= .45 and median < 2 and area > 1000 and cv2.isContourConvex(points)
                record.update(valid=bool(valid), quad=np.round(points, 2).tolist(),
                    inliers=count, ratio=round(ratio, 4), residual=round(median, 4))
        records.append(record)
    cap.release()
    report = {'source': str(video), 'width': w, 'height': h, 'fps': fps, 'method': 'SIFT reference-to-frame homography with RANSAC',
        'frames': records, 'summary': {'frames': len(records), 'valid': sum(r['valid'] for r in records),
        'worstMedianResidual': max((r.get('residual', 0) for r in records), default=0)}}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, separators=(',', ':')))
    print(json.dumps(report['summary']))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('video', type=Path)
    ap.add_argument('output', type=Path)
    ap.add_argument('--quad', required=True, help='x,y,x,y,x,y,x,y in TL TR BR BL order')
    args = ap.parse_args()
    if args.output.exists(): ap.error("Refusing existing output; use a new file.")
    track(args.video, args.output, list(map(float, args.quad.split(','))))
