# -*- coding: utf-8 -*-
"""NeoX 字节码 → 栈式伪代码（线性，带跳转标签）。

不是完整反编译器：只做栈模拟 + 表达式拼装 + 跳转标注，
目的是把 891 条指令压成能读的语句序列。
"""
from __future__ import annotations

import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import script_decode as SD  # noqa: E402

P = r"E:/la拆包项目/01_索引与产物/41_还原树/apk_mumu_5.0.679/assets/script.py314.lc.npk/com/formula/HurtCalc.py"
OUT = r"C:/Users/Administrator/AppData/Local/hermes/cache/scratch"

BIN = {0: "+", 1: "&", 2: "//", 3: "<<", 4: "@", 5: "*", 6: "%", 7: "|", 8: "**",
       9: ">>", 10: "-", 11: "/", 12: "^", 13: "+=", 14: "&=", 15: "//=", 16: "<<=",
       17: "@=", 18: "*=", 19: "%=", 20: "|=", 21: "**=", 22: ">>=", 23: "-=",
       24: "/=", 25: "^=", 26: "[]"}
CMP = {18: "==", 58: "<=", 88: "==", 148: ">=", 40: "<", 68: "!="}


def codes(buf):
    n = len(buf)
    r = SD.NeoXReader(buf)
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
        return "<code>"
    if v.kind in ("int", "float", "float32", "uint", "tag3e"):
        return str(v.v)
    if v.kind == "none":
        return "None"
    if v.kind == "tuple":
        return "(" + ", ".join(txt(x) for x in v.v[:8]) + ")"
    return "<%s>" % v.kind


def decompile(c, limit=100000):
    names = c.names
    consts = c.consts
    ins = list(SD.dis_code(c.co_code))
    labels = {i.off for i in ins if i.name.startswith("POP_JUMP") or i.name.startswith("JUMP")}
    stack: list[str] = []
    out: list[str] = []
    indent = 0

    def pop(n=1):
        vals = []
        for _ in range(n):
            vals.append(stack.pop() if stack else "?")
        return list(reversed(vals))

    for k, i in enumerate(ins[:limit]):
        if i.off in labels:
            out.append("L%d:" % i.off)
        nm, a = i.name, i.arg
        if nm == "RESUME" or nm == "NOT_TAKEN" or nm == "NOP":
            continue
        if nm in ("LOAD_FAST_BORROW", "LOAD_FAST", "LOAD_FAST_CHECK"):
            stack.append("v%d" % a)
        elif nm == "LOAD_FAST_BORROW_LOAD_FAST_BORROW" or nm == "LOAD_FAST_LOAD_FAST":
            stack.append("v%d" % (a >> 4))
            stack.append("v%d" % (a & 0xF))
        elif nm == "LOAD_SMALL_INT":
            stack.append(str(a))
        elif nm == "LOAD_CONST":
            stack.append(txt(consts[a]) if a < len(consts) else "?")
        elif nm == "LOAD_GLOBAL":
            j = a >> 1
            stack.append(txt(names[j]) if j < len(names) else "?")
        elif nm == "LOAD_NAME":
            stack.append(txt(names[a]) if a < len(names) else "?")
        elif nm in ("LOAD_ATTR", "LOAD_METHOD", "LOAD_SUPER_ATTR"):
            j = a >> 1
            obj = pop()[0]
            stack.append("%s.%s" % (obj, txt(names[j]) if j < len(names) else "?"))
        elif nm == "PUSH_NULL":
            stack.append("NULL")
        elif nm == "BINARY_OP":
            b, aa = pop(2)
            op = BIN.get(a, "op%d" % a)
            if op == "[]":
                stack.append("%s[%s]" % (aa, b))
            elif a >= 13:
                out.append("%s %s %s" % (aa, op, b))
            else:
                stack.append("(%s %s %s)" % (aa, op, b))
        elif nm == "COMPARE_OP":
            b, aa = pop(2)
            stack.append("(%s %s %s)" % (aa, CMP.get(a, "cmp%d" % a), b))
        elif nm == "CONTAINS_OP":
            b, aa = pop(2)
            stack.append("(%s %s %s)" % (aa, "in" if a == 0 else "not in", b))
        elif nm == "IS_OP":
            b, aa = pop(2)
            stack.append("(%s is %s)" % (aa, b) if a == 0 else "(%s is not %s)" % (aa, b))
        elif nm == "TO_BOOL":
            v = pop()[0]
            stack.append(v)
        elif nm == "CALL":
            args = pop(a)
            fn = pop()[0]
            if stack and stack[-1] == "NULL":
                stack.pop()
            stack.append("%s(%s)" % (fn, ", ".join(args)))
        elif nm == "BUILD_MAP":
            items = pop(2 * a)
            stack.append("{%s}" % ", ".join("%s: %s" % (items[i], items[i + 1]) for i in range(0, len(items), 2)))
        elif nm == "BUILD_LIST":
            items = pop(a)
            stack.append("[%s]" % ", ".join(items))
        elif nm == "BUILD_TUPLE":
            items = pop(a)
            stack.append("(%s)" % ", ".join(items))
        elif nm == "STORE_FAST":
            v = pop()[0]
            out.append("v%d = %s" % (a, v))
        elif nm == "STORE_NAME":
            v = pop()[0]
            out.append("%s = %s" % (txt(names[a]) if a < len(names) else "?", v))
        elif nm == "STORE_ATTR":
            j = a >> 1
            v, obj = pop(2)
            out.append("%s.%s = %s" % (obj, txt(names[j]) if j < len(names) else "?", v))
        elif nm == "STORE_FAST_STORE_FAST":
            b, aa = pop(2)
            out.append("v%d, v%d = %s" % (a >> 4, a & 0xF, "%s, %s" % (aa, b)))
        elif nm == "POP_TOP":
            v = pop()[0]
            if v and v != "NULL":
                out.append(str(v))
        elif nm in ("POP_JUMP_IF_FALSE", "POP_JUMP_IF_TRUE", "POP_JUMP_IF_NONE", "POP_JUMP_IF_NOT_NONE"):
            v = pop()[0]
            cond = {"POP_JUMP_IF_FALSE": "if not %s", "POP_JUMP_IF_TRUE": "if %s",
                    "POP_JUMP_IF_NONE": "if %s is None", "POP_JUMP_IF_NOT_NONE": "if %s is not None"}[nm]
            out.append((cond % v) + ":  goto L%d" % (i.off + 2 + a))
        elif nm in ("JUMP_FORWARD", "JUMP_BACKWARD", "JUMP_BACKWARD_NO_INTERRUPT"):
            out.append("goto L%d" % (i.off + 2 + a if nm == "JUMP_FORWARD" else i.off + 2 - a))
        elif nm == "GET_ITER":
            pass
        elif nm == "FOR_ITER":
            out.append("for ... (L%d):" % (i.off + 2 + a))
        elif nm == "UNPACK_SEQUENCE":
            v = pop()[0]
            stack.extend(["%s[%d]" % (v, n) for n in range(a)])
        elif nm == "RETURN_VALUE":
            v = pop()[0]
            out.append("return %s" % v)
        else:
            out.append("# %s %s" % (nm, a))
    return out


def main() -> int:
    which = sys.argv[1] if len(sys.argv) > 1 else "calc_internal"
    for c in codes(open(P, "rb").read()):
        if c.name.v == which:
            body = decompile(c)
            dest = OUT + "/pseudo_" + which + ".txt"
            open(dest, "w", encoding="utf-8").write("\n".join(body))
            print("写出", dest, len(body), "行")
            return 0
    print("没找到", which)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
