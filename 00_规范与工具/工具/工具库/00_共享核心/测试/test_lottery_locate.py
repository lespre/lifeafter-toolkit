# -*- coding: utf-8 -*-
r"""奖池定位 / 概率公示 / 回填门禁 —— 契约测试。

钉的是 2026-09-30 修的三处**真缺陷**（每处都先量了再修）：
  ① `lottery prob 幻夜` 报「没匹配」——公示块判据只认名字含「奖池/抽奖/转盘」，
     而幻夜在官方公示里叫【神谕童话概率公示】⇒ 整块被跳过。
  ② `lottery locate 幻夜` 只报 1 张 `_chs`、id 命中 0 —— 扫描只有 `com\cdata\*.py`
     顶层，漏 `oversea/` 下 18,666 张（渠道真表都在那里）；且中文只在 `_chs` 池里，
     命中没归位到 base 表；且帧内整数是 LEB128 varint，字节搜必然假阴性。
  ③ 回填无门禁 —— `common_item` 38,070 条只有 27.6% 可用（其余是长句/icon
     路径/重名），原来「查不到就退 common_item」= 把未核名字当结论。
"""
from __future__ import annotations

import pytest
from toolkit_core import common_item_names as CI
from toolkit_core import lottery_chain as LC
from toolkit_core import lottery_locate as LL
from toolkit_core import paths as P

# ★ 2026-10-01 层级对标 E:\mrzh 后：配置表在 <树>/<容器>/com/cdata/…，
#   老扁平 <树>/com/cdata 已不存在 ⇒ 判据改走【表定位链】（与 CLI 同一条），
#   否则测试会静默 skip（把「布局变了」伪装成「没数据」）。
TREE_CD = P.cdata_dir()          # = <树>/Documents/script.py314.lc.npk/com/cdata


def _cli(argv):
    from toolkit_cli import main
    return main(argv)


def _tree_ok() -> bool:
    try:
        return P.cdata_table("desc_info_data_chs.py").is_file()
    except Exception:
        return False


need_tree = pytest.mark.skipif(not _tree_ok(),
                               reason="还原树里定位不到配置表（层级/表定位链不可用）")
need_ci = pytest.mark.skipif(not CI.stats()["exists"], reason="common_item 索引没建")


# ── ① 概率公示：判据以结构为准 ───────────────────────────────
@need_tree
def test_公示块判据能抓到神谕童话且老判据抓不到():
    dp = LL.desc_info_path()
    assert dp and dp.is_file(), "desc_info_data_chs.py 定位失败"
    names = [b["name"] for b in LL.prob_blocks(dp)]
    assert "神谕童话概率公示" in names, "幻夜神谕的官方公示块没抓到"
    # 老判据（只认 奖池/抽奖/转盘）对这个名字恒 False —— 这就是当初漏的真因
    assert not any(k in "神谕童话概率公示" for k in ("奖池", "抽奖", "转盘"))
    # 结构判据应把 秘宝概率公示 一批也收进来（≥20 块）
    assert len(names) >= 20, "结构判据收得太少：%d 块" % len(names)
    assert any("秘宝概率公示" in n for n in names), "秘宝概率公示 一批仍漏"


@need_tree
def test_公示别名_幻夜神谕映射到神谕童话():
    assert "神谕童话" in LL.prob_alias("幻夜")
    assert "神谕童话" in LL.prob_alias("幻夜神谕")
    blocks = LL.prob_match(LL.desc_info_path(), "幻夜")
    assert len(blocks) == 1 and blocks[0]["name"] == "神谕童话概率公示"
    assert len(blocks[0]["entries"]) == 8
    total = sum(float(p.rstrip("%")) for _i, _n, p in blocks[0]["entries"])
    assert 99.9 < total < 100.1, "公示概率合计应 ≈100%%，实际 %.3f" % total


# ── ② locate：覆盖 oversea 渠道表 + 活动表(L1) + 解码档 id 命中 ──
@need_tree
def test_locate扫到oversea渠道表并标出渠道():
    out = LL.scan_systems({139353, 633170140}, TREE_CD, keyword="幻夜")
    rels = [s.get("rel") or "" for s in out]
    assert any(r.startswith("oversea/") for r in rels), \
        "oversea/ 下的渠道真表没被扫到（老实现只 glob 顶层）"
    chans = {s.get("channel") for s in out if s.get("channel")}
    assert {"kj1", "kjxq"} <= chans, "渠道号没解出来：%s" % chans
    # 中文只存在于 _chs 池 ⇒ 命中必须归位到 base 表，否则永远只看到 _chs
    assert any(r.endswith(".py") and not r.endswith("_chs.py") for r in rels), \
        "命中没归位到 base 表"


@need_tree
def test_locate扫到活动表L1_红尘剑仙():
    """活动表（huodong_conf_data*）是池的上游 —— 不扫就会报「0 张表」假阴性。"""
    out = LL.scan_systems(set(), TREE_CD, keyword="红尘剑仙")
    assert any("huodong" in (s.get("rel") or "").lower() for s in out), \
        "L1 活动表没进扫描范围：%s" % [s.get("rel") for s in out]


@need_tree
def test_locate_id命中走解码而非字节搜():
    """帧内整数是 LEB128 varint ⇒ 字节搜恒 0。命中必须标 id_via=解码。"""
    out = LL.scan_systems({139353, 633170140}, TREE_CD, keyword="幻夜")
    dec = [s for s in out if s.get("id_via") == "解码"]
    assert dec, "没有任何「解码档」命中（说明 decoded_ids 没跑或又被吞异常）"
    assert any(139353 in (s.get("hit_ids") or []) for s in dec)


@need_tree
def test_decoded_ids能解出跳转组里的展示大奖():
    f = TREE_CD / "oversea" / "super_fashion_lottery_conf_data_auto_oversea_data_kj1.py"
    if not f.is_file():
        pytest.skip("kj1 渠道表不在")
    got = LL.decoded_ids(f)
    assert {139353, 633170140} <= got, "解码档没拿到展示大奖：%s" % sorted(got)[:20]


# ── ③ 回填门禁：只有 usable 能进交付名字 ─────────────────────
@need_ci
def test_common_item索引存在且可用率是少数():
    st = CI.stats()
    assert st["count"] > 30000
    assert 0 < st["usable"] < st["count"], "可用率不应是 0 或 100%（体检：27.6%）"
    assert st["usable"] == 10517 or st["usable"] > 8000, \
        "可用条数异常（体检值 10,517）：%d" % st["usable"]


@need_ci
def test_usable_names排除重名与bad值():
    names = CI.usable_names()
    assert names, "可用名字集不能为空"
    meta = CI.lookup_meta_all()
    assert all(meta[i]["quality"] == "ok" and not meta[i]["dup"] for i in names)
    # 已知取错槽的样本必须被排除
    assert 150004 not in names or meta[150004]["dup"], "重名项漏进门禁"
    assert not any("ui/" in v for v in names.values()), "icon 路径漏进门禁"


def test_apply_names的common_item门禁与标签():
    """门禁必须在 apply_names 生效：标签是 common_item(ok)，且报收/拒计数。"""
    rep = {"rows": [{"show_items": [139353, 633170140, 570124]}]}
    LC.apply_names(rep, verbose=False)
    vias = {s.get("via") for s in rep["rows"][0]["show_names"]}
    assert "common_item" not in vias, "老的无限定标签还在（会误导成已核）"
    assert all(v is None or v.startswith(("csv:", "ns:", "common_item(ok)"))
               for v in vias), "出现未预期的来源标签：%s" % vias
    g = rep.get("common_item_gate")
    assert g and g["accepted"] + g["rejected"] >= 0 and "why" in g


# ── CLI 层：命令真的能跑通 ──────────────────────────────────
@need_tree
def test_cli_lottery_prob幻夜(capsys):
    assert _cli(["lottery", "prob", "幻夜"]) == 0
    out = capsys.readouterr().out
    assert "神谕童话概率公示" in out and "幻夜" in out


@need_ci
def test_cli_names_common_item带可信度(capsys):
    assert _cli(["names", "items", "lookup", "--ns", "common_item", "570124"]) == 0
    out = capsys.readouterr().out
    assert "工作副本专用链" in out and "候选" in out


# ── ④ 展示大奖名字表直解（补 CSV 只覆盖 180 张的缺口）───────────
def _sn():
    """★ 用户口径：「这几个玩意早就热更来了，肯定是你方法还有问题」——
    对：不是数据没有，是名字源只认 `表结构解析_*/结构/*.rows.csv` 那 180 张，
    而 741470120（星穹环冕）在 `player_module_appear_data` 里（CSV 没覆盖）。
    """
    from toolkit_core import show_item_names as SN
    return SN


def test_show_item_names直解树里的名字表():
    SN = _sn()
    if not SN.stats().get("exists"):
        SN.build(verbose=False)
    hits = SN.lookup([139353, 633170140, 741470120])
    assert 139353 in hits and hits[139353][0][0] == "幻夜神谕典藏礼盒"
    assert 633170140 in hits and hits[633170140][0][0] == "幻夜星轮"
    assert 741470120 in hits, "头饰（星穹环冕）没解出来 —— 名字源又缺表了"
    assert hits[741470120][0][0] == "星穹环冕"
    assert "player_module_appear_data" in hits[741470120][0][1]
    st = SN.stats()
    assert sum((st.get("tables") or {}).values()) >= 15000, \
        "直解到的名字总量太少：%s" % st.get("tables")


def test_apply_names会用直解源补名字():
    rep = {"rows": [{"show_items": [741470120]}]}
    LC.apply_names(rep, verbose=False)
    rec = rep["rows"][0]["show_names"][0]
    assert rec["name"] == "星穹环冕", "直解源没接进回填链：%s" % rec
    assert str(rec["via"]).startswith("tree:"), rec["via"]


# ── 活动桥接（extra_param ←→ 抽奖配置 key）────────────────────
@need_tree
def test_活动桥接_幻夜233对到活动3610():
    """★ 桥 = 活动行 `extra_param` ←→ 抽奖配置 key。

    实测：`huodong_conf_data`(kj1) key=**3610**（幻夜神谕）的 extra_param = **233**
    = `super_fashion_lottery_conf_data` 的行 key ⇒ 用它把
    「抽奖配置 → 活动号 → 静态展示道具（9 件）」串起来。
    """
    bridge = LC.hd_bridge()
    assert 233 in bridge, "233 没在活动桥里"
    cands = bridge[233]
    assert any(str(c["hd_key"]) == "3610" for c in cands), \
        "233 应对上活动号 3610：%s" % cands
    one = next(c for c in cands if str(c["hd_key"]) == "3610")
    assert one["hd_name"] == "幻夜神谕", one
    assert one["hd_class"] == "DragonBlessingLotteryHD", one


@need_tree
def test_静态展示道具_活动3610九件():
    st = LC.hd_show_items()
    ids = st.get("3610") or []
    assert len(ids) == 9, "幻夜静态展示道具应为 9 件：%s" % ids
    for x in (139353, 633170140, 1110185, 741470120, 660076, 660060):
        assert x in ids, "%d 不在静态展示道具里" % x


@need_tree
def test_attach_hd_给幻夜行补活动与静态道具():
    rep = {"rows": [{"table": "super_fashion_lottery_conf_data.py", "key": 233,
                     "show_items": [139353, 633170140, 1110185, 741470120]}]}
    LC.attach_hd(rep, verbose=False)
    hd = rep["rows"][0]["hd"]
    assert hd and str(hd["hd_key"]) == "3610" and hd["hd_name"] == "幻夜神谕", hd
    assert hd["n_static"] == 9 and hd["n_panel"] == 4, hd
    names = {it["id"]: it["name"] for it in hd["static_show_names"]}
    assert names.get(139353) == "幻夜神谕典藏礼盒"
    assert names.get(741470120) == "星穹环冕"
    assert names.get(660060) == "异变核芯-贯通战术"


def test_csv名字缓存生效():
    """★ 回归钉：`_csv_names()` 必须走缓存，否则 attach_hd 每行都重扫 101 个 CSV
    （实测 217 行 ≈ 60 秒 → 缓存后秒级）。"""
    a = LC._csv_names()
    b = LC._csv_names()
    assert a is b, "第二次调用返回了新对象 —— 缓存没生效（性能会退化到分钟级）"


# ── common_item 必须走 fid 定位且 Documents 副本优先 ────────────────
@need_ci
def test_奇迹_1110185从common_item解出():
    """★ 用户当场纠正：「1110185 是奇迹，你武器皮肤 wiki 都更新上去了」。

    根因（我的错）：同名表在树里有**两份副本、内容不同** ——
      · `Documents\\script.py314.lc.npk` 副本（客户端当前态）55,615 行 → **有** 1110185=奇迹
      · `script.py314.lc.npk` 根包副本 55,408 行 → **没有**这两行
    我原来按「快照 + entry 号」读 config_work 老快照（≈根包态）⇒ 热更新增的道具名全丢，
    把真实存在的「奇迹」报成「无名字」。正解：**按 fid 定位 + Documents 副本优先**。
    """
    from toolkit_core import common_item_names as CI
    rec = CI.lookup_meta([1110185]).get(1110185)
    assert rec and rec.get("name") == "奇迹", "1110185 应解出「奇迹」：%s" % rec
    rec2 = CI.lookup_meta([1110186]).get(1110186)
    assert rec2 and rec2.get("name") == "星辰刀", "1110186 应解出「星辰刀」：%s" % rec2


@need_ci
def test_common_item按fid定位且优先Documents副本():
    from toolkit_core import common_item_names as CI
    r = CI.resolve_by_fid(CI.FID_BASE)
    assert r, "按 fid 没定位到 common_item_data_base"
    path, container, row, decoded = r
    assert "Documents" in container, \
        "应优先 Documents 副本（客户端当前态），实际拿到 %s" % container
    from pathlib import Path as _Path
    assert _Path(path).is_file(), "树里应真有这个文件：%s" % path
    # ★ 2026-09-30：**别再断言具体行号** —— 索引重建会让无名文件的行号位移
    #   （实测该 fid 的 Documents 副本行号 19141 → 19192），写死行号会假红。
    #   断言「落在 Documents 容器目录下 + 带容器分区」即可。
    assert "Documents" in str(path), "应落到 Documents（overlay）层：%s" % path
    assert "script.py314.lc.npk" in str(path), "路径应带容器分区：%s" % path


# ── ⑤ 活动展示道具（★ 键是活动号，不是池号）──────────────────
@need_tree
def test_活动展示道具表按活动号取到幻夜九件():
    """★ 用户 2026-09-30 当场纠正：池成员别按 pool id 找（0 命中），要按【活动号】。

    `common_hd_show_reward_data` 行 key = 活动号（幻夜 = 3610），值 `show_item_ids` =
    展示道具列表。实测 9 件，含全部 4 件 panel_show_item_ids。
    """
    from toolkit_core import lottery_chain as _LC
    cd = _LC.tree_cdata()
    p = cd / "common_hd_show_reward_data.py"
    if not p.is_file():
        pytest.skip("表不在")
    M = _LC._mods()
    import struct as _st
    fr, b = _LC._frame(p)
    assert fr, "common_hd_show_reward_data 应有合法帧"
    body = b[fr[0] + 6: fr[0] + 6 + fr[1]]
    cnt, _ = _st.unpack_from("<II", body, 0)
    blob = body[8 + 4 * cnt:]
    chs = cd / "common_hd_show_reward_data_chs.py"
    pool = M["MP"].pool_of_file(str(chs)) if chs.is_file() else []
    rows, _u = M["BP"].decode_table_rows_with_chs_slots(body, pool)
    assert len(rows) >= 30, "这张表应有 30+ 个活动（实测 36）"
    row = next((r for r in rows if str(r.get("key")) == "3610"), None)
    assert row is not None, "表里没有活动号 3610（幻夜神谕）"
    v = row.get("values") or {}
    g = v.get("show_item_ids")
    g = g[1] if isinstance(g, (list, tuple)) and len(g) > 1 else g
    ids = M["BT"].resolve_jump_group(blob, int(str(g).split(":")[1])) or []
    assert len(ids) == 9, "幻夜展示道具应为 9 件，实际 %d：%s" % (len(ids), ids)
    # 4 件 panel_show_item_ids 必须都在里面
    for x in (139353, 633170140, 1110185, 741470120):
        assert x in ids, "panel_show_item_ids 的 %d 不在展示道具里" % x


@need_ci
def test_占位词不当名字():
    """★ 皮肤 1110185 在特效表里的 sfx_name 是占位词「真实」—— 不能当名字交出去。"""
    SN = _sn()
    if not SN.stats().get("exists"):
        SN.build(verbose=False)
    hits = SN.lookup([1110185])
    if 1110185 in hits:
        assert hits[1110185][0][0] != "真实", "占位词漏进门禁：%s" % hits[1110185]
