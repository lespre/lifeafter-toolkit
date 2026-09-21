# -*- coding: utf-8 -*-
"""在**解压后**的条目数据里搜目标皮肤（而不是容器原始字节）。

教训：gres/*.gpk、res.gpk 这些容器里的条目是压缩/加密的，直接在文件原始字节里
搜 "skin_1003_010" 一律 0 命中（我前面就栽在这）。正确做法：先按条目解包，
再在解出的字节里搜。

用法：
  python tools/search_decompressed.py --gpk "E:\mrzh\res.gpk" --pat skin_1003_010 --pat guangying
  python tools/search_decompressed.py --npk "E:\mrzh\res.npk" --pat skin_1003_010
产物：analysis/audit/decompressed_search.json
"""
from __future__ import annotations

import argparse
import json
import shutil
import struct
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")))
import lifeafter_unpacker_full as m  # noqa: E402

OUT = ROOT / "analysis" / "audit" / "decompressed_search.json"


def scan_blob(blob: bytes, pats: list[bytes], where: str, hits: list) -> None:
    for p in pats:
        pos = 0
        while True:
            j = blob.find(p, pos)
            if j < 0:
                break
            pos = j + 1
            ctx = blob[max(0, j - 120):j + 160]
            txt = "".join(chr(c) if 32 <= c < 127 else "." for c in ctx)
            hits.append({"where": where, "pat": p.decode("latin1"), "offset": j, "context": txt})
            if len(hits) > 500:
                return


def scan_dir(d: Path, pats: list[bytes], hits: list) -> int:
    n = 0
    for f in d.rglob("*"):
        if not f.is_file():
            continue
        n += 1
        try:
            scan_blob(f.read_bytes(), pats, str(f.name), hits)
        except Exception:
            pass
    return n


def npk_entries(path: Path):
    """NPK：头 64B AES-ECB，off=u32@16，n=u32@20，条目表 n*48 整体解密，首字段 u64 FID。"""
    from Crypto.Cipher import AES
    cipher = AES.new(m.AES_KEY, AES.MODE_ECB)
    with path.open("rb") as f:
        head = cipher.decrypt(f.read(64))
        off = struct.unpack_from("<I", head, 16)[0]
        n = struct.unpack_from("<I", head, 20)[0]
        f.seek(off)
        tab = cipher.decrypt(f.read(n * 48))
    out = []
    for i in range(n):
        b = tab[i * 48:(i + 1) * 48]
        out.append(b)
    return out, cipher


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gpk", default="")
    ap.add_argument("--npk", default="")
    ap.add_argument("--pat", action="append", default=[])
    a = ap.parse_args()
    pats = [p.encode() for p in (a.pat or ["skin_1003_010"])]
    doc = {"schema": "decompressed-search-v1",
           "generated": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
           "pats": [p.decode() for p in pats], "hits": [], "notes": []}
    if a.gpk:
        pk = Path(a.gpk)
        tmp = Path(tempfile.mkdtemp(prefix="gpk_search_"))
        t0 = time.time()
        try:
            m.extract_gpk(str(pk), str(tmp))
            n = scan_dir(tmp, pats, doc["hits"])
            doc["notes"].append(f"{pk.name}: 解包 {n} 个文件，用时 {time.time()-t0:.0f}s")
        except Exception as e:  # noqa: BLE001
            doc["notes"].append(f"{pk.name}: 解包失败 {type(e).__name__}: {e}")
        shutil.rmtree(tmp, ignore_errors=True)
    if a.npk:
        pk = Path(a.npk)
        try:
            ents, cipher = npk_entries(pk)
            doc["notes"].append(f"{pk.name}: 条目表 {len(ents)} 条")
            with pk.open("rb") as fh:
                data = fh.read()
            ok = 0
            for i, b in enumerate(ents):
                fid = struct.unpack_from("<Q", b, 0)[0]
                # 试常见布局：FID(8) + off(4) + cmp(4) + dec(4) + flag(4)
                for base in (8,):
                    try:
                        o, cmp_, dec, fl = struct.unpack_from("<IIII", b, base)
                    except Exception:
                        continue
                    if not (0 < o < len(data)) or cmp_ <= 0 or cmp_ > 64 << 20 or dec_ok(dec) is False:
                        continue
                    raw = data[o:o + cmp_]
                    try:
                        out = m.unpack_entry(raw, dec, fl)
                    except Exception:
                        continue
                    if out:
                        ok += 1
                        scan_blob(out, pats, f"npk-entry-{i}", doc["hits"])
                    break
            doc["notes"].append(f"{pk.name}: 成功解出 {ok} 条")
        except Exception as e:  # noqa: BLE001
            doc["notes"].append(f"{pk.name}: 失败 {type(e).__name__}: {e}")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"hits": len(doc["hits"]), "notes": doc["notes"]}, ensure_ascii=False)[:1500])
    for h in doc["hits"][:12]:
        print("  ", h["where"], h["pat"], h["context"][:160])
    print("→", OUT.relative_to(ROOT))
    return 0


def dec_ok(dec: int) -> bool:
    return 0 < dec < 512 << 20


if __name__ == "__main__":
    raise SystemExit(main())
