# -*- coding: utf-8 -*-
"""HTTP contract for the local, read-only LifeAfter Wiki service."""
from __future__ import annotations

import importlib.util
import json
import sys
import threading
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

WIKI_ROOT = Path(__file__).resolve().parents[1]
SERVER_PATH = WIKI_ROOT / "tools" / "wiki_server.py"
SOURCES_PATH = WIKI_ROOT / "data" / "live_sources.json"


def load_server_module():
    assert SERVER_PATH.exists(), "Wiki 本地 HTTP 服务尚未实现"
    spec = importlib.util.spec_from_file_location("wiki_server", SERVER_PATH)
    assert spec and spec.loader, "无法加载 Wiki 本地 HTTP 服务"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def get_json(url: str) -> dict:
    with urlopen(url, timeout=15) as response:
        assert response.status == 200
        return json.loads(response.read().decode("utf-8"))


class WikiServerContractTests(unittest.TestCase):
    def test_localhost_api_lists_and_inspects_current_source_without_download_route(self):
        """服务必须仅暴露只读元数据/摘要接口，不给原始包下载入口。"""
        module = load_server_module()
        self.assertTrue(SOURCES_PATH.is_file(), "当前源注册表尚未建立")
        server = module.create_server(
            wiki_root=WIKI_ROOT,
            sources_path=SOURCES_PATH,
            host="127.0.0.1",
            port=0,
        )
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address[:2]
        base = f"http://{host}:{port}"
        try:
            health = get_json(base + "/api/health")
            self.assertEqual(health["bind"], "127.0.0.1")
            self.assertTrue(health["read_only"])

            sources = get_json(base + "/api/sources")
            self.assertEqual(len(sources["sources"]), 2)
            source = sources["sources"][0]
            self.assertEqual(source["source_write_policy"], "read_only")
            self.assertRegex(source["package_sha256"], r"^[0-9a-f]{64}$")

            source_id = source["source_id"]
            page = get_json(base + f"/api/sources/{source_id}/entries?offset=0&limit=1")
            entry = page["entries"][0]
            self.assertEqual(page["source_package_sha256"], source["package_sha256"])

            summary = get_json(base + f"/api/sources/{source_id}/entries/{entry['entry_index']}/summary")
            self.assertEqual(summary["evidence_level"], "package_entry_exists")
            self.assertEqual(summary["interpretation_boundary"], "entry_exists_does_not_prove_runtime_activation")
            with self.assertRaises(HTTPError) as blocked:
                urlopen(base + f"/api/sources/{source_id}/raw", timeout=15)
            self.assertEqual(blocked.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_static_board_assets_are_policy_gated(self):
        """隔离 board 的 JSON/JS 不得通过 localhost 静态路径直取。"""
        module = load_server_module()
        server = module.create_server(WIKI_ROOT, SOURCES_PATH, host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address[:2]
        base = f"http://{host}:{port}"
        try:
            with urlopen(base + "/data/boards/weapon_attrs_schema_static.js", timeout=15) as response:
                self.assertEqual(response.status, 200)
            with urlopen(base + "/data/boards/gift_data_text_sources.json", timeout=15) as response:
                self.assertEqual(response.status, 200)
            for suffix in (".js", ".json"):
                with self.assertRaises(HTTPError) as blocked:
                    urlopen(base + "/data/boards/weapon_attrs" + suffix, timeout=15)
                self.assertEqual(blocked.exception.code, 404)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)

    def test_static_wiki_exposes_live_reader_as_a_tool_not_a_catalog_category(self):
        """现场读取入口必须能从首页到达，但不应伪装成新的业务图鉴分类。"""
        module = load_server_module()
        server = module.create_server(WIKI_ROOT, SOURCES_PATH, host="127.0.0.1", port=0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        host, port = server.server_address[:2]
        base = f"http://{host}:{port}"
        try:
            with urlopen(base + "/", timeout=15) as response:
                home = response.read().decode("utf-8")
            self.assertIn('href="live_reader.html"', home)
            with urlopen(base + "/live_reader.html", timeout=15) as response:
                reader_page = response.read().decode("utf-8")
            self.assertIn("本地只读 NPK 检查器", reader_page)
            self.assertIn("包内存在不等于活动已开启", reader_page)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
