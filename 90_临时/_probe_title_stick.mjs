import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
for (const [w,h,tag] of [[1500,1000,'desktop'],[390,844,'mobile']]){
  const p = await b.newPage({ viewport: { width: w, height: h } });
  await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
  await p.waitForTimeout(1500);
  const at0 = await p.evaluate(()=>{
    const c=document.querySelector('.controls'); const hd=document.querySelector('header.hd2');
    const cs=getComputedStyle(c), hs=getComputedStyle(hd||document.body);
    return {ctlPos:cs.position, ctlTop:cs.top, ctlH:c.offsetHeight, hdPos:hs.position, tgTop:getComputedStyle(document.documentElement).getPropertyValue('--tg-top')};
  });
  await p.evaluate(()=>window.scrollTo(0,1400)); await p.waitForTimeout(500);
  const at1400 = await p.evaluate(()=>{
    const c=document.querySelector('.controls'); const t=[...document.querySelectorAll('#grid>.tg-head')].find(x=>x.getBoundingClientRect().top>0);
    return {ctlRectTop:Math.round(c.getBoundingClientRect().top), ctlBottom:Math.round(c.getBoundingClientRect().bottom),
      tgRectTop:t?Math.round(t.getBoundingClientRect().top):null, tgText:t?t.textContent.replace(/\s+/g,' ').trim():null};
  });
  console.log(tag, JSON.stringify({at0,at1400},null,1));
  await p.close();
}
await b.close();
