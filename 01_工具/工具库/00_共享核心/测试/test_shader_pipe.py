# -*- coding: utf-8 -*-
r"""`ccaa5566`（NeoX .pipe 编译着色器变体）解析契约测试。

★ 为什么要有这个文件：
   这个格式在项目里被反复误判过 —— 一度被当成「未解格式」扔进未识别，
   其实 2026-09-28 已实证是「自定义头 + 标准 DXBC」。这些断言把结论钉住。

★ 实测基线（400 文件 / 800 blob）：DXBC 100%，每文件 2 个（vertex + pixel）。
"""
import struct
import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1]
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import shader_pipe as SP  # noqa: E402

REAL_DIR = Path(r"E:/la拆包项目/03_执行/30_分析/热更交付_5目录_20260928/03_脚本与其他/着色器")
_samples = sorted(REAL_DIR.glob("*.ccaa5566"))[:30] if REAL_DIR.is_dir() else []
need_samples = pytest.mark.skipif(not _samples, reason="没有真实 .ccaa5566 样本")


# ── 魔数契约（★ 这里最容易错） ──────────────────────
def test_魔数是4字节二进制不是8字节ASCII():
    """★ 踩过的坑：把魔数写成 b"ccaa5566"（8 字节 ASCII）会一个都匹配不上。

    真实魔数只有 4 字节：cc aa 55 66。
    `.ccaa5566` 这个扩展名是我们按十六进制起的命名约定，不是游戏原生扩展名。
    """
    assert SP.MAGIC == b"\xcc\xaa\x55\x66"
    assert len(SP.MAGIC) == 4
    assert SP.is_pipe(b"\xcc\xaa\x55\x66" + b"\x00" * 40)
    assert not SP.is_pipe(b"ccaa5566" + b"\x00" * 40)


def test_头部布局常量():
    assert SP.HEADER_SIZE == 0x20
    assert SP.STAGE_NAME[0] == "vertex"
    assert SP.STAGE_NAME[1] == "pixel"
    assert SP.STAGE_NAME[2] == "compute"


# ── 真实样本 ────────────────────────────────────
@need_samples
def test_真实样本_头部自洽():
    for p in _samples[:10]:
        b = p.read_bytes()
        h = SP.parse_header(b)
        assert h["ok"], p
        assert h["version"] == 2
        assert h["f04"] == 2
        assert h["zeros_ok"], "0x10..0x1F 必须是 16 字节零填充：%s" % p.name


@need_samples
def test_真实样本_blob链精确走到EOF():
    """★ 核心判据：blob 个数无显式字段，靠链走到文件末尾（实测 300/300 精确自洽）。"""
    for p in _samples[:10]:
        b = p.read_bytes()
        blobs = SP.parse_blobs(b)
        assert blobs, p
        end = blobs[-1]["meta"]["offset"] + blobs[-1]["meta"]["size"]
        assert end == len(b), "%s：blob 链走到 %d，文件 %d，差 %d" % (
            p.name, end, len(b), len(b) - end)


@need_samples
def test_真实样本_blob是DXBC且恰好vs加ps():
    """实测基线：每文件 2 个 blob，阶段 0(vertex) + 1(pixel)，内层全 DXBC。"""
    for p in _samples[:10]:
        blobs = SP.parse_blobs(p.read_bytes())
        assert len(blobs) == 2, "%s 有 %d 个 blob" % (p.name, len(blobs))
        stages = [x["meta"]["stage"] for x in blobs]
        assert stages == [0, 1], "%s 阶段序列 %s" % (p.name, stages)
        for x in blobs:
            assert x["meta"]["is_dxbc"], "%s blob#%d 不是 DXBC" % (p.name, x["meta"]["index"])
            tags = [c["tag"] for c in x["meta"]["chunks"]]
            assert tags == ["RDEF", "ISGN", "OSGN", "SHEX", "STAT"], tags


@need_samples
def test_真实样本_chunk类型符合DXBC规范():
    b = SP.parse_blobs(_samples[0].read_bytes())[0]["blob"]
    d = SP.dxbc_info(b)
    assert d["chunk_count"] == 5
    assert all(c["name"] in SP.DXBC_CHUNKS.values() for c in d["chunks"])


# ── 分类契约 ────────────────────────────────────
def test_着色器不再落未识别():
    """★ 回归：曾把 10,733 个着色器全扔进 `04_脚本与其他/未识别`。"""
    from toolkit_core import hotfix_bundle as HB
    assert HB.O_SHADER == "着色器"
    assert HB.O_SHADER != HB.O_MISC
    assert HB.magic_class(b"\xcc\xaa\x55\x66") == "shader"


@need_samples
def test_导出只出dxbc不出原格式():
    """导出应以 .dxbc 为落地格式（原始 .ccaa5566 是容器，不是可用产物）。"""
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "o"
        files = SP.export(_samples[0], out)
        exts = {f.suffix for f in files}
        assert exts == {".dxbc"}, exts
        assert all(f.read_bytes()[:4] == b"DXBC" for f in files)
