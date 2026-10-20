function renderFrame(seconds,target){
  const canvas=target||document.getElementById('c'),g=canvas.getContext('2d');
  const frame=Math.max(0,Math.min(NFRAMES-1,Math.round(seconds*FPS))),t=frame/FPS;
  g.setTransform(1,0,0,1,0,0);g.globalAlpha=1;g.globalCompositeOperation='source-over';g.clearRect(0,0,canvas.width,canvas.height);
  // Portrait uses the established graphic region. Landscape uses a wider,
  // centered region with room above and below. No crop of a portrait export.
  const portrait=W<H,scale=portrait?W/1080:Math.min(W/1120,H/1000);
  g.translate(W/2,H*(portrait?0.45:0.5));g.scale(scale,scale);g.translate(-540,-864);
  const i=Math.min(2,Math.floor(t/3)),local=t-i*3;
  amScene(g,t);
  const textIn=i===0?1:amProgress(local,0,.20);
  const textOut=i===2?1:1-amProgress(local,2.80,3);
  g.save();g.globalAlpha=textIn*textOut;
  amText(g,CUSTOMER.labels[i],540,565,94);
  amText(g,CUSTOMER.lines[i],540,1165,48,AM.muted);
  g.restore();
  g.setTransform(1,0,0,1,0,0);
  return i+1;
}
window.renderFrame=renderFrame;
window.renderBoard=()=>{
  const board=document.createElement('canvas');board.width=1080;board.height=720;
  const g=board.getContext('2d');g.fillStyle=AM.black;g.fillRect(0,0,1080,720);
  const frame=document.createElement('canvas');frame.width=W;frame.height=H;
  TIMELINE.board.forEach((b,i)=>{renderFrame(b.t,frame);const scale=Math.min(340/W,640/H);g.drawImage(frame,i*360+(360-W*scale)/2,0,W*scale,H*scale);amText(g,`${b.t.toFixed(1)} s`,i*360+180,695,24,AM.muted);});
  return board;
};
renderFrame(Number(new URLSearchParams(location.search).get('t')||0));
</script></body></html>
