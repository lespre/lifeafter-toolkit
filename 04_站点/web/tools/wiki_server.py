# -*- coding: utf-8 -*-
"""127.0.0.1-only server for the LifeAfter Wiki and lazy script NPK inspection.

There is intentionally no route for downloading raw NPK payloads, triggering a
full extraction, or writing source packages. The API exposes source locks,
index metadata, and one on-demand entry summary at a time.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from datetime import datetime
from functools import partial
import concurrent.futures as _tp
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, unquote, urlparse

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))

from live_npk_reader import LiveNpkReader, NpkFormatError, SourceChangedError
from publication_policy import is_openable_board

API_VERSION = "v1"
SAFE_STATIC_DENY_PREFIXES = {"tools", "tests", "docs", ".git"}
SAFE_STATIC_DENY_PATHS = {"data/live_sources.json"}
_BOARD_ASSET_RE = re.compile(r"^data/boards/([A-Za-z0-9_-]+)\.(?:json|js)$")

# ---------------------------------------------------------------- 主页实时快照
# 取数逻辑只保留一套：这里 **复用** gen_home.collect()，不重写第二套菜单。
# 采集一次实测约 1.5 秒（其中索引状态 ~1.2 秒），因此 15 秒缓存足够让页面「几乎无感」。
HOME_SNAPSHOT_TTL_SECONDS = 15.0
# 独立后端 api/server.py（工作台 API）的默认地址：/api/coverage 在那里，8765 只做只读转发。
WORKBENCH_API_DEFAULT = "http://127.0.0.1:8770"
WORKBENCH_API_TIMEOUT_SECONDS = 30.0

# ★ 服务器时间：直接抓网易各服的 HTTP Date 头（与客户端一致的判据）
_SERVER_TIME_TTL = 20.0
_server_time_cache: dict[str, Any] = {}
_server_time_lock = threading.Lock()
SERVER_TIME_ENDPOINTS = {
    "release": ("正式服", "https://g66.update.netease.com/pl/npk_version_newpc4"),
    "playertest": ("测试服", "https://g66.update.netease.com/pl/npk_version_newpc4_playertest"),
    "futuretest": ("未来测试服", "https://g66.update.netease.com/pl/npk_version_newpc4_futuretest"),
    "bisai": ("比赛服", "https://g66.update.netease.com/pl/npk_version_newpc4_playertest_bisai"),
    "kol_zy": ("KOL服", "https://g66.update.netease.com/pl/npk_version_newpc4_playertest_kol_zy"),
}


def _fetch_one_server_time(key: str) -> dict[str, Any]:
    """抓一个服的 HTTP Date 头 → 服务器时间。"""
    label, url = SERVER_TIME_ENDPOINTS[key]
    out: dict[str, Any] = {"key": key, "label": label, "url": url, "ok": False}
    try:
        req = urllib.request.Request(url, method="GET", headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.headers.get("Date") or ""
        if raw:
            import email.utils as _eu
            dt = _eu.parsedate_to_datetime(raw)
            if dt is not None:
                local = dt.astimezone()
                out.update({
                    "ok": True,
                    "date_raw": raw,
                    "utc": dt.strftime("%Y-%m-%d %H:%M:%S"),
                    "local": local.strftime("%Y-%m-%d %H:%M:%S"),
                    "epoch": int(dt.timestamp()),
                    "delta_seconds": int((local - datetime.now().astimezone()).total_seconds()),
                })
    except Exception as exc:  # noqa: BLE001 - 只读探测，失败如实返回
        out["error"] = str(exc)[:120]
    return out


def _server_time_snapshot() -> dict[str, Any]:
    """实时返回各服服务器时间（20 秒内复用缓存）。"""
    now = time.time()
    with _server_time_lock:
        cached = _server_time_cache.get("payload")
        if cached and now - _server_time_cache.get("at", 0) < _SERVER_TIME_TTL:
            return cached
    rows: list[dict[str, Any]] = []
    with _tp.ThreadPoolExecutor(max_workers=len(SERVER_TIME_ENDPOINTS)) as pool:
        for row in pool.map(_fetch_one_server_time, list(SERVER_TIME_ENDPOINTS)):
            rows.append(row)
    payload = {
        "api_version": API_VERSION,
        "read_only": True,
        "fetched_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "HTTP Date 响应头（与客户端同源）",
        "servers": rows,
    }
    with _server_time_lock:
        _server_time_cache["payload"] = payload
        _server_time_cache["at"] = now
    return payload


_home_snapshot_cache: dict[str, Any] = {"payload": None, "at": 0.0}
_home_snapshot_lock = threading.Lock()


class HomeSnapshotError(RuntimeError):
    """主页快照采集失败——如实上报，绝不返回编造数值。"""


def _home_snapshot_unreadable(data: dict[str, Any]) -> list[str]:
    """如实列出本次采集读不到的字段（None / 空 ⇒ 读取失败）；不填默认值、不猜。"""
    checks = [
        ("索引行数", data.get("rows")),
        ("快速校验", data.get("quick")),
        ("数据新鲜", data.get("stale")),
        ("失败容器", data.get("failed_containers")),
        ("工具数", data.get("tools")),
        ("统一入口子命令", data.get("entries")),
        ("站点页面", data.get("pages")),
        ("皮肤资产目录数", data.get("skin_assets")),
        ("交付区体积", data.get("size_deliver")),
        ("源包区体积", data.get("size_source")),
        ("源包文件数", data.get("files_source")),
        ("审阅区体积", data.get("size_review")),
        ("待清理区体积", data.get("size_clean")),
    ]
    missing = [name for name, value in checks if value is None or value == [] or value == {}]
    backlog = data.get("backlog") or {}
    if backlog.get("open") is None or backlog.get("done") is None:
        missing.append("待修清单")
    if data.get("index_from") == "读取失败":
        missing.append("索引状态来源")
    return missing


_GEN_HOME_SIG = None


def _load_gen_home():
    """加载站点唯一的取数实现；文件变了就重新加载。

    ★ 为什么需要：import gen_home 之后模块被 sys.modules 缓存，改 gen_home.py
      不会生效，端点会一直跑旧代码。实测踩过 —— 新加的 lanes / ref_warnings
      字段在重启服务前拿不到，于是「页面初次生成有内容、实时刷新却没有」，
      看起来像实时功能坏了。这里按 mtime+size 判断，变了就 reload。
    """
    global _GEN_HOME_SIG
    import gen_home
    try:
        st = Path(gen_home.__file__).stat()
        sig = (st.st_mtime_ns, st.st_size)
    except OSError:
        return gen_home
    if _GEN_HOME_SIG is not None and sig != _GEN_HOME_SIG:
        import importlib
        gen_home = importlib.reload(gen_home)
    _GEN_HOME_SIG = sig
    return gen_home


def home_snapshot(force: bool = False, ttl: float = HOME_SNAPSHOT_TTL_SECONDS) -> dict[str, Any]:
    """主页实时数据：复用 gen_home.collect()，15 秒缓存 + 并发锁（同一时刻只跑一次全量采集）。"""
    with _home_snapshot_lock:
        cached = _home_snapshot_cache["payload"]
        age = time.monotonic() - float(_home_snapshot_cache["at"] or 0.0)
        if not force and isinstance(cached, dict) and age < ttl:
            payload = dict(cached)
            payload["cache"] = {"hit": True, "age_seconds": round(age, 3), "ttl_seconds": ttl, "forced": False}
            return payload
        started = time.monotonic()
        try:
            gen_home = _load_gen_home()  # 取数实现，带变更重载
        except Exception as exc:  # noqa: BLE001 - 如实上报，不编造
            raise HomeSnapshotError(f"取数模块 gen_home 加载失败：{exc.__class__.__name__}: {exc}") from exc
        try:
            gen_home.FAILS.clear()  # collect() 把失败项累积在模块级列表，每次采集前清空，避免跨请求累积
            data = gen_home.collect()
        except Exception as exc:  # noqa: BLE001 - 如实上报，不编造
            raise HomeSnapshotError(f"gen_home.collect() 采集失败：{exc.__class__.__name__}: {exc}") from exc
        elapsed = round(time.monotonic() - started, 3)
        collected = datetime.now()
        payload = {
            "api_version": API_VERSION,
            "endpoint": "/api/home/snapshot",
            "read_only": True,
            "collector": "gen_home.collect()",
            "collect_seconds": elapsed,
            "collected_at": collected.strftime("%Y-%m-%d %H:%M:%S"),
            "collected_at_epoch": round(collected.timestamp(), 3),
            "failed_items": {
                "read_errors": list(data.get("fails") or []),
                "unreadable_fields": _home_snapshot_unreadable(data),
                "index_status_from": data.get("index_from"),
            },
            "data": data,
            "cache": {"hit": False, "age_seconds": 0.0, "ttl_seconds": ttl, "forced": bool(force)},
        }
        _home_snapshot_cache["payload"] = payload
        _home_snapshot_cache["at"] = time.monotonic()
        return payload


class SourceLockMismatchError(RuntimeError):
    """The configured source lock no longer matches the physical package."""


class RegisteredSource:
    def __init__(self, definition: dict[str, Any]):
        required = {"source_id", "label", "kind", "server_branch", "path", "expected_sha256", "expected_bytes"}
        missing = sorted(required.difference(definition))
        if missing:
            raise ValueError(f"live source missing keys: {', '.join(missing)}")
        if definition["kind"] != "script_npk":
            raise ValueError(f"unsupported live source kind: {definition['kind']}")
        self.definition = definition
        self.reader = LiveNpkReader(definition["path"], definition["server_branch"])

    @property
    def source_id(self) -> str:
        return self.definition["source_id"]

    def _lock_state(self) -> str:
        expected_hash = self.definition["expected_sha256"].lower()
        expected_bytes = int(self.definition["expected_bytes"])
        if self.reader.package_sha256 != expected_hash or self.reader.source_metadata()["bytes"] != expected_bytes:
            return "mismatch"
        return "verified"

    def metadata(self) -> dict[str, Any]:
        metadata = self.reader.source_metadata()
        metadata.update({
            "source_id": self.source_id,
            "label": self.definition["label"],
            "kind": self.definition["kind"],
            "source_kind": self.definition.get("source_kind", "unspecified"),
            "client_role": self.definition.get("client_role", "unspecified"),
            "snapshot_role": self.definition.get("snapshot_role", "unspecified"),
            "expected_sha256": self.definition["expected_sha256"],
            "expected_bytes": int(self.definition["expected_bytes"]),
            "source_lock_state": self._lock_state(),
        })
        return metadata

    def _require_verified_lock(self) -> None:
        if self._lock_state() != "verified":
            raise SourceLockMismatchError(
                "physical source does not match live_sources.json; update the source lock only after a new audit"
            )

    def list_entries(self, **kwargs: Any) -> dict[str, Any]:
        self._require_verified_lock()
        return self.reader.list_entries(**kwargs)

    def inspect_entry(self, entry_index: int) -> dict[str, Any]:
        self._require_verified_lock()
        return self.reader.inspect_entry(entry_index)


class WikiContext:
    def __init__(self, wiki_root: Path | str, sources_path: Path | str,
                 workbench_api: str = WORKBENCH_API_DEFAULT):
        self.wiki_root = Path(wiki_root).resolve()
        self.sources_path = Path(sources_path).resolve()
        # 独立后端（api/server.py）地址；8765 只做只读转发，不复制它的取数逻辑
        self.workbench_api = (workbench_api or WORKBENCH_API_DEFAULT).rstrip("/")
        if not self.wiki_root.is_dir():
            raise FileNotFoundError(f"Wiki root missing: {self.wiki_root}")
        raw = json.loads(self.sources_path.read_text(encoding="utf-8"))
        if raw.get("schema_version") not in {2, 3} or not isinstance(raw.get("sources"), list):
            raise ValueError("unsupported live source registry schema")
        self.sources: dict[str, RegisteredSource] = {}
        self.publication_policy_path = self.wiki_root / "data" / "publication_policy.json"
        for item in raw["sources"]:
            if not isinstance(item, dict):
                raise ValueError("live source registry sources must be objects")
            # Historical/full fallback packages stay auditable in the registry,
            # but are deliberately not opened or hashed by the default browser
            # endpoint. Enabling one is an explicit, read-only source review.
            if item.get("reader_enabled", True) is not True:
                continue
            source = RegisteredSource(item)
            if source.source_id in self.sources:
                raise ValueError(f"duplicate source_id: {source.source_id}")
            self.sources[source.source_id] = source

    def resolve_source(self, source_id: str) -> RegisteredSource:
        try:
            return self.sources[source_id]
        except KeyError as exc:
            raise KeyError(f"unknown source: {source_id}") from exc


class WikiRequestHandler(SimpleHTTPRequestHandler):
    """Static Wiki handler with a narrow, source-locked localhost API."""

    def __init__(self, *args: Any, context: WikiContext, **kwargs: Any):
        self.context = context
        super().__init__(*args, directory=str(context.wiki_root), **kwargs)

    def log_message(self, format: str, *args: Any) -> None:  # pragma: no cover - noisy integration detail
        print("[wiki] " + (format % args))

    def end_headers(self) -> None:
        """开发服务器：静态资源一律禁缓存，保证前端改动刷新即生效（避免拿到旧 JS/CSS/GLB）。"""
        buffered = getattr(self, "_headers_buffer", None) or []
        if not any(b"Cache-Control" in chunk for chunk in buffered):
            self.send_header("Cache-Control", "no-store, must-revalidate")
            self.send_header("Pragma", "no-cache")
        super().end_headers()

    def _json(self, payload: dict[str, Any], status: int | HTTPStatus = HTTPStatus.OK) -> None:
        body = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.send_response(status.value if isinstance(status, HTTPStatus) else int(status))
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _error(self, status: HTTPStatus, code: str, message: str) -> None:
        self._json({"error": {"code": code, "message": message}, "api_version": API_VERSION}, status)

    def do_GET(self) -> None:  # noqa: N802 - stdlib handler signature
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/"):
            self._handle_api(parsed)
            return
        self._handle_static(parsed.path)

    def _handle_api(self, parsed) -> None:
        try:
            parts = [unquote(part) for part in parsed.path.strip("/").split("/")]
            query = parse_qs(parsed.query, keep_blank_values=True)
            if parts == ["api", "health"]:
                self._json({
                    "api_version": API_VERSION,
                    "status": "ok",
                    "bind": self.server.server_address[0],
                    "read_only": True,
                    "source_count": len(self.context.sources),
                    "raw_payload_download": False,
                    "full_extract": False,
                    "home_snapshot_route": "/api/home/snapshot",
                    "home_snapshot_ttl_seconds": HOME_SNAPSHOT_TTL_SECONDS,
                    "workbench_api": self.context.workbench_api,
                })
                return
            if parts == ["api", "server_time"]:
                # ★ 实时抓网易各服 HTTP Date 头（服务器时间）
                self._json(_server_time_snapshot())
                return
            if parts == ["api", "sources"]:
                self._json({
                    "api_version": API_VERSION,
                    "read_only": True,
                    "sources": [source.metadata() for source in self.context.sources.values()],
                })
                return
            if len(parts) == 4 and parts[0:2] == ["api", "sources"] and parts[3] == "entries":
                source = self.context.resolve_source(parts[2])
                offset = self._int_query(query, "offset", 0)
                limit = self._int_query(query, "limit", 50)
                q = query.get("q", [""])[0]
                self._json(source.list_entries(offset=offset, limit=limit, query=q))
                return
            if len(parts) == 6 and parts[0:2] == ["api", "sources"] and parts[3] == "entries" and parts[5] == "summary":
                source = self.context.resolve_source(parts[2])
                self._json(source.inspect_entry(int(parts[4])))
                return
            # 主页实时数据：复用 gen_home.collect()，15 秒缓存，?force=1 绕过缓存
            if parts == ["api", "home", "snapshot"]:
                self._home_snapshot(self._flag_query(query, "force"))
                return
            # /api/coverage 属于独立后端 api/server.py（默认 127.0.0.1:8770）：只读转发，不复制其逻辑
            if parts == ["api", "coverage"]:
                self._workbench_coverage()
                return
            self._error(HTTPStatus.NOT_FOUND, "route_not_found", "API route not found")
        except SourceChangedError as exc:
            self._error(HTTPStatus.CONFLICT, "source_changed", str(exc))
        except SourceLockMismatchError as exc:
            self._error(HTTPStatus.CONFLICT, "source_lock_mismatch", str(exc))
        except KeyError as exc:
            self._error(HTTPStatus.NOT_FOUND, "source_not_found", str(exc))
        except IndexError as exc:
            self._error(HTTPStatus.NOT_FOUND, "entry_not_found", str(exc))
        except (ValueError, NpkFormatError) as exc:
            self._error(HTTPStatus.BAD_REQUEST, "invalid_request", str(exc))
        except Exception as exc:  # pragma: no cover - safety net for local API only
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "internal_error", repr(exc))

    @staticmethod
    def _int_query(query: dict[str, list[str]], name: str, default: int) -> int:
        values = query.get(name)
        if not values or values[0] == "":
            return default
        return int(values[0])

    @staticmethod
    def _flag_query(query: dict[str, list[str]], name: str) -> bool:
        values = query.get(name)
        return bool(values) and str(values[0]).strip().lower() in {"1", "true", "yes", "on"}

    def _home_snapshot(self, force: bool) -> None:
        try:
            payload = home_snapshot(force=force)
        except HomeSnapshotError as exc:
            self._error(HTTPStatus.INTERNAL_SERVER_ERROR, "home_snapshot_failed", str(exc))
            return
        self._json(payload)

    @staticmethod
    def _proxy_error_payload(code: str, message: str, detail: str) -> dict[str, Any]:
        """转发端点专用的错误形状：workbench_client.js 读的是字符串 `error` + `detail`
        （写成 wiki_server 默认的 {code,message} 对象，页面只会显示「[object Object]」）。"""
        return {"error": message, "detail": detail, "code": code, "api_version": API_VERSION}

    def _workbench_coverage(self) -> None:
        """把 /api/coverage 只读转发给独立后端（api/server.py，默认 127.0.0.1:8770）。

        后端没起时明确回「未连接 + 启动方式」，既不伪造覆盖度数据，也不吞掉错误。
        """
        url = f"{self.context.workbench_api}/api/coverage"
        raw = b""
        status_code = 200
        try:
            with urllib.request.urlopen(url, timeout=WORKBENCH_API_TIMEOUT_SECONDS) as response:
                status_code = getattr(response, "status", 200) or 200
                raw = response.read()
        except urllib.error.HTTPError as exc:
            status_code = exc.code
            try:
                raw = exc.read()
            except Exception:  # noqa: BLE001
                raw = b""
        except Exception as exc:  # noqa: BLE001 - 后端未连接/超时
            self._json(
                self._proxy_error_payload(
                    "workbench_api_unavailable",
                    "工作台后端未连接",
                    f"目标 {url}：{exc.__class__.__name__}: {exc}；启动方式：在 04_站点/web 目录执行 "
                    "python -m api.server --host 127.0.0.1 --port 8770",
                ),
                HTTPStatus.SERVICE_UNAVAILABLE,
            )
            return
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            self._json(
                self._proxy_error_payload(
                    "workbench_api_bad_payload",
                    "工作台后端返回的不是 JSON",
                    f"目标 {url}：{exc.__class__.__name__}: {exc}",
                ),
                HTTPStatus.BAD_GATEWAY,
            )
            return
        if isinstance(payload, dict):
            payload = dict(payload)
            payload["proxied_by"] = "wiki_server.py (8765) → " + self.context.workbench_api
        safe_status = status_code if 100 <= status_code <= 599 else 502
        self._json(payload if isinstance(payload, dict) else {"payload": payload}, safe_status)

    def _handle_static(self, raw_path: str) -> None:
        # 站点根默认页：存在新主页 index.html 时用它，否则回落原图鉴首页 wiki.html
        # （/wiki.html 始终直连可达，图鉴功能不受影响）
        default_page = "wiki.html"
        if (Path(self.context.wiki_root) / "index.html").is_file():
            default_page = "index.html"
        normalized = raw_path.lstrip("/") or default_page
        normalized = normalized.replace("\\", "/")
        first = normalized.split("/", 1)[0]
        board_asset = _BOARD_ASSET_RE.fullmatch(normalized)
        if normalized.startswith("data/boards/") and (
            board_asset is None
            or not is_openable_board(self.context.publication_policy_path, board_asset.group(1))   # published_hidden（隐藏审计板）直链可达
        ):
            self.send_error(HTTPStatus.NOT_FOUND.value, "not found")
            return
        if first in SAFE_STATIC_DENY_PREFIXES or normalized in SAFE_STATIC_DENY_PATHS:
            self.send_error(HTTPStatus.NOT_FOUND.value, "not found")
            return
        self.path = "/" + normalized
        super().do_GET()


def create_server(
    wiki_root: Path | str,
    sources_path: Path | str,
    host: str = "0.0.0.0",
    port: int = 8765,
    workbench_api: str | None = None,
) -> ThreadingHTTPServer:
    """Read-only service; caller owns serve_forever/shutdown.
    host 默认 0.0.0.0 —— 允许局域网访问（用户要求，单端口）。只读，无写接口。"""
    context = WikiContext(
        wiki_root,
        sources_path,
        workbench_api=workbench_api or os.environ.get("LA_WORKBENCH_API") or WORKBENCH_API_DEFAULT,
    )
    handler = partial(WikiRequestHandler, context=context)
    server = ThreadingHTTPServer((host, port), handler)
    server.wiki_context = context  # type: ignore[attr-defined]
    return server


def main() -> None:
    wiki_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="LifeAfter Wiki read-only server (LAN-enabled)")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--sources", default=str(wiki_root / "data" / "live_sources.json"))
    parser.add_argument("--workbench", default=os.environ.get("LA_WORKBENCH_API", WORKBENCH_API_DEFAULT),
                        help="/api/coverage 转发目标（独立后端 api/server.py），默认 127.0.0.1:8770")
    args = parser.parse_args()
    server = create_server(wiki_root=wiki_root, sources_path=args.sources, host=args.host, port=args.port,
                           workbench_api=args.workbench)
    print(f"LifeAfter Wiki: http://{args.host}:{args.port}/ (read-only, LAN-enabled)")
    print(f"  主页实时数据: /api/home/snapshot（缓存 {HOME_SNAPSHOT_TTL_SECONDS:.0f} 秒，?force=1 可跳过）")
    print(f"  覆盖度转发:   /api/coverage → {args.workbench}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWiki server stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
