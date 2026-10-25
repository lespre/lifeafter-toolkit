# -*- coding: utf-8 -*-
"""场景平衡板：右侧改表格视图（含按服型/来源筛选、点表头排序）。

只对 board id = scene_balance 生效，其它板块不动。
"""
from __future__ import annotations

import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
HTML = WEB / "board.html"

CSS = """
/* ── 场景平衡表格模式（board id = scene_balance）── */
body.scene-mode .grid{display:block;overflow:auto;border:1px solid #1e2b33;border-radius:10px;background:#0f161c}
body.scene-mode .grid table.sbt{width:100%;border-collapse:collapse;font-size:12.5px}
body.scene-mode .sbt thead th{position:sticky;top:0;background:#131c23;color:#8fa3b0;font-weight:500;
  text-align:left;padding:9px 12px;border-bottom:1px solid #22303a;white-space:nowrap;cursor:pointer;user-select:none}
body.scene-mode .sbt thead th:hover{color:#cfe4f2}
body.scene-mode .sbt tbody td{padding:8px 12px;border-bottom:1px solid #182129;color:#dbe6ee;white-space:nowrap}
body.scene-mode .sbt tbody tr:hover td{background:#131d25}
body.scene-mode .sbt td.num{font-family:ui-monospace,Consolas,monospace;color:#a9c0cf}
body.scene-mode .sbt td.scene{color:#eaf2f8}
body.scene-mode .sbt .tag{display:inline-block;padding:1px 7px;border-radius:999px;font-size:11px;
  border:1px solid #2a3a45;color:#9dbccd;background:#141e26}
"""

JS_CONST = """const SCENE_TABLE=(function(){try{return (getParam("b")||"")==="scene_balance";}catch(e){return false;}})();
if(SCENE_TABLE)document.body.classList.add("scene-mode");
"""

JS_FUNC = """
/* 场景平衡表格：列可点排序；沿用既有自定义筛选（服型/来源）与搜索 */
let SB_SORT={key:"name",dir:1};
function sbVal(it,k){
  if(k==="场景编号")return (it["场景编号"]||"").replace(/[^0-9,，]/g,"");
  if(k==="服型")return it["服型"]||"";
  if(k==="加成下限")return Number(it.lower);
  if(k==="加成上限")return Number(it.upper);
  if(k==="生效最低攻击")return Number(it.min_attack);
  if(k==="来源类型")return it["来源类型"]||"";
  if(k==="加成区间")return it.range||"";
  return it.name||"";
}
function sbRender(items){
  const cols=["场景","场景编号","服型","加成下限","加成上限","加成区间","生效最低攻击","来源类型"];
  const sorted=items.slice().sort((a,b)=>{
    const k=SB_SORT.key,v1=sbVal(a,k),v2=sbVal(b,k);
    if(typeof v1==="number"&&typeof v2==="number"){
      if(v1!==v2)return (v1-v2)*SB_SORT.dir;
    }else{
      const c=String(v1).localeCompare(String(v2),"zh-CN");
      if(c)return c*SB_SORT.dir;
    }
    return String(a.name||"").localeCompare(String(b.name||""),"zh-CN");
  });
  const g=document.getElementById("grid");
  g.innerHTML="";
  const t=document.createElement("table");
  t.className="sbt";
  const thead=document.createElement("thead");
  const trh=document.createElement("tr");
  for(const c of cols){
    const th=document.createElement("th");
    th.textContent=c+(SB_SORT.key===c?(SB_SORT.dir>0?" ▲":" ▼"):"");
    th.onclick=()=>{
      if(SB_SORT.key===c)SB_SORT.dir*=-1;else{SB_SORT.key=c;SB_SORT.dir=1;}
      render();
    };
    trh.appendChild(th);
  }
  thead.appendChild(trh);t.appendChild(thead);
  const tb=document.createElement("tbody");
  for(const it of sorted){
    const tr=document.createElement("tr");
    const cells=[
      ["scene",it.name||""],
      ["num",(it["场景编号"]||"").replace(" 个：","")],
      ["",`<span class="tag">${esc(it["服型"]||"-")}</span>`],
      ["num",it.lower??"-"],
      ["num",it.upper??"-"],
      ["num",it.range||"-"],
      ["num",it.min_attack??"-"],
      ["","<span class=\"tag\">"+esc(it["来源类型"]||"-")+"</span>"],
    ];
    for(const [cls,val] of cells){
      const td=document.createElement("td");
      if(cls)td.className=cls;
      if(cls==="num")td.textContent=val; else td.innerHTML=String(val);
      tr.appendChild(td);
    }
    tb.appendChild(tr);
  }
  t.appendChild(tb);g.appendChild(t);
  const c=document.getElementById("count");
  if(c)c.textContent=`显示 ${items.length} / ${DATA.items.length} 条`;
}
"""


def main() -> int:
    s = HTML.read_text(encoding="utf-8")

    if "scene-mode" not in s:
        anchor = "/* ── 载具模式（board id = vehicle_full）"
        i = s.find(anchor)
        if i < 0:
            raise SystemExit("CSS 锚点未命中")
        s = s[:i] + CSS.strip() + "\n\n" + s[i:]

    if "const SCENE_TABLE=" not in s:
        anchor = "const VEHICLE_BOARD="
        i = s.find(anchor)
        if i < 0:
            raise SystemExit("常量锚点未命中")
        s = s[:i] + JS_CONST + s[i:]

    if "function sbRender(" not in s:
        anchor = "function render(){"
        i = s.find(anchor)
        if i < 0:
            raise SystemExit("render 锚点未命中")
        s = s[:i] + JS_FUNC.strip() + "\n\n" + s[i:]

    old = '  const g=document.getElementById("grid");g.innerHTML="";'
    if "if(SCENE_TABLE){ sbRender(items); return; }" not in s:
        if old not in s:
            raise SystemExit("grid 锚点未命中")
        s = s.replace(old, '  if(SCENE_TABLE){ sbRender(items); return; }\n' + old, 1)

    HTML.write_text(s, encoding="utf-8")
    print("场景平衡已切换为表格模式")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
