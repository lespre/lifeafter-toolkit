// CDP 探针 v2：卡面品级/魅力值 + 排序控件 + 筛选联动 + 折叠区
import fs from "node:fs";

const PORT = process.argv[2] || "9223";
const OUT = process.argv[3] || "E:/la拆包项目/04_站点/web/artifacts/fashion_rebuild";
const BASE = process.argv[4] || "http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=rb4";

async function listTargets() {
  for (let i = 0; i < 40; i++) {
    try {
      const j = await (await fetch(`http://127.0.0.1:${PORT}/json`)).json();
      const p = j.find((t) => t.type === "page" && t.webSocketDebuggerUrl);
      if (p) return p;
    } catch (e) {}
    await new Promise((r) => setTimeout(r, 250));
  }
  throw new Error("no cdp target");
}
const target = await listTargets();
const ws = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
let seq = 0;
const pending = new Map();
const events = [];
ws.onmessage = (ev) => {
  const m = JSON.parse(ev.data);
  if (m.id && pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
  else if (m.method) events.push(m);
};
const send = (method, params = {}) => {
  const id = ++seq;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((res) => pending.set(id, res));
};
async function ev(expr) {
  const r = await send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result && r.result.exceptionDetails) return { error: r.result.exceptionDetails.text };
  return r.result && r.result.result ? r.result.result.value : undefined;
}
async function shot(name) {
  const r = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: false });
  fs.writeFileSync(`${OUT}/${name}`, Buffer.from(r.result.data, "base64"));
  return `${OUT}/${name}`;
}
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
await send("Runtime.enable"); await send("Page.enable");
await send("Page.navigate", { url: BASE });
for (let i = 0; i < 60; i++) { if (await ev("document.querySelectorAll('.fcard').length") > 100) break; await sleep(250); }
await sleep(700);
console.log("exceptions:", JSON.stringify(events.filter((e) => e.method === "Runtime.exceptionThrown").map((e) => e.params.exceptionDetails.text)));

const snap = () => ev(`(() => {
  const cards=[...document.querySelectorAll('.fcard')];
  const pick=(c)=>(({name:c.querySelector('.fr-name').textContent, grade:(c.querySelector('.fr-grade')||{}).textContent||'', sub:c.querySelector('.fr-sub').textContent.replace(/\\s+/g,' ').trim()}));
  return {cards:cards.length,
    count:document.getElementById('count').textContent.trim(),
    pills:document.getElementById('pills').textContent.replace(/\\s+/g,' ').trim(),
    sort:(document.getElementById('frSort')||{}).value,
    pressed:[...document.querySelectorAll('.fr-chip')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent.trim()).join('|'),
    gradeBadges:document.querySelectorAll('.fr-grade').length,
    charmBadges:document.querySelectorAll('.fr-charm').length,
    charmNA:document.querySelectorAll('.fr-charm.na').length,
    first:cards.slice(0,4).map(pick),
    last:cards.slice(-2).map(pick),
    url:location.search};
})()`);

console.log("initial:", JSON.stringify(await snap()));
console.log(await shot("fashion_top.png"));

// 排序：魅力值 ↓
await ev(`(() => { const s=document.getElementById('frSort'); s.value='charm_desc'; s.dispatchEvent(new Event('change',{bubbles:true})); })()`);
await sleep(600);
let s = await snap();
console.log("sort charm_desc:", JSON.stringify({sort:s.sort, count:s.count, first:s.first.map(x=>x.name+':'+x.sub), last:s.last.map(x=>x.name+':'+x.sub), url:s.url}));
console.log(await shot("fashion_sort_charm_desc.png"));

// 排序：魅力值 ↑
await ev(`(() => { const s=document.getElementById('frSort'); s.value='charm_asc'; s.dispatchEvent(new Event('change',{bubbles:true})); })()`);
await sleep(500);
s = await snap();
console.log("sort charm_asc:", JSON.stringify({first:s.first.map(x=>x.name+':'+x.sub), last:s.last.map(x=>x.name+':'+x.sub)}));

// 排序 + 筛选联动：头饰 + 魅力值 ↓
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim().startsWith('头饰')).click()`);
await sleep(500);
await ev(`(() => { const s=document.getElementById('frSort'); s.value='charm_desc'; s.dispatchEvent(new Event('change',{bubbles:true})); })()`);
await sleep(500);
s = await snap();
console.log("hat+charm_desc:", JSON.stringify({cards:s.cards, count:s.count, pressed:s.pressed, first:s.first.map(x=>x.name+':'+x.sub), url:s.url}));
console.log(await shot("fashion_hat_charm_desc.png"));

// 展开折叠区
await ev(`(() => { const d=document.querySelector('.fcard details.tech'); d.open=true; d.scrollIntoView({block:'center'}); })()`);
await sleep(400);
console.log("details keys:", JSON.stringify(await ev(`[...document.querySelectorAll('.fcard details.tech')][0].querySelectorAll('.k').length`)));
console.log(await shot("fashion_card_details.png"));
ws.close();
