# -*- coding: utf-8 -*-
r"""活动界面「画布拼装器」——把解出来的控件模块拖到画布上手工拼一屏。

═══════════════════════════════════════════════════════════════════════════
★ 为什么是「手工拼」而不是「自动还原」
   模块之间的层级关系在缺失的 `hd_ui_scheme_data_base` 里（见
   `ACTIVITY_PANEL_EVIDENCE.md` 验证 1/2），本包没有该表 ⇒ 谁摆在哪不可由数据推出。
   所以这里**不猜默认位置**：模块落点、缩放、层级全部由人拖，程序只负责
   ①忠实还原模块内部的真实 `pnl_offset` 布局；②把没有坐标的控件**单独隔离**，
   不混进真实布局里假装是有位置的。

★ 数据流
   `ui_scheme.py` → `_ui_preview/scheme/scheme.json` →（本脚本内联）→
   `_ui_preview/composer/index.html`（file:// 可直接打开，无需 server）

★ 用法
   python composer.py                    # 生成/覆盖 index.html
   python composer.py --check            # 只体检：数据源在不在、页面标记齐不齐
   python composer.py --bake a.json      # 把页面「导出单文件」的 json 烘成自包含 HTML
                                         # （贴图 base64 内联，离线可看，可直接发人）

★ 单文件的几何从哪来
   页面点「导出单文件」时，交出去的是**已渲染好的画布 DOM**（`stage_html`）。
   Python 只负责把 `../assets/x.png` 换成 base64、套一层壳。
   **故意不在 Python 里重算几何**——两套实现早晚漂移，改一处必须同步另一处。
"""
from __future__ import annotations

import base64
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402

ROOT = la_paths.find_project_root()
SCHEME = ROOT / "_ui_preview" / "scheme" / "scheme.json"
ACT_MAP = ROOT / "_ui_preview" / "scheme" / "activity_ui_map.json"
ASSETS = ROOT / "_ui_preview" / "assets"
OUT = ROOT / "_ui_preview" / "composer"
PAGE = "index.html"

CANVAS_W, CANVAS_H = 1136, 640          # 默认画布（横屏手游常见尺寸，可页面内改）

PAGE_TPL = r"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>活动界面拼装器 · 手工拼一屏</title>
<style>
:root{--bg:#f6f7f9;--panel:#fff;--line:#e3e6ea;--ink:#1d2129;--dim:#6b7280;
--accent:#2563eb;--warn:#b45309;--sel:#2563eb;}
*{box-sizing:border-box}
html,body{height:100%}
body{margin:0;background:var(--bg);color:var(--ink);overflow:hidden;
font:13px/1.5 "Noto Sans SC","Microsoft YaHei",system-ui,sans-serif}
header{height:46px;display:flex;align-items:center;gap:10px;padding:0 14px;
border-bottom:1px solid var(--line);background:var(--panel);flex-wrap:nowrap;overflow:hidden}
header h1{margin:0;font-size:14px;font-weight:650;white-space:nowrap}
header .tag{font-size:11.5px;color:var(--dim);white-space:nowrap}
.grow{flex:1}
button,select,input{font:inherit}
button{border:1px solid var(--line);background:var(--panel);border-radius:7px;
padding:5px 10px;cursor:pointer;white-space:nowrap;color:var(--ink)}
button:hover{border-color:#c7ccd4;background:#fafbfc}
button.pri{background:var(--accent);border-color:var(--accent);color:#fff}
button.pri:hover{background:#1d4ed8}
button:disabled{opacity:.45;cursor:not-allowed}
.wrap{display:grid;grid-template-columns:268px 1fr 236px;height:calc(100% - 46px)}
aside{background:var(--panel);padding:10px}
aside.l{border-right:1px solid var(--line);display:flex;flex-direction:column;
overflow:hidden;height:100%}
aside.r{border-left:1px solid var(--line);overflow:auto}
aside input[type=text]{width:100%;padding:6px 8px;border:1px solid var(--line);
border-radius:7px;margin-bottom:8px;flex:0 0 auto}
#clist{overflow:auto;flex:0 1 auto;max-height:30vh;min-height:54px;
border:1px solid var(--line);border-radius:7px;padding:3px}
#glist{overflow:auto;flex:0 1 auto;max-height:15vh;min-height:40px;
border:1px solid var(--line);border-radius:7px;padding:3px}
#mlist{overflow:auto;flex:1 1 auto;min-height:90px;padding-right:2px}
.modes{display:flex;gap:0;margin-bottom:8px;flex:0 0 auto}
.modes button{flex:1;border-radius:0;padding:5px 8px;font-size:12px}
.modes button:first-child{border-radius:7px 0 0 7px}
.modes button:last-child{border-radius:0 7px 7px 0;border-left:none}
.modes button[aria-pressed="true"]{background:var(--accent);border-color:var(--accent);
color:#fff}
.pane{display:flex;flex-direction:column;min-height:0;flex:1 1 auto}
#alist{overflow:auto;flex:1 1 auto;min-height:120px}
.act{padding:6px 7px;border:1px solid var(--line);border-radius:7px;margin-bottom:5px;
cursor:pointer;background:#fff}
.act:hover{border-color:#a5b4fc;background:#f8faff}
.act .an{font-size:12.5px;font-weight:600;display:flex;gap:6px;align-items:baseline}
.act .an em{font-style:normal;margin-left:auto;font-size:10.5px;font-weight:600;
color:#15803d;white-space:nowrap}
.act .an em.warn{color:var(--warn)}
.act .an em.none{color:#9aa3af;font-weight:500}
.act .an b{font-size:10.5px;font-weight:600;padding:0 5px;border-radius:999px;
background:#eef2ff;color:#4338ca}
.act .an b.live{background:#dcfce7;color:#15803d}
.act .an b.next{background:#fef3c7;color:#b45309}
.act .am{font-size:10.5px;color:var(--dim);margin-top:2px;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.act .am i{font-style:normal;color:#15803d}
.act .am u{text-decoration:none;color:var(--warn)}
.act[data-m="none"]{opacity:.62}
#addAll{border:1px solid var(--line);background:#f8fafc;border-radius:5px;
font-size:10.5px;padding:1px 6px;margin-left:4px;cursor:pointer;font-weight:500}
.cls{display:flex;justify-content:space-between;gap:8px;padding:5px 7px;border-radius:6px;
cursor:pointer;font-size:12.5px}
.cls:hover{background:#eef2ff}
.cls[aria-current="true"]{background:var(--accent);color:#fff}
.cls b{opacity:.7;font-weight:600;font-size:11.5px}
.grp{display:flex;justify-content:space-between;padding:4px 7px;border-radius:6px;
cursor:pointer;font-size:12px;border:1px solid transparent}
.grp:hover{background:#f1f5f9}
.grp[aria-current="true"]{background:#e0e7ff;border-color:#c7d2fe;font-weight:600}
h2{font-size:11px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);
margin:12px 0 6px;font-weight:650}
h2:first-child{margin-top:0}
.mod{display:flex;gap:8px;align-items:center;padding:6px;border:1px solid var(--line);
border-radius:8px;margin-bottom:6px;cursor:grab;background:#fff}
.mod:hover{border-color:#a5b4fc;box-shadow:0 1px 3px rgba(37,99,235,.12)}
.mod:active{cursor:grabbing}
.mod .th{width:60px;height:46px;flex:0 0 60px;position:relative;overflow:hidden;
background:repeating-conic-gradient(#f0f2f5 0 25%,#fff 0 50%) 0 0/12px 12px;
border-radius:5px}
.mod .th>div{position:absolute;left:0;top:0;transform-origin:0 0}
.mod .info{min-width:0;flex:1}
.mod .info b{display:block;font-size:12px;font-weight:600;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.mod .info span{font-size:11px;color:var(--dim);display:block;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
.mod .info i{font-style:normal;color:var(--warn)}
#stageWrap{overflow:auto;background:#eceef2;padding:20px;position:relative}
/*BAKE-BEGIN*/
#stage{position:relative;margin:0 auto;background:#3a3f46 url() 0 0/24px 24px;
box-shadow:0 3px 14px rgba(16,24,40,.16);transform-origin:0 0;flex:0 0 auto;
overflow:hidden}                       /* 画布即视口：超出屏幕的部分裁掉，所见即所得 */
#stage.bgimg{background-repeat:no-repeat;background-size:100% 100%}
.grid{position:absolute;inset:0;pointer-events:none;
background-image:linear-gradient(rgba(255,255,255,.09) 1px,transparent 1px),
linear-gradient(90deg,rgba(255,255,255,.09) 1px,transparent 1px);
background-size:40px 40px}
.inst{position:absolute;transform-origin:0 0;cursor:move;outline:1px dotted rgba(255,255,255,.30)}
.inst:hover{outline:1px dashed rgba(37,99,235,.75)}
.inst[aria-selected="true"]{outline:1.5px solid #60a5fa;outline-offset:2px;
box-shadow:0 0 0 3px rgba(37,99,235,.18)}
.inst .lbl{position:absolute;left:2px;top:2px;z-index:999;font-size:10px;color:#eff6ff;
background:rgba(37,99,235,.88);padding:1px 5px;border-radius:3px;white-space:nowrap;
display:none;pointer-events:none}
.inst[aria-selected="true"] .lbl,.inst:hover .lbl{display:block}
.w{position:absolute;overflow:hidden;display:flex;align-items:center;
justify-content:center;background-repeat:no-repeat;background-size:100% 100%}
.w.txt{background:none;color:#fff;font-weight:600;white-space:nowrap;
text-shadow:0 1px 2px rgba(0,0,0,.5)}
.w.slot{background:rgba(255,255,255,.045);border:1px dashed rgba(255,255,255,.34);
color:#c9d2de;font-size:8.5px;font-weight:400;text-shadow:none;letter-spacing:0;
line-height:1;padding:0 1px;text-align:center}
.ghost.k-txt{border-color:rgba(96,165,250,.8);color:#93c5fd;background:rgba(96,165,250,.13)}
.ghost.k-box{border-color:rgba(148,163,184,.85);color:#cbd5e1;background:rgba(148,163,184,.10)}
.ghost.k-fx{border-color:rgba(52,211,153,.8);color:#6ee7b7;background:rgba(52,211,153,.13)}
.ghost .gb{position:absolute;right:-3px;top:-5px;font-size:8px;line-height:1;
color:#fde68a;font-weight:700;text-shadow:0 0 2px #000}
.ghost{position:absolute;border:1px dashed rgba(251,191,36,.6);background:
rgba(251,191,36,.10);border-radius:3px;display:flex;align-items:center;justify-content:center;
font-size:9px;color:#fcd34d;overflow:hidden;background-repeat:no-repeat;
background-size:contain;background-position:center}
.gtitle{position:absolute;left:0;font-size:9px;color:#fcd34d;letter-spacing:.02em;
white-space:nowrap;opacity:.9}
/*BAKE-END*/
.lay{display:flex;align-items:center;gap:6px;padding:4px 6px;border-radius:6px;
cursor:pointer;font-size:11.5px;border:1px solid transparent}
.lay:hover{background:#eef2ff}
.lay[aria-current="true"]{background:#e0e7ff;border-color:#c7d2fe;font-weight:600}
.lay span{flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.lay em{font-style:normal;color:var(--dim);font-size:10.5px}
.lay button{border:none;background:none;color:#b91c1c;padding:0 3px;font-size:12px;
line-height:1;cursor:pointer}
#layers{max-height:26vh;overflow:auto;border:1px solid var(--line);border-radius:7px;
padding:3px;margin-bottom:8px}
.fsel{padding:4px 6px;border:1px solid var(--line);border-radius:6px;font-size:11.5px;
color:var(--ink);background:#fff;width:100%;margin-bottom:6px}
.fld{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:8px}
.fld label{display:flex;flex-direction:column;gap:2px;font-size:11px;color:var(--dim)}
.fld input{padding:4px 6px;border:1px solid var(--line);border-radius:6px;width:100%;
font-size:12px;color:var(--ink);background:#fff}
.hint{font-size:11.5px;color:var(--dim);line-height:1.6}
.hint code{background:#f1f3f6;padding:0 3px;border-radius:3px;font-size:11px}
.note{margin:0 0 10px;padding:8px 10px;border-left:3px solid var(--warn);
background:#fffbeb;border-radius:0 7px 7px 0;font-size:11.5px;color:#78350f;line-height:1.55}
.hidden{display:none}
.selbar{display:flex;flex-wrap:wrap;gap:5px;margin-bottom:8px}
.selbar button{padding:3px 8px;font-size:11.5px}
#empty{position:absolute;inset:0;display:flex;align-items:center;justify-content:center;
color:#9aa3af;font-size:13px;pointer-events:none;text-align:center;line-height:1.9}
</style></head><body>
<header>
  <h1>活动界面拼装器</h1>
  <span class="tag" id="tag">—</span>
  <span class="grow"></span>
  <label class="tag">画布
    <input id="cw" type="number" value="__CW__" min="320" max="2400" step="8"
      style="width:56px;padding:2px 4px;border:1px solid var(--line);border-radius:5px">
    ×
    <input id="ch" type="number" value="__CH__" min="240" max="1600" step="8"
      style="width:56px;padding:2px 4px;border:1px solid var(--line);border-radius:5px">
  </label>
  <label class="tag">缩放 <input id="zoom" type="range" min="20" max="150" value="70"
    style="width:80px;vertical-align:middle"><span id="zv">70%</span></label>
  <button id="undo" title="撤销 Ctrl+Z">↶ 撤销</button>
  <button id="redo" title="重做 Ctrl+Shift+Z">↷ 重做</button>
  <button id="snap" aria-pressed="true">吸附 2px</button>
  <button id="gh" aria-pressed="false">未定位控件</button>
  <button id="bgbtn">底图…</button>
  <button id="clear">清空</button>
  <button id="exp">导出 JSON</button>
  <button id="bake">导出单文件</button>
  <button id="imp">导入</button>
  <input id="impFile" type="file" accept=".json,application/json" class="hidden">
</header>
<div class="wrap">
  <aside class="l">
    <div class="modes">
      <button id="modeAct" aria-pressed="true">按活动</button>
      <button id="modeCls" aria-pressed="false">按控件类</button>
    </div>
    <input id="q" type="text" placeholder="搜索活动名 / 活动类 / 模块号…">
    <div id="paneAct" class="pane">
      <select id="afilter" class="fsel">
        <option value="live">进行中（按结束时间）</option>
        <option value="live_next">进行中 + 未开始</option>
        <option value="scheme">只看能拼的（有模块数据）</option>
        <option value="all">全部 3535 条</option>
      </select>
      <div class="hint" id="ahead" style="margin:-2px 0 6px;font-size:10.5px"></div>
      <div id="alist"></div>
    </div>    <div id="paneCls" class="pane hidden">
      <h2>活动类 <span id="ncls" class="tag"></span></h2>
      <div id="clist"></div>
      <h2>ui_group</h2>
      <div id="glist"></div>
      <h2>模块 <span id="nmod" class="tag"></span> · 拖到画布
        <button id="addAll" title="把该组模块按临时网格铺到画布，之后再拖">全部铺上</button>
      </h2>
      <select id="mfilter" class="fsel" title="模块太多时，先筛出真有坐标的那些">
        <option value="all">全部模块（按组内顺序）</option>
        <option value="rich">有坐标贴图 ≥4（推荐）</option>
        <option value="any">有坐标 ≥1</option>
        <option value="tray">只有未定位控件</option>
      </select>
      <div id="mlist"></div>
    </div>
  </aside>

  <div id="stageWrap">
    <div id="stage" style="width:__CW__px;height:__CH__px">
      <div class="grid" id="grid"></div>
      <div id="layer"></div>
      <div id="empty">把左侧模块拖进来（或双击模块）<br>模块内部是数据里的真实 pnl_offset；没有坐标的控件会被隔离标注</div>
    </div>
  </div>

  <aside class="r">
    <p class="note"><b>不猜位置</b>：模块之间的相对位置在缺失的
      <code>hd_ui_scheme_data_base</code> 里，本包没有该表。落点由你拖，布局只存本地。</p>
    <h2>图层 <span id="nlay" class="tag"></span></h2>
    <div id="layers"></div>
    <h2>选中模块</h2>
    <div id="insp"><div class="hint">未选中。点画布里的模块编辑属性。</div></div>
    <h2>快捷键</h2>
    <div class="hint">
      <code>方向键</code> 微移 1px（<code>Shift</code> 10px）<br>
      <code>[</code> <code>]</code> 调层级<br>
      <code>Del</code> 删除<br>
      <code>Ctrl</code>+滚轮 缩放选中模块<br>
      <code>Alt</code>+拖 不吸附
    </div>
    <h2>口径</h2>
    <div class="hint">
      模块内部的 <b>有坐标控件</b>按数据 <code>pnl_offset</code>（y 轴向上已翻成屏幕坐标）还原；
      <b>无坐标控件</b>不参与布局，用琥珀色虚线框占位并标 <code>?</code>，数量如实显示。
    </div>
  </aside>
</div>
<script>
const DATA = __DATA__;
const ACT = __ACT__;                 // 活动 → (hd_class, ui_group) 匹配表
const SNAP_ON = {v:true};
const GHOST_ON = {v:false};          // 未定位控件默认不画（会盖住真实布局）
let MFILTER = 'all';                 // 模块列表筛选：all / rich / any / tray
let curMode = 'act';                 // act=按活动 / cls=按控件类
let AFILTER = 'live';                // 活动筛选：live / live_next / scheme / all
let curCls=null, curGrp=null, q='', zoom=.7, sel=null, uid=1;
let insts=[];                       // {uid, mid, x, y, s, a, z}
let bgData=null;
const $ = s => document.querySelector(s);
const esc = s => String(s==null?'':s).replace(/[&<>"']/g,
  c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'})[c]);
const modById = {};                 // "cls:mid" -> module
const lsKey = () => 'uiComposer:' + (curCls||'_');

/* ── 模块几何：有坐标的按 pnl_offset，其余隔离 ───────────────────────── */
function geo(m){
  const placed = m.widgets.filter(w => w.pos);
  let x0=0, y0=0, x1=1, y1=1;
  placed.forEach(w => {
    const s = w.size || [40,40];
    x0 = Math.min(x0, w.pos[0]); x1 = Math.max(x1, w.pos[0]+s[0]);
    y1 = Math.max(y1, w.pos[1]); y0 = Math.min(y0, w.pos[1]-s[1]);
  });
  const pad = 6;
  const ghosts = m.widgets.filter(w => !w.pos);
  const GW = Math.max(1, x1-x0) + pad*2, GH = Math.max(1, y1-y0) + pad*2;
  return {placed, ghosts, x0, y0, y1, pad, W: Math.max(60,GW), H: Math.max(30,GH)};
}

/* 状态变体后缀：nor/down/hover/dis 三态贴图在数据里是三个控件，
   同一个按钮铺成三块会让画面看起来「乱」——按基名归并，只画一块 + 角标 ×N。 */
const STATE_RE = /_(nor|normal|down|hover|dis|disabled|select|sel|on|off|press)$/i;
function baseName(n){ return String(n||'').replace(STATE_RE,'') || String(n||''); }

function kindOf(w){
  const n = String(w.name||'').toLowerCase();
  if (n.indexOf('txt')===0 || n.indexOf('richtxt')===0 || w.text) return 'txt';
  if (n.indexOf('plist')===0 || n.indexOf('par')===0) return 'fx';
  if (n.indexOf('pnl')===0 || n.indexOf('panel')===0 || n.indexOf('sv')===0 ||
      n.indexOf('lb')===0 || n.indexOf('item')===0 || n.indexOf('btn')===0) return 'box';
  return 'img';
}
const KIND_GLYPH = {txt:'文', box:'框', fx:'特', img:'?'};

function innerHTML(m, opt){
  const g = geo(m);
  const parts = g.placed.map(w => {
    const s = w.size || [40,40];
    const L = w.pos[0]-g.x0+g.pad, T = (g.y1-w.pos[1])+g.pad;
    const st = ['left:'+L.toFixed(1)+'px','top:'+T.toFixed(1)+'px',
      'width:'+s[0].toFixed(1)+'px','height:'+s[1].toFixed(1)+'px'];
    if (w.png) st.push('background-image:url(../assets/'+w.png+')');
    if (w.text) st.push('font-size:'+(Math.min(24, Number(w.font)||13))+'px');
    const empty = !w.png && !w.text;             // 空槽：文字或图标由运行时塞进来
    return '<div class="w'+(w.text?' txt':'')+(empty?' slot':'')+'" title="'+
      esc(w.name)+(w.text?'：'+esc(w.text):'')+'" style="'+st.join(';')+'">'+
      (w.text ? esc(w.text) : (empty ? esc(w.name || ('#'+w.id)) : ''))+'</div>';
  });

  // ①用户开了开关 ②本模块压根没有带坐标控件 —— 两种情况都铺托盘，
  // 否则实例会变成一个看不清的空盒子（这是数据现状，不是渲染 bug）
  const wantG = (opt && opt.ghosts) || g.placed.length === 0;
  const W = g.placed.length ? g.W : Math.max(g.W, 176);
  let H = g.H;
  if (wantG && g.ghosts.length){
    // 1) 按基名归并状态变体  2) 有贴图的排前面、面积大的排前面
    const map = new Map();
    g.ghosts.forEach(w => {
      const k = baseName(w.name) || ('#'+w.id);
      if (!map.has(k)) map.set(k, {k, items:[], png:null, kind:'img'});
      const grp = map.get(k);
      grp.items.push(w);
      if (!grp.png && w.png) grp.png = w.png;
      if (grp.kind === 'img' && kindOf(w) !== 'img') grp.kind = kindOf(w);
    });
    let groups = Array.from(map.values());
    groups.sort((a,b) => (b.png?1:0)-(a.png?1:0) || b.items.length-a.items.length);

    const cell = 26, per = Math.max(1, Math.floor((W-g.pad*2)/cell));
    const top = g.H + 12;
    const shown = (opt && opt.cap) ? groups.slice(0, opt.cap) : groups;
    const rows = Math.ceil(shown.length/per);
    parts.push('<div class="gtitle" style="top:'+(g.H+1)+'px">未定位 '+
      g.ghosts.length+' 项 · 归并 '+groups.length+' 组（状态变体已合并；数据无 '+
      'pnl_offset，位置未知）</div>');
    shown.forEach((grp,i) => {
      const L = g.pad + (i%per)*cell, T = top + Math.floor(i/per)*cell;
      const st = ['left:'+L+'px','top:'+T+'px','width:'+(cell-3)+'px',
                  'height:'+(cell-3)+'px'];
      if (grp.png) st.push('background-image:url(../assets/'+grp.png+')');
      const badge = grp.items.length > 1
        ? '<b class="gb">'+grp.items.length+'</b>' : '';
      parts.push('<div class="ghost k-'+grp.kind+'" title="'+esc(grp.k)+
        (grp.items.length>1?'（'+grp.items.length+' 个状态变体）':'')+
        '" style="'+st.join(';')+'">'+(grp.png?'':KIND_GLYPH[grp.kind]||'?')+
        badge+'</div>');
    });
    H = top + rows*cell;
  }
  return {html: parts.join(''), W: W, H: H,
          ghosts: g.ghosts.length, placed: g.placed.length};
}

/* ── 侧栏 ─────────────────────────────────────────────────────── */
function renderCls(){
  const kw = q.trim().toLowerCase();
  const hitMod = kw && /^#?\d+$/.test(kw);
  const names = Object.keys(DATA.classes).filter(n => {
    if (!kw || hitMod) return true;
    return n.toLowerCase().includes(kw);
  });
  document.getElementById('ncls').textContent = '('+names.length+')';
  document.getElementById('clist').innerHTML = names.map(n => {
    const cnt = Object.keys(DATA.classes[n]).reduce((a,g)=>a+DATA.classes[n][g].length,0);
    return '<div class="cls" data-c="'+esc(n)+'" aria-current="'+(n===curCls)+
      '"><span>'+esc(n)+'</span><b>'+cnt+'</b></div>';
  }).join('') || '<div class="hint">无匹配</div>';
  document.querySelectorAll('.cls').forEach(el => el.onclick = () => {
    curCls = el.dataset.c;
    curGrp = Object.keys(DATA.classes[curCls]).sort((a,b)=>a-b)[0];
    load(); sync(); render();
  });
}

function renderGrp(){
  const gs = Object.keys(DATA.classes[curCls]||{}).sort((a,b)=>a-b);
  document.getElementById('glist').innerHTML = gs.map(g =>
    '<div class="grp" data-g="'+g+'" aria-current="'+(g===curGrp)+'"><span>ui_group '+
    g+'</span><b>'+DATA.classes[curCls][g].length+'</b></div>').join('');
  document.querySelectorAll('.grp').forEach(el => el.onclick = () => {
    curGrp = el.dataset.g; sync(); renderGrp(); renderMods();
  });
}

function modStats(m){
  const placed = m.widgets.filter(w => w.pos);
  return {placed: placed.length, tex: placed.filter(w => w.png).length,
          ghosts: m.widgets.length - placed.length};
}

function renderMods(){
  const mods = (DATA.classes[curCls]||{})[curGrp] || [];
  const kw = q.trim().toLowerCase();
  let show = kw && /^#?\d+$/.test(kw)
    ? Object.values(DATA.classes[curCls]).flat().filter(m => String(m.id).includes(kw.replace('#','')))
    : mods;
  if (MFILTER === 'rich') show = show.filter(m => modStats(m).tex >= 4);
  else if (MFILTER === 'any') show = show.filter(m => modStats(m).placed > 0);
  else if (MFILTER === 'tray') show = show.filter(m => modStats(m).placed === 0);
  document.getElementById('nmod').textContent = '('+show.length+'/'+mods.length+')';
  document.getElementById('mlist').innerHTML = show.map(m => {
    const r = innerHTML(m, {ghosts:false, cap:8});
    const s = modStats(m);
    const k = Math.min(1, 58/r.W, 44/r.H);
    return '<div class="mod" draggable="true" data-mid="'+m.id+'" title="拖到画布，或双击置中">'+
      '<div class="th"><div style="width:'+r.W+'px;height:'+r.H+'px;transform:scale('+k+
        ');position:absolute">'+r.html+'</div></div>'+
      '<div class="info"><b>#'+m.id+'</b><span>'+m.widgets.length+' 控件 · 坐标 '+
        s.placed+' · 贴图 '+s.tex+(s.ghosts?' · <i>未 '+s.ghosts+'</i>':'')+
        '</span></div></div>';
  }).join('') || '<div class="hint">该筛选下无模块，换成「全部模块」看看</div>';

  document.querySelectorAll('.mod').forEach(el => {
    el.ondragstart = e => {
      const m = findMod(el.dataset.mid);
      e.dataTransfer.setData('text/plain', JSON.stringify({cls:curCls, mid:m.id}));
      e.dataTransfer.effectAllowed = 'copy';
    };
    el.ondblclick = () => {
      const m = findMod(el.dataset.mid);
      const g = geo(m);
      add(m.id, Math.round((+$('#cw').value - g.W)/2), Math.round((+$('#ch').value - g.H)/2));
    };
  });
}

function findMod(mid){
  const all = Object.values(DATA.classes[curCls]||{}).flat();
  return all.find(m => String(m.id) === String(mid));
}

/* ── 画布 ─────────────────────────────────────────────────────── */
function add(mid, x, y){
  const m = findMod(mid); if (!m) return;
  push();
  const z = insts.reduce((a,i)=>Math.max(a,i.z),0)+1;
  insts.push({uid:uid++, mid:m.id, x:Math.round(x), y:Math.round(y), s:1, a:1, z});
  sel = insts[insts.length-1].uid;
  paint(); save(); renderInsp();
}

/* ── 撤销 / 重做（快照式，栈深 100） ──────────────────────────── */
let undoStack=[], redoStack=[], lastNudge=0;
function snapState(){
  return JSON.stringify({insts, sel, cw:+$('#cw').value, ch:+$('#ch').value, gh:GHOST_ON.v});
}
function push(){
  undoStack.push(snapState());
  if (undoStack.length > 100) undoStack.shift();
  redoStack.length = 0; syncUndo();
}
function restore(s){
  const d = JSON.parse(s);
  insts = d.insts || []; sel = d.sel || null;
  if (d.cw) $('#cw').value = d.cw;
  if (d.ch) $('#ch').value = d.ch;
  GHOST_ON.v = !!d.gh;
  $('#gh').setAttribute('aria-pressed', String(GHOST_ON.v));
  uid = insts.reduce((a,i)=>Math.max(a,i.uid),0)+1;
  applySize(); paint(); save(); renderInsp();
}
function doUndo(){
  if (!undoStack.length) return;
  redoStack.push(snapState()); restore(undoStack.pop()); syncUndo();
}
function doRedo(){
  if (!redoStack.length) return;
  undoStack.push(snapState()); restore(redoStack.pop()); syncUndo();
}
function syncUndo(){
  $('#undo').disabled = !undoStack.length;
  $('#redo').disabled = !redoStack.length;
}

/* ── 图层列表 ─────────────────────────────────────────────────── */
function renderLayers(){
  const box = document.getElementById('layers');
  document.getElementById('nlay').textContent = insts.length ? '('+insts.length+')' : '';
  box.innerHTML = insts.slice().sort((a,b)=>b.z-a.z).map(it => {
    const m = findMod(it.mid);
    let nm;
    if (!m) nm = '<em>模块缺失</em>';
    else { const g = geo(m); nm = '<em>'+g.placed.length+'置/'+g.ghosts.length+'未</em>'; }
    return '<div class="lay" data-u="'+it.uid+'" aria-current="'+(sel===it.uid)+'">'+
      '<span>#'+it.mid+' · '+Math.round(it.x)+','+Math.round(it.y)+'</span>'+nm+
      '<button data-del="'+it.uid+'" title="删除">✕</button></div>';
  }).join('') || '<div class="hint" style="padding:4px">画布还是空的</div>';
  box.querySelectorAll('.lay').forEach(el => el.onclick = e => {
    if (e.target.dataset.del) return;
    sel = +el.dataset.u; markSel(); renderInsp(); renderLayers();
  });
  box.querySelectorAll('button[data-del]').forEach(b => b.onclick = e => {
    e.stopPropagation(); push();
    const u = +b.dataset.del;
    insts = insts.filter(i => i.uid !== u);
    if (sel === u) sel = null;
    paint(); save(); renderInsp();
  });
}

function paint(){
  const layer = document.getElementById('layer');
  layer.innerHTML = insts.slice().sort((a,b)=>a.z-b.z).map(it => {
    const m = findMod(it.mid); if (!m) return '';
    const r = innerHTML(m, {ghosts:GHOST_ON.v});
    return '<div class="inst" data-u="'+it.uid+'" aria-selected="'+(sel===it.uid)+
      '" style="left:'+it.x+'px;top:'+it.y+'px;width:'+r.W+'px;height:'+r.H+
      'px;transform:scale('+it.s+');opacity:'+it.a+'">'+
      '<div class="lbl">#'+it.mid+' · '+Math.round(it.x)+','+Math.round(it.y)+
      ' · ×'+it.s.toFixed(2)+(r.ghosts?' · 未定位 '+r.ghosts:'')+'</div>'+r.html+'</div>';
  }).join('');
  document.getElementById('empty').style.display = insts.length ? 'none' : '';
  bindInst();
  const st2 = (ACT && ACT.stats) || {};
  document.getElementById('tag').textContent = curMode === 'act'
    ? '活动视图 ｜ 可拼 '+ (st2.scheme||0) +' ｜ 仅对到类 '+ (st2.class_only||0) +
      ' ｜ 无界面数据 '+ (st2.none||0) +' ｜ 画布 '+ insts.length +' 个'
    : (curCls||'—')+' · ui_group '+(curGrp||'—')+
      ' · '+insts.length+' 个模块实例';
  renderLayers();
}

function bindInst(){
  document.querySelectorAll('.inst').forEach(el => {
    el.onpointerdown = e => {
      const it = insts.find(i => i.uid === +el.dataset.u); if (!it) return;
      sel = it.uid; renderInsp(); markSel(); renderLayers();
      const noSnap = e.altKey;
      const sx = e.clientX, sy = e.clientY, ox = it.x, oy = it.y;
      const before = snapState();          // 只在真的移动后才入撤销栈，避免「点一下就一条」
      let moved = false;
      el.setPointerCapture(e.pointerId);
      const mv = ev => {
        let nx = ox + (ev.clientX-sx)/zoom, ny = oy + (ev.clientY-sy)/zoom;
        const st = (!noSnap && SNAP_ON.v) ? 2 : 1;
        it.x = Math.round(nx/st)*st; it.y = Math.round(ny/st)*st;
        if (!moved && (it.x !== ox || it.y !== oy)) {
          undoStack.push(before); redoStack.length = 0; syncUndo(); moved = true;
        }
        el.style.left = it.x+'px'; el.style.top = it.y+'px';
        el.querySelector('.lbl').textContent = '#'+it.mid+' · '+it.x+','+it.y+
          ' · ×'+it.s.toFixed(2);
      };
      const up = () => {
        el.onpointermove=null; el.onpointerup=null;
        save(); renderInsp(); renderLayers(); syncUndo();
      };
      el.onpointermove = mv; el.onpointerup = up;
    };
  });
}

function markSel(){
  document.querySelectorAll('.inst').forEach(el =>
    el.setAttribute('aria-selected', String(+el.dataset.u === sel)));
}

function renderInsp(){
  const it = insts.find(i => i.uid === sel);
  const box = document.getElementById('insp');
  if (!it){ box.innerHTML = '<div class="hint">未选中。点画布里的模块编辑属性。</div>'; return; }
  const m = findMod(it.mid);
  if (!m){ box.innerHTML = '<div class="hint">模块 #'+it.mid+' 不在当前活动类里。</div>'; return; }
  const r = innerHTML(m, {ghosts:GHOST_ON.v});
  box.innerHTML =
    '<div class="hint" style="margin-bottom:6px">模块 <b>#'+it.mid+'</b> · 自然尺寸 '+
      r.W.toFixed(0)+'×'+r.H.toFixed(0)+'<br>有坐标 '+r.placed+' ｜ 未定位 '+
      r.ghosts+'</div>'+
    '<div class="fld">'+
      '<label>X<input type="number" id="ix" value="'+Math.round(it.x)+'"></label>'+
      '<label>Y<input type="number" id="iy" value="'+Math.round(it.y)+'"></label>'+
      '<label>缩放<input type="number" id="is" value="'+it.s.toFixed(2)+'" step="0.05" min="0.1" max="4"></label>'+
      '<label>不透明<input type="number" id="ia" value="'+it.a.toFixed(2)+'" step="0.05" min="0" max="1"></label>'+
    '</div>'+
    '<div class="selbar">'+
      '<button data-act="center">水平居中</button>'+
      '<button data-act="fit">等比套满高度</button>'+
      '<button data-act="up">上移一层</button>'+
      '<button data-act="down">下移一层</button>'+
      '<button data-act="del">删除</button>'+
    '</div>'+
    '<div class="hint">模块 id 在同一活动类下唯一；跨类可能有同号不同内容，布局文件已记 cls。</div>';
  const bind = (id, key, fn) => {
    const el = document.getElementById(id); if (!el) return;
    el.onfocus = () => push();
    el.oninput = () => { const v = parseFloat(el.value); if (isFinite(v)) { it[key] = fn(v); paint(); } };
    el.onchange = () => { save(); renderInsp(); };
  };
  bind('ix','x', v=>v); bind('iy','y', v=>v);
  bind('is','s', v=>Math.min(4, Math.max(.1, v)));
  bind('ia','a', v=>Math.min(1, Math.max(0, v)));
  box.querySelectorAll('button[data-act]').forEach(b => b.onclick = () => {
    const a = b.dataset.act;
    push();
    if (a === 'del') { insts = insts.filter(i => i.uid !== it.uid); sel = null; }
    else if (a === 'center') it.x = Math.round((+$('#cw').value - r.W*it.s)/2);
    else if (a === 'fit') it.s = Math.min(3, Math.max(.1, (+$('#ch').value / r.H)));
    else if (a === 'up') it.z = insts.reduce((x,i)=>Math.max(x,i.z),0)+1;
    else if (a === 'down') it.z = insts.reduce((x,i)=>Math.min(x,i.z),9e9)-1;
    paint(); save(); renderInsp();
  });
}

/* ── 持久化 ───────────────────────────────────────────────────── */
function save(){
  try {
    localStorage.setItem(lsKey(), JSON.stringify({
      cls:curCls, cw:+$('#cw').value, ch:+$('#ch').value, gh:GHOST_ON.v, insts
    }));
  } catch(e){ /* 隐私模式忽略 */ }
}
function load(){
  insts = []; sel = null;
  try {
    const raw = localStorage.getItem(lsKey());
    if (raw){
      const d = JSON.parse(raw);
      insts = (d.insts||[]).filter(i => findMod(i.mid));
      uid = insts.reduce((a,i)=>Math.max(a,i.uid),0)+1;
      if (d.cw) $('#cw').value = d.cw;
      if (d.ch) $('#ch').value = d.ch;
      if (d.gh){ GHOST_ON.v = true; $('#gh').setAttribute('aria-pressed','true'); }
    }
  } catch(e){ insts = []; }
  applySize();
  paint(); renderInsp();
}
function applySize(){
  const w = +$('#cw').value || __CW__, h = +$('#ch').value || __CH__;
  const st = document.getElementById('stage');
  st.style.width = w+'px'; st.style.height = h+'px';
  st.style.transform = 'scale('+zoom+')';
  document.getElementById('stageWrap').firstElementChild;
  st.parentElement.style.alignItems = 'flex-start';
  st.style.marginBottom = ((zoom-1)*h)+'px';
}

function sync(){
  const u = new URL(location.href);
  u.searchParams.set('cls', curCls||'');
  u.searchParams.set('g', curGrp||'');
  history.replaceState(null,'',u);
}

/* ── 按活动浏览（hd_class + ui_group 对到模块） ───────────────────── */
function statusBadge(a){
  const cls = a.st==='进行中' ? 'live' : (a.st==='未开始' ? 'next' : '');
  return '<b class="'+cls+'">'+esc(a.st)+'</b>';
}

function gotoClass(cls, gid){
  if (!cls || !DATA.classes[cls]) return false;
  curCls = cls;
  const gs = Object.keys(DATA.classes[cls]).sort((a,b)=>(+a)-(+b));
  curGrp = (gid && DATA.classes[cls][gid]) ? String(gid) : gs[0];
  return true;
}

function flashAct(el, msg){
  const d = document.createElement('div');
  d.className = 'am';
  d.style.color = '#b45309';
  d.style.whiteSpace = 'normal';
  d.textContent = msg;
  el.appendChild(d);
  setTimeout(() => d.remove(), 3600);
}

function renderAct(){
  const box = document.getElementById('alist');
  const items = (ACT && ACT.items) || [];
  const kw = q.trim().toLowerCase();
  let list = items;
  if (AFILTER === 'live') list = items.filter(a => a.st === '进行中');
  else if (AFILTER === 'live_next')
    list = items.filter(a => a.st === '进行中' || a.st === '未开始');
  else if (AFILTER === 'scheme') list = items.filter(a => a.m === 'scheme');
  if (kw) list = list.filter(a => (a.n||'').toLowerCase().indexOf(kw) >= 0 ||
    (a.hc||'').toLowerCase().indexOf(kw) >= 0 || String(a.k) === kw.replace('#',''));

  const CAP = 400;
  const shown = list.slice(0, CAP);
  box.innerHTML = shown.map(a => {
    const tail = a.m === 'scheme'
      ? '<em>'+a.mods+' 模块 / '+a.w+' 控件</em>'
      : a.m === 'class' ? '<em class="warn">仅对到类</em>'
      : '<em class="none">无界面数据</em>';
    return '<div class="act" data-k="'+a.k+'" data-c="'+esc(a.hc)+'" data-g="'+
      esc(a.gid)+'" data-m="'+a.m+'" title="'+esc((a.n||'')+' · '+(a.hc||'')+
      ' · ui_class '+(a.uc||'—')+' · use_ui '+a.ui+' · ui_group '+a.gid)+'">'+
      '<div class="an">'+esc(a.n)+statusBadge(a)+tail+'</div>'+
      '<div class="am">'+(a.s||'—')+' ~ '+(a.e||'—')+' · '+
      esc(a.hc||'（无 hd_class）')+'</div></div>';
  }).join('') + (list.length > CAP
    ? '<div class="hint" style="padding:4px">另有 '+(list.length-CAP)+' 条未列出，用搜索收窄</div>'
    : '') || '<div class="hint" style="padding:4px">没有匹配的活动</div>';
  const st = (ACT && ACT.stats) || {};
  const head = document.getElementById('ahead');
  if (head) head.textContent = '共 '+(st.items||0)+' 条 ｜ 可拼 '+(st.scheme||0)+
    ' ｜ 仅对到类 '+(st.class_only||0)+' ｜ 无模块 '+(st.none||0)+
    '（其中包里无脚本 '+(st.no_script||0)+'）';

  box.querySelectorAll('.act').forEach(el => el.onclick = () => {
    const m = el.dataset.m;
    if (m === 'none'){
      const a = (ACT.items||[]).find(x => String(x.k) === el.dataset.k) || {};
      flashAct(el, a.sc
        ? '这个类有界面脚本，但控件模块表里没有它——不是漏匹配，是 reverse 表只收了 90 个 HD 类'
        : '包里连 '+(a.uc||a.hc||'该界面')+' 的脚本都没有（配置更新到 2026-11，'
          +'界面属于热更未入库部分）⇒ 无法还原，不是匹配失败');
      return;
    }
    if (!gotoClass(el.dataset.c, el.dataset.g)){
      flashAct(el, '类 '+(el.dataset.c||'')+' 不在模块表里'); return;
    }
    setMode('cls'); sync();
  });
}

function setMode(m){
  curMode = m;
  $('#modeAct').setAttribute('aria-pressed', String(m === 'act'));
  $('#modeCls').setAttribute('aria-pressed', String(m === 'cls'));
  $('#paneAct').classList.toggle('hidden', m !== 'act');
  $('#paneCls').classList.toggle('hidden', m !== 'cls');
  render();
}

function addAllOfGroup(){
  const mods = (DATA.classes[curCls]||{})[curGrp] || [];
  if (!mods.length) return;
  push();
  const cw = +$('#cw').value, ch = +$('#ch').value;
  const cols = cw > 900 ? 3 : 2, gap = 12;
  const cellW = Math.floor((cw - gap*(cols+1)) / cols);
  const cellH = Math.min(260, Math.floor((ch - gap*(cols+1)) / cols));
  let i = 0;
  mods.slice(0, 30).forEach(m => {
    const g = geo(m);
    // 自然尺寸远大于格子时按格子等比缩小 —— 总览视图，不是原始排版
    const s = Math.min(1, cellW / Math.max(g.W,1), cellH / Math.max(g.H,1));
    const col = i % cols, row = Math.floor(i / cols);
    const z = insts.reduce((a,x)=>Math.max(a,x.z),0)+1;
    insts.push({uid:uid++, mid:m.id,
      x: Math.round(gap + col*(cellW+gap)),
      y: Math.round(gap + row*(cellH+gap)),
      s: Math.round(s*100)/100, a:1, z});
    i++;
  });
  paint(); save(); renderInsp();
}

function render(){
  const act = curMode === 'act';
  $('#paneAct').classList.toggle('hidden', !act);
  $('#paneCls').classList.toggle('hidden', act);
  if (act){ renderAct(); paint(); return; }
  renderCls();
  if (!curCls){ paint(); return; }
  renderGrp(); renderMods(); paint();
}

function refreshPanels(){
  if (curMode === 'act') renderAct();
  else { renderCls(); renderMods(); }
}

/* ── 事件 ─────────────────────────────────────────────────────── */
document.getElementById('q').oninput = e => { q = e.target.value; refreshPanels(); };
document.getElementById('afilter').onchange = e => { AFILTER = e.target.value; renderAct(); };
document.getElementById('modeAct').onclick = () => setMode('act');
document.getElementById('modeCls').onclick = () => setMode('cls');
document.getElementById('addAll').onclick = addAllOfGroup;
document.getElementById('mfilter').onchange = e => { MFILTER = e.target.value; renderMods(); };
document.getElementById('undo').onclick = doUndo;
document.getElementById('redo').onclick = doRedo;
document.getElementById('zoom').oninput = e => {
  zoom = +e.target.value/100; $('#zv').textContent = e.target.value+'%'; applySize();
};
document.getElementById('snap').onclick = e => {
  SNAP_ON.v = !SNAP_ON.v;
  e.currentTarget.setAttribute('aria-pressed', String(SNAP_ON.v));
};
document.getElementById('gh').onclick = e => {
  GHOST_ON.v = !GHOST_ON.v;
  e.currentTarget.setAttribute('aria-pressed', String(GHOST_ON.v));
  save(); paint(); renderInsp();
};
document.getElementById('cw').onchange = document.getElementById('ch').onchange = () => {
  applySize(); save(); renderInsp();
};document.getElementById('clear').onclick = () => {
  if (!insts.length || confirm('清空当前活动类的 '+insts.length+' 个模块实例？')) {
    push();
    insts = []; sel = null; paint(); save(); renderInsp();
  }
};
function download(obj, name){
  const blob = new Blob([JSON.stringify(obj, null, 2)], {type:'application/json'});
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name;
  a.click(); URL.revokeObjectURL(a.href);
}

document.getElementById('exp').onclick = () => {
  download({cls:curCls, ui_group:curGrp, cw:+$('#cw').value, ch:+$('#ch').value,
    exported_at:new Date().toISOString(),
    note:'模块落点为人手工摆放，非游戏原始布局（hd_ui_scheme_data_base 缺失）',
    insts:insts.map(i => ({mid:i.mid, x:i.x, y:i.y, s:i.s, a:i.a, z:i.z}))},
    'layout_'+(curCls||'draft')+'.json');
};
// 单文件：把渲染好的画布 DOM 原样交出去，由 composer.py --bake 把贴图内联成 base64。
// ★ 不让 Python 重算几何，避免两边算法漂移。
document.getElementById('bake').onclick = () => {
  if (!insts.length) { alert('画布还是空的'); return; }
  download({kind:'ui_composer_bake', version:1, cls:curCls, ui_group:curGrp,
    cw:+$('#cw').value, ch:+$('#ch').value,
    exported_at:new Date().toISOString(),
    note:'模块落点为人手工摆放，非游戏原始布局（hd_ui_scheme_data_base 缺失）',
    stage_html:document.getElementById('layer').innerHTML},
    'bake_'+(curCls||'draft')+'.json');
};
document.getElementById('imp').onclick = () => document.getElementById('impFile').click();
document.getElementById('impFile').onchange = e => {
  const f = e.target.files[0]; if (!f) return;
  const fr = new FileReader();
  fr.onload = () => {
    try {
      const d = JSON.parse(fr.result);
      if (!d.insts || !Array.isArray(d.insts)) throw new Error('缺少 insts 数组');
      push();
      insts = d.insts.filter(i => findMod(i.mid)).map((i,n) => ({
        uid:uid++, mid:i.mid, x:+i.x||0, y:+i.y||0,
        s:Math.min(4,Math.max(.1,+i.s||1)), a:Math.min(1,Math.max(0,+i.a??1)), z:+i.z||n}));
      if (d.cw) $('#cw').value = d.cw;
      if (d.ch) $('#ch').value = d.ch;
      applySize(); paint(); save(); renderInsp();
    } catch(err){ alert('导入失败：'+err.message); }
  };
  fr.readAsText(f); e.target.value = '';
};
document.getElementById('bgbtn').onclick = () => {
  const inp = document.createElement('input');
  inp.type = 'file'; inp.accept = 'image/*';
  inp.onchange = () => {
    const f = inp.files[0]; if (!f) return;
    const r = new FileReader();
    r.onload = () => {
      const st = document.getElementById('stage');
      st.style.backgroundImage = 'url('+r.result+')';
      st.classList.add('bgimg');
    };
    r.readAsDataURL(f);
  };
  inp.click();
};

document.addEventListener('keydown', e => {
  if (/^(INPUT|TEXTAREA|SELECT)$/.test(e.target.tagName)) return;
  const mod = e.ctrlKey || e.metaKey;
  const k = e.key.toLowerCase();
  if (mod && k === 'z') { e.preventDefault(); e.shiftKey ? doRedo() : doUndo(); return; }
  if (mod && k === 'y') { e.preventDefault(); doRedo(); return; }
  const it = insts.find(i => i.uid === sel);
  if (!it) return;
  if (mod && k === 'd') {                       // 复制一份，右下错开 12px
    e.preventDefault(); push();
    const z = insts.reduce((a,i)=>Math.max(a,i.z),0)+1;
    insts.push({uid:uid++, mid:it.mid, x:it.x+12, y:it.y+12, s:it.s, a:it.a, z});
    sel = insts[insts.length-1].uid;
    paint(); save(); renderInsp(); return;
  }
  const step = e.shiftKey ? 10 : 1;
  const move = (dx,dy) => {
    const now = Date.now();
    if (now - lastNudge > 600) push();          // 连按合一，别把栈刷满
    lastNudge = now;
    it.x += dx; it.y += dy; paint(); save(); renderInsp(); e.preventDefault();
  };
  if (e.key === 'ArrowLeft') move(-step,0);
  else if (e.key === 'ArrowRight') move(step,0);
  else if (e.key === 'ArrowUp') move(0,-step);
  else if (e.key === 'ArrowDown') move(0,step);
  else if (e.key === 'Delete' || e.key === 'Backspace') {
    push();
    insts = insts.filter(i => i.uid !== it.uid); sel = null;
    paint(); save(); renderInsp(); e.preventDefault();
  }
  else if (e.key === '[') { push(); it.z = insts.reduce((x,i)=>Math.min(x,i.z),9e9)-1; paint(); save(); }
  else if (e.key === ']') { push(); it.z = insts.reduce((x,i)=>Math.max(x,i.z),0)+1; paint(); save(); }
});

document.getElementById('stage').addEventListener('dragover', e => {
  e.preventDefault(); e.dataTransfer.dropEffect = 'copy';
});
document.getElementById('stage').addEventListener('drop', e => {
  e.preventDefault();
  let d; try { d = JSON.parse(e.dataTransfer.getData('text/plain')); } catch(err){ return; }
  if (!d || d.mid == null) return;
  if (d.cls && d.cls !== curCls){
    curCls = d.cls; curGrp = Object.keys(DATA.classes[curCls]).sort((a,b)=>a-b)[0];
    load(); sync(); render();
  }
  const r = document.getElementById('stage').getBoundingClientRect();
  add(d.mid, (e.clientX-r.left)/zoom, (e.clientY-r.top)/zoom);
});
document.getElementById('stage').addEventListener('wheel', e => {
  if (!e.ctrlKey) return;
  const it = insts.find(i => i.uid === sel); if (!it) return;
  e.preventDefault();
  it.s = Math.min(4, Math.max(.1, it.s * (e.deltaY < 0 ? 1.06 : 1/1.06)));
  paint(); save(); renderInsp();
}, {passive:false});

/* ── 启动 ─────────────────────────────────────────────────────── */
(function boot(){
  const P = new URLSearchParams(location.search);
  const first = Object.keys(DATA.classes)[0];
  if (P.get('cls') && DATA.classes[P.get('cls')]){
    curCls = P.get('cls');
    const g = P.get('g');
    curGrp = (g && DATA.classes[curCls][g]) ? g : Object.keys(DATA.classes[curCls]).sort((a,b)=>a-b)[0];
    curMode = 'cls';
  } else if (first){
    curCls = first; curGrp = Object.keys(DATA.classes[first]).sort((a,b)=>a-b)[0];
    curMode = (ACT && ACT.items && ACT.items.length) ? 'act' : 'cls';
  }
  if (P.get('m') === 'cls' || P.get('m') === 'act') curMode = P.get('m');
  if (P.get('af')) AFILTER = P.get('af');
  applySize();
  load();
  setMode(curMode);
  syncUndo();
})();
</script></body></html>
"""


def build() -> pathlib.Path:
    if not SCHEME.exists():
        raise SystemExit("缺数据源：%s\n先跑 `python ui_scheme.py`" % SCHEME)
    data = json.loads(SCHEME.read_text(encoding="utf-8"))
    act = {"items": [], "stats": {}}
    if ACT_MAP.exists():
        act = json.loads(ACT_MAP.read_text(encoding="utf-8"))
    else:
        print("  ⚠ 缺 %s（先跑 match_activities.py），按活动视图会为空" % ACT_MAP.name)
    OUT.mkdir(parents=True, exist_ok=True)
    page = (PAGE_TPL
            .replace("__DATA__", json.dumps(data, ensure_ascii=False, separators=(",", ":")))
            .replace("__ACT__", json.dumps(act, ensure_ascii=False, separators=(",", ":")))
            .replace("__CW__", str(CANVAS_W))
            .replace("__CH__", str(CANVAS_H)))
    out = OUT / PAGE
    out.write_text(page, encoding="utf-8", newline="\n")
    n_mod = sum(len(v) for g in data["classes"].values() for v in g.values())
    print("  写出 %s（%.1f MB）" % (out, out.stat().st_size / 1e6))
    print("  活动类 %d ｜ 模块 %d ｜ 画布 %d×%d"
          % (len(data["classes"]), n_mod, CANVAS_W, CANVAS_H))
    return out


def baked_css() -> str:
    """只取画布相关的样式（模板里 BAKE 标记之间的那段），保证单一来源。"""
    a = PAGE_TPL.index("/*BAKE-BEGIN*/") + len("/*BAKE-BEGIN*/")
    b = PAGE_TPL.index("/*BAKE-END*/")
    return PAGE_TPL[a:b].strip()


ASSET_RE = re.compile(r"\.\./assets/([^)'\"\s]+\.png)")

BAKE_SHELL = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} · 界面拼装</title>
<style>
*{{box-sizing:border-box}}
html,body{{height:100%}}
body{{margin:0;background:#12151a;color:#8b95a3;display:flex;flex-direction:column;
align-items:center;justify-content:center;gap:10px;
font:12px/1.5 "Noto Sans SC","Microsoft YaHei",system-ui,sans-serif}}
#wrap{{position:relative;flex:0 1 auto}}
{css}
#stage{{margin:0;background-color:#2a2f36;background-image:none}}
.inst{{outline:none!important;cursor:default}}
.inst .lbl{{display:none!important}}
footer{{opacity:.72;text-align:center;padding:0 16px}}
footer b{{color:#c3ccd8;font-weight:600}}
</style></head><body>
<div id="wrap"><div id="stage" style="width:{cw}px;height:{ch}px">{html}</div></div>
<footer><b>{title}</b> · ui_group {grp} · 画布 {cw}×{ch} ·
  模块落点为人手工摆放，非游戏原始布局<br>
  贴图 {n_tex} 张已内联{extra} · 数据源 <code>hd_ui_scheme_reverse</code></footer>
<script>
(function fit(){{
  var cw={cw}, ch={ch}, st=document.getElementById('stage'), w=document.getElementById('wrap');
  function go(){{
    var k=Math.min(1,(innerWidth-48)/cw,(innerHeight-96)/ch);
    st.style.transform='scale('+k+')'; st.style.transformOrigin='0 0';
    st.style.marginBottom=((k-1)*ch)+'px';
    w.style.width=(cw*k)+'px'; w.style.height=(ch*k)+'px';
  }}
  go(); addEventListener('resize', go);
}})();
</script>
</body></html>
"""


def bake(src: pathlib.Path, out: pathlib.Path | None = None) -> int:
    """把页面「导出单文件」得到的 json 烘成自包含 HTML（贴图 base64）。"""
    if not src.exists():
        raise SystemExit("找不到 %s" % src)
    data = json.loads(src.read_text(encoding="utf-8"))
    if data.get("kind") != "ui_composer_bake":
        raise SystemExit("这不是「导出单文件」的 json（缺 kind=ui_composer_bake）")
    html = data.get("stage_html") or ""
    if not html.strip():
        raise SystemExit("stage_html 为空：画布上没有任何模块")
    cw = int(data.get("cw") or CANVAS_W)
    ch = int(data.get("ch") or CANVAS_H)

    names = sorted(set(ASSET_RE.findall(html)))
    miss, hit = [], 0
    for name in names:
        p = ASSETS / name
        if not p.exists():
            miss.append(name)
            continue
        b64 = base64.b64encode(p.read_bytes()).decode("ascii")
        html = html.replace("../assets/" + name, "data:image/png;base64," + b64)
        hit += 1

    extra = ""
    if miss:
        extra = "；<b>缺 %d 张</b>（%s）" % (len(miss), "、".join(miss[:3]))
    title = data.get("cls") or "draft"
    out = out or src.with_suffix(".html")
    out.write_text(BAKE_SHELL.format(
        title=title, grp=data.get("ui_group") or "—", cw=cw, ch=ch,
        css=baked_css(), html=html, n_tex=hit, extra=extra),
        encoding="utf-8", newline="\n")
    print("  单文件 → %s（%.2f MB）｜ 贴图 %d 张内联，缺 %d 张"
          % (out, out.stat().st_size / 1e6, hit, len(miss)))
    return 0


def check() -> int:
    bad = 0
    if not SCHEME.exists():
        print("  ✗ 缺 scheme.json，先跑 ui_scheme.py"); return 1
    data = json.loads(SCHEME.read_text(encoding="utf-8"))
    n_mod = sum(len(v) for g in data["classes"].values() for v in g.values())
    print("  scheme.json：%d 活动类 / %d 模块 / 320 行表" % (len(data["classes"]), n_mod))
    p = OUT / PAGE
    if not p.exists():
        print("  ✗ 缺 %s，先跑 composer.py（无 --check）" % p); return 1
    txt = p.read_text(encoding="utf-8")
    for marker, why in [
        ("const DATA = {\"classes\"", "数据未内联（file:// 会白屏）"),
        ('id="stage"', "缺画布容器"),
        ("hd_ui_scheme_data_base", "缺「不猜位置」口径说明"),
        ("pnl_offset", "缺坐标口径说明"),
    ]:
        if marker not in txt:
            print("  ✗ %s" % why); bad += 1
    if "__DATA__" in txt:
        print("  ✗ 占位符未替换"); bad += 1
    print("  %s %s（%.1f MB）" % ("✓" if not bad else "✗", p, p.stat().st_size / 1e6))
    return 1 if bad else 0


def main() -> int:
    if "--check" in sys.argv:
        return check()
    if "--bake" in sys.argv:
        i = sys.argv.index("--bake")
        args = [a for a in sys.argv[i + 1:] if not a.startswith("--")]
        if not args:
            raise SystemExit("用法：composer.py --bake <导出的 bake_*.json> [--out x.html]")
        src = pathlib.Path(args[0])
        if not src.is_absolute():
            src = pathlib.Path.cwd() / src
        out = None
        if "--out" in sys.argv:
            out = pathlib.Path(sys.argv[sys.argv.index("--out") + 1])
        return bake(src, out)
    build()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
