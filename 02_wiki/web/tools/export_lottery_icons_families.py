#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""只给奖池板上的两族补图标：异变核芯 660xxx / 芯片 330xxx·331xxx。

命名规则（不是猜的，来自配置表里的 icon 字段）：
  1) 主源 = common_item_data（真表在 01_索引与产物/30_分析/90_表缓存/
     base_B42760CCA41DBC25.py，字符串池是同目录 base_EF3A8474A5E5F7A4.py）
     每行 `icon` 字段直接给 `ui/item_icon/icon_xxx`，再补档位后缀 _b/_s 定位 .ktx。
       · 异变核芯 660xxx → icon 是【元素图标】icon_jin_huo / icon_jin_bing /
         icon_jin_dian / icon_jin_suan（同一元素的多枚核芯共用一张）
       · 芯片 330xxx/331xxx → icon 是 icon_330NNN（★ 与 item_id 不是同一编号空间：
         330013 雷霆一击 → icon_330032；icon_330013 是 330008 轻装上阵的图）
  2) 兜底 = chip_type_data（chip_name → chip_big_icon/chip_icon），只用于 item 表缺行的 id
     （目前只有 331032 处变不惊）。

解码：KTX 走 android_gpk.parse_ktx + _ktx_rgba（ETC2_EAC），
      CompBlks 走 pe_icon_bind.decoders.decode_compblks（_s 常见格式）。
只用 PE 还原树资源，不碰 PC/APK。
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_索引与产物/10_索引/热更检测/pe_icon_bind"))
from toolkit_core import android_gpk as AG  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402
import decoders as DEC  # noqa: E402

CORE_PREFIX = "660"
CHIP_PREFIXES = ("330", "331")
SUFFIXES = ("_b", "_s", "")          # 档位优先级：大图横幅 > 小图 > 裸名


# ---------- 表解码 ----------
def _load_body(name: str) -> bytes | None:
    """从 0x73 表文件里切出 bindict 表体（7b|fb + u32 长度 + 载荷）。"""
    b = (CD / f"{name}.py").read_bytes()
    for i in range(len(b) - 5):
        if b[i] in (0x7B, 0xFB):
            n = struct.unpack_from("<I", b, i + 1)[0]
            if 8 <= n <= len(b) - i - 5 and i + 5 + n <= len(b):
                cnt = struct.unpack_from("<I", b, i + 5)[0]
                if 0 < cnt < 200000 and 8 + 4 * cnt < n + 8:
                    return b[i + 5:i + 5 + n]
    return None


def _pool(name: str) -> list[str]:
    p = CD / f"{name}_chs.py"
    return BT.parse_legacy_chs_pool(p.read_bytes()[12:]) if p.exists() else []


def item_icon_map() -> dict[str, str]:
    """common_item_data：item_id → icon 路径（无扩展名、无档位后缀）。"""
    body_f = CACHE / "base_B42760CCA41DBC25.py"
    pool_f = CACHE / "base_EF3A8474A5E5F7A4.py"
    if not (body_f.exists() and pool_f.exists()):
        raise SystemExit(f"缺表缓存：{body_f} / {pool_f}")
    b = body_f.read_bytes()
    off = b.find(b"\x7b", 264)
    n = struct.unpack_from("<I", b, off + 1)[0]
    body = b[off + 5:off + 5 + n]
    pool = BT.parse_legacy_chs_pool(pool_f.read_bytes()[12:])
    rows, _ = BT.decode_table_rows(body, pool, lenient=True)

    def g(v, k):
        x = v.get(k)
        return x[1] if isinstance(x, (list, tuple)) and len(x) == 2 else x

    out: dict[str, str] = {}
    for r in rows:
        iid, icon = g(r["values"], "id"), g(r["values"], "icon")
        if iid and icon:
            out[str(iid)] = icon
    return out


def chip_name_icon_map() -> dict[str, str]:
    """chip_type_data：chip_name → chip 图标（兜底用）。"""
    body = _load_body("chip_type_data")
    pool = _pool("chip_type_data")
    rows, _ = BT.decode_table_rows(body, pool) if body else ([], [])

    def g(v, k):
        x = v.get(k)
        return x[1] if isinstance(x, (list, tuple)) and len(x) == 2 else x

    out: dict[str, str] = {}
    for r in rows:
        nm, big, sm = g(r["values"], "chip_name"), g(r["values"], "chip_big_icon"), g(r["values"], "chip_icon")
        if nm and (big or sm):
            out[nm] = "ui/item_icon/" + (big or sm)
    return out


# ---------- 资源定位 + 解码 ----------
def find_asset(icon: str) -> Path | None:
    """icon 形如 ui/item_icon/icon_x → 按档位顺序找 .ktx。"""
    rel = icon.replace("/", "\\")
    base = Path(str(TREE) + "\\" + rel)
    if base.suffix:
        base = base.with_suffix("")
    stem = base.name
    for suf in SUFFIXES:
        if stem.endswith(("_b", "_s", "_max", "_mid")) and suf:
            continue
        p = base.with_name(stem + suf + ".ktx")
        if p.exists():
            return p
    return None


def decode(path: Path) -> np.ndarray | None:
    data = path.read_bytes()
    if data.startswith(b"CompBlks"):
        arr = DEC.decode_compblks(data)
        return None if arr is None else np.asarray(arr)
    info = AG.parse_ktx(data)
    if not info:
        return None
    return AG._ktx_rgba(data, info)


def magenta_ratio(arr: np.ndarray) -> float:
    if arr.ndim != 3 or arr.shape[2] < 3:
        return 0.0
    m = (arr[..., 0] == 255) & (arr[..., 1] == 0) & (arr[..., 2] == 255)
    return float(m.mean())


def main() -> int:
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    fam: dict[str, str] = {}
    for it in board["items"]:
        iid = str(it.get("item_id") or "")
        if not iid:
            continue
        if iid.startswith(CORE_PREFIX) or iid.startswith(CHIP_PREFIXES):
            fam[iid] = it.get("name") or ""

    imap = item_icon_map()
    chip_by_name = chip_name_icon_map()

    OUT.mkdir(parents=True, exist_ok=True)
    rep = {"core": {"ids": 0, "hit": 0, "exported": 0, "miss": []},
           "chip": {"ids": 0, "hit": 0, "exported": 0, "miss": []},
           "detail": []}

    for iid in sorted(fam):
        grp = "core" if iid.startswith(CORE_PREFIX) else "chip"
        rep[grp]["ids"] += 1
        icon = imap.get(iid)
        src = "common_item_data.icon"
        if not icon:
            icon = chip_by_name.get(fam[iid])
            src = "chip_type_data.chip_big_icon(name join)"
        if not icon:
            rep[grp]["miss"].append({"id": iid, "name": fam[iid], "why": "表里没有该道具行"})
            continue
        path = find_asset(icon)
        if not path:
            rep[grp]["miss"].append({"id": iid, "name": fam[iid], "icon": icon, "why": "图标文件未在 PE 树"})
            continue
        rep[grp]["hit"] += 1
        try:
            arr = decode(path)
        except Exception as exc:  # noqa: BLE001
            rep[grp]["miss"].append({"id": iid, "icon": icon, "why": f"decode {type(exc).__name__}"})
            continue
        if arr is None:
            rep[grp]["miss"].append({"id": iid, "icon": icon, "why": f"解码失败 {path.name}"})
            continue
        if magenta_ratio(arr) > 0.30:
            rep[grp]["miss"].append({"id": iid, "icon": icon, "why": "解出大面积品红，判解错"})
            continue
        dst = OUT / f"{iid}.png"
        Image.fromarray(np.ascontiguousarray(arr.astype("uint8"))).save(dst)
        rep[grp]["exported"] += 1
        rep["detail"].append({"id": iid, "name": fam[iid], "icon": icon,
                              "file": str(path).replace(str(TREE) + "\\", ""),
                              "size": f"{arr.shape[1]}x{arr.shape[0]}", "from": src})

    print(json.dumps({k: v for k, v in rep.items() if k != "detail"}, ensure_ascii=False, indent=1))
    for d in rep["detail"]:
        print(f"  {d['id']} {d['name'][:22]:<24} {d['file']:<58} {d['size']}")
    (WEB / "tools/_last_export_families.json").write_text(
        json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
