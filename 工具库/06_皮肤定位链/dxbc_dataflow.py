# -*- coding: utf-8 -*-
"""dxbc_dataflow.py — 从 DXBC 反汇编做寄存器 def-use 反向追踪。
输入：asm 路径 + 起始行号 + 目标寄存器
输出：到「纹理采样 / cbX[..] 常量 / 输入属性」叶子的依赖树。
用法: python dxbc_dataflow.py <asm> <startLine> <reg>
"""
import io, re, sys

INS = re.compile(r'^\s*([a-z][a-z0-9_]*)\s+(.*)$')
DEST = re.compile(r'^(r\d+|o\d+)(\.[xyzw]{1,4})?$')
SRC = re.compile(r'\b([rv]\d+|cb\d+\[\d+\]|l\(|t\d+)\b')


def load(path):
    return io.open(path, encoding="utf-8", errors="ignore").read().split("\n")


def parse(lines):
    """返回 [(lineno, op, dst, [srcs...], raw)]"""
    out = []
    for i, L in enumerate(lines):
        s = L.strip()
        if not s or s.startswith("//") or s.startswith("dcl_"):
            continue
        m = INS.match(s)
        if not m:
            continue
        op, rest = m.group(1), m.group(2)
        if op in ("ret", "endif", "else", "endloop", "endswitch", "nop"):
            out.append((i + 1, op, None, [], s)); continue
        parts = rest.split(",")
        dst = None
        dm = re.match(r'^\s*(r\d+|o\d+)(\.[xyzw]{1,4})?\s*$', parts[0])
        if dm:
            dst = dm.group(1)
            srcs = parts[1:]
        else:
            srcs = parts
        # 展开资源操作数里的寄存器
        regs = []
        for x in srcs:
            regs += re.findall(r'\b(r\d+)\b', x)
        out.append((i + 1, op, dst, regs, s))
    return out


def trace(insns, reg, upto_line, depth=0, maxdepth=7, seen=None, path=""):
    """反向找 reg 在 upto_line 之前的最后一次写入，递归展开。"""
    if seen is None:
        seen = set()
    key = (reg, upto_line)
    if depth > maxdepth or key in seen:
        return [" " * (depth * 2) + "%s (达到深度上限/已访问)" % reg]
    seen.add(key)
    w = None
    for ln, op, dst, srcs, raw in reversed(insns):
        if ln >= upto_line:
            continue
        if dst == reg:
            w = (ln, op, dst, srcs, raw); break
    if not w:
        return [" " * (depth * 2) + "%s ← (未找到写入；可能是输入属性/未初始化)" % reg]
    ln, op, dst, srcs, raw = w
    lines = [" " * (depth * 2) + "L%-4d %s" % (ln, raw[:120])]
    for r in dict.fromkeys(srcs):
        lines += trace(insns, r, ln, depth + 1, maxdepth, seen, path + "/" + r)
    return lines


def main():
    path, start, reg = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    lines = load(path)
    insns = parse(lines)
    print("指令数: %d" % len(insns))
    print("=" * 74)
    print("反向追踪 %s 在 L%d 之前（深度上限 7）" % (reg, start))
    print("=" * 74)
    for L in trace(insns, reg, start):
        print(L)
    # 叶子归类
    print()
    print("=" * 74)
    print("该 shader 内全部纹理采样 → 目标寄存器")
    print("=" * 74)
    for i, L in enumerate(lines):
        s = L.strip()
        m = re.search(r'sample[_a-z]*_?indexable\(\s*(texture2d|cube|texture3d|texture2darray)\s*\)\([^)]*\)\s+(r\d+)\.(\w+),\s+([^,]+),\s*(t\d+)', s)
        if m:
            print("  L%-5d %-14s %-8s UV=%-18s tex=%s" % (i + 1, m.group(1), m.group(2) + "." + m.group(3), m.group(4)[:18], m.group(5)))
    print()
    print("=" * 74)
    print("该 shader 内全部 cbX[..] 常量引用（去重计数）")
    print("=" * 74)
    from collections import Counter
    c = Counter()
    for L in lines:
        for m in re.finditer(r'\bcb(\d+)\[(\d+)\]\.([xyzw]+)', L):
            c["cb%s[%s].%s" % (m.group(1), m.group(2), m.group(3))] += 1
    for k, v in sorted(c.items(), key=lambda x: -x[1]):
        print("  %-22s ×%d" % (k, v))


if __name__ == "__main__":
    main()
