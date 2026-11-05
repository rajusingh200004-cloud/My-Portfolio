const $=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const E=s=>String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const RM=matchMedia('(prefers-reduced-motion:reduce)').matches;
function load(cb){fetch('data.json?v='+Date.now()).then(r=>r.json()).then(cb).catch(e=>{console.error(e);document.body.insertAdjacentHTML('beforeend','<p style="position:fixed;top:45%;left:0;right:0;text-align:center;color:#999;font:14px sans-serif;padding:0 24px;z-index:999">Open through GitHub Pages (or run python -m http.server) so data.json can load.</p>')})}
function tipOf(d,s,g){const t=(d.toolYears||[]).find(x=>x.tool.toLowerCase().includes(s.toLowerCase()));
  const n=d.experience.filter(e=>e.tools.some(u=>u.toLowerCase()===s.toLowerCase())).length;
  return `<b>${E(s)}</b><br>${[t&&t.years+' hands-on',n&&`Used in ${n} of ${d.experience.length} roles`].filter(Boolean).join('<br>')||E(g)}`}
function photo(d,cls=''){const i=d.name.split(' ').map(w=>w[0]).join('').slice(0,2);
  return `<img class="${cls}" src="assets/photo.jpg" alt="Portrait of ${E(d.name)}" onerror="this.outerHTML='<div class=ph>${E(i)}</div>'">`}
function viz(n){let h=0;for(const c of n)h=(h*31+c.charCodeAt(0))>>>0;const r=()=>(h=(h*1664525+1013904223)>>>0)/4294967296;let b='',p=[];
  for(let i=0;i<10;i++){const v=20+r()*85;b+=`<rect x="${16+i*38}" y="${150-v}" width="22" height="${v}" rx="2" fill="currentColor" opacity="${.25+r()*.5}"/>`;p.push(`${27+i*38},${130-r()*90}`)}
  return `<svg viewBox="0 0 400 170" preserveAspectRatio="none" aria-hidden="true">${b}<polyline points="${p.join(' ')}" fill="none" stroke="#fff" stroke-width="2" opacity=".8"/><line x1="8" y1="152" x2="392" y2="152" stroke="currentColor" opacity=".35"/></svg>`}
function behave(){
  const count=el=>{const m=el.dataset.v.match(/^(\d+(?:\.\d+)?)(.*)$/);if(!m||RM)return;const n=+m[1],dec=(m[1].split('.')[1]||'').length,t0=performance.now();
    (function f(t){const p=Math.min((t-t0)/1200,1),e=1-Math.pow(1-p,3);el.textContent=(n*e).toFixed(dec)+m[2];if(p<1)requestAnimationFrame(f)})(t0)};
  const io=new IntersectionObserver(es=>es.forEach(x=>{if(!x.isIntersecting)return;const t=x.target;t.classList.add('in');io.unobserve(t);t.querySelectorAll('.num').forEach(count);if(t.classList.contains('num'))count(t)}),{threshold:.12});
  $$('.rv').forEach((el,i)=>{el.style.transitionDelay=(i%4)*60+'ms';io.observe(el)});
  const tip=$('#tip'),SEL='.tilt,.foc,[data-tip]';let tt;const clear=()=>$$('.on').forEach(e=>e.classList.remove('on'));
  $$(SEL).forEach(el=>{
    el.addEventListener('pointerenter',e=>{if(e.pointerType!=='touch'){clear();el.classList.add('on')}});
    el.addEventListener('pointerleave',e=>{if(e.pointerType==='touch')return;el.classList.remove('on');if(el.classList.contains('tilt'))el.style.transform=''});
    el.addEventListener('pointerdown',e=>{if(e.pointerType!=='touch')return;const w=el.classList.contains('on');clear();if(!w)el.classList.add('on')});
    if(el.classList.contains('tilt'))el.addEventListener('pointermove',e=>{const r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
      el.style.setProperty('--mx',(x+.5)*100+'%');el.style.setProperty('--my',(y+.5)*100+'%');
      if(e.pointerType!=='touch')el.style.transform=`perspective(800px) rotateX(${-y*9}deg) rotateY(${x*11}deg) scale(1.03)`})});
  document.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'&&!e.target.closest(SEL))clear()});
  $$('[data-tip]').forEach(el=>{const show=e=>{tip.innerHTML=el.dataset.tip;tip.classList.add('s');const w=tip.offsetWidth;tip.style.left=Math.min(Math.max(8,e.clientX-w/2),innerWidth-w-8)+'px';tip.style.top=Math.max(8,e.clientY-tip.offsetHeight-18)+'px'};
    el.addEventListener('pointermove',show);el.addEventListener('pointerenter',show);el.addEventListener('pointerleave',()=>tip.classList.remove('s'));
    el.addEventListener('pointerdown',e=>{if(e.pointerType==='touch'){show(e);clearTimeout(tt);tt=setTimeout(()=>tip.classList.remove('s'),2600)}})});
  $$('.acc-h').forEach(b=>b.onclick=()=>b.closest('.acc').classList.toggle('open'));
  if($('#bb'))$('#bb').onclick=()=>$('#bb').setAttribute('aria-expanded',$('#mm').classList.toggle('show'));
  $$('#mm a').forEach(a=>a.onclick=()=>$('#mm').classList.remove('show'));
  const links=$$('.nl a'),so=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting)links.forEach(a=>a.classList.toggle('cur',a.hash==='#'+x.target.id))}),{rootMargin:'-45% 0px -50% 0px'});
  $$('section[id]').forEach(s=>so.observe(s));
  const bar=$('#bar'),prog=()=>{window.S=scrollY/Math.max(1,document.documentElement.scrollHeight-innerHeight);if(bar)bar.style.width=S*100+'%'};addEventListener('scroll',prog,{passive:true});prog();
}
