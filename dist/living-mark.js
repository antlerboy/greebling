(() => {
 'use strict';
 const host=document.getElementById('living-mark'),next=document.getElementById('next-mark'),pause=document.getElementById('pause-mark');
 const preference=matchMedia('(prefers-reduced-motion: reduce)'); let paused=preference.matches,marks=[],last='',selected=null;
 function sync(){ const v=host.querySelector('video'); if(v){if(paused||document.hidden)v.pause();else v.play().catch(()=>{});} pause.textContent=paused?'Play motion':'Pause motion';pause.setAttribute('aria-pressed',String(paused)); }
 function show(m){selected=m;last=m.id;const element=document.createElement(m.kind==='video'?'video':'img');element.src='/'+m.src; if(m.kind==='video'){element.poster='/'+m.poster;element.muted=true;element.defaultMuted=true;element.loop=true;element.playsInline=true;element.preload='metadata';element.setAttribute('aria-label',m.description||'An unfurling living mark');element.addEventListener('error',()=>{const still=document.createElement('img');still.src='/'+m.poster;still.alt=m.description||'A living mark';host.replaceChildren(still);},{once:true});}else{element.alt=m.description||'A living mark';element.decoding='async';}host.replaceChildren(element);sync();}
 function choose(initial=false){let pool=marks.filter(m=>m.id!==last && (!initial||m.kind==='video'));if(!pool.length)pool=marks;if(!pool.length)return; const n=new Uint32Array(1);crypto.getRandomValues(n);show(pool[n[0]%pool.length]);}
 next.addEventListener('click',()=>choose()); pause.addEventListener('click',()=>{paused=!paused;sync();}); preference.addEventListener('change',e=>{paused=e.matches;sync();});document.addEventListener('visibilitychange',sync);sync();
 fetch('/assets/living-marks/manifest.json').then(r=>{if(!r.ok)throw Error('manifest');return r.json();}).then(d=>{marks=d.marks.filter(m=>m.id&&m.src);choose(true);}).catch(()=>{next.disabled=true;});
})();
