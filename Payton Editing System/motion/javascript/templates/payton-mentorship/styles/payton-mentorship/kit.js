// Payton-derived starting palette. Edit this working copy to customize the palette.
const AM=CUSTOMER;
const STYLE={name:'payton-mentorship',paper:AM.black,ones:true};
function amText(g,text,x,y,size,color=AM.ink){
  g.save();g.fillStyle=color;g.textAlign='center';g.font=`800 ${size}px ${CUSTOMER.font}`;g.fillText(text,x,y);g.restore();
}
function amCircle(g,x,y,r,color){g.beginPath();g.arc(x,y,r,0,Math.PI*2);g.fillStyle=color;g.fill();}
function amLine(g,points,color=AM.depth,width=5){
  g.beginPath();points.forEach(([x,y],i)=>i?g.lineTo(x,y):g.moveTo(x,y));g.strokeStyle=color;g.lineWidth=width;g.lineCap='round';g.lineJoin='round';g.stroke();
}
function amFrame(g,x,y,w,h,accent=false){
  g.save();g.fillStyle='rgba(0,0,0,0.94)';g.strokeStyle=accent?AM.mint:AM.depth;g.lineWidth=5;
  g.beginPath();g.roundRect(x,y,w,h,22);g.fill();g.stroke();g.restore();
}
