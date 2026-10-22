"""Workbench HTTP API + 静态服务（stdlib，无第三方依赖）。

用法：
    python -m api.server --host 127.0.0.1 --port 8770

v1.3：
- 大数据 Domain（item / lottery pools / lottery rewards）默认 **API 分页**，单次响应有硬上限（page_size ≤ 200）；
- 新增 `/api/entity`（统一详情）与 `/api/coverage`（覆盖度/绑定状态）；
- **无写端点**：只读服务，Wiki View 无法通过 API 改业务状态。
"""
from __future__ import annotations

import argparse
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from services import (CoverageService, EntityService, FashionService, ItemService,  # noqa: E402
                      LotteryService, StatusService, WeaponSkinService)
from services.query import PAGE_SIZE_MAX, norm_page  # noqa: E402
from services.store import EVIDENCE, RESIDUALS, load_json  # noqa: E402

STATIC_ROOT = REPO
API_VERSION = "v1.3"


def _int(qs, key, default=None):
    v = qs.get(key, [default])[0]
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


def _flag(qs, key) -> bool:
    v = str(qs.get(key, ["0"])[0]).strip().lower()
    return v in ("1", "true", "yes", "on")


def _str(qs, key, default=None):
    v = qs.get(key, [default])[0]
    return v if v not in ("", None) else default


class Handler(BaseHTTPRequestHandler):
    server_version = "LifeAfterWorkbench/1.3"

    def log_message(self, fmt, *args):  # 安静一点
        if getattr(self.server, "verbose", False):
            super().log_message(fmt, *args)

    # --- helpers ---
    def _json(self, payload, code=200):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _static(self, path: Path):
        if not path.exists() or not path.is_file():
            self._json({"error": "not found", "path": str(path)}, 404)
            return
        ctype = {".html": "text/html; charset=utf-8", ".js": "application/javascript; charset=utf-8",
                 ".css": "text/css; charset=utf-8", ".json": "application/json; charset=utf-8"}.get(path.suffix, "application/octet-stream")
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        if path.suffix in (".html", ".js", ".json"):
            self.send_header("Cache-Control", "no-store")   # 避免用户看到缓存的旧页/旧板
        self.end_headers()
        self.wfile.write(body)

    # --- routes ---
    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        qs = parse_qs(parsed.query)
        path = unquote(parsed.path)
        try:
            if path.startswith("/api/"):
                return self._api(path, qs)
            rel = path.lstrip("/") or "workbench.html"
            target = (STATIC_ROOT / rel).resolve()
            if not str(target).startswith(str(STATIC_ROOT.resolve())):
                return self._json({"error": "forbidden"}, 403)
            return self._static(target)
        except Exception as exc:  # noqa: BLE001
            return self._json({"error": type(exc).__name__, "detail": str(exc)}, 500)

    def do_POST(self):  # noqa: N802
        # 只读服务：Workbench / Wiki View 都不允许通过 API 改业务状态
        self._json({"error": "read_only", "detail": "Workbench API 只读；无写入端点"}, 405)

    def _api(self, path: str, qs):
        status = StatusService()
        if path == "/api/status":
            return self._json(status.status())
        if path == "/api/sources":
            return self._json(status.sources())
        if path == "/api/snapshots":
            return self._json(status.snapshots())
        if path == "/api/namespaces":
            return self._json(status.namespaces())
        if path == "/api/chains":
            return self._json(status.chains())
        if path == "/api/evidence":
            return self._json({"evidence": status.evidence_list()})
        if path == "/api/coverage":
            return self._json(CoverageService().coverage())
        if path == "/api/web-client":
            return self._json(load_json(REPO / "registry" / "web_client.json"))
        if path == "/api/residuals":
            domain = _str(qs, "domain")
            if domain:
                payload = {"domain": domain}
                for name in ("unresolved_namespace_ids", "binding_residuals", "unresolved_ids", "unresolved_targets", "replacement_overlay"):
                    p = RESIDUALS / domain / f"{name}.json"
                    if p.exists():
                        payload[name] = json.loads(p.read_text(encoding="utf-8"))
                return self._json(payload)
            return self._json(status.residual_manifest())

        # --- 统一实体详情（v1.3） ---
        if path == "/api/entity":
            kind = _str(qs, "kind")
            ident = _str(qs, "id")
            row = EntityService().detail(kind, ident, pool_key=_int(qs, "pool_key"), item_no=_int(qs, "item_no"))
            if not row:
                return self._json({"error": "entity not found", "kind": kind, "id": ident}, 404)
            return self._json(row)

        # --- Item（API-first 分页） ---
        if path == "/api/items":
            page, size, clamped = norm_page(page=_int(qs, "page"), page_size=_int(qs, "page_size"),
                                            limit=_int(qs, "limit"), offset=_int(qs, "offset"))
            payload = ItemService().page(q=_str(qs, "q", ""), namespace=_str(qs, "namespace"),
                                        name_status=_str(qs, "name_status"),
                                        identity_status=_str(qs, "identity_status"),
                                        sort=_str(qs, "sort", "item_id"), desc=_flag(qs, "desc"),
                                        page=page, page_size=size)
            payload["clamped"] = payload.get("clamped") or clamped
            return self._json(payload)
        if path.startswith("/api/items/"):
            item_id = _int({"v": [path.rsplit("/", 1)[-1]]}, "v")
            row = ItemService().get_item(item_id) if item_id is not None else None
            return self._json(row) if row else self._json({"error": "item not found", "item_id": item_id}, 404)

        # --- 武器皮肤 ---
        if path == "/api/weapon-skins/status-vocab":
            return self._json(WeaponSkinService().status_vocab())
        if path == "/api/weapon-skins":
            svc = WeaponSkinService()
            sid = _int(qs, "skin_item_id", _int(qs, "id"))
            if sid is not None:
                row = svc.get_skin(sid)
                return self._json(row) if row else self._json({"error": "skin not found", "skin_item_id": sid}, 404)
            paged = any(_str(qs, k) is not None for k in ("page", "page_size", "limit", "offset", "q",
                                                          "listing_status", "name_status", "level", "weapon_type"))
            if not paged:
                return self._json(svc.skins_page(page_size=200))
            page, size, clamped = norm_page(page=_int(qs, "page"), page_size=_int(qs, "page_size"),
                                            limit=_int(qs, "limit"), offset=_int(qs, "offset"))
            payload = svc.skins_page(q=_str(qs, "q", ""), listing_status=_str(qs, "listing_status"),
                                     name_status=_str(qs, "name_status"),
                                     runtime_row_binding=_str(qs, "runtime_row_binding"),
                                     level=_str(qs, "level"), weapon_type=_str(qs, "weapon_type"),
                                     sort=_str(qs, "sort", "skin_item_id"), desc=_flag(qs, "desc"),
                                     page=page, page_size=size)
            payload["clamped"] = payload.get("clamped") or clamped
            return self._json(payload)
        if path == "/api/fashion/status":
            return self._json(FashionService().status())

        # --- Lottery（两层都分页；pool_key 单独给出时保留旧行为） ---
        if path == "/api/lottery/pools":
            svc = LotteryService()
            pk = _int(qs, "pool_key")
            if _flag(qs, "stats"):   # 显式只要统计
                return self._json(svc.pool_stats())
            if pk is not None and not any(_str(qs, k) is not None for k in ("page", "page_size", "limit", "offset", "q", "component")):
                return self._json(svc.get_pool(pk))   # 单池明细（兼容旧调用）
            page, size, clamped = norm_page(page=_int(qs, "page"), page_size=_int(qs, "page_size"),
                                            limit=_int(qs, "limit"), offset=_int(qs, "offset"))
            payload = svc.pools_page(pool_key=pk, component=_str(qs, "component"), q=_str(qs, "q", ""),
                                     sort=_str(qs, "sort", "pool_key"), desc=_flag(qs, "desc"),
                                     page=page, page_size=size)
            payload["clamped"] = payload.get("clamped") or clamped
            payload["records"] = payload["total"]     # 兼容旧键
            payload["stats"] = svc.pool_stats()       # 统计仍随包返回（不含全量行）
            return self._json(payload)
        if path == "/api/lottery/rewards":
            svc = LotteryService()
            page, size, clamped = norm_page(page=_int(qs, "page"), page_size=_int(qs, "page_size"),
                                            limit=_int(qs, "limit"), offset=_int(qs, "offset"))
            payload = svc.reward_targets_page(
                pool_key=_int(qs, "pool_key"),
                reward_target_type=_str(qs, "reward_target_type", _str(qs, "type")),
                item_namespace=_str(qs, "item_namespace"),
                runtime_final_status=_str(qs, "runtime_final_status"),
                unresolved_only=_flag(qs, "unresolved_only") or _flag(qs, "unresolved"),
                q=_str(qs, "q", ""), sort=_str(qs, "sort", "pool_key"), desc=_flag(qs, "desc"),
                page=page, page_size=size)
            payload["clamped"] = payload.get("clamped") or clamped
            return self._json(payload)

        if path == "/api/manifest":
            p = REPO / "data" / "workbench_manifest.json"
            return self._json(json.loads(p.read_text(encoding="utf-8")) if p.exists() else {"error": "manifest not generated"})
        if path == "/api/health":
            return self._json({"ok": True, "service": "workbench-api", "version": API_VERSION,
                               "page_size_max": PAGE_SIZE_MAX, "read_only": True})
        return self._json({"error": "unknown endpoint", "path": path, "routes": sorted(ROUTES)}, 404)


ROUTES = {"/api/status", "/api/sources", "/api/snapshots", "/api/namespaces", "/api/chains", "/api/evidence",
          "/api/coverage", "/api/web-client", "/api/entity", "/api/residuals",
          "/api/items", "/api/items/{item_id}", "/api/weapon-skins", "/api/weapon-skins/status-vocab",
          "/api/fashion/status",
          "/api/lottery/pools", "/api/lottery/rewards", "/api/manifest", "/api/health"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8770)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    httpd.verbose = args.verbose
    print(f"Workbench API {API_VERSION} on http://{args.host}:{args.port}  routes={len(ROUTES)}  page_size_max={PAGE_SIZE_MAX}")
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
