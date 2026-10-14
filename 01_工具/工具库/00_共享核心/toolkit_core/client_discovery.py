# -*- coding: utf-8 -*-
"""交接包用的客户端发现与版本识别（只读）。

扫描边界：先看显式路径/环境变量/常见目录，再做有限深度、有限数量的候选扫描；
不把正式服当体验服，不修改客户端文件。
"""
from __future__ import annotations

import configparser
import json
import os
import pickle
import re
import string
import time
from pathlib import Path
from typing import Iterable

_MARKERS = (
    "lifeafter.exe", "mrzh_launcher.exe", "local_state_314_lc",
    "cloud.json", "update.ini", "download_playertest_patch",
    "download_futuretest_patch", "download_gray_patch",
)
_LINE_MARKERS = {
    "playertest": "download_playertest_patch",
    "futuretest": "download_futuretest_patch",
    "gray": "download_gray_patch",
}


def _marker_map(root: Path) -> dict[str, bool]:
    doc = root / "Documents"
    return {m: (doc / m).is_file() if m.startswith("download_") or m in {
        "local_state_314_lc", "cloud.json", "update.ini"} else (root / m).is_file()
            for m in _MARKERS}


def classify_client(root: Path | str, *, markers: dict[str, bool] | None = None) -> dict:
    """依据硬标记分类客户端，不依据目录名猜服别。"""
    root = Path(root)
    m = dict(markers) if markers is not None else _marker_map(root)
    if m.get("download_playertest_patch"):
        line, kind = "playertest", "测试服"
    elif m.get("download_futuretest_patch"):
        line, kind = "futuretest", "未来测"
    elif m.get("download_gray_patch"):
        line, kind = "gray", "灰度"
    else:
        line, kind = "release", "正式服"
    evidence = [k for k, v in m.items() if v]
    return {
        "root": str(root), "line": line, "server_kind": kind,
        "markers": m, "evidence": evidence,
        "safe_for_experience_source": line in {"playertest", "futuretest"},
    }


def _cdn_dir_from_version_info(vi: dict) -> str | None:
    for value in vi.values():
        if not isinstance(value, dict):
            continue
        name = value.get("name")
        if isinstance(name, str) and "/" in name and (
                "pkg_lst" in name or re.search(r"/pkg_\d+\.pi$", name)):
            return name.split("/", 1)[0]
    return None


def version_summary(state: dict) -> dict:
    """从 local_state 的 version_info 提取版本号、CDN目录和版本滞后关系。"""
    vi = state.get("version_info") if isinstance(state, dict) else None
    vi = vi if isinstance(vi, dict) else (state if isinstance(state, dict) else {})
    version = vi.get("version") or vi.get("client_version")
    cdn_dir = _cdn_dir_from_version_info(vi)
    revision = vi.get("revision")
    if not version and isinstance(vi.get("files"), dict):
        for value in vi["files"].values():
            if isinstance(value, dict) and value.get("fver"):
                version = value.get("fver")
                break
    def stamp(value: str | None) -> str | None:
        m = re.search(r"(\d{8}_\d{6})", value or "")
        return m.group(1) if m else None
    vs, cs = stamp(str(version) if version else None), stamp(cdn_dir)
    if vs and cs and cs > vs:
        relation = "版本号早于 CDN 包目录"
    elif vs and cs and cs == vs:
        relation = "版本号与 CDN 包目录同批"
    elif vs and cs:
        relation = "版本号晚于 CDN 包目录（需复核）"
    else:
        relation = "无法从状态文件比较"
    return {"version": version, "cdn_dir": cdn_dir, "revision": revision,
            "version_vs_cdn": relation}


def read_client(root: Path | str) -> dict:
    root = Path(root).resolve()
    info = classify_client(root)
    doc = root / "Documents"
    state = None
    state_path = doc / "local_state_314_lc"
    if state_path.is_file():
        try:
            with state_path.open("rb") as fh:
                state = pickle.load(fh)
        except Exception as exc:  # 状态文件异常不能阻断路径识别
            info["state_error"] = "%s: %s" % (type(exc).__name__, exc)
    summary = version_summary(state) if isinstance(state, dict) else {}
    update_version = None
    update = doc / "update.ini"
    if update.is_file():
        cp = configparser.ConfigParser()
        try:
            cp.read(update, encoding="utf-8")
            for sec in cp.sections():
                update_version = cp.get(sec, "version", fallback=update_version)
        except (OSError, configparser.Error):
            pass
    cloud = None
    cloud_path = doc / "cloud.json"
    if cloud_path.is_file():
        try:
            cloud = json.loads(cloud_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            pass
    info.update({"version": summary.get("version"),
                 "cdn_dir": summary.get("cdn_dir"),
                 "revision": summary.get("revision"),
                 "version_vs_cdn": summary.get("version_vs_cdn"),
                 "update_ini_version": update_version,
                 "cloud_combo_patch_dir": cloud.get("combo_patch_dir") if isinstance(cloud, dict) else None,
                 "state_path": str(state_path) if state_path.is_file() else None})
    return info


def _candidate_roots(explicit: Iterable[Path | str] | None = None) -> list[Path]:
    out: list[Path] = []
    def add(p: Path | str):
        p = Path(p).expanduser()
        if p not in out and p.is_dir():
            out.append(p)
    for value in explicit or ():
        add(value)
    if os.environ.get("LA_GAME_ROOT"):
        add(os.environ["LA_GAME_ROOT"])
    common = ("mrzh", "LifeAfter", "NetEase/Mrzh", "NetEase/LifeAfter")
    for letter in string.ascii_uppercase:
        drive = Path(f"{letter}:/")
        if drive.is_dir():
            for rel in common:
                add(drive / rel)
    return out


def discover_clients(*, roots: Iterable[Path | str] | None = None,
                     max_dirs: int = 3000, timeout: float = 5.0) -> list[dict]:
    """有限扫描客户端候选；结果按证据强度排序。"""
    started, seen, found = time.monotonic(), set(), []
    candidates = _candidate_roots(roots)
    # 显式/常见目录优先；只在每个磁盘根做有限深度扫描。
    for root in list(candidates):
        if time.monotonic() - started > timeout:
            break
        key = str(root.resolve()).lower()
        if key in seen:
            continue
        seen.add(key)
        info = read_client(root)
        if len(info["evidence"]) >= 2:
            found.append(info)
    for letter in string.ascii_uppercase:
        if time.monotonic() - started > timeout or len(seen) >= max_dirs:
            break
        drive = Path(f"{letter}:/")
        if not drive.is_dir():
            continue
        for base, dirs, files in os.walk(drive):
            if time.monotonic() - started > timeout or len(seen) >= max_dirs:
                break
            basep = Path(base)
            depth = len(basep.parts) - len(drive.parts)
            if depth > 3:
                dirs[:] = []
                continue
            dirs[:] = [d for d in dirs if d.lower() not in {"$recycle.bin", "system volume information", "windows", "programdata"}]
            if not ({"Documents", "lifeafter.exe", "mrzh_launcher.exe"} & set(files)) and "Documents" not in dirs:
                continue
            key = str(basep.resolve()).lower()
            if key in seen:
                continue
            seen.add(key)
            info = read_client(basep)
            if len(info["evidence"]) >= 2:
                found.append(info)
    unique = {x["root"].lower(): x for x in found}
    return sorted(unique.values(), key=lambda x: (-len(x["evidence"]), x["root"]))
