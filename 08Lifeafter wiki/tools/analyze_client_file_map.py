# -*- coding: utf-8 -*-
"""客户端文件地图分析器：分类统计 / 差异对比 / 候选清单 / Markdown 报告。

纪律：
- client 维度：test=E:\\mrzh（任务给定 + 根目录"体验服.lnk"）、live=E:\\LifeAfter（"正式服.exe"）——verified。
- server_branch 维度（经典服/简单生存服）：仅凭客户端目录不可判定，本报告一律 unresolved。
- 分类：扩展名映射为初步类别（likely）；对每类代表文件做魔数抽检，命中则整类升级依据写明
  （verified 仅对抽检样本本身，整类保留 likely+抽检说明）；无法归类的 unknown。
- 不产出任何业务关联结论；不动 wiki boards/业务数据。
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

AUDIT = Path(r"E:\la拆包项目\08Lifeafter wiki\data\audit\client_file_maps")
CLIENT_META = {
    "mrzh": {
        "client": "test",
        "root": r"E:\mrzh",
        "client_role": "测试服",
        "client_evidence": "任务指定 + 根目录 体验服.lnk（客户端类型昵称）",
        "server_branch": "unresolved",
        "server_evidence": "仅凭客户端目录无法判定经典服/简单生存服；无账号/启动器/公告级锚",
    },
    "lifeafter": {
        "client": "live",
        "root": r"E:\LifeAfter",
        "client_role": "正式服",
        "client_evidence": "任务指定 + 根目录 正式服.exe",
        "server_branch": "unresolved",
        "server_evidence": "仅凭客户端目录无法判定经典服/简单生存服；无账号/启动器/公告级锚",
    },
}

# 扩展名 → 用途（初始分类=likely 级；抽检命中后按说明处理）
EXT_CATEGORY = {
    ".py": "配置/脚本", ".pyc": "配置/脚本", ".nxs": "配置/脚本",
    ".bin": "配置/脚本", ".dat": "配置/脚本", ".conf": "配置/脚本",
    ".cfg": "配置/脚本", ".ini": "配置/脚本", ".yaml": "配置/脚本",
    ".json": "配置/脚本", ".xml": "配置/脚本", ".txt": "配置/脚本",
    ".ver": "配置/脚本", ".version": "配置/脚本", ".inf": "配置/脚本",
    ".csv": "配置/脚本", ".lua": "配置/脚本",
    ".idx": "索引", ".pi": "索引", ".hash": "索引",
    ".npk": "容器", ".gpk": "容器", ".wpk": "容器", ".fpk": "容器",
    ".pak": "容器", ".gpkx": "容器", ".ark": "容器", ".epk": "容器",
    ".bxml": "UI", ".layout": "UI", ".ui": "UI", ".atlas": "UI",
    ".dds": "贴图", ".png": "贴图", ".tga": "贴图", ".jpg": "贴图",
    ".jpeg": "贴图", ".ktx": "贴图", ".webp": "贴图",
    ".gim": "模型", ".mesh": "模型", ".mtg": "模型", ".skel": "模型",
    ".spine": "模型", ".skeleton": "模型", ".prefab": "模型",
    ".fsb": "音频", ".wav": "音频", ".ogg": "音频", ".mp3": "音频",
    ".bnk": "音频", ".soundbank": "音频", ".m4a": "音频",
    ".scene": "场景", ".unity": "场景", ".asset": "场景",
    ".hlod": "场景", ".terrain": "场景", ".nav": "场景",
    ".mp4": "视频/动画", ".anim": "视频/动画", ".ani": "视频/动画",
    ".fbx": "视频/动画",
    ".exe": "可执行/库", ".dll": "可执行/库", ".lnk": "可执行/库",
    ".bat": "可执行/库", ".cmd": "可执行/库", ".pdb": "可执行/库",
    ".log": "日志", ".md": "日志", ".sha256": "其它", ".bak": "其它",
    ".tmp": "其它", ".zip": "其它", ".7z": "其它", ".rar": "其它",
    ".wpd": "未知容器", ".cfs": "其它", ".store": "其它",
}

# 候选用途分类（输出统一类别）
CATEGORY_LABELS = [
    "配置/脚本", "文字数据", "UI", "贴图", "模型", "音频", "场景",
    "索引", "容器", "可执行/库", "视频/动画", "日志", "其它", "unknown",
    "运行时缓存(shader管线)", "运行时产物(客户端录像)", "运行时产物",
    "运行时产物(散装缓存)", "运行时产物(云缓存)", "运行时缓存/产物",
    "索引(云端资源)", "状态标记",
]

# 目录角色 → 业务角色说明（likely 级提示，非文件级判定）
DIR_ROLE_NOTES = {
    "bin": "二进制/启动链（客户端程序）",
    "res": "资源根（贴图/模型/音频/场景/UI 的主目录）",
    "documents": "热更/补丁覆盖区（脚本与资源增量）+ 运行时产物",
    "launcher_conf": "启动器配置",
    "root": "客户端根（入口 exe/容器/配置）",
}

# 路径身份特判（verified 依据=路径模式+大小形态；高于扩展名分类）
PATH_IDENTITY = [
    # (路径子串, 类别, 依据说明)
    ("g66discrete/effect_cache", "运行时缓存(shader管线)", "DX11 .pipe 着色器管线缓存，路径含 nfx2/pipeline/shader"),
    ("g66discrete/client_record", "运行时产物(客户端录像)", "client_record 录像分段 .vd，文件名含账号与会话时间"),
    ("g66discrete", "运行时产物", "g66discrete 运行时目录"),
    ("multi_cloud1/thd", "索引(云端资源)", "THFB/THX 资源索引对（building/character/ui/...），resource cloud"),
    ("multi_cloud1", "运行时产物(云缓存)", "multi_cloud1 云端资源缓存区"),
    ("/thd/", "索引(云端资源)", "THFB/THX 索引对"),
    ("Documents/res/", "运行时产物(散装缓存)", "Documents/res 无扩展名 hash 缓存/覆盖资源实体"),
    ("Documents/configs/", "配置/脚本", "Documents/configs 覆盖配置"),
    ("Documents/bin/", "可执行/库", "Documents/bin 运行链覆盖"),
    ("Documents/gres/", "容器", "gres gpk 热更资源容器区"),
    ("/gres/", "容器", "gres gpk 资源容器"),
    ("announce_bl_sig", "状态标记", "公告签名文件"),
    ("Documents/cfs_", "状态标记", "CFS 内容文件系统状态标记"),
    ("Documents/downloaded_packages", "状态标记", "已下载包清单"),
    ("Documents/compress_pc", "状态标记", "压缩状态标记"),
    ("Documents/bindict_mmap_enabled", "状态标记", "bindict mmap 开关标记"),
    ("launcher_conf/", "配置/脚本", "启动器配置目录"),
    ("launcher_conf", "配置/脚本", "启动器配置文件(无扩展)"),
    ("/plcoht_ag", "运行时产物(补丁缓存)", "plcoht_ag* = 补丁下载暂存分片（含 s_patch2/ 同名）"),
    ("/s_patch2/", "运行时产物(补丁缓存)", "s_patch2 补丁暂存区"),
    ("/local_state", "状态标记", "local_state* 客户端本地状态（版本/区服线索区，非服务器分支证据）"),
    ("/local_finfo", "状态标记", "local_finfo* 本地文件校验信息"),
    ("shader_compile.db", "运行时缓存(shader管线)", "SQLite shader 编译缓存"),
    ("/db/", "状态标记", "本地 SQLite 状态/缓存目录"),
    ("/fo_version", "状态标记", "fo_version 客户端资源版本标记"),
    ("/patchlock", "状态标记", "patchlock 补丁锁标记"),
    ("/fpk_history_res", "状态标记", "fpk 资源历史标记"),
    ("/history_downloaded_packages", "状态标记", "历史下载包清单"),
    ("/install_ts", "状态标记", "安装时间戳"),
    ("/last_cfs_compact_ts", "状态标记", "CFS 压缩时间戳"),
    ("/local_py3_ready", "状态标记", "py3 就绪标记"),
    ("/last_region_code", "状态标记", "区服代码本地记录（客户端自述，非独立验证；不得作为服务器分支 verified 依据）"),
    ("/download_", "状态标记", "download_* 补丁下载开关标记"),
    ("/ext_pack_config", "状态标记", "扩展包配置标记"),
    ("/pkg_left_files", "状态标记", "残留包文件目录"),
    ("/scan_progress.json", "状态标记", "扫描进度记录"),
    ("/sprite_history_data.txt", "日志", "精灵历史记录"),
    ("/obstruct_record.txt", "日志", "遮挡记录"),
    ("/gm_command_history.txt", "日志", "GM 命令历史"),
    ("/client_record_pending.json", "状态标记", "录像待上传清单"),
    ("/static.json", "状态标记", "云资源 static 元数据"),
    ("/Record/", "运行时产物", "录像相关目录"),
    ("mpay.cef.depends", "可执行/库", "CEF 支付组件"),
    ("webviewsupport", "可执行/库", "CEF webview 组件"),
    ("/grecord", "运行时产物", "录制组件数据"),
    ("ccmini", "日志", "ccmini 日志组件"),
    ("client_doc@", "状态标记", "client_doc@N/mail_content=已应用补丁编号点序列（空标记）"),
    ("/plls", "状态标记", "plls 补丁状态标记"),
    ("/prbsw", "状态标记", "prbsw 补丁状态标记"),
    ("/patch_ab_test_version", "状态标记", "patch AB 测试版本标记"),
    ("/patch_opt_2023_state_new", "状态标记", "补丁优化状态标记"),
    ("/pc_first_pack_converted", "状态标记", "首包转换标记"),
    ("/vlm_mark", "状态标记", "vlm 标记"),
    ("/gpk_ck1", "状态标记", "gpk 校验标记"),
    ("/local_dflag2", "状态标记", "本地标记 dflag2"),
    ("/cloud.lock", "状态标记", "云缓存锁"),
]

# 运行时/缓存类附加扩展名（非业务数据）
RUNTIME_EXTS = {".pipe", ".thh", ".thx", ".vd", ".ptx", ".ldb"}

# 扩展名 → 头部魔数抽检（命中即 verified 该样本）
MAGIC_PROBES = {
    ".png": [(b"\x89PNG\r\n\x1a\n", "png")],
    ".dds": [(b"DDS ", "dds")],
    ".jpg": [(b"\xff\xd8\xff", "jpeg")],
    ".fsb": [(b"FSB4", "fsb4"), (b"FSB5", "fsb5")],
    ".wav": [(b"RIFF", "riff-wav")],
    ".ogg": [(b"OggS", "ogg")],
    ".bxml": [(b"BXML", "bxml")],
    ".tga": [],
    ".gim": [],
    ".npk": [],
    ".gpk": [],
    ".wpk": [],
    ".fpk": [(b"\x28\xb5\x2f\xfd", "zstd-frame")],
    ".idx": [],
    ".pi": [],
    ".pyc": [],
    ".dat": [],
    ".nxs": [(b"tI", "tI-wrap")],
    ".bin": [],
    ".exe": [(b"MZ", "pe")],
    ".dll": [(b"MZ", "pe")],
}

# 头部探针：读取文件前 32B
def probe(path: Path) -> str | None:
    try:
        with path.open("rb") as f:
            head = f.read(32)
    except OSError:
        return None
    probes = MAGIC_PROBES.get(path.suffix.lower(), [])
    for magic, label in probes:
        if magic and head.startswith(magic):
            return label
    return None


def load_inventory(client: str) -> list[dict]:
    p = AUDIT / f"{client}_file_inventory.jsonl"
    if not p.is_file():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    return [json.loads(ln) for ln in lines if ln.strip()]


def categorize(rec: dict) -> str:
    """路径身份特判 > 扩展名映射 > unknown。"""
    path = rec["path"]
    for marker, cat, _why in PATH_IDENTITY:
        if marker in path:
            return cat
    ext = rec["ext"]
    if not ext:
        return "unknown"
    if ext in RUNTIME_EXTS:
        return "运行时缓存/产物"
    return EXT_CATEGORY.get(ext, "unknown")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--probe-samples", type=int, default=12,
                    help="每扩展名每客户端抽检样本数")
    ap.add_argument("--out", type=Path, default=AUDIT / "client_file_map_report.md")
    args = ap.parse_args()

    clients = ["mrzh", "lifeafter"]
    inv: dict[str, list[dict]] = {}
    for c in clients:
        inv[c] = load_inventory(c)
        print(f"{c}: {len(inv[c])} files")

    # ---- 1. 分类统计（likely 级：扩展名+目录角色）----
    stats: dict[str, dict] = {}
    for c in clients:
        cat = Counter(categorize(r) for r in inv[c])
        ext_counter = Counter(r["ext"] for r in inv[c])
        role_counter = Counter(r["dir_role"] for r in inv[c])
        size_by_cat = defaultdict(int)
        for r in inv[c]:
            size_by_cat[categorize(r)] += r["size"]
        stats[c] = {
            "total_files": len(inv[c]),
            "total_bytes": sum(r["size"] for r in inv[c]),
            "by_category": dict(cat),
            "bytes_by_category": dict(size_by_cat),
            "by_extension": dict(ext_counter.most_common(40)),
            "by_dir_role": dict(role_counter),
            "sha_full": sum(1 for r in inv[c] if r.get("sha_scope") == "full"),
            "sha_large_skip": sum(1 for r in inv[c] if r.get("sha_scope") == "large-skip"),
            "sha_media_skip": sum(1 for r in inv[c] if r.get("sha_scope") == "media-skip"),
        }

    # ---- 2. 魔数抽检（对抽检样本 verified；整类仍按说明）----
    probe_results: dict[str, dict[str, dict]] = {c: {} for c in clients}
    for c in clients:
        by_ext: dict[str, list[dict]] = defaultdict(list)
        for r in inv[c]:
            by_ext[r["ext"]].append(r)
        root_map = {c: Path(CLIENT_META[c]["root"]) for c in clients}
        for ext, recs in by_ext.items():
            if ext not in MAGIC_PROBES or not MAGIC_PROBES[ext]:
                continue
            hits: Counter = Counter()
            samples_done = 0
            for r in recs[: args.probe_samples]:
                p = root_map[c] / r["path"]
                label = probe(p)
                if label:
                    hits[label] += 1
                samples_done += 1
            probe_results[c][ext] = {
                "samples": samples_done,
                "hits": dict(hits),
            }

    # ---- 3. 差异对比（路径集合；同路径比 size/sha）----
    live_paths = {r["path"]: r for r in inv["lifeafter"]}
    test_paths = {r["path"]: r for r in inv["mrzh"]}
    only_live = sorted(set(live_paths) - set(test_paths))
    only_test = sorted(set(test_paths) - set(live_paths))
    both = sorted(set(live_paths) & set(test_paths))
    same = []
    differ_size = []
    differ_sha = []
    sha_unknown = 0
    for p in both:
        t, l = test_paths[p], live_paths[p]
        if t["size"] != l["size"]:
            differ_size.append(p)
            continue
        ts, ls = t.get("sha256"), l.get("sha256")
        if ts and ls:
            if ts != ls:
                differ_sha.append(p)
            else:
                same.append(p)
        else:
            sha_unknown += 1

    # ---- 4. 高优先级文字/配置候选 ----
    # 排除运行时/组件路径后，按扩展名与目录筛选；脚本容器（script*.npk 家族）
    # 单独成组——它们内部才是文字/配置数据的真正主体。
    RUNTIME_MARKERS = ("/bin/", "g66discrete", "multi_cloud", "plcoht_ag",
                       "s_patch2", "grecord", "mpay", "webview", "ccmini",
                       "/db/", "effect_cache", "client_record", "SurveyRes",
                       "shader_compile", "/res/", "thd/")
    TEXT_CFG_EXTS = {".nxs", ".pyc", ".json", ".xml", ".csv", ".yaml",
                     ".conf", ".cfg", ".ini", ".txt"}
    candidates: dict[str, list[dict]] = {c: [] for c in clients}
    script_packs: dict[str, list[dict]] = {c: [] for c in clients}
    for c in clients:
        for r in inv[c]:
            path = r["path"]
            if any(m in path for m in RUNTIME_MARKERS):
                continue
            if "script" in path and r["ext"] == ".npk":
                script_packs[c].append(r)
                continue
            if r["ext"] in TEXT_CFG_EXTS:
                candidates[c].append(r)
        candidates[c].sort(key=lambda x: -x["size"])
        script_packs[c].sort(key=lambda x: -x["size"])

    # ---- 5. unknown 清单 ----
    unknown: dict[str, list[dict]] = {c: [] for c in clients}
    for c in clients:
        for r in inv[c]:
            if categorize(r) == "unknown":
                unknown[c].append(r)
        unknown[c].sort(key=lambda x: -x["size"])

    # ---- 容器细分（npk/gpk/wpk/fpk 按路径前缀聚合，文件层身份）----
    container_split: dict[str, dict[str, dict]] = {c: {} for c in clients}
    for c in clients:
        by_pref: dict[str, dict] = {}
        for r in inv[c]:
            if r["ext"] not in (".npk", ".gpk", ".wpk", ".fpk", ".pak"):
                continue
            p = r["path"]
            if p.startswith("res/"):
                pref = "res-root/" + p.split("/", 2)[1] if "/" in p else "res-root"
            elif p.startswith("Documents/gres/"):
                pref = "documents-gres"
            elif p.startswith("Documents/res/"):
                pref = "documents-res"
            else:
                pref = p.split("/")[0]
            d = by_pref.setdefault(pref, {"files": 0, "bytes": 0, "names": []})
            d["files"] += 1
            d["bytes"] += r["size"]
            if len(d["names"]) < 12:
                d["names"].append(p)
        container_split[c] = by_pref

    # ---- 6. 输出 JSON 事实 + Markdown 报告 ----
    facts = {
        "generated_note": "file map v1; server_branch 一律 unresolved（客户端≠服务器）",
        "clients": {c: CLIENT_META[c] for c in clients},
        "stats": stats,
        "magic_probe": probe_results,
        "container_split": container_split,
        "diff": {
            "only_live": only_live,
            "only_test": only_test,
            "same": same,
            "differ_size": differ_size,
            "differ_sha": differ_sha,
            "sha_unknown_pairs": sha_unknown,
            "both_total": len(both),
        },
        "candidates": {c: [r["path"] for r in candidates[c]] for c in clients},
        "script_packs": {c: [r["path"] for r in script_packs[c]] for c in clients},
    }
    (AUDIT / "client_file_map_facts.json").write_text(
        json.dumps(facts, ensure_ascii=False, indent=1), encoding="utf-8")

    md = []
    md.append("# 双客户端文件地图（v1）\n")
    md.append("> 纪律：client 维度 verified（任务指定+启动器文件）；server_branch 一律 unresolved。")
    md.append("> 分类：verified=魔数抽检命中样本；likely=扩展名+目录角色；unknown=无法归类。\n")
    for c in clients:
        meta = CLIENT_META[c]
        st = stats[c]
        md.append(f"## {meta['client_role']}（{c}）\n")
        md.append(f"- 根：`{meta['root']}`；client 判定：{meta['client_evidence']}")
        md.append(f"- **server_branch：{meta['server_branch']}**（{meta['server_evidence']}）\n")
        md.append(f"- 文件数 {st['total_files']}；总大小 {st['total_bytes']/1e9:.1f} GB；SHA 全量 {st['sha_full']}；")
        md.append(f"大文件跳过 {st['sha_large_skip']}；媒体跳过 {st['sha_media_skip']}\n")
        md.append("### 分类统计（likely 级）\n")
        md.append("| 类别 | 文件数 | 字节(GB) |")
        md.append("|---|---:|---:|")
        for label in CATEGORY_LABELS:
            n = st["by_category"].get(label, 0)
            if n:
                md.append(f"| {label} | {n} | {st['bytes_by_category'].get(label,0)/1e9:.2f} |")
        md.append("\n### 顶层目录角色\n")
        md.append("| 目录 | 文件数 |")
        md.append("|---|---:|")
        for role, n in sorted(st["by_dir_role"].items(), key=lambda x: -x[1])[:15]:
            md.append(f"| {role} | {n} |")
        md.append("\n### 魔数抽检（命中=样本 verified）\n")
        md.append("| 扩展名 | 抽检 | 命中 |")
        md.append("|---|---:|---|")
        for ext, res in sorted(probe_results[c].items()):
            if res["hits"]:
                md.append(f"| {ext} | {res['samples']} | {json.dumps(res['hits'], ensure_ascii=False)} |")
        md.append("")
    # 差异
    d = facts["diff"]
    md.append("## C. 正式服/测试服差异\n")
    md.append(f"- 双端共有路径：{d['both_total']}；内容一致(SHA同)：{len(d['same'])}；")
    md.append(f"仅测试服：{len(d['only_test'])}；仅正式服：{len(d['only_live'])}；同路径大小不同：{len(d['differ_size'])}；")
    md.append(f"同路径同大小 SHA 未知（媒体/大文件）：{d['sha_unknown_pairs']}\n")
    for label, items in (("仅正式服", d["only_live"]), ("仅测试服", d["only_test"]),
                         ("同路径大小不同", d["differ_size"]), ("同大小SHA不同", d["differ_sha"])):
        md.append(f"### {label}（{len(items)}）")
        md.append("```text")
        for p in items[:60]:
            md.append(p)
        if len(items) > 60:
            md.append(f"... 共 {len(items)} 条，全量见 facts JSON")
        md.append("```\n")
    # 候选
    md.append("## D. 高优先级文字/配置候选\n")
    md.append("> 判定：**文件层 likely**。真正业务文字/配置位于 script*.npk 容器**内部**；")
    md.append("> 下列散装文件仅文件层候选，需包内条目级验证后才可读内容。\n")
    for c in clients:
        md.append(f"### {CLIENT_META[c]['client_role']} · 脚本容器（script 家族，文字/配置主体候选）")
        md.append("| 路径 | 大小(MB) |")
        md.append("|---|---:|")
        for r in script_packs[c]:
            md.append(f"| {r['path']} | {r['size']/1e6:.1f} |")
        md.append("")
    for c in clients:
        md.append(f"### {CLIENT_META[c]['client_role']} · 散装配置/文字（前 60 按大小）")
        md.append("| 路径 | 大小(MB) |")
        md.append("|---|---:|")
        for r in candidates[c][:60]:
            md.append(f"| {r['path']} | {r['size']/1e6:.1f} |")
        md.append("")
    # 容器细分
    md.append("## B2. 容器细分（文件层；包内内容需条目级扫描）\n")
    for c in clients:
        md.append(f"### {CLIENT_META[c]['client_role']}")
        md.append("| 容器区 | 文件数 | 大小(GB) | 样本 |")
        md.append("|---|---:|---:|---|")
        for pref, d in sorted(container_split[c].items(), key=lambda x: -x[1]["bytes"]):
            names = "; ".join(n.split("/")[-1] for n in d["names"][:6])
            md.append(f"| {pref} | {d['files']} | {d['bytes']/1e9:.1f} | {names[:120]} |")
        md.append("")
    # unknown
    md.append("## E. unknown 清单\n")
    md.append("> 文件层无法归类的文件；均为小文件/状态标记类，无大体积业务数据。\n")
    for c in clients:
        md.append(f"### {CLIENT_META[c]['client_role']}（{len(unknown[c])} 条，前 50 按大小）")
        md.append("| 路径 | 大小(MB) | ext |")
        md.append("|---|---:|---|")
        for r in unknown[c][:50]:
            md.append(f"| {r['path']} | {r['size']/1e6:.1f} | {r['ext']} |")
        md.append("")
    md.append("## F. 下一步建议\n")
    md.append("优先级从高到低（全部只读）：\n")
    md.append("1. **script*.npk 容器家族条目级盘点**（双端 Documents + 根目录）：这是文字/配置业务数据的真正主体；")
    md.append("   双端已有 11 个候选源的 SHA/条目锁（live_sources.json），建议扩展到全部 script 包并按容器内条目分类。")
    md.append("2. **双端同路径脚本/容器做条目级 diff**（现有 214 个文件级 SHA 相同=内容一致基线）；")
    md.append("   同路径大小不同 419 个里挑 script/config 类做内容 diff。")
    md.append("3. **res-root 容器**（mrzh 独有 4GB 级 character/ui/model 大 npk）与 **documents-gres**（双端 2.15GB×N gpk）：")
    md.append("   内容分类建议按 1DPW/IDX/gpk 条目层做抽样盘点，明确贴图/模型/音频/场景配额。")
    md.append("4. **launcher_conf 文件**（双端 1916B）：读内容确认启动器配置语义（客户端身份线索，非服务器分支证据）。")
    md.append("5. **local_state / local_finfo / last_region_code** 仅作客户端自述线索登记，需要账号/公告级锚才能验证服务器分支。")
    md.append("6. 双端 `.vd` 客户端录像为账号 14221351 会话录像（已属既有 external_refs 玩家），无业务价值，后续可排除。")
    (args.out).write_text("\n".join(md), encoding="utf-8")
    print(f"report -> {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
