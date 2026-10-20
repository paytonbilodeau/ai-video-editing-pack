import json
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter,sosfiltfilt,firwin2,fftconvolve
import gentlemen_marker_options as original
import gentlemen_squeak_options as round2
import gentlemen_reference_options as round3
ROOT=original.ROOT
SR=48000


OPTIONS = [
    dict(id='A',name='Thin nib',description='Fine writing detail with a small, higher squeak.',
         sources=(1.,0.),band=(600,5200),pitch=1.10,guide=.80,grain=.30,
         squeak=.55,accentSources=(.20,.80),accentPitch=(1.00,1.26),
         accentFraction=.70,accentPosition=.42,accentQuantile=.65),
    dict(id='B',name='Paper touch',description='More dry writing grain, with the faintest squeak in this set.',
         sources=(.90,.10),band=(850,5900),pitch=1.02,guide=.35,grain=.55,
         squeak=.38,accentSources=(.55,.45),accentPitch=(.96,1.10),
         accentFraction=.55,accentPosition=.48,accentQuantile=.72),
    dict(id='C',name='Soft felt',description='Smoother contact with a rounded, soft marker squeak.',
         sources=(.65,.35),band=(480,4200),pitch=1.04,guide=.80,grain=.18,
         squeak=.62,accentSources=(.15,.85),accentPitch=(.92,1.10),
         accentFraction=.85,accentPosition=.50,accentQuantile=.60),
    dict(id='D',name='Feather squeak',description='Light writing texture with brief squeaks late in longer strokes.',
         sources=(1.,0.),band=(700,4900),pitch=1.16,guide=.80,grain=.22,
         squeak=.50,accentSources=(.35,.65),accentPitch=(1.08,1.30),
         accentFraction=.40,accentPosition=.68,accentQuantile=.76),
    dict(id='E',name='Warm glide',description='Warmer contact with a lower, gentler rubbing squeak.',
         sources=(.45,.55),band=(450,3600),pitch=.97,guide=.60,grain=.28,
         squeak=.57,accentSources=(.10,.90),accentPitch=(.88,.98),
         accentFraction=.90,accentPosition=.50,accentQuantile=.65),
]

def guide_filter(strength):
    report=json.loads((round3.REV/'reference-tone-profile.json').read_text())
    freq=np.r_[0,report['bandCentersHz'],11000,24000]
    gain=np.r_[0,report['broadGainDb'],-3,-3]*strength
    return firwin2(257,freq/(SR/2),10**(gain/20))

def friction_bank(option,name,raw,candidates):
    """Keep original fine friction; do not flatten it through tanh distortion."""
    x=sosfiltfilt(butter(3,option['band'],fs=SR,btype='bandpass',output='sos'),raw)
    x=fftconvolve(x,guide_filter(option['guide']),mode='same')
    items=[]
    for candidate in candidates:
        a=round(candidate['start']*SR);b=round(candidate['end']*SR)
        segment=x[a:b].copy()
        # Partial envelope correction retains some real grain and nib pressure.
        envelope=np.sqrt(gaussian_filter1d(segment**2,SR*.010))
        segment/=np.maximum(envelope,np.median(envelope)*.40+1e-10)**(1-option['grain'])
        segment/=max(np.sqrt(np.mean(segment**2)),1e-12)
        if np.max(abs(segment))>6.5:
            continue
        items.append(dict(start=candidate['start'],end=candidate['end'],audio=segment))
    if len(items)<3:
        raise RuntimeError(f'Not enough contact fragments for {option["id"]}/{name}')
    return items

def accent_track(clip,items,pitch,option,seed):
    rng=np.random.default_rng(seed)
    out=np.zeros(round(clip['duration']*SR));placements=[]
    threshold=max(1/clip['fps'],float(np.quantile(
        [s['end']-s['start'] for s in clip['strokes']],option['accentQuantile'])))
    for stroke in clip['strokes']:
        if stroke['end']-stroke['start']<threshold:
            continue
        a=round((np.floor(stroke['start']*clip['fps'])+1)/clip['fps']*SR)
        b=min(len(out),round((np.ceil(stroke['end']*clip['fps'])+1)/clip['fps']*SR))
        length=b-a
        if length<=0:
            continue
        size=max(2,round(length*option['accentFraction']))
        center=a+round(length*option['accentPosition'])
        start=max(a,min(b-size,center-size//2));end=start+size
        # Short natural resonances rise and fall within the visible stroke.
        # This is one soft nib sound, without a sustained added whistle.
        fragment=original.contact_texture(items,size,rng,pitch)
        fragment*=np.sin(np.linspace(0,np.pi,size))**1.6
        out[start:end]+=fragment
        placements.append(dict(start=start/SR,end=end/SR,
                               visibleStart=a/SR,visibleEnd=b/SR))
    active=np.repeat(np.asarray(clip['motion'])>1e-9,SR//clip['fps'])
    out[~active]=0
    out/=max(np.sqrt(np.mean(out[active]**2)),1e-12)
    return out,placements

def render_option(option,index,clip,banks,squeaks):
    """Render one material against supplied visible-motion events, without I/O."""
    names=('giddster','picklejones')
    active=np.repeat(np.asarray(clip['motion'])>1e-9,SR//clip['fps'])
    friction=np.zeros(len(active));accent=np.zeros(len(active));placement=[]
    for source_index,(name,weight) in enumerate(zip(names,option['sources'])):
        if not weight:
            continue
        layer,_=original.make_stem(option,banks[name],clip,42001+index*131+source_index*29)
        layer/=max(np.sqrt(np.mean(layer[active]**2)),1e-12)
        friction+=weight*layer
    friction/=max(np.sqrt(np.mean(friction[active]**2)),1e-12)
    for source_index,(name,weight,pitch) in enumerate(zip(names,option['accentSources'],option['accentPitch'])):
        layer,placement=accent_track(clip,squeaks[name],pitch,option,42500+index*137+source_index*31)
        accent+=weight*layer
    accent/=max(np.sqrt(np.mean(accent[active]**2)),1e-12)
    x=round3.normalize(friction+option['squeak']*accent,active)
    assert np.isfinite(x).all() and np.max(abs(x))<10**(-23/20)
    return x,placement
