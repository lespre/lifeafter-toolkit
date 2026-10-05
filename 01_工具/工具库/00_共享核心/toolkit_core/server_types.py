# -*- coding: utf-8 -*-
r"""服务器类型（服型）后缀 —— ★ 全项目唯一来源。

## 为什么要有这个模块
服型后缀（`_auto_oversea_data_<后缀>` / `<表名>_<后缀>.py`）此前**散在两处**：
`lottery_locate.VARIANT_NAMES` 与 `lottery_chain` 的注释里各写一份 —— 结论写在注释里
等于没写（本项目的既有教训）。这里固化成一份，并附**依据**与**本客户端实际存在性**。

## 术语
`_auto_oversea_data_<后缀>` = **服务器类型变体**（不是"渠道"）。同一张逻辑表在不同服型下
可能内容不同（实测幻夜神谕：base 表 lottery_id=391821，kj1/kjxq 表 = 391831）。

## 依据（都是客户端自带，可复核）
① `com/cdata/server_cluster_data.py`：`theme` → `theme_name`
     theme=kj1  → 简单生存   （hostnum 10008/20018/21018…）
     theme=yk   → 会员专享   （hostnum 10010/10011）＝ 月卡服
     theme=yh   → 硬核       （hostnum 10009）
     theme=kjhmt/kjjp/kjna/kjsea → 简单生存（region=hmt/jp/na/sea）
     `table_region_code` = 表名侧代号：kjxq / xq / ykxq
② `com/cdata/server_group_data.py`：`theme_type` / `region_name`（共创特别季/特色专属服务器/各地区专区）
③ `com/cdata/new_server_show_data.py`：tags 池 经典服 / 卡级直升 / 简单生存
★ 用户口径：硬核服【没有奖池】⇒ `yh` 无池表族是预期；经典服【可能不走后缀】（用无后缀 base）。

`xq` / `xyd` / `cn`：用户也不确定 ⇒ 标「未定」，**不推断**。
"""
from __future__ import annotations

from pathlib import Path

#: 后缀 → (中文名, 依据/备注)
VARIANT_NAMES: dict[str, tuple[str, str]] = {
    "kj1": ("简单生存", "server_cluster_data: theme=kj1 → theme_name=简单生存"),
    "kjxq": ("简单生存", "table_region_code=kjxq → theme=kj1"),
    "kjjp": ("简单生存·日本", "theme=kjjp, region=jp"),
    "kjna": ("简单生存·北美", "theme=kjna, region=na"),
    "kjhmt": ("简单生存·港澳台", "theme=kjhmt, region=hmt"),
    "kjsea": ("简单生存·东南亚", "theme=kjsea, region=sea"),
    "yk": ("会员专享（月卡服）", "server_cluster_data: theme=yk → theme_name=会员专享"),
    "yxq": ("会员专享·新区？", "未证；table_region_code=ykxq 同一族，标待确认"),
    "ykxq": ("会员专享·新区", "table_region_code=ykxq"),
    "yh": ("硬核", "theme=yh；★无奖池、无表后缀（用户口径）"),
    "jp": ("日本区", "region=jp"),
    "na": ("北美区", "region=na"),
    "au": ("澳洲区", "region=au"),
    "eu": ("欧洲区", "region=eu"),
    "hmt": ("港澳台区", "region=hmt"),
    "kr": ("韩国区", "region=kr"),
    "sea": ("东南亚区", "region=sea"),
    "xq": ("未定（★待确认）", "用户也不确定"),
    "xyd": ("未定（★待确认）", "用户也不确定"),
    "cn": ("未定（★待确认）", "用户也不确定"),
}

#: 扫描顺序（先长后短，避免 `kj1` 吃掉 `kjxq` 之类的前缀误判）
SUFFIX_ORDER = sorted(VARIANT_NAMES, key=len, reverse=True)


def label(suffix: str | None) -> str:
    """后缀 → 可读标签。空后缀 = base（通用/经典服）。未知后缀如实标未定，不推断。

    ★ 支持复合后缀（实测存在 `..._auto_oversea_data_kjxq_kj1.py` 这种双后缀名：
      一份名字里同时写 region_code 与 theme，正好自证 kjxq→kj1 的对应）。
    """
    if not suffix:
        return "base（通用/经典服）"
    got = VARIANT_NAMES.get(suffix)
    if got:
        return "%s %s" % (suffix, got[0])
    if "_" in suffix:
        parts = [p for p in suffix.split("_") if p]
        names = []
        for p in parts:
            g = VARIANT_NAMES.get(p)
            if g is None:
                return "%s 未定（★未收录，不推断）" % suffix
            if g[0] not in names:
                names.append(g[0])
        return "%s %s" % (suffix, " + ".join(names))
    return "%s 未定（★未收录，不推断）" % suffix


def why(suffix: str | None) -> str:
    if not suffix:
        return "无后缀；用户口径「经典服可能不走后缀、用 base 表」"
    got = VARIANT_NAMES.get(suffix)
    if got:
        return got[1]
    if "_" in suffix:
        parts = [p for p in suffix.split("_") if p]
        return "复合后缀：%s" % " ; ".join("%s=%s" % (p, VARIANT_NAMES.get(p, ("未收录",))[0])
                                          for p in parts)
    return "未收录"


def split_suffix(stem: str) -> tuple[str, str]:
    """表名主干 → (逻辑表名, 服型后缀)。识别两种写法：
       ① `X_auto_oversea_data_kj1`   ② `X_kj1` / `X_chs`（chs 不算服型）
    """
    s = stem
    if "_auto_oversea_data_" in s:
        head, _, suf = s.partition("_auto_oversea_data_")
        if suf.endswith("_chs"):
            suf = suf[:-4]
        return head, suf
    for suf in SUFFIX_ORDER:
        if s.endswith("_" + suf):
            return s[: -(len(suf) + 1)], suf
    return s, ""


def scan_tree(tree: Path | None = None, limit_dirs: int = 0) -> dict:
    """扫还原树里各服型实际有多少张表（回答「这个服型在本客户端有没有表族」）。

    只按【文件名后缀】统计，不做内容解析 —— 便宜且足够判断存在性。
    """
    tree = Path(tree) if tree else Path(r"E:\la拆包项目\03_执行\41_还原树")
    per: dict[str, dict] = {}
    scanned = 0
    if not tree.is_dir():
        return {"tree": str(tree), "error": "树不存在", "per_suffix": {}}
    for p in tree.rglob("*.py"):
        parts = p.parts
        if "com" not in parts or "cdata" not in parts:
            continue
        scanned += 1
        _, suf = split_suffix(p.stem)
        if not suf:
            continue
        d = per.setdefault(suf, {"files": 0, "containers": set(), "sample": []})
        d["files"] += 1
        try:
            d["containers"].add(str(p.relative_to(tree).parts[0]))
        except ValueError:
            pass
        if len(d["sample"]) < 3:
            d["sample"].append(p.name)
    out = {}
    for suf, d in per.items():
        lbl = label(suf)
        nm = lbl.split(" ", 1)[1] if " " in lbl else lbl
        ev = why(suf)
        out[suf] = {"name": nm, "evidence": ev, "files": d["files"],
                    "containers": sorted(d["containers"]), "sample": d["sample"]}
    return {"tree": str(tree), "scanned_py": scanned, "per_suffix": out,
            "unknown": sorted(k for k in out if "未定" in out[k]["name"])}


if __name__ == "__main__":
    import json
    r = scan_tree()
    print("扫 %d 个 cdata 表文件（%s）" % (r.get("scanned_py", 0), r.get("tree")))
    rows = sorted(r["per_suffix"].items(), key=lambda kv: -kv[1]["files"])
    print("%-8s %-22s %7s  %s" % ("后缀", "中文名", "表数", "依据"))
    for suf, d in rows:
        print("%-8s %-22s %7d  %s" % (suf, d["name"], d["files"], d["evidence"][:44]))
    if r.get("unknown"):
        print("\n★ 未收录后缀（需补）：%s" % r["unknown"])
