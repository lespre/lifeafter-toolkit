# -*- coding: utf-8 -*-
"""批量解密 WPK 纹理库（通用版）——支持任意 idx + 对应 wpk 前缀，DDS→PNG。

用法：
  python batch_wpk_textures.py <res_dir> <output_root> [idx1,idx2,...] [--png]

  例：python batch_wpk_textures.py E:\\mrzh\\Documents\\res E:\\wpk_out ui,model,weapon --png
  例：python batch_wpk_textures.py E:\\mrzh\\Documents\\res E:\\wpk_out ui --png 4  # 仅 pkg 4

产物：<output_root>/<idx名>/*.dds + _manifest.json（含 hash/payload_size/type）
依赖：同目录 wpk_1dpw_decryptor.py（decrypt_payload/parse_idx）
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from wpk_1dpw_decryptor import decrypt_payload, parse_idx  # noqa: E402


def decrypt_idx(res_dir: Path, idx_name: str, output_dir: Path, pkg_filter=None, max_count=0, to_png=False):
    idx_path = res_dir / f"{idx_name}.idx"
    if not idx_path.exists():
        print(f"[skip] {idx_name}.idx 不存在")
        return 0, 0
    entries = parse_idx(str(idx_path))
    if pkg_filter:
        entries = [e for e in entries if e["pkg"] in pkg_filter]
    if max_count > 0:
        entries = entries[:max_count]
    output_dir.mkdir(parents=True, exist_ok=True)
    success = failed = 0
    results = []
    for e in entries:
        wpk = res_dir / f"{idx_name}{e['pkg']}.wpk"
        if not wpk.exists():
            failed += 1
            continue
        try:
            with wpk.open("rb") as f:
                f.seek(e["offset"])
                raw = f.read(e["header_size"] + e["payload_size"])
            if len(raw) != e["header_size"] + e["payload_size"] or raw[:4] != b"1DPW":
                failed += 1
                continue
            payload = raw[e["header_size"]:e["header_size"] + e["payload_size"]]
            final, meta = decrypt_payload(payload)
            ext = meta["type"]
            out_name = f"{e['index']:05d}_{e['hash'][:16]}.{ext}"
            out_path = output_dir / out_name
            out_path.write_bytes(final)
            if to_png and ext == "dds":
                try:
                    from PIL import Image
                    png_path = output_dir / (out_name[:-4] + ".png")
                    Image.open(out_path).convert("RGB").save(png_path)
                    meta["png"] = png_path.name
                except Exception:
                    pass
            meta["entry"] = e
            results.append(meta)
            success += 1
        except Exception:
            failed += 1
    (output_dir / "_manifest.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    print(f"[{idx_name}] 成功 {success} 失败 {failed} -> {output_dir}")
    return success, failed


def main() -> None:
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    res_dir = Path(sys.argv[1])
    out_root = Path(sys.argv[2])
    idx_names = sys.argv[3].split(",") if len(sys.argv) > 3 else ["ui"]
    to_png = "--png" in sys.argv
    pkg_filter = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 and not sys.argv[5].startswith("--") else None
    total_ok = total_fail = 0
    for name in idx_names:
        ok, fail = decrypt_idx(res_dir, name, out_root / name, pkg_filter=pkg_filter, to_png=to_png)
        total_ok += ok
        total_fail += fail
    print(f"\n总计：成功 {total_ok}，失败 {total_fail}")


if __name__ == "__main__":
    main()
