import path from "node:path";
import { pathToFileURL } from "node:url";
const CAND = ["playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) { try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {} }
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1150 } });
await page.goto("http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=20261101facemedia", { waitUntil: "networkidle" });
await page.waitForTimeout(1500);

// 只看面饰：先点头饰再点一次取消，再点面饰
await page.locator("button.fr-chip", { hasText: "头饰111" }).first().click();
await page.waitForTimeout(600);
await page.locator("button.fr-chip", { hasText: "头饰111" }).first().click();
await page.waitForTimeout(600);
await page.locator("button.fr-chip", { hasText: "面饰53" }).first().click();
await page.waitForTimeout(1500);

// 找一张女版替代卡（小天使-粉 是缺图；用 绮绚燃焰 之类有 _h_f_）
const target = "绮绚燃焰";
const card = page.locator(`.fcard[data-frid]`, { hasText: target }).first();
console.log("card count for", target, await card.count());
await card.click();
await page.waitForTimeout(1000);
const det = page.locator("details.tech").first();
if (await det.count()) { await det.evaluate((e) => (e.open = true)); }
await page.waitForTimeout(600);
await page.screenshot({ path: "90_临时/shot_face_tech.png" });

const txt = await page.evaluate(() => {
  const m = document.querySelector(".c2-stage") || document.querySelector(".c2-mask");
  const d = document.querySelector("details.tech");
  return { modal: m ? m.innerText.slice(0, 400) : "", tech: d ? d.innerText.slice(0, 900) : "" };
});
console.log("=== MODAL ===\n" + txt.modal);
console.log("=== TECH ===\n" + txt.tech);
await browser.close();
