# -*- coding: utf-8 -*-
"""武器皮肤卡：战斗表现优先显示游戏内正式名（weapon_skin_effect_show_data），
备注名与资源基名作为次要信息保留。"""
from __future__ import annotations

import pathlib

P = pathlib.Path("E:/la拆包项目/02_wiki/web/board.html")


def rep(s: str, old: str, new: str, tag: str) -> str:
    if old not in s:
        raise SystemExit("锚点未命中：" + tag)
    return s.replace(old, new, 1)


def main() -> int:
    s = P.read_text(encoding="utf-8")

    # 1) 在 main 组装完后，用正式名覆盖显示名，原备注名降级为 note
    s = rep(s,
            '  known.forEach(k=>main.push({k:k,label:BIZ_EXTRA_LABEL[k],name:acc[k].names[0]||"",internals:acc[k].internals,srcs:acc[k].srcs}));',
            '  known.forEach(k=>main.push({k:k,label:BIZ_EXTRA_LABEL[k],name:acc[k].names[0]||"",internals:acc[k].internals,srcs:acc[k].srcs}));\n'
            '  const normSlot=t=>String(t||"").replace(/[（(][^）)]*[）)]/g,"").trim();\n'
            '  const showMap={};\n'
            '  (it.effect_show||[]).forEach(r=>{if(r&&r.name)showMap[normSlot(r.slot_key||r.slot)]=r.name;});\n'
            '  main.forEach(d=>{const hit=showMap[normSlot(d.label)];if(hit){d.note=d.name;d.name=hit;d.official=true;}});',
            "正式名覆盖")

    # 2) 渲染：真名在前，备注名其后（小字）
    s = rep(s,
            '      (d.name?`<span class="perf-name">${esc(d.name)}</span>`\n'
            '             :(fallback?`<span class="perf-name">${esc(fallback)}</span>`:`<span class="perf-name weak">已配置</span>`))+',
            '      (d.name?`<span class="perf-name${d.official?" official":""}">${esc(d.name)}</span>`\n'
            '             :(fallback?`<span class="perf-name">${esc(fallback)}</span>`:`<span class="perf-name weak">已配置</span>`))+\n'
            '      (d.note&&d.official?`<span class="perf-note">${esc(d.note)}</span>`:"")+',
            "渲染真名+备注名")

    # 3) 样式
    s = rep(s,
            '<style>',
            '<style>\n'
            '.perf-name.official{color:#f3e7c8;font-weight:600}\n'
            '.perf-note{color:var(--muted,#8b8b8b);font-size:12px;margin-left:8px;opacity:.75}\n',
            "样式")

    P.write_text(s, encoding="utf-8")
    print("已改：战斗表现 = 游戏内正式名（主） + 备注名（次） + 资源基名（右）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
