# -*- coding: utf-8 -*-
"""武器皮肤「特效与战斗表现」补内部名：每行显示 中文真名 + 内部资源名（.sfx 基名）。"""
from __future__ import annotations
import sys

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

P = pathlib.Path(WEB / "board.html")


def rep(s: str, old: str, new: str, tag: str) -> str:
    if old not in s:
        raise SystemExit("锚点未命中：" + tag)
    return s.replace(old, new, 1)


def main() -> int:
    s = P.read_text(encoding="utf-8")

    s = rep(s,
            '  const put=(k,name,src)=>{\n    if(!k)return;\n    const o=acc[k]||(acc[k]={srcs:[],names:[]});\n    if(src&&o.srcs.indexOf(src)<0)o.srcs.push(src);\n    if(name&&!isWeakName(name)&&o.names.indexOf(name)<0)o.names.push(name);\n  };',
            '  const base=p=>{const t=String(p||"");const i=t.lastIndexOf("/");return i>=0?t.slice(i+1):t;};\n'
            '  const put=(k,name,src,internal)=>{\n    if(!k)return;\n    const o=acc[k]||(acc[k]={srcs:[],names:[],internals:[]});\n    if(src&&o.srcs.indexOf(src)<0)o.srcs.push(src);\n    if(name&&!isWeakName(name)&&o.names.indexOf(name)<0)o.names.push(name);\n    const b=base(internal);\n    if(b&&o.internals.indexOf(b)<0)o.internals.push(b);\n  };',
            "put 增加内部名")

    s = rep(s,
            '  (it.sfx_items||[]).forEach(c=>{if(c)put(BIZ_FROM_SFX[c.sfx_type],c.display_name,"同快照配置");});',
            '  (it.sfx_items||[]).forEach(c=>{if(c)put(BIZ_FROM_SFX[c.sfx_type],c.sfx_name||c.display_name,"同快照配置",c.sfx_params);});',
            "sfx_items 传内部名")

    s = rep(s,
            '  (it.behavior_resources||[]).forEach(r=>{if(r&&r.field)put(BIZ_FROM_BEHAVIOR[r.field],"","行为资源");});',
            '  (it.behavior_resources||[]).forEach(r=>{if(r&&r.field)put(BIZ_FROM_BEHAVIOR[r.field],"","行为资源",r.path);});',
            "behavior 传内部名")

    s = rep(s,
            '    main.push({k:b.k,label:(b.melee&&isMelee)?b.melee:b.t,name:o.names[0]||"",srcs:o.srcs});});',
            '    main.push({k:b.k,label:(b.melee&&isMelee)?b.melee:b.t,name:o.names[0]||"",internals:o.internals,srcs:o.srcs});});',
            "主项带内部名")

    s = rep(s,
            '  known.forEach(k=>main.push({k:k,label:BIZ_EXTRA_LABEL[k],name:acc[k].names[0]||"",srcs:acc[k].srcs}));',
            '  known.forEach(k=>main.push({k:k,label:BIZ_EXTRA_LABEL[k],name:acc[k].names[0]||"",internals:acc[k].internals,srcs:acc[k].srcs}));',
            "附加项带内部名")

    old_row = ('    return `<li class="perf-row"${tip}><span class="perf-cat">${esc(d.label)}</span>`+\n'
               '      (d.name?`<span class="perf-name">${esc(d.name)}</span>`:`<span class="perf-name weak">已配置</span>`)+')
    new_row = ('    const internals=(d.internals||[]).slice(0,3).map(x=>`<code class="perf-internal">${esc(x)}</code>`).join("");\n'
               '    const fallback=(d.internals||[])[0]||"";\n'
               '    return `<li class="perf-row"${tip}><span class="perf-cat">${esc(d.label)}</span>`+\n'
               '      (d.name?`<span class="perf-name">${esc(d.name)}</span>`\n'
               '             :(fallback?`<span class="perf-name">${esc(fallback)}</span>`:`<span class="perf-name weak">已配置</span>`))+\n'
               '      internals+')
    s = rep(s, old_row, new_row, "渲染行加内部名")

    P.write_text(s, encoding="utf-8")
    print("已改：战斗表现行 = 类型 + 中文真名 + 内部名（最多 3 个）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
