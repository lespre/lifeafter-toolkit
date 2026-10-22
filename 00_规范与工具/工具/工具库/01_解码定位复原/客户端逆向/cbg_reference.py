# -*- coding: utf-8 -*-
r"""藏宝阁（CBG）前端配置 · 外部参照源的抓取 / 规范化 / 质检。

为什么有它
----------
藏宝阁是网易官方交易站（入口 https://mrzh.cbg.163.com/ ），页面在路由守卫
`gameConfigFirst` 里加载 https://cbg-mrzh.res.netease.com/js/game_auto_config.js
（单行 JS，约 25 MB），挂成 `window.CBG_GAME_CONFIG`。
这份字典是【官方口径的物品名 / 图标 / 品级 / 属性显示定义】，
独立于客户端拆包 ⇒ 正好补「all_equips 文本槽错位、不能拿去命名」的缺口。

★ 它是外部参照，不是拆包数据：
  · 不含战斗数值（没有伤害倍率、属性数值），品级只是交易站展示档位
  · 不进 41_还原树（那边只放从容器还原出来的东西）

落点
----
01_索引与产物/参考资料/藏宝阁_CBG/
  raw/<文件名>              上游原始字节（校验基准，只读）
  json/<顶层键>.json        规范化后一键一文件
  json/_index.json          键 → 条目数 / 字节数 / sha256
  _manifest.json            URL / 抓取时间 / HTTP 头 / sha256 / 大小
  README.md                 来源与边界

用法
----
  python cbg_reference.py fetch          # 下载 raw/ + 写 _manifest.json
  python cbg_reference.py build          # raw/ → json/ + json/_index.json
  python cbg_reference.py check          # 质检：哈希 / 一键一文件 / 可重解析
  python cbg_reference.py all            # fetch + build + check
  python cbg_reference.py keys [--top N] # 列出顶层键与条目数（人看）

退出码：0 = 全过；1 = 有 FAIL 项（check 用）
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.request
from pathlib import Path

for _s in ("stdout", "stderr"):
    try:
        getattr(sys, _s).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass

# ── 路径中心（唯一权威，禁硬编码项目根）────────────────────────────────
TOOLKIT_CORE = Path(__file__).resolve().parents[2] / "00_共享核心"
sys.path.insert(0, str(TOOLKIT_CORE))
try:
    from toolkit_core.paths import PROJECT_ROOT          # noqa: E402
except Exception:                                         # pragma: no cover
    PROJECT_ROOT = Path(__file__).resolve().parents[4]

REF_ROOT = PROJECT_ROOT / "01_索引与产物" / "参考资料" / "藏宝阁_CBG"
RAW_DIR = REF_ROOT / "raw"
JSON_DIR = REF_ROOT / "json"
MANIFEST = REF_ROOT / "_manifest.json"

BASE = "https://cbg-mrzh.res.netease.com/js"
# 键名 = 文件里 `var <KEY>=` 的变量名
SOURCES = {
    "game_auto_config.js": "CBG_GAME_CONFIG",
    "format_game_auto_config.js": "CBG_FORMAT_GAME_CONFIG",
}
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def strip_js(text: str, var: str) -> str:
    """`var CBG_GAME_CONFIG={...};` → `{...}`（容忍 BOM / 空白 / 结尾分号）。"""
    body = text.lstrip("\ufeff").strip()
    for head in (f"var {var}=", f"var {var} =", f"window.{var}=", f"{var}="):
        if body.startswith(head):
            body = body[len(head):]
            break
    else:
        eq = body.find("=")
        if eq < 0:
            raise ValueError(f"找不到赋值号，前 80 字符：{body[:80]!r}")
        body = body[eq + 1:]
    return body.strip().rstrip(";").strip()


def load_ref(dest: Path, var: str):
    text = dest.read_text(encoding="utf-8", errors="strict")
    return json.loads(strip_js(text, var))


# ── fetch ─────────────────────────────────────────────────────────────
def cmd_fetch(_args) -> int:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    man = json.loads(MANIFEST.read_text("utf-8")) if MANIFEST.is_file() else {}
    man.setdefault("_about", {
        "what": "藏宝阁（CBG）明日之后交易站前端配置 = 外部参照源",
        "kind": "official-web-frontend-config",
        "not": "不是拆包数据；不含战斗数值；品级仅为交易站展示档位",
        "entry": "https://mrzh.cbg.163.com/",
        "loaded_by": "dist/main.js 的 gameConfigFirst 守卫（$.getScript）",
        "landed": "01_索引与产物/参考资料/藏宝阁_CBG（外部参照不进 41_还原树）",
    })
    man.setdefault("files", {})
    ok = 0
    for name, var in SOURCES.items():
        url = f"{BASE}/{name}"
        dest = RAW_DIR / name
        print(f"[fetch] {url}")
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        t0 = time.time()
        with urllib.request.urlopen(req, timeout=180) as resp:
            blob = resp.read()
            hdrs = {k: v for k, v in resp.headers.items()
                    if k.lower() in {"content-length", "content-type", "etag",
                                     "last-modified", "cache-control", "server"}}
            status = resp.status
        dest.write_bytes(blob)
        entry = {
            "url": url,
            "var": var,
            "http_status": status,
            "headers": hdrs,
            "bytes": len(blob),
            "sha256": _sha256(dest),
            "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "elapsed_s": round(time.time() - t0, 2),
        }
        old = man["files"].get(name)
        if old and old.get("sha256") != entry["sha256"]:
            entry["prev_sha256"] = old["sha256"]
            entry["prev_fetched_at"] = old.get("fetched_at")
            print(f"  ★ 内容变了：{old['sha256'][:12]}… → {entry['sha256'][:12]}…")
        man["files"][name] = entry
        print(f"  {len(blob):,} B  sha256={entry['sha256'][:16]}…  {entry['elapsed_s']}s")
        ok += 1
    man["checked_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2), "utf-8")
    print(f"[fetch] {ok}/{len(SOURCES)} 完成 → {RAW_DIR}")
    return 0


# ── build ─────────────────────────────────────────────────────────────
def cmd_build(_args) -> int:
    if not RAW_DIR.is_dir():
        print("[build] 先跑 fetch", file=sys.stderr)
        return 1
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    index = {}
    for name, var in SOURCES.items():
        src = RAW_DIR / name
        if not src.is_file():
            print(f"[build] 跳过（raw 缺失）：{name}")
            continue
        obj = load_ref(src, var)
        stem = name[:-3] if name.endswith(".js") else name
        sub = JSON_DIR / stem
        sub.mkdir(parents=True, exist_ok=True)
        per_key = {}
        for key, val in obj.items():
            out = sub / f"{key}.json"
            payload = json.dumps(val, ensure_ascii=False, indent=None,
                                 separators=(",", ":"))
            out.write_text(payload, encoding="utf-8")
            per_key[key] = {
                "n": len(val) if hasattr(val, "__len__") else None,
                "bytes": len(payload.encode("utf-8")),
                "sha256": hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16],
            }
        full = JSON_DIR / f"{stem}.json"
        full.write_text(json.dumps(obj, ensure_ascii=False, separators=(",", ":")),
                        encoding="utf-8")
        index[stem] = {
            "var": var,
            "source_bytes": src.stat().st_size,
            "source_sha256": _sha256(src),
            "top_keys": len(obj),
            "full_json_bytes": full.stat().st_size,
            "keys": dict(sorted(per_key.items())),
        }
        print(f"[build] {stem}: {len(obj)} 个顶层键 → {sub}")
    (JSON_DIR / "_index.json").write_text(
        json.dumps(index, ensure_ascii=False, indent=2), "utf-8")
    print(f"[build] 索引 → {JSON_DIR / '_index.json'}")
    return 0


# ── check ─────────────────────────────────────────────────────────────
def cmd_check(_args) -> int:
    fails, warns = [], []

    if not MANIFEST.is_file():
        fails.append("_manifest.json 不存在（先 fetch）")
        man = {}
    else:
        man = json.loads(MANIFEST.read_text("utf-8"))

    for name, var in SOURCES.items():
        src = RAW_DIR / name
        if not src.is_file():
            fails.append(f"raw 缺失：{name}")
            continue
        sha = _sha256(src)
        rec = man.get("files", {}).get(name, {})
        if not rec:
            fails.append(f"manifest 未登记：{name}")
        elif rec.get("sha256") != sha:
            fails.append(f"{name} sha256 与 manifest 不符"
                         f"（盘上 {sha[:12]}… / 记录 {str(rec.get('sha256'))[:12]}…）")
        elif rec.get("bytes") != src.stat().st_size:
            fails.append(f"{name} 字节数与 manifest 不符")
        else:
            print(f"[check] ✓ {name} sha256 一致 {sha[:16]}… ({src.stat().st_size:,} B)")

        stem = name[:-3]
        sub = JSON_DIR / stem
        try:
            obj = load_ref(src, var)
        except Exception as exc:                       # noqa: BLE001
            fails.append(f"{name} 解析失败：{exc}")
            continue
        if not sub.is_dir():
            fails.append(f"json/{stem}/ 不存在（先 build）")
            continue

        missing, mismatch = [], []
        for key, val in obj.items():
            out = sub / f"{key}.json"
            if not out.is_file():
                missing.append(key)
                continue
            got = json.loads(out.read_text("utf-8"))
            if got != val:
                mismatch.append(key)
        if missing:
            fails.append(f"json/{stem}/ 缺 {len(missing)} 个键：{missing[:5]}")
        if mismatch:
            fails.append(f"json/{stem}/ 有 {len(mismatch)} 个键内容不一致：{mismatch[:5]}")
        if not missing and not mismatch:
            print(f"[check] ✓ {stem}: {len(obj)} 键 / 一键一文件 全部对上")

        # 重复值检测（同名不同 id、同 id 不同名）只作告警
        names = [(k, v.get("name")) for k, v in obj.items()
                 if isinstance(v, dict) and isinstance(v.get("name"), str)]
        dup = {}
        for k, nm in names:
            dup.setdefault(nm, []).append(k)
        heavy = {nm: ids for nm, ids in dup.items() if len(ids) > 6}
        if heavy:
            warns.append(f"{stem}: {len(heavy)} 个名字挂了 >6 个 id"
                         f"（展示名复用，正常；样例 {next(iter(heavy))} → "
                         f"{heavy[next(iter(heavy))][:3]}…）")

        # _classic 双份配对
        bases = {k for k in obj if not k.endswith("_classic")}
        pairs = {k for k in bases if f"{k}_classic" in obj}
        orphan = sorted(bases - pairs)
        if orphan:
            warns.append(f"{stem}: {len(orphan)} 个键没有 _classic 双胞胎：{orphan[:6]}")

    for w in warns:
        print(f"[check] ⚠ {w}")
    for f in fails:
        print(f"[check] ✗ {f}")
    print(f"[check] {'通过' if not fails else f'失败 {len(fails)} 项'}"
          f"（告警 {len(warns)} 项）")
    return 0 if not fails else 1


# ── keys ──────────────────────────────────────────────────────────────
def cmd_keys(args) -> int:
    src = RAW_DIR / "game_auto_config.js"
    obj = load_ref(src, SOURCES["game_auto_config.js"])
    rows = sorted(((len(v) if hasattr(v, "__len__") else 0, k, type(v).__name__)
                   for k, v in obj.items()), reverse=True)
    for n, k, t in rows[: args.top]:
        print(f"{n:>7}  {k:<44} {t}")
    print(f"—— 共 {len(rows)} 个顶层键")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="藏宝阁 CBG 前端配置参照源")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("fetch", help="下载 raw/ 并写 manifest").set_defaults(fn=cmd_fetch)
    sub.add_parser("build", help="raw/ → json/ 一键一文件").set_defaults(fn=cmd_build)
    sub.add_parser("check", help="质检哈希 / 一键一文件 / 可重解析").set_defaults(fn=cmd_check)
    p_all = sub.add_parser("all", help="fetch + build + check")
    p_all.set_defaults(fn=None)
    p_keys = sub.add_parser("keys", help="列顶层键与条目数")
    p_keys.add_argument("--top", type=int, default=30)
    p_keys.set_defaults(fn=cmd_keys)

    args = ap.parse_args(argv)
    if args.cmd == "all":
        rc = cmd_fetch(args) or cmd_build(args) or cmd_check(args)
        return rc
    if not getattr(args, "fn", None):
        ap.print_help()
        return 2
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
