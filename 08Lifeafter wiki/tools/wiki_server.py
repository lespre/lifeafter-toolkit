# -*- coding: utf-8 -*-
"""127.0.0.1-only server for the LifeAfter Wiki and lazy script NPK inspection.

There is intentionally no route for downloading raw NPK payloads, triggering a
full extraction, or writing source packages. The API exposes source locks,
index metadata, and one on-demand entry summary at a time.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from functools import partial
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
    def __init__(self, wiki_root: Path | str, sources_path: Path | str):
        self.wiki_root = Path(wiki_root).resolve()
        self.sources_path = Path(sources_path).resolve()
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

    def _json(self, payload: dict[str, Any], status: HTTPStatus = HTTPStatus.OK) -> None:
        body = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        self.send_response(status.value)
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
                    "bind": "127.0.0.1",
                    "read_only": True,
                    "source_count": len(self.context.sources),
                    "raw_payload_download": False,
                    "full_extract": False,
                })
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

    def _handle_static(self, raw_path: str) -> None:
        normalized = raw_path.lstrip("/") or "wiki.html"
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
    host: str = "127.0.0.1",
    port: int = 8765,
) -> ThreadingHTTPServer:
    """Build a localhost-only service; caller owns serve_forever/shutdown."""
    if host != "127.0.0.1":
        raise ValueError("Wiki live reader must bind only to 127.0.0.1")
    context = WikiContext(wiki_root, sources_path)
    handler = partial(WikiRequestHandler, context=context)
    server = ThreadingHTTPServer((host, port), handler)
    server.wiki_context = context  # type: ignore[attr-defined]
    return server


def main() -> None:
    wiki_root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description="LifeAfter Wiki local read-only server")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--sources", default=str(wiki_root / "data" / "live_sources.json"))
    args = parser.parse_args()
    server = create_server(wiki_root=wiki_root, sources_path=args.sources, host=args.host, port=args.port)
    print(f"LifeAfter Wiki: http://{args.host}:{args.port}/ (read-only, localhost only)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nWiki server stopped")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
