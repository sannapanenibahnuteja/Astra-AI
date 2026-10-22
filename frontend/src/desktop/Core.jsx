import { useEffect, useRef } from 'react';
import './particle-orb.css';
import { accents, surfaces } from './appearanceTheme';

const colors = ['#ff91b5','#62e6cf','#f0d785','#b5e987','#ab9ff1','#f4a17c','#7fc7ed','#ef9bc5'];
let seed = 173;
const random = () => { seed = (Math.imul(seed,1664525) + 1013904223) >>> 0; return seed / 4294967296; };
const particles = Array.from({length:3600},()=>{
  const y=1-random()*2, angle=random()*Math.PI*2, r=Math.sqrt(1-y*y);
  return {x:Math.cos(angle)*r,y,z:Math.sin(angle)*r,color:Math.floor(random()*8),length:.9+random()*.8};
});

export default function Core({state='idle',level=0,onClick,disabled=false,label,appearance={}}) {
  const canvas=useRef(null), signal=useRef({state,level,appearance});
  useEffect(()=>{ signal.current={state,level,appearance}; canvas.current?.dispatchEvent(new Event('orb-change')); },[state,level,appearance]);
  useEffect(()=>{
    const surface=canvas.current, context=surface.getContext('2d',{alpha:false});
    if(!context) return;
    const motion=matchMedia('(prefers-reduced-motion: reduce)');
    let frame=0,last=0,elapsed=0,energy=0,visible=true,size=0;
    const paused=()=>document.hidden || !visible || document.documentElement.classList.contains('background-mode');
    function draw(now) {
      frame=0;
      if(paused()) return;
      if(now-last>=1000/(signal.current.state==='idle'?18:30) || !last) {
        const dt=last?Math.min(.08,(now-last)/1000):.04; last=now;
        const settings=signal.current.appearance;
        const still=motion.matches || settings.motion==='off';
        if(!still) elapsed+=dt*({calm:.65,balanced:1,lively:1.6}[settings.orb_speed]||.65);
        const raw=Number(signal.current.level);
        const target=['listening','speaking'].includes(signal.current.state) && Number.isFinite(raw)?Math.max(0,Math.min(1,raw)):0;
        energy+=(target-energy)*(1-Math.exp(-dt*(target>energy?9:3.5)));
        const width=surface.clientWidth;
        if(width>0) {
          const ratio=Math.min(window.devicePixelRatio||1,1.5);
          if(size!==width || surface.width!==Math.round(width*ratio)) {size=width;surface.width=surface.height=Math.round(width*ratio);}
          context.setTransform(ratio,0,0,ratio,0,0); context.fillStyle=surfaces[settings.background]||'#000';context.fillRect(0,0,width,width);
          const breath=still?0:Math.sin(elapsed*.8)*.004;
          const radius=width*.445*(1+breath+(still?0:energy*.022));
          const yaw=elapsed*(signal.current.state==='thinking'?.095:.045), cy=Math.cos(yaw),sy=Math.sin(yaw),ct=Math.cos(.24),st=Math.sin(.24);
          const groups=Array.from({length:16},()=>[]);
          for(let i=0;i<particles.length;i+=(width<100?2:1)) {
            const p=particles[i];
            const x=p.x*cy+p.z*sy,z=p.z*cy-p.x*sy,y=p.y*ct-z*st,depth=z*ct+p.y*st;
            const tx=z,ty=x*st,len=Math.hypot(tx,ty)||1,dash=width/260*p.length*(depth>0?1.4:1);
            groups[p.color+(depth>0?8:0)].push([width/2+x*radius,width/2+y*radius,tx/len*dash,ty/len*dash]);
          }
          context.lineCap='round';context.lineWidth=Math.max(.65,width/195);
          for(let g=0;g<groups.length;g++) {
            context.strokeStyle=settings.orb_color==='accent'?(accents[settings.accent]||accents.violet):colors[g%8];context.globalAlpha=g<8?.48:.92+energy*.08;context.beginPath();
            for(const [x,y,dx,dy] of groups[g]) {context.moveTo(x-dx,y-dy);context.lineTo(x+dx,y+dy);}
            context.stroke();
          }
          context.globalAlpha=1;
        }
      }
      if(!motion.matches && signal.current.appearance.motion!=='off') frame=requestAnimationFrame(draw);
    }
    function resume(){cancelAnimationFrame(frame);frame=0;last=0;if(!paused()) frame=requestAnimationFrame(draw);}
    const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;resume();});observer.observe(surface);
    const resize=new ResizeObserver(resume);resize.observe(surface);
    const background=new MutationObserver(resume);background.observe(document.documentElement,{attributes:true,attributeFilter:['class']});
    surface.addEventListener('orb-change',resume);document.addEventListener('visibilitychange',resume);motion.addEventListener('change',resume);resume();
    return ()=>{surface.removeEventListener('orb-change',resume);cancelAnimationFrame(frame);observer.disconnect();resize.disconnect();background.disconnect();document.removeEventListener('visibilitychange',resume);motion.removeEventListener('change',resume);};
  },[]);
  const Surface=onClick?'button':'div';
  return <Surface type={onClick?'button':undefined} className={`core-scene particle-core ${state} ${onClick?'interactive-core':''}`} onClick={onClick} disabled={onClick?disabled:undefined} aria-label={label||`Bob ${state}`} title={onClick?label:undefined}><canvas ref={canvas} className="particle-canvas" aria-hidden="true" /></Surface>;
}
