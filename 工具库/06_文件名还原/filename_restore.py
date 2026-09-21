# -*- coding: utf-8 -*-
"""文件名还原 — 三合一（dict / bindict / verify）

用法：
  python filename_restore.py dict              # 路径字典匹配（filename_restorer 逻辑）
  python filename_restore.py bindict           # 配置表提取资源路径 → path_id 匹配（170 条）
  python filename_restore.py verify            # 批量解包验证命中条目（PNG/DDS）
"""
from __future__ import annotations
import csv,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "output" / "filename_restore"
NPK_READER = ROOT / "01_核心解包器" / "npk_reader.py"
BIN_COPY_ROOTS = [
    Path(r"C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_001/命中原始载荷"),
    Path(r"C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_002/命中原始载荷"),
    ROOT / "05_BinDict解码器" / "attribute_data_PC静态副本_001" if (ROOT/"05_BinDict解码器").exists() else Path(""),
]
EXT_RE = re.compile(rb'[A-Za-z0-9_\-/\\\.]{4,}\.(?:png|jpg|jpeg|dds|fsb|mesh|atlas|json|mat|anim|tga|wav|ogg|mp3|mp4|sfx|prefab|txt|xml|bin)(?=[^a-z]|$)', re.I)

def _reader():
    spec = importlib.util.spec_from_file_location("npkr", NPK_READER)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m

def load_ids(pkg: Path):
    m = _reader()
    ids = {}
    with pkg.open("rb") as f:
        h = m.aes_ecb(f.read(32))
        _r, magic, ver, to, n = struct.unpack_from("<QIIII", h)
        f.seek(to); tab = m.aes_ecb(f.read(n * 48))
        for i in range(n):
            row = struct.unpack_from("<QIIIIIi", tab, i * 48)
            ids[row[0]] = (i, row)
    return ids

def cmd_dict(npk: str = "script.py3.npk"):
    """路径字典匹配（原 filename_restorer 核心）。"""
    pkg = Path(r"E:/mrzh/Documents") / npk
    m = _reader()
    ids = load_ids(pkg)
    dictp = ROOT / "output" / "path_dictionary.txt"
    if not dictp.exists():
        print("字典缺失:", dictp); return
    hits = []
    for line in dictp.read_text(encoding="utf-8", errors="ignore").splitlines():
        p = line.strip()
        if not p: continue
        fid = m.path_id(p)
        if fid in ids:
            hits.append({"path": p, "file_id": f"{fid:016X}", "entry": ids[fid][0]})
    (OUT / "dict_matches.json").write_text(json.dumps(hits, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"dict 命中 {len(hits)} 条 -> output/filename_restore/dict_matches.json")

def cmd_bindict():
    """配置表提取资源路径 → path_id 匹配（170 条）。"""
    m = _reader()
    paths = set()
    for root in BIN_COPY_ROOTS:
        if not root or not root.is_dir(): continue
        for p in root.rglob("*.bin"):
            if p.stat().st_size > 20 << 20: continue
            try: d = p.read_bytes()
            except: continue
            for mm in EXT_RE.finditer(d):
                paths.add(mm.group().decode("latin1"))
    variants = set()
    for s in paths:
        variants.add(s); variants.add(s.replace("/", "\\")); variants.add(s.replace("\\", "/"))
        for pre in ("ui/","ui\\","res/","res\\","common/","common\\","scene/","scene\\","effect/","effect\\",
                    "item_icon/","item_icon\\","font_icon/","font_icon\\","main_v4_icon/","main_v4_icon\\","capture_","2","201","MVP"):
            if s.startswith(pre):
                rest = s[len(pre):]
                variants.add(rest); variants.add(rest.replace("/", "\\")); variants.add(rest.replace("\\", "/"))
    ids = load_ids(Path(r"E:/mrzh/res/ui.npk"))
    matches = []
    for s in sorted(variants):
        fid = m.path_id(s)
        if fid in ids:
            matches.append({"path": s, "file_id": f"{fid:016X}", "entry": ids[fid][0]})
    (OUT / "bindict_matches.json").write_text(json.dumps(matches, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"bindict 命中 {len(matches)} 条 -> output/filename_restore/bindict_matches.json")

def cmd_verify():
    """批量解包验证命中条目。"""
    m = _reader()
    matches = json.loads((OUT / "bindict_matches.json").read_text(encoding="utf-8"))
    ids = load_ids(Path(r"E:/mrzh/res/ui.npk"))
    results = []
    with Path(r"E:/mrzh/res/ui.npk").open("rb") as f:
        for x in matches:
            ent = ids.get(int(x["file_id"], 16))
            if not ent: continue
            i, row = ent
            f.seek(row[1]); raw = m.unpack_entry(f.read(row[2]), row[3], row[6])
            typ = "png" if raw[:4] == b"\x89PNG" else "dds" if raw[:4] == b"DDS " else raw[:8].hex()
            results.append({"path": x["path"], "file_id": x["file_id"], "entry": i, "flag": row[6], "raw_bytes": len(raw), "type": typ})
    ok = sum(1 for r in results if r["type"] in ("png", "dds"))
    (OUT / "verified.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"verify: {ok}/{len(results)} 合法资源 -> output/filename_restore/verified.json")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "bindict"
    {"dict": cmd_dict, "bindict": cmd_bindict, "verify": cmd_verify}.get(cmd, cmd_bindict)()

if __name__ == "__main__":
    main()
