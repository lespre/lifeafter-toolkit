# -*- coding: utf-8 -*-
"""新 GUI 核心的行为契约：先红后绿。"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.paths import DEFAULT_OUTPUT_ROOT, OutputPolicy
from toolkit_core.scheduler import JobKind, SmartScheduler
from toolkit_core.skin_chain import EvidenceLevel, SkinCatalog


def test_new_gui_prefills_the_unified_artifact_root():
    app_path = ROOT / "app.py"
    spec = importlib.util.spec_from_file_location("new_gui_under_test", app_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert module.DEFAULT_OUTPUT == DEFAULT_OUTPUT_ROOT


def test_core_backend_default_output_is_the_unified_artifact_root():
    backend_path = ROOT.parent / "01_核心解包器" / "lifeafter_unpacker_full.py"
    spec = importlib.util.spec_from_file_location("backend_under_test", backend_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert Path(module.UNPACK_DIR).resolve() == DEFAULT_OUTPUT_ROOT


def test_legacy_qt_gui_prefills_the_unified_artifact_root():
    legacy_path = ROOT.parent / "01_核心解包器" / "main_qt.py"
    spec = importlib.util.spec_from_file_location("legacy_gui_under_test", legacy_path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    assert Path(module.DEFAULT_OUTPUT_DIR).resolve() == DEFAULT_OUTPUT_ROOT


def test_default_output_policy_uses_unified_artifact_root(tmp_path: Path):
    source = tmp_path / "mrzh"
    source.mkdir()
    policy = OutputPolicy(exe_dir=tmp_path / "app")

    target = policy.resolve(None, source_root=source)

    assert DEFAULT_OUTPUT_ROOT == Path(r"E:/la拆包项目/03拆包产物").resolve()
    assert target == DEFAULT_OUTPUT_ROOT


def test_output_policy_never_uses_source_or_pyinstaller_temp(tmp_path: Path):
    exe_dir = tmp_path / "app"
    source = tmp_path / "mrzh" / "res"
    source.mkdir(parents=True)
    policy = OutputPolicy(exe_dir=exe_dir)

    target = policy.resolve(None, source_root=source)

    assert target == DEFAULT_OUTPUT_ROOT
    assert target.is_dir()
    assert source not in target.parents
    assert "_MEI" not in str(target)


def test_output_policy_rejects_output_inside_game_source(tmp_path: Path):
    source = tmp_path / "mrzh"
    source.mkdir()
    policy = OutputPolicy(exe_dir=tmp_path / "app")

    try:
        policy.resolve(source / "output", source_root=source)
    except ValueError as exc:
        assert "源目录" in str(exc)
    else:
        raise AssertionError("必须拒绝写入游戏源目录")


def test_scheduler_serializes_large_same_disk_archive_reads(tmp_path: Path):
    scheduler = SmartScheduler(cpu_count=20, cpu_percent=10, gpu_percent=10)
    plan = scheduler.plan([
        (JobKind.LARGE_ARCHIVE_READ, tmp_path / "res" / "001.fpk", tmp_path / "out"),
        (JobKind.LARGE_ARCHIVE_READ, tmp_path / "res" / "002.fpk", tmp_path / "out"),
        (JobKind.CPU_CONVERT, tmp_path / "res" / "a.dds", tmp_path / "out"),
    ])

    assert plan.max_cpu_workers == 16  # ≤ 80% of 20 cores
    assert plan.large_archive_workers == 1
    assert plan.convert_workers >= 1
    assert plan.cancel_supported is True


def test_scheduler_throttles_when_machine_is_busy(tmp_path: Path):
    scheduler = SmartScheduler(cpu_count=20, cpu_percent=86, gpu_percent=85)
    plan = scheduler.plan([(JobKind.CPU_CONVERT, tmp_path / "a.dds", tmp_path / "out")])

    assert plan.max_cpu_workers <= 8
    assert plan.convert_workers == 1


def test_catalog_import_preserves_unresolved_physical_boundary(tmp_path: Path):
    source = tmp_path / "behavior.json"
    source.write_text(
        '{"decoded_records":[{"skin_item_id":4448244,"weapon_kind_name":"霰弹枪",'
        '"unique_logical_skin_id_status":"VERIFIED_UNIQUE_DIRECT_PATH",'
        '"verified_unique_logical_skin_id":"skin_1006_001"}]}',
        encoding="utf-8",
    )
    catalog = SkinCatalog()
    catalog.import_behavior_chain(source)
    rows = catalog.search("4448244")

    assert len(rows) == 1
    assert rows[0].logical_skin_id == "skin_1006_001"
    assert rows[0].evidence_level is EvidenceLevel.DIRECT_LOGICAL_PATH
    assert rows[0].physical_status == "未建立路径→IDX hash桥，禁止绑定纹理预览"


def test_catalog_does_not_promote_unbound_preview_to_skin(tmp_path: Path):
    source = tmp_path / "physical.json"
    source.write_text(
        '{"result":{"skin_groups":109,"groups_with_verified_bound_previews":0,'
        '"unbound_weapon_preview_pool_count":93},"barrier":"no bridge"}',
        encoding="utf-8",
    )
    catalog = SkinCatalog()
    catalog.import_physical_summary(source)

    assert catalog.physical_summary["bound_preview_groups"] == 0
    assert catalog.physical_summary["unbound_preview_pool"] == 93
    assert catalog.can_bind_preview is False
