# -*- coding: utf-8 -*-
"""扫描当前客户端包：找出**武器皮肤图鉴/UI 真正引用的图片资源路径**。

为什么要这样找：图鉴面板显示的不是随便的纹理，而是面板模块自己声明的资源
（ui/... .png / 模型 .gim / spine）。此前"挖出来的图片是错的纹理"就是因为
没有从**面板引用**出发，而是按名字猜纹理。

做法（只读，不改源包）：
  逐 entry 解包（AES + lz4/zstd）→ 在 payload 里找
    (a) 含 weapon_skin / skin_ 的图片或模型路径字面
    (b) PanelWeaponSkin* 面板模块名
  命中即记录：entry / file_id / 命中串 / 上下文。

产物：analysis/audit/weapon_skin_ui_asset_paths.json
用法：python tools/scan_weapon_skin_ui_assets.py [--max N] [--sha8 508bb5bd]
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")

PKG = Path(r"E:\mrzh\Documents\script.py314.lc.npk")

PATHS = re.compile(
    rb"[A-Za-z0-9_/\\\.-]{4,140}\.(?:png|jpg|jpeg|tga|dds|gim|prefab|mat|spine|skel|atlas|wem|bnk)",
    re.I)
PANELS = re.compile(rb"(?:Panel|UI|Widget)[A-Za-z_]*[Ss]kin[A-Za-z_]*", re.I)


def open_table(fh):
    import npk_reader as NR
    head = NR.aes_ecb(fh.read(64))
    off, cnt = struct.unpack_from("<I", head, 16)[0], struct.unpack_from("<I", head, 20)[0]
    fh.seek(off)
    return NR, NR.aes_ecb(fh.read(cnt * 48)), cnt


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=0)
    ap.add_argument("--sha8", default="508bb5bd")
    a = ap.parse_args()
    hits, panels, kinds = [], [], Counter()
    with PKG.open("rb") as fh:
        NR, table, cnt = open_table(fh)
        n = a.max or cnt
        for idx in range(n):
            e = table[idx * 48:(idx + 1) * 48]
            fid = struct.unpack_from("<Q", e, 0)[0]
            off, ps, ds = (struct.unpack_from("<I", e, 8)[0], struct.unpack_from("<I", e, 12)[0],
                           struct.unpack_from("<I", e, 16)[0])
            flag = struct.unpack_from("<i", e, 28)[0]
            if ps <= 0 or off <= 0:
                continue
            fh.seek(off)
            try:
                pl = NR.unpack_entry(fh.read(ps), ds, flag)
            except Exception:
                continue
            low = pl.lower()
            if b"skin" not in low and b"weapon_skin" not in low:
                continue
            for m in PATHS.finditer(pl):
                s = m.group(0).decode("utf-8", "ignore")
                if "skin" in s.lower() or "wuqiku" in s.lower():
                    hits.append({"entry": idx, "file_id": f"{fid:016X}", "path": s})
                    kinds[s.rsplit(".", 1)[-1].lower()] += 1
            for m in PANELS.finditer(pl):
                panels.append({"entry": idx, "file_id": f"{fid:016X}",
                               "name": m.group(0).decode("utf-8", "ignore")})
            if idx % 5000 == 0:
                print(f"  ..{idx}/{cnt}", flush=True)
    OUT = ROOT / "analysis" / "audit" / "weapon_skin_ui_asset_paths.json"
    doc = {"schema": "weapon-skin-ui-asset-paths-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "snapshot_sha8": a.sha8, "scanned_entries": n,
           "path_hit_count": len(hits), "panel_hit_count": len(panels),
           "by_ext": dict(kinds.most_common()),
           "ui_paths": sorted({h["path"] for h in hits if h["path"].lower().startswith(("ui/", "ui\\"))})[:400],
           "model_paths": sorted({h["path"] for h in hits if h["path"].lower().endswith(".gim")})[:200],
           "audio_paths": sorted({h["path"] for h in hits if h["path"].lower().endswith((".wem", ".bnk"))})[:200],
           "panels": sorted({p["name"] for p in panels})[:80],
           "raw_hits": hits[:1500]}
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: doc[k] for k in ("scanned_entries", "path_hit_count", "panel_hit_count", "by_ext")},
                     ensure_ascii=False))
    print("panels:", doc["panels"][:20])
    print("ui_paths(前 20):", doc["ui_paths"][:20])
    print("→", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
