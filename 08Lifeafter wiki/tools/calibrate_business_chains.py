# -*- coding: utf-8 -*-
"""
calibrate_business_chains.py —— 业务定位链双服双版本校准器（2026-09-06 用户定版铁律）

对 wiki 每条业务定位链（奖池/满减/神秘/核芯/芯片/载具/外观名册）做 BA8（简单服·测试包）vs
正式服 LifeAfter npk（经典服）的双源对照：每张链表的 FID 存在性（同 FID=同文件）、大小、
通道分类（ykxq 全量/kj1 覆盖/kjxq 专属/海外壳/chs 池），输出结论供卡面标注与文档同步。

用法：
  python tools/calibrate_business_chains.py --json          # 全链对照（默认人读表）
  python tools/calibrate_business_chains.py --chain chip    # 单链
输出：stdout 对照表；--json 全量 JSON（含 BA8 表清单+FID+双源判定）
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BA8_ENTRIES = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries")
BA8_MANIFEST = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\manifest.json")
TAIL_PAT = re.compile(rb"[A-Za-z0-9_\\]{8,}\.py")

# 业务链 → 表名关键词（命中=该链成员表；注意别跨链误伤：用表名核心词）
CHAINS = {
    "lottery":  ["super_fashion_lottery", "reward_pool_data", "common_lottery_conf",
                 "lottery_big_reward", "fashion_sale_conf"],
    "manjian":  ["manjian_market", "manjian_huodong", "discount_market"],
    "mystery":  ["random_discount"],
    "nucleus":  ["nucleus_lottery", "nucleus_build_data"],
    "chip":     ["special_chip_lottery", "chip_type_data", "special_chip"],
    "vehicle":  ["vehicle_lottery", "vehicle_proto", "tuning_vehicle", "vehicle_purchase"],
    "chenshi":  ["optional_hd_exchange_shop_data"],
    "huodong":  ["huodong_conf_data"],
    "fashion":  ["fashion_data", "player_module_appear", "player_appear_data", "buff_data",
                 "weapon_skin_data", "gift_data", "common_item_data"],
}

def classify(name: str) -> str:
    n = name.lower()
    if "_chs.py" in n or n.endswith("_chs"):
        return "chs"
    if any(r in n for r in ("_auto_oversea_data_kjxq", "_auto_oversea_data_kj1",
                            "_auto_oversea_data_xq", "_auto_oversea_data_kj")):
        return "kj1/kjxq"
    if "_auto_oversea_data_ykxq" in n:
        return "ykxq"
    if "_auto_oversea_data_yk" in n or "_auto_oversea_data_y" in n:
        return "yk"
    if any(r in n for r in ("_auto_oversea_data_kr", "_auto_oversea_data_sea",
                            "_auto_oversea_data_kjhmt", "_auto_oversea_data_au",
                            "_auto_oversea_data_kjjp", "_auto_oversea_data_kjna")):
        return "oversea-shell"
    if "auto_oversea_data" in n:
        return "oversea-var"
    return "main"

def load_ba8():
    manifest = json.load(open(BA8_MANIFEST, encoding="utf-8"))
    fid_by_file = {}
    for item in manifest if isinstance(manifest, list) else manifest.get("entries", []):
        fi = item.get("file_id")
        ix = item.get("index")
        fn = f"{int(ix):06d}.bin"
        if fi is not None:
            fid_by_file[fn] = f"{fi:016X}" if isinstance(fi, int) else str(fi).upper()
    return fid_by_file

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chain", default=None, help="只跑指定链：lottery/manjian/mystery/nucleus/chip/vehicle/huodong/fashion")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    fid_by_file = load_ba8()
    # 正式服 FID 全集
    sys.path.insert(0, str(ROOT / "tools"))
    reg = json.load(open(ROOT / "data" / "live_sources.json", encoding="utf-8"))
    src = next(s for s in reg["sources"] if s.get("source_id") == "lifeafter-classic-current")
    from live_npk_reader import LiveNpkReader
    rd = LiveNpkReader(src["path"], src.get("server_branch", "classic"))
    formal = {f"{e.file_id:016X}" for e in rd._entries}
    formal_size = {f"{e.file_id:016X}": getattr(e, "declared_size", getattr(e, "size", None)) for e in rd._entries}

    # 单次全扫 BA8：file -> {names, fid, bytes}
    ba8 = {}
    for p in BA8_ENTRIES.glob("*.bin"):
        if p.stat().st_size < 250:
            continue
        names = {m.decode("ascii", "replace").split("\\")[-1] for m in TAIL_PAT.findall(p.read_bytes()[-8192:])}
        ba8[p.name] = {"names": names, "fid": fid_by_file.get(p.name, ""), "bytes": p.stat().st_size}

    chains = {c: CHAINS[c] for c in (CHAINS if not args.chain else [args.chain])}
    out = {"chains": {}}
    for cname, kws in chains.items():
        members = []
        for fn, info in ba8.items():
            hit = next((n for n in info["names"] if any(k in n.lower() for k in kws)), None)
            if hit:
                fid = info["fid"]
                members.append({
                    "file": fn, "bytes": info["bytes"], "name": hit, "fid": fid,
                    "cls": classify(hit),
                    "dual": ("shared" if fid and fid in formal else ("formal-only" if not fid and False else
                             ("ba8-only" if fid and fid not in formal else "no-fid"))),
                    "formal_bytes": formal_size.get(fid) if fid else None,
                })
        out["chains"][cname] = members

    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=1))
        return
    for cname, members in out["chains"].items():
        print(f"\n══ {cname}（{len(members)} 文件）")
        mem_sorted = sorted(members, key=lambda m: (m["cls"], m["file"]))
        for m in mem_sorted:
            if m["cls"] in ("oversea-shell",) and m["bytes"] < 1000:
                continue
            st = {"shared": "双源共享", "ba8-only": "BA8/简单服专属", "no-fid": "无FID"}[m["dual"]]
            sz = f"（正式 {m['formal_bytes']:,}B）" if m["dual"] == "shared" and m["formal_bytes"] else ""
            print(f"  {m['file']} {m['bytes']:>9,}B {m['cls']:<10} {m['name'][:66]:68s} {st}{sz}")

if __name__ == "__main__":
    main()
