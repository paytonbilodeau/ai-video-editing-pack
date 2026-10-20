from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter1d,maximum_filter1d
SR=48000
REV=Path(__file__).resolve().parents[1]/"sound-sources"


def normalize(x,active):
    x[~active]=0
    for _ in range(3):
        x*=10**(-39/20)/max(np.sqrt(np.mean(x[active]**2)),1e-12)
        envelope=gaussian_filter1d(maximum_filter1d(abs(x),481),SR*.003)
        x*=np.minimum(1,10**(-26/20)/np.maximum(envelope,1e-12))
    x*=10**(-39/20)/max(np.sqrt(np.mean(x[active]**2)),1e-12)
    return x
