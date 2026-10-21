// CDP 交互探针：点击时装筛选 chip、读统计、截图（headless Chrome，临时 profile）
import fs from "node:fs";

const PORT = process.argv[2] || "9223";
const OUT = process.argv[3] || "E:/la拆包项目/04_站点/web/artifacts/fashion_rebuild";
const BASE = process.argv[4] || "http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=rb3";

async function listTargets() {
  for (let i = 0; i < 40; i++) {
    try {
      const r = await fetch(`http://127.0.0.1:${PORT}/json`);
      const j = await r.json();
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
function send(method, params = {}) {
  const id = ++seq;
  ws.send(JSON.stringify({ id, method, params }));
  return new Promise((res) => pending.set(id, res));
}
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

await send("Runtime.enable");
await send("Page.enable");
await send("Page.navigate", { url: BASE });
for (let i = 0; i < 60; i++) { if (await ev("document.querySelectorAll('.fcard').length") > 100) break; await sleep(250); }
await sleep(600);

const errs = events.filter((e) => e.method === "Runtime.exceptionThrown").map((e) => e.params.exceptionDetails.text);
console.log("exceptions:", JSON.stringify(errs));
console.log("initial:", JSON.stringify(await ev(`(() => ({
  cards: document.querySelectorAll('.fcard').length,
  count: document.getElementById('count').textContent.trim(),
  pills: document.getElementById('pills').textContent.replace(/\\s+/g,' ').trim(),
  chips: [...document.querySelectorAll('.fr-chip')].map(b=>b.textContent.trim()).join('|'),
  pressed: [...document.querySelectorAll('.fr-chip')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent.trim()).join('|'),
  railMax: Math.max(...[...document.querySelectorAll('.fr-rail')].map(r=>r.querySelectorAll('figure').length)),
  headText: [...document.querySelectorAll('.fcard')].slice(0,3).map(c=>c.querySelector('.fr-name').textContent+' / '+c.querySelector('.fr-sub').textContent.replace(/\\s+/g,' ').trim()),
  detailRows: document.querySelectorAll('.fcard .fr-kv .k').length,
  imgs: document.images.length
}))()`)));

// 点「头饰」
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim().startsWith('头饰')).click()`);
await sleep(500);
console.log("after hat:", JSON.stringify(await ev(`(() => ({
  cards: document.querySelectorAll('.fcard').length,
  count: document.getElementById('count').textContent.trim(),
  pressed: [...document.querySelectorAll('.fr-chip')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent.trim()).join('|'),
  url: location.search
}))()`)));
console.log(await shot("fashion_filter_hat.png"));

// 再点「背包」→ 多选（头饰+背包）
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim().startsWith('背包')).click()`);
await sleep(500);
console.log("after hat+bag:", JSON.stringify(await ev(`(() => ({
  cards: document.querySelectorAll('.fcard').length,
  pressed: [...document.querySelectorAll('.fr-chip')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent.trim()).join('|'),
  url: location.search
}))()`)));

// 清空部位 → 期限=限时 + 图示=有图
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim()==='全部').click()`);
await sleep(300);
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim().startsWith('限时')).click()`);
await sleep(300);
await ev(`[...document.querySelectorAll('.fr-chip')].find(b=>b.textContent.trim().startsWith('有图')).click()`);
await sleep(600);
console.log("timed+img:", JSON.stringify(await ev(`(() => ({
  cards: document.querySelectorAll('.fcard').length,
  count: document.getElementById('count').textContent.trim(),
  pressed: [...document.querySelectorAll('.fr-chip')].filter(b=>b.getAttribute('aria-pressed')==='true').map(b=>b.textContent.trim()).join('|'),
  url: location.search
}))()`)));
console.log(await shot("fashion_filter_timed_img.png"));

// 搜索 + 筛选叠加
await ev(`(() => { const q=document.getElementById('q'); q.value='背包'; q.dispatchEvent(new Event('input',{bubbles:true})); })()`);
await sleep(700);
console.log("search+filter:", JSON.stringify(await ev(`(() => ({
  cards: document.querySelectorAll('.fcard').length,
  count: document.getElementById('count').textContent.trim(),
  pills: document.getElementById('pills').textContent.replace(/\\s+/g,' ').trim()
}))()`)));
console.log(await shot("fashion_search_stack.png"));

// 展开一张卡的折叠区（验收「其余字段都在折叠区」）
await ev(`(() => { const d=document.querySelector('.fcard details.tech'); d.open=true; d.scrollIntoView({block:'center'}); return d.querySelectorAll('.k').length; })()`);
await sleep(400);
console.log("expanded rows:", await ev(`(() => { const d=document.querySelector('.fcard details.tech'); return [d.querySelectorAll('.k').length, [...d.querySelectorAll('.k')].map(k=>k.textContent).join('|')]; })()`));
console.log(await shot("fashion_card_details.png"));

ws.close();
