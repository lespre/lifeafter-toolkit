# -*- coding: utf-8 -*-
"""THFB 工具 — 三合一（extract / merge / verify-weapon）

用法：
  python thfb_toolkit.py extract            # 全量提取 THX hash（27.3 万条）
  python thfb_toolkit.py merge              # 与历史 CSV 交叉映射（hash ↔ IDX）
  python thfb_toolkit.py verify-weapon      # weapon SKPW → 1DPW → DDS 复验
"""
from __future__ import annotations
import csv,hashlib,importlib.util,json,struct,sys,zlib
from pathlib import Path
import zstandard as zstd


def _tool_produce_root():
    """工具产出根：<项目根>/03_执行/90_临时/工具产出。

    ★ 产出不写工具区（工具库/output 曾被当作「乱」的来源之一）。
    ★ 仍然向上搜索项目根，不手算 parents[N]。
    """
    import pathlib
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "03_执行").is_dir() and (up / "00_治理").is_dir():
            return up / "03_执行" / "90_临时" / "工具产出"
    return pathlib.Path(__file__).resolve().parent / "output"   # 退路：找不到就还写旁边
def _toolkit_root():
    """向上搜索【工具库】那一层（判据：含 00_共享核心/toolkit_core/paths.py）。

    ★ 不用 parents[N] / parent.parent：迁移让文件深了一层，旧写法会集体指错。
    ★ 内部自己 import pathlib，不依赖模块级是否导入了 Path ——
      有的文件是 `from pathlib import Path as _P`，模块级根本没有 Path。
    """
    import pathlib
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_共享核心" / "toolkit_core" / "paths.py").is_file():
            return up
    raise RuntimeError("找不到工具库根：向上没有含 00_共享核心/toolkit_core/paths.py 的目录")
ROOT = _toolkit_root()
OUT = _tool_produce_root() / "09_thfb"
THD = Path(r"E:/mrzh/Documents/thd")
MULTI = Path(r"E:/mrzh/Documents/multi_cloud1")
CSV_PATH = Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/物理实体链路_001/THX与IDX原始Hash交叉引用.csv")
MAGIC = b"\x28\xb5\x2f\xfd"

def murmur3_x86_32(data: bytes, seed: int) -> int:
    c1, c2 = 0xCC9E2D51, 0x1B873593
    h = seed & 0xFFFFFFFF
    end = len(data) & ~3
    for off in range(0, end, 4):
        k = int.from_bytes(data[off:off + 4], "little")
        k = (k * c1) & 0xFFFFFFFF; k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF; k = (k * c2) & 0xFFFFFFFF
        h ^= k; h = ((h << 13) | (h >> 19)) & 0xFFFFFFFF; h = (h * 5 + 0xE6546B64) & 0xFFFFFFFF
    tail = data[end:]; k = 0
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if tail:
        k ^= tail[0]; k = (k * c1) & 0xFFFFFFFF; k = ((k << 15) | (k >> 17)) & 0xFFFFFFFF; k = (k * c2) & 0xFFFFFFFF
        h ^= k
    h ^= len(data); h ^= h >> 16; h = (h * 0x85EBCA6B) & 0xFFFFFFFF
    h ^= h >> 13; h = (h * 0xC2B2AE35) & 0xFFFFFFFF; h ^= h >> 16
    return h & 0xFFFFFFFF

def path_id(p: str) -> int:
    """路径 → 64 位 fid。委托给唯一实现 toolkit_core.path_fid（见该模块的说明）。"""
    import importlib.util
    from pathlib import Path as _P
    q = _toolkit_root() / "00_共享核心" / "toolkit_core" / "path_fid.py"
    s = importlib.util.spec_from_file_location("_path_fid_for_thfb", q)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m.fid_of(p, encoding="utf-8", normalize_sep=True)

def struct_unpack(data, off):
    a, b = struct.unpack_from("<II", data, off)
    return a, b

def extract_thx(data: bytes, csv_set: set):
    """24B 条目 [16B hash][u32][u32]；CSV 锚点对齐优先。"""
    n = len(data)
    def ok(off):
        if off + 24 > n: return False
        if len(set(data[off:off + 16])) < 12: return False
        a, b = struct_unpack(data, off + 16)
        return a < 0xF0000000 and b < 0xF0000000
    best = None; off = 0
    while off + 24 <= n:
        if not ok(off): off += 1; continue
        cnt = 0; o = off; hashes = []
        while ok(o):
            hashes.append(data[o:o + 16].hex()); cnt += 1; o += 24
        ov = sum(1 for h in hashes if h in csv_set)
        key = (ov, cnt)
        if best is None or key > best[0]:
            best = (key, off, hashes)
        off = o
    return best

def cmd_extract():
    csv_set = set()
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            h = row.get("resource_hash", "").strip()
            if len(h) == 32: csv_set.add(h)
    # ★ 不静默跳过：Path.rglob 对【不存在的目录】返回空而不报错，
    #   历史上因此少扫一整片 .thx，输出看起来却完全正常（又是「静默给少」）。
    files = []
    for _root in (THD, MULTI):
        if not _root.is_dir():
            print(f"  [thfb] 跳过不存在的目录（非错误，但会影响覆盖）：{_root}")
            continue
        _got = sorted(_root.rglob("*.thx"))
        print(f"  [thfb] {_root.name} → {len(_got)} 个 .thx")
        files += _got
    byname = {}
    for f in files: byname.setdefault(f.name, []).append(f)
    all_hash = set(); rows = []
    for name, plist in sorted(byname.items()):
        p = max(plist, key=lambda x: x.stat().st_size)
        r = extract_thx(p.read_bytes(), csv_set)
        if r:
            (ov, cnt), start, hashes = r
            all_hash.update(hashes)
            rows.append({"file": name, "size": p.stat().st_size, "entries": cnt, "entry_start": start})
        else:
            rows.append({"file": name, "size": p.stat().st_size, "entries": 0})
    (OUT / "thx_hashes_all.txt").write_text("\n".join(sorted(all_hash)), encoding="utf-8")
    (OUT / "thx_hash_full_extract.json").write_text(json.dumps({"files": rows, "unique_hashes": len(all_hash)}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"extract: {len(rows)} 文件, {sum(r['entries'] for r in rows)} 条, 唯一 {len(all_hash)} -> output/09_thfb/")

def cmd_merge():
    thx_all = set((OUT / "thx_hashes_all.txt").read_text().split())
    idx_cache = {}
    for p in Path(r"E:/mrzh/Documents/res").glob("*.idx"):
        idx_cache[p.name] = p.read_bytes()
    rows = []; matched = 0; in_idx = 0
    with CSV_PATH.open(encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            h = row.get("resource_hash", "").strip()
            if len(h) != 32: continue
            thx_hit = "yes" if h in thx_all else ""
            idx_hit = [n for n, d in idx_cache.items() if bytes.fromhex(h) in d]
            if thx_hit: matched += 1
            if idx_hit: in_idx += 1
            rows.append({"hash": h, "group": row.get("group", ""), "idx_index": row.get("idx_index", ""),
                         "payload_size": row.get("idx_payload_size", ""), "in_thx": thx_hit, "in_idx": ";".join(idx_hit)})
    (OUT / "thx_idx_mapping_final.csv").write_text(
        "hash,group,idx_index,payload_size,in_thx,in_idx\n" + "\n".join(
            f"{r['hash']},{r['group']},{r['idx_index']},{r['payload_size']},{r['in_thx']},{r['in_idx']}" for r in rows), encoding="utf-8")
    print(f"merge: {len(rows)} 行, THX 命中 {matched}, IDX 命中 {in_idx}/{len(rows)} -> output/09_thfb/thx_idx_mapping_final.csv")

def cmd_verify_weapon():
    spec = importlib.util.spec_from_file_location("v1", ROOT  / "01_解码定位复原" / "容器格式" / "wpk_1dpw_verifier.py")
    M = importlib.util.module_from_spec(spec); spec.loader.exec_module(M)
    wpk = Path(r"E:/mrzh/Documents/res/weapon3.wpk").read_bytes()
    off = 6774784; size = 24164
    payload = wpk[off + 0x30: off + 0x30 + size]
    s1, _ = getattr(M, "decode_wpd1_stage1")(payload, apply_header_transform=True)
    assert s1[:4] == b"DTSZ", "stage1 非 DTSZ"
    final, _ = getattr(M, "strict_dtsz_decompress")(s1)
    ok = final[:4] == b"DDS "
    sha = hashlib.sha256(final).hexdigest()[:16]
    (OUT / "weapon0_final.dds").write_bytes(final)
    print(f"verify-weapon: DTSZ->DDS {len(final)}B sha {sha} {'OK' if ok else 'FAIL'} -> output/09_thfb/weapon0_final.dds")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "extract"
    {"extract": cmd_extract, "merge": cmd_merge, "verify-weapon": cmd_verify_weapon}.get(cmd, cmd_extract)()

if __name__ == "__main__":
    main()
