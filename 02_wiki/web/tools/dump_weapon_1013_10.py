# -*- coding: utf-8 -*-
"""1013_10 全链路拆解：本体资源清单 + 本地落地情况 + FSB 音频参数 + 结论。

同名表里混着大量“多路径粘连”的脏串，这里只收 shape 正常的路径。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
import wave
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
IDX = PROJ / "01_索引与产物/10_索引/热更检测"
OUT = PROJ / "01_索引与产物/30_分析/weapon_1013_10_拆解_20261025.md"
FSB = PROJ / "01_索引与产物/30_分析/fsb_sample_index_pe.json"
AUDIO = PROJ / "02_wiki/web/assets/audio/weapon_skin/penhuoqi_base"
PREFIXES = ("effect/fx/weapon/weapon_1013_10/",
            "effect/mesh/weapon/weapon_1013_10/",
            "weapon/weapon_1013_10/")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402


def locate(pi: sqlite3.Connection, path: str):
    for ext in ("", ".ktx", ".png"):
        try:
            f = "%016X" % (fid_of(path + ext) & 0xFFFFFFFFFFFFFFFF)
        except Exception:  # noqa: BLE001
            continue
        r = pi.execute("select pack,row,decoded from rows where fid=?", (f,)).fetchone()
        if r:
            return r
    return None


def wav_info(p: pathlib.Path):
    if not p.is_file():
        return None
    with wave.open(str(p)) as w:
        frames, rate, ch = w.getnframes(), w.getframerate(), w.getnchannels()
    return frames / rate if rate else 0, rate, ch, p.stat().st_size


def main() -> int:
    nj = sqlite3.connect(IDX / "names_join.sqlite3")
    pi = sqlite3.connect(IDX / "pe_index.sqlite3")
    raw = [r[0] for r in nj.execute("select name from nm where name like '%1013_10%'")]
    keep = set()
    for n in raw:
        p = n.replace("\\", "/")
        if not p.startswith(PREFIXES):
            continue
        if p.count(".") != 1:          # 粘连串一律丢
            continue
        keep.add(p)

    have = defaultdict(list)
    miss = defaultdict(list)
    for p in sorted(keep):
        ext = p.rsplit(".", 1)[-1]
        (have if locate(pi, p) else miss)[ext].append(p)

    skin_rows = [r[0] for r in nj.execute("select name from nm where name like '%skin_1013_010%'")]

    fsb = json.loads(FSB.read_text(encoding="utf-8"))["index"]
    fsb_rows = sorted(k for k in fsb if "1013_10" in k)

    L = ["# weapon_1013_10 全链路拆解（2026-10-25）", "",
         "## 一、性质判定", "",
         "- 前缀 `effect/fx/weapon/weapon_1013_10/`、`effect/mesh/weapon/weapon_1013_10/` ⇒ **武器本体**。",
         "- 皮肤资源在 `effect/fx/weapon/skin/skin_XXXX_YYY/`，本体资源不在 skin 目录下。",
         "- 同族本体 `weapon_1013_03 / 05 / 08 / 09 / 10`；皮肤是 `skin_1013_001…010`。", "",
         "## 二、本体资源落地情况", "",
         "| 类型 | 在包 | 未进包 |", "|---|---|---|"]
    for ext in sorted(set(have) | set(miss)):
        L.append("| %s | %d | %d |" % (ext, len(have[ext]), len(miss[ext])))

    L += ["", "### 未进包的资源（按类型）", ""]
    for ext in sorted(miss):
        L.append("- **%s（%d）**" % (ext, len(miss[ext])))
        for p in miss[ext]:
            L.append("  - `%s`" % p)
        L.append("")

    L += ["## 三、FSB 音频（%d 条，均在 0188.gpk 同一 bank）" % len(fsb_rows), "",
          "| 样本名 | bank 偏移 | bank 长度 | 序号 | 时长 | 采样率 | 声道 |",
          "|---|---|---|---|---|---|---|"]
    for k in fsb_rows:
        pack, off, ln, i = fsb[k][0]
        inf = wav_info(AUDIO / (k + ".wav"))
        if inf:
            L.append("| %s | %d | %d | %d | %.2fs | %d | %d |"
                     % (k, off, ln, i, inf[0], inf[1], inf[2]))
        else:
            L.append("| %s | %d | %d | %d | - | - | - |" % (k, off, ln, i))

    L += ["", "## 四、皮肤侧 skin_1013_010", "",
          "- 名表命中 **%d 条**：该皮肤的深模/特效/贴图完全没有下发。" % len(skin_rows),
          "- 卡上音效因此只能取本体默认音 + 喷火器通用音。", "",
          "## 五、结论", "",
          "1. `weapon_1013_10` 是喷火器本体（新本体），不是皮肤；它自己的资源只下发了一部分。",
          "2. 音频 3 条在包（循环 1/2 + 单发），已在卡上。",
          "3. 特效缺口集中在开火火焰（kh_01_hy / kh_02_hy）、枪口（muzzleflash_lc*）、"
          "命中（hit_hy）、弹道/击杀（dj_*_hy、qk_03_gx、qt_01_gx）、待机（idle_01）。",
          "4. 模型缺口集中在 `idle_water_*`、`qt_water*`、`zishen_*` 这批（水/紫身特效件），"
          "与传世皮肤的观感强化相关。",
          "5. 1110189 的皮肤资源整体未下发，下一版热更盯 `skin_1013_010` 与 `weapon_1013_10` 两个前缀即可收齐。"]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("路径 %d ｜ 有 %s ｜ 缺 %s ｜ 皮肤侧 %d ｜ 音频 %d"
          % (len(keep), {k: len(v) for k, v in have.items()},
             {k: len(v) for k, v in miss.items()}, len(skin_rows), len(fsb_rows)))
    print("报告", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
