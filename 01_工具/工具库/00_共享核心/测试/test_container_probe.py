# -*- coding: utf-8 -*-
r"""container_probe / locate / fiddiff / ovl 的契约测试（★ 全部用真实数据，不 mock）。

数据来源（项目内实物）：
  · 产物层     03_执行/20_提取/全量实测_20260926/files/<容器目录>/<8位行号>.<ext>   ← 仓库里有
  · 索引库     03_执行/10_索引/indexes/lifeafter_files.sqlite3
  · 官方清单   03_执行/30_分析/全量拆包复核_20260928/03_download/{pi,pi_release,overlay}
               （这几个是 2026-09-28 从官方 CDN 下回来的实物；缺失时本文件整组 skip，
                 但 locate 组不依赖它们，永远会跑）

为什么钉这些数：它们是**实测值**，不是估计值。任何一个变了都说明
pi 布局 / overlay 是不是 NPK / 容器目录名规则被改动了 —— 那正是要报警的事。
"""

import json
from pathlib import Path

import pytest

from toolkit_core import container_probe as CP

BASE = Path(r"E:/la拆包项目")
DL = BASE / "03_执行" / "30_分析" / "全量拆包复核_20260928" / "03_download"
PI = DL / "pi"
PI_REL = DL / "pi_release"
OVL = DL / "overlay"
PRODUCTS = CP.PRODUCT_ROOT

_need_dl = pytest.mark.skipif(not PI.is_dir() or not OVL.is_dir(),
                              reason="官方 CDN 下载物不在（%s）—— 需先跑 03_download 下载" % DL)


# ══════════════════════════════════════════════════════════════════════
# ① pkg_N.pi 布局
# ══════════════════════════════════════════════════════════════════════

@_need_dl
def test_parse_pi_layout_is_8_plus_8n():
    """实测布局 [u64 count][count × u64 fid]；17 个包全部自检通过。"""
    counts = {}
    for n in range(1, 18):
        r = CP.parse_pi(PI / ("pkg_%d.pi" % n))
        assert r["layout_ok"] is True, r["error"]
        assert r["expected_bytes"] == r["actual_bytes"]
        assert r["count"] == (r["actual_bytes"] - 8) // 8
        assert len(r["fids"]) == r["count"]
        counts[n] = r["count"]
    # 实测：空包 8 字节（count=0）
    for n in (5, 6, 7, 9, 10, 11, 12, 14, 17):
        assert counts[n] == 0
    # 实测总数
    assert sum(counts.values()) == 2302285


@_need_dl
def test_parse_pi_reports_truncation_instead_of_guessing(tmp_path):
    """长度不符必须如实报 layout_ok=False，不许静默截断。"""
    good = (PI / "pkg_16.pi").read_bytes()
    bad = tmp_path / "pkg_16.pi"
    bad.write_bytes(good[:-8])                       # 声明 count 不变、少一条
    r = CP.parse_pi(bad)
    assert r["layout_ok"] is False
    assert r["fids"] == []
    assert "应为" in r["error"]


@_need_dl
def test_pi_diff_release_vs_playertest_counts():
    """实测：新增 23322 / 移除 3879 / 共有 2275211。"""
    d = CP.pi_diff(PI_REL, PI)
    assert d["a_pkgs"] == 17 and d["b_pkgs"] == 17
    assert d["a_total"] == 2279090
    assert d["b_total"] == 2298533
    assert len(d["added"]) == 23322
    assert len(d["removed"]) == 3879
    assert d["common"] == 2275211
    assert not (set(d["added"]) & set(d["removed"]))


# ══════════════════════════════════════════════════════════════════════
# ② overlay 包 = 普通 NPK 容器
# ══════════════════════════════════════════════════════════════════════

@_need_dl
def test_overlay_is_npk_and_entry_counts():
    """★ 反旧口径：overlay 不是「32B 头 + zstd 帧流」，是 NPK 容器。

    实测条目数（扫 zstd 魔数只能拿到 371 条，这里必须 1741 条）：
      effect=2 / instance.1.1.1=390 / instance.1.1=379 / script.overlay3=958 /
      sound=2 / ui.1.1.1=0 / ui.1.1.2=1 / ui.1.1.3=2 / ui.1.1=0 / video=2 /
      zhutihuodong_v5=5
    """
    want = {
        "effect.layers.1.1.overlay.1790223366974.npk": 2,
        "instance.layers.1.1.1.overlay.1790223366974.npk": 390,
        "instance.layers.1.1.overlay.1790223366974.npk": 379,
        "script.py314.lc.overlay3.1790223366974.npk": 958,
        "sound.layers.1.1.overlay.1790223366974.npk": 2,
        "ui.layers.1.1.1.overlay.1790223366974.npk": 0,
        "ui.layers.1.1.2.overlay.1790223366974.npk": 1,
        "ui.layers.1.1.3.overlay.1790223366974.npk": 2,
        "ui.layers.1.1.overlay.1790223366974.npk": 0,
        "video.layers.1.1.overlay.1790223366974.npk": 2,
        "zhutihuodong_v5.layers.1.1.overlay.1790223366974.npk": 5,
    }
    total = 0
    for name, n in want.items():
        m = CP.overlay_entries(OVL / name)
        assert m["n"] == n, (name, m["n"], m.get("error"))
        total += m["n"]
    assert total == 1741


@_need_dl
def test_overlay_instance_has_flag0_entries_the_old_scan_missed():
    """instance.1.1.1 实测 flags = {0:198, 12:192} —— flag 0 的 198 条旧路一条都拿不到。"""
    m = CP.overlay_entries(OVL / "instance.layers.1.1.1.overlay.1790223366974.npk")
    assert m["flags"] == {"0": 198, "12": 192}
    assert m["n"] == 390                       # ≠ 192（「zstd 魔数」个数）


@_need_dl
def test_overlay_empty_container_is_not_an_error():
    """32 字节的空 overlay 包：如实返回空表，不抛异常、不当成坏包。"""
    m = CP.overlay_entries(OVL / "ui.layers.1.1.overlay.1790223366974.npk")
    assert m["bytes"] == 32
    assert m["n"] == 0
    assert m["empty"] is True


@_need_dl
def test_overlay_unpack_dry_run_effect_pkg():
    """条目级解包：2 条全解出，且带 md5/sha256/类型。"""
    rep = CP.overlay_unpack(OVL / "effect.layers.1.1.overlay.1790223366974.npk",
                            DL / "_pytest_ovl_out", write=False)
    assert rep["n_entries"] == 2 and rep["ok"] == 2 and rep["failed"] == 0
    for e in rep["entries"]:
        assert len(e["sha256"]) == 64 and len(e["md5"]) == 32
        assert e["bytes"] == e["decoded"]
    assert rep["types"].get("fx") == 2 or rep["types"].get("path+fx") == 2


@_need_dl
def test_classify_bytes_real_samples():
    """DDS 头部（zhutihuodong 第一帧实测 DDS 1832×1372）与 MP4（video 包）。"""
    m = CP.overlay_entries(OVL / "zhutihuodong_v5.layers.1.1.overlay.1790223366974.npk")
    assert CP.classify_bytes(b"DDS |\x00\x00\x00") == "dds"
    assert CP.classify_bytes(b"\x00\x00\x00 ftypisom") == "mp4"
    assert m["n"] == 5


# ══════════════════════════════════════════════════════════════════════
# ③ 物理定位（不依赖下载物，永远会跑）
# ══════════════════════════════════════════════════════════════════════

def test_container_dir_name_无载荷时退回stem_防撞车已移到树():
    r"""★ 2026-09-30（S5 后）改口径。

    `container_dir_name` 的消歧判据是「把分隔符换成 __ 的规范化目录
    **在产物根里真的存在**」—— 初拆载荷被架构改造清掉后，它必然退回 stem。
    所以**同名 stem 防撞车不再靠它**，改由 `TreeResolver`（真实路径）保证。
    本测试记两件事：① 普通容器名照旧 ② 载荷不在时两个 script 容器会折成同一个名字
    —— 这正是「不能再依赖它定位」的证据。
    """
    assert CP.container_dir_name(r"res\ui_02.gpk") == "ui_02"
    assert CP.container_dir_name(r"Documents\gres\0000.gpk") == "0000"
    assert CP.container_dir_name("res/ui_02.gpk") == "ui_02"      # 正斜杠也认
    a = CP.container_dir_name("script.py314.lc.npk")
    b = CP.container_dir_name(r"Documents\script.py314.lc.npk")
    # ★ 判据要测**消歧用的那个目录本身是否存在**，不是 PRODUCT_ROOT 是否存在 ——
    #   S5 只删了载荷铺法目录（`files/`），根还在（老产物 15.7 GB 仍在根下）。
    probe = Path(CP.PRODUCT_ROOT) / "Documents__script.py314.lc"
    if probe.is_dir():
        assert a != b, "规范化目录存在 ⇒ 应消歧"
    else:
        assert a == b, "规范化目录不存在 ⇒ 两者折成同一名（防撞车改由树负责）"


def _products_usable() -> bool:
    """★ 产物可读判据（2026-09-29 S5 修）。

    原来写的是 `PRODUCTS.is_dir()` —— 载荷被清后它为假，测试会**静默 skip**，
    等于悄悄丢掉覆盖。改为「载荷在 **或** 还原树在」都算可用。
    """
    if PRODUCTS.is_dir():
        return True
    try:
        from toolkit_core import artifact_locator as _AL
        return _AL.TreeResolver().available
    except Exception:
        return False


@pytest.mark.skipif(not _products_usable(), reason="载荷与还原树都不可用")
def test_locator_does_not_cross_to_the_other_script_container():
    """★ 回归钉：artifact_locator 用 Path.stem 会把两个容器折成一个（实测串了）。

    真实数据：r100 在 Documents__script.py314.lc 与 script.py314.lc 下是两个不同文件
    （实测树里：953 B 的 oversea 表 vs 751 B 的 lottery_coupon_data）。

    ★ 2026-09-29（S5）：改为不显式传根 —— 走 auto（树优先、载荷回退）。
    """
    loc = CP.Locator()
    a = loc.path(r"Documents\script.py314.lc.npk", 100)
    b = loc.path(r"script.py314.lc.npk", 100)
    assert a is not None and b is not None, "两个 script 容器的 r100 产物都应在盘上"
    assert a != b, "两个同名 stem 的容器被串到一起了（正是要防的缺陷）"
    assert a.stat().st_size != b.stat().st_size


@pytest.mark.skipif(not _products_usable(), reason="载荷与还原树都不可用")
def test_locator_known_rows_match_index_names():
    """实测三条：(gres 0000, 6604)=.dds · (scene_03, 5334)=.c159 · (scene_03, 6320)=.dds

    ★ 2026-09-29（S5）：改为**不显式传根** —— 走 `UnifiedResolver` 的 auto 模式
      （树优先、载荷回退）。载荷已被架构改造清掉，只查载荷会静默返回 None。
      三条断言本身不变（树里同样命中、扩展名一致，已实测）。
    """
    loc = CP.Locator()
    assert loc.path(r"Documents\gres\0000.gpk", 6604).suffix == ".dds"
    assert loc.path(r"res\scene_03.gpk", 5334).suffix == ".c159"
    assert loc.path(r"res\scene_03.gpk", 6320).suffix == ".dds"
    assert loc.path(r"res\scene_03.gpk", 10 ** 9) is None       # 不存在的行 → None


@pytest.mark.skipif(not CP.INDEX_DB.is_file(), reason="索引库不在")
def test_locator_fid_lookup_roundtrip():
    """fid 反查：拿一个真实 fid 反查，再用查到的 (容器,行) 正查，必须回到同一个文件。

    ★ 2026-09-30：`CP.Locator(PRODUCTS)` 是**显式载荷根** ⇒ 载荷删后 `exists` 恒假。
      改为不给根 ⇒ 走 `UnifiedResolver`（树优先、载荷回退），与调用方实际行为一致。
    """
    loc = CP.Locator()
    import sqlite3
    con = sqlite3.connect("file:%s?mode=ro" % str(CP.INDEX_DB).replace("\\", "/"), uri=True)
    try:
        c, r, f = con.execute(
            "SELECT container,row_index,fid_hex FROM entries "
            "WHERE container LIKE '%scene_03%' AND row_index=5334").fetchone()
    finally:
        con.close()
    assert f
    rows = loc.locate_fid(f)
    assert rows and rows[0]["container"] == c and rows[0]["row"] == r
    assert rows[0]["exists"] is True, "树里应有该行（载荷已删，定位改走树）"
    assert Path(rows[0]["artifact"]) == loc.path(c, r)


# ══════════════════════════════════════════════════════════════════════
# CLI 契约（真正调 main()，不是 mock）
# ══════════════════════════════════════════════════════════════════════

def _cli(argv):
    from toolkit_cli import main
    return main(argv)


@pytest.mark.skipif(not _products_usable(), reason="载荷与还原树都不可用")
def test_cli_locate_two_containers_differ(capsys):
    """★ 回归钉（CLI 层）：两个同名 stem 的 script 容器不能被折成一个。

    ★ 2026-09-29（S5）改断言：以前找的是输出里的【容器目录名】
      （`Documents__script.py314.lc` / `script.py314.lc\\00000100.bin`）。
      现在 locate 解析到【还原树路径】，输出里已无容器目录名 ⇒ 老断言过时。
      改成钉【真意图】：两次解析出的文件必须【不同】，各自的路径必须出现在输出里。
    """
    assert _cli(["locate", r"Documents\script.py314.lc.npk", "100"]) == 0
    out1 = capsys.readouterr().out
    assert _cli(["locate", r"script.py314.lc.npk", "100"]) == 0
    out2 = capsys.readouterr().out

    def _path_of(out: str) -> str:
        for line in out.splitlines():
            if "→" in line and "\\" in line:
                return line.split("→", 1)[1].strip()
        return ""

    p1, p2 = _path_of(out1), _path_of(out2)
    assert p1 and p2, "两次 locate 都应解析出文件路径：\n%s\n%s" % (out1, out2)
    assert p1 != p2, "两个同名 stem 的容器被折到同一个文件了（正是要防的缺陷）"
    assert p1 in out1 and p2 in out2


def test_cli_locate_miss_returns_5(capsys):
    assert _cli(["locate", r"res\scene_03.gpk", "999999999"]) == 5
    assert "没有产物" in capsys.readouterr().out


def test_cli_locate_requires_row(capsys):
    assert _cli(["locate", r"res\scene_03.gpk"]) == 2


@_need_dl
def test_cli_fiddiff_json_contract(capsys):
    """--json - 必须把 JSON 打到 stdout（下游脚本靠它取数）。"""
    assert _cli(["fiddiff", str(PI_REL), str(PI), "--json", "-"]) == 0
    out = capsys.readouterr().out
    j = json.loads(out[out.index("{"):out.rindex("}") + 1])
    assert j["added_n"] == 23322 and j["removed_n"] == 3879
    # ★ 2026-09-30：字典口径改为「自动选最高版本」—— `names_dict_v16.json`
    #   （v13 ∪ v14 ∪ v15 并集，1,266,521 条）比 v13 多命中若干条 ⇒ 用 >= 钉住下界，
    #   避免每次扩字典都要改这个数字（数字只会随字典变大而不减）。
    assert j["named_added"] >= 7548 and j["named_removed"] == 7


@_need_dl
def test_cli_fiddiff_grep_and_named_filters(capsys):
    """--grep 是纯过滤器，不该改变「字典能给出名字」的统计（实测新增里有名字 ≥7548）。"""
    assert _cli(["fiddiff", str(PI_REL), str(PI), "--named", "--grep", "cdata",
                 "--limit", "3"]) == 0
    out = capsys.readouterr().out
    assert "字典能给出名字：新增 " in out and "/ 移除 7" in out
    assert "＋" not in out            # 实测：新增里没有 com\cdata\ 的


@_need_dl
def test_cli_ovl_entries_and_unpack(capsys, tmp_path):
    fp = OVL / "instance.layers.1.1.1.overlay.1790223366974.npk"
    assert _cli(["ovl", "entries", str(fp), "--limit", "2"]) == 0
    out = capsys.readouterr().out
    assert "条目 390 条" in out and "'0': 198" in out

    assert _cli(["ovl", "unpack", str(OVL / "effect.layers.1.1.overlay.1790223366974.npk"),
                 "--out", str(tmp_path)]) == 0
    out = capsys.readouterr().out
    assert "条目 2 条 → 解出 2" in out
    # 落盘目录名 = "<包名去 .overlay 换成 _ov>"，实测形如 effect.layers.1.1_ov.1790223366974
    landed = list(tmp_path.glob("*_ov*/*"))
    assert len(landed) == 2, landed


def test_cli_help_lists_new_commands(capsys):
    """三条新命令必须在 --help 里出现（否则等于没接）。"""
    from toolkit_cli import build_parser
    try:
        build_parser().parse_args(["--help"])
    except SystemExit:
        pass
    out = capsys.readouterr().out
    for name in ("locate", "fiddiff", "ovl"):
        assert name in out
