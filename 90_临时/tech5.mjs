import path from "node:path";
import { pathToFileURL } from "node:url";
const CAND = ["playwright",
  path.join(process.env.LOCALAPPDATA || "", "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright"),
  path.join(process.env.USERPROFILE || "", "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright")].filter(Boolean);
let pw = null;
for (const c of CAND) { try { const t = path.isAbsolute(c) ? pathToFileURL(path.join(c, "index.mjs")).href : c; const m = await import(t); if (m && m.chromium) { pw = m; break; } } catch {} }
const browser = await pw.chromium.launch();
const page = await browser.newPage({ viewport: { width: 1500, height: 1300 } });
await page.goto("http://127.0.0.1:8765/board.html?b=fashion_wardrobe&v=20261101facemedia", { waitUntil: "networkidle" });
await page.waitForTimeout(1200);
await page.locator("button.fr-chip", { hasText: "面饰53" }).first().click();
await page.waitForTimeout(1200);
for (const name of ["绮绚燃焰", "小天使-粉"]) {
  const c = page.locator(".fcard", { hasText: name }).first();
  if (!(await c.count())) { console.log("no card", name); continue; }
  await c.click();
  await page.waitForTimeout(800);
  const t = await page.evaluate(() => {
    const ds = [...document.querySelectorAll("details.tech")];
    const d = ds.find((x) => x.querySelector(".fr-kv")) || ds[0];
    if (d) d.open = true;
    return d ? d.innerText.replace(/\n+/g, " | ") : "";
  });
  console.log("### " + name + "\n" + t + "\n");
  await page.screenshot({ path: "90_临时/shot_tech_" + name + ".png" });
  await page.keyboard.press("Escape");
  await page.waitForTimeout(600);
}
await browser.close();
