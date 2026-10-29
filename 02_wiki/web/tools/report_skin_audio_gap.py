# -*- coding: utf-8 -*-
"""生成武器皮肤音效缺口清单（真名/资源/音频三级状态）。"""
from __future__ import annotations
import sys

import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
TREE = ROOT / "01_索引与产物/41_还原树/pe/资源/effect/fx/weapon/skin"
OUT = ROOT / "01_索引与产物/30_分析/武器皮肤音效缺口_20261025.md"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    its = d["items"]
    rows = []
    for it in its:
        names = it.get("sfx_real_names") or []
        state = it.get("sfx_audio_state") or ""
        mp = str(it.get("model_path") or "")
        m = re.search(r"skin_(\d+_\d+)", mp)
        tag = "skin_" + m.group(1) if m else ""
        sfx_n = len(list((TREE / tag).glob("*.sfx"))) if tag and (TREE / tag).is_dir() else 0
        rows.append({
            "id": it["id"], "name": it.get("name") or "(未定名)",
            "grade": it.get("grade") or "", "names": len(names),
            "audio": "已提取" if state == "已提取" else "缺",
            "sfx_dir": tag, "sfx_files": sfx_n,
        })
    gap = [r for r in rows if r["audio"] == "缺"]
    lines = ["# 武器皮肤音效缺口（2026-10-25）", "",
             "总计 %d 卡 ｜ 已提取 %d ｜ 缺口 %d" % (len(rows), len(rows) - len(gap), len(gap)), "",
             "| id | 名称 | 品级 | 真名数 | sfx 目录 | sfx 文件 | 缺口原因 |",
             "|---|---|---|---|---|---|---|"]
    for r in gap:
        if r["sfx_files"] == 0:
            why = "效果资源未进本地包"
        else:
            why = "有视觉效果文件但无音效节点，音频走事件池"
        lines.append("| %s | %s | %s | %d | %s | %d | %s |"
                     % (r["id"], r["name"], r["grade"], r["names"], r["sfx_dir"] or "-",
                        r["sfx_files"], why))
    lines += ["", "## 口径", "",
              "- 真名来自音效查询表内联键值对（绑定该皮 SFX 配置行），内部名原样保留。",
              "- 有真名 ≠ 有音频；两者分开统计。",
              "- 视觉效果 `.sfx` 内不含音效节点（实测 0 命中），音频须沿事件池 → FEV → FSB 闭链。",
              "- 本机只有 173 个 PE gpk，缺 168 块；缺失资源的卡标注为未进包，不做替代。"]
    OUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("缺口 %d 卡，清单写出 %s" % (len(gap), OUT))
    for r in gap[:5]:
        print(" ", r["id"], r["name"], r["grade"], "真名", r["names"], "sfx", r["sfx_files"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
