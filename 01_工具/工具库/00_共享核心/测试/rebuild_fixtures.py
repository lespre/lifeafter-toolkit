# -*- coding: utf-8 -*-
"""重建测试夹具：从历史源包解出 007767.bin / 002949.bin。

## 为什么需要这个脚本

tests/test_36_mapping_row.py 与 test_86_detail_row.py 需要两份「工作副本条目」：
    007767.bin  （common_exchange_shop_data, entry 7767）
    002949.bin  （optional_hd_exchange,     entry 2949）

历史上它们放在
    03_执行/30_分析/config_work/script_py314_docs_56def41376ed/entries/
但该目录的实体已被清理，只剩 manifest.json（12 MB 的条目清单）。

★ 关键认识：清单还在 ⇒ 夹具【可以从源包重新解出来】，且可逐字节核验。

## 为什么不能「挑 bin 最多的那份快照」

config_work 下并存 7 份快照，但它们来自【不同版本的 script.py314.lc.npk】。
同一个编号在不同版本里指向不同内容，所以「挑最大的」是错的判据。
本脚本用【清单里的 sha256】锁定唯一正确的那一版源包。

## 产物

    tests/fixtures/script_py314_7767_2949/
        PROVENANCE.json          来源凭据（源包 sha256 + 条目元数据 + 输出 sha256）
        entries/007767.bin
        entries/002949.bin
"""
import sys, importlib.util, hashlib, json, shutil
from pathlib import Path

ROOT = Path(r"E:/la拆包项目/01_工具/工具库")
sys.path.insert(0, str(ROOT  / "00_共享核心"))

MANIFEST = Path(r"E:/la拆包项目/03_执行/30_分析/config_work/"
                r"script_py314_docs_56def41376ed/manifest.json")
SRC_ROOT = Path(r"E:/la拆包项目/02_资料/源包/热更历史容器_20260829-20260916")
# ★ 原先写 parents[4] / "00_共享核心" / "tests" / ... —— 那是 la拆包项目 下并不存在的路径；
#   而且守卫 `if not str(OUT).startswith("E:")` 恒为假（路径确实以 E: 开头），兜底永远走不到。
#   直接用上面已经算好的 ROOT（= 工具库），不手算 parents[N]。
OUT = ROOT  / "00_共享核心" / "测试" / "fixtures" / "script_py314_7767_2949"


def load(n, p):
    s = importlib.util.spec_from_file_location(n, p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


g = load("g", ROOT  / "02_图文音频渲染" / "皮肤链与渲染" / "gpk_npk_index.py")
nr = load("nr", ROOT  / "01_解码定位复原" / "解包与扫描" / "npk_reader.py")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for c in iter(lambda: f.read(1 << 20), b""):
            h.update(c)
    return h.hexdigest()


def find_source():
    """按清单的 size + sha256 全盘锁定源包（不按名字猜）。"""
    man = json.load(MANIFEST.open(encoding="utf-8"))
    want_size = man["source"]["size"]
    want_hash = man["source"]["sha256"]
    name = Path(man["source"]["path"]).name
    cands = []
    for r, _d, fs in __import__("os").walk(SRC_ROOT):
        for f in fs:
            if f == name:
                p = Path(r) / f
                if p.stat().st_size == want_size:
                    cands.append(p)
    print("  尺寸匹配的候选：%d 个" % len(cands))
    for p in cands:
        got = sha256_file(p)
        if got == want_hash:
            print("  ✓ sha256 命中：%s" % p)
            return p, man
        else:
            print("    ✗ sha256 不符：%s" % p)
    return None, man


def main():
    print("=" * 74)
    print("① 锁定源包（按清单的 size + sha256，不按名字猜）")
    print("=" * 74)
    src, man = find_source()
    if src is None:
        print("  ✗ 源包定位失败 —— 夹具无法重建")
        return 1

    print("\n" + "=" * 74)
    print("② 解出两个条目")
    print("=" * 74)
    want = {}
    for e in man["entries"]:
        if e["index"] in (7767, 2949):
            want[e["index"]] = e

    rec, factory = g.parse_npk(str(src))
    got = {}
    for idx, fid, off, packed, decoded, flag in factory():
        for i, e in want.items():
            if fid == int(e["file_id"], 16):
                got[i] = (off, packed, decoded, flag)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "entries").mkdir(parents=True, exist_ok=True)
    prov = {
        "schema": "lifeafter-test-fixture-v1",
        "why": "原夹具目录 entries/ 已被清理，只剩清单；本夹具按清单元数据从源包重建并逐字节核验",
        "source": {"path": man["source"]["path"], "size": man["source"]["size"],
                   "sha256": man["source"]["sha256"],
                   "rebuilt_from": str(src)},
        "entries": {},
    }
    ok = True
    for idx, e in sorted(want.items()):
        print("\n  ── entry %d ──" % idx)
        if idx not in got:
            print("     ✗ 解析未找到 file_id %s" % e["file_id"])
            ok = False
            continue
        off, packed, decoded, flag = got[idx]
        with src.open("rb") as f:
            f.seek(off)
            raw = f.read(packed)
        out = nr.unpack_entry(raw, decoded, flag)
        oh = sha256_bytes(out)
        sz_ok = str(len(out)) == str(e.get("actual_output_size"))
        h_ok = oh == e.get("output_sha256")
        print("     解出 %d B，尺寸 %s，sha256 %s"
              % (len(out), "✓" if sz_ok else "✗", "✓" if h_ok else "✗"))
        if not (sz_ok and h_ok):
            ok = False
            print("     ✗ 与清单不符，拒绝落盘（夹具必须是可核验的）")
            continue
        dest = OUT / "entries" / ("%06d.bin" % idx)
        dest.write_bytes(out)
        print("     ✓ 落盘 %s" % dest.relative_to(ROOT.parent.parent.parent))
        prov["entries"]["%06d.bin" % idx] = {
            "index": idx, "file_id": e["file_id"], "archive_offset": off,
            "packed_size": packed, "flag": flag,
            "output_size": len(out), "output_sha256": oh,
        }
    prov["verified"] = ok
    (OUT / "PROVENANCE.json").write_text(
        json.dumps(prov, ensure_ascii=False, indent=2), encoding="utf-8")
    print("\n" + "=" * 74)
    print("③ 结果：%s" % ("全部逐字节核验通过 ✓" if ok else "存在不符，见上"))
    print("   夹具目录：%s" % OUT)
    print("   凭据文件：PROVENANCE.json")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
