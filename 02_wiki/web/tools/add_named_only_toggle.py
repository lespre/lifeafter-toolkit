# -*- coding: utf-8 -*-
"""时装板：默认只显示有图；新增「仅玩家可见名」勾选项。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/board.html")


def rep(s: str, old: str, new: str, tag: str) -> str:
    if old not in s:
        raise SystemExit("锚点未命中：" + tag)
    return s.replace(old, new, 1)


def main() -> int:
    s = P.read_text(encoding="utf-8")

    s = rep(s, 'const FR={parts:new Set(),grade:"",img:"",gender:"",sort:""};',
            'const FR={parts:new Set(),grade:"",img:"有图",gender:"",sort:"",named:false};', "FR 初始化")

    s = rep(s, '    FR.img=u.get("frimg")||"";',
            '    FR.img=(u.get("frimg")===null?"有图":u.get("frimg"));\n    FR.named=(u.get("frnamed")==="1");', "URL 预置")

    s = rep(s, 'put("frgrade",FR.grade);put("frimg",FR.img);put("frgender",FR.gender);put("frsort",FR.sort);',
            'put("frgrade",FR.grade);put("frimg",FR.img);put("frgender",FR.gender);put("frsort",FR.sort);'
            'put("frnamed",FR.named?"1":"");', "URL 同步")

    s = rep(s, '  if(FR.img==="含占位"&&it.icon_state!=="含占位")return false;',
            '  if(FR.img==="含占位"&&it.icon_state!=="含占位")return false;\n'
            '  if(FR.named&&it.name_visible===false)return false;', "筛选判定")

    old = '  box.appendChild(one("图示","img",[["全部",items.length,""],["有图",cnt.img["有图"]||0],["含占位",cnt.img["含占位"]||0]],FR.img));'
    new = old + '''
  // 仅玩家可见名：默认不勾；勾上就只留名字能对上玩家可见表的条目
  (function(){
    const namedN=items.filter(it=>it.name_visible!==false).length;
    const lab=document.createElement("label");
    lab.className="fr-grp";
    lab.title="勾上后只显示名字能对上玩家可见表的条目（开发名/工程名会被隐藏）";
    const cb=document.createElement("input");
    cb.type="checkbox";cb.checked=!!FR.named;
    cb.addEventListener("change",()=>{FR.named=cb.checked;redraw();frRender();});
    const em=document.createElement("em");em.textContent="仅玩家可见名";
    const n=document.createElement("span");n.className="n";n.textContent=String(namedN);
    lab.appendChild(em);lab.appendChild(cb);lab.appendChild(n);
    box.appendChild(lab);
  })();'''
    s = rep(s, old, new, "图示分组后插入勾选")

    P.write_text(s, encoding="utf-8")
    print("已加：默认有图 + 仅玩家可见名勾选")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
