# -*- coding: utf-8 -*-
"""bindict 解码器（Python 版）— 依据引擎反编译规范实现。

规范来源：APK lib/x86_64/libclient.so 反编译（2026-10-02）
  值：tag = *p++；type = tag & 0x0F；width = tag & 0xF0
    type 1  整数   LEB128；width==0x10 → ZigZag 有符号
    type 2  浮点   width==0x20 → float64(8B)；width==0x10 → float32(4B)
    type 3  布尔   1 字节
    type 4  None
    type 5  共享节点引用  varint 索引 → shared[idx]
    type 6  容器A  位宽打包数组（tag&0x80 走共享表；tag&0x40 省略）
    type 7  容器B  列表：tag&0x20 → 先读"公共类型字节"；tag&0x40 省略
    type 8  容器C
    type 9  容器D
    type 11 缓冲区偏移引用  varint 偏移 → 从 base+off 继续解析（容器 B 内使用）
  顶层：前 4 字节 = 长度（u32 LE），其后为根值
"""
from __future__ import annotations

import struct
from typing import Any

__all__ = ["decode", "decode_value", "BindictError"]


class BindictError(Exception):
    pass


def read_varint(buf: bytes, pos: int) -> tuple[int, int]:
    """LEB128（最多 10 字节；与引擎 FUN_01a6a2a0 一致）。"""
    value = 0
    shift = 0
    while True:
        if pos >= len(buf):
            raise BindictError("varint 越界")
        b = buf[pos]
        pos += 1
        value |= (b & 0x7F) << shift
        if not (b & 0x80):
            return value & 0xFFFFFFFFFFFFFFFF, pos
        shift += 7
        if shift > 63:
            raise BindictError("varint 过长")


def zigzag(v: int) -> int:
    return -(v & 1) ^ (v >> 1)


class Decoder:
    def __init__(self, buf: bytes):
        self.buf = buf
        self.shared: list[Any] = []

    # ---------------------------------------------------------------- 值
    def value(self, pos: int, tag: int | None = None) -> tuple[Any, int]:
        if tag is None:
            if pos >= len(self.buf):
                raise BindictError("读 tag 越界")
            tag = self.buf[pos]
            pos += 1
        t = tag & 0x0F
        w = tag & 0xF0

        if t == 1:                                  # 整数
            v, pos = read_varint(self.buf, pos)
            if w == 0x10:
                v = zigzag(v)
            return v, pos

        if t == 2:                                  # 浮点
            if w == 0x20:
                if pos + 8 > len(self.buf):
                    raise BindictError("float64 越界")
                return struct.unpack_from("<d", self.buf, pos)[0], pos + 8
            if w == 0x10:
                if pos + 4 > len(self.buf):
                    raise BindictError("float32 越界")
                return struct.unpack_from("<f", self.buf, pos)[0], pos + 4
            raise BindictError("浮点宽度非 0x10/0x20：0x%02x" % tag)

        if t == 3:                                  # 布尔
            if pos >= len(self.buf):
                raise BindictError("bool 越界")
            return self.buf[pos] != 0, pos + 1

        if t == 4:                                  # None
            return None, pos

        if t == 5:                                  # 共享节点引用
            idx, pos = read_varint(self.buf, pos)
            if idx < len(self.shared):
                return self.shared[idx], pos
            raise BindictError("共享引用越界：%d" % idx)

        if t == 11:                                 # 缓冲区偏移引用
            off, pos = read_varint(self.buf, pos)
            node, _ = self.value(off)
            return node, pos

        if t in (6, 7, 8, 9):
            return self.container(t, tag, pos)

        raise BindictError("未知类型 %d（tag=0x%02x）" % (t, tag))

    # ------------------------------------------------------------ 容器
    def container(self, t: int, tag: int, pos: int) -> tuple[Any, int]:
        if tag & 0x40:                              # 省略 → 走共享表（此处只登记不展开）
            count, pos = read_varint(self.buf, pos)
            node = {"__omitted__": True, "count": count}
            self.shared.append(node)
            return node, pos

        if t == 7:                                  # 列表（已验证）
            common = None
            if tag & 0x20:
                if pos >= len(self.buf):
                    raise BindictError("公共类型字节越界")
                common = self.buf[pos]
                pos += 1
            count, pos = read_varint(self.buf, pos)
            items = []
            self.shared.append(items)
            for _ in range(count):
                if common is None:
                    sub = self.buf[pos]
                    pos += 1
                else:
                    sub = common
                if (sub & 0x0F) == 11:              # 引用 → 从 base+off 继续
                    off, pos = read_varint(self.buf, pos)
                    v, _ = self.value(off)
                else:
                    v, pos = self.value(pos, sub)
                items.append(v)
            return items, pos

        if t == 6:
            # 位宽打包数组：先读元素位宽与数量
            bits, pos = read_varint(self.buf, pos)
            count, pos = read_varint(self.buf, pos)
            nbytes = (bits * count + 7) // 8 if bits and count else 0
            raw = self.buf[pos:pos + nbytes]
            pos += nbytes
            vals = []
            if bits:
                acc = int.from_bytes(raw, "little")
                mask = (1 << bits) - 1
                for i in range(count):
                    vals.append((acc >> (i * bits)) & mask)
            node = {"__bitpack__": True, "bits": bits, "values": vals}
            self.shared.append(node)
            return node, pos

        if t == 9:
            # 容器 D = 结构体/记录（据引擎 FUN_01a70b50）
            #   varint 字段数 N → varint M → N 次： [varint 字段索引][1 字节]
            n, pos = read_varint(self.buf, pos)
            m, pos = read_varint(self.buf, pos)
            fields = []
            self.shared.append(fields)
            for _ in range(n):
                idx, pos = read_varint(self.buf, pos)
                if pos >= len(self.buf):
                    raise BindictError("容器9 字段字节越界")
                flag = self.buf[pos]
                pos += 1
                fields.append({"field_index": idx, "flag": flag})
            return {"__struct__": fields, "m": m}, pos

        # 容器 C：结构未完全定稿 → 只按 数量 + 子值 尝试，失败则如实抛
        count, pos = read_varint(self.buf, pos)
        items = []
        self.shared.append(items)
        for _ in range(count):
            if pos >= len(self.buf):
                raise BindictError("容器%d 子项越界" % t)
            sub = self.buf[pos]
            pos += 1
            if (sub & 0x0F) == 11:
                off, pos = read_varint(self.buf, pos)
                v, _ = self.value(off)
            else:
                v, pos = self.value(pos, sub)
            items.append(v)
        return {"__container%d__" % t: items}, pos


def decode(blob: bytes, skip_header: bool = True) -> Any:
    """解一个 bindict 缓冲。skip_header=True 时跳过前 4 字节长度。"""
    start = 4 if skip_header else 0
    d = Decoder(blob)
    node, _ = d.value(start)
    return node


def decode_value(blob: bytes, pos: int = 0) -> tuple[Any, int]:
    d = Decoder(blob)
    return d.value(pos)
