import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });

async function run(w, h, file, tag){
  const p = await b.newPage({ viewport: { width: w, height: h } });
  const errs=[]; p.on('pageerror',e=>errs.push(e.message));
  await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(1800);
  const facts = await p.evaluate(()=>{
    const q=s=>document.querySelector(s), qa=s=>Array.from(document.querySelectorAll(s));
    const heads=qa('#grid > .tg-head');
    const cards=qa('#grid > .i');
    const first=cards[0];
    const cols=getComputedStyle(q('#grid')).gridTemplateColumns.split(' ').length;
    return {
      heads: heads.length,
      headTexts: heads.slice(0,20).map(x=>x.textContent.replace(/\s+/g,' ').trim()),
      cards: cards.length,
      cols,
      cardH: first?Math.round(first.getBoundingClientRect().height):0,
      count: (q('#count')||{}).textContent,
      selects: qa('.controls select').map(s=>({v:s.value,o:s.options.length})),
      hScroll: document.documentElement.scrollWidth > document.documentElement.clientWidth+2,
      cardTags: first?qa('.state-tag, .state-pill').length:0
    };
  });
  await p.screenshot({ path: file });
  // 滚到中段再看分组头吸顶
  await p.evaluate(()=>window.scrollTo(0, 1400)); await p.waitForTimeout(700);
  await p.screenshot({ path: file.replace('.png','_mid.png') });
  console.log(tag, JSON.stringify(facts,null,1), 'errors', errs);
  await p.close();
}
await run(1500, 1000, '90_临时/shot_title_d.png', 'desktop');
await run(390, 844, '90_临时/shot_title_m.png', 'mobile');
await b.close();
