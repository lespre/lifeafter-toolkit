# -*- coding: utf-8 -*-
"""gres 包 → FSB5 bank → WAV（终版：先按条目解包，再在解出文件里开凿）。

为什么这样：包里裸搜 FSB5 拿到的明文多半不是 bank 起点（实测 0058 有 13 处
但窗口解析全失败）；而 extract_gpk 解出的条目里，bank 可能是 *.fsb，也可能
藏在 *.bin 里面。所以两步走：extract_gpk → 对每个解出文件找 FSB5 → 窗口解析 → WAV。

用法：python tools/carve_fsb5_banks.py --only 0057,0058
产物：03拆包产物/skin_audio_carved/<pack>/{*.fsb, WAV/*.wav, _banks.json}
"""
from __future__ import annotations
import argparse, gc, json, shutil, sys, tempfile, time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")))
import lifeafter_unpacker_full as m  # noqa: E402
import fsb5  # noqa: E402

DEST = Path(r"E:\la拆包项目\03拆包产物\skin_audio_carved")
GRES = Path(r"E:\mrzh\Documents\gres")
MAGIC = b"FSB5"
WINDOWS = (1 << 20, 8 << 20, 32 << 20, 128 << 20)
KEYS = ("skin", "weapon", "wepon", "wuqi", "hexin", "gunshot", "ice_", "motor", "car_", "jg_", "butterfly")


def harvest(blob: bytes, pd: Path, rec: dict, src: str) -> None:
    pos = 0
    while True:
        off = blob.find(MAGIC, pos)
        if off < 0:
            return
        pos = off + 4
        fsb = None
        used = 0
        for w in WINDOWS:
            try:
                fsb = fsb5.FSB5(blob[off:off + w])
                used = w
                break
            except Exception:
                continue
        if fsb is None:
            continue
        try:
            names = [s.name for s in fsb.samples]
        except Exception:
            names = []
        if not names:
            continue
        fn = pd / f"{src}_{off:010d}.fsb"
        if not fn.exists():
            fn.write_bytes(blob[off:off + min(used, len(blob) - off)])
            try:
                m.extract_fsb(str(fn), str(pd / "WAV"))
            except Exception as e:
                rec.setdefault("wav_errors", []).append(f"{fn.name}: {type(e).__name__}")
        rec["banks"].append({"source": src, "offset": off, "file": fn.name,
                             "samples": len(names), "names": names[:200]})
        del fsb
        gc.collect()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--packs", type=int, default=0)
    a = ap.parse_args()
    packs = sorted(GRES.glob("*.gpk"))
    if a.only:
        want = {x.strip() for x in a.only.split(",") if x.strip()}
        packs = [p for p in packs if p.stem in want]
    if a.packs:
        packs = packs[: a.packs]
    DEST.mkdir(parents=True, exist_ok=True)
    out = {"schema": "carved-banks-v2",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "packs": []}
    for pk in packs:
        pd = DEST / pk.stem
        pd.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        rec = {"pack": pk.name, "banks": []}
        tmp = Path(tempfile.mkdtemp(prefix=f"gpk_{pk.stem}_"))
        try:
            m.extract_gpk(str(pk), str(tmp))
            for f in sorted(tmp.rglob("*")):
                if f.is_file():
                    try:
                        harvest(f.read_bytes(), pd, rec, f.name)
                    except Exception:
                        pass
        except Exception as e:
            rec["error"] = f"{type(e).__name__}: {e}"
        shutil.rmtree(tmp, ignore_errors=True)
        rec["seconds"] = round(time.time() - t0, 1)
        (pd / "_banks.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
        out["packs"].append(rec)
        rel = [n for b in rec["banks"] for n in b["names"] if any(k in n.lower() for k in KEYS)]
        print(f"  {pk.name}: bank {len(rec['banks'])} / 样本 {sum(b['samples'] for b in rec['banks'])}"
              f" / 相关样本名 {len(rel)} / {rec['seconds']}s", flush=True)
        if rel:
            print("     例:", rel[:12], flush=True)
    (DEST / "_all.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print("总 bank:", sum(len(p["banks"]) for p in out["packs"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
