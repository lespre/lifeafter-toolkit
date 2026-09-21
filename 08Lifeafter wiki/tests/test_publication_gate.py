# -*- coding: utf-8 -*-
"""Publication gate contract: un-audited boards must never enter public Wiki manifest."""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "publication_policy.py"


def load_module():
    spec = importlib.util.spec_from_file_location("wiki_publication_policy", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PublicationGateContract(unittest.TestCase):
    def test_only_published_and_provenance_complete_board_can_be_public(self):
        policy = load_module()
        data = {
            "boards": {
                "fashion_wardrobe": {"publication_status": "quarantined", "reason": "row provenance missing"},
                "fashion_rebuilt": {"publication_status": "published", "reason": "current-source verified"},
            }
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "publication_policy.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            public = policy.public_board_ids(path, {"fashion_wardrobe", "fashion_rebuilt"})
        self.assertEqual(public, ["fashion_rebuilt"])

    def test_unknown_or_quarantined_board_is_denied(self):
        policy = load_module()
        data = {"boards": {"lottery_bad": {"publication_status": "quarantined", "reason": "missing selector"}}}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "publication_policy.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertFalse(policy.is_public_board(path, "lottery_bad"))
            self.assertFalse(policy.is_public_board(path, "not_registered"))

    def test_audited_board_requires_machine_readable_row_provenance(self):
        policy = load_module()
        board = {
            "meta": {
                "provenance": {
                    "audit_status": "passed",
                    "source_locks": [{"sha256": "a" * 64, "bytes": 1, "mtime_ns": 1}],
                }
            },
            "items": [{
                "id": "example-1",
                "name": "示例",
                "evidence_level": "static/candidate",
                "provenance": {
                    "source_lock_sha256": "a" * 64,
                    "source_entries": [{"entry_index": 1, "file_id": "0123456789ABCDEF", "decoded_sha256": "b" * 64}],
                    "table": "example_table",
                    "row_key": 1,
                    "field_refs": ["item_id"],
                    "name_source": "same-snapshot item table",
                },
            }],
        }
        self.assertEqual(policy.publication_contract_errors(board), [])
        del board["items"][0]["provenance"]["row_key"]
        self.assertIn("items[0].provenance.row_key", policy.publication_contract_errors(board))

    def test_builder_refuses_published_board_without_row_provenance(self):
        sys.path.insert(0, str(ROOT / "tools"))
        try:
            spec = importlib.util.spec_from_file_location("wiki_builder_for_test", ROOT / "tools" / "build_wiki.py")
            builder = importlib.util.module_from_spec(spec)
            assert spec and spec.loader
            spec.loader.exec_module(builder)
        finally:
            sys.path.remove(str(ROOT / "tools"))
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            boards_dir = tmp_root / "boards"
            boards_dir.mkdir()
            (boards_dir / "unsafe.json").write_text(json.dumps({
                "meta": {"name": "unsafe", "category": "test", "source_server": "test", "package_sha": "a" * 64, "generated": "2026-09-02", "evidence": "structure"},
                "items": [{"id": "x", "name": "unsafe", "evidence": "structure", "source": "legacy free text"}],
            }), encoding="utf-8")
            policy_path = tmp_root / "policy.json"
            policy_path.write_text(json.dumps({"boards": {"unsafe": {"publication_status": "published"}}}), encoding="utf-8")
            builder.BOARDS_DIR = boards_dir
            builder.POLICY_FILE = policy_path
            builder.OUT_FILE = tmp_root / "manifest.js"
            builder.POLICY_JS_FILE = tmp_root / "policy.js"
            self.assertEqual(builder.main(), 1)
            self.assertFalse(builder.OUT_FILE.exists())

    def test_builder_exports_policy_for_static_ui(self):
        result = subprocess.run(
            [sys.executable, "tools/build_wiki.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (ROOT / "data" / "publication_policy.js").read_text(encoding="utf-8")
        payload = json.loads(text.removeprefix("window.WIKI_PUBLICATION_POLICY = ").rstrip(";\n"))
        self.assertEqual(payload["boards"]["nucleus"]["publication_status"], "quarantined")

    def test_builder_publishes_only_provenance_complete_rebuilt_board(self):
        result = subprocess.run(
            [sys.executable, "tools/build_wiki.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (ROOT / "data" / "manifest.js").read_text(encoding="utf-8")
        payload = json.loads(text.removeprefix("window.WIKI_MANIFEST = ").rstrip(";\n"))
        self.assertEqual(
            [board["board"] for board in payload["boards"]],
            sorted(
                bid for bid, entry in json.loads(
                    (ROOT / "data" / "publication_policy.json").read_text(encoding="utf-8")
                )["boards"].items()
                if entry.get("publication_status") == "published"
                and (ROOT / "data" / "boards" / f"{bid}.json").exists()
            ),
            # published_hidden（两块武器皮肤旧入口）不上首页；数据仍保留、直链可达
        )
        self.assertEqual(
            [board["items"] for board in payload["boards"]],
            [65, 31112, 26, 5477, 1189, 23567, 77, 4, 47, 196, 115],   # 隐藏审计板（133/3）不上首页
        )
        self.assertNotIn("nucleus", {board["board"] for board in payload["boards"]})
        self.assertNotIn("weapon_skins", {board["board"] for board in payload["boards"]})
        self.assertNotIn("common_item_text_sources", {board["board"] for board in payload["boards"]})
        # weapon_skin_sfx_text_sources 于 2026-09-11 按用户指令作为「武器皮肤图鉴」发布（二、时装类（七））
        self.assertNotIn("lottery_kaijia_panel_static", {board["board"] for board in payload["boards"]})

    def test_board_page_loads_policy_before_any_dynamic_board_data(self):
        text = (ROOT / "board.html").read_text(encoding="utf-8")
        self.assertRegex(text, r'<script src="data/publication_policy\.js\?v=[^"]+"></script>')
        # 直链门禁：published 或 published_hidden 放行（published_hidden=隐藏审计板，不上首页但可直链打开）
        gate = '!["published","published_hidden"].includes(policyEntry.publication_status)'
        self.assertIn(gate, text)
        self.assertLess(text.index(gate), text.index('else loadBoard(b,d=>'))

    def test_homepage_has_no_legacy_board_links_while_policy_quarantines_them(self):
        text = (ROOT / "wiki.html").read_text(encoding="utf-8")
        self.assertIsNone(re.search(r'<a\b[^>]*\bhref=["\']board\.html\?b=', text))
        self.assertNotIn('href="nucleus.html"', text)
        self.assertNotIn('href="weapon_skins.html"', text)
        self.assertNotIn('href="new_textures.html"', text)

    def test_homepage_renders_only_manifest_boards_in_their_declared_category(self):
        text = (ROOT / "wiki.html").read_text(encoding="utf-8")
        self.assertIn('data-wiki-group="一、道具总表"', text)
        self.assertIn('data-wiki-group="二、时装类"', text)
        self.assertIn('data-wiki-group="三、战力类"', text)
        self.assertIn('data-wiki-group="四、奖池"', text)
        self.assertIn("（五）无人机", text)
        self.assertIn("（二）护具", text)
        # （八）载具=AUDIT 占位已转正为真板（category 尾段由板数据动态渲染）
        self.assertIn("（八）载具", (ROOT / "data/boards/vehicle_garage_names.json").read_text(encoding="utf-8"))
        self.assertIn("const groups={}", text)
        self.assertIn("for(const head of Object.keys(groups).sort(", text)
        self.assertIn('document.querySelector(`[data-wiki-group="', text)
        self.assertIn("groups[head].length", text)
        self.assertIn("catSeq(a.category)", text)
        self.assertIn("cards.sort((x,y)=>x.seq-y.seq).forEach(c=>target.appendChild(c.el));", text)

    def test_board_page_primary_title_matches_homepage_card_category_tail(self):
        """A child page must not expose its generator-internal meta.name as its title."""
        text = (ROOT / "board.html").read_text(encoding="utf-8")
        helper = re.search(r"const TITLE_CN=\[[\s\S]*?\];", text)
        self.assertIsNotNone(helper, "board.html must define the title-normalisation table")
        assert helper is not None
        zhtext = re.search(r"function zhTitle\(s\)\{[\s\S]*?\}", text)
        self.assertIsNotNone(zhtext, "board.html must define zhTitle")
        assert zhtext is not None
        match = re.search(
            r"function boardCardTitle\(meta\)\{[\s\S]*?\}",
            text,
        )
        self.assertIsNotNone(match, "board.html must define the shared card-title rule")
        assert match is not None
        probe = helper.group(0) + chr(10) + zhtext.group(0) + chr(10) + match.group(0) + chr(10) + chr(10).join(
            [
                'if(boardCardTitle({name:"铠甲再临 · 静态面板配置",category:"四、奖池 / （一）抽奖、转盘、不放回抽奖"})!=="（一）抽奖、转盘、不放回抽奖")process.exit(11);',
                'if(boardCardTitle({name:"内部名",category:"二、时装类 / （三）背包/挂件"})!=="（三）背包/挂件")process.exit(12);',
                'if(boardCardTitle({name:"内部回退名",category:""})!=="内部回退名")process.exit(13);',
                'if(boardCardTitle({name:"武器皮肤 · 静态候选（identity unresolved）",category:"三、战力类 / （六）武器皮肤（静态候选）"})!=="（六）武器皮肤（静态候选）")process.exit(14);',
                'if(/[A-Za-z]{4,}/.test(boardCardTitle({name:"x",category:"三、战力类 / 武器属性（schema 6109 原始属性关系）"})))process.exit(15);',
            ]
        )
        result = subprocess.run(["node", "-e", probe], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        self.assertIn('const title=boardCardTitle(m);', text)
        self.assertIn('document.title=title+" · Wiki";', text)
        self.assertIn('document.getElementById("title").textContent=title;', text)
        self.assertNotIn('document.title=m.name+" · Wiki";', text)

    def test_legacy_static_pages_redirect_to_policy_gated_board(self):
        """Old hard-coded catalog URLs may not render stale claims directly."""
        legacy = {
            "nucleus.html": "nucleus",
        }
        archive_dir = ROOT / "data" / "quarantine_legacy_html"
        for page, board_id in legacy.items():
            self.assertTrue((archive_dir / page).is_file(), f"legacy source not archived: {page}")
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn(f'window.location.replace("board.html?b={board_id}")', text)
            self.assertIn("该历史页面已隔离", text)


if __name__ == "__main__":
    unittest.main()
