# -*- coding: utf-8 -*-
r"""给 wiki 主页换上《明日之后》主题皮肤：暗色金属 + 锈橙警示色。
只替换 <style> 块，结构/类名/JS 全不动。
"""
from __future__ import annotations

import pathlib
import shutil

HTML = pathlib.Path(r"E:/la拆包项目/04_站点/web/wiki.html")
BAK = HTML.with_suffix(".html.bak_theme20261018")

CSS = r"""
/* ===== 明日之后 · 废土日志主题 ===== */
:root{
  --bg:#0b0d0e; --bg2:#121517; --panel:#14181a; --panel2:#171c1f;
  --fg:#e8e4dc; --fg-dim:#b9b3a7; --muted:#8b8579;
  --line:#2a2f31; --line2:#3a4145;
  --amber:#e2a13c; --amber-hi:#f6c76a; --amber-dim:#8a6a2f;
  --rust:#b4462f; --green:#5fa06a;
  --radius:4px;
  --shadow:0 1px 0 rgba(255,255,255,.04) inset,0 2px 10px rgba(0,0,0,.55);
  --noise:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='140' height='140'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.85' numOctaves='3'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='140' height='140' filter='url(%23n)' opacity='.28'/%3E%3C/svg%3E");
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-padding-top:140px}
body{
  font-family:"Microsoft YaHei","Segoe UI",system-ui,sans-serif;
  font-size:14px;line-height:1.55;color:var(--fg);
  background:
    radial-gradient(1200px 600px at 12% -10%,rgba(226,161,60,.10),transparent 60%),
    radial-gradient(900px 500px at 92% 0%,rgba(180,70,47,.10),transparent 65%),
    linear-gradient(180deg,#0b0d0e,#101314 40%,#0b0d0e);
  background-attachment:fixed;
  -webkit-font-smoothing:antialiased;
}
body::before{content:"";position:fixed;inset:0;background-image:var(--noise);opacity:.35;pointer-events:none;z-index:0}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(120% 90% at 50% 0%,transparent 55%,rgba(0,0,0,.55) 100%)}
.topin,.wrap{position:relative;z-index:1}
::selection{background:rgba(226,161,60,.35);color:#fff}

/* 顶栏：金属板 + 警示条 */
.topbar{position:sticky;top:0;z-index:20;padding:0;
  background:linear-gradient(180deg,rgba(16,19,21,.97),rgba(12,14,15,.94));
  backdrop-filter:blur(10px);border-bottom:1px solid #2f3538;
  box-shadow:0 1px 0 rgba(255,255,255,.03) inset,0 8px 26px rgba(0,0,0,.55)}
.topbar::after{content:"";display:block;height:3px;
  background:repeating-linear-gradient(115deg,#e2a13c 0 14px,#1a1c1d 14px 28px);opacity:.55}
.topin{max-width:1200px;margin:0 auto;padding:14px 24px 12px}
.title-row{display:flex;align-items:center;justify-content:space-between;gap:14px;flex-wrap:wrap}
h1{font-size:21px;font-weight:800;letter-spacing:.06em;
  background:linear-gradient(180deg,#f7d591,#e2a13c 55%,#a9762a);
  -webkit-background-clip:text;background-clip:text;color:transparent;
  text-shadow:0 0 22px rgba(226,161,60,.18);white-space:nowrap}
h1::before{content:"";display:inline-block;width:4px;height:18px;margin-right:10px;
  background:linear-gradient(180deg,var(--amber-hi),var(--rust));vertical-align:-3px;
  box-shadow:0 0 10px rgba(226,161,60,.5)}
.sub{color:var(--muted);font-size:12px;margin-top:6px;letter-spacing:.02em}
.tool-link{font-size:12px;color:var(--fg-dim);text-decoration:none;
  border:1px solid var(--line2);background:linear-gradient(180deg,#1a1e20,#121517);
  border-radius:var(--radius);padding:6px 11px;letter-spacing:.04em;
  transition:border-color .15s,color .15s,background .15s}
.tool-link:hover{color:var(--amber-hi);border-color:var(--amber-dim);background:#1d2225}

/* 主体 */
.wrap{max-width:1200px;margin:0 auto;padding:26px 24px 70px}
h2{font-size:15px;font-weight:800;letter-spacing:.08em;margin:26px 0 8px;padding-bottom:7px;
  border-bottom:1px solid var(--line);color:var(--fg)}
h2::before{content:"// ";color:var(--amber);opacity:.9}
h3.group{font-size:12.5px;font-weight:700;color:var(--muted);margin:14px 0 8px;letter-spacing:.05em}

/* 搜索 */
.home-tools{margin:6px 0 20px}
.search-row{display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.search-row input{flex:1;min-width:200px;padding:12px 14px;font:inherit;color:var(--fg);
  background:linear-gradient(180deg,#101314,#0d1011);border:1px solid var(--line2);
  border-radius:var(--radius);letter-spacing:.02em;
  box-shadow:0 1px 0 rgba(255,255,255,.03) inset,0 2px 8px rgba(0,0,0,.4)}
.search-row input::placeholder{color:#6f6a61}
.search-row input:focus{outline:none;border-color:var(--amber);box-shadow:0 0 0 1px rgba(226,161,60,.35),0 0 18px rgba(226,161,60,.12)}
.search-row button{padding:11px 16px;font:inherit;cursor:pointer;color:var(--fg-dim);
  background:linear-gradient(180deg,#1a1e20,#121517);border:1px solid var(--line2);
  border-radius:var(--radius);letter-spacing:.05em;transition:.15s}
.search-row button:hover{color:var(--amber-hi);border-color:var(--amber-dim)}
.search-status{font-size:11.5px;color:var(--muted);margin-top:8px;letter-spacing:.02em}
.home-empty{padding:34px;text-align:center;color:var(--muted);
  border:1px dashed var(--line2);border-radius:var(--radius);background:rgba(255,255,255,.015)}

/* 体系树：装甲板 */
.system-cards{display:flex;flex-direction:column;gap:10px}
.system-cards details{background:linear-gradient(180deg,var(--panel2),var(--panel));
  border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;
  box-shadow:var(--shadow)}
.system-cards>details.sys-lv1{position:relative}
.system-cards>details.sys-lv1::before{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;
  background:linear-gradient(180deg,var(--amber),transparent 70%);opacity:.55}
.sys-lv1>summary{padding:14px 16px;font-size:14.5px;font-weight:800;letter-spacing:.06em;
  color:#efe9df;background:linear-gradient(180deg,#1b2023,#151a1c)}
.sys-lv1[open]>summary{border-bottom:1px solid var(--line);
  background:linear-gradient(180deg,#20262a,#171c1f)}
.summary,.sys-lv1>summary{transition:background .15s}
.sys-lv2,.sys-lv3,.sys-lv4{border:0!important;border-radius:0!important;background:transparent!important;box-shadow:none!important}
.sys-lv2{border-top:1px solid var(--line)!important}
.sys-lv2>summary{padding:10px 16px 10px 32px;font-size:13px;font-weight:700;color:#cfc8bb;background:rgba(255,255,255,.012)}
.sys-lv3{border-top:1px solid #22282a!important}
.sys-lv3>summary{padding:8px 16px 8px 50px;font-size:12.5px;font-weight:600;color:#b6afa2}
.sys-lv4{border-top:1px solid #1e2426!important}
.sys-lv4>summary{padding:7px 16px 7px 68px;font-size:12px;font-weight:500;color:#9a9488}
summary{display:flex;align-items:center;gap:9px;cursor:pointer;list-style:none;user-select:none}
summary::-webkit-details-marker{display:none}
summary::before{content:"";flex:0 0 auto;width:0;height:0;
  border-left:5px solid #6f6a61;border-top:4px solid transparent;border-bottom:4px solid transparent;
  transition:transform .16s,border-left-color .16s}
details[open]>summary::before{transform:rotate(90deg);border-left-color:var(--amber)}
summary:hover{background:rgba(226,161,60,.07)}
.summary:hover,.sys-lv2>summary:hover,.sys-lv3>summary:hover{background:rgba(226,161,60,.07)}
.sys-t{flex:1 1 auto;min-width:0}
.sys-n{flex:0 0 auto;font-size:10.5px;font-weight:700;letter-spacing:.04em;
  color:#c8a468;background:rgba(226,161,60,.10);border:1px solid rgba(226,161,60,.28);
  border-radius:2px;padding:1px 9px;white-space:nowrap}
details[open]>summary>.sys-n{color:#1a1206;background:linear-gradient(180deg,var(--amber-hi),var(--amber));border-color:var(--amber)}

/* 卡片 */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.card{background:linear-gradient(180deg,#151a1c,#111517);border:1px solid var(--line);
  border-radius:var(--radius);padding:12px 13px;box-shadow:var(--shadow);
  display:flex;flex-direction:column;gap:5px;position:relative;transition:border-color .15s,transform .12s,box-shadow .15s}
.card.published{text-decoration:none;color:var(--fg);border-color:var(--line2);background:linear-gradient(180deg,#171c1f,#121618)}
.card.published:hover{border-color:var(--amber-dim);transform:translateY(-1px);
  box-shadow:0 1px 0 rgba(255,255,255,.05) inset,0 6px 20px rgba(0,0,0,.6),0 0 0 1px rgba(226,161,60,.12)}
.card.published:hover .cname{color:var(--amber-hi)}
.cname{font-size:13px;font-weight:700;letter-spacing:.02em;color:#eae5da;line-height:1.6}
.csub{font-size:11px;color:var(--muted);line-height:1.55}
.badge{display:inline-block;font-size:10px;padding:1px 7px;border-radius:2px;
  border:1px solid rgba(226,161,60,.3);color:var(--amber);background:rgba(226,161,60,.08);
  margin-left:6px;vertical-align:1px;letter-spacing:.03em}
.card.note{border-style:dashed;border-color:var(--line2);background:transparent;box-shadow:none}
.card.note .cname{font-weight:600;color:#a8a296;font-size:12px}
.card.placeholder,.card.deprecated{border-style:dashed;border-color:#2b3134;background:transparent;
  color:#6f6a61;box-shadow:none;cursor:default}
.card.placeholder .cname,.card.deprecated .cname{color:#6f6a61;font-weight:600;font-size:12px}
.sys-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:9px;padding:11px 16px 13px}
.sys-lv2>.sys-grid{padding-left:32px}
.sys-lv3>.sys-grid{padding-left:50px}
.sys-lv4>.sys-grid{padding-left:68px}
.sys-grid .card{padding:9px 11px;gap:2px}
.sys-grid .cname{font-size:12px;font-weight:650}
.sys-grid .csub{font-size:10.5px}
.sys-empty{font-size:11.5px;color:#6f6a61;padding:6px 2px;grid-column:1/-1}

/* 状态 chip */
.state-line{display:flex;flex-wrap:wrap;gap:4px;margin-top:3px}
.state-chip{font-size:9.5px;line-height:1.5;padding:1px 6px;border-radius:2px;
  border:1px solid var(--line2);background:rgba(255,255,255,.04);color:#a8a296;letter-spacing:.02em}
.state-chip.verified{background:rgba(95,160,106,.12);color:#8fd39a;border-color:rgba(95,160,106,.35)}
.state-chip.unresolved{background:rgba(226,161,60,.10);color:#e6bd7c;border-color:rgba(226,161,60,.3)}
.state-chip.quarantined{background:rgba(180,70,47,.14);color:#e08c78;border-color:rgba(180,70,47,.4)}
.state-chip.runtime-final-unknown{background:rgba(140,140,160,.12);color:#b9b9c9;border-color:rgba(140,140,160,.3)}

/* 其他 */
.sys-bar{display:flex;justify-content:flex-end;margin:0 0 6px}
.sys-bar label{display:inline-flex;align-items:center;gap:6px;font-size:11px;color:var(--muted);
  cursor:pointer;padding:4px 10px;border:1px solid var(--line);border-radius:2px;
  background:rgba(255,255,255,.02);letter-spacing:.03em}
.sys-bar label:hover{color:var(--amber-hi);border-color:var(--amber-dim)}
.sys-bar input{accent-color:var(--amber);cursor:pointer}
details.tech{margin-top:10px;border:1px dashed var(--line2);border-radius:var(--radius);
  background:rgba(255,255,255,.015)}
details.tech>summary{cursor:pointer;padding:8px 11px;font-size:11.5px;color:#8f897d;font-weight:600;letter-spacing:.04em}
details.tech .csub{padding:0 11px 11px}
.gate{margin-top:12px;border:1px dashed var(--line2);border-radius:var(--radius);
  background:rgba(255,255,255,.015);padding:10px 12px;color:#9a9488;font-size:12px}
.gate code{font-family:ui-monospace,Consolas,monospace;font-size:11px;color:#c9a877}
.foot{margin-top:42px;padding-top:14px;border-top:1px solid var(--line);color:#6f6a61;font-size:11.5px;letter-spacing:.03em}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}
.preflight{grid-column:1/-1;background:transparent!important;box-shadow:none;font-size:12px}
.preflight summary{cursor:pointer;font-weight:600}
.preflight .csub{margin-top:8px}
[hidden]{display:none!important}
a:focus-visible,input:focus-visible,summary:focus-visible,button:focus-visible{
  outline:2px solid var(--amber);outline-offset:2px}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:#0c0e0f}
::-webkit-scrollbar-thumb{background:#2b3134;border-radius:2px;border:2px solid #0c0e0f}
::-webkit-scrollbar-thumb:hover{background:#3d4448}

@media(max-width:540px){
  .topbar{padding:0}.topin{padding:12px 16px 10px}.wrap{padding:18px 16px 44px}
  .grid{grid-template-columns:1fr}h1{font-size:17px}
  .sys-grid{grid-template-columns:1fr}
  .sys-lv2>summary{padding-left:22px}.sys-lv3>summary{padding-left:32px}
  .sys-lv4>summary{padding-left:40px}
  .sys-lv2>.sys-grid{padding-left:18px}.sys-lv3>.sys-grid{padding-left:26px}.sys-lv4>.sys-grid{padding-left:40px}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.card.published{transition:none}}
"""


def main() -> int:
    html = HTML.read_text(encoding="utf-8")
    if not BAK.is_file():
        shutil.copy2(HTML, BAK)
    i = html.find("<style>")
    j = html.find("</style>")
    if i < 0 or j < 0:
        print("找不到 style 块")
        return 1
    new = html[: i + len("<style>")] + CSS + html[j:]
    HTML.write_text(new, encoding="utf-8")
    print("主题已写入 ｜ 备份", BAK.name, "｜ 新大小", len(new))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
