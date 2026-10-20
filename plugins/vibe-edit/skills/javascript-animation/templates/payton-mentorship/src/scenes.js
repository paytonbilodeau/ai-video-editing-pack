// A single persistent point carries time -> frame -> sequence.
// Every shape is a function of time, so random seeking preserves the motion.
const amSmooth=x=>{const u=amClamp(x);return u*u*u*(u*(u*6-15)+10);};
function amProgress(t,start,end){return amSmooth((t-start)/(end-start));}
function amShape(g,cx,cy,w,h,r,alpha=1){
  g.save();g.globalAlpha*=alpha;g.fillStyle=AM.black;g.strokeStyle=AM.mint;g.lineWidth=5;
  g.beginPath();g.roundRect(cx-w/2,cy-h/2,w,h,r);g.fill();g.stroke();g.restore();
}
function amScene(g,t){
  const cx=540,cy=870;
  const capture=amProgress(t,2.10,3.45),split=amProgress(t,4.80,6.25);
  const orbit=amProgress(t,0,2.10),angle=-Math.PI/2+orbit*Math.PI*1.42;
  const w=amMix(amMix(360,540,capture),220,split);
  const h=amMix(amMix(360,350,capture),290,split);
  const corner=amMix(180,22,capture);
  const pointX=amMix(cx+180*Math.cos(angle),cx,capture);
  const pointY=amMix(cy+180*Math.sin(angle),cy,capture);

  // Copies emerge from the same frame before separating to either side.
  if(split>0){
    for(const side of [-1,1]){
      const x=cx+side*255*split;
      amShape(g,x,cy,w,h,Math.min(corner,w/2,h/2),split);
      g.save();g.globalAlpha*=split;
      amCircle(g,x,cy+side*68*split,amMix(22,25,split),AM.mint);g.restore();
    }
  }
  amShape(g,cx,cy,w,h,Math.min(corner,w/2,h/2));
  if(capture<1){
    g.save();g.globalAlpha*=1-capture;
    for(let k=0;k<12;k++){const a=k*Math.PI/6;amLine(g,[[cx+162*Math.cos(a),cy+162*Math.sin(a)],[cx+175*Math.cos(a),cy+175*Math.sin(a)]],AM.muted,3);}
    amLine(g,[[cx,cy],[pointX,pointY]],AM.mint,5);
    amCircle(g,cx,cy,8,AM.ink);g.restore();
  }
  amCircle(g,pointX,pointY,amMix(22,25,capture),AM.mint);

  // A measured playback sweep follows the completed sequence, then settles.
  const reveal=amProgress(t,6.20,6.65),play=amProgress(t,6.65,8.55);
  if(reveal>0){
    g.save();g.globalAlpha*=reveal;
    amLine(g,[[215,1080],[865,1080]],AM.depth,4);
    amLine(g,[[215,1080],[215+650*play,1080]],AM.mint,4);
    amCircle(g,215+650*play,1080,9,AM.mint);g.restore();
  }
}
