# -*- coding: utf-8 -*-
"""构建「影音资源库」板数据：全量音频样本索引 + 已还原视频清单。

输入（只读，不改动）：
  01_索引与产物/30_分析/sound_pack_sample_index.json   # 样本名 → [[bank_entry, sample_index], …]
  01_索引与产物/41_还原树/pe/资源/video/**                # 已还原 mp4
  01_索引与产物/41_还原树/pe/资源/res/video.gpk/_未命名   # 按条目编号还原的 mp4
  01_索引与产物/20_提取/影音/audio/**                     # 已转码 mp3（由 convert_audio_to_mp3.py 产出）

输出：
  02_wiki/web/data/boards/media_catalog.json
  02_wiki/web/data/boards/media_catalog.js

口径：
  * 音频条目 = sound_pack_sample_index.json 的全部样本名（19,959），一条样本一行；
    category 仅按样本名前缀粗分组，只用于左侧导航，不代表官方分类。
  * extracted 字段 = 目标 mp3 是否已落盘；未转码条目坦白标「待提取」，不伪装可播。
  * 视频条目 = 还原树里实际存在的 mp4 文件，一条文件一行；不复制媒体进 web。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import re
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, WEB, DATA_DIR, BOARDS_DIR, ANALYSIS_ROOT, ARTIFACTS, INDEX_ROOT, rel  # noqa: E402

SOUND_INDEX = ANALYSIS_ROOT / "sound_pack_sample_index.json"
SOUND_BANK_DIR = ARTIFACTS / "41_还原树" / "pe" / "资源" / "res" / "sound.gpk" / "_未命名"
VIDEO_ROOT = ARTIFACTS / "41_还原树" / "pe" / "资源"
VIDEO_ENTRY_INDEX = (INDEX_ROOT / "site_data" / "audit" / "package_indexes"
                     / "gpk_test_res_video_gpk.entries.jsonl")
MEDIA_AUDIO_DIR = ARTIFACTS / "20_提取" / "影音" / "audio"
BOARD_ID = "media_catalog"

# 物证通道（2026-11-02）：影音板没有 cdata 表行，按既有「名册级条目」通道登记。
#   音频 = FSB5 样本名索引（19,959 个去重名）；视频 = video.gpk 条目表 + 已还原 mp4。
#   两者都只有「名字/路径 + 包内定位」，没有行级字段解码链 ⇒ roster 块（static-export），
#   条目强制 unverified 标签，页面据此做视觉区分（不伪造 locator_chain）。
AUDIO_SOURCE_ID = "sound-pack-sample-index"
VIDEO_SOURCE_ID = "video-gpk-entry-index"
ITEM_TAGS = ["unverified", "static config"]


def _lock(path: pathlib.Path, source_id: str, role: str, desc: str) -> dict:
    data = path.read_bytes()
    return {
        "source_id": source_id,
        "role": role,
        "path": rel(path),
        "sha256": hashlib.sha256(data).hexdigest(),
        "bytes": len(data),
        "mtime_ns": path.stat().st_mtime_ns,
        "desc": desc,
    }

# 音频分类：id → 中文名 + 前缀集合。顺序即左侧导航顺序。
AUDIO_CATS: list[tuple[str, str, tuple[str, ...]]] = [
    ("bgm", "背景音乐", ("bgm",)),
    ("music", "主题音乐", ("music",)),
    ("amb", "环境音", ("amb",)),
    ("ui", "界面音", ("ui", "s")),
    ("vo", "语音 / 对白", ("vo",)),
    ("cutscene", "过场 / 演示", ("cutscene", "anim")),
    ("newrace", "新种族", ("newrace",)),
    ("weapon", "武器 / 装备", ("weapon", "shotgun", "eqm", "equip")),
    ("object", "物件交互", ("object", "utility")),
    ("fx", "特效", ("fx", "firework", "mst")),
    ("impact", "打击 / 撞击", ("impact", "shoot", "toll")),
    ("furni", "家具", ("furni", "firework_dummy")),
    ("vehicle", "载具 / 机械", ("car", "veh", "motor", "drone", "aircraft", "carrier")),
    ("char", "角色", ("char", "fs", "bx", "bxr", "happy101", "newxinshou")),
    ("zombie", "丧尸", ("zombie",)),
    ("entity", "怪物 / 生物", ("m", "n", "b", "r", "vat", "ape", "snake", "rhino", "tiger",
                              "horse", "dog", "cat", "fish", "fernir", "harold", "linglong",
                              "7021", "7018", "7019", "7020")),
]
# 明确属于载具型号的 m####（避免把 m_1028 这类怪物攻击音归到载具）
VEHICLE_MODEL = re.compile(r"m(1130|1009|1283|6010|9006|1043)_", re.I)

VIDEO_DIR_CATS = {
    "artifact": "异变核武",
    "artifact_guide": "异变指南",
    "cyborg": "赛博",
    "drone": "无人机",
    "furniture": "家具 CG",
    "huodong": "活动视频",
    "nbs": "NBS",
    "ocean_fish": "海洋鱼类",
    "scan_map": "扫描地图",
    "summer_2025": "夏日活动",
    "talent": "职业教学",
    "winter_2025": "冬日活动",
}


def prefix_of(name: str) -> str:
    return name.split("_")[0].lower()


def audio_cat_of(name: str) -> str:
    p = prefix_of(name)
    if VEHICLE_MODEL.match(name):
        return "vehicle"
    for cid, _cn, prefixes in AUDIO_CATS:
        if p in prefixes:
            return cid
    return "other"


def safe_stem(name: str) -> str:
    return re.sub(r'[\\/:*?"<>|]', "_", name)


def rel_web(path: pathlib.Path) -> str:
    """项目内绝对路径 → 相对 02_wiki/web 的 URL 路径（正斜杠，允许指向 web 之外）。"""
    import os
    return os.path.relpath(str(path), str(WEB)).replace("\\", "/")


def video_cat_of(rel_parts: list[str], stem: str) -> str:
    # 还原树内命名的子目录优先
    for part in rel_parts:
        if part in VIDEO_DIR_CATS:
            return VIDEO_DIR_CATS[part]
    if "_未命名" in rel_parts:
        return "未命名视频"
    low = stem.lower()
    if any(k in low for k in ("cg", "dungeon", "story", "cutscene", "juben")):
        return "剧情 CG"
    if any(k in low for k in ("login", "loading", "huanye", "title", "kaichang")):
        return "登录 / 加载"
    if any(k in low for k in ("chest", "lottery", "hd_", "huodong", "shichao", "outbreak")):
        return "活动视频"
    return "其他视频"


def build() -> dict:
    if not SOUND_INDEX.exists():
        raise SystemExit(f"缺少音频索引：{SOUND_INDEX}")
    idx: dict[str, list[list[int]]] = json.loads(SOUND_INDEX.read_text(encoding="utf-8"))

    audio_items: list[dict] = []
    for name in sorted(idx):
        entry, sidx = idx[name][0]
        cat = audio_cat_of(name)
        mp3 = MEDIA_AUDIO_DIR / cat / (safe_stem(name) + ".mp3")
        audio_items.append({
            "kind": "a",
            "id": "a:" + name,
            "name": name,
            "category": cat,
            "bank_entry": int(entry),
            "sample_index": int(sidx),
            "media_path": rel_web(mp3),
            "extracted": mp3.exists() and mp3.stat().st_size > 1024,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "sound.gpk 样本索引 · bank %d #%d" % (int(entry), int(sidx)),
            "status_tags": list(ITEM_TAGS),
            "provenance": {
                "table": "sound_pack_sample_index",
                "row_key": name,
                "roster": {
                    "evidence": "static-export",
                    "source_id": AUDIO_SOURCE_ID,
                    "source_desc": "FMOD FSB5 样本名索引（res/sound.gpk + 热更 layers npk）；"
                                   "bank_entry/sample_index 指向包内样本",
                },
            },
        })

    video_files: list[pathlib.Path] = []
    vroot = VIDEO_ROOT / "video"
    if vroot.exists():
        video_files += sorted(vroot.rglob("*.mp4"))
    unnamed = VIDEO_ROOT / "res" / "video.gpk" / "_未命名"
    if unnamed.exists():
        video_files += sorted(unnamed.glob("*.mp4"))

    video_items: list[dict] = []
    for p in video_files:
        parts = list(p.relative_to(VIDEO_ROOT).parts)
        stem = p.stem
        cat = video_cat_of(parts, stem)
        base = stem
        if re.fullmatch(r"\d{8}", stem):
            display = f"未命名视频 #{int(stem)}"
            entry_index = int(stem)
        else:
            display = stem
            entry_index = None
        video_items.append({
            "kind": "v",
            "id": "v:" + str(p.relative_to(VIDEO_ROOT)).replace("\\", "/"),
            "name": display,
            "file_stem": base,
            "category": cat,
            "entry_index": entry_index,
            "media_path": rel_web(p),
            "size": p.stat().st_size,
            "extracted": True,
            "evidence": "structure",
            "evidence_level": "physical-resource-chain",
            "source": "res/video.gpk 条目 %s · 已还原 mp4" % (
                entry_index if entry_index is not None else "命名目录"),
            "status_tags": list(ITEM_TAGS),
            "provenance": {
                "table": "res/video.gpk",
                "row_key": entry_index if entry_index is not None else str(p.relative_to(VIDEO_ROOT)),
                "roster": {
                    "evidence": "static-export",
                    "source_id": VIDEO_SOURCE_ID,
                    "source_desc": "res/video.gpk 条目表（offset/packed_size/flag 见审计索引）"
                                   "+ 41_还原树已还原 mp4；媒体文件不复制进 web",
                },
            },
        })

    # 分类清单（只列非空分类）
    cnt_a = Counter(x["category"] for x in audio_items)
    cnt_v = Counter(x["category"] for x in video_items)
    cats = []
    for cid, cn, _p in AUDIO_CATS:
        if cnt_a.get(cid):
            cats.append({"id": cid, "name": cn, "kind": "a", "count": cnt_a[cid]})
    if cnt_a.get("other"):
        cats.append({"id": "other", "name": "其他样本", "kind": "a", "count": cnt_a["other"]})
    v_order: list[str] = []
    for _cid, cn in VIDEO_DIR_CATS.items():
        if cnt_v.get(cn) and cn not in v_order:
            v_order.append(cn)
    for cn in ("剧情 CG", "登录 / 加载", "活动视频", "其他视频", "未命名视频"):
        if cnt_v.get(cn) and cn not in v_order:
            v_order.append(cn)
    for cn in v_order:
        cats.append({"id": "v:" + cn, "name": cn, "kind": "v", "count": cnt_v[cn]})

    total = len(audio_items) + len(video_items)
    locks = [
        _lock(SOUND_INDEX, AUDIO_SOURCE_ID, "primary",
              "FMOD FSB5 样本名索引（样本名 → bank_entry/sample_index）"),
        _lock(VIDEO_ENTRY_INDEX, VIDEO_SOURCE_ID, "comparison",
              "res/video.gpk 条目表审计索引（offset/packed_size/decoded_size/flag）"),
    ]
    meta = {
        "name": "影音资源库 · 音频 19,959 + 视频 %d" % len(video_items),
        "category": "三、综合资料 / （七）影音资源",
        "board_id": BOARD_ID,
        "board_mode": "media_library",
        "generated": "2026-11-02",
        "source_server": "PE 测试服 · res/sound.gpk + 热更 res.sound.layers.1.1.npk 样本名索引；res/video.gpk 还原树",
        "package_sha": locks[0]["sha256"],
        "evidence": "structure",
        "state_summary": {
            "音频": len(audio_items),
            "视频": len(video_items),
            "可播放": sum(1 for x in audio_items if x["extracted"]) + len(video_items),
            "待提取": sum(1 for x in audio_items if not x["extracted"]),
        },
        "provenance": {
            "contract_version": 3,
            "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": locks,
            "source_scope": {
                "cross_source_policy": "no-cross-source-field-join",
                "integer_join_policy": "no-equal-integer-join",
                "runtime_final_policy": "unknown-unless-runtime-proven",
            },
        },
        "notes": "分类按样本名前缀 / 视频目录粗分组，仅作导航，不是官方分类。音频来自 FMOD FSB5 样本名索引（19,959 个去重名）；"
                 "可播文件为 20_提取/影音/audio 下已转码 mp3，未转码条目显示「待提取」。视频直接引用 41_还原树 内已还原 mp4，不复制进 web。",
        "counts": {
            "audio": len(audio_items),
            "audio_extracted": sum(1 for x in audio_items if x["extracted"]),
            "video": len(video_items),
            "video_extracted": len(video_items),
        },
        "categories": cats,
    }
    return {"meta": meta, "items": audio_items + video_items}


def main() -> int:
    d = build()
    BOARDS_DIR.mkdir(parents=True, exist_ok=True)
    (BOARDS_DIR / f"{BOARD_ID}.json").write_text(
        json.dumps(d, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    js = "window.WIKI_BOARD_%s=%s;\n" % (BOARD_ID, json.dumps(d, ensure_ascii=False, separators=(",", ":")))
    (BOARDS_DIR / f"{BOARD_ID}.js").write_text(js, encoding="utf-8")
    m = d["meta"]
    print("音频 %d（已转码 %d）/ 视频 %d" % (m["counts"]["audio"], m["counts"]["audio_extracted"], m["counts"]["video"]))
    print("分类：", ", ".join(f'{c["name"]}={c["count"]}' for c in m["categories"]))
    print("写出", BOARDS_DIR / f"{BOARD_ID}.json", (BOARDS_DIR / f"{BOARD_ID}.json").stat().st_size // 1024, "KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
