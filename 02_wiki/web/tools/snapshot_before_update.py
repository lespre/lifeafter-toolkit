# -*- coding: utf-8 -*-
"""更新前基线快照：记下当前 PE 源状态，更新后用来做 fid 级 diff。

产出：01_索引与产物/30_分析/baseline_pe_before_update_<日期>.json
"""
from __future__ import annotations

import datetime
import json
import pathlib
import sqlite3

ROOT = pathlib.Path("E:/la拆包项目")
TREE = ROOT / "01_索引与产物/41_还原树/pe"
PKGS = ROOT / "01_索引与产物/源包/pe_gres_android"
INDEX = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
OUT = ROOT / "01_索引与产物/30_分析"


def count_files(p: pathlib.Path) -> int:
    n = 0
    for _ in p.rglob("*"):
        n += 1
    return n


def main() -> int:
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    data = {"snapshot_at": datetime.datetime.now().isoformat(timespec="seconds")}

    # 1) 包清单
    pkgs = []
    for p in sorted(PKGS.glob("*.gpk")):
        st = p.stat()
        pkgs.append({"name": p.name, "size": st.st_size, "mtime": int(st.st_mtime)})
    data["packages"] = {"count": len(pkgs), "total_bytes": sum(x["size"] for x in pkgs), "files": pkgs}

    # 2) 还原树
    cdata = TREE / "配置/com/cdata"
    data["tree"] = {
        "cdata_tables": sum(1 for _ in cdata.glob("*.py")),
        "config_files": count_files(TREE / "配置") if (TREE / "配置").is_dir() else 0,
        "resource_files": count_files(TREE / "资源") if (TREE / "资源").is_dir() else 0,
    }

    # 3) 索引
    if INDEX.is_file():
        try:
            con = sqlite3.connect(INDEX)
            tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
            rows = {}
            for t in tabs[:6]:
                try:
                    rows[t] = con.execute(f"select count(*) from {t}").fetchone()[0]
                except Exception:                       # noqa: BLE001
                    pass
            data["index"] = {"size": INDEX.stat().st_size, "tables": rows}
            con.close()
        except Exception as e:                          # noqa: BLE001
            data["index"] = {"error": str(e)[:120]}
    else:
        data["index"] = {"status": "missing"}

    OUT.mkdir(parents=True, exist_ok=True)
    dst = OUT / f"baseline_pe_before_update_{stamp}.json"
    dst.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")

    print("基线已写：", dst)
    print("包 %d 个 / %.1f GB" % (len(pkgs), data["packages"]["total_bytes"] / 1e9))
    print("还原树：cdata %d 表 ｜ 配置 %d 文件 ｜ 资源 %d 文件"
          % (data["tree"]["cdata_tables"], data["tree"]["config_files"], data["tree"]["resource_files"]))
    print("索引：", data["index"].get("size"), data["index"].get("tables"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
