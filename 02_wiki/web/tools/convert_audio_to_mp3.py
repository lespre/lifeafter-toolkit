# -*- coding: utf-8 -*-
"""把 FSB5 音频库里的样本批量转成浏览器可播的 mp3。

前置（都已存在，脚本只读）：
  01_索引与产物/30_分析/sound_pack_sample_index.json      # 样本名 → [[bank_entry, sample_index], …]
  01_索引与产物/41_还原树/pe/资源/res/sound.gpk/_未命名/  # 已还原的 FSB5 bank（<entry:08d>.fsb5）
  热更包 01_索引与产物/源包/pe_npk_20261029/res.sound.layers.1.1.npk（bank 缺失时兜底读取）

输出：
  01_索引与产物/20_提取/影音/audio/<category>/<sample>.mp3

用法：
  python convert_audio_to_mp3.py --only bgm,music,amb,ui,cutscene
  python convert_audio_to_mp3.py --workers 6
  python convert_audio_to_mp3.py --max-samples 200          # 冒烟

口径：
  * 已存在的 mp3 一律跳过（可断点续跑）；--force 才覆盖。
  * 分类映射复用 build_media_catalog.audio_cat_of，保证目录与看板 category 一致。
  * 解码用 vgmstream-cli（`-s N` 选 subsong，1 基）；转码用 ffmpeg（libmp3lame VBR）。
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import pathlib
import shutil
import subprocess
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ARTIFACTS  # noqa: E402
from build_media_catalog import SOUND_INDEX, SOUND_BANK_DIR, MEDIA_AUDIO_DIR, audio_cat_of, safe_stem  # noqa: E402

VGMSTREAM = pathlib.Path(r"C:\Users\Administrator\AppData\Local\Temp\vgm\ex\vgmstream-cli.exe")
HOTFIX_NPK = ARTIFACTS / "源包" / "pe_npk_20261029" / "res.sound.layers.1.1.npk"
TMP_ROOT = ARTIFACTS / "90_临时" / "_audio_convert"

_G: dict = {}


def _init(only: set[str] | None, force: bool) -> None:
    TMP_ROOT.mkdir(parents=True, exist_ok=True)
    _G["idx"] = json.loads(SOUND_INDEX.read_text(encoding="utf-8"))
    banks: dict[int, list[tuple[int, str]]] = {}
    for name, locs in _G["idx"].items():
        for entry, sidx in locs:
            banks.setdefault(int(entry), []).append((int(sidx), name))
    _G["banks"] = banks
    _G["only"] = only
    _G["force"] = force
    _G["archive"] = None


def _get_archive():
    if _G["archive"] is None:
        sys.path.insert(0, str(ARTIFACTS.parent / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
        from la_unpack_core import NpkArchive
        _G["archive"] = NpkArchive(str(HOTFIX_NPK))
    return _G["archive"]


def _bank_path(entry: int) -> pathlib.Path:
    return SOUND_BANK_DIR / ("%08d.fsb5" % entry)


def _decode_all(bank_file: pathlib.Path, tmpdir: pathlib.Path, tag: str, n_samples: int) -> dict[int, pathlib.Path]:
    """一次调用把 bank 内所有 subsong 解成 wav，返回 {sample_index(0基): wav}。"""
    pattern = tmpdir / (tag + "_?s.wav")
    cmd = [str(VGMSTREAM), "-s", "1", "-S", "0", "-o", str(pattern), str(bank_file)]
    subprocess.run(cmd, capture_output=True)
    out: dict[int, pathlib.Path] = {}
    for i in range(n_samples):
        p = tmpdir / f"{tag}_{i + 1}.wav"
        if p.exists() and p.stat().st_size > 1000:
            out[i] = p
    return out


def _to_mp3(wav: pathlib.Path, mp3: pathlib.Path) -> bool:
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav),
           "-c:a", "libmp3lame", "-q:a", "5", str(mp3)]
    r = subprocess.run(cmd, capture_output=True)
    return r.returncode == 0 and mp3.exists() and mp3.stat().st_size > 1024


def _work(entry: int) -> dict:
    items = _G["banks"].get(entry, [])
    only = _G["only"]
    todo = [(s, n) for s, n in items if not only or audio_cat_of(n) in only]
    stat = {"bank": entry, "done": 0, "skip": 0, "fail": 0, "samples": len(todo)}
    if not todo:
        return stat

    # 目标已全部存在 → 直接跳过，不读 bank
    pending = []
    for sidx, name in todo:
        mp3 = MEDIA_AUDIO_DIR / audio_cat_of(name) / (safe_stem(name) + ".mp3")
        if mp3.exists() and mp3.stat().st_size > 1024 and not _G["force"]:
            stat["skip"] += 1
            continue
        pending.append((sidx, name, mp3))
    if not pending:
        return stat

    tmpdir = TMP_ROOT / ("%d_%d" % (os.getpid(), entry))
    tmpdir.mkdir(parents=True, exist_ok=True)
    # 以热更 NPK 为准：索引里的 bank_entry 就是 NPK 条目号。
    # （还原树 _未命名 下的 fsb5 编号与 NPK 条目号并不一致，不能拿来用。）
    try:
        data = _get_archive().read_entry(entry_index=entry)
    except Exception:
        stat["fail"] += len(pending)
        return stat
    # vgmstream 按扩展名判容器：FSB 必须用 .fsb，.fsb5 会打不开。
    bank_file = tmpdir / ("%08d.fsb" % entry)
    bank_file.write_bytes(data)

    n_samples = max(s for s, _ in _G["banks"][entry]) + 1
    wavs = _decode_all(bank_file, tmpdir, "b", n_samples)
    for sidx, name, mp3 in pending:
        wav = wavs.get(sidx)
        if wav is None:
            stat["fail"] += 1
            continue
        mp3.parent.mkdir(parents=True, exist_ok=True)
        if _to_mp3(wav, mp3):
            stat["done"] += 1
        else:
            stat["fail"] += 1
        try:
            wav.unlink()
        except OSError:
            pass
    shutil.rmtree(tmpdir, ignore_errors=True)
    return stat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="", help="只转这些分类（逗号分隔，如 bgm,music,amb）")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--max-samples", type=int, default=0, help="最多转多少条（按 bank 顺序估算，0=不限）")
    ap.add_argument("--force", action="store_true")
    args = ap.parse_args()

    global _G
    idx = json.loads(SOUND_INDEX.read_text(encoding="utf-8"))
    banks: dict[int, list[tuple[int, str]]] = {}
    for name, locs in idx.items():
        for entry, sidx in locs:
            banks.setdefault(int(entry), []).append((int(sidx), name))
    only = set(x.strip() for x in args.only.split(",") if x.strip()) or None

    # 提前算好待转条数，便于估算
    need = 0
    for entry, items in banks.items():
        for sidx, name in items:
            if only and audio_cat_of(name) not in only:
                continue
            mp3 = MEDIA_AUDIO_DIR / audio_cat_of(name) / (safe_stem(name) + ".mp3")
            if not (mp3.exists() and mp3.stat().st_size > 1024):
                need += 1
    print("待转码 %d 条 / %d 个 bank（分类=%s）" % (need, len(banks), ",".join(sorted(only)) if only else "全部"), flush=True)
    if args.max_samples and need > args.max_samples:
        need = args.max_samples
        print("按 --max-samples 限制为 %d 条" % need, flush=True)

    order = sorted(banks)
    t0 = time.time()
    done = fail = skip = 0
    with mp.Pool(args.workers, initializer=_init, initargs=(only, args.force)) as pool:
        # 用 imap 以便观察进度；只下发按分类过滤后仍有待办的 bank
        pending_entries = []
        for entry in order:
            items = banks[entry]
            if only and not any(audio_cat_of(n) in only for _s, n in items):
                continue
            pending_entries.append(entry)
        for k, st in enumerate(pool.imap_unordered(_work, pending_entries), 1):
            done += st["done"]; fail += st["fail"]; skip += st["skip"]
            if k % 20 == 0 or k == len(pending_entries):
                el = time.time() - t0
                print("  bank %d/%d · 新转 %d · 跳过 %d · 失败 %d · %.1fs"
                      % (k, len(pending_entries), done, skip, fail, el), flush=True)
            if args.max_samples and done >= args.max_samples:
                pool.terminate()
                break
    print("完成：新转 %d · 跳过 %d · 失败 %d · 用时 %.1fs" % (done, skip, fail, time.time() - t0))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
