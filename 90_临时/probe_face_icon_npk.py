# -*- coding: utf-8 -*-
r"""临时探针：在未建索引的 PE .npk（pe_npk_full / pe_ui_npk）里按候选路径的 file_id
查找缺失的头饰/面饰图标。只读条目表，不读载荷。
"""
from __future__ import annotations

import struct
import sys
import pathlib

PROJ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from npk_reader import aes_ecb  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

STEMS = [
    "icon_h_m_4087001", "icon_h_m_4043001", "icon_260030",  # 阳性对照（PE gpk 里已命中）
    "icon_h_m_4007001", "icon_h_m_4025001", "icon_h_m_3514003", "icon_h_m_4027001",
    "icon_h_m_3549001", "icon_h_m_4029001", "icon_h_m_3496002", "icon_h_m_3496003",
    "icon_h_m_3354001", "icon_h_m_3355001", "icon_h_m_3447001", "icon_h_m_4140001",
    "icon_h_m_4141001", "icon_h_m_3507001", "icon_h_m_3451001", "icon_h_m_3452001",
    "icon_h_m_3495001", "icon_h_m_3443001", "icon_h_m_3395001", "icon_h_m_3444001",
    "icon_h_m_3377001", "icon_h_m_3379001", "icon_h_m_3547001", "icon_h_m_4030001",
    "icon_h_m_4049001", "icon_h_m_4048001", "icon_h_m_4050001",
    "icon_260041", "icon_260042", "icon_260054", "icon_260053", "icon_260020",
    "icon_260010", "icon_260000", "icon_260070", "icon_260051", "icon_260052",
    "icon_260050",
]
PRE = ["ui/item_icon/", "ui/item_big_icon/", "ui/upload_icon/item_icon/",
       "item_icon/", "ui/icon/", "ui/item_icon_s/"]
SUF = ["_b", "_s", "", "_1"]
EXT = [".ktx", ".dds", ".png", ".bc7"]


def build_candidates() -> dict:
    m = {}
    for stem in STEMS:
        for pre in PRE:
            for suf in SUF:
                for ext in EXT:
                    for sep in ("/", "\\"):
                        p = (pre + stem + suf + ext).replace("/", sep)
                        m["%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)] = p
    return m


def iter_npks():
    for d in ("pe_npk_full", "pe_ui_npk", "pe_npk_20261029"):
        root = PROJ / "01_索引与产物/源包" / d
        if not root.is_dir():
            continue
        for p in sorted(root.rglob("*.npk")):
            yield p


def main() -> int:
    cands = build_candidates()
    print("候选 fid %d 个" % len(cands), flush=True)
    hits = {}
    for i, p in enumerate(iter_npks(), 1):
        try:
            with open(p, "rb") as f:
                h = aes_ecb(f.read(32))
                _u, magic, _ver, tbl, cnt = struct.unpack_from("<QIIII", h, 0)
                if magic != 0x4B50584E or cnt == 0 or cnt > 8_000_000:
                    print("  跳过(头异常) %s magic=%s cnt=%s" % (p.name, hex(magic), cnt), flush=True)
                    continue
                if tbl + cnt * 48 > p.stat().st_size:
                    print("  跳过(表越界) %s tbl=%d cnt=%d size=%d"
                          % (p.name, tbl, cnt, p.stat().st_size), flush=True)
                    continue
                f.seek(tbl)
                tab = aes_ecb(f.read(cnt * 48))
                if len(tab) < cnt * 48:
                    print("  跳过(表读短) %s" % p.name, flush=True)
                    continue
        except Exception as e:
            print("  异常 %s %r" % (p.name, e), flush=True)
            continue
        for k in range(cnt):
            fid = struct.unpack_from("<Q", tab, k * 48)[0]
            hx = "%016X" % fid
            if hx in cands:
                hits[hx] = (cands[hx], str(p.relative_to(PROJ)), k)
        if i % 10 == 0:
            print("  扫描 %d 个 npk ｜ 命中 %d" % (i, len(hits)), flush=True)
    print("=== 命中 %d ===" % len(hits))
    for hx, (path, npk, row) in sorted(hits.items(), key=lambda x: x[1][0]):
        print("  %-46s %s row %d" % (path, npk, row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
