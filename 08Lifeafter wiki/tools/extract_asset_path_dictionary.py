# -*- coding: utf-8 -*-
"""从脚本包抽**全量资源路径字典**（路线 C：依赖图传播命名）。

背景（见 06_文件名还原/GPK文件名还原_最终结论与交接_20260830.md）：
  · GPK/WPK 条目**匿名**（c1/c2 = 内容指纹，不是路径哈希）⇒ 只能靠外部映射命名
  · NPK 条目**带 64 位 file_id = 双 Murmur3(路径, 0x77777777 高 / 0x66666666 低)**
    ⇒ 只要有一份「逻辑路径」字典，就能用 npk_reader.path_id() 反查条目
  · 本工具产出的字典就是那份「逻辑路径」来源：脚本包里的 UI/逻辑代码会把
    它引用的资源路径当普通字符串带在里面（前例：PanelWeaponSkinCollection
    等 1,331 个面板名 + 370 条 ui/ 图片路径就是这么捞出来的）

产出：data/asset_path_dictionary.jsonl（每行一条路径 + 出现的 entry 序号）
      data/asset_path_dictionary.summary.json

用法：python tools/extract_asset_path_dictionary.py [--limit N]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKCOPY = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_508BB5BD")
OUT = ROOT / "data" / "asset_path_dictionary.jsonl"
SUMMARY = ROOT / "data" / "asset_path_dictionary.summary.json"
PATH_RE = re.compile(rb"(?:[A-Za-z0-9_][A-Za-z0-9_/\\.-]{2,180})\.(?:png|dds|tga|jpg|gim|mat|mesh|fx|sfx|prefab|anim|bnk|wem|ogg|mp3|wav|fbx|atlas)", re.I)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()
    idx = WORKCOPY / "_entry_index.json"
    files = sorted(WORKCOPY.glob("*.bin")) + sorted(WORKCOPY.glob("*.dat"))
    if not files:
        print("工作副本里没有条目文件；看:", WORKCOPY.exists(), flush=True)
        files = sorted(p for p in WORKCOPY.rglob("*") if p.is_file())[: a.limit or None]
    print(f"扫描 {len(files)} 个条目文件于 {WORKCOPY}", flush=True)
    seen: dict[str, dict] = {}
    ext = Counter()
    n = 0
    with OUT.open("w", encoding="utf-8") as fh:
        for p in files[: a.limit or None]:
            try:
                data = p.read_bytes()
            except Exception:
                continue
            n += 1
            if n % 4000 == 0:
                print(f"  ...{n}/{len(files)} 累计路径 {len(seen)}", flush=True)
            for m in PATH_RE.finditer(data):
                raw = m.group(0).decode("utf-8", "ignore").replace("\\", "/")
                # 字符串无分隔拼接会产生跨边界长串，按常见根目录切分
                for root in ("res/", "weapon/", "ui/", "character/", "effect/", "model/", "scene/", "building/", "utility/", "sound/", "audio/", "common/"):
                    k = raw.find(root)
                    if k > 0:
                        raw = raw[k:]
                if len(raw) > 200 or len(raw) < 8:
                    continue
                e = raw.rsplit(".", 1)[-1].lower()
                if raw not in seen:
                    seen[raw] = {"path": raw, "ext": e, "entries": [p.stem]}
                    ext[e] += 1
                elif len(seen[raw]["entries"]) < 6:
                    seen[raw]["entries"].append(p.stem)
                fh.write(json.dumps(seen[raw], ensure_ascii=False) + "\n")
    doc = {"schema": "asset-path-dictionary-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "workcopy": str(WORKCOPY), "entries_scanned": n, "unique_paths": len(seen),
           "by_ext": dict(ext.most_common(30)),
           "skin_paths": sum(1 for k in seen if "skin" in k.lower()),
           "ui_paths": sum(1 for k in seen if k.lower().startswith("ui/")),
           "audio_paths": sum(1 for k, v in seen.items() if v["ext"] in ("wem", "bnk", "ogg", "mp3", "wav"))}
    SUMMARY.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(doc, ensure_ascii=False))
    print("→", OUT.relative_to(ROOT), "|", SUMMARY.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
