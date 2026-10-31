import path from "node:path";
import { pathToFileURL } from "node:url";
const CAND = [process.env.PLAYWRIGHT_PKG || "", "playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) {
  try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {}
}
const BASE = "http://127.0.0.1:8765";
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1150 } });
await page.goto(`${BASE}/board.html?b=fashion_wardrobe&v=20261101facemedia`, { waitUntil: "networkidle" });
await page.waitForTimeout(1500);
await page.locator("button.fr-chip", { hasText: "头饰111" }).first().click();
await page.waitForTimeout(1500);
const r = await page.evaluate(() => {
  const cards = [...document.querySelectorAll(".fcard")];
  const byId = cards.map((c) => c.dataset.frid);
  const act = [...document.querySelectorAll("button.fr-chip.on, button.fr-chip.active, button.fr-chip[aria-pressed=true]")].map((e) => e.textContent.trim());
  return { n: cards.length, face: byId.filter((x) => x.startsWith("face_")).length, other: byId.filter((x) => !x.startsWith("face_")).slice(0, 12), act, countLine: (document.querySelector(".fr-count-line, #frStat, .board-stat") || {}).textContent };
});
console.log(JSON.stringify(r));
await browser.close();
