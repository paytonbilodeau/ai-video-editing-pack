#!/usr/bin/env python3
"""Portable version of the actual Gentlemen layered-interchange mechanism.
Use: layered_fcpxml.py job.json new.fcpxml. Native import/relink remains separate.
"""
from pathlib import Path
from fractions import Fraction
import argparse, json, xml.etree.ElementTree as E

def build(job_path, output):
    if output.exists():raise FileExistsError(output)
    job=json.loads(job_path.read_text());root=job_path.resolve().parent
    fps=Fraction(str(job['fps']));frames=int(job['frames'])
    if fps<=0 or frames<=0:raise ValueError('Positive FPS and frames required')
    dur=Fraction(frames,1)/fps
    ts=lambda v:f'{v.numerator}/{v.denominator}s'
    doc=E.Element('fcpxml',version='1.11');res=E.SubElement(doc,'resources')
    E.SubElement(res,'format',id='fmt',frameDuration=ts(1/fps),width=str(job['width']),height=str(job['height']),colorSpace='1-1-1 (Rec. 709)')
    def asset(key,video,audio):
        p=(root/job[key]).resolve()
        if not p.is_file():raise FileNotFoundError(p)
        a=dict(id=key,name=p.stem,start='0s',duration=ts(dur),hasVideo='1' if video else '0',hasAudio='1' if audio else '0')
        if video:a.update(format='fmt',videoSources='1')
        if audio:a.update(audioSources='1',audioChannels=str(job.get('audioChannels',2)),audioRate='48000')
        node=E.SubElement(res,'asset',a);E.SubElement(node,'media-rep',kind='original-media',src=p.as_uri())
    asset('base',True,bool(job.get('baseHasAudio',False)));asset('overlay',True,False)
    if job.get('sound'):asset('sound',False,True)
    lib=E.SubElement(doc,'library');event=E.SubElement(lib,'event',name=job.get('name','Layered motion practice'));project=E.SubElement(event,'project',name=job.get('name','Layered motion practice'))
    seq=E.SubElement(project,'sequence',format='fmt',duration=ts(dur),tcStart='0s',tcFormat='NDF',audioLayout='stereo',audioRate='48k');spine=E.SubElement(seq,'spine')
    clip=E.SubElement(spine,'asset-clip',ref='base',name='Source picture',offset='0s',start='0s',duration=ts(dur),format='fmt')
    E.SubElement(clip,'asset-clip',ref='overlay',name='Editable graphic layer',lane='1',offset='0s',start='0s',duration=ts(dur),format='fmt')
    if job.get('sound'):E.SubElement(clip,'asset-clip',ref='sound',name='Independent marker sound',lane='-1',offset='0s',start='0s',duration=ts(dur),audioRole='effects')
    E.indent(doc,space='  ');output.write_bytes(b'<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n'+E.tostring(doc,encoding='utf-8'))
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('job',type=Path);ap.add_argument('output',type=Path);a=ap.parse_args();build(a.job,a.output);print('Saved layered XML. Verify media dimensions/duration, native import and alpha.')
