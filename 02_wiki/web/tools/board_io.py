# -*- coding: utf-8 -*-
"""board_io.py — 板文件（boards/*.json 与同名 .js）的**统一读写入口**

## 为什么有这个模块

2026-10-30 实测：53 块入库板共 386MB，其中 **231MB 是 .js 的逐字节副本**
（`build_wiki.py` 把每个 .json 原样包成 `window.WIKI_BOARD_x = {...}`）。
加上 JSON 自身的缩进空白，克隆者要下载的体积里有大量纯冗余。

两个方案在此收敛为**一个**序列化口径：

1. **紧凑化**：条目内部不缩进，每个条目占一行 —— 体积与「全紧凑单行」几乎相同
   （实测 item_master_full：62.5MB → 50.7MB），但保留行边界便于 diff 与调试。
2. **溯源常量上提**：见 `provenance_defaults.py`。

## 铁律

- **只改格式，不改数据**：`dumps_board` 输出与 `json.loads(原文件)` 语义严格等价。
  紧凑化不得改变任何条目的字段与取值。
- **幂等**：同一 board 对象连续 dumps 两次，字节完全相同。
- **UTF-8 + LF**：`newline="\n"` 固定换行，避免 Windows 上写出 CRLF
  （仓库 `core.autocrlf=true` 时，CRLF 会在入库时被归一化回来，但工作区字节会变，
   让人误以为文件「变了」—— 实测工作区 67.5MB vs 仓库 65.5MB 正是此因）。
- **.js 与 .json 同源**：`.js` 由 `.json` 内容派生，两者永远一致。

## 用法

```python
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from board_io import dumps_board, dumps_board_js, write_board, write_board_pair
```
"""
from __future__ import annotations

import json
import os
import pathlib
from typing import Any

# 条目内部紧凑分隔符（无空格）
_SEPARATORS = (",", ":")


def _canonical(obj: Any) -> str:
    """紧凑 JSON 序列化：中文不转义、无多余空白。"""
    return json.dumps(obj, ensure_ascii=False, separators=_SEPARATORS)


def dumps_board(board: dict[str, Any]) -> str:
    """把板对象序列化成紧凑格式：meta 单行，每个 item 一行。

    格式形如::

        {"meta":{...},"periods":[...],"items":[
        {...},
        {...}
        ]}

    ★ 顶层**保留全部键**（不只 meta/items）—— 有些板还有 periods / stats 等顶层键，
      写死两个键会把它们丢掉（实测 title_catalog 有顶层 periods）。
      键序 = 原 dict 插入序，未知键原样保留。

    与 `json.loads(原文件)` 语义等价。
    """
    items = board.get("items", [])
    if not isinstance(items, list):
        items = []
    # 顶层键序：原插入序，但把 items 挪到最后（items 内容单独成行更好读）
    head_parts: list[str] = []
    for k, v in board.items():
        if k == "items":
            continue
        head_parts.append(_canonical(k) + ":" + _canonical(v))
    head = "{" + ",".join(head_parts)
    if head_parts:
        head += ","
    body = ",\n".join(_canonical(it) for it in items)
    return head + '"items":[\n' + body + "\n]\n}"


def dumps_board_js(board_id: str, board_text: str) -> str:
    """由板 JSON 文本派生同名 .js（window 全局变量形式）。

    ★ 必须与 .json 同源：`.js` 只是 `window.WIKI_BOARD_<id> = <json>;` 的包装。
    """
    return f"window.WIKI_BOARD_{board_id} = " + board_text.rstrip() + ";\n"


def write_text(path: pathlib.Path, text: str) -> None:
    """以 UTF-8 + LF 写文本（幂等；不追加空行）。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def write_board(path_json: pathlib.Path, board: dict[str, Any]) -> str:
    """写板 .json，返回写入的文本内容。"""
    text = dumps_board(board)
    write_text(path_json, text)
    return text


def write_board_pair(path_json: pathlib.Path, board: dict[str, Any],
                     board_id: str | None = None) -> tuple[str, str]:
    """同时写 .json 与同名 .js，返回 (json 文本, js 文本)。"""
    text = write_board(path_json, board)
    bid = board_id or path_json.stem
    js = dumps_board_js(bid, text)
    write_text(path_json.with_suffix(".js"), js)
    return text, js


def board_sizes(board: dict[str, Any]) -> tuple[int, int]:
    """返回 (紧凑后 json 字节数, 紧凑后 js 字节数) —— 用于收益测算。"""
    j = dumps_board(board).encode("utf-8")
    s = dumps_board_js("x", dumps_board(board)).encode("utf-8")
    return len(j), len(s)


if __name__ == "__main__":
    import sys
    src = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if not src:
        print(__doc__)
        raise SystemExit(0)
    raw = src.read_text(encoding="utf-8-sig")
    d = json.loads(raw)
    old = len(raw.encode("utf-8"))
    new, newjs = board_sizes(d)
    # 校验语义等价
    assert json.loads(dumps_board(d)) == d, "紧凑化改变了数据语义！"
    print(f"{src.name}")
    print(f"  旧 (缩进)      {old/1048576:8.2f} MB")
    print(f"  新 (紧凑)      {new/1048576:8.2f} MB   省 {(old-new)/1048576:.2f} MB "
          f"({100*(1-new/old):.0f}%)")
    print(f"  新 .js         {newjs/1048576:8.2f} MB")
    print(f"  行数           {raw.count(chr(10))} → {dumps_board(d).count(chr(10))}")
