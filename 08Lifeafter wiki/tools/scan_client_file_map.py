# -*- coding: utf-8 -*-
"""只读客户端文件地图采集器：枚举 mrzh / LifeAfter 全部文件（元数据 + 定向 SHA）。

- 原始文件只读，无任何写入客户端目录。
- 输出：data/audit/client_file_maps/<client>_file_inventory.jsonl
  （path_rel, dir_role, ext, size, mtime_ns, sha256|None, sha_scope）
- SHA 范围：容器/配置类（npk gpk wpk idx fpk pi pak ini conf cfg txt json xml log dat bin nxs）
  全量计算；其余（dds png tga gim mesh mp4 fsb 等媒体）只记元数据 sha_scope=skip-media。
- dir_role 按顶层目录角色：root/bin/Documents/res/launcher_conf/…
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path

SHA_EXTENSIONS = {
    ".npk", ".gpk", ".wpk", ".idx", ".fpk", ".pi", ".pak", ".ini", ".conf",
    ".cfg", ".txt", ".json", ".xml", ".log", ".dat", ".bin", ".nxs", ".yaml",
    ".csv", ".inf", ".ver", ".version",
}
# 明确跳过 SHA 的媒体大目录（避免数百 GB 哈希）
MEDIA_EXTENSIONS = {
    ".dds", ".png", ".tga", ".jpg", ".jpeg", ".gim", ".mesh", ".mtg",
    ".mp4", ".fsb", ".wav", ".ogg", ".atlas", ".sfx", ".spine", ".skel",
    ".prefab", ".unity", ".asset",
}


def dir_role(root: Path, rel: Path) -> str:
    parts = rel.parts
    if not parts:
        return "root"
    top = parts[0].lower()
    if top in ("bin", "res", "documents", "launcher_conf"):
        return top
    # res 内二级结构
    if len(parts) >= 2 and parts[0].lower() == "res":
        return "res/" + parts[1].lower()
    return "root"


def sha256_file(path: Path, chunk: int = 4 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            block = f.read(chunk)
            if not block:
                break
            h.update(block)
    return h.hexdigest()


def scan(client_root: Path, max_sha_bytes: int = 400 << 20) -> dict:
    out_lines = []
    counts = {"files": 0, "sha_full": 0, "sha_skipped_media": 0,
              "sha_skipped_large": 0, "errors": 0}
    started = time.time()
    for dirpath, dirnames, filenames in os.walk(client_root):
        # 跳过明显系统/隐藏目录（.git 等）
        dirnames[:] = [d for d in dirnames if not d.startswith((".", "$"))]
        dp = Path(dirpath)
        for fn in filenames:
            fp = dp / fn
            try:
                st = fp.stat()
            except OSError:
                counts["errors"] += 1
                continue
            rel = fp.relative_to(client_root)
            ext = fp.suffix.lower() if fp.suffix else ""
            role = dir_role(client_root, rel)
            size = st.st_size
            sha = None
            scope = "skip"
            if ext in SHA_EXTENSIONS and size <= max_sha_bytes:
                try:
                    sha = sha256_file(fp)
                    scope = "full"
                    counts["sha_full"] += 1
                except OSError:
                    scope = "error"
                    counts["errors"] += 1
            elif ext in SHA_EXTENSIONS and size > max_sha_bytes:
                scope = "large-skip"
                counts["sha_skipped_large"] += 1
            elif ext in MEDIA_EXTENSIONS:
                scope = "media-skip"
                counts["sha_skipped_media"] += 1
            rec = {
                "path": rel.as_posix(),
                "dir_role": role,
                "ext": ext,
                "size": size,
                "mtime_ns": st.st_mtime_ns,
                "sha256": sha,
                "sha_scope": scope,
            }
            out_lines.append(json.dumps(rec, ensure_ascii=False))
            counts["files"] += 1
            if counts["files"] % 20000 == 0:
                print(f"  ...{counts['files']} files, {time.time()-started:.0f}s",
                      flush=True)
    counts["seconds"] = round(time.time() - started, 1)
    return out_lines, counts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("client", choices=["mrzh", "lifeafter"])
    ap.add_argument("--max-sha-bytes", type=int, default=400 << 20)
    args = ap.parse_args()
    root = Path(r"E:\mrzh" if args.client == "mrzh" else r"E:\LifeAfter")
    out_dir = Path(r"E:\la拆包项目\08Lifeafter wiki\data\audit\client_file_maps")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.client}_file_inventory.jsonl"
    lines, counts = scan(root, args.max_sha_bytes)
    with out_path.open("w", encoding="utf-8", newline="\n") as f:
        for ln in lines:
            f.write(ln + "\n")
    summary = out_dir / f"{args.client}_inventory_summary.json"
    summary.write_text(json.dumps(counts, ensure_ascii=False, indent=1),
                       encoding="utf-8")
    print(f"{args.client}: {counts}")
    print(f"inventory -> {out_path} ({len(lines)} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
