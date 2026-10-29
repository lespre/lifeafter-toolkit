# -*- coding: utf-8 -*-
r"""把 wiki 主页换成官网《明日之后》视觉：冷蓝钢灰底 + 血红主按钮 + 金棕高亮。

官网 liferafter.game 的取色：
  底      #0d151a → #16232b（钢灰蓝，雾光在上）
  文字    #dfe7ec / 次要 #8ea0ab
  结构色  #6f9fba（冷钢蓝，细线、导航）
  主行动  #a01d1a → #c0392b（血红按钮）
  高亮    #d9a441（金，用于稀有/计数）
"""
from __future__ import annotations
import sys

import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

HTML = pathlib.Path(WEB / "wiki.html")
BAK = HTML.with_suffix(".html.bak_officialtheme")

CSS = r"""
/* ============================================================
   明日之后 · 资料档案馆 —— 官网视觉（钢灰蓝 / 血红 / 金）
   ============================================================ */
:root{
  --bg:#0b1116; --bg-2:#101a21;
  --panel:#121a20; --panel-2:#16212a;
  --ink:#dfe7ec; --ink-2:#a9b8c2; --ink-3:#7d8e99;
  --line:#22303a; --line-2:#33454f;
  --steel:#6f9fba; --steel-dim:#3c5a6b;
  --blood:#a01d1a; --blood-2:#c0392b;
  --gold:#d9a441;
  --r:2px;
  --shadow:0 1px 0 rgba(255,255,255,.03) inset,0 12px 30px rgba(0,0,0,.55);
  --noise:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='160' height='160'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='3'/%3E%3CfeColorMatrix type='saturate' values='0'/%3E%3C/filter%3E%3Crect width='160' height='160' filter='url(%23n)' opacity='.3'/%3E%3C/svg%3E");
}
*{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;scroll-padding-top:120px}
body{
  font-family:"Microsoft YaHei","PingFang SC",system-ui,sans-serif;
  font-size:14px;line-height:1.6;color:var(--ink);
  background:
    linear-gradient(180deg,rgba(120,155,175,.16) 0%,rgba(20,32,40,.0) 32%),
    radial-gradient(1000px 460px at 20% -6%,rgba(111,159,186,.14),transparent 62%),
    radial-gradient(800px 400px at 85% -4%,rgba(160,29,26,.10),transparent 66%),
    linear-gradient(180deg,#0d151a,#0b1116 55%,#080d11);
  background-attachment:fixed;
  -webkit-font-smoothing:antialiased;
}
body::before{content:"";position:fixed;inset:0;background-image:var(--noise);opacity:.26;pointer-events:none;z-index:0}
body::after{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(130% 92% at 50% -12%,transparent 50%,rgba(0,0,0,.66) 100%)}
::selection{background:rgba(192,57,43,.42);color:#fff}
a{color:inherit}
[hidden]{display:none!important}

/* ---------- 顶栏 ---------- */
.wp-top{position:sticky;top:0;z-index:40;
  background:linear-gradient(180deg,rgba(13,21,26,.97),rgba(10,16,20,.92));
  backdrop-filter:blur(10px);border-bottom:1px solid var(--line);
  box-shadow:0 10px 28px rgba(0,0,0,.5)}
.wp-top::after{content:"";display:block;height:1px;background:linear-gradient(90deg,transparent,rgba(111,159,186,.55),transparent)}
.wp-top-in{max-width:1400px;margin:0 auto;padding:11px 22px;display:flex;align-items:center;gap:20px}
.wp-brand{display:flex;align-items:center;gap:11px;text-decoration:none;flex:0 0 auto}
.wp-logo{width:22px;height:22px;flex:0 0 auto;border:1px solid var(--steel-dim);
  transform:rotate(45deg);background:linear-gradient(135deg,rgba(111,159,186,.4),rgba(160,29,26,.25))}
.wp-brand b{display:block;font-size:15px;font-weight:800;letter-spacing:.14em;color:#eaf1f5;white-space:nowrap}
.wp-brand em{display:block;font:600 9px/1.2 ui-monospace,Consolas,monospace;font-style:normal;
  letter-spacing:.3em;color:rgba(111,159,186,.6);margin-top:4px}
.wp-nav{display:flex;gap:4px;flex:1 1 auto;flex-wrap:wrap}
.wp-nav a{font-size:12px;text-decoration:none;color:var(--ink-2);letter-spacing:.08em;
  padding:6px 10px;border-bottom:2px solid transparent;white-space:nowrap}
.wp-nav a:hover{color:#fff;border-bottom-color:var(--blood-2);background:rgba(111,159,186,.06)}
.wp-tools{display:flex;align-items:center;gap:8px;flex:0 0 auto}
.wp-tools input{width:250px;padding:8px 11px;font:inherit;font-size:12.5px;color:var(--ink);
  background:rgba(6,10,13,.85);border:1px solid var(--line-2);border-radius:var(--r)}
.wp-tools input::placeholder{color:#63737d}
.wp-tools input:focus{outline:none;border-color:var(--steel);
  box-shadow:0 0 0 1px rgba(111,159,186,.35),0 0 18px rgba(111,159,186,.12)}
.wp-tools button{padding:8px 13px;font:inherit;font-size:12px;cursor:pointer;color:#fff;
  background:linear-gradient(180deg,var(--blood-2),var(--blood));border:1px solid #7d1512;border-radius:var(--r);
  letter-spacing:.06em}
.wp-tools button:hover{background:linear-gradient(180deg,#c94534,#a8201c)}

/* ---------- 首屏 ---------- */
.wp-hero{position:relative;z-index:1;overflow:hidden;border-bottom:1px solid var(--line);
  background:
    linear-gradient(180deg,rgba(150,180,195,.10),rgba(10,16,20,0) 78%),
    radial-gradient(900px 320px at 72% 10%,rgba(111,159,186,.16),transparent 66%)}
.wp-hero::before{content:"";position:absolute;inset:0;background-image:var(--noise);opacity:.2;pointer-events:none}
.wp-hero::after{content:"";position:absolute;left:0;right:0;bottom:0;height:1px;
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.18),transparent)}
.wp-hero-in{max-width:1400px;margin:0 auto;padding:38px 22px 30px;position:relative;
  display:flex;align-items:flex-end;justify-content:space-between;gap:26px;flex-wrap:wrap}
.wp-hero h1{font-size:30px;line-height:1.15;font-weight:900;letter-spacing:.16em;color:#f2f7fa;
  text-shadow:0 2px 18px rgba(0,0,0,.6)}
.wp-hero .jp{margin-top:10px;font:600 10px/1 ui-monospace,Consolas,monospace;
  letter-spacing:.34em;color:rgba(111,159,186,.75)}
.wp-hero p.lead{margin-top:13px;color:var(--ink-3);font-size:12.5px;letter-spacing:.03em;max-width:56ch}
.wp-stats{display:flex;gap:26px;margin-top:18px;flex-wrap:wrap}
.wp-stat b{display:block;font-size:21px;font-weight:800;color:var(--gold);font-variant-numeric:tabular-nums}
.wp-stat span{font-size:10.5px;color:var(--ink-3);letter-spacing:.16em}
.wp-hero-art{display:flex;align-items:flex-end;gap:10px;opacity:.9;pointer-events:none}
.wp-hero-art img{height:126px;width:auto;filter:drop-shadow(0 12px 26px rgba(0,0,0,.8)) saturate(.9)}
.wp-hero-art img:nth-child(2){height:158px;transform:translateY(-6px)}
.wp-hero-art img:nth-child(3){height:110px;opacity:.86}

/* ---------- 布局 ---------- */
.wp-body{position:relative;z-index:1;max-width:1400px;margin:0 auto;
  padding:24px 22px 70px;display:grid;grid-template-columns:210px minmax(0,1fr);gap:26px;align-items:start}
.wp-side{position:sticky;top:112px;align-self:start}
.wp-side h2{font-size:10px;letter-spacing:.24em;color:var(--ink-3);font-weight:700;
  padding:0 0 8px;border-bottom:1px solid var(--line);margin-bottom:8px}
#categoryNav{display:flex;flex-direction:column;gap:1px}
#categoryNav a{display:flex;align-items:center;gap:9px;text-decoration:none;padding:8px 9px;
  border-left:2px solid transparent;color:var(--ink-2);font-size:12.5px;letter-spacing:.04em;transition:.14s}
#categoryNav a:hover{color:#fff;background:rgba(111,159,186,.10);border-left-color:var(--blood-2)}
#categoryNav a b{font-weight:800;color:var(--steel)}
#categoryNav a i{font-style:normal;margin-left:auto;font-size:10px;color:#5f6f79;font-variant-numeric:tabular-nums}
.wp-side .arch{margin-top:14px;padding-top:12px;border-top:1px solid var(--line);
  display:flex;align-items:center;gap:7px;font-size:11px;color:var(--ink-3);cursor:pointer}
.wp-side .arch input{accent-color:var(--blood-2);cursor:pointer}
#gen{margin-top:10px;font-size:10.5px;color:#5f6f79;letter-spacing:.04em;line-height:1.5}

/* ---------- 分类 ---------- */
.wp-main{min-width:0}
.wp-cat{margin-bottom:34px;scroll-margin-top:120px}
.wp-cat > h2{display:flex;align-items:baseline;gap:12px;font-size:16px;font-weight:800;
  letter-spacing:.14em;color:#eef4f7;padding-bottom:9px;border-bottom:1px solid var(--line-2);margin-bottom:16px}
.wp-cat > h2 .no{font:800 11px/1 ui-monospace,Consolas,monospace;color:var(--steel);
  letter-spacing:.14em;padding:4px 8px;border:1px solid var(--steel-dim);border-radius:1px}
.wp-cat > h2 .cnt{margin-left:auto;font-size:10.5px;font-weight:600;color:var(--gold);letter-spacing:.14em}
.wp-cat > h2 span{flex-shrink:0}
.wp-cat > h2 span:nth-child(2){flex-shrink:1;min-width:0}
.wp-sub{margin:0 0 18px}
.wp-sub > h3{font-size:12px;font-weight:700;color:var(--ink-2);letter-spacing:.1em;
  margin:0 0 9px;display:flex;align-items:center;gap:8px}
.wp-sub > h3::before{content:"";width:5px;height:5px;background:var(--blood-2);transform:rotate(45deg)}
.wp-sub > h3 em{font-style:normal;color:#5f6f79;font-weight:600;font-size:10px;letter-spacing:.1em}

/* ---------- 瓦片 ---------- */
.tiles{display:grid;grid-template-columns:repeat(auto-fill,minmax(272px,1fr));gap:10px}
.card{position:relative}
.tile{display:flex;gap:11px;align-items:flex-start;text-decoration:none;padding:11px 12px;
  border:1px solid var(--line);border-radius:var(--r);
  background:linear-gradient(180deg,rgba(22,33,42,.72),rgba(15,23,29,.72));
  box-shadow:var(--shadow);transition:border-color .15s,transform .12s,background .15s}
.tile:hover{border-color:var(--steel-dim);transform:translateY(-1px);
  background:linear-gradient(180deg,rgba(30,45,56,.85),rgba(17,26,33,.85));
  box-shadow:0 1px 0 rgba(255,255,255,.04) inset,0 10px 24px rgba(0,0,0,.6)}
.tile .thumb{flex:0 0 auto;width:46px;height:46px;border-radius:1px;margin-top:2px;
  background:rgba(6,10,13,.6) center/contain no-repeat;border:1px solid var(--line)}
.tile .thumb.glyph{display:flex;align-items:center;justify-content:center;
  font:700 15px/1 ui-monospace,Consolas,monospace;color:rgba(111,159,186,.7);
  background:linear-gradient(135deg,rgba(111,159,186,.12),rgba(160,29,26,.08))}
.tile .tx{min-width:0}
.tile .tname{font-size:12.5px;font-weight:700;color:#e7eef2;line-height:1.4;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.tile:hover .tname{color:#fff}
.tile .tmeta{font-size:10.5px;color:var(--ink-3);letter-spacing:.05em;margin-top:3px;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.tile.placeholder,.tile.deprecated{opacity:.6;cursor:default}
.tile.note{background:transparent;border-style:dashed}

/* ---------- 其它 ---------- */
.wp-empty{padding:34px;text-align:center;color:var(--ink-3);
  border:1px dashed var(--line-2);border-radius:var(--r);background:rgba(255,255,255,.012)}
#searchStatus{font-size:11px;color:var(--ink-3);letter-spacing:.08em;margin:0 0 14px}
#searchStatus b{color:var(--gold);font-variant-numeric:tabular-nums}
.wp-foot{max-width:1400px;margin:0 auto;padding:0 22px 50px;position:relative;z-index:1}
details.tech{border:1px solid var(--line);border-radius:var(--r);background:rgba(255,255,255,.012)}
details.tech > summary{cursor:pointer;padding:9px 12px;font-size:11.5px;font-weight:600;
  color:var(--ink-3);letter-spacing:.08em}
details.tech .csub{padding:0 12px 12px;color:var(--ink-3);font-size:11.5px}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:10.5px;color:#6b7b85}
.copyright{margin-top:16px;text-align:center;color:#53636d;font-size:10px;letter-spacing:.24em}
a:focus-visible,input:focus-visible,summary:focus-visible,button:focus-visible{
  outline:2px solid var(--steel);outline-offset:2px}
::-webkit-scrollbar{width:10px;height:10px}
::-webkit-scrollbar-track{background:#0a1014}
::-webkit-scrollbar-thumb{background:#26343d;border:2px solid #0a1014}
::-webkit-scrollbar-thumb:hover{background:#374a56}

@media(max-width:1080px){
  .wp-hero-art{display:none}
  .wp-body{grid-template-columns:1fr;gap:18px}
  .wp-side{position:static;display:flex;gap:14px;align-items:flex-start;flex-wrap:wrap}
  .wp-side h2{border:0;padding:0;margin:0}
  #categoryNav{flex-direction:row;flex-wrap:wrap}
  #categoryNav a{border:1px solid var(--line);border-radius:1px}
}
@media(max-width:720px){
  .wp-top-in{flex-wrap:wrap;gap:10px;padding:9px 14px}
  .wp-nav{order:3;width:100%;overflow:auto;flex-wrap:nowrap}
  .wp-tools{width:100%}
  .wp-tools input{flex:1;width:auto}
  .wp-hero-in{padding:24px 14px 20px}
  .wp-hero h1{font-size:22px;letter-spacing:.1em}
  .wp-body{padding:16px 14px 50px}
  .tiles{grid-template-columns:1fr}
  .wp-foot{padding:0 14px 40px}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.tile{transition:none}}
"""


def main() -> int:
    h = HTML.read_text(encoding="utf-8")
    if not BAK.is_file():
        shutil.copy2(HTML, BAK)
    i = h.find("<style>")
    j = h.find("</style>")
    if i < 0 or j < 0:
        print("找不到 style 块")
        return 1
    HTML.write_text(h[: i + len("<style>")] + CSS + h[j:], encoding="utf-8")
    print("wiki 换肤完成 ｜ 备份", BAK.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
