# -*- coding: utf-8 -*-
r"""进程内存 dump + 指纹扫描（纯 ctypes，无外部依赖，Windows x64）。

## 用途
客户端 exe 被**网易自研壳**保护（节名伪装成 UPX0/UPX1，但没有 UPX! 魔数，
标准 `upx -d` 直接拒；全树 6 份副本全加壳，静态取不到 CPython 表）。
⇒ 只能**运行时**从内存里取已展开的镜像：在里面找
   ① marshal tag 分派  ② opcode 名表/元数据  ③ zstd 自定义字典

## 风险（必须知情）
进程内存读取可能被反作弊/SDK 检测。仅用于本机自测；不用于绕过任何服务端逻辑。

## 用法
    python -m toolkit_core.proc_dump --list                      # 列进程
    python -m toolkit_core.proc_dump --name lifeafter --out DIR   # dump 该进程
    python -m toolkit_core.proc_dump --pid 1234 --scan "bad marshal data"
"""
from __future__ import annotations

import ctypes
import ctypes.wintypes as wt
import sys
import time
from pathlib import Path

k32 = ctypes.WinDLL("kernel32", use_last_error=True)

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_NOACCESS = 0x01
PAGE_GUARD = 0x100
READABLE = {0x02, 0x04, 0x20, 0x40, 0x80}      # R / RW / ER / ERW / EW(可读)


class MEMORY_BASIC_INFORMATION64(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_ulonglong),
                ("AllocationBase", ctypes.c_ulonglong),
                ("AllocationProtect", wt.DWORD),
                ("__alignment1", wt.DWORD),
                ("RegionSize", ctypes.c_ulonglong),
                ("State", wt.DWORD),
                ("Protect", wt.DWORD),
                ("Type", wt.DWORD),
                ("__alignment2", wt.DWORD)]


def list_processes() -> list[tuple[int, str]]:
    """(pid, exe名) 列表。"""
    out: list[tuple[int, str]] = []
    TH32CS_SNAPPROCESS = 0x2

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [("dwSize", wt.DWORD), ("cntUsage", wt.DWORD), ("th32ProcessID", wt.DWORD),
                    ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
                    ("th32ModuleID", wt.DWORD), ("cntThreads", wt.DWORD),
                    ("th32ParentProcessID", wt.DWORD), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", wt.DWORD), ("szExeFile", ctypes.c_char * 260)]

    snap = k32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    if snap == -1:
        return out
    pe = PROCESSENTRY32()
    pe.dwSize = ctypes.sizeof(PROCESSENTRY32)
    ok = k32.Process32First(snap, ctypes.byref(pe))
    while ok:
        out.append((int(pe.th32ProcessID), pe.szExeFile.decode("mbcs", "replace")))
        ok = k32.Process32Next(snap, ctypes.byref(pe))
    k32.CloseHandle(snap)
    return out


def find_pid(name_part: str) -> list[tuple[int, str]]:
    name_part = name_part.lower()
    return [(p, n) for p, n in list_processes() if name_part in n.lower()]


def dump_process(pid: int, out_dir: Path, *, scan: bytes | None = None,
                 max_region: int = 256 * 1024 * 1024, only_hits: bool = False) -> dict:
    """把该进程【已提交且可读】的内存写到 out_dir（每区一个 .bin + 索引）。

    only_hits=True：只写【含 scan 指纹】的区域（扫描整进程但落盘很少）——对付 GB 级进程。
    """
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        raise OSError("OpenProcess 失败（err=%d）—— 试试管理员权限；某些反作弊会拦"
                      % ctypes.get_last_error())
    out_dir.mkdir(parents=True, exist_ok=True)
    mbi = MEMORY_BASIC_INFORMATION64()
    addr = 0
    idx = 0
    index = []
    hits = []
    t0 = time.time()
    scanned = 0
    while k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                             ctypes.sizeof(mbi)) == ctypes.sizeof(mbi):
        base = int(mbi.BaseAddress)
        size = int(mbi.RegionSize)
        if (mbi.State == MEM_COMMIT and mbi.Protect in READABLE
                and not (mbi.Protect & PAGE_GUARD) and 0 < size <= max_region):
            buf = ctypes.create_string_buffer(size)
            read = ctypes.c_size_t(0)
            if k32.ReadProcessMemory(h, ctypes.c_void_p(base), buf, size, ctypes.byref(read)):
                data = buf.raw[:read.value]
                scanned += len(data)
                found = scan is not None and scan in data
                if found:
                    off = data.find(scan)
                    hits.append({"base": base, "size": size, "off": off,
                                 "ctx": data[max(0, off - 32):off + 96].hex()})
                if (not only_hits) or found:
                    p = out_dir / ("r%05d_%016X.bin" % (idx, base))
                    p.write_bytes(data)
                    index.append({"idx": idx, "base": base, "size": len(data),
                                  "protect": mbi.Protect, "file": p.name,
                                  "has_scan": found})
                    idx += 1
        addr = base + size
        if addr <= base:
            break
    k32.CloseHandle(h)
    (out_dir / "_index.json").write_text(
        __import__("json").dumps({"pid": pid, "regions": index, "scan_hits": hits,
                                  "scanned_bytes": scanned},
                                 ensure_ascii=False, indent=1), encoding="utf-8")
    return {"pid": pid, "regions_written": len(index), "bytes_written": sum(r["size"] for r in index),
            "scanned_mb": round(scanned / 2 ** 20, 1),
            "seconds": round(time.time() - t0, 1), "scan_hits": len(hits), "out": str(out_dir)}


def scan_dir(d: Path, needle: bytes, *, max_files: int | None = None) -> list[dict]:
    """在已 dump 的目录里扫指纹，返回命中文件与偏移。"""
    hits = []
    for p in sorted(Path(d).glob("r*.bin")):
        try:
            b = p.read_bytes()
        except OSError:
            continue
        i = b.find(needle)
        if i >= 0:
            hits.append({"file": p.name, "off": i, "size": len(b),
                         "ctx": b[max(0, i - 24):i + 72].hex()})
        if max_files and len(hits) >= max_files:
            break
    return hits


def main(argv: list[str]) -> int:
    import argparse
    import json
    ap = argparse.ArgumentParser(description="进程内存 dump / 指纹扫描")
    ap.add_argument("--list", action="store_true", help="列进程（含 lifeafter 高亮）")
    ap.add_argument("--name", help="按进程名子串找 pid")
    ap.add_argument("--pid", type=int, help="指定 pid")
    ap.add_argument("--out", default="E:/la拆包项目/03_执行/90_临时/memdump")
    ap.add_argument("--scan", help="dump 时顺带扫的指纹（如 'bad marshal data'）")
    ap.add_argument("--scan-dir", help="只扫已 dump 的目录")
    ap.add_argument("--only-hits", action="store_true",
                    help="只落盘【含指纹】的内存区（GB 级进程必备）")
    a = ap.parse_args(argv)

    if a.list:
        for p, n in sorted(list_processes()):
            mark = "  ★" if "lifeafter" in n.lower() or "mrzh" in n.lower() else ""
            print("   %-7d %s%s" % (p, n, mark))
        return 0
    if a.scan_dir:
        hits = scan_dir(Path(a.scan_dir), (a.scan or "bad marshal data").encode())
        print("命中 %d" % len(hits))
        for h in hits[:10]:
            print("   %s @%d ｜ %s" % (h["file"], h["off"], h["ctx"][:100]))
        return 0
    pid = a.pid
    if pid is None and a.name:
        cand = find_pid(a.name)
        if not cand:
            print("✗ 没找到进程名含 %r 的进程（客户端起了吗？）" % a.name, file=sys.stderr)
            return 3
        pid = cand[0][0]
        print("选中 pid=%d %s" % (pid, cand[0][1]))
    if pid is None:
        print("需要 --pid 或 --name（或 --list）", file=sys.stderr)
        return 2
    rep = dump_process(pid, Path(a.out), scan=(a.scan.encode() if a.scan else None),
                       only_hits=a.only_hits)
    print(json.dumps(rep, ensure_ascii=False, indent=1)[:1500])
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
