# -*- coding: utf-8 -*-
"""中文化验收护栏：字段中文名 / 徽章中文 / 排序标签中文 / 卡面-技术详情分流。

浏览器渲染后的实测脚本：analysis/tools/check_zh_surface.py（首页+四页可见区零裸英文）。
本测试只做结构不变量，避免在单测里起浏览器。
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_HTML = ROOT / "board.html"
WIKI_HTML = ROOT / "wiki.html"

# ── 白名单：不强制做「普通字段中文名」的四类（用户可以看不到它们，或已有专门渲染器）──
# 说明：技术详情折叠区允许显示原始英文键（用户口径），故 TECHNICAL 组内的字段不要求中文名；
# 但若某字段确实渲染在普通视图（不在 TECH_KEYS/FIXED/白名单里），就必须有 FIELD_CN 中文名。
WHITELIST_CONTAINER = {          # ① 纯容器/结构键：items/meta/pools/rows 等，由渲染器展开
    "items", "meta", "pools", "rows", "variant_items", "sfx_items", "behavior_resources",
    "rewards", "activity_pool_refs", "reference_fields", "field_provenance", "static_fields",
    "candidate_reference_fields", "name_resolution", "text_provenance", "rank_star_segments",
    "sort", "sort_660", "period_date", "period_name", "filters", "notes",
}
WHITELIST_INDEX = {               # ② 内部索引键：排序/搜索/来源定位用，不作为玩家字段展示
    "search_text", "row_key", "record_key", "structural_record_key", "entry_index", "file_id",
    "decoded_sha256", "source_lock_sha256", "source_entries", "field_refs", "upstream",
    "package_sha256", "source_path", "source_sha256", "source_entry", "manifest_path", "dataset",
}
WHITELIST_RENDERER = {            # ③ 已有专门渲染器接管：卡名/ID 行/图标/战斗面板/变体块…
    "id", "name", "desc", "icon", "icon_path", "model", "model_path", "texture", "res_path",
    "paths", "sample_paths", "sfx_paths", "asset_paths", "label_path",
    "combat_panel", "skill_desc", "skill_icon", "candidate_name_source", "candidate_name_status",
    "ui_short_name_candidates", "ui_combat_short_names", "ui_short_name_es_key", "es_registry_row_key",
    "variant_item_count", "sfx_item_count", "named_sfx_item_count", "display_name",
}
WHITELIST_TECHNICAL = {           # ④ 技术详情区字段：折叠区内允许原始英文键
    "provenance", "source", "evidence", "evidence_level", "publication_tier", "status_tags",
    "identity_status", "identity_state", "identity_reason", "reliability_state", "hide_in_bag_state",
    "name_evidence", "sfx_consensus_state", "source_record_layer", "source_kind", "scope",
    "chain_status", "component", "dataset_partition", "audit_status", "locator_chain", "schema_ref",
    "schema_refs", "physical_fid", "payload_sha", "payload_sha256", "source_state", "identity_ns",
    "identity_namespace", "evidence_refs", "origin", "node_type", "value_type", "kind", "role", "src",
    "field_chs_slot", "value_chs_slot", "scalar_type", "search_terms",
}
WHITELIST = WHITELIST_CONTAINER | WHITELIST_INDEX | WHITELIST_RENDERER | WHITELIST_TECHNICAL

# 排序/筛选标签里允许出现的通用缩写（不算"英文内部值"）
LABEL_ALLOWED_TOKENS = ("IP", "ID", "UI", "SFX", "DIY", "PK", "HP", "MP")


def _read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def _load_js_object(path: pathlib.Path) -> dict:
    text = _read(path)
    body = text.split("=", 1)[1].strip().rstrip(";")
    return json.loads(body)


def _string_set(block: str) -> set[str]:
    """从 JS 片段里抠出双引号/单引号字符串（用作已中文化的证据）。"""
    return set(re.findall(r'"([^"]+)"', block)) | set(re.findall(r"'([^']+)'", block))


def published_boards() -> list[dict]:
    manifest = _load_js_object(ROOT / "data" / "manifest.js")
    return list(manifest.get("boards") or [])


def board_field_names() -> dict[str, set[str]]:
    """所有已发布板里出现过的字段名 → 出现在哪些板。"""
    out: dict[str, set[str]] = {}
    for board in published_boards():
        bid = board.get("board")
        path = ROOT / "data" / "boards" / f"{bid}.js"
        if not path.exists():
            continue
        data = _load_js_object(path)
        seen = out.setdefault(bid, set())
        for item in data.get("items") or []:
            if not isinstance(item, dict):
                continue
            seen.update(item.keys())
            for variant in item.get("variant_items") or []:
                if isinstance(variant, dict):
                    seen.update(variant.keys())
            for pool in item.get("pools") or []:
                for row in ((pool or {}).get("rows") if isinstance(pool, dict) else []) or []:
                    if isinstance(row, dict):
                        seen.update(row.keys())
        for flt in ((data.get("meta") or {}).get("filters") or []):
            if isinstance(flt, dict) and flt.get("key"):
                seen.add(str(flt["key"]))
    return out


class ChineseSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.board_html = _read(BOARD_HTML)
        cls.wiki_html = _read(WIKI_HTML)
        block = re.search(r"const FIELD_CN=\{([\s\S]*?)\n\};", cls.board_html)
        assert block, "board.html 缺少 FIELD_CN 定义"
        cls.field_cn_block = block.group(1)
        cls.field_cn = set(re.findall(r"([A-Za-z_][A-Za-z0-9_]*)\s*:", cls.field_cn_block))
        cls.tech_keys = set(re.findall(
            r'"([^"]+)"', re.search(r"const TECH_KEYS=new Set\(\[([\s\S]*?)\]\);", cls.board_html).group(1)))
        cls.fixed_keys = set(re.findall(
            r'"([^"]+)"', re.search(r"const FIXED=new Set\(\[([\s\S]*?)\]\);", cls.board_html).group(1)))

    def test_every_visible_field_has_chinese_label(self):
        """普通视图字段必须有中文名；折叠进技术详情/白名单内的字段不强制。"""
        missing: dict[str, list[str]] = {}
        for bid, fields in board_field_names().items():
            gap = sorted(
                f for f in fields
                if f not in self.field_cn
                and f not in WHITELIST
                and f not in self.tech_keys
                and f not in self.fixed_keys
            )
            if gap:
                missing[bid] = gap
        self.assertEqual(missing, {}, f"以下板存在没有中文名的普通视图字段：{missing}")

    def test_whitelist_groups_are_documented_and_disjoint_roles(self):
        """白名单必须四类齐全（容器/索引/专门渲染器/技术详情），不能混成一个黑箱。"""
        for name, group in (
            ("容器键", WHITELIST_CONTAINER), ("内部索引键", WHITELIST_INDEX),
            ("专门渲染器接管", WHITELIST_RENDERER), ("技术详情区", WHITELIST_TECHNICAL),
        ):
            self.assertTrue(group, f"白名单分组为空：{name}")
        self.assertIn("search_text", WHITELIST_INDEX)
        self.assertIn("provenance", WHITELIST_TECHNICAL)
        self.assertIn("variant_items", WHITELIST_CONTAINER)

    def test_state_badges_are_chinese(self):
        """状态徽章不得直接展示英文内部值（原始值只能进技术详情）。"""
        m = re.search(r"const STATE_CN=\{([\s\S]*?)\};", self.board_html)
        self.assertIsNotNone(m, "board.html 缺少 STATE_CN")
        for key, value in re.findall(r'"?([^":\s]+)"?\s*:\s*"([^"]*)"', m.group(1)):
            self.assertTrue(
                re.search(r"[\u4e00-\u9fff]", value),
                f"状态徽章 {key} 未中文化：{value}",
            )
        for state in ("verified", "unresolved", "quarantined", "static config", "runtime final unknown", "candidate"):
            self.assertIn(state, m.group(1), f"状态徽章缺少 {state} 的映射")
        wiki = re.search(r"const STATE_ZH=\{([\s\S]*?)\};", self.wiki_html)
        self.assertIsNotNone(wiki, "wiki.html 缺少 STATE_ZH")
        self.assertIn("已核验", wiki.group(1))
        self.assertIn("静态配置", wiki.group(1))

    def test_sort_option_labels_are_chinese(self):
        """搜索/排序选项标签不得出现内部值（sale_desc/id_desc 等只能作为 option value）。"""
        for match in re.finditer(r"<option[^>]*>([^<]*)</option>", self.board_html):
            label = match.group(1)
            stripped = re.sub("|".join(sorted(LABEL_ALLOWED_TOKENS)), "", label)
            self.assertIsNone(re.search(r"[A-Za-z]", stripped), f"排序/筛选选项标签含英文：{label}")

    def test_engineering_fields_are_folded_into_tech_section(self):
        """用户点名的工程字段必须收进技术详情折叠区，而不是铺在卡面。"""
        m = re.search(r"const TECH_KEYS=new Set\(\[([\s\S]*?)\]\);", self.board_html)
        self.assertIsNotNone(m, "board.html 缺少 TECH_KEYS")
        tech = set(re.findall(r'"([^"]+)"', m.group(1)))
        for field in (
            "source", "provenance", "physical_fid", "payload_sha256", "publication_tier",
            "schema_ref", "schema_refs", "identity_status", "identity_reason", "evidence_level",
            "source_lock_sha256", "static_fields", "search_text", "locator_chain",
        ):
            self.assertIn(field, tech, f"{field} 应折叠进技术详情")
        self.assertIn("技术详情", self.board_html)
        self.assertRegex(self.board_html, r"<details class=\"tech\">")

    def test_no_english_internal_prefix_on_card_id(self):
        """卡片 ID 行不得出现 item_id/SFX 之类内部前缀。"""
        self.assertNotIn("item_id ${", self.board_html)
        self.assertNotIn(">item_id ", self.board_html)


if __name__ == "__main__":
    unittest.main()

class InlineScriptSyntaxTests(unittest.TestCase):
    """页面靠内联脚本渲染：语法一处错就整页空白，必须进护栏。"""

    def _blocks(self, path: pathlib.Path) -> list[str]:
        return re.findall(r"<script>([\s\S]*?)</script>", _read(path))

    def test_inline_scripts_are_syntactically_valid(self):
        import shutil
        import subprocess
        import tempfile

        node = shutil.which("node")
        if not node:
            self.skipTest("node 未安装，跳过语法校验")
        for page in (BOARD_HTML, WIKI_HTML):
            for index, block in enumerate(self._blocks(page)):
                with tempfile.TemporaryDirectory() as tmp:
                    target = pathlib.Path(tmp) / f"{page.stem}_{index}.js"
                    target.write_text(block, encoding="utf-8")
                    done = subprocess.run([node, "--check", str(target)], capture_output=True, text=True)
                self.assertEqual(
                    done.returncode, 0,
                    f"{page.name} 内联脚本 #{index} 语法错误：{(done.stderr or '')[:400]}",
                )
