# -*- coding: utf-8 -*-
"""把 calc_internal 伪代码按阶段整理成两条 issue 评论正文（Markdown）。

正文由本地伪代码文件生成，避免手打；
输出到 scratch，供 gh issue comment --body-file 使用。
"""
from __future__ import annotations

import pathlib

SRC = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")
OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")

REPO = "https://github.com/lespre/lifeafter-toolkit/blob/main/00_%E8%A7%84%E8%8C%83%E4%B8%8E%E5%B7%A5%E5%85%B7/%E6%B2%BB%E7%90%86/%E6%89%8B%E5%86%8C/"


def block(name: str) -> str:
    p = SRC / name
    txt = p.read_text(encoding="utf-8", errors="replace").rstrip()
    return "```text\n" + txt + "\n```\n"


def main() -> int:
    part1 = """按你说的，分阶段贴。这一段是**主流程**：`calc_internal` 的完整伪代码（1/2）。

说明：
- `L<n>` 是原函数的字节码偏移，方便你按地址对回反汇编；
- `v5` = hurt 参数包（dict），`v1` = 攻击方，`v0` = 防守方；
- `trigger_event('before_calc')` 是**唯一**在算术前执行的外部钩子；
- `source_calc_stage_2` / `target_calc_stage_finish` 里只有事件分发，没有乘法。

"""
    part1 += block("pseudo_calc_internal.txt")
    part1 += """
同目录还有这几份（仓库里也有副本）：

```
pseudo_handle_critical_hit.txt        暴击判定
pseudo_get_body_part_hurt_rate.txt    部位系数
pseudo__apply_rate_factor.txt         分段换算（压缩曲线求值）
```

下一段贴这三个子阶段的伪代码。
"""

    part3 = """继续，三个子阶段的伪代码（2/2）。

**① 部位系数 `get_body_part_hurt_rate`**

"""
    part3 += block("pseudo_get_body_part_hurt_rate.txt")
    part3 += """
**② 暴击判定 `handle_critical_hit`**

"""
    part3 += block("pseudo_handle_critical_hit.txt")
    part3 += """
**③ 压缩曲线求值 `_apply_rate_factor`**

"""
    part3 += block("pseudo__apply_rate_factor.txt")
    part3 += """
## 怎么读这三段

```
攻击方是玩家时才会走 ③（enable_compress_attr）
① 的结果是"部位加成率"，进 ③ 之前是原始值
② 是纯加法桶，不进压缩
```

仓库位置（和上面链接同一份）：
`00_规范与工具/治理/手册/伤害伪代码/`

如果你需要 `calc_internal` 之前的**服务端最终值**（有没有硬上限、叠加顺序），那部分只能反汇编 `libclient_x64`，客户端伪代码给不出。
"""

    (OUT / "issue3_pseudo_1.md").write_text(part1, encoding="utf-8")
    (OUT / "issue3_pseudo_2.md").write_text(part3, encoding="utf-8")
    print("生成", (OUT / "issue3_pseudo_1.md"), len(part1), "字节")
    print("生成", (OUT / "issue3_pseudo_2.md"), len(part3), "字节")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
