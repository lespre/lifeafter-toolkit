# -*- coding: utf-8 -*-
"""战斗表现行加游戏面板同款小图标（18px，左对齐）。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/board.html")


def rep(s: str, old: str, new: str, tag: str) -> str:
    if old not in s:
        raise SystemExit("锚点未命中：" + tag)
    return s.replace(old, new, 1)


def main() -> int:
    s = P.read_text(encoding="utf-8")

    s = rep(s,
            '(it.effect_show||[]).forEach(r=>{if(r&&r.name){showMap[normSlot(r.slot_key||r.slot)]=r.name;showMap[normSlot(r.slot)]=r.name;}});',
            '(it.effect_show||[]).forEach(r=>{if(r&&r.name){const h={name:r.name,icon:r.icon_rel||""};'
            'showMap[normSlot(r.slot_key||r.slot)]=h;showMap[normSlot(r.slot)]=h;}});',
            "showMap 存对象")

    s = rep(s,
            'main.forEach(d=>{const k=normSlot(d.label);const hit=showMap[k]||showMap[SLOT_ALIAS[k]];if(hit){d.note=d.name;d.name=hit;d.official=true;}});',
            'main.forEach(d=>{const k=normSlot(d.label);const hit=showMap[k]||showMap[SLOT_ALIAS[k]];'
            'if(hit){d.note=d.name;d.name=hit.name;d.icon=hit.icon;d.official=true;}});',
            "取图标")

    s = rep(s,
            "    return `<li class=\"perf-row\"${tip}><span class=\"perf-cat\">${esc(d.label)}</span>`+",
            "    const ico=d.icon?`<img class=\"perf-icon\" src=\"${esc(d.icon)}\" alt=\"\">`:`<span class=\"perf-icon blank\"></span>`;\n"
            "    return `<li class=\"perf-row\"${tip}>`+ico+`<span class=\"perf-cat\">${esc(d.label)}</span>`+",
            "渲染图标")

    s = rep(s,
            '.perf-name.official{color:#f3e7c8;font-weight:600}',
            '.perf-name.official{color:#f3e7c8;font-weight:600}\n'
            '.perf-icon{width:18px;height:18px;margin-right:8px;vertical-align:-4px;image-rendering:auto;flex:0 0 18px}\n'
            '.perf-icon.blank{display:inline-block}',
            "图标样式")

    P.write_text(s, encoding="utf-8")
    print("已改：战斗表现行左侧加 18px 图标，缺失时留空占位对齐")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
