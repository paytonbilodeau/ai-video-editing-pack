import React, {useLayoutEffect, useRef} from 'react';
import {cancelRender, continueRender, delayRender, useCurrentFrame, useVideoConfig} from 'remotion';

/** Serve the built HTML from this Remotion project's public folder (same origin).
 * Width and height match piece.json; the host fps may differ. Keep host duration
 * within source duration; frame time is quantized to the nearest source frame.
 * Audio is separate: add the exported WAV using Remotion's Audio component.
 */
export const AnimationFrame: React.FC<{src: string}> = ({src}) => {
  const iframe = useRef<HTMLIFrameElement>(null);
  const frame = useCurrentFrame();
  const {fps, width, height} = useVideoConfig();
  const serial = useRef(0);
  useLayoutEffect(() => {
    const handle = delayRender(`JavaScript animation frame ${frame}`, {timeoutInMilliseconds: 15000});
    const id = ++serial.current;
    const node = iframe.current!;
    let released = false;
    const release = () => {if (!released) {released = true; continueRender(handle);}};
    const send = () => node.contentWindow?.postMessage({type:'animation:frame',id,frame,fps,width,height}, location.origin);
    const onMessage = (event: MessageEvent) => {
      if (event.source !== node.contentWindow || event.origin !== location.origin || event.data?.type !== 'animation:ack' || event.data.id !== id || event.data.frame !== frame) return;
      if (!event.data.ok) {cancelRender(new Error(event.data.error)); return;}
      release();
    };
    window.addEventListener('message', onMessage);
    node.addEventListener('load', send);
    send();
    return () => {window.removeEventListener('message',onMessage); node.removeEventListener('load',send); release();};
  }, [frame,fps,width,height,src]);
  return <iframe ref={iframe} src={src + (src.includes('?') ? '&' : '?') + 'export=1'} title="JavaScript animation" style={{border:0,width,height,display:'block'}} />;
};
