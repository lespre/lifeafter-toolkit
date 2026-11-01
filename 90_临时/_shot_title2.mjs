import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
const errs=[]; p.on('pageerror',e=>errs.push(e.message));
await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1600);

// 1) 获取途径筛选：营地市长
await p.selectOption('.controls select:not([id])', '').catch(()=>{});
const selInfo = await p.evaluate(()=>{
  const s=[...document.querySelectorAll('.controls select')].find(x=>[...x.options].some(o=>o.text==='营地市长'));
  return s?{id:s.id||'(no id)', opts:[...s.options].map(o=>o.value+'='+o.text)}:null;
});
await p.evaluate(()=>{
  const s=[...document.querySelectorAll('.controls select')].find(x=>[...x.options].some(o=>o.text==='营地市长'));
  s.value='Mayor'; s.onchange();
});
await p.waitForTimeout(600);
const afterFilter = await p.evaluate(()=>({
  count: document.getElementById('count').textContent,
  cards: document.querySelectorAll('#grid > .i').length,
  heads: [...document.querySelectorAll('#grid > .tg-head')].map(h=>h.textContent.replace(/\s+/g,' ').trim()),
}));
await p.screenshot({path:'90_临时/shot_title_filter.png'});

// 2) 搜索「市长」看分组头是否随过滤结果重算
await p.evaluate(()=>{
  const s=[...document.querySelectorAll('.controls select')].find(x=>[...x.options].some(o=>o.text==='营地市长'));
  s.value=''; s.onchange();
});
await p.fill('#q','花'); await p.waitForTimeout(900);
const afterSearch = await p.evaluate(()=>({
  count: document.getElementById('count').textContent,
  cards: document.querySelectorAll('#grid > .i').length,
  heads: [...document.querySelectorAll('#grid > .tg-head')].map(h=>h.textContent.replace(/\s+/g,' ').trim()),
}));

// 3) 点开一张卡看 D2 详情是否完整（clamp 不影响详情）
await p.evaluate(()=>{ document.querySelector('#grid > .i .i-head').click(); });
await p.waitForTimeout(900);
const detail = await p.evaluate(()=>{
  const panel=document.querySelector('#d2Panel, .d2-panel, #detail, .side, #sidePanel');
  const open=[...document.querySelectorAll('[id*=d2],[class*=d2],[class*=detail]')].map(x=>x.id||x.className).slice(0,8);
  return {open, panelText: panel?panel.textContent.replace(/\s+/g,' ').slice(0,160):null};
});
await p.screenshot({path:'90_临时/shot_title_detail.png'});
console.log(JSON.stringify({selInfo, afterFilter, afterSearch, detail, errs},null,1));
await b.close();
