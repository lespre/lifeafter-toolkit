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
OUT = _tool_produce_root() / "filename_restore"
NPK_READER = ROOT  / "01_解码定位复原" / "解包与扫描" / "npk_reader.py"
BIN_COPY_ROOTS = [
    Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_001/命中原始载荷"),
    Path(r"C:/Users/<user>/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服武器商品中文表扫描_002/命中原始载荷"),
    ROOT  / "01_解码定位复原" / "表解码" / "attribute_data_PC静态副本_001" if (ROOT / "01_解码定位复原" / "表解码").exists() else Path(""),
]
EXT_RE = re.compile(rb'[A-Za-z0-9_\-/\\\.]{4,}?\.(?:png|jpg|jpeg|dds|fsb|mesh|atlas|json|mat|anim|tga|wav|ogg|mp3|mp4|sfx|prefab|txt|xml|bin)', re.I)
# ↑ 修（2026-09-26）：原为 {4,}（贪婪）+ 后缀前瞻 (?=[^a-z]|$)，
#   但 .bin 里的资源路径是【无分隔符拼接】的。若某扩展名后紧接小写字母
#   （如 '...flying02.sfx' 紧跟 'effect/fx/...'），前瞻失败后正则继续向后吞，
#   把多段路径粘成一整坨 ⇒ path_id 算的是整坨哈希 ⇒ 命中恒为 0。
#   改为懒惰 {4,}? 并去掉前瞻：命中第一个「点+扩展名」即止，恢复成单条路径。

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



def _gpk_module():
    """复用已验证的 gpk_npk_index（索引里 58 个 gpk 就是它读的）。"""
    spec = importlib.util.spec_from_file_location(
        "_la_gpk_npk_index", ROOT  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def resolve_ui_packages():
    """定位 UI 包：优先 ui.npk（旧客户端）；否则取 res/ui_*.gpk（新客户端多包）。

    返回 (packages, note)。note 如实说明用的是哪一种，便于在报告里标注来源。
    """
    res = Path(r"E:/mrzh/res")
    npk = res / "ui.npk"
    if npk.is_file():
        return [npk], "ui.npk（单包，NPK 格式）"
    gpks = sorted(res.glob("ui_*.gpk"))
    if gpks:
        return gpks, "ui_*.gpk（%d 包，GPK 格式：%s）" % (len(gpks), [p.name for p in gpks])
    return [], ("未找到 UI 包。已查 %s 与 %s/ui_*.gpk\n"
                "    ⇒ 该功能需要 UI 资源包；当前客户端两种都没有。" % (npk, res))


def load_ids_multi(packages):
    """合并多个包 → {fid: dict(pkg, offset, packed, decoded, flag, row, source)}。

    两种格式分别处理（形状不同，不可混用）：
      · .npk → parse_npk()        产出 (fid, off, packed, decoded, flag)
      · .gpk → _gpk_blockchain()  产出 (row, fid, off, packed, decoded, flag)
                                   payload 偏移须加该行所属块的 payload_delta
    同名 fid 多包命中时保留首个，并保留来源包名以便追溯。
    """
    m = _reader()
    g = None
    ids = {}
    for pkg in packages:
        suffix = pkg.suffix.lower()
        if suffix == ".npk":
            if g is None:
                g = _gpk_module()
            rec, factory = g.parse_npk(str(pkg))
            for fid, off, packed, decoded, flag in factory():
                ids.setdefault(fid, {"pkg": pkg, "offset": off, "packed": packed,
                                     "decoded": decoded, "flag": flag, "row": None,
                                     "source": "npk-table-48b"})
        elif suffix == ".gpk":
            if g is None:
                g = _gpk_module()
            rec, factory, _ = g._gpk_blockchain(str(pkg))
            limits, cursor = [], 0
            for block in rec.get("blocks", []):
                cursor += int(block["entries"])
                limits.append((cursor, int(block["payload_delta"])))
            block_pos = 0
            for row, fid, off, packed, decoded, flag in factory():
                while block_pos + 1 < len(limits) and row >= limits[block_pos][0]:
                    block_pos += 1
                delta = limits[block_pos][1] if limits else int(rec["payload_delta"])
                ids.setdefault(fid, {"pkg": pkg, "offset": off + delta, "packed": packed,
                                     "decoded": decoded, "flag": flag, "row": row,
                                     "source": "gpk-table-8u32"})
        else:
            raise ValueError("不支持的包后缀：%s" % pkg)
    return ids


def _read_entry(m, info):
    """按 load_ids_multi 的记录读出一条载荷并解压。"""
    with info["pkg"].open("rb") as f:
        f.seek(info["offset"])
        raw = f.read(info["packed"])
    if len(raw) != info["packed"]:
        raise IOError("短读 %d/%d @ %s" % (len(raw), info["packed"], info["pkg"].name))
    return m.unpack_entry(raw, info["decoded"], info["flag"])

def cmd_dict(npk: str = "script.py3.npk"):
    """路径字典匹配（原 filename_restorer 核心）。"""
    pkg = Path(r"E:/mrzh/Documents") / npk
    m = _reader()
    ids = load_ids(pkg)
    dictp = _tool_produce_root() / "path_dictionary.txt"
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
    packages, note = resolve_ui_packages()
    if not packages:
        print("[restore] UI 包不可用，命令终止（不是工具坏了）：")
        print("    " + note)
        return
    print("[restore] UI 包来源：" + note)
    ids = load_ids_multi(packages)
    print(f"[restore] 合并条目 {len(ids):,} 条")
    matches = []
    for s in sorted(variants):
        fid = m.path_id(s)
        if fid in ids:
            matches.append({"path": s, "file_id": f"{fid:016X}",
                            "entry": ids[fid]["row"], "pkg": ids[fid]["pkg"].name})
    (OUT / "bindict_matches.json").write_text(json.dumps(matches, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"bindict 命中 {len(matches)} 条 -> output/filename_restore/bindict_matches.json")

def cmd_verify():
    """批量解包验证命中条目。"""
    m = _reader()
    matches = json.loads((OUT / "bindict_matches.json").read_text(encoding="utf-8"))
    packages, note = resolve_ui_packages()
    if not packages:
        print("[restore] UI 包不可用，命令终止（不是工具坏了）：")
        print("    " + note)
        return
    print("[restore] UI 包来源：" + note)
    ids = load_ids_multi(packages)
    results = []
    for x in matches:
        info = ids.get(int(x["file_id"], 16))
        if not info:
            continue
        try:
            raw = _read_entry(m, info)
        except Exception as exc:
            results.append({"path": x["path"], "file_id": x["file_id"],
                            "entry": info["row"], "flag": info["flag"], "raw_bytes": None,
                            "type": "decode_error:%s" % type(exc).__name__,
                            "pkg": info["pkg"].name, "source": info["source"]})
            continue
        typ = "png" if raw[:4] == b"\x89PNG" else "dds" if raw[:4] == b"DDS " else raw[:8].hex()
        results.append({"path": x["path"], "file_id": x["file_id"], "entry": info["row"],
                        "flag": info["flag"], "raw_bytes": len(raw), "type": typ,
                        "pkg": info["pkg"].name, "source": info["source"]})
    ok = sum(1 for r in results if r["type"] in ("png", "dds"))
    (OUT / "verified.json").write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"verify: {ok}/{len(results)} 合法资源 -> output/filename_restore/verified.json")

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "bindict"
    {"dict": cmd_dict, "bindict": cmd_bindict, "verify": cmd_verify}.get(cmd, cmd_bindict)()

if __name__ == "__main__":
    main()
