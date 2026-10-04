# -*- coding: utf-8 -*-
"""①-4 名字还原 · 字典读取 + `names stats` 的契约测试。

## 防的回归（2026-09-28 实修，改前实测复现）

`03_执行/10_索引/names/` 下**两种字典格式并存**（直接读文件头核对过）：

    ① 裸映射 `{fid_hex: 路径}`                    —— v2…v13 全是它（v13 = 1,061,631 行）
    ② 带包装 `{…, "entries": {路径: fid_hex}}`    —— `names build` 的输出（213,996 行）

旧 `stats()` 只认②：`d.get("entries")` 在裸映射上是 None ⇒ 静默读成 **0 条**，
而「哈希自检」照旧通过（自检与字典无关）⇒ 表现为「索引 230 万行 + 字典 86 MB =
规模 0 条」。本文件把「两种格式都必须读出真实数字」钉成契约。

另外钉住两条口径/归一规则：
  · **行口径**：一个 fid = 一行。实测 v13 有 15,807 条路径各自对应 2 个 fid
    （1,061,631 行 vs 1,045,803 个唯一路径）—— 统计规模/命中率必须按行，不能按路径。
  · **fid 归一**：字典键可能是小写，索引 `entries.fid_hex` 是大写；不归一就全落空。

测试用临时索引（不碰真库），真字典只做一次「读得进且非 0」的冒烟。
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import names as N                                   # noqa: E402
from toolkit_core.paths import DEFAULT_NAMES_DICT                     # noqa: E402
from toolkit_core.unified_index import initialize_schema              # noqa: E402

CLI = CORE / "命令行" / "toolkit_cli.py"

#: 三条固定路径：两条进索引（命中），一条不进（未命中）
P_HIT_A = r"ui/a/img_1.png"
P_HIT_B = r"effect/b/sfx_2.sfx"
P_MISS = r"ui/z/nothere_9.png"


def _make_index(tmp: Path, rows) -> Path:
    """最小真库结构：entries(fid_hex,container,…) + containers。rows=[(fid, 容器, 行号)]。"""
    db = tmp / "idx.sqlite3"
    con = sqlite3.connect(str(db))
    initialize_schema(con)
    for fid, container, row in rows:
        con.execute(
            "INSERT INTO entries(fid_hex,container,kind,row_index,offset,payload_offset,"
            "packed,decoded,flag,source) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (fid, container, "gpk", row, 0, 0, 0, 0, 0, "test"))
        con.execute("INSERT OR REPLACE INTO containers"
                    "(container,kind,bytes,mtime_ns,rows,status,error) VALUES(?,?,?,?,?,?,?)",
                    (container, "gpk", 0, 0, 1, "ok", None))
    con.commit()
    con.close()
    return db


class DictFormatTests(unittest.TestCase):
    """格式判向：靠【键本身】是不是 16 位 HEX，不靠文件名。"""

    def test_flat_detected(self):
        self.assertEqual(N.dict_format({"A" * 16: "ui/a.png"}), "flat")

    def test_wrapped_detected(self):
        self.assertEqual(N.dict_format({"version": 1, "entries": {"ui/a.png": "A" * 16}}),
                         "wrapped")

    def test_non_dict_payload_raises(self):
        with self.assertRaises(ValueError):
            N.fid_map(["not", "a", "dict"])


class FidMapTests(unittest.TestCase):
    """读出来的形状与无损性。"""

    def test_flat_is_lossless_rows(self):
        """同一路径两个 fid ⇒ 仍是两行（按行口径，不按路径去重）。"""
        p = r"ui\main_tips\MainTipsItemCommon.py"
        flat = {"0087ED095E1D2019": p, "70441A44322D89C5": p}
        got = N.fid_map(flat)
        self.assertEqual(len(got), 2)
        self.assertEqual(set(got), {"0087ED095E1D2019", "70441A44322D89C5"})

    def test_entries_of_is_path_view_loses_rows(self):
        p = r"ui\a.py"
        got = N.entries_of({"0087ED095E1D2019": p, "70441A44322D89C5": p})
        self.assertEqual(got, {p: "70441A44322D89C5"})     # 路径为键 ⇒ 塌成一条

    def test_fid_keys_uppercased(self):
        """字典键小写也必须归一成大写 —— 否则与索引 fid_hex 比对全落空。"""
        got = N.fid_map({"0087ed095e1d2019": "ui/a.py"})
        self.assertEqual(got, {"0087ED095E1D2019": "ui/a.py"})

    def test_wrapped_inverted_to_fid_keyed(self):
        got = N.fid_map({"version": 1, "built": "t", "sources": [],
                         "entries": {"ui/a.py": "0087ED095E1D2019"}})
        self.assertEqual(got, {"0087ED095E1D2019": "ui/a.py"})

    def test_empty_payload(self):
        self.assertEqual(N.fid_map({}), {})
        self.assertEqual(N.fid_map({"entries": {}}), {})


class StatsContractTests(unittest.TestCase):
    """`names stats` 对两种格式都必须给出【同一组真实数字】。"""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(prefix="names_stats_"))
        self.fids = {p: N.fid_hex(p) for p in (P_HIT_A, P_HIT_B, P_MISS)}
        self.db = _make_index(self.tmp, [
            (self.fids[P_HIT_A], r"res\ui_01.gpk", 11),
            (self.fids[P_HIT_B], r"res\effect_01.gpk", 22),
        ])
        self.flat = {f: p for p, f in self.fids.items()}
        self.wrapped = {"version": 1, "built": "2026-09-28T00:00:00",
                        "sources": ["x"], "count": 3, "entries": self.fids}

    def _write(self, name, payload) -> Path:
        p = self.tmp / name
        p.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
        return p

    def test_flat_dict_reports_real_numbers_NOT_zero(self):
        """★ 回归本体：裸映射格式（v13 就是它）过去被读成 0 条。"""
        rep = N.stats(self._write("flat.json", self.flat), self.db)
        self.assertEqual(rep["dict_format"], "flat")
        self.assertEqual(rep["count"], 3)
        self.assertGreater(rep["count"], 0)                 # 改前是 0
        self.assertEqual(rep["hit"], 2)
        self.assertEqual(rep["miss"], 1)
        self.assertEqual(rep["containers_covered"], 2)
        self.assertEqual(rep["index_rows"], 2)
        self.assertEqual(set(rep["containers"]), {r"res\ui_01.gpk", r"res\effect_01.gpk"})
        self.assertEqual(rep["containers"][r"res\ui_01.gpk"], 1)
        self.assertAlmostEqual(rep["rate"], 2 / 3)

    def test_wrapped_dict_same_numbers(self):
        """带包装格式（build 的输出）数字必须与裸映射一致 —— 格式无关。"""
        rep = N.stats(self._write("wrapped.json", self.wrapped), self.db)
        self.assertEqual(rep["dict_format"], "wrapped")
        self.assertEqual(rep["built"], "2026-09-28T00:00:00")
        self.assertEqual(rep["sources"], ["x"])
        self.assertEqual((rep["count"], rep["hit"], rep["miss"],
                          rep["containers_covered"], rep["index_rows"]),
                         (3, 2, 1, 2, 2))

    def test_case_insensitive_keys_still_hit(self):
        """小写 fid 键的字典也必须命中（归一到大写）。"""
        low = {f.lower(): p for p, f in self.fids.items()}
        rep = N.stats(self._write("lower.json", low), self.db)
        self.assertEqual(rep["hit"], 2)

    def test_missing_dict_raises(self):
        with self.assertRaises(FileNotFoundError):
            N.stats(self.tmp / "nope.json", self.db)


class CliStatsTests(unittest.TestCase):
    """`names stats --json -` 端到端：裸映射字典必须报非 0。"""

    def test_cli_reports_nonzero_for_flat_dict(self):
        tmp = Path(tempfile.mkdtemp(prefix="names_cli_"))
        fids = {p: N.fid_hex(p) for p in (P_HIT_A, P_MISS)}
        db = _make_index(tmp, [(fids[P_HIT_A], r"res\ui_01.gpk", 7)])
        d = tmp / "flat.json"
        d.write_text(json.dumps({f: p for p, f in fids.items()}), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(CLI), "names", "stats",
             "--dict", str(d), "--db", str(db), "--json", "-"],
            capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        rep = json.loads(proc.stdout)
        self.assertEqual(rep["count"], 2)
        self.assertEqual(rep["hit"], 1)
        self.assertEqual(rep["miss"], 1)
        self.assertEqual(rep["dict_format"], "flat")


class RealDictSmokeTests(unittest.TestCase):
    """真字典冒烟：默认解析到的那份必须读得进、且非 0 条（改前这里是 0）。"""

    def test_latest_dict_reads_nonzero(self):
        if not Path(DEFAULT_NAMES_DICT).is_file():
            raise unittest.SkipTest("字典不在：%s" % DEFAULT_NAMES_DICT)
        payload = json.loads(Path(DEFAULT_NAMES_DICT).read_text(encoding="utf-8"))
        rows = N.fid_map(payload)
        self.assertGreater(len(rows), 100_000,
                           "默认字典 %s 只读出 %d 行 —— 字典读取又坏了"
                           % (DEFAULT_NAMES_DICT, len(rows)))
        for fid in list(rows)[:200]:
            self.assertRegex(fid, r"^[0-9A-F]{16}$")


if __name__ == "__main__":
    unittest.main()
