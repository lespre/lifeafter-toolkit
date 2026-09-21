"""Workbench v1.3 —— Web Client / Projection Performance 守护测试。

覆盖用户列的 10 项性能/行为要求：
  1) /api/items 默认不返回全量        2) page_size 上限守护
  3) 30k item 首屏不加载 35MB JS      4) lottery 首屏不加载全量
  5) 搜索/过滤正确                    6) item detail provenance 正确
  7) BA8A basis 不被隐藏              8) API 不可用时不回退 historical/legacy
  9) legacy board 不参与 Workbench 查询  10) Wiki View 不改业务状态
"""
from __future__ import annotations

import builtins
import hashlib
import json
import pathlib
import sys
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FORBIDDEN = ("data/boards", "data\\boards", "historical", "06（agent写）", ".db", "script.py314", "03拆包产物")
ITEM_ROWS = 30467
LOTTERY_TARGETS = 23567
LOTTERY_POOLS = 24041


def _h(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


class _Server(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from api.server import Handler
        cls.httpd = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.port = cls.httpd.server_address[1]
        cls.thread = threading.Thread(target=cls.httpd.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def _get(self, path, params=None):
        url = f"http://127.0.0.1:{self.port}{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        with urllib.request.urlopen(url, timeout=60) as resp:
            raw = resp.read()
            return resp.status, len(raw), json.loads(raw.decode("utf-8"))


class PagingGuards(_Server):
    def test_1_items_default_is_paged(self):
        code, size, d = self._get("/api/items")
        self.assertEqual(code, 200)
        self.assertEqual(d["total"], ITEM_ROWS)
        self.assertLessEqual(d["page_size"], 200)
        self.assertLessEqual(len(d["items"]), 200)
        self.assertLess(size, 200_000, "默认 /api/items 响应不应是几十 MB")
        self.assertEqual(d["pages"], -(-ITEM_ROWS // d["page_size"]))

    def test_2_page_size_is_clamped(self):
        _c, _s, d = self._get("/api/items", {"page_size": 100000})
        self.assertEqual(d["page_size"], 200)
        self.assertTrue(d["clamped"])
        self.assertLessEqual(len(d["items"]), 200)

    def test_2b_offset_limit_compat(self):
        _c, _s, d = self._get("/api/items", {"limit": 3, "offset": 0})
        self.assertEqual(d["page_size"], 3)
        self.assertEqual(d["page"], 1)
        self.assertEqual(len(d["items"]), 3)

    def test_3_lottery_endpoints_paged(self):
        _c, _s, pools = self._get("/api/lottery/pools", {"page_size": 5})
        self.assertEqual(pools["total"], LOTTERY_POOLS)
        self.assertLessEqual(len(pools["items"]), 5)
        _c, _s, rew = self._get("/api/lottery/rewards")
        self.assertEqual(rew["total"], LOTTERY_TARGETS)
        self.assertLessEqual(len(rew["items"]), 200)
        self.assertIn("runtime_final_status", rew["items"][0])
        self.assertNotIn("item_master_id", rew["items"][0])

    def test_5_filters_correct(self):
        _c, _s, hit = self._get("/api/items", {"q": "新币", "page_size": 5})
        self.assertGreaterEqual(hit["total"], 1)
        self.assertIn(150005, [r["item_id"] for r in hit["items"]])
        _c, _s, chip = self._get("/api/items", {"namespace": "belt_chip"})
        self.assertEqual(chip["total"], 54)
        _c, _s, un = self._get("/api/items", {"name_status": "unresolved"})
        self.assertEqual(un["total"], 216)
        _c, _s, uo = self._get("/api/lottery/rewards", {"unresolved_only": 1})
        self.assertEqual(uo["total"], 1665)
        _c, _s, sort_d = self._get("/api/items", {"sort": "name", "desc": 1, "page_size": 5})
        self.assertEqual(sort_d["sort"], "name")
        self.assertTrue(sort_d["desc"])

    def test_14_page_metadata(self):
        _c, _s, d = self._get("/api/items", {"page": 3, "page_size": 200})
        self.assertEqual(d["page"], 3)
        self.assertTrue(d["has_prev"] and d["has_next"])
        self.assertEqual(d["pages"], 153)


class FrontendFirstScreen(_Server):
    """首屏 payload：API 默认响应 vs 离线全量投影文件。"""

    def test_3b_item_first_screen_not_35mb(self):
        boards = ROOT / "data" / "workbench_boards"
        full = boards / "item_master_active.js"
        self.assertTrue(full.exists(), "离线全量投影应存在（作为 offline 导出，而非默认路径）")
        full_bytes = full.stat().st_size
        _c, size, _d = self._get("/api/items", {"page_size": 50})
        self.assertLess(size * 100, full_bytes, f"首屏 {size}B 应远小于离线全量 {full_bytes}B")
        html = (ROOT / "workbench_items.html").read_text(encoding="utf-8")
        self.assertIn("/api/items", html)
        for bad in ("workbench_boards/item_master_active.js", "data/boards"):
            self.assertNotIn(bad, html, f"物品页不得加载 {bad}")

    def test_4_lottery_first_screen_not_full(self):
        boards = ROOT / "data" / "workbench_boards"
        for name, api in (("lottery_pool_active.js", "/api/lottery/pools"),
                          ("lottery_rewards_active.js", "/api/lottery/rewards")):
            self.assertTrue((boards / name).exists())
            _c, size, _d = self._get(api, {"page_size": 50})
            self.assertLess(size * 100, (boards / name).stat().st_size)
        html = (ROOT / "workbench_lottery.html").read_text(encoding="utf-8")
        self.assertIn("/api/lottery/pools", html)
        self.assertIn("/api/lottery/rewards", html)
        for bad in ("workbench_boards/lottery_pool_active.js", "workbench_boards/lottery_rewards_active.js", "data/boards"):
            self.assertNotIn(bad, html)

    def test_8_no_silent_fallback_on_api_unavailable(self):
        board = (ROOT / "board.html").read_text(encoding="utf-8")
        items = (ROOT / "workbench_items.html").read_text(encoding="utf-8")
        client = (ROOT / "assets" / "workbench_client.js").read_text(encoding="utf-8")
        # board.html：API-first 板块在创建 script 之前直接返回，离线全量必须显式 offline=1
        self.assertIn("function wbApiFirst(b)", board)
        guard = board.index("if(wbApiFirst(b)){wbApiFirstNotice(b);return;}")
        loader = board.index("const s=document.createElement(\"script\");")
        self.assertLess(guard, loader, "API-first 门必须在加载 board.js 之前生效")
        self.assertIn('getParam("offline")!=="1"', board)
        self.assertIn("offline_full_projection", board)
        # 前端错误提示必须明确“不回退 legacy/historical”
        self.assertIn("legacy board", client)
        self.assertIn("historical", client)
        for text in (items, client):
            self.assertNotIn("data/boards", text)


class EntityDetail(_Server):
    def test_6_item_detail_provenance(self):
        _c, _s, d = self._get("/api/entity", {"kind": "item", "id": 150005})
        for sec in ("identity", "data", "source", "raw_presence", "evidence", "provenance", "residuals", "media"):
            self.assertIn(sec, d["sections"])
        self.assertEqual(d["sections"]["identity"]["name"], "新币")
        self.assertEqual(d["sections"]["identity"]["item_namespace"], "common_item")
        self.assertTrue(d["sections"]["provenance"]["row"]["package_sha256"].startswith("ba8a239a"))
        self.assertEqual(d["sections"]["media"]["status"], "not_implemented")

    def test_7_ba8a_basis_visible_and_current_not_overclaimed(self):
        _c, _s, d = self._get("/api/entity", {"kind": "item", "id": 102602})
        src = d["sections"]["source"]
        self.assertIn("BA8A", str(src["snapshot_basis"]))
        self.assertTrue(src["snapshot_basis_explicit"])
        self.assertNotEqual(src["current_snapshot_binding"]["status"], "ok",
                            "current 物理绑定未验证时不得显示 ok")
        st = d["sections"]["identity"]
        self.assertEqual(st["name_status"], "unresolved")
        # 前端必须分别显示两条硬规则字段
        client = (ROOT / "assets" / "workbench_client.js").read_text(encoding="utf-8")
        self.assertIn("Snapshot basis", client)
        self.assertIn("Current snapshot binding", client)
        self.assertIn("wb-snapshotbox", client)

    def test_entity_kinds_supported(self):
        for params in ({"kind": "weapon_skin", "id": 1110001},
                       {"kind": "lottery_pool", "id": 390000},
                       {"kind": "lottery_reward", "pool_key": 390000, "item_no": 0}):
            code, _s, d = self._get("/api/entity", params)
            self.assertEqual(code, 200, params)
            self.assertEqual(d["kind"], params["kind"])
            self.assertIn("media", d["sections"])

    def test_fashion_has_no_entity_detail(self):
        """fashion 是状态型页面，不伪造 entity detail（API 明确 404）。"""
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._get("/api/entity", {"kind": "fashion", "id": 1})
        self.assertEqual(ctx.exception.code, 404)
        body = json.loads(ctx.exception.read().decode("utf-8"))
        self.assertIn("error", body)


class CoverageAndContract(_Server):
    def test_11_projection_profiles_and_web_client_registry(self):
        m = json.loads((ROOT / "data" / "workbench_manifest.json").read_text(encoding="utf-8"))
        by = {p["projection_id"]: p for p in m["projections"]}
        for pid in ("item_master_active", "lottery_pool_active", "lottery_rewards_active"):
            self.assertEqual(by[pid]["profile"], "offline_full_projection")
            self.assertFalse(by[pid]["web_default"])
        for pid in ("item_stats", "lottery_stats", "fashion_active"):
            self.assertEqual(by[pid]["profile"], "lightweight")
            self.assertTrue(by[pid]["web_default"])
        # 2026-09-13：武器皮肤图鉴唯一入口 = weapon_skin_sfx_text_sources（115，当前包基准）；
        # weapon_skin_active（126 active 结构）降为内部审计投影：不进 lightweight、不默认展示、不列出。
        self.assertEqual(by["weapon_skin_active"]["profile"], "internal")
        self.assertFalse(by["weapon_skin_active"]["web_default"])
        self.assertNotIn("weapon_skin_active", m["profiles"]["lightweight"])
        self.assertIn("weapon_skin_active", by)  # 文件仍生成，供审计直链使用
        web = json.loads((ROOT / "registry" / "web_client.json").read_text(encoding="utf-8"))
        self.assertEqual(set(web["api_first_boards"]),
                         {"item_master_active", "lottery_pool_active", "lottery_rewards_active"})
        self.assertEqual(set(web["view_modes"]), {"wiki", "workbench"})
        self.assertEqual(web["view_modes"]["workbench"]["shares_data_with"], "wiki")

    def test_12_coverage_endpoint_from_registry(self):
        _c, _s, d = self._get("/api/coverage")
        self.assertEqual(d["workbench_version"], "v1.3")
        cov = d["snapshot_table_coverage"]
        self.assertIn("test-documents-ba8a239a", cov)
        self.assertIn("test-documents-328b8446", cov)
        self.assertGreater(cov["test-documents-ba8a239a"]["ok"], 10)
        self.assertEqual(cov["test-documents-ba8a239a"]["not_ok"], 0)
        self.assertEqual(d["unresolved_counts"]["item"]["unresolved_namespace_ids"]["count"], 554)
        self.assertEqual(d["unresolved_counts"]["lottery"]["unresolved_targets"]["count"], 1665)
        item = [a for a in d["active_artifacts"] if a["artifact"].endswith("item/ITEM_MASTER.jsonl")][0]
        self.assertEqual(item["rows"], ITEM_ROWS)
        self.assertEqual(item["sha256"], _h(ROOT / "artifacts" / "active" / "item" / "ITEM_MASTER.jsonl"))
        self.assertIsNotNone(d["regression"])

    def test_10_api_is_read_only(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/items", data=b"{}",
                                     headers={"Content-Type": "application/json"}, method="POST")
        try:
            urllib.request.urlopen(req, timeout=30)
            self.fail("POST 应被拒绝（只读服务）")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 405)
        server = (ROOT / "api" / "server.py").read_text(encoding="utf-8")
        self.assertIn("read_only", server)
        for rel in ("wiki.html", "board.html"):
            self.assertNotIn("method:'POST'", (ROOT / rel).read_text(encoding="utf-8"))


class BoundaryGuardV13(unittest.TestCase):
    def test_9_services_never_touch_legacy_paths(self):
        from services import (CoverageService, EntityService, FashionService, ItemService,
                              LotteryService, StatusService, WeaponSkinService)
        touched: list[str] = []
        real_read = pathlib.Path.read_text
        real_open = builtins.open

        def spy_read(self, *a, **k):
            touched.append(str(self))
            return real_read(self, *a, **k)

        def spy_open(file, *a, **k):
            touched.append(str(file))
            return real_open(file, *a, **k)

        pathlib.Path.read_text = spy_read
        builtins.open = spy_open
        try:
            it = ItemService()
            it.count(); it.facets(); it.page(page_size=2); it.page(q="新币"); it.get_item(150005); it.residual()
            sk = WeaponSkinService(); sk.list_skins(2)
            fa = FashionService(); fa.status()
            lo = LotteryService()
            lo.pool_stats(); lo.pools_page(page_size=2); lo.reward_targets_page(page_size=2, unresolved_only=True)
            lo.reward_targets_page(item_namespace="common_item"); lo.get_target(390000, 0); lo.residual()
            st = StatusService(); st.status(); st.residual_manifest()
            en = EntityService()
            for kind, ident, kw in (("item", 150005, {}), ("weapon_skin", 1110001, {}),
                                    ("lottery_pool", 390000, {}), ("lottery_reward", None, {"pool_key": 390000, "item_no": 0})):
                en.detail(kind, ident, **kw)
            CoverageService().coverage()
        finally:
            pathlib.Path.read_text = real_read
            builtins.open = real_open
        offenders = [p for p in touched if any(bad in p.replace("/", "\\") for bad in FORBIDDEN)]
        self.assertEqual(offenders, [], f"service 读取了 legacy 数据：{offenders[:5]}")
        self.assertTrue(touched)

    def test_9b_webclient_does_not_decide_business_state(self):
        """前端不得自己推 namespace / join / verified / target 类型。"""
        client = (ROOT / "assets" / "workbench_client.js").read_text(encoding="utf-8")
        for bad in ("raw_presence &&", "item_namespace =", "reward_target_type =", "business_identity ="):  # 赋值/推断
            self.assertNotIn(bad, client, f"前端出现业务推断：{bad}")
        for page in ("workbench_items.html", "workbench_lottery.html", "workbench_entity.html"):
            text = (ROOT / page).read_text(encoding="utf-8")
            self.assertIn("assets/workbench_client.js", text)
            self.assertIn("WB.api", text)


class CliV13(unittest.TestCase):
    def test_cli_paged_items_and_entity(self):
        import subprocess
        r1 = subprocess.run([sys.executable, "-m", "api.cli", "items", "--page-size", "2"],
                            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r1.returncode, 0, r1.stderr[-300:])
        d = json.loads(r1.stdout)
        self.assertEqual(d["total"], ITEM_ROWS)
        self.assertEqual(len(d["items"]), 2)
        r2 = subprocess.run([sys.executable, "-m", "api.cli", "entity", "item", "150005"],
                            cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(r2.returncode, 0, r2.stderr[-300:])
        self.assertIn("新币", r2.stdout)


if __name__ == "__main__":
    unittest.main()
