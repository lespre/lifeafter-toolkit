# -*- coding: utf-8 -*-
"""NPK 切分器 v1：32B 头 + 连续完整 PNG 序列。

对 UI 类 npk：从 offset 32 起顺序扫描 PNG 签名，逐 PNG 提取到
<stem>/<i:04d>.png，并记录每个 PNG 的字节边界与 SHA-256。
对非 PNG 开头包：只记录 payload 前 64B hex 供后续格式判定。

只读 E:\\mrzh；输出写本目录 extracted/。
用法: python npk_split_001.py <rel_path> [--max N]
"""
import argparse, hashlib, json, struct, sys
from pathlib import Path

SRC = Path(r"E:\mrzh\res")
OUT = Path(__file__).parent
PNG_SIG = b"\x89PNG\r\n\x1a\n"

def walk_pngs(data: bytes, start: int = 32):
    """Locate PNG signatures sequentially; each PNG ends at IEND.

    容错: chunk 损坏时用下一个 PNG 签名作硬边界。
    """
    n = len(data)
    sigs = []
    pos = start
    while True:
        p = data.find(PNG_SIG, pos)
        if p == -1:
            break
        sigs.append(p)
        pos = p + 8
    for i, s in enumerate(sigs):
        hard_end = sigs[i + 1] if i + 1 < len(sigs) else n
        p = s + 8
        end = None
        while p + 8 <= hard_end:
            ln = struct.unpack_from(">I", data, p)[0]
            ctype = data[p + 4:p + 8]
            if ln > hard_end - p:
                break
            p += 12 + ln
            if ctype == b"IEND":
                end = p
                break
        if end is None:
            # 无完整 IEND：退化为到下一签名（减去间隙）
            end = hard_end
            while end > s and data[end - 1] == 0:
                end -= 1
        yield s, end


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rel")
    ap.add_argument("--max", type=int, default=0)
    a = ap.parse_args()
    p = SRC / a.rel
    stem = p.stem
    outdir = OUT / "extracted" / (p.parent.name + "_" + stem)
    outdir.mkdir(parents=True, exist_ok=True)
    data = p.read_bytes()
    entries = []
    for i, (s, e) in enumerate(walk_pngs(data)):
        if a.max and i >= a.max:
            break
        chunk = data[s:e]
        w, h, bd, ct = struct.unpack_from(">IIBB", chunk, 16)
        sha = hashlib.sha256(chunk).hexdigest()
        out = outdir / f"{i:04d}.png"
        out.write_bytes(chunk)
        entries.append({"idx": i, "start": s, "end": e, "bytes": e - s,
                        "width": w, "height": h, "bitdepth": bd, "colortype": ct,
                        "sha256": sha, "out": str(out)})
    # 非PNG开头的信息
    payload_sig = data[32:48].hex()
    manifest = {
        "source": str(p), "source_bytes": len(data),
        "source_sha256": hashlib.sha256(data).hexdigest(),
        "header_32_hex": data[:32].hex(),
        "payload_head_hex": payload_sig,
        "png_count": len(entries),
        "entries": entries,
    }
    (outdir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in manifest.items() if k != "entries"}, ensure_ascii=False))
    for e in entries[:10]:
        print(f'  {e["idx"]:04d} {e["width"]}x{e["height"]} bd={e["bitdepth"]} ct={e["colortype"]} {e["bytes"]:,}B sha={e["sha256"][:16]}')
    if len(entries) > 10:
        print(f'  ... total {len(entries)}')

if __name__ == "__main__":
    main()
