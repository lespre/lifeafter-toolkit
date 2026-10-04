# -*- coding: utf-8 -*-
r"""script_decode.py — 网易 NeoX Python 方言（客户端 py314）字节码反汇编 / 结构解析器。

★ 原理（已实测成立）：
   客户端保留【标准 CPython 3.14 的指令宽度】（含 inline cache 槽），只是把 opcode 号换表。
   ⇒ 用本地 Python 3.14 的标准库/已知源码模块做对拍，DP 对齐即可反推 opcode 表。

★ 已锁定的映射（DP 对齐 functools.py ↔ 标准 functools.pyc，单候选者）：
   0x4F LOAD_NAME · 0x78 STORE_NAME · 0x44 LOAD_CONST · 0x67 LOAD_SMALL_INT
   0x6E IMPORT_NAME · 0x45 IMPORT_FROM · 0x7A LOAD_GLOBAL · 0x12 RETURN_VALUE
   0x07 POP_TOP · 0x2A POP_EXCEPT · 0x22 NOP · 0x7E RAISE_VARARGS · 0x09 PUSH_EXC_INFO
   0x17 CHECK_EXC_MATCH · 0x5A POP_JUMP_IF_NOT_NONE · 0x32 JUMP_BACKWARD_NO_INTERRUPT
   0x6B STORE_ATTR · 0x73 LOAD_FAST_BORROW · 0x76 STORE_FAST · 0x56 CALL · 0x3F LOAD_ATTR
   0x1A NOT_TAKEN · 0x58 POP_JUMP_IF_FALSE · 0x16 MAKE_FUNCTION · 0x31 LOAD_FAST
   0x33 LOAD_FAST_BORROW_LOAD_FAST_BORROW · 0x38 BUILD_TUPLE · 0x52 BINARY_OP
   0x61 COMPARE_OP · 0x6D BUILD_LIST · 0x1B FORMAT_SIMPLE · 0x08 TO_BOOL

★ 铁证：`67 80`（LOAD_SMALL_INT 128）在客户端 functools 里恰好出现 1 次，
   而 lru_cache 的默认 maxsize = 128 ⇒ 小整数是【值内联】的。

════════════════════════════════════════════════════════════════════════════
★ 2026-10-03 大升级：**带常量解析的结构化反汇编器**（见本文件下半部分）
   逐字段实测的 code object 布局（字段顺序与 CPython 3.11+ marshal 一致）：

      73
      argcount u32 | posonly u32 | kwonly u32 | stacksize u32 | flags u32
      co_code            : 7b|fb + u32 len + 原始字节
                           ★ 无额外前缀；首条通常就是 `80 00` = RESUME 0
      co_consts          : 2e|ae + u8 count + 若干值
      co_names           : 同上
      co_localsplusnames : 同上（也常写成 5a 引用复用已有元组）
      co_localspluskinds : 7b|fb + u32 len（每字节 0x26=local / 0x80=cell·free）
      co_filename        : 串（常被 5a 引用复用，第 2 个函数起几乎都是引用）
      co_name            : 串 或 5a 引用
      co_qualname        : 串 或 5a 引用
      co_firstlineno     : 裸 u32（无标签）
      co_linetable       : 7b|fb + u32 len
      co_exceptiontable  : 7b|fb + u32 len

   验证：`com\cdata\common_model_show_conf.py` 解析终点 == 文件长度（逐字节吻合）；
        随机抽样 40 个模块里 39 个解析终点 == 文件长度。

★ marshal 标签（FLAG_REF：字节 = 基标签 | 0x80）：
   0x53/0xd3/0x79/0xf9 = 短串(u8 长；0xFF→u32)     0x7b/0xfb = 长 bytes/串(u32 长)
   0x2e/0xae = 元组(u8 元素数)                       0x73/0xf3 = 嵌套 code
   0x78/0xf8 = None                                  0x5a/0xda = 引用(u32 索引)
   0xbe = u32 · 0x7a/0xfa = 小整数标记 · 0x3c = u8 · 0x3e+u32 = 标记
   0x22 = f64 · 0x12 = f32
★ 引用表(5a)规则（实测对齐多个锚点）：按文档序登记 **str / 元组 / code / co_code** 四类对象，
   根 code 自身不入表。
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from pathlib import Path

# ── opcode 表 ────────────────────────────────────────────────────────────────
# 实测：客户端保留标准 3.14 的指令宽度（含 inline cache），只换 opcode 号。
# 表由 lib/*（22 个模块，标准侧源码/字节码可得）批量 DP 对齐投票得出，
# 落盘为同目录的 neoX_opcode_table.json（opname→客户端字节）与 neoX_op_widths.json。
import json as _json

_HERE = Path(__file__).with_name


def _load_tables():
    ops: dict[int, tuple[str, int]] = {}
    try:
        tbl = _json.loads(_HERE("neoX_opcode_table.json").read_text(encoding="utf-8"))
        wid = _json.loads(_HERE("neoX_op_widths.json").read_text(encoding="utf-8"))
        for opname, by in tbl.items():
            ops[int(by)] = (opname, int(wid.get(opname, 2)))
    except Exception:
        pass
    return ops


OPS: dict[int, tuple[str, int]] = _load_tables() or {
    0x4F: ("LOAD_NAME", 2), 0x78: ("STORE_NAME", 2), 0x44: ("LOAD_CONST", 2),
    0x67: ("LOAD_SMALL_INT", 2), 0x6E: ("IMPORT_NAME", 2), 0x45: ("IMPORT_FROM", 2),
    0x7A: ("LOAD_GLOBAL", 10), 0x12: ("RETURN_VALUE", 2), 0x07: ("POP_TOP", 2),
    0x2A: ("POP_EXCEPT", 2), 0x22: ("NOP", 2), 0x7E: ("RAISE_VARARGS", 2),
    0x09: ("PUSH_EXC_INFO", 2), 0x17: ("CHECK_EXC_MATCH", 2),
    0x5A: ("POP_JUMP_IF_NOT_NONE", 2), 0x32: ("JUMP_BACKWARD_NO_INTERRUPT", 2),
    0x6B: ("STORE_ATTR", 2), 0x73: ("LOAD_FAST_BORROW", 2), 0x76: ("STORE_FAST", 2),
    0x56: ("CALL", 10), 0x3F: ("LOAD_ATTR", 10), 0x1A: ("NOT_TAKEN", 2),
    0x58: ("POP_JUMP_IF_FALSE", 4), 0x16: ("MAKE_FUNCTION", 2), 0x31: ("LOAD_FAST", 2),
    0x33: ("LOAD_FAST_BORROW_LOAD_FAST_BORROW", 4), 0x38: ("BUILD_TUPLE", 2),
    0x52: ("BINARY_OP", 2), 0x61: ("COMPARE_OP", 2), 0x6D: ("BUILD_LIST", 2),
    0x1B: ("FORMAT_SIMPLE", 2), 0x08: ("TO_BOOL", 2),
}
# 0x80 实测是每个 code 的首条指令（宽度 2）—— 标成 RESUME，避免被当成「未知」影响对齐判断
OPS.setdefault(0x80, ("RESUME", 2))


@dataclass
class Ins:
    off: int
    op: int
    name: str
    arg: int


def dis_code(body: bytes) -> list[Ins]:
    """反汇编一段客户端字节码。未映射的 op 记为 ?，按 2 字节前进。
    ★ 2026-10-02：支持本方言的 EXTENDED_ARG（= 0x3b，载荷在其后 1 字节）。
      不合并高位 ⇒ 下标 >255 的常量/名字根本读不出来（实测踩过）。
    ★ 2026-10-03：补 0x80 = RESUME（每个函数第一条，2 字节），否则会被算成未知指令。
    """
    out: list[Ins] = []
    i, n = 0, len(body)
    ext = None
    while i < n - 1:
        op = body[i]
        if op == 0x3B:
            ext = body[i + 1]
            i += 2
            continue
        if op in OPS:
            name, w = OPS[op]
            if i + w > n:
                break
            arg = int.from_bytes(body[i + 1:i + w], "little")
            if ext is not None:
                arg = (ext << 8) | (arg & 0xFF)
                ext = None
            out.append(Ins(i, op, name, arg))
            i += w
        else:
            out.append(Ins(i, op, "?", body[i + 1]))
            i += 2
            ext = None
    return out


def const_tables(buf: bytes, lo: int = 0, hi: int | None = None):
    """扫出 `2e <n>` 序列（常量/名字/元组表）。返回 [(offset, count, [items])]。"""
    hi = len(buf) if hi is None else hi
    res = []
    i = lo
    while i < hi - 2:
        if buf[i] == 0x2E:
            cnt = buf[i + 1]
            items, j, ok = [], i + 2, True
            while len(items) < cnt and j < hi:
                t = buf[j]
                if t in (0xD3, 0xF3, 0xDA, 0xFA):
                    ln = buf[j + 1]
                    st = j + 2
                    if ln == 0xFF:
                        ln = struct.unpack_from("<I", buf, j + 2)[0]
                        st = j + 6
                    if 0 < ln <= 512 and st + ln <= hi and all(0x20 <= c < 0x7F for c in buf[st:st + ln]):
                        items.append(buf[st:st + ln].decode("latin1"))
                        j = st + ln
                        continue
                    ok = False
                    break
                if t == 0xBE and j + 5 <= hi:
                    items.append(struct.unpack_from("<I", buf, j + 1)[0])
                    j += 5
                    continue
                ok = False
                break
            if ok and len(items) == cnt:
                res.append((i, cnt, items))
            i += 2
        else:
            i += 1
    return res


def blobs(buf: bytes):
    """所有码段：(offset, payload)。
    ★ 2026-10-01 更正（子代理实测）：code 容器有两种 tag —— 0xfb 与 0x7b
      （同一个 `80 00` 魔数，差 0x80 位）；只认 0xfb 会漏掉约一半 code 对象。
    ★ 2026-10-03：本函数是【旧版宽松扫描】，保留兼容；精确结构请用 load_module()。
    """
    out = []
    i, n = 0, len(buf)
    while i < n - 7:
        if buf[i] in (0xFB, 0x7B) and buf[i + 5:i + 7] == b"\x80\x00":
            ln = struct.unpack_from("<I", buf, i + 1)[0]
            if 0 < ln <= n - i - 7:
                out.append((i, buf[i + 7:i + 7 + ln]))
                i += 7 + ln
                continue
        i += 1
    return out


# ════════════════════════════════════════════════════════════════════════════
#  结构化读取器（常量/名字解析）
# ════════════════════════════════════════════════════════════════════════════
STR_TAGS = (0xD3, 0xF3, 0xDA, 0xFA, 0x79, 0x53, 0xF9)
BYTES_TAGS = (0x7B, 0xFB)
TUPLE_TAGS = (0x2E, 0xAE)
CODE_TAG = 0x73
KNOWN_TAGS = {0x73, 0x2E, 0x78, 0x7B, 0x79, 0x53, 0xD3, 0x5A, 0x7A, 0xBE, 0x3C, 0x22, 0x12, 0x3E}

NAME_OPS_SHIFTED = {"LOAD_ATTR", "LOAD_GLOBAL", "LOAD_METHOD", "STORE_ATTR"}
NAME_OPS_PLAIN = {"LOAD_NAME", "STORE_NAME", "DELETE_NAME", "IMPORT_NAME", "IMPORT_FROM",
                  "LOAD_FROM_DICT_OR_GLOBALS"}
FAST_OPS = {"LOAD_FAST", "LOAD_FAST_BORROW", "LOAD_FAST_CHECK", "LOAD_FAST_AND_CLEAR",
            "STORE_FAST", "DELETE_FAST", "MAKE_CELL"}
FAST_PAIR_OPS = {"LOAD_FAST_LOAD_FAST", "LOAD_FAST_BORROW_LOAD_FAST_BORROW"}


class NeoxDecodeError(Exception):
    """结构不合预期（消息里带偏移与观测到的字节）。"""


class Value:
    """一个 marshal 值。"""
    __slots__ = ('kind', 'v', 'off', 'size', 'ref', 'code', 'idx')

    def __init__(self, kind, v, off, size):
        self.kind = kind
        self.v = v
        self.off = off
        self.size = size
        self.ref = None
        self.code = None
        self.idx = None

    @property
    def base_kind(self):
        return self.kind[4:] if self.kind.startswith('ref:') else self.kind

    def show(self, maxstr: int = 60) -> str:
        k = self.kind
        if k == 'str':
            s = self.v if len(self.v) <= maxstr else self.v[:maxstr] + '…'
            return repr(s)
        if k == 'bytes':
            return '<bytes %d B>' % len(self.v)
        if k == 'cbytes':
            return '<co_code %d B>' % len(self.v)
        if k == 'code':
            nm = self.code.name_str if self.code else None
            return '<code %s>' % (nm if nm else '?')
        if k == 'none':
            return 'None'
        if k == 'tuple':
            return '(' + ', '.join(x.show(20) for x in self.v) + ')'
        if k == 'ref':
            return '<ref#%s 未解析>' % (self.idx if self.idx is not None else '?')
        if k.startswith('ref:'):
            i = self.idx if self.idx is not None else '?'
            if isinstance(self.v, str):
                s = self.v if len(self.v) <= maxstr else self.v[:maxstr] + '…'
                return '<ref#%s %r?>' % (i, s)
            if isinstance(self.v, list):
                return '<ref#%s 元组(%d 项)?>' % (i, len(self.v))
            return '<ref#%s %s?>' % (i, self.kind[4:])
        if k == 'mark7a':
            return '<标记 0x7a>'
        if k == 'tag3e':
            return '<标记 0x3e:%d>' % self.v
        return repr(self.v)[:maxstr]


class CodeObj:
    """一个 code object（模块体 / 函数体）。字段名与 CPython 同名。"""

    def __init__(self, **kw):
        self.off = 0
        self.code_off = 0
        self.code_len = 0
        self.holder_off = 0
        self.holder_len = 0
        self.co_code = b''
        self.argcount = self.posonly = self.kwonly = self.stacksize = self.flags = 0
        self._val = None
        self.consts: list[Value] = []
        self.names: list[Value] = []
        self.localsplusnames: list[Value] = []
        self.localspluskinds: Value | None = None
        self.filename: Value | None = None
        self.name: Value | None = None
        self.qualname: Value | None = None
        self.firstlineno = 0
        self.linetable: Value | None = None
        self.exceptiontable: Value | None = None
        self.end = 0
        self.complete = False
        self.depth = 0
        self.parent = None
        self.children: list = []
        self.anomalies: list = []
        self.__dict__.update(kw)

    # ── 便捷属性 ──
    @staticmethod
    def _lit(v):
        """只接受【字面串】（kind == 'str'）；引用串(5a)因编号未完全复现，带 ? 不算正式值"""
        return v.v if v is not None and v.kind == 'str' else None

    @staticmethod
    def _refish(v):
        if v is not None and v.kind.startswith('ref:') and isinstance(v.v, str):
            return '%s?<ref#%s>' % (v.v, v.idx)
        return None

    @property
    def filename_str(self):
        return self._lit(self.filename)

    @property
    def name_str(self):
        return self._lit(self.name)

    @property
    def qualname_str(self):
        return self._lit(self.qualname)

    @property
    def display_name(self):
        """优先字面 qualname → 字面 name → 引用串（带 ?）→ code@off"""
        return (self.qualname_str or self.name_str
                or self._refish(self.qualname) or self._refish(self.name)
                or ('code@%d' % self.off))

    @property
    def nlocals(self):
        if self.localspluskinds is not None and isinstance(self.localspluskinds.v, bytes):
            return len(self.localspluskinds.v)
        return 0

    def const(self, i: int):
        return self.consts[i] if 0 <= i < len(self.consts) else None

    def name_at(self, i: int):
        return self.names[i] if 0 <= i < len(self.names) else None

    def var(self, i: int):
        return self.localsplusnames[i] if 0 <= i < len(self.localsplusnames) else None

    # ── 指令操作数解析 ──
    def arg_of(self, ins: Ins):
        """→ (显示串, 来源标签) ；来源 ∈ const/name/var/int/None"""
        nm = ins.name
        if nm == 'LOAD_CONST':
            v = self.const(ins.arg)
            return (v.show() if v is not None else '?<%d>' % ins.arg, 'const')
        if nm in NAME_OPS_SHIFTED:
            v = self.name_at(ins.arg >> 1)
            return (v.show() if v is not None else '?<%d>' % (ins.arg >> 1), 'name')
        if nm in NAME_OPS_PLAIN:
            v = self.name_at(ins.arg)
            return (v.show() if v is not None else '?<%d>' % ins.arg, 'name')
        if nm in FAST_PAIR_OPS:
            a, b = ins.arg >> 4, ins.arg & 0xF
            va, vb = self.var(a), self.var(b)
            return ('%s, %s' % (va.show(24) if va else a, vb.show(24) if vb else b), 'var')
        if nm in FAST_OPS:
            v = self.var(ins.arg)
            return (v.show() if v is not None else '?<%d>' % ins.arg, 'var')
        if nm == 'LOAD_SMALL_INT':
            return (str(ins.arg), 'int')
        return ('', None)

    def dis_resolved(self):
        """→ [(Ins, 解析串, 来源)] —— 带常量/名字解析的反汇编。"""
        return [(x,) + self.arg_of(x) for x in dis_code(self.co_code)]

    #: 「声明块」里 LOAD_CONST 与 STORE 之间允许出现的指令（实测模式：
    #: LOAD_CONST N + LOAD_FAST_BORROW 0 + STORE_ATTR M，中间可能再夹一条 LOAD_FAST_BORROW）
    SETUP_OK = {'LOAD_CONST', 'LOAD_FAST', 'LOAD_FAST_BORROW', 'LOAD_FAST_CHECK',
                'LOAD_FAST_BORROW_LOAD_FAST_BORROW', 'LOAD_FAST_LOAD_FAST',
                'LOAD_NAME', 'LOAD_ATTR', 'LOAD_GLOBAL', 'LOAD_SMALL_INT', 'PUSH_NULL',
                'COPY', 'SWAP', 'BUILD_LIST', 'BUILD_TUPLE', 'BUILD_MAP',
                'BUILD_CONST_KEY_MAP', 'LIST_EXTEND', 'LIST_APPEND', 'BUILD_SLICE',
                'NOP', 'NOT_TAKEN', 'TO_BOOL', 'EXTENDED_ARG'}

    def field_assignments(self, window: int = 6, strict: bool = True):
        """★ LOAD_CONST ↔ STORE_ATTR/STORE_NAME 配对 → [(字段名, 常量值, 指令偏移, 模式)]

        strict=True（默认）：只认「声明块」模式 —— 从该 LOAD_CONST 到 STORE 之间的
        所有指令都必须在本类 SETUP_OK 里（没有 CALL / IMPORT_NAME / POP_TOP 等），
        这样 `import x` / `data = bindict.bindict(...)` 这类噪声不会被误配成字段赋值。
        strict=False：只要窗口内有 LOAD_CONST 就配（宽松，噪声多）。
        """
        ins = dis_code(self.co_code)
        res = []
        for i, x in enumerate(ins):
            if x.name not in ('STORE_ATTR', 'STORE_NAME'):
                continue
            fld = self.arg_of(x)[0]
            if not fld or fld.startswith('?'):
                continue
            start = None
            for j in range(i - 1, max(-1, i - window - 1), -1):
                if ins[j].name == 'LOAD_CONST':
                    start = j
                    break
            if start is None:
                continue
            val = self.const(ins[start].arg)
            if val is None:
                continue
            if strict:
                mid = [ins[k].name for k in range(start + 1, i)]
                if any(m not in self.SETUP_OK for m in mid):
                    continue
                res.append((fld, val, x.off, 'strict'))
            else:
                res.append((fld, val, x.off, 'loose'))
        return res


class NeoXReader:
    """NeoX py314 marshal 读取器：递归解析 code object 树。"""

    def __init__(self, buf: bytes):
        self.b = buf
        self.hi = len(buf)
        self.refs: list[Value] = []
        self.codes: list[CodeObj] = []
        self.anomalies: list[str] = []
        self.ref_mismatch: list = []
        self.error: str | None = None
        self.z7a = 'marker'

    # ── 引用表（文档序：str / 元组 / code / co_code）──
    def _reg(self, val: Value) -> Value:
        if val.kind in ('str', 'tuple', 'code', 'cbytes'):
            val.ref = len(self.refs)
            self.refs.append(val)
        return val

    def resolve(self, idx: int):
        return self.refs[idx] if 0 <= idx < len(self.refs) else None

    # ── 单个值 ──
    def value(self, off: int, depth: int = 0, is_ccode: bool = False) -> Value:
        b = self.b
        if off >= self.hi or depth > 80:
            raise NeoxDecodeError('偏移 %d 越界或嵌套过深' % off)
        raw_t = b[off]
        t = raw_t
        if t not in KNOWN_TAGS:
            t = t & 0x7F
            if t not in KNOWN_TAGS:
                raise NeoxDecodeError('未知 marshal 标签 0x%02x @%d（上下文 %s）'
                                      % (raw_t, off, b[off:off + 12].hex(' ')))
        if t in (0x79, 0x53):
            t = 0xD3
        if t == 0x78:
            return Value('none', None, off, 1)
        if t == 0xD3:
            ln = b[off + 1]
            st = off + 2
            if ln == 0xFF:
                if off + 6 > self.hi:
                    raise NeoxDecodeError('长串头越界 @%d' % off)
                ln = struct.unpack_from('<I', b, off + 2)[0]
                st = off + 6
            if st + ln > self.hi or ln > 8_000_000:
                raise NeoxDecodeError('串长度越界 @%d (len=%d)' % (off, ln))
            raw = b[st:st + ln]
            s = None
            for enc in ('utf-8', 'gbk', 'latin1'):
                try:
                    s = raw.decode(enc)
                    break
                except Exception:
                    continue
            if s is None:
                s = raw.decode('latin1', 'replace')
            return self._reg(Value('str', s, off, st + ln - off))
        if t == 0x7B:
            if off + 5 > self.hi:
                raise NeoxDecodeError('bytes 头越界 @%d' % off)
            ln = struct.unpack_from('<I', b, off + 1)[0]
            if ln > self.hi - off - 5:
                raise NeoxDecodeError('bytes 长度越界 @%d (len=%d)' % (off, ln))
            v = Value('cbytes' if is_ccode else 'bytes', b[off + 5:off + 5 + ln], off, 5 + ln)
            return self._reg(v) if is_ccode else v
        if t == 0x2E:
            v = Value('tuple', [], off, 0)
            self._reg(v)
            j = off + 2
            for _ in range(b[off + 1]):
                it = self.value(j, depth + 1)
                v.v.append(it)
                j = it.off + it.size
            v.size = j - off
            return v
        if t == CODE_TAG:
            c, _end = self.parse_code(off, depth + 1)
            return c._val
        if t == 0x5A:
            if off + 5 > self.hi:
                raise NeoxDecodeError('ref 越界 @%d' % off)
            idx = struct.unpack_from('<I', b, off + 1)[0]
            v = Value('ref', idx, off, 5)
            v.idx = idx
            tgt = self.resolve(idx)
            if tgt is not None:
                v.v = tgt.v
                v.kind = 'ref:' + tgt.kind
                v.code = tgt.code
            return v
        if t == 0xBE:
            return Value('uint', struct.unpack_from('<I', b, off + 1)[0], off, 5)
        if t == 0x7A:
            if self.z7a == 'i32':
                return Value('int', struct.unpack_from('<i', b, off + 1)[0], off, 5)
            return Value('mark7a', None, off, 1)
        if t == 0x3C:
            return Value('int', b[off + 1], off, 2)
        if t == 0x3E:
            return Value('tag3e', struct.unpack_from('<I', b, off + 1)[0], off, 5)
        if t == 0x22:
            if off + 9 > self.hi:
                raise NeoxDecodeError('f64 越界 @%d' % off)
            return Value('float', struct.unpack_from('<d', b, off + 1)[0], off, 9)
        if t == 0x12:
            if off + 5 > self.hi:
                raise NeoxDecodeError('f32 越界 @%d' % off)
            return Value('float32', struct.unpack_from('<f', b, off + 1)[0], off, 5)
        raise NeoxDecodeError('未知 marshal 标签 0x%02x @%d' % (raw_t, off))

    # ── 表 / blob ──
    def table(self, off: int, depth: int = 0):
        v = self.value(off, depth)
        if v.kind in ('tuple', 'ref:tuple'):
            return list(v.v), v.off + v.size, None
        return [], v.off + v.size, v.kind

    def _blob_lenient(self, off: int):
        """filename / name / qualname 槽：允许任意类型的 5a 引用（引用表编号未完全复现时
        会解析成别的对象）⇒ 类型不符就标 anomaly 并按【未解析】处理，绝不冒充正确值。"""
        v = self.value(off)
        if v.base_kind in ('bytes', 'str'):
            return v, v.off + v.size
        if v.kind.startswith('ref:') or v.kind == 'ref':
            if v.kind != 'ref:str':
                self.ref_mismatch.append((v.off, v.idx, v.kind[4:] if v.kind != 'ref' else '未解析'))
                v.kind = 'ref'
                v.v = v.idx
            return v, v.off + v.size
        raise NeoxDecodeError('字段 @%d 既不是 bytes/串 也不是引用（%s）' % (off, v.kind))

    def _blob(self, off: int):
        v = self.value(off)
        if v.base_kind not in ('bytes', 'str'):
            raise NeoxDecodeError('字段 @%d 期望 bytes/串，实得 %s（上下文 %s）'
                                  % (off, v.kind, self.b[off:off + 12].hex(' ')))
        return v, v.off + v.size

    # ── code object ──
    def parse_code(self, off: int, depth: int = 0, parent: CodeObj | None = None):
        b = self.b
        if off + 21 > self.hi or b[off] != CODE_TAG:
            raise NeoxDecodeError('@%d 不是 code 对象（0x%02x）'
                                  % (off, b[off] if off < self.hi else -1))
        arg, pos, kw, stk, flg = struct.unpack_from('<IIIII', b, off + 1)
        if arg > 255 or pos > 255 or kw > 255 or stk > 0xFFFF or flg > 0x7FFFFFFF:
            raise NeoxDecodeError('@%d code 头不合理 %r' % (off, [arg, pos, kw, stk, flg]))
        p = off + 21
        c = CodeObj(off=off, argcount=arg, posonly=pos, kwonly=kw,
                    stacksize=stk, flags=flg, depth=depth, parent=parent)
        cv = Value('code', None, off, 0)
        cv.code = c
        c._val = cv
        if depth > 0:                                  # 根 code 不入引用表（实测）
            self._reg(cv)
        self.codes.append(c)                           # 提前登记：中途失败也能列出已解析的
        if b[p] not in BYTES_TAGS:
            raise NeoxDecodeError('@%d 缺 co_code 标签（0x%02x）' % (p, b[p]))
        cb = self.value(p, depth, is_ccode=True)
        end = cb.off + cb.size
        c.holder_off, c.holder_len = cb.off, cb.size
        c.code_off, c.code_len, c.co_code = cb.off + 5, len(cb.v), cb.v
        for key in ('consts', 'names', 'localsplusnames'):
            items, end, anom = self.table(end, depth)
            setattr(c, key, items)
            if anom:
                msg = '%s 表位置解析成 %s' % (key, anom)
                c.anomalies.append(msg)
                self.anomalies.append('code@%d %s' % (off, msg))
        v, end = self._blob_lenient(end)      # localspluskinds（也见过 5a 引用）
        c.localspluskinds = v
        for key in ('filename', 'name', 'qualname'):
            v, end = self._blob_lenient(end)
            if v.kind == 'ref':
                c.anomalies.append('%s 是引用 #%s（解析结果类型不符/未解析，已按未解析显示）'
                                   % (key, v.idx))
            setattr(c, key, v)
        if end + 4 > self.hi:
            raise NeoxDecodeError('@%d 缺 co_firstlineno' % off)
        c.firstlineno = struct.unpack_from('<I', b, end)[0]
        end += 4
        for key in ('linetable', 'exceptiontable'):
            v, end = self._blob_lenient(end)   # 也常是 5a 引用（同一张表复用）
            setattr(c, key, v)
        c.end = end
        c.complete = True
        cv.size = end - off
        if parent is not None:
            parent.children.append(c)
        return c, end

    def read_top(self):
        return self.parse_code(0, 0, None)


def load_module(path, z7a: str = 'marker'):
    """读一个 .py（NeoX 字节码）文件 → (reader, 顶层 CodeObj|None, 解析终点)。
    解析失败时 reader.error 带原因（含偏移与观测字节）。"""
    buf = Path(path).read_bytes()
    modes = [z7a] + (['i32'] if z7a == 'marker' else [])
    last = None
    for mode in modes:
        r = NeoXReader(buf)
        r.z7a = mode
        try:
            c, end = r.read_top()
            return r, c, end
        except NeoxDecodeError as e:
            r.error = str(e)
            last = r
    return last, None, 0


def all_codes_from_root(root: CodeObj):
    """深度优先取出全部 code 对象（按偏移排序）。"""
    out, stack = [], [root]
    while stack:
        c = stack.pop()
        out.append(c)
        for v in c.consts:
            if v.kind == 'code' and v.code is not None:
                stack.append(v.code)
    out.sort(key=lambda x: x.off)
    return out


def complete_codes(reader):
    """递归解析中途失败时，返回【字段已完整解析】的 code 对象（按偏移排序）。
    用于 UI/lib 模块的降级输出：哪怕顶层没解完，先把解出来的函数列出来。"""
    return sorted([c for c in reader.codes if c.complete], key=lambda x: x.off)


def scan_code_headers(buf: bytes, min_score: float = 0.55):
    """回退路径：按特征扫 `73 <5×u32> <7b|fb> <u32 len>` 的 code 头，
    用「payload 反汇编已知 opcode 占比」过滤 ⇒ 递归解析中途失步时仍可列出函数。
    → [(off, argcount, stacksize, flags, code_off, code_len, score)]"""
    b = buf
    n = len(b)
    out = []
    i = 0
    while i < n - 26:
        if b[i] != CODE_TAG:
            i += 1
            continue
        arg, pos, kw, stk, flg = struct.unpack_from('<IIIII', b, i + 1)
        if not (arg <= 255 and pos <= 255 and kw <= 255 and stk <= 0xFFFF
                and flg <= 0x7FFFFFFF and b[i + 21] in BYTES_TAGS):
            i += 1
            continue
        ln = struct.unpack_from('<I', b, i + 22)[0]
        if not (8 <= ln <= n - i - 26):
            i += 1
            continue
        ins = dis_code(b[i + 26:i + 26 + ln])
        if not ins:
            i += 1
            continue
        score = sum(1 for x in ins if x.name != '?') / len(ins)
        if score >= min_score:
            out.append((i, arg, stk, flg, i + 26, ln, round(score, 3)))
            i += 26 + ln
            continue
        i += 1
    return out


def read_record_at(buf: bytes, off: int):
    """只解析 off 处那一个 code 对象的字段（不递归进它的 consts），用于回退扫描。
    → (CodeObj, None) 或 (None, 失败原因)"""
    r = NeoXReader(buf)
    try:
        b = buf
        arg, pos, kw, stk, flg = struct.unpack_from('<IIIII', b, off + 1)
        p = off + 21
        c = CodeObj(off=off, argcount=arg, stacksize=stk, flags=flg)
        cv = Value('code', None, off, 0)
        cv.code = c
        c._val = cv
        cb = r.value(p, is_ccode=True)
        end = cb.off + cb.size
        c.holder_off, c.holder_len = cb.off, cb.size
        c.code_off, c.code_len, c.co_code = cb.off + 5, len(cb.v), cb.v
        for key in ('consts', 'names', 'localsplusnames'):
            items, end, _a = r.table(end)
            setattr(c, key, items)
        v, end = r._blob_lenient(end)
        c.localspluskinds = v
        for key in ('filename', 'name', 'qualname'):
            v, end = r._blob_lenient(end)
            setattr(c, key, v)
        c.firstlineno = struct.unpack_from('<I', b, end)[0]
        end += 4
        for key in ('linetable', 'exceptiontable'):
            v, end = r._blob_lenient(end)
            setattr(c, key, v)
        c.end = end
        c.complete = True
        cv.size = end - off
        return c, None
    except (NeoxDecodeError, struct.error) as e:
        return None, str(e)


def pool_strings(blob: bytes, min_len: int = 3, limit: int = 200000):
    """从 bytes 常量块里抽可读串（短串/长串）。→ [(offset, 串)]"""
    res = []
    n = len(blob)
    i = 0
    while i < n - 2 and len(res) < limit:
        t = blob[i]
        if t in STR_TAGS:
            ln = blob[i + 1]
            st = i + 2
            if ln == 0xFF:
                if i + 6 > n:
                    i += 1
                    continue
                ln = struct.unpack_from('<I', blob, i + 2)[0]
                st = i + 6
            if min_len <= ln <= 8192 and st + ln <= n:
                raw = blob[st:st + ln]
                s = None
                try:
                    s = raw.decode('utf-8')
                except Exception:
                    s = None
                if s is not None and '\x00' not in s:
                    res.append((i, s))
                    i = st + ln
                    continue
        i += 1
    return res


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="NeoX 方言字节码反汇编器（旧版轻接口）")
    ap.add_argument("module")
    ap.add_argument("--blob", type=int, help="只反汇编指定偏移的码段")
    ap.add_argument("--tables", action="store_true", help="列出常量/名字表")
    a = ap.parse_args()
    buf = Path(a.module).read_bytes()
    print("★ %s ｜ %d B ｜ 码段 %d 个" % (Path(a.module).name, len(buf), len(blobs(buf))))
    if a.tables:
        for off, cnt, items in const_tables(buf):
            print("   @%-8d 2e %-3d → %s" % (off, cnt, items[:10]))
        return
    for off, body in blobs(buf):
        if a.blob is not None and off != a.blob:
            continue
        print("══ 码段 @%d（%d B）" % (off, len(body)))
        for ins in dis_code(body):
            print("   %5d  %-32s %s" % (ins.off, ins.name, ins.arg))


if __name__ == "__main__":
    main()
