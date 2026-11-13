# -*- coding: utf-8 -*-
"""称号动态 WebP 播放节奏归一（展示层补偿，**不是**游戏内时间轴还原）。

## 为什么需要这一步
从 PE csb 只能导出逐帧贴图序列；csb 的 ActionTimeline 时间轴（Duration / fps）
没有随冻结产物导出，项目里也没有对应 flatbuffers schema 解析器。
既有导出脚本一律写 `duration=40`（注释原文「源 csb 没写时长，按 25fps 估」）
—— 这是**估值**，不是游戏内实测。帧数少的动画因此一轮只有 80~480ms，
1 秒循环 2~12 次，观感就是「闪动过快」。

## 口径（唯一来源 = 本文件，可复算）
同批正常动画整轮时长实测 1200ms / 1600ms（各 4 个 csb），取 **1200~2400ms 为整轮区间**：
  · 区间内的动画一律不动（保留原导出节奏，最小改动）；
  · 整轮 < 1200ms 的（帧数少，1 秒闪好几次），每帧改为
    `max(40, ceil(1200 / 帧数))`；
  · 整轮 > 2400ms 的（csb 原始帧数多、被降采样拉长，6 秒一轮近乎静止），
    每帧改为 `max(40, round(2400 / 帧数))` —— 2026-11-07 补充，解决「有些动态的怎么不动」。
★ 只做展示层节奏归一，不声称等于游戏内帧率。日后若拿到游戏内录屏或
  csb ActionTimeline 的 Duration / fps，改 `TARGET_CYCLE_MS` / `MAX_CYCLE_MS` /
  `ANIM_FRAME_MS` 三个常量重跑即可全量重算。

## 实现
直接改 WebP ANMF chunk 的 24bit duration 字段，**不重编码画面**：
字节级可复现、无画质损失、幂等（第二次跑 0 改动）。默认 dry-run，`--apply` 才写盘。

用法：
  python title_anim_pace.py             # dry-run，列出将改的文件
  python title_anim_pace.py --apply     # 写盘
  python title_anim_pace.py --verify    # 校验全部动画整轮落在 1200~2400ms 区间
"""
from __future__ import annotations

import math
import pathlib
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

ASSET_DIRS = (WEB / "assets/title_dyn/seq",   # 2026-11-07 起的标准产物（精确帧序列）
             WEB / "assets/title_dyn/anim",  # 旧 csb 导出器产物（仍被少数条目回退引用）
             WEB / "assets/title_dyn/pe")    # 旧按家族拼帧目录（2026-11-07 已停用并清空）
ANIM_FRAME_MS = 40        # 原导出脚本的估值（25fps），保留为每帧下限
TARGET_CYCLE_MS = 1200    # 同批正常动画整轮时长实测下限
MAX_CYCLE_MS = 2400       # 整轮上限：超过就慢到近乎静止（展示层补偿，非局内实测）


def frame_duration(n_frames: int, base_ms: int = ANIM_FRAME_MS) -> int:
    """构建脚本共用的每帧时长：整轮落在 TARGET_CYCLE_MS~MAX_CYCLE_MS 区间。

    base_ms 可能是 csb 原始帧数折算出的较大值（会生成 5~6 秒一轮、近乎静止的动画），
    因此这里同时做上限裁剪 —— 与 retime() 的口径完全一致，将来重建不会再退回去。
    """
    n = max(1, int(n_frames))
    lo = math.ceil(TARGET_CYCLE_MS / n)
    hi = max(int(ANIM_FRAME_MS), round(MAX_CYCLE_MS / n))
    return min(max(int(base_ms), lo), hi)


def _anmf_duration_offsets(data: bytes) -> list[int]:
    """定位每个 ANMF chunk 的 duration 字段偏移（RIFF chunk 按 2 字节对齐）。

    ANMF payload: x(3) y(3) w(3) h(3) duration(3) flags(1) ... ⇒ duration 在 +12。
    """
    i, out = 12, []
    while i + 8 <= len(data):
        cid = data[i:i + 4]
        size = struct.unpack_from("<I", data, i + 4)[0]
        body = i + 8
        if cid == b"ANMF" and size >= 16 and body + 15 <= len(data):
            out.append(body + 12)
        i = body + size + (size & 1)
    return out


def read_durations(path: pathlib.Path) -> list[int]:
    data = path.read_bytes()
    return [int.from_bytes(data[o:o + 3], "little")
            for o in _anmf_duration_offsets(data)]


def retime(path: pathlib.Path, apply: bool) -> tuple[str, int, int, int]:
    """返回 (状态, 帧数, 原整轮ms, 新整轮ms)。"""
    data = bytearray(path.read_bytes())
    offs = _anmf_duration_offsets(bytes(data))
    if not offs:
        return "非动画/无ANMF", 0, 0, 0
    old = [int.from_bytes(data[o:o + 3], "little") for o in offs]
    total = sum(old)
    if TARGET_CYCLE_MS <= total <= MAX_CYCLE_MS:
        return "已达标", len(offs), total, total
    if total < TARGET_CYCLE_MS:
        new = frame_duration(len(offs))
    else:
        new = max(int(ANIM_FRAME_MS), round(MAX_CYCLE_MS / len(offs)))
    if apply:
        for o in offs:
            data[o:o + 3] = new.to_bytes(3, "little")
        path.write_bytes(bytes(data))   # 文件长度不变，只改 duration 字段
    return "已归一" if apply else "待归一", len(offs), total, new * len(offs)


def main() -> int:
    apply = "--apply" in sys.argv
    verify = "--verify" in sys.argv
    files = sorted(p for d in ASSET_DIRS if d.exists() for p in d.glob("*.webp"))
    pending = changed = bad = 0
    for p in files:
        status, n, old_ms, new_ms = retime(p, apply and not verify)
        if status in ("待归一", "已归一"):
            pending += 1
            print(f"  {p.name:46s} {n:3d}帧 {old_ms:5d}ms → {new_ms:5d}ms  {status}")
        if status == "非动画/无ANMF":
            bad += 1
        if status == "已归一":
            changed += 1
    if verify:
        left = [p.name for p in files
                if not (TARGET_CYCLE_MS <= sum(read_durations(p)) <= MAX_CYCLE_MS)]
        print(f"校验：{len(files)} 个动画，仍有 {len(left)} 个整轮不在 "
              f"{TARGET_CYCLE_MS}~{MAX_CYCLE_MS}ms {left[:5]}")
        return 0 if not left else 1
    print(f"\n共 {len(files)} 个 WebP；需归一 {pending} 个，本次写盘 {changed} 个"
          f"（{'--apply' if apply else 'dry-run，未写盘'}）；无 ANMF {bad} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
