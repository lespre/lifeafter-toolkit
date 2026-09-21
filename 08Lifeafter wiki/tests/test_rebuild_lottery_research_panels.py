# -*- coding: utf-8 -*-
"""Nucleus research & chip guarantee structure boards contract."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_lottery_research_panels.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("rp_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build(board: str) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "b.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--board", board, "--output", str(out)],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class ResearchPanelsContract(unittest.TestCase):
    def test_nucleus_board(self):
        board = build("nucleus")
        self.assertEqual(board["meta"]["category"], "四、奖池 / （五）限定核芯研制")
        # ykxq 全量主表：72 期（2023-08-04 起 ~ 2026-09-16），sub_title=真实期名
        self.assertGreaterEqual(len(board["items"]), 70)
        periods = [it for it in board["items"] if it["id"].startswith("hd-")]
        self.assertGreaterEqual(len(periods), 70)
        self.assertEqual(periods[0]["start_date"], "2023-08-04")
        names = [p["name"] for p in periods]
        self.assertTrue(any("2026-09-03" in n for n in names), names[-3:])
        subs = [p.get("sub_title") for p in periods]
        self.assertIn("凝滞侵袭返场", subs)
        self.assertIn("电掣双刀返场", subs)  # 同名多期：出现多次
        self.assertGreaterEqual(subs.count("电掣双刀返场"), 3)
        self.assertIn("穿心极雷登场", subs)
        self.assertFalse(any(it["id"] in ("structure-tables", "content-pool-family", "up-period-name-samples") for it in board["items"]))
        self.assertFalse(any("up_candidate" in it for it in board["items"]))  # 无推测字段
        for p in periods:
            self.assertEqual(p["hd_class"], "NucleusLotteryHD")
            self.assertEqual(p["evidence_level"], "structure-only")
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])

    def test_chip_board(self):
        board = build("chip")
        self.assertEqual(board["meta"]["category"], "四、奖池 / （六）限定芯片保底")
        periods = [it for it in board["items"] if it["id"].startswith("hd-")]
        self.assertEqual(len(periods), 0)  # huodong periods live in the directory item now
        # conf 31 期 = 31 张子卡（2026-09-10 热更后 +1 期）；ykxq 全量期对齐（首期 2023-05-25，key30=2026-07-16~08-05）
        conf_cards = [it for it in board["items"] if it["id"].startswith("chip-period-")]
        self.assertEqual(len(conf_cards), 31)
        self.assertIn("芯片期 1（2023-05-25~2023-06-07", conf_cards[0]["name"])
        self.assertRegex(conf_cards[2]["name"], r"芯片期 3（(?:\d{4}-\d{2}-\d{2}~\d{4}-\d{2}-\d{2}|时间待校准) · ui\d+ · 保底 \d+）")
        # no ghost structure/content/directory cards on the chip board
        self.assertFalse(any(it["id"] in ("structure-tables", "content-conf-rule", "period-directory") for it in board["items"]))
        self.assertEqual(len(board["items"]), 31)
        # 新格式期（key13，ui20）：UP 返厂组=8 款芯片
        p13 = next(it for it in conf_cards if it["id"] == "chip-period-13")
        up13 = p13["当期芯片（UP 返厂组）"]
        parts = [s for s in up13.split(", ") if s.strip()]
        self.assertGreaterEqual(len(parts), 7, up13)
        self.assertIn("雷霆一击", up13)
        self.assertIn("荆棘护盾", up13)
        self.assertIn("限定特级芯片自选箱", p13["保底奖励"])
        self.assertEqual(p13["金芯片保底数"], 450)
        self.assertEqual(p13["总保底数"], 180)
        # 旧格式期（key1，ui8）：UP=2 款 + 保底自选箱名
        p1 = next(it for it in conf_cards if it["id"] == "chip-period-1")
        self.assertIn("330014(连环暴击)", p1["当期芯片（UP 返厂组）"])
        self.assertIn("240807(连环暴击自选箱)", p1["保底奖励"])
        self.assertEqual(p1["金芯片保底数"], 80)
        # 错位修复验证：conf key = extra 值（用户校准 key30=2026-07-16 连环暴击返场）
        p30 = next(it for it in board["items"] if it["id"] == "chip-period-30")
        self.assertIn("2026-07-16~2026-08-05", p30["name"])
        self.assertEqual(p30["activity_period"], "2026-07-16~2026-08-05")
        # 双服差异实证：huodong 期名（ykxq 主表两服共享）=破盾强攻返场（经典服），
        # conf UP 组（BA8 简单服配置）=连环暴击 8 款
        self.assertIn("破盾强攻返场", p30.get("activity_subtitle") or "")
        up30 = p30["当期芯片（UP 返厂组）"]
        for chip_name in ("连环暴击", "覆盖打击", "好事成双", "势如破竹", "全副武装",
                          "坚如磐石", "坚韧不拔", "荆棘护盾"):
            self.assertIn(chip_name, up30, chip_name)
        # user-verified names fill the two roster-gap ids
        self.assertIn("331026(坚如磐石)", up30)
        self.assertIn("331018(坚韧不拔)", up30)
        p27 = next(it for it in board["items"] if it["id"] == "chip-period-27")
        self.assertIn("2026-02-12~2026-03-04", p27["name"])
        # no period-directory card; total = 30 period cards only
        self.assertFalse(any(it["id"] == "period-directory" for it in board["items"]))
        self.assertEqual(len(board["items"]), 31)
        for p in conf_cards:
            self.assertEqual(p["evidence_level"], "structure-only")
            self.assertIsNotNone(p["provenance"]["row_key"])
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])

    def test_no_current_period_claims(self):
        for board_name in ("nucleus", "chip"):
            board = build(board_name)
            blob = json.dumps(board, ensure_ascii=False)
            self.assertIn("预测当期", board["meta"]["notes"])


if __name__ == "__main__":
    unittest.main()
