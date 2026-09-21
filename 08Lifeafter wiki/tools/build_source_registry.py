# -*- coding: utf-8 -*-
"""统一 source registry 构建器（P0-6/7 收尾）。

从双客户端文件地图（inventory JSONL）筛选“后续可能参与解析的数据源”并登记：

纳入：
1. 容器：.npk/.gpk/.wpk/.fpk（script 家族、res-root 资源、gres、documents-res 覆盖）——
   排除 bin/g66discrete/multi_cloud/plcoht 等运行区；
2. 散装配置/文字：Documents 根与客户端根的 .json/.ini/.txt/.xml/.csv/.yaml/.conf/.cfg/.dat/.bin，
   排除运行记录（scan_progress/sprite_history/obstruct_record/gm_command_history/mrzh_installer/
   loading_record/client_record_pending/*.log）与 CEF 组件（cef*/natives/snapshot/v8/locales/percent pak）；
3. file_hash_pack.bin（客户端外层文件清单，P1 全包索引直接有用）。

不纳入（记录原因）：
- 媒体（dds/png/gim/mesh/fsb/mp4…）、.pipe/.thh/.thx/.vd/.ptx/.ldb、bin/* 运行组件、
  CEF、g66discrete/multi_cloud/plcoht_ag/s_patch2 缓存、Documents/res 散装缓存、日志/运行记录、
  SQLite db、SurveyRes/Record/grecord/ccmini。

字段：source_id / client_channel(test|live) / server_branch(一律 unresolved) /
      kind / path / ext / size / mtime_ns / sha256 / sha_scope / file_map_ref / note。
server_branch=unresolved 是硬纪律：仅凭客户端目录不可判定经典服/简单生存服。
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AUDIT = Path(r"E:\la拆包项目\08Lifeafter wiki\data\audit\client_file_maps")
OUT = Path(r"E:\la拆包项目\08Lifeafter wiki\data\source_registry.json")
CLIENT_ROLE = {"mrzh": "test", "lifeafter": "live"}

CONTAINER_EXTS = {".npk", ".gpk", ".wpk", ".fpk", ".idx"}
CONFIG_EXTS = {".json", ".ini", ".txt", ".xml", ".csv", ".yaml", ".conf",
               ".cfg", ".dat", ".bin"}
RUN_RECORD_MARKERS = (
    "scan_progress", "sprite_history", "obstruct_record", "gm_command_history",
    "mrzh_installer", "loading_record", "client_record_pending", "ccmini",
    "survey", "natives_blob", "snapshot_blob", "v8_context",
)
CEF_MARKERS = ("cef", "devtools", "locales/", "_percent", "en-gb", "en-us",
               "zh-cn", "zh-tw", "ja.pak")

KIND_MAP = {
    ".npk": "容器(script)" if "script" else "容器(npk)",
    ".gpk": "容器(gpk)",
    ".wpk": "容器(wpk)",
    ".fpk": "容器(fpk)",
}


def is_run_area(path: str) -> bool:
    # Documents/res/ 下的 .wpk/.idx/.gpk/.npk/.fpk 是真热更覆盖容器（非散装缓存）
    if path.startswith("Documents/res/") and path.rsplit(".", 1)[-1].lower() in (
            "wpk", "idx", "gpk", "npk", "fpk", "pak"):
        return False
    return (path.startswith("bin/") or "/bin/" in path
            or "g66discrete" in path or "multi_cloud" in path
            or "plcoht" in path or "s_patch2" in path or "grecord" in path
            or "/db/" in path or "shader_compile" in path
            or "Documents/res/" in path or "thd/" in path
            or "/Record/" in path or "client_record" in path)


def kind_of(path: str, ext: str, size: int) -> str:
    if "script" in path and ext == ".npk":
        return "容器(script)"
    if ext == ".npk":
        return "容器(npk)"
    if ext == ".gpk":
        return "容器(gpk)"
    if ext == ".wpk":
        return "容器(wpk)"
    if ext == ".fpk":
        return "容器(fpk)"
    if ext == ".idx":
        return "索引(idx)"
    if path.endswith("file_hash_pack.bin"):
        return "文件清单(fhpk)"
    if ext == ".bin":
        return "配置/脚本(bin)"
    if ext == ".dat":
        return "配置/脚本(dat)"
    if ext == ".txt":
        return "配置/文字(txt)"
    return f"配置/文字({ext.lstrip('.')})"


def main() -> int:
    entries = []
    for client, inv_name in (("mrzh", "mrzh_file_inventory.jsonl"),
                             ("lifeafter", "lifeafter_file_inventory.jsonl")):
        lines = (AUDIT / inv_name).read_text(encoding="utf-8").splitlines()
        for ln in lines:
            if not ln.strip():
                continue
            r = json.loads(ln)
            path = r["path"]
            ext = r["ext"]
            size = r["size"]
            if is_run_area(path):
                continue
            name_l = path.split("/")[-1].lower()
            include = False
            reason = ""
            if ext in CONTAINER_EXTS:
                include = True
            elif path.endswith("file_hash_pack.bin"):
                include = True
            elif ext in CONFIG_EXTS:
                if path.startswith(("Documents/", "")) and "/" not in path:
                    pass
                if any(m in path for m in RUN_RECORD_MARKERS):
                    reason = "运行/会话记录，不参与解析"
                elif any(m in name_l for m in CEF_MARKERS):
                    reason = "CEF 组件"
                else:
                    include = True
            if not include:
                continue
            kind = kind_of(path, ext, size)
            sha = r.get("sha256")
            scope = r.get("sha_scope")
            if scope == "large-skip" and not sha:
                # 大包 SHA 补充文件（big_npk_sha.json）回填；键为绝对路径
                # （含反斜杠），用 posix 相对路径后缀匹配避免斜杠形态不一致
                big = (AUDIT / "big_npk_sha.json")
                if big.is_file():
                    m = json.loads(big.read_text(encoding="utf-8"))
                    for abs_path, digest in m.items():
                        if abs_path.replace("\\", "/").endswith(path):
                            sha = digest
                            scope = "full"
                            break
            entries.append({
                "source_id": f"{CLIENT_ROLE[client]}-{kind.replace('(', '').replace(')', '').replace('/', '-')}-{len(entries) + 1:04d}",
                "client_channel": CLIENT_ROLE[client],
                "server_branch": "unresolved",
                "kind": kind,
                "path": path,
                "ext": ext,
                "size": size,
                "mtime_ns": r["mtime_ns"],
                "sha256": sha,
                "sha_scope": scope if sha else "missing",
                "note": reason or "file-map registered source (P0-7)",
            })
    # 稳定排序：client → kind → path
    entries.sort(key=lambda e: (e["client_channel"], e["kind"], e["path"]))
    # source_id 重排为稳定序
    for i, e in enumerate(entries, 1):
        e["source_id"] = f"{e['client_channel']}-{e['kind'].replace('(', '').replace(')', '').replace('/', '-').replace('.', '')}-{i:04d}"
    registry = {
        "schema_version": 1,
        "kind": "unified-source-registry",
        "generated_from": "data/audit/client_file_maps/*_file_inventory.jsonl + big_npk_sha.json",
        "scope": "双客户端文件层数据源（后续可能参与解析）",
        "client_channels": {"test": "E:\\mrzh 测试服", "live": "E:\\LifeAfter 正式服"},
        "server_branch_policy": "unresolved（仅凭客户端目录不可判定经典服/简单生存服）",
        "excluded": {
            "media": "dds/png/gim/mesh/fsb/mp4 等媒体（P7 图片索引阶段单独登记）",
            "runtime_cache": ".pipe/.thh/.thx/.vd/无扩展散装缓存/plcoht_ag/SQLite db",
            "bin_runtime": "bin/* 运行组件与 CEF（exe/dll/pak/locales/natives/snapshot）",
            "logs_records": "日志与运行记录（.log/.ldb/scan_progress/录像等）",
            "cloud": "multi_cloud/g66discrete 云端与运行时产物",
        },
        "sources": entries,
    }
    OUT.write_text(json.dumps(registry, ensure_ascii=False, indent=1) + "\n",
                   encoding="utf-8")
    # 统计
    from collections import Counter
    by_client = Counter(e["client_channel"] for e in entries)
    by_kind = Counter(e["kind"] for e in entries)
    sha_missing = [e["path"] for e in entries if not e["sha256"]]
    print("total:", len(entries), dict(by_client))
    print("by_kind:", dict(by_kind))
    print("sha_missing:", len(sha_missing), sha_missing[:8])
    print("registry ->", OUT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
