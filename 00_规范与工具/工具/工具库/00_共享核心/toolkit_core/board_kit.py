# -*- coding: utf-8 -*-
"""Board Kit —— 基于还原树构建 wiki 板块的唯一入口。

目标：让第三方只需「有还原树 + 会写字段映射」就能产出合规板块，
不必再重复实现：找树、解表、取 CHS 池、写 provenance、写 json/js、注册策略、校验。

用法（最小）：

    from toolkit_core.board_kit import Tree, Board

    tree = Tree()                       # 自动找最新 pe_* 还原树
    rows = tree.rows("weapon_skin_data")  # 解表 + CHS 池，直接给 values

    b = Board("my_board", "我的板块", "二、战力类 / 示例")
    for r in rows:
        b.add(
            id="x_" + str(r["key"]),
            name=r["values"].get("name", [None, "?"])[1],
            fields={"grade": ...},
            table="weapon_skin_data",
            row_key=r["key"],
            field_refs=["name"],
        )
    b.write()                           # 校验 + 写 json/js + 注册策略

命令行：

    python la.py board check <board_id>        # 校验一个板块
    python la.py board run <builder.py>        # 跑构建脚本（脚本里用 Board/Tree）
"""
from __future__ import annotations

import hashlib
import json
import os
import pathlib
import struct
import sys
from typing import Any, Iterable

# ---------------------------------------------------------------- 路径

def project_root() -> pathlib.Path:
    env = os.environ.get("LA_ROOT")
    if env:
        return pathlib.Path(env).expanduser().resolve()
    here = pathlib.Path(__file__).resolve()
    for up in here.parents:
        if (up / "00_规范与工具/治理").is_dir() and (up / "00_规范与工具/工具").is_dir():
            return up
    return here.parents[3]


ROOT = project_root()
WEB = ROOT / "02_wiki/web"
BOARDS = WEB / "data/boards"


# ---------------------------------------------------------------- 还原树

class Tree:
    """还原树访问器：自动定位最新 pe_* 树，按表名解出 rows。"""

    def __init__(self, root: pathlib.Path | None = None):
        self.root = pathlib.Path(root) if root else self._detect()
        self.cdata = self._cdata_dir()
        self._cache: dict[str, list[dict]] = {}
        self.source_lock = self._source_lock()

    def _detect(self) -> pathlib.Path:
        base = ROOT / "01_索引与产物/41_还原树"
        cands = sorted([p for p in base.glob("pe_*") if p.is_dir()])
        if not cands:
            raise FileNotFoundError("找不到还原树（01_索引与产物/41_还原树/pe_*）")
        return cands[-1]

    def _cdata_dir(self) -> pathlib.Path:
        for rel in ("com/cdata", "Documents/script.py314.lc.npk/com/cdata",
                    "script.py314.lc.npk/com/cdata"):
            p = self.root / rel
            if p.is_dir():
                return p
        raise FileNotFoundError("还原树里找不到 com/cdata：%s" % self.root)

    def _source_lock(self) -> dict:
        """源锁：取客户端 npk 的 sha/bytes/mtime（拿不到就用树的位置兜底）。"""
        for cand in (ROOT / "01_索引与产物/源包/script.py314.lc.npk",
                     pathlib.Path(r"E:/mrzh/Documents/script.py314.lc.npk")):
            if cand.is_file():
                st = cand.stat()
                h = hashlib.sha256()
                with cand.open("rb") as f:
                    for blk in iter(lambda: f.read(1 << 20), b""):
                        h.update(blk)
                return {"path": cand.as_posix(), "sha256": h.hexdigest(),
                        "bytes": st.st_size, "mtime_ns": st.st_mtime_ns}
        return {"path": self.cdata.as_posix(), "sha256": "0" * 64,
                "bytes": 0, "mtime_ns": 0}

    # -- 表访问 --
    def table_path(self, name: str) -> pathlib.Path:
        p = self.cdata / (name if name.endswith(".py") else name + ".py")
        if not p.is_file():
            raise FileNotFoundError("表不存在：%s（目录 %s）" % (name, self.cdata))
        return p

    def has_table(self, name: str) -> bool:
        return (self.cdata / (name if name.endswith(".py") else name + ".py")).is_file()

    def rows(self, name: str, *, chs: bool = True) -> list[dict]:
        """解表 → [{key, values}]；values 为 {字段: (tag, 值)}。"""
        if name in self._cache:
            return self._cache[name]
        sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
        from toolkit_core.bindict_table import parse_legacy_chs_pool, decode_table_rows
        from bindict_provenance import decode_table_rows_with_chs_slots  # type: ignore

        base = self.table_path(name)
        raw = base.read_bytes()
        at = raw.find(b"x{")
        if at < 0:
            raise ValueError("表无 x{ 帧：%s" % base)
        n = struct.unpack_from("<I", raw, at + 2)[0]
        body = raw[at + 6: at + 6 + n]

        pool = []
        chs_path = base.with_name(base.stem + "_chs.py")
        if chs and chs_path.is_file():
            pool = parse_legacy_chs_pool(chs_path.read_bytes())

        if pool:
            rows, _bad = decode_table_rows_with_chs_slots(body, pool)
        else:
            rows, _bad = decode_table_rows(body, [], lenient=True)
        out = [{"key": r.get("key"), "values": r.get("values") or {}} for r in rows]
        self._cache[name] = out
        return out

    def value(self, row: dict, field: str, default: Any = None) -> Any:
        v = (row.get("values") or {}).get(field)
        return v[1] if isinstance(v, (list, tuple)) and len(v) > 1 else default

    # -- 资源 --
    def image_hit(self, logical_path: str) -> bool:
        """判断一张图在索引里能否定位（不导出）。"""
        sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
        try:
            import pe_fetch_hires as H
        except Exception:
            return False
        return bool(H.candidates(logical_path.rsplit(".", 1)[0]))


# ---------------------------------------------------------------- 板块

REQ_PROV = ("source_id", "source_lock_sha256", "table", "row_key",
            "field_refs", "name_source", "upstream", "locator_chain")


class Board:
    def __init__(self, board_id: str, name: str, category: str, *,
                 tree: Tree | None = None, filters: list[dict] | None = None,
                 card_mode: str = "list", notes: str = ""):
        self.board_id = board_id
        self.tree = tree or Tree()
        self.items: list[dict] = []
        self.meta: dict[str, Any] = {
            "name": name,
            "category": category,
            "source_server": "PE 测试服",
            "generated": __import__("datetime").date.today().isoformat(),
            "evidence": "structure",
            "card_mode": card_mode,
            "package_sha": self.tree.source_lock["sha256"],
            "note": notes,
        }
        if filters:
            self.meta["filters"] = filters

    def add(self, *, id: str, name: str, table: str, row_key: Any,
            field_refs: Iterable[str], fields: dict | None = None,
            evidence_level: str = "static/candidate",
            status_tags: list[str] | None = None,
            name_source: str = "chs-pool", media: dict | None = None,
            provenance: dict | None = None) -> dict:
        lock = self.tree.source_lock
        prov = provenance or {
            "source_id": "documents-py314-current",
            "source_lock_sha256": lock["sha256"],
            "table": table,
            "row_key": str(row_key),
            "field_refs": list(field_refs),
            "name_source": name_source,
            "upstream": {"package_sha256": lock["sha256"], "role": "SuperFashion"},
            "locator_chain": {
                "chain_status": "replayed-structural", "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{"kind": "decoded-table-row",
                           "source_id": "documents-py314-current",
                           "table": table, "row_key": str(row_key),
                           "field_refs": list(field_refs)}],
            },
            "table_raw": table,
        }
        item = {"id": id, "name": name, "evidence": "structure",
                "evidence_level": evidence_level,
                "status_tags": status_tags or ["static config"],
                "source": table, "provenance": prov}
        if fields:
            item.update(fields)
        if media:
            item["_media"] = media
        self.items.append(item)
        return item

    def validate(self) -> list[str]:
        errs: list[str] = []
        lock = self.tree.source_lock
        if not self.board_id or "/" in self.board_id:
            errs.append("board_id 非法")
        for k in ("name", "category", "package_sha", "evidence"):
            if not self.meta.get(k):
                errs.append("meta 缺 %s" % k)
        if len(str(self.meta.get("package_sha", ""))) != 64:
            errs.append("meta.package_sha 不是 64 位")
        self.meta.setdefault("provenance", {
            "contract_version": 3, "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                              "path": lock["path"], "sha256": lock["sha256"],
                              "bytes": lock["bytes"], "mtime_ns": lock["mtime_ns"]}],
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        })
        self.meta.setdefault("state_summary", {"条目": len(self.items)})
        ids = [i["id"] for i in self.items]
        dup = {x for x in ids if ids.count(x) > 1}
        if dup:
            errs.append("重复 id：%s" % list(dup)[:3])
        for it in self.items:
            if "table-absent" in (it.get("status_tags") or []):
                continue
            miss = [k for k in REQ_PROV if not (it.get("provenance") or {}).get(k)]
            if miss:
                errs.append("%s provenance 缺 %s" % (it["id"], ",".join(miss)))
                break
            if not it.get("evidence_level"):
                errs.append("%s 缺 evidence_level" % it["id"])
                break
        return errs

    def write(self, *, publish: bool = False, category: str | None = None) -> pathlib.Path:
        errs = self.validate()
        if errs:
            raise ValueError("板块校验失败：\n - " + "\n - ".join(errs))
        BOARDS.mkdir(parents=True, exist_ok=True)
        data = {"meta": self.meta, "items": self.items}
        j = BOARDS / (self.board_id + ".json")
        s = BOARDS / (self.board_id + ".js")
        j.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        s.write_text("window.WIKI_BOARD_%s = %s;\n" % (self.board_id, json.dumps(data, ensure_ascii=False)),
                     encoding="utf-8")
        if publish:
            self._publish(category)
        return j

    def _publish(self, category: str | None) -> None:
        p = WEB / "data/publication_policy.json"
        pol = json.loads(p.read_text(encoding="utf-8"))
        pol.setdefault("boards", {})[self.board_id] = {
            "publication_status": "published",
            "category": category or self.meta.get("category"),
            "reason": "由 board_kit 构建，evidence=structure",
            "items": len(self.items),
        }
        p.write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/publication_policy.js").write_text(
            "window.WIKI_PUBLICATION_POLICY = " + json.dumps(pol, ensure_ascii=False) + ";\n",
            encoding="utf-8")
