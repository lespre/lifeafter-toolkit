/**
 * 前端冒烟测试（基线/回归对比用）
 *
 * 用途：前端改造前后必须能自动对比，而不是"看着还行"。
 * 做法：打开若干代表板，抓取关键 DOM 事实 + JS 错误 + 控制台错误，输出指纹 JSON。
 *       两次运行（改造前/后）diff 指纹，即可判断有没有改坏。
 *
 * 用法：
 *   node 02_wiki/web/tools/checks/frontend_smoke.mjs                     # 跑默认板组
 *   node 02_wiki/web/tools/checks/frontend_smoke.mjs --out state/smoke_a.json
 *   node 02_wiki/web/tools/checks/frontend_smoke.mjs --boards fashion_wardrobe,vehicle_full
 *   node 02_wiki/web/tools/checks/frontend_smoke.mjs --diff state/smoke_a.json
 *   node 02_wiki/web/tools/checks/frontend_smoke.mjs --base http://127.0.0.1:8765
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
// 本文件在 02_wiki/web/tools/checks/ → 项目根在 ../../..
const WIKI_ROOT = path.resolve(__dirname, "../../..");
const REPO_ROOT = path.resolve(__dirname, "../../../..");

// playwright 包可能在 npx 缓存里，尝试多种解析路径后动态 import
async function resolvePlaywright() {
  const cands = [
    process.env.PLAYWRIGHT_PKG || "",
    "playwright",
    path.join(
      process.env.LOCALAPPDATA || "",
      "npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright",
    ),
    path.join(
      process.env.USERPROFILE || "",
      "AppData/Local/npm-cache/_npx/e41f203b7505f1fb/node_modules/playwright",
    ),
  ].filter(Boolean);
  const seen = new Set();
  for (const c of cands) {
    // 允许直接给目录（补 package.json 主入口）或包名
    const asDir = path.isAbsolute(c) ? path.join(c, "package.json") : null;
    const targets = [];
    if (asDir && fs.existsSync(asDir)) {
      try {
        const pkg = JSON.parse(fs.readFileSync(asDir, "utf8"));
        // playwright 的 ESM 入口是 index.mjs（CJS 的 index.js 顶层无具名导出）
        const main = pkg.module || "index.mjs";
        targets.push(path.join(c, main));
        if (main !== "index.mjs") targets.push(path.join(c, "index.mjs"));
      } catch {
        /* ignore */
      }
    }
    targets.push(c);
    for (const t of targets) {
      const key = path.isAbsolute(t) ? t : `name:${t}`;
      if (seen.has(key)) continue;
      seen.add(key);
      try {
        const url = path.isAbsolute(t) ? pathToFileURL(t).href : t;
        const mod = await import(url);
        if (mod && mod.chromium) return mod;
      } catch {
        /* try next */
      }
    }
  }
  throw new Error(
    "找不到 playwright 包。请 `npm i -D playwright`（或 npx playwright install chromium），" +
      "或设置 PLAYWRIGHT_PKG 指向包目录。",
  );
}

// ── 参数 ──────────────────────────────────────────────────────────────
const argv = process.argv.slice(2);
function arg(name, def = null) {
  const i = argv.indexOf(name);
  return i >= 0 && argv[i + 1] ? argv[i + 1] : def;
}
const BASE = arg("--base", "http://127.0.0.1:8765");
const OUT = arg("--out", null);
const DIFF_AGAINST = arg("--diff", null);
const VIEWPORTS = arg("--mobile", "1") !== "0";

// 默认板组：覆盖不同渲染模式（大表 / 时装 / 载具 / 芯片 / 名册级 / 静态导出）
const DEFAULT_BOARDS = [
  "fashion_wardrobe",
  "vehicle_full",
  "chip_item_catalog",
  "talent_catalog",
  "drone_catalog",
  "gene_potential_catalog",
  "equipment_attrs",
  "common_item_text_sources",
  "lottery_periods",
  "title_catalog",
];

const boards = (arg("--boards", "") || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
const BOARDS = boards.length ? boards : DEFAULT_BOARDS;

// ── 抓取 ──────────────────────────────────────────────────────────────
async function probe(page, board, viewport) {
  const errors = [];
  const consoleErrors = [];
  page.removeAllListeners("pageerror");
  page.removeAllListeners("console");
  page.on("pageerror", (e) => errors.push(String(e.message || e).slice(0, 300)));
  page.on("console", (m) => {
    if (m.type() === "error") consoleErrors.push(m.text().slice(0, 300));
  });

  const url = `${BASE}/board.html?b=${encodeURIComponent(board)}`;
  let navOk = true;
  let navErr = "";
  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30000 });
    // 等首屏渲染（标题不再是「加载中…」）
    await page
      .waitForFunction(
        () => {
          const t = document.getElementById("title");
          return t && t.textContent && t.textContent !== "加载中…" && t.textContent !== "…";
        },
        { timeout: 25000 },
      )
      .catch(() => {});
    await page.waitForTimeout(1200);
  } catch (e) {
    navOk = false;
    navErr = String(e.message || e).slice(0, 200);
  }

  const facts = await page.evaluate(() => {
    const q = (s) => document.querySelector(s);
    const qa = (s) => Array.from(document.querySelectorAll(s));
    const txt = (el) => (el ? el.textContent.trim().replace(/\s+/g, " ").slice(0, 200) : null);
    const grid = q("#grid");
    const cards = qa("#grid > *");
    return {
      title: txt(q("#title")),
      metaline: txt(q("#metaline")),
      count: txt(q("#count")),
      pillCount: qa("#pills > *").length,
      filterSelects: qa(".controls select").length,
      gridChildren: grid ? grid.children.length : -1,
      cardTags: cards.slice(0, 40).map((c) => {
        const n = c.querySelector(".i-name, .name, h3, .i-title");
        const tags = Array.from(c.querySelectorAll(".state-tag, .state-pill, .tag")).map((t) =>
          t.textContent.trim(),
        );
        const ev = c.querySelector(".ev, .evidence");
        return { n: n ? n.textContent.trim().slice(0, 40) : null, tags, ev: ev ? ev.textContent.trim() : null };
      }),
      stateTagKinds: Array.from(
        new Set(
          qa("#grid .state-tag, #grid .state-pill").map((t) =>
            (t.className.match(/(verified|unresolved|quarantined|unverified|static-config|runtime-final-unknown)/) || [
              "?",
            ])[0],
          ),
        ),
      ),
      siteNavItems: qa("#siteNav a, #siteNav .nav-item").length,
      hasHamburger: !!q("#navToggle, .nav-toggle, #mobileNavBtn"),
      bodyClasses: document.body.className,
      hasHorizontalScroll:
        document.documentElement.scrollWidth > document.documentElement.clientWidth + 2,
      // 移动端抽屉：按钮须存在，点击后 siteNav 须由隐藏变为可见
      drawer: (() => {
        const btn = q("#navToggle");
        const nav = q("#siteNav");
        if (!btn) return "no-toggle";
        const before = getComputedStyle(nav).display;
        btn.click();
        const after = getComputedStyle(nav).display;
        const openCls = document.body.classList.contains("nav-open");
        btn.click(); // 复位
        return before + "->" + after + (openCls ? "|opened" : "|not-opened");
      })(),
      // 关键：详情面板能否打开（点第一张卡）
      detailOpens: (() => {
        try {
          const first = q("#grid > *");
          if (!first) return "no-card";
          first.click();
          const d = q(".detail, .detail-panel, #detail, .modal");
          return d ? "ok" : "no-panel";
        } catch (e) {
          return "err:" + String(e.message || e).slice(0, 60);
        }
      })(),
    };
  });

  return {
    board,
    viewport,
    navOk,
    navErr,
    pageErrors: errors,
    consoleErrors: consoleErrors.slice(0, 10),
    facts,
  };
}

// ── 主流程 ────────────────────────────────────────────────────────────
const { chromium: browser } = await resolvePlaywright();
const browserInst = await browser.launch();
const report = { base: BASE, at: new Date().toISOString(), results: [] };

const viewports = [{ name: "desktop", width: 1440, height: 900 }];
if (VIEWPORTS) viewports.push({ name: "mobile", width: 390, height: 844 });

for (const vp of viewports) {
  const ctx = await browserInst.newContext({
    viewport: { width: vp.width, height: vp.height },
    deviceScaleFactor: 1,
  });
  const page = await ctx.newPage();
  for (const b of BOARDS) {
    const r = await probe(page, b, vp.name);
    report.results.push(r);
    const f = r.facts || {};
    const bad = !r.navOk || r.pageErrors.length || r.consoleErrors.length;
    console.log(
      `${bad ? "✗" : "✓"} ${vp.name.padEnd(7)} ${b.padEnd(26)} ` +
        `cards=${String(f.gridChildren).padStart(6)} count=${(f.count || "-").slice(0, 22).padEnd(22)} ` +
        `tags=[${(f.stateTagKinds || []).join(",")}] ` +
        `err=${r.pageErrors.length}/${r.consoleErrors.length}`,
    );
  }
  await ctx.close();
}
await browserInst.close();

// ── 输出 / 对比 ───────────────────────────────────────────────────────
if (OUT) {
  const p = path.isAbsolute(OUT) ? OUT : path.join(REPO_ROOT, OUT);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, JSON.stringify(report, null, 2), "utf8");
  console.log(`\n指纹已写入 ${p}`);
}

if (DIFF_AGAINST) {
  const p = path.isAbsolute(DIFF_AGAINST) ? DIFF_AGAINST : path.join(REPO_ROOT, DIFF_AGAINST);
  const old = JSON.parse(fs.readFileSync(p, "utf8"));
  const key = (r) => `${r.viewport}::${r.board}`;
  const oldMap = new Map((old.results || []).map((r) => [key(r), r]));
  let diffs = 0;
  for (const r of report.results) {
    const o = oldMap.get(key(r));
    if (!o) {
      console.log(`＋ 新增 ${key(r)}`);
      diffs++;
      continue;
    }
    const of = o.facts || {};
    const nf = r.facts || {};
    const fields = [
      "title", "count", "gridChildren", "pillCount", "siteNavItems",
      "bodyClasses", "hasHamburger", "drawer", "hasHorizontalScroll",
    ];
    for (const f of fields) {
      if (JSON.stringify(of[f]) !== JSON.stringify(nf[f])) {
        console.log(`✗ ${key(r)} ${f}: ${JSON.stringify(of[f])} → ${JSON.stringify(nf[f])}`);
        diffs++;
      }
    }
    if (JSON.stringify(of.stateTagKinds) !== JSON.stringify(nf.stateTagKinds)) {
      console.log(
        `✗ ${key(r)} stateTagKinds: ${JSON.stringify(of.stateTagKinds)} → ${JSON.stringify(nf.stateTagKinds)}`,
      );
      diffs++;
    }
    if ((o.pageErrors || []).length < (r.pageErrors || []).length) {
      console.log(`✗ ${key(r)} 新增 JS 错误 ${r.pageErrors.length - o.pageErrors.length} 条`);
      diffs++;
    }
  }
  console.log(diffs === 0 ? "\n✅ 与基线一致，无回归" : `\n⚠️ 共 ${diffs} 处差异`);
  process.exitCode = diffs === 0 ? 0 : 1;
}
