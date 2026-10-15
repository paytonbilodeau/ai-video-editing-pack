from pathlib import Path
import json,subprocess
import numpy as np
from scipy.ndimage import gaussian_filter1d,binary_closing
from scipy.signal import butter,sosfiltfilt
from scipy.io.wavfile import write
ROOT=Path(__file__).resolve().parents[1]
SOURCES=ROOT/"sound-sources"
SR=48000


def read_audio(path):
    raw = subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-ac','1','-ar',str(SR),'-f','f32le','-'])
    return np.frombuffer(raw,dtype=np.float32).astype(np.float64)

def regions(mask):
    edges = np.diff(np.r_[False, mask, False].astype(int))
    return list(zip(np.flatnonzero(edges == 1),np.flatnonzero(edges == -1)))

def bank(option):
    path = next(p for p in SOURCES.glob(option['source']+'.*') if p.suffix in ['.wav','.mp3'])
    raw = read_audio(path)
    x = sosfiltfilt(butter(3,[option['low'],option['high']],fs=SR,btype='bandpass',output='sos'),raw)
    # Remove the original recording's level envelope so its unrelated writing
    # rhythm does not compete with the visible pen. Preserve contact timbre.
    hop = 480
    rms = np.sqrt(np.mean(x[:len(x)//hop*hop].reshape(-1,hop)**2,axis=1))
    threshold = max(np.quantile(rms,.20)*5, np.quantile(rms,.75)*.55)
    active = binary_closing(rms > threshold,structure=np.ones(3))
    active[:int((10 if option['source']=='edctrainer' else 1.0)*100)] = False
    active[-50:] = False
    items=[]
    for a,b in regions(active):
        seg=x[a*hop:b*hop]
        if not .075 <= len(seg)/SR <= 4:
            continue
        energy=np.sqrt(np.mean(seg**2))
        crest=np.max(np.abs(seg))/max(energy,1e-12)
        if crest > 8:
            continue  # Reject sharp cap/handling impacts.
        local=gaussian_filter1d(seg*seg,SR*.012)**.5
        flat=seg/np.maximum(local,np.median(local)*.28+1e-10)
        if option['id'] in ['03','05']:
            # Accentuate existing narrow contact resonances, without adding a
            # continuous synthetic oscillator or a fabricated glass recording.
            band=[1000,2450] if option['id']=='03' else [1750,2950]
            detail=sosfiltfilt(butter(2,band,fs=SR,btype='bandpass',output='sos'),flat)
            flat=.45*flat+.85*detail
        flat=np.tanh(flat*.65)
        flat/=max(np.sqrt(np.mean(flat**2)),1e-10)
        items.append({'start':a/100,'end':b/100,'audio':flat,'crest':float(crest)})
    if len(items)<3:
        raise RuntimeError(f'Insufficient clean contact segments for {option["name"]}')
    return items

def contact_texture(items,n,rng,pitch):
    # Assemble actual contact fragments with smooth joins. Playback-rate changes
    # are small; the visible movement controls the final amplitude envelope.
    output=np.zeros(n+SR)
    cursor=0
    overlap=round(.012*SR)
    while cursor<n:
        source=items[int(rng.integers(len(items)))]['audio']
        fragment=np.interp(np.arange(0,len(source)-1,pitch),np.arange(len(source)),source)
        size=len(fragment)
        fade=min(overlap,size//3)
        ramp=np.linspace(0,1,fade)
        fragment[:fade]*=ramp;fragment[-fade:]*=ramp[::-1]
        if cursor+size>len(output):output=np.pad(output,(0,cursor+size-len(output)))
        output[cursor:cursor+size]+=fragment
        cursor+=max(1,size-overlap)
    return output[:n]

def make_stem(option,items,clip,seed):
    rng=np.random.default_rng(seed)
    motion=np.asarray(clip['motion'])
    active=motion>1e-9
    n=round(clip['duration']*SR)
    audio=np.zeros(n)
    support=np.zeros(n,dtype=bool)
    typical=np.median(motion[active])
    spans=[]
    for a,b in regions(active):
        start=round(a/clip['fps']*SR);end=min(n,round(b/clip['fps']*SR))
        size=end-start
        if size<=0:continue
        energy=np.clip((motion[a:b]/max(typical,1e-9))**.23,.48,1.4)
        envelope=np.interp(np.arange(size)/SR*clip['fps'],np.arange(len(energy)),energy)
        # Smooth tiny frame steps without extending the sound into a hold.
        envelope=gaussian_filter1d(envelope,SR*.005)
        fade=min(round(.008*SR),size//3)
        ramp=np.sin(np.linspace(0,np.pi/2,fade))**2
        envelope[:fade]*=ramp;envelope[-fade:]*=ramp[::-1]
        audio[start:end]=contact_texture(items,size,rng,option['pitch'])*envelope
        support[start:end]=True
        spans.append({'start':start/SR,'end':end/SR})
    # Equal active RMS gives a useful material comparison instead of a contest
    # won by the loudest file. Reserve peak headroom for stronger squeaks.
    level=np.sqrt(np.mean(audio[support]**2))
    audio*=10**(-39/20)/max(level,1e-12)
    peak=np.max(np.abs(audio))
    if peak>10**(-27/20):audio*=10**(-27/20)/peak
    assert np.max(np.abs(audio[~support]),initial=0)==0
    return audio,{'activeRmsDbfs':round(20*np.log10(np.sqrt(np.mean(audio[support]**2))),2),
                 'peakDbfs':round(20*np.log10(np.max(np.abs(audio))),2),
                 'silentOutsideVisibleContact':True,'contactSpans':spans,
                 'writingFrames':int(active.sum()),'frames':len(active)}

def wav(path,audio):
    path.parent.mkdir(parents=True,exist_ok=True)
    stereo=np.column_stack([audio,audio])
    write(path,SR,np.int16(np.clip(stereo,-1,1)*32767))
