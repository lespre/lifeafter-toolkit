import { chromium } from 'file:///C:/Users/Administrator/AppData/Local/hermes/hermes-agent/node_modules/playwright/index.mjs';
const b = await chromium.launch({ executablePath: 'C:/Users/Administrator/AppData/Local/ms-playwright/chromium_headless_shell-1248/chrome-headless-shell-win64/chrome-headless-shell.exe' });
const p = await b.newPage({ viewport: { width: 1500, height: 1000 } });
await p.goto('http://127.0.0.1:8765/board.html?b=title_catalog', { waitUntil:'domcontentloaded' });
await p.waitForTimeout(1600);
console.log(JSON.stringify(await p.evaluate(()=>[...document.querySelectorAll('.controls select')].map(s=>({
  id:s.id||'(none)', aria:s.getAttribute('aria-label'), opts:[...s.options].map(o=>`[${o.value}]${o.text}`)
}))),null,1));
await b.close();
