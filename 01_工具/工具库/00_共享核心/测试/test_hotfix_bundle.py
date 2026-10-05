# -*- coding: utf-8 -*-
r"""hotfix bundle 交付结构的契约测试。

★ 为什么要有这个文件：
   实现过程中连续出现三次「缺 import → NameError → 静默半途而废」：
     · hotfix_bundle 里缺 `import json`  → 磁盘缓存静默失效（142s 不降）
     · toolkit_cli 里缺 `import shutil`  → 报告归类失败，还带崩后面的文字表写入
     · toolkit_cli 里缺 `import sqlite3` → 02_文字表 直接 0 产出
   所以这里用真实数据把「交付结构必须成立」钉成断言。

★ 性能纪律：**不要在测试里列真实大目录**；只用小样本 + 结构断言。
"""
import json
import sys
from pathlib import Path

import pytest

CORE = Path(__file__).resolve().parents[1]
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import hotfix_bundle as HB  # noqa: E402

REAL_OUT = Path(r"E:/la拆包项目/03_执行/30_分析/热更交付_5目录_20260928")
need_out = pytest.mark.skipif(not REAL_OUT.is_dir(), reason="交付目录不存在")


# ── 结构契约（不依赖真实数据） ─────────────────────────────
def test_四个顶层目录名固定():
    """★ 用户口径（2026-09-29 S4 改）：交付 4 个顶层，**不含还原树**。

    为什么去掉还原树：热更不再单独产还原树 —— 它改为在全量还原树上「增增补补」
    （`hotfix apply`），交付只给「变了什么」的可读视图。
    """
    assert HB.D_TEXT == "01_文字表"
    assert HB.D_MEDIA == "02_媒体文件"
    assert HB.D_OTHER == "03_脚本与其他"
    assert HB.D_DELTA == "04_变更清单与报告总结"


def test_交付不含还原树():
    """★ 反向断言：D_TREE 必须为空，且不在 TOP_DIRS 里。

    回归背景：曾把 `01_还原树` 当交付顶层之一（5 目录口径）；
    改口径后若还有人往交付里铺树，这条会立刻红。
    """
    assert HB.D_TREE == "", "D_TREE 已弃用，必须为空字符串"
    assert HB.D_TREE not in HB.TOP_DIRS
    assert len(HB.TOP_DIRS) == 4
    assert not any("还原树" in d for d in HB.TOP_DIRS), "交付顶层不应出现还原树"


def test_图片分类三级路径常量齐备():
    assert HB.M_IMG == "图片"
    assert HB.M_IMG_R == "能看的图"
    assert HB.M_IMG_M == "看不懂的"
    assert HB.M_VIDEO == "视频" and HB.M_AUDIO == "音频"


def test_classify_image_返回二级标记():
    """判据：方块2幂 → 看不懂的；非方块按短边分三级 → 能看的图。"""
    assert HB.classify_image(None, (2048, 2048))[0] == HB.M_IMG_M
    assert HB.classify_image(None, (1024, 1024))[0] == HB.M_IMG_M
    assert HB.classify_image(None, (1920, 1372)) == (HB.M_IMG_R, HB.R_BIG)
    assert HB.classify_image(None, (132, 132)) == (HB.M_IMG_R, HB.R_UI)
    assert HB.classify_image(None, (36, 36)) == (HB.M_IMG_R, HB.R_ICON)
    # 非图
    assert HB.classify_image(None, None) == (None, None)


def test_classify_image_有名文件走路径与关键词():
    assert HB.classify_image(r"ui\spine\a\icon_x.png", None)[0] == HB.M_IMG_R
    assert HB.classify_image(r"effect\fx\a\x_d.tga", None) == (HB.M_IMG_M, "特效图")
    assert HB.classify_image("scene/instance/x/terrain/matidtex/-1_1.tga", None) == \
        (HB.M_IMG_M, "场景地表")


def test_add_按容器行去重():
    """★ 回归：overlay 块与新增行会指向同一行，重复登记会让计数虚高（实测 ×2）。"""
    b = HB.Bundle("x", names_dict=None)
    b.add(container="c", row=1, name=None, source="overlay")
    b.add(container="c", row=1, name=None, source="pkg_N.pi")
    b.add(container="c", row=2, name=None, source="pkg_N.pi")
    assert len(b.rows) == 2, "同一 (容器,行) 必须只登记一次"
    assert "overlay" in b.rows[0]["source"] and "pkg_N.pi" in b.rows[0]["source"], \
        "重复来源应合并进 source，而不是新增条目"


def test_magic_class_覆盖已知格式():
    assert HB.magic_class(b"DDS |\x00\x00") == "image"
    assert HB.magic_class(b"\x89PNG\r\n\x1a\n") == "image"
    assert HB.magic_class(b"FSB5\x01") == "audio"
    assert HB.magic_class(b"<FxGroup>") == "fx"
    assert HB.magic_class(b"\x00\x00\x00 ftyp") == "video"
    assert HB.magic_class(b"ccaa5566") == ""      # 未解格式，如实返回空


# ── 真实交付目录（结构断言，只 stat 不遍历内容）──────────────
@need_out
def test_真实交付物_四个顶层都在():
    """★ 真实交付样本：4 个顶层都在，且**不该有** 01_还原树。"""
    for d in HB.TOP_DIRS:
        assert (REAL_OUT / d).is_dir(), "缺顶层目录 %s" % d
    assert not (REAL_OUT / "01_还原树").exists(), "交付里不该再有 01_还原树（S4 口径）"


@need_out
def test_真实交付物_图片三一分类存在():
    base = REAL_OUT / HB.D_MEDIA / HB.M_IMG
    assert (base / HB.M_IMG_R / HB.R_BIG).is_dir()
    assert (base / HB.M_IMG_R / HB.R_UI).is_dir()
    assert (base / HB.M_IMG_R / HB.R_ICON).is_dir()
    assert (base / HB.M_IMG_M / "方块贴图图集").is_dir()
    assert (REAL_OUT / HB.D_MEDIA / HB.M_VIDEO).is_dir()
    assert (REAL_OUT / HB.D_MEDIA / HB.M_AUDIO).is_dir()


@need_out
def test_真实交付物_02文字表给出变更文案():
    """★★★ 回归：overlay 里的 `_chs.py` 块【不能直接读 raw】—— 必须走解码链。

    flag=0 的块是加密的，要 `la_unpack_core.npk_decode_entry`：
      AES-ECB 解密 → 判 i64@0==1 → 从偏移 18 起 zlib 解压 → marshal 明文。
    实测：走解码链后 102 个表解出 9,608 条中文（去重 6,068）。
    坑：raw 当明文读会得到高熵垃圾，然后误判成「加密读不出」。
    """
    d = REAL_OUT / HB.D_TEXT
    f = d / "变更文案_去重.txt"
    assert f.is_file(), "缺「变更文案_去重.txt」"
    lines = [l.strip() for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lines) > 1000, "变更文案应有数千条（实测 6,068），现在 %d 条" % len(lines)
    # 抽检：必须是真中文（含常用字），不是字节错位假中文
    common = set("的一是不了在人有我他这个上们来到时大地为子中你说生国年着就那和要")
    good = sum(1 for s in lines[:200] if any(ch in common for ch in s))
    assert good > 180, "抽样 200 条里只有 %d 条像真中文" % good


@need_out
def test_真实交付物_02文字表非空():
    """★ 回归：曾经只写一句「本次未涉及」，用户直接指出「你逗我呢」。"""
    d = REAL_OUT / HB.D_TEXT
    fs = [f for f in d.iterdir() if f.is_file()]
    assert fs, "02_文字表 不能是空的"
    assert any(f.name == "本次热更涉及.md" for f in fs or []), "缺「本次热更涉及.md」"


@need_out
def test_真实交付物_02文字表列出本次变更的表():
    """★★★ 回归：本次热更确实动了 102 个 `_chs.py`。

    踩过的坑：只用 `pkg_N.pi` 物理布局 diff 判 → 得出「0 个」的错结论。
    真因：script 容器按【模块名】索引，表的变更只出现在 **overlay 清单**里。
    ⇒ 判据必须是 `pkg_N.pi diff ∪ script overlay 清单`。
    """
    d = REAL_OUT / HB.D_TEXT
    ls = (d / "本次变更文字表_表名清单.txt")
    assert ls.is_file(), "缺「本次变更文字表_表名清单.txt」"
    names = [l.strip() for l in ls.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(names) >= 50, "本次变更的 _chs.py 应上百个（实测 102），现在只有 %d 个" % len(names)
    assert all("_chs." in n.lower() for n in names), "清单里混进了非 _chs 表"
    assert all(n.lower().startswith("com\\cdata\\") or n.startswith("com/") for n in names), \
        "清单里的表应都在 com\\cdata\\ 下"

    md = (d / "本次热更涉及.md").read_text(encoding="utf-8")
    assert "102 个" in md or "%d 个" % len(names) in md, "md 里的结论数应与清单一致"
    assert "overlay" in md, "md 应写明 overlay 这条判据"


@need_out
def test_真实交付物_媒体目录不并存dds与png():
    """★ 用户要求：除 01_还原树 外，图片只留 PNG，不留 DDS（省空间）。"""
    dds = list((REAL_OUT / HB.D_MEDIA).rglob("*.dds"))
    assert not dds, "03_媒体文件 下不该有 .dds（应已转成 PNG）：%s" % dds[:3]


@need_out
def test_真实交付物_manifest有classified字段():
    """★ 回归：manifest 曾只记还原树路径，导致分类目录里的文件反查不到。"""
    m = json.loads((REAL_OUT / "manifest.json").read_text(encoding="utf-8"))
    es = m["entries"]
    withc = [e for e in es if e.get("classified")]
    assert len(withc) > 0.9 * len(es), \
        "manifest 里带 classified 的应占绝大多数（实测 %d/%d）" % (len(withc), len(es))
    # 且 classified 指到的文件必须真存在（抽 5 条）
    bad = [e["classified"] for e in withc[:5] if not (REAL_OUT / e["classified"]).exists()]
    assert not bad, "classified 指向不存在的文件：%s" % bad
