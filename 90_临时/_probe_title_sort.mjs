import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1600);

const facts = async () => p.evaluate(()=>{
  const cells=[...document.querySelectorAll('#grid > *')];
  const heads=[...document.querySelectorAll('#grid > .tg-head')];
  const ids=[]; let firstHead=null;
  for(const c of cells){
    if(c.classList.contains('tg-head')){ if(firstHead===null){firstHead=c;continue;} break; }
    if(firstHead&&c.classList.contains('i')){
      const t=c.querySelector('.i-id')?.textContent||'';
      ids.push(Number(t.replace(/[^\d]/g,''))||0);
    }
  }
  const sel=document.getElementById('fOrder');
  return {
    visible:getComputedStyle(sel).display!=='none',
    value:sel.value,
    firstGroupName:firstHead?.querySelector('.tg-name')?.textContent||'',
    firstGroupIds:ids.slice(0,8),
    asc:ids.every((x,i)=>i===0||x>=ids[i-1]),
    desc:ids.every((x,i)=>i===0||x<=ids[i-1]),
    cards:document.querySelectorAll('#grid > .i').length,
    heads:heads.length,
    count:document.getElementById('count').textContent,
    hScroll:document.documentElement.scrollWidth>document.documentElement.clientWidth
  };
});
const setSort = async v => p.evaluate(v=>{
  const s=document.getElementById('fOrder');
  s.value=v; s.dispatchEvent(new Event('change'));
}, v);

console.log('asc ', JSON.stringify(await facts()));
await setSort('id_desc'); await p.waitForTimeout(600);
console.log('desc', JSON.stringify(await facts()));
await p.screenshot({path:'90_临时/shot_title_sort_desc.png'});
await setSort('id_asc'); await p.waitForTimeout(600);
console.log('back', JSON.stringify(await facts()));
console.log('errs', errs);
await b.close();
