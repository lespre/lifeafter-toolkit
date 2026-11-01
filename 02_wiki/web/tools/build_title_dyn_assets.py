# -*- coding: utf-8 -*-
"""动态称号资源：从 csb 里取出动画首帧（步骤 1），后续可扩成完整逐帧。

数据链（全部可复核）：
  title_catalog item.anim_csb（来自 title_conf_data.shining_style → shining_title_conf_data.cocos_csb）
    → 定位 .csb：① row_path_map.db（PC 容器 res/ui_*.gpk、Documents/res/gres/*.gpk）按 fid 查 (container,row)
                  ② PE 包 pe_gres_android（头 32B 解密 + 表在 table_offset）
    → 读载荷（gpk 行 8×u32；载荷自 block_base(16)+offset+20，zstd/lz4 解压）
    → 扫描 csb 内 PNG/KTX 资源名（Cocos 场景里直接写着贴图路径）
    → img_fetch 导出（PE .ktx 优先，回落 PC .bc7），首帧缩到 ≤ 480px 宽
    → 回填 item.dyn_png / dyn_frames / dyn_csb_texture
不猜：csb 取不到或贴图取不到就不填，前端只显示已有内容。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import struct
import sys

PROJ = pathlib.Path(__file__).resolve().parents[3]
WEB = PROJ / "02_wiki/web"
BOARD = WEB / "data/boards/title_catalog.json"
OUT_DIR = WEB / "assets/title_dyn"

CORE = PROJ / "00_规范与工具/工具/工具库/00_共享核心"
SCAN = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"
for p in (str(CORE), str(SCAN)):
    if p not in sys.path:
        sys.path.insert(0, str(p))

from toolkit_core import img_fetch as IF  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from gpk_reader import aes_ecb  # noqa: E402
import la_unpack_core as UC  # noqa: E402

MRZH = pathlib.Path(r"E:\mrzh")
RPMAP = PROJ / "01_索引与产物/10_索引/indexes/row_path_map.db"
PE_IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PE_PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
IMG_RE = re.compile(rb"[ -~]{5,200}\.(?:png|ktx|jpg)", re.I)

# ── csb 定位 ────────────────────────────────────────────────
def locate_pc(csb_paths):
    """row_path_map.db：fid → (容器相对路径, 行号)。"""
    out = {}
    con = sqlite3.connect("file:%s?mode=ro" % RPMAP.as_posix(), uri=True)
    cur = con.cursor()
    for p in csb_paths:
        key = p if p.lower().endswith(".csb") else p + ".csb"
        r = cur.execute("select container,row_index from rows where fid_hex=? limit 1",
                        ("%016X" % fid_of(key),)).fetchone()
        if r:
            out[p] = r
    con.close()
    return out


def locate_pe(csb_paths):
    """PE gres 包：fid → (pack 文件名, 行号)。"""
    con = sqlite3.connect("file:%s?mode=ro" % PE_IDX.as_posix(), uri=True)
    cur = con.cursor()
    out = {}
    for p in csb_paths:
        key = p if p.lower().endswith(".csb") else p + ".csb"
        r = cur.execute("select pack,row from rows where fid=? limit 1",
                        ("%016X" % fid_of(key),)).fetchone()
        if r:
            out[p] = r
    con.close()
    return out


def gpk_row_bytes(path, row):
    """HPGF 行 → 解压后的载荷。格式见 gpk_npk_index.py 文档。"""
    with open(path, "rb") as f:
        head = aes_ecb(f.read(4096))
        n = struct.unpack_from("<I", head, 20)[0]
        f.seek(64)
        table = aes_ecb(f.read(n * 32))
    off, packed, decoded = struct.unpack_from("<III", table, row * 32)
    with open(path, "rb") as f:
        f.seek(16 + off + 20)
        raw = f.read(packed)
    if raw[:4] == b"\x28\xb5\x2f\xfd":
        return UC.decompress_zstd(raw, decoded or None)
    if raw[:2] == b"\x04\x22" or raw[:4] == b"\x04\x22\x4d\x18":
        try:
            return UC.decompress_lz4_block(raw, decoded, prefer_native=True)
        except Exception:
            return raw
    return raw


def csb_textures(raw):
    names = sorted({m.decode("utf-8", "ignore").replace("\\", "/") for m in IMG_RE.findall(raw)})
    return names


def pick_first(names):
    """逐帧取第一帧（文件名里带 00/01 序号时取最小）；单图原样返回。"""
    if not names:
        return ""
    if len(names) == 1:
        return names[0]
    def key(n):
        m = re.search(r"(\d{2,4})(?=\.[a-z]+$)", n, re.I)
        return (int(m.group(1)) if m else 1e9, n)
    return sorted(names, key=key)[0]


def export_png(tex, out):
    base = tex
    for ext in (".png", ".ktx", ".jpg"):
        if base.lower().endswith(ext):
            base = base[: -len(ext)]
            break
    for cand in (base, "ui/" + base):
        if IF.export(cand, out):
            return True
    return False


def shrink(out, max_w=480):
    """缩到 ≤ max_w，控制体积（只是预览，不改变资源内容）。"""
    try:
        from PIL import Image
        im = Image.open(out)
        if im.width > max_w:
            im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
        im.save(out, "PNG", optimize=True)
    except Exception as e:
        print("  缩放失败（保留原图）:", out.name, e)


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board["items"]
    csbs = sorted({str(it["anim_csb"]) for it in items if it.get("anim_csb")})
    print("动态条目 %d，唯一 csb %d" % (sum(1 for it in items if it.get("anim_csb")), len(csbs)))

    pc = locate_pc(csbs)
    pe = locate_pe(csbs)
    print("定位：PC %d，PE %d，合计 %d" % (len(pc), len(pe), len(set(pc) | set(pe))))
    payloads = {}
    # PC 容器：按容器聚合，只读需要的行
    by_cont = {}
    for p, (cont, row) in pc.items():
        by_cont.setdefault(cont, set()).add(row)
    for cont, rows in by_cont.items():
        fp = MRZH / cont
        if not fp.is_file():
            print("  容器缺失:", cont)
            continue
        for row in rows:
            try:
                payloads[("pc", cont, row)] = gpk_row_bytes(fp, row)
            except Exception as e:
                print("  读取失败:", cont, row, e)

    # PE 包：逐个包遍历一次表
    if pe:
        try:
            from toolkit_core import android_gpk as AG
            by_pack = {}
            for p, (pack, row) in pe.items():
                by_pack.setdefault(pack, set()).add(row)
            for pack, rows in by_pack.items():
                fp = PE_PACKS / pack
                if not fp.is_file():
                    print("  PE 包缺失:", pack)
                    continue
                for e in AG.iter_entries(str(fp)):
                    if e["row"] in rows:
                        payloads[("pe", pack, e["row"])] = e.get("payload") or b""
        except Exception as e:
            print("  PE 遍历异常:", e)

    # 每个 csb 取首帧
    tex_of = {}
    for p in csbs:
        raw = b""
        loc = None
        if p in pc:
            cont, row = pc[p]
            raw = payloads.get(("pc", cont, row), b"")
            loc = ("pc", cont, row)
        elif p in pe:
            pack, row = pe[p]
            raw = payloads.get(("pe", pack, row), b"")
            loc = ("pe", pack, row)
        if raw:
            names = csb_textures(raw)
            if names:
                tex_of[p] = (names, pick_first(names))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ok = miss = 0
    for it in items:
        it.pop("dyn_png", None)
        it.pop("dyn_frames", None)
        it.pop("dyn_tex", None)
        p = str(it.get("anim_csb") or "")
        if not p or p not in tex_of:
            continue
        names, first = tex_of[p]
        rel = "assets/title_dyn/ta_%s.png" % it["item_id"]
        if export_png(first, WEB / rel):
            shrink(WEB / rel)
            it["dyn_png"] = rel
            it["dyn_frames"] = len(names)
            it["dyn_tex"] = first
            ok += 1
        else:
            miss += 1
            print("  贴图未命中:", it["item_id"], it["name"], first)

    labels = board["meta"].setdefault("field_labels", {})
    labels.update({"dyn_png": "动态预览", "dyn_frames": "动画帧数", "dyn_tex": "动画贴图（csb 内引用）"})
    txt = json.dumps(board, ensure_ascii=False, indent=1)
    BOARD.write_text(txt, encoding="utf-8")
    (WEB / "data/boards/title_catalog.js").write_text(
        "window.WIKI_BOARD_title_catalog = " + txt + ";", encoding="utf-8")
    print("首帧导出 %d / 未命中 %d；总动态条目 %d"
          % (ok, miss, sum(1 for it in items if it.get("anim_csb"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
