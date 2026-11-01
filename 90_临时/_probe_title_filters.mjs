import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1600);

const pick = async (aria, val) => p.evaluate(([aria,val])=>{
  const s=[...document.querySelectorAll('.controls select')].find(x=>x.getAttribute('aria-label')===aria);
  if(!s) return 'NO_SELECT';
  s.value=val; s.onchange();
  return 'ok';
}, [aria,val]);
const facts = async () => p.evaluate(()=>({
  count: document.getElementById('count').textContent,
  cards: document.querySelectorAll('#grid > .i').length,
  vals: [...document.querySelectorAll('.controls select')].map(s=>s.getAttribute('aria-label')+':'+(s.value||'∅')),
  badges: [...document.querySelectorAll('#grid > .i')].slice(0,3).map(c=>c.querySelector('.i-badges')?.textContent.replace(/\s+/g,' ').trim()||null)
}));

console.log('pick1', await pick('特性','动态'));
await p.waitForTimeout(500);
console.log('dyn', JSON.stringify(await facts()));
await p.screenshot({path:'90_临时/shot_title_dyn.png'});

console.log('pick2', await pick('特性','美术字'));
await p.waitForTimeout(500);
console.log('art', JSON.stringify(await facts()));
await p.screenshot({path:'90_临时/shot_title_art.png'});

console.log('pick3', await pick('特性',''));
console.log('pick4', await pick('颜色','金'));
await p.waitForTimeout(500);
console.log('gold', JSON.stringify(await facts()));
console.log('errs', errs);
await b.close();
