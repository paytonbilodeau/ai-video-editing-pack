import numpy as np
from scipy.ndimage import gaussian_filter,gaussian_filter1d,maximum_filter1d
from scipy.signal import stft,istft,butter,sosfiltfilt
import gentlemen_marker_options as original
SR=48000


def squeak_bank(name):
    path = original.SOURCES/f'{name}.mp3'
    x = original.read_audio(path)
    freq, times, spectrum = stft(x, SR, nperseg=2048, noverlap=1568)
    used = (freq >= 1100) & (freq <= 6500)
    power = abs(spectrum[used])**2
    energy = power.sum(axis=0)
    peaks = power.argmax(axis=0)
    concentration = np.array([power[max(0,k-2):k+3,i].sum() for i,k in enumerate(peaks)])/np.maximum(energy,1e-16)
    valid = (times > 2) & (times < len(x)/SR-.5) & (energy > np.quantile(energy,.55))
    candidates = []
    for start in np.arange(2,len(x)/SR-.8,.08):
        mask = (times >= start) & (times < start+.24) & valid
        if mask.sum() < 16:
            continue
        score = float(np.median(concentration[mask]))
        variation = float(np.std(freq[used][peaks[mask]]))
        if variation < 800:
            candidates.append((score,float(start)))
    chosen = []
    for score,start in sorted(candidates,reverse=True):
        if any(abs(start - item['start']) < .24 for item in chosen):
            continue
        seg = x[round(start*SR):round((start+.24)*SR)]
        f,t,z = stft(seg,SR,nperseg=1024,noverlap=768)
        magnitude = abs(z)
        # Retain the original phase and changing resonances. Reduce broad
        # friction around peaks rather than generating a whistling oscillator.
        local = gaussian_filter1d(magnitude,8,axis=0)
        mask = np.clip((magnitude/(local+1e-10)-1.10)/2.1,0,1)**.6
        mask = gaussian_filter(mask,(1,1.3))
        _, cleaned = istft(z*(.05+.95*mask),SR,nperseg=1024,noverlap=768)
        cleaned = cleaned[:len(seg)]
        cleaned = sosfiltfilt(butter(3,[1100,6500],btype='bandpass',fs=SR,output='sos'),cleaned)
        # Preserve most natural pressure dynamics; no tanh flattening here.
        envelope = gaussian_filter1d(cleaned**2,SR*.025)**.5
        cleaned /= np.maximum(envelope,np.median(envelope)*.7+1e-10)**.30
        cleaned /= max(np.sqrt(np.mean(cleaned**2)),1e-10)
        if np.max(np.abs(cleaned)) > 6:
            continue  # Discard cap/handling-like impacts rather than flattening them.
        chosen.append({'start':round(start,3),'end':round(start+.24,3),
                       'concentration':score,'audio':cleaned})
        if len(chosen) == 18:
            break
    if len(chosen) < 8:
        raise RuntimeError(f'Not enough recorded squeak fragments: {name}')
    return chosen
