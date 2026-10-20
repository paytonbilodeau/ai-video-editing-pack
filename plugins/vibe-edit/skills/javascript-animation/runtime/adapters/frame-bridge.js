// Only same-origin parent requests are accepted. Seconds never come from wall time.
// The host owns the frame; out-of-range frames fail rather than wrapping silently.
{
  const ready = window.ASSETS_READY || Promise.resolve();
  window.ANIMATION_READY = ready.then(() => document.fonts.ready).then(() => true);
  window.addEventListener('message', async event => {
    const m = event.data;
    if (event.source !== parent || event.origin !== location.origin || m?.type !== 'animation:frame') return;
    const response = {type:'animation:ack', id:m.id, frame:m.frame};
    try {
      await window.ANIMATION_READY;
      const t = window.TIMELINE;
      if (!Number.isInteger(m.frame) || m.frame < 0 || !Number.isFinite(m.fps) || m.fps <= 0 || m.frame / m.fps >= t.duration || m.width !== t.width || m.height !== t.height) throw Error('host frame or composition metadata mismatch');
      const nativeFrame = Math.min(t.frames - 1, Math.round(m.frame / m.fps * t.fps));
      window.renderFrame(nativeFrame / t.fps);
      parent.postMessage({...response, ok:true}, event.origin);
    } catch (error) {
      parent.postMessage({...response, ok:false, error:String(error.message)}, event.origin);
    }
  });
}
