#!/usr/bin/env python3
"""Selected Gentlemen marker: Feather squeak with a slight Thin nib blend.

Accepts the existing visible-motion event schema for any scene at a supported
integer frame rate. Does not reuse demonstration rhythm for new text.
"""
from pathlib import Path
from functools import lru_cache
import argparse
import json
import numpy as np
import gentlemen_fine_nib_options as r4

PRESET_PATH=r4.ROOT/'flow/src/components/gentlemen/sound-preset.json'


def validate_clip(clip):
    fps=clip['fps'];duration=clip['duration'];motion=np.asarray(clip['motion'],dtype=float)
    if not isinstance(fps,int) or fps<=0 or r4.SR%fps:
        raise ValueError('Use an integer frame rate dividing 48000, such as 24, 25, 30, 50 or 60.')
    if not np.isfinite(duration) or duration<=0 or abs(len(motion)-duration*fps)>1e-7:
        raise ValueError('Duration and visible-motion frame count must agree exactly.')
    if motion.ndim!=1 or not np.isfinite(motion).all() or np.any(motion<0):
        raise ValueError('Motion must be a one-dimensional array of finite nonnegative distances.')
    for stroke in clip['strokes']:
        if not np.isfinite([stroke['start'],stroke['end']]).all() or not 0<=stroke['start']<stroke['end']<=duration:
            raise ValueError('Every stroke needs a finite start and later end within the scene.')
    if np.any(motion>1e-9) and not clip['strokes']:
        raise ValueError('Visible writing needs its actual stroke events.')
    return np.repeat(motion>1e-9,r4.SR//fps)


@lru_cache(maxsize=1)
def material_banks():
    names=('giddster','picklejones')
    raw={name:r4.original.read_audio(r4.original.SOURCES/f'{name}.mp3') for name in names}
    candidates={name:r4.original.bank(dict(id='R4',name=name,source=name,low=450,high=6000)) for name in names}
    squeaks={name:r4.round2.squeak_bank(name) for name in names}
    banks={}
    for index in (3,0):
        option=r4.OPTIONS[index]
        banks[option['id']]={name:r4.friction_bank(option,name,raw[name],candidates[name])
                            for name,weight in zip(names,option['sources']) if weight>0}
    return banks,squeaks


def pcm_reference(x):
    """Match the int16 audition waveform before blending the two materials."""
    return np.int16(np.clip(x,-1,1)*32767).astype(float)/32768


def blend(feather,thin,active):
    preset=json.loads(PRESET_PATH.read_text())
    x=preset['amplitudeWeights']['D']*feather+preset['amplitudeWeights']['A']*thin
    if not np.any(active):
        return np.zeros_like(x)
    x=r4.round3.normalize(x,active)
    if not np.isfinite(x).all() or np.max(abs(x))>=10**(-23/20):
        raise ValueError('Selected sound exceeds its peak headroom; review the supplied events.')
    return x


def render(clip):
    active=validate_clip(clip)
    if not np.any(active):
        return np.zeros(len(active))
    banks,squeaks=material_banks();layers={}
    for index in (3,0):
        option=r4.OPTIONS[index]
        x,_=r4.render_option(option,index,clip,banks[option['id']],squeaks)
        layers[option['id']]=pcm_reference(x)
    return blend(layers['D'],layers['A'],active)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--events',type=Path,required=True,help='JSON containing one scene or a mapping of named scenes.')
    parser.add_argument('--scene',help='Named scene when the input is a mapping.')
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists(): parser.error("Refusing existing output; use a new file.")
    data=json.loads(args.events.read_text());clip=data[args.scene] if args.scene else data
    r4.original.wav(args.output,render(clip))
    print(f'Saved selected marker sound: {args.output}')
