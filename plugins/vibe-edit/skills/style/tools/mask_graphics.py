#!/usr/bin/env python3
"""Apply inverse foreground matte to ONLY a graphic's alpha. Original footage stays separate.
Requires aligned input durations/rates and an alpha-bearing graphic. Uses a new output only.
"""
import argparse, json, subprocess
from pathlib import Path

def probe(p):
    d=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=width,height,avg_frame_rate,duration,nb_frames,pix_fmt','-of','json',str(p)]))['streams'][0]
    return d

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('graphic',type=Path);ap.add_argument('matte',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args()
    if a.output.exists():ap.error('Output exists; choose a new path')
    g,m=probe(a.graphic),probe(a.matte)
    if g['avg_frame_rate']!=m['avg_frame_rate']:ap.error('Input frame rates differ; align in a new working copy first')
    if g.get('nb_frames') and m.get('nb_frames') and g['nb_frames']!=m['nb_frames']:ap.error('Input frame counts differ')
    if 'a' not in g['pix_fmt'] and not g['pix_fmt'].startswith('yuva'):ap.error('Graphic must carry an alpha channel')
    w,h=g['width'],g['height']
    graph=f'[0:v]format=rgba,split[c][a];[a]alphaextract[alpha];[1:v]scale={w}:{h}:flags=bilinear,format=gray,negate[inv];[alpha][inv]blend=all_mode=multiply[masked];[c][masked]alphamerge[out]'
    subprocess.run(['ffmpeg','-v','error','-nostdin','-n','-i',str(a.graphic),'-i',str(a.matte),'-filter_complex',graph,'-map','[out]','-c:v','prores_ks','-profile:v','4','-pix_fmt','yuva444p10le','-an',str(a.output)],check=True)
    print('Wrote graphic-only occlusion layer. Native import and full visual inspection remain required.')
if __name__=='__main__':main()
