# -*- coding: utf-8 -*-
"""mini_yaml.py — 无 PyYAML 时的**最小可用** YAML 解析器（兜底用）

## 为什么需要它

克隆者可能直接用系统 python（没装 PyYAML）。执行图 `rules/pipeline_graph.yml`
是编排器的唯一执行来源 —— 读不到它，编排器就没法用。

参照 `checks/portability_audit.py` 的既有做法：缺依赖时**明确告警 + 内置兜底**，
而不是让工具静默降级成「看起来正常、结果全错」。

## 支持范围（够用即可，不是通用 YAML）

* 嵌套映射 `key:` / `key: value`
* 列表 `- item`（标量项与映射项）
* 块标量 `|`（保留换行）与折叠标量 `>`（合并为一行）
* 引号包裹的标量（单/双引号）
* 行内注释（`#` 前有空格才算注释，避免误伤 URL 里的 `#`）
* 布尔 / 数字 / null 的自动转换

**不支持**：锚点、别名、标签、流式集合、多文档、复杂锚点键。
遇到这些会抛 `MiniYamlError`，由调用方决定如何降级。

## 用法

```python
from mini_yaml import loads
data = loads(text)
```
"""
from __future__ import annotations

import re


class MiniYamlError(ValueError):
    """兜底解析器无法处理的结构。"""


_TRUE = {"true", "yes", "on"}
_FALSE = {"false", "no", "off"}
_NULL = {"", "null", "~", "none"}

# ★ 映射键的正则：**键名不允许含空格**，且冒号必须后接空格或行尾。
#   否则值里带冒号的标量（如 `41_还原树/pe/资源`、URL 里的 `://`）会被误判成映射。
_KEY_RE = re.compile(r"^([^:\s][^:]*?):(?:\s+(.*))?$")


def _is_key_line(text: str) -> bool:
    """判断一行是否为映射项（而非含冒号的普通标量）。"""
    if text.startswith("- ") or text == "-":
        return False
    m = _KEY_RE.match(text)
    if not m:
        return False
    # 键名里有空格 ⇒ 更可能是「值里带冒号」的普通标量
    if " " in m.group(1).strip():
        return False
    return True


def _strip_comment(s: str) -> str:
    """去掉行内注释。`#` 前必须是空格或行首才算注释（避免误伤 URL 片段）。"""
    out = []
    quote = None
    i = 0
    while i < len(s):
        c = s[i]
        if quote:
            out.append(c)
            if c == quote:
                quote = None
        elif c in "\"'":
            quote = c
            out.append(c)
        elif c == "#" and (i == 0 or s[i - 1] in " \t"):
            break
        else:
            out.append(c)
        i += 1
    return "".join(out).rstrip()


def _scalar(tok: str):
    """把标量 token 转成 Python 值。"""
    t = tok.strip()
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "\"'":
        return t[1:-1]
    low = t.lower()
    if low in _NULL:
        return None
    if low in _TRUE:
        return True
    if low in _FALSE:
        return False
    if re.fullmatch(r"-?\d+", t):
        try:
            return int(t)
        except ValueError:
            pass
    if re.fullmatch(r"-?\d+\.\d+", t):
        try:
            return float(t)
        except ValueError:
            pass
    return t


def _indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" "))


class _Line:
    __slots__ = ("indent", "text", "raw", "no")

    def __init__(self, raw: str, no: int):
        self.raw = raw
        self.no = no
        self.indent = _indent_of(raw)
        self.text = _strip_comment(raw.strip())


def _collect_lines(text: str) -> list[_Line]:
    out: list[_Line] = []
    for no, raw in enumerate(text.splitlines(), 1):
        if not raw.strip():
            continue
        s = raw.strip()
        if s.startswith("#"):
            continue
        if s in ("---", "..."):
            continue
        out.append(_Line(raw, no))
    return out


def _read_block_scalar(lines: list[_Line], start: int, parent_indent: int,
                      folded: bool) -> tuple[str, int]:
    """读块标量（| / >）。返回 (内容, 下一行索引)。"""
    buf: list[str] = []
    i = start
    base = None
    while i < len(lines):
        ln = lines[i]
        if ln.indent <= parent_indent and ln.text not in ("|", ">"):
            break
        if base is None:
            base = ln.indent
        buf.append(ln.raw[base:] if ln.indent >= base else ln.raw.strip())
        i += 1
    content = (" ".join(x.strip() for x in buf) if folded else "\n".join(buf))
    # ★ 块标量保留尾部换行（与 PyYAML 一致）—— 不对齐会导致同一文件的两种解析
    #   结果指纹不同，diff/快照体系里出现假差异。
    if content and not content.endswith("\n"):
        content += "\n"
    return content, i


def _parse_block(lines: list[_Line], idx: int, indent: int) -> tuple[object, int]:
    """解析一个缩进块（映射或列表），返回 (值, 下一行索引)。"""
    if idx >= len(lines):
        return None, idx
    if lines[idx].text.startswith("- "):
        return _parse_list(lines, idx, indent)
    if lines[idx].text == "-":
        return _parse_list(lines, idx, indent)
    return _parse_map(lines, idx, indent)


def _parse_list(lines: list[_Line], idx: int, indent: int) -> tuple[list, int]:
    out: list = []
    while idx < len(lines) and lines[idx].indent == indent:
        ln = lines[idx]
        if not (ln.text == "-" or ln.text.startswith("- ")):
            break
        rest = ln.text[1:].strip()
        if not rest:
            # "-" 单独一行：子块
            if idx + 1 < len(lines) and lines[idx + 1].indent > indent:
                val, idx = _parse_block(lines, idx + 1, lines[idx + 1].indent)
                out.append(val)
                continue
            out.append(None)
            idx += 1
            continue
        # "- key: value" —— 映射项。★ 后续同 item_indent 的行是**同一个映射项的后续键**，
        #   不是新的列表项（YAML 规范：紧凑写法 `- k: v` 后续键与 k 同列）。
        m = _KEY_RE.match(rest) if _is_key_line(rest) else None
        if m:
            item: dict = {}
            key = _scalar(m.group(1))
            val_text = (m.group(2) or "").strip()
            item_indent = ln.indent + 2
            if val_text in ("|", ">"):
                content, nxt = _read_block_scalar(lines, idx + 1, ln.indent, val_text == ">")
                item[key] = content
                idx = nxt
            elif val_text:
                if val_text.startswith("[") or val_text.startswith("{"):
                    val, idx = _read_flow(lines, idx + 1, val_text)
                    item[key] = val
                else:
                    item[key] = _scalar(val_text)
                    idx += 1
            else:
                # 空值：子块（同 item_indent 的映射续写 / 更深的块）
                if idx + 1 < len(lines) and lines[idx + 1].indent == item_indent \
                        and not (lines[idx + 1].text.startswith("- ") or lines[idx + 1].text == "-"):
                    val, idx = _parse_map(lines, idx + 1, item_indent)
                    item[key] = val
                elif idx + 1 < len(lines) and lines[idx + 1].indent > item_indent:
                    val, idx = _parse_block(lines, idx + 1, lines[idx + 1].indent)
                    item[key] = val
                else:
                    item[key] = None
                    idx += 1
            # 继续读同一映射项的后续键
            while idx < len(lines) and lines[idx].indent == item_indent \
                    and not (lines[idx].text.startswith("- ") or lines[idx].text == "-"):
                sub, idx = _parse_map(lines, idx, item_indent)
                item.update(sub)
            out.append(item)
            continue
        # 普通标量项
        out.append(_scalar(rest))
        idx += 1
    return out, idx


def _read_flow(lines: list[_Line], idx: int, start: str) -> tuple[object, int]:
    """读流式集合（`[a, b, ...]` / `{k: v, ...}`），支持跨行。

    start 是已读到的第一个片段（形如 "[a, b" 或 "{k: v"）。
    返回 (值, 下一行索引)。
    """
    buf = start
    # ★ 深度必须**累计**：每读一行就把该行的括号计入 buf，而不是用该行的净增量。
    #   （用净增量会让跨行流式集合提前判定闭合。）
    def _depth(s: str) -> int:
        return s.count("[") + s.count("{") - s.count("]") - s.count("}")

    depth = _depth(buf)
    while depth > 0 and idx < len(lines):
        nxt = lines[idx]
        buf += " " + nxt.text
        depth = _depth(buf)
        idx += 1
    return _parse_flow_value(buf), idx


def _parse_flow_value(buf: str):
    """解析已闭合的流式集合文本。"""
    b = buf.strip()
    if b.startswith("[") and b.endswith("]"):
        inner = b[1:-1].strip()
        if not inner:
            return []
        return [_scalar(x) for x in _split_flow(inner)]
    if b.startswith("{") and b.endswith("}"):
        inner = b[1:-1].strip()
        out: dict = {}
        if not inner:
            return out
        for part in _split_flow(inner):
            if ":" in part:
                k, v = part.split(":", 1)
                out[_scalar(k)] = _scalar(v)
            else:
                out[_scalar(part)] = None
        return out
    return _scalar(b)


def _split_flow(inner: str) -> list[str]:
    """按顶层逗号切分流式集合内容（忽略括号内的逗号）。"""
    parts: list[str] = []
    depth = 0
    cur: list[str] = []
    quote = None
    for ch in inner:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
            continue
        if ch in "\"'":
            quote = ch
            cur.append(ch)
            continue
        if ch in "[{":
            depth += 1
        elif ch in "]}":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
            continue
        cur.append(ch)
    tail = "".join(cur).strip()
    if tail:
        parts.append(tail)
    return [p for p in parts if p]


def _parse_map(lines: list[_Line], idx: int, indent: int) -> tuple[dict, int]:
    out: dict = {}
    while idx < len(lines):
        ln = lines[idx]
        if ln.indent < indent:
            break
        if ln.indent > indent:
            raise MiniYamlError(f"第 {ln.no} 行缩进异常：{ln.text[:60]!r}")
        # ★ 顶层（或任意层）映射后面跟同缩进的列表项时，列表属于**上一个键**，
        #   不能在这里 break —— 否则映射会提前结束，后续顶层键全部丢失。
        if ln.text.startswith("- ") or ln.text == "-":
            break
        m = _KEY_RE.match(ln.text) if _is_key_line(ln.text) else None
        if not m:
            raise MiniYamlError(f"第 {ln.no} 行无法解析：{ln.text[:60]!r}")
        key = _scalar(m.group(1))
        val_text = (m.group(2) or "").strip()
        if val_text in ("|", ">"):
            content, idx = _read_block_scalar(lines, idx + 1, ln.indent, val_text == ">")
            out[key] = content
            continue
        if val_text:
            # 流式集合（可能跨行）
            if val_text.startswith("[") or val_text.startswith("{"):
                val, idx = _read_flow(lines, idx + 1, val_text)
                out[key] = val
                continue
            # ★ 隐式多行标量：值行后跟**更深缩进**的续行。
            #   PyYAML 对普通多行标量的行为是**折为空格连接**（不是换行）——
            #   块标量（| / >）才保留换行。两种规则不同，别混。
            if idx + 1 < len(lines) and lines[idx + 1].indent > indent:
                parts = [val_text]
                idx += 1
                while idx < len(lines) and lines[idx].indent > indent:
                    parts.append(lines[idx].text)
                    idx += 1
                out[key] = " ".join(parts)
                continue
            out[key] = _scalar(val_text)
            idx += 1
            continue
        # 空值 → 子块？
        if idx + 1 < len(lines):
            nxt = lines[idx + 1]
            if nxt.indent > indent:
                val, idx = _parse_block(lines, idx + 1, nxt.indent)
                out[key] = val
                continue
            if nxt.indent == indent and (nxt.text.startswith("- ") or nxt.text == "-"):
                val, idx = _parse_list(lines, idx + 1, indent)
                out[key] = val
                continue
        out[key] = None
        idx += 1
    return out, idx


def loads(text: str) -> dict:
    """解析 YAML 文本为 dict。空文本返回 {}。"""
    lines = _collect_lines(text)
    if not lines:
        return {}
    val, _ = _parse_block(lines, 0, lines[0].indent)
    return val if isinstance(val, dict) else {"__root__": val}


def load(path) -> dict:
    """读文件并解析（utf-8）。"""
    import pathlib
    p = pathlib.Path(path)
    return loads(p.read_text(encoding="utf-8"))


if __name__ == "__main__":
    import sys
    print(load(sys.argv[1]))
