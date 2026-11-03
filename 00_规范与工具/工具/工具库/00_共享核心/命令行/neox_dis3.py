# -*- coding: utf-8 -*-
"""NeoX 反汇编 v3：解码组合指令参数 + BINARY_OP 枚举名。

用法：neox_dis3.py <目标文件> [--list | 函数名]
"""
import os
import sys
import tempfile

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import script_decode as SD  # noqa: E402

OUT = os.path.join(tempfile.gettempdir(), "neox_dis3")

SHIFTED = {"LOAD_ATTR", "LOAD_GLOBAL", "LOAD_METHOD", "STORE_ATTR", "LOAD_SUPER_ATTR"}
PLAIN = {"LOAD_NAME", "STORE_NAME", "IMPORT_NAME", "IMPORT_FROM", "LOAD_FROM_DICT_OR_GLOBALS"}
COMBINED = {"LOAD_FAST_LOAD_FAST", "STORE_FAST_STORE_FAST", "STORE_FAST_LOAD_FAST",
            "LOAD_FAST_BORROW_LOAD_FAST_BORROW", "LOAD_FAST_AND_CLEAR"}

BINOP = {0: "ADD", 1: "AND", 2: "FLOOR_DIV", 3: "LSHIFT", 4: "MATMUL", 5: "MUL",
         6: "MOD", 7: "OR", 8: "POW", 9: "RSHIFT", 10: "SUB", 11: "TRUEDIV",
         12: "XOR", 13: "IADD", 14: "IAND", 15: "IFLOORDIV", 16: "ILSHIFT",
         17: "IMATMUL", 18: "IMUL", 19: "IMOD", 20: "IOR", 21: "IPOW",
         22: "IRSHIFT", 23: "ISUB", 24: "ITRUEDIV", 25: "IXOR"}


def codes(buf):
    """每个 code 对象用独立 reader 解析：共享 reader 会让 0x5A 引用跨对象串号。"""
    n = len(buf)
    pos, out = 0, []
    while pos < n - 26:
        i = pos
        while i < n - 26 and (buf[i] & 0x7F) != 0x73:
            i += 1
        if i >= n - 26:
            break
        try:
            c, end = SD.NeoXReader(buf).parse_code(i, 0, None)
        except Exception:
            pos = i + 1
            continue
        out.append(c)
        pos = end
    return out


def txt(v):
    if v is None:
        return "?"
    if isinstance(v.v, str):
        return repr(v.v)
    if v.code is not None:
        return "<code %s>" % (v.code.name.v if hasattr(v.code.name, "v") else "?")
    if v.kind in ("int", "float", "float32", "uint", "tag3e"):
        return str(v.v)
    if v.kind == "none":
        return "None"
    if v.kind == "tuple":
        return "(" + ", ".join(txt(x) for x in v.v[:6]) + ("" if len(v.v) <= 6 else " ...") + ")"
    return "<%s>" % v.kind


def listing(c):
    out = ["=== %s @%d args=%d len=%dB" % (c.name.v, c.off, c.argcount, c.code_len)]
    for i in SD.dis_code(c.co_code):
        nm, arg, extra = i.name, i.arg, ""
        if nm == "LOAD_CONST" and 0 <= arg < len(c.consts):
            extra = "<- " + txt(c.consts[arg])
        elif nm in SHIFTED:
            j = arg >> 1
            extra = "<- " + (txt(c.names[j]) if 0 <= j < len(c.names) else "?")
        elif nm in PLAIN:
            extra = "<- " + (txt(c.names[arg]) if 0 <= arg < len(c.names) else "?")
        elif nm in COMBINED:
            extra = "<- v%d, v%d" % (arg >> 4, arg & 0xF)
        elif nm and nm.startswith("LOAD_FAST") or (nm and nm.startswith("STORE_FAST")):
            extra = "<- v%d" % arg
        elif nm == "BINARY_OP":
            extra = "<- " + BINOP.get(arg, "OP%d" % arg)
            if BINOP.get(arg) == "SUBSCR":
                nm = "BINARY_SUBSCR"
        out.append("  %5d %-30s %-6s %s" % (i.off, nm, arg, extra))
    return out


def main() -> int:
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        print("用法: neox_dis3.py <目标文件> [--list | 函数名]")
        return 0
    src = args[0]
    if not os.path.isfile(src):
        print("文件不存在:", src)
        return 2
    which = args[1] if len(args) > 1 else "--list"
    cs = codes(open(src, "rb").read())
    if which == "--list":
        for c in cs:
            print("  @%-7d arg=%-2d %-38s %dB" % (c.off, c.argcount, c.name.v, c.code_len))
        return 0
    hit = False
    for c in cs:
        if c.name.v == which:
            hit = True
            body = listing(c)
            os.makedirs(OUT, exist_ok=True)
            dest = os.path.join(OUT, "dis3_" + which + ".txt")
            open(dest, "w", encoding="utf-8").write("\n".join(body))
            print("写出", dest, len(body), "行")
    if not hit:
        print("没找到", which)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
