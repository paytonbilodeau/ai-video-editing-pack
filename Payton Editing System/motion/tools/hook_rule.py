"""Hook-card duration rule used by render_short.py (Payton-derived starting preference; customer profile may change it): the card stays for the whole short; when a phone or
desktop layout arrives it ends 0.1 s before that first screen layout and never returns. Camera-only layout changes do not end it."""
CAMERA_LAYOUTS={'cam_full','cam_in_phone'}
def hook_end_seconds(S, start_f, dur, fps=30):
    first_change=next(((seg[0]-start_f)/fps for seg in S['segments'][1:] if seg[2] not in CAMERA_LAYOUTS and (len(seg)<4)),None)
    return round(first_change-0.1,2) if first_change is not None else round(dur,2)
