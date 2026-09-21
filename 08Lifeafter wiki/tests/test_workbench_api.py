"""Workbench API / service 层测试 + 数据边界守护（Phase 9）。

守护目标：**web client cannot become business truth source**
- 运行时证明：任何 service 查询过程都不读取 legacy board / historical / 日志 / raw package / LOCATOR DB
- 静态证明：越界路径直接抛 AccessBoundaryError
"""
from __future__ import annotations

import builtins
import json
import pathlib
import sys
import threading
import unittest
import urllib.request
from http.server import ThreadingHTTPServer

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FORBIDDEN_SUBSTRINGS = ("data/boards", "data\\boards", "historical", "06（agent写）", ".db", "script.py314", "script.py3", "03拆包产物")


class BoundaryGuard(unittest.TestCase):
    def test_assert_allowed_blocks_legacy(self):
        from services.store import AccessBoundaryError, assert_allowed
        for bad in (ROOT / "data" / "boards" / "item_master_v01.json",
                    ROOT / "artifacts" / "historical" / "item" / "v01" / "ITEM_MASTER.jsonl",
                    ROOT / "data" / "NAME_LOCATOR.db"):
            with self.assertRaises(AccessBoundaryError):
                assert_allowed(bad)

    def test_services_never_touch_legacy_paths(self):
        from services import FashionService, ItemService, LotteryService, StatusService, WeaponSkinService

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
            items = ItemService()
            items.count(); items.namespaces(); items.get_item(150005); items.search("", None, 3); items.residual()
            skin = WeaponSkinService()
            skin.count(); skin.list_skins(2); skin.get_skin(1110001); skin.residual()
            fash = FashionService(); fash.status(); fash.residual()
            lot = LotteryService(); lot.pool_stats(); lot.get_pool(390000, 1); lot.reward_targets(None, "unresolved", 2); lot.residual()
            st = StatusService(); st.status(); st.chains(); st.sources(); st.snapshots(); st.namespaces(); st.evidence_list(); st.residual_manifest()
        finally:
            pathlib.Path.read_text = real_read
            builtins.open = real_open

        offenders = [p for p in touched if any(bad in p.replace("/", "\\") for bad in FORBIDDEN_SUBSTRINGS)]
        self.assertEqual(offenders, [], f"service 读取了 legacy 数据：{offenders[:5]}")
        self.assertTrue(touched, "spy 未记录到任何读取，测试无效")

    def test_api_modules_do_not_reference_boards(self):
        for rel in ("services/store.py", "services/item_service.py", "services/weapon_skin_service.py",
                    "services/fashion_service.py", "services/lottery_service.py", "services/status_service.py",
                    "api/server.py", "api/cli.py"):
            text = (ROOT / rel).read_text(encoding="utf-8")
            # 只查“真实路径用法”，不误伤 store.py 里守卫常量的字面量定义
            for marker in ('REPO / "data" / "boards"', "data/boards/", "historical/item", "NAME_LOCATOR"):
                self.assertNotIn(marker, text, f"{rel} 引用了 legacy 路径标记 {marker}")


class ApiEndpoints(unittest.TestCase):
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

    def _get(self, path):
        with urllib.request.urlopen(f"http://127.0.0.1:{self.port}{path}", timeout=30) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8"))

    def test_status_and_registries(self):
        for path in ("/api/health", "/api/status", "/api/chains", "/api/namespaces", "/api/sources", "/api/manifest"):
            code, data = self._get(path)
            self.assertEqual(code, 200, path)
            self.assertNotIn("error", data, path)

    def test_item_queries_use_active_30251(self):
        code, status = self._get("/api/status")
        self.assertEqual(status["domains"]["item"]["rows"], 30467)
        code, one = self._get("/api/items/150005")
        self.assertEqual(one["item_id"], 150005)
        self.assertEqual(one["name"], "新币")
        self.assertEqual(one["item_namespace"], "common_item")
        code, listing = self._get("/api/items?limit=3")
        self.assertGreater(listing["total"], 30000)

    def test_domain_endpoints(self):
        for path in ("/api/weapon-skins?limit=2", "/api/fashion/status", "/api/lottery/pools",
                     "/api/lottery/rewards?type=unresolved&limit=2", "/api/residuals", "/api/residuals?domain=fashion", "/api/evidence"):
            code, data = self._get(path)
            self.assertEqual(code, 200, path)
            self.assertNotIn("error", data, path)

    def test_fashion_not_faked_as_resolved(self):
        code, data = self._get("/api/fashion/status")
        self.assertEqual(data["kind"], "identity_state_not_resolved")
        self.assertEqual(data["unresolved"]["business_identity"], "unresolved")

    def test_lottery_layers_stay_separate(self):
        code, pools = self._get("/api/lottery/pools")
        self.assertIn("records", pools)
        code, rewards = self._get("/api/lottery/rewards?limit=1")
        self.assertIn("targets", rewards)
        self.assertIn("runtime_final_status", rewards["targets"][0])
        self.assertNotIn("item_master_id", rewards["targets"][0])

    def test_unknown_endpoint_404(self):
        try:
            self._get("/api/does-not-exist")
            self.fail("应返回 404")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)


class CliWithoutWiki(unittest.TestCase):
    def test_cli_runs_standalone(self):
        import subprocess
        out = subprocess.run([sys.executable, "-m", "api.cli", "item", "150005"], cwd=str(ROOT),
                             capture_output=True, text=True, encoding="utf-8", timeout=300)
        self.assertEqual(out.returncode, 0, out.stderr[-400:])
        self.assertIn("新币", out.stdout)


if __name__ == "__main__":
    unittest.main()
