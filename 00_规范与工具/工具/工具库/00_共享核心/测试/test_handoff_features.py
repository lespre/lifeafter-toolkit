# -*- coding: utf-8 -*-
"""交接包自检、客户端发现、空间预估与热更计划契约测试。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.client_discovery import classify_client, version_summary
from toolkit_core.storage_estimate import estimate_storage
from toolkit_core.hotfix_plan import build_hotfix_plan


def test_classify_playertest_without_path_guessing():
    got = classify_client(
        Path(r"E:\Games\mrzh"),
        markers={"download_playertest_patch": True,
                 "local_state_314_lc": True,
                 "lifeafter.exe": True},
    )
    assert got["line"] == "playertest"
    assert got["server_kind"] == "测试服"
    assert got["safe_for_experience_source"] is True


def test_classify_formal_is_not_experience_source():
    got = classify_client(
        Path(r"D:\Games\LifeAfter"),
        markers={"local_state_314_lc": True, "lifeafter.exe": True},
    )
    assert got["line"] == "release"
    assert got["server_kind"] == "正式服"
    assert got["safe_for_experience_source"] is False


def test_version_summary_distinguishes_version_and_cdn_directory():
    state = {
        "version_info": {
            "version": "20260923_164313_playertest_newpc",
            "revision": 5748977,
            "cloud_dir_name": "release_playertest_newpc",
            "pkg_lst": {"name": "20260929_172554_playertest_newpc/pkg_lst.pl"},
        }
    }
    got = version_summary(state)
    assert got["version"] == "20260923_164313_playertest_newpc"
    assert got["cdn_dir"] == "20260929_172554_playertest_newpc"
    assert got["version_vs_cdn"] == "版本号早于 CDN 包目录"


def test_storage_estimate_reports_insufficient_space():
    got = estimate_storage(
        source_bytes=10 * 1024**3,
        decoded_bytes=20 * 1024**3,
        index_bytes=2 * 1024**3,
        temp_bytes=5 * 1024**3,
        free_bytes=30 * 1024**3,
    )
    assert got["required_bytes"] >= 37 * 1024**3
    assert got["enough"] is False
    assert got["verdict"] == "空间不足"


def test_hotfix_plan_combines_overlay_and_fid_diff():
    got = build_hotfix_plan(
        client_root=r"E:\Games\mrzh",
        version={"version": "v1", "cdn_dir": "d1"},
        overlay_packages=[{"name": "ui.overlay.npk", "size": 100}],
        pkg_diff={"added": ["A", "B"], "removed": ["C"], "changed": ["D"]},
    )
    assert got["scope"] == "hotfix"
    assert got["overlay"]["package_count"] == 1
    assert got["fid_diff"] == {"added": 2, "removed": 1, "changed": 1}
    assert got["requires_full_tree"] is False
