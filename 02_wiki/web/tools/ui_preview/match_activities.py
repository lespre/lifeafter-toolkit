# -*- coding: utf-8 -*-
r"""活动 → 控件模块 的**可复算**匹配表（从 `huodong_conf` 逐行取值）。

═══════════════════════════════════════════════════════════════════════════
★ 这张表补的是什么
   之前 `ACTIVITY_PANEL_EVIDENCE.md` 的结论是「活动 → 面板不可由数据推出」，
   依据是 `ui_class` 脚本里只有 `load_hd_ui_scheme(ui_group_id)`、没有 `.csb` 字面量。
   **那个结论只对「面板组成」成立，对「活动 → 用哪套模块」不成立**：
   `huodong_conf_data` 的行里其实直接带
       hd_class       活动处理器类（3457 行）
       ui_class       界面类（3152 行）
       use_ui         1=旧界面 / 2=HD 动态界面（3100 行）
       ui_group_id    该活动用哪个 ui_group（84 行，新活动才有这个字段）
       use_ui_scheme  另一套 scheme 编号（265 行，指向缺失的 hd_ui_scheme 基表，解不了）
   所以「某个活动用哪一组模块」是**能对上**的，只是覆盖率有限：
   90 / 635 个 hd_class 在 reverse 表里有模块。

★ 口径
   match = "scheme"    hd_class 在表里，且 ui_group_id 这一组存在 → 可直接拼
   match = "class"     hd_class 在表里，但 ui_group_id 那组不存在 / 没填组
   match = "none"      这个类根本没有控件模块数据（旧界面居多）
   状态按 start_ts/end_ts 与当前时间比，**不用 activity_master 的旧快照**。

★ 用法
   python match_activities.py            # 落 _ui_preview/scheme/activity_ui_map.json
   python match_activities.py --check    # 只体检
"""
from __future__ import annotations

import importlib.util
import json
import pathlib
import sys
import time

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent))
import la_paths  # noqa: E402

ROOT = la_paths.find_project_root()
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
SCHEME = ROOT / "_ui_preview/scheme/scheme.json"
OUT = ROOT / "_ui_preview/scheme/activity_ui_map.json"
CORE = ROOT / "00_规范与工具/工具/工具库/00_共享核心"

FIELDS = ("name", "hd_class", "ui_class", "use_ui", "ui_group_id",
          "use_ui_scheme", "start_ts", "end_ts", "sub_title", "first_level_tab")


def load_conf() -> list[tuple[int, dict]]:
    """huodong_conf 逐行取值（与 build_activity_master 同一台 mini-VM）。"""
    sys.path.insert(0, str(CORE))
    import importlib.util as iu
    spec = iu.spec_from_file_location("vm_cdata_table", HERE.parent / "vm_cdata_table.py")
    vm = iu.module_from_spec(spec)
    spec.loader.exec_module(vm)
    from toolkit_core import script_decode as SD           # noqa: N813
    _r, code, _e = SD.load_module(str(CD / "huodong_conf_data.py"))
    vm.run(code)
    return [(k, v) for k, v in vm.MAPADD if isinstance(v, dict)]


def fmt(ts) -> str:
    try:
        return time.strftime("%Y-%m-%d", time.localtime(float(ts)))
    except (TypeError, ValueError, OSError):
        return ""


def status_of(start, end, now: float) -> str:
    try:
        s, e = float(start), float(end)
    except (TypeError, ValueError):
        return "无时间"
    if e and now > e:
        return "已结束"
    if s and now < s:
        return "未开始"
    return "进行中"


def build() -> dict:
    scheme = json.loads(SCHEME.read_text(encoding="utf-8"))["classes"]
    rows = load_conf()
    now = time.time()
    # 包里到底有没有这个界面的脚本？用来区分「没匹配上」和「本来就没有」
    stems = {p.stem for p in (CD / "ui").glob("*.py")} if (CD / "ui").is_dir() else set()

    items, seen = [], set()
    n_named = n_class_in = 0
    for key, v in rows:
        name = v.get("name")
        if not name:
            continue
        n_named += 1
        hd = v.get("hd_class") or ""
        gid = v.get("ui_group_id")
        gid = "" if gid in (None, "") else str(gid)
        if hd in scheme:
            n_class_in += 1
            groups = scheme[hd]
            if gid and gid in groups:
                match = "scheme"
            else:
                match = "class"
                # 没填组时退到「该类第一个组」，但**标记成 class**，页面不得当成事实
                gid = sorted(groups, key=lambda x: int(x) if x.isdigit() else 0)[0] if groups else ""
        else:
            match = "none"

        mods = scheme.get(hd, {}).get(gid, []) if match != "none" and gid else []
        uc = v.get("ui_class") or ""
        sc = 1 if ((uc and uc in stems) or (hd and hd in stems)) else 0
        item = {
            "k": int(key), "n": name,
            "hc": hd, "uc": uc,
            "ui": v.get("use_ui"), "gid": gid, "us": v.get("use_ui_scheme") or "",
            "s": fmt(v.get("start_ts")), "e": fmt(v.get("end_ts")),
            "st": status_of(v.get("start_ts"), v.get("end_ts"), now),
            "m": match, "sc": sc,
            "mods": len(mods),
            "w": sum(len(m["widgets"]) for m in mods),
        }
        sig = (item["k"], item["hc"], gid)
        if sig in seen:
            continue
        seen.add(sig)
        items.append(item)

    order = {"进行中": 0, "未开始": 1, "无时间": 2, "已结束": 3}
    items.sort(key=lambda x: (order.get(x["st"], 9),
                              x["e"] or x["s"] or "", -x["mods"]))

    stat = {
        "rows": len(rows), "named": n_named, "items": len(items),
        "class_in_scheme": n_class_in,
        "scheme": sum(1 for i in items if i["m"] == "scheme"),
        "class_only": sum(1 for i in items if i["m"] == "class"),
        "none": sum(1 for i in items if i["m"] == "none"),
        "no_script": sum(1 for i in items if i["m"] == "none" and not i.get("sc")),
        "classes_total": len(scheme),
        "by_status": {s: sum(1 for i in items if i["st"] == s) for s in order},
    }
    return {"generated": time.strftime("%Y-%m-%d %H:%M"),
            "now": int(now), "stats": stat, "items": items}


def build_page(data: dict) -> pathlib.Path:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8", newline="\n")
    print("  %s（%.0f KB）" % (OUT, OUT.stat().st_size / 1024))
    s = data["stats"]
    print("  活动 %d 条（带名字 %d）｜ 可拼 scheme %d ｜ 仅对到类 %d ｜ 无模块数据 %d"
          % (s["items"], s["named"], s["scheme"], s["class_only"], s["none"]))
    print("  状态：进行中 %d / 未开始 %d / 已结束 %d / 无时间 %d"
          % (s["by_status"]["进行中"], s["by_status"]["未开始"],
             s["by_status"]["已结束"], s["by_status"]["无时间"]))
    return OUT


def check() -> int:
    if not SCHEME.exists():
        print("  ✗ 缺 scheme.json，先跑 ui_scheme.py"); return 1
    if not OUT.exists():
        print("  ✗ 缺 %s，先跑 match_activities.py" % OUT.name); return 1
    d = json.loads(OUT.read_text(encoding="utf-8"))
    bad = 0
    for k in ("now", "stats", "items"):
        if k not in d:
            print("  ✗ 缺字段 %s" % k); bad += 1
    if d.get("stats", {}).get("scheme", 0) < 1:
        print("  ✗ 一条都没对到 scheme"); bad += 1
    # 时间戳必须是「算出来的」，不能是写死的字符串
    for it in d["items"][:1]:
        for f in ("s", "e"):
            v = it.get(f, "")
            if v and not (len(v) == 10 and v[4] == "-"):
                print("  ✗ 日期格式异常 %r" % v); bad += 1
    print("  %s %s" % ("✓" if not bad else "✗", OUT))
    return 1 if bad else 0


def main() -> int:
    if "--check" in sys.argv:
        return check()
    build_page(build())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
