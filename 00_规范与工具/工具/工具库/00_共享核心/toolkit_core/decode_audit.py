# -*- coding: utf-8 -*-
"""解码线体检：判据【不带盲区】的全面自检。

## 为什么要有它

A38 那个 bug（flag 0 把 GPK 明文 AES 毁掉，274,295 条）逃过了我上一轮的抽样测试，
因为我的判据是 `if decoded != packed and len(data) != decoded` ——
**flag 0 恒有 decoded == packed ⇒ 这一类完全不在校验内。**

⇒ 教训：判据不能只看「长度」，必须看【内容证据】，而且要能发现
  「解码把本来好好的内容弄坏了」。所以这里加一条关键判据：

    ★ 解码前后证据对比：
        raw 认出格式 且 out 认不出   ⇒ 【解码毁内容】致命（A38 正是这一类）
        out 认出格式 且 raw 认不出   ⇒ 【解码有效】
        out 与 raw 逐字节相同        ⇒ 【无变换直通】（flag 声明无压缩时应如此）
        都不认但有长度吻合            ⇒ 【中立】（无魔数的数据块，不算错）
        长度不吻合                   ⇒ 【长度不符】

覆盖维度：**每个容器 × 每个 flag** 都要抽到（上一轮我只按容器抽，没按 flag 分层）。
"""
from __future__ import annotations

import collections
import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

from toolkit_core import bulk


def entropy(b: bytes) -> float:
    if not b:
        return 0.0
    c = collections.Counter(b)
    n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


# 判据强弱：强证据 = 【内容】魔数命中。
# ★ 关键区分（第一版判据在这里栽了）：压缩流魔数【不是】内容证据 ——
#   原始以 28b52ffd（zstd）开头，只说明「它是被压过的」，本来就该被解开；
#   把它算成「原始有结构」会让每一条压缩条目都误报「解码毁内容」（实测误报 85 例）。
#   所以这里把「容器/压缩类」和「弱猜测类」都排除在内容证据之外。
NON_CONTENT = {
    "bin", "empty",
    "zstd", "zlib",              # 压缩流：不是内容
    "npk", "skpw", "1dpw", "gpk",  # 容器标记：不是内容
    "zip",                        # 打包：也不当内容证据
    "dds?", "quicktime?",         # 弱猜测
    "marshal",                    # 弱判据（首字节撞 [{( 就会中）
    "text",                       # 太宽，不当强证据
}


def _is_content(short: str) -> bool:
    """该识别结果能否作为「这份载荷已经是可用的内容」的强证据。"""
    return short not in NON_CONTENT


@dataclass
class Case:
    container: str
    row: int
    flag: int
    packed: int
    decoded: int
    verdict: str
    raw_type: str
    out_type: str
    out_len: int
    note: str = ""


@dataclass
class AuditReport:
    sampled: int = 0
    per_container_flag: dict = field(default_factory=dict)   # "容器|flag" → 计数
    verdicts: dict = field(default_factory=dict)             # 判据 → 计数
    bad: list = field(default_factory=list)                  # 致命样例
    notes: list = field(default_factory=list)
    seconds: float = 0.0

    def as_dict(self) -> dict:
        return {"sampled": self.sampled, "verdicts": self.verdicts,
                "per_container_flag": self.per_container_flag,
                "bad": self.bad[:50], "notes": self.notes,
                "seconds": round(self.seconds, 2)}


def audit(conn, res_root: Path, unpack: Callable[[bytes, int, int], bytes], *,
          per_group: int = 12, progress=None, max_rows: Optional[int] = None,
          full: bool = False, policy=None, workers: Optional[int] = None) -> AuditReport:
    """按【容器 × flag】分层抽样体检；**按容器并行**跑。

    per_group：每个（容器, flag）组合抽多少条。
    full=True：**不抽样，逐条全过**（2,300,843 条）——
               这是「确保解码线不出纰漏」的唯一硬保证；抽样只能证伪、不能证明。
    policy    ：LoadPolicy，决定并行预算（核数 × cpu_limit%）与限流上限。
    workers   ：显式指定并行数（不给就用 policy 算）。
    """
    import threading
    import time
    from concurrent.futures import ThreadPoolExecutor, as_completed

    from toolkit_core.throttle import LoadGate, LoadPolicy

    t0 = time.time()
    rep = AuditReport()
    pol = policy or LoadPolicy(kinds=("decode",))
    n_workers = workers or pol.workers()
    gate = LoadGate(pol, every=50000)
    _cnt = [0]
    _lock = threading.Lock()

    groups = conn.execute(
        "SELECT container, flag, COUNT(*) n FROM entries GROUP BY container, flag "
        "ORDER BY container, flag").fetchall()
    if progress:
        progress({"groups": len(groups), "phase": "start", "full": full,
                  "total_rows": sum(g[2] for g in groups),
                  "workers": n_workers, "cpu_limit": pol.cpu_limit})

    # 按容器归组：一个容器一个任务（容器内顺序读，容器间并行）
    per_cont: dict = {}
    for cont, flag, total in groups:
        per_cont.setdefault(cont, []).append((flag, total))

    # ★ SQLite 连接不能跨线程用（实测 ProgrammingError）。
    #   查出库文件路径，让每个 worker 自己开连接。
    db_file = None
    try:
        for _seq, _name, _f in conn.execute("PRAGMA database_list").fetchall():
            if _name == "main" and _f:
                db_file = _f
                break
    except Exception:
        db_file = None
    if not db_file:
        raise RuntimeError("拿不到索引库文件路径，无法安全并行（请用 workers=1 串行跑）")

    def _one_container(cont: str, flags: list) -> dict:
        """跑一个容器的全部 flag；返回该容器的局部结果（避免共享可变状态）。

        ★ 自己开 SQLite 连接：连接是线程绑定的，主连接不能跨线程用。
        """
        import sqlite3 as _sq
        my = _sq.connect(db_file)
        try:
            return _one_container_inner(my, cont, flags)
        finally:
            my.close()

    def _one_container_inner(myconn, cont: str, flags: list) -> dict:
        src = Path(res_root) / cont
        out = {"per_group": {}, "sampled": 0, "verdicts": {},
               "bad": [], "missing": False, "progress": []}
        if not src.is_file():
            for flag, _tot in flags:
                out["per_group"]["%s|%s" % (cont, flag)] = {"sampled": 0,
                                                            "missing_container": True}
            out["missing"] = True
            return out
        with src.open("rb") as handle:
            for flag, total in flags:
                key = "%s|%s" % (cont, flag)
                if full:
                    rows = myconn.execute(
                        "SELECT row_index,payload_offset,packed,decoded FROM entries "
                        "WHERE container=? AND flag=? ORDER BY row_index",
                        (cont, flag)).fetchall()
                else:
                    step = max(1, total // per_group)
                    picked = list(range(0, min(total, per_group * step), step))[:per_group]
                    rows = myconn.execute(
                        "SELECT row_index,payload_offset,packed,decoded FROM entries "
                        "WHERE container=? AND flag=? AND row_index IN (%s)"
                        % ",".join(map(str, picked)), (cont, flag)).fetchall()
                cnt = collections.Counter()
                for row, poff, pk, dc in rows:
                    out["sampled"] += 1
                    cnt["sampled"] += 1
                    try:
                        handle.seek(poff)
                        raw = handle.read(pk)
                        if len(raw) != pk:
                            cnt["读取短读"] += 1
                            out["bad"].append({"container": cont, "flag": flag, "row": row,
                                               "verdict": "读取短读",
                                               "note": "%d/%d" % (len(raw), pk)})
                            continue
                        data = unpack(raw, dc, flag)
                    except Exception as e:
                        cnt["解码异常"] += 1
                        out["bad"].append({"container": cont, "flag": flag, "row": row,
                                           "verdict": "解码异常",
                                           "note": "%s: %s" % (type(e).__name__, str(e)[:100])})
                        continue

                    s_raw, _ = bulk.identify(raw[:4096])
                    s_out, _ = bulk.identify(data[:4096])
                    c_raw, c_out = _is_content(s_raw), _is_content(s_out)
                    compressed = (pk != dc)

                    # ★ 解出空（本次补的判据，前两版都漏了）：
                    #   容器声明 decoded==0 ⇒ 合法占位条目（实测 scene_03 有 47 条这种）；
                    #   容器声明 decoded>0 却解出空 ⇒ 真缺陷。
                    if not data:
                        if dc <= 0 and pk <= 0:
                            v = "合法空条目"
                        else:
                            v = "★解出空"
                            out["bad"].append({"container": cont, "flag": flag, "row": row,
                                               "verdict": v,
                                               "note": "容器声明 decoded=%d/packed=%d，却解出空"
                                                       % (dc, pk)})
                        cnt[v] += 1
                        out["verdicts"][v] = out["verdicts"].get(v, 0) + 1
                        with _lock:
                            _cnt[0] += 1
                            n = _cnt[0]
                        if n % 50000 == 0:
                            info = gate.tick(n, force=True)
                            out["progress"].append(info)
                            if progress:
                                progress({"phase": "run", "rows": n,
                                          "seconds": round(time.time() - t0, 1),
                                          "cpu": (info or {}).get("cpu"),
                                          "fatal": 0, "workers": n_workers})
                        continue

                    if data == raw:
                        v = "无变换直通"
                    elif c_raw and not c_out:
                        v = "★解码毁内容"
                        out["bad"].append({"container": cont, "flag": flag, "row": row,
                                           "verdict": v, "raw_type": s_raw, "out_type": s_out,
                                           "note": "原始是 %s，解码后认不出" % s_raw})
                    elif compressed and len(data) != dc:
                        v = "★长度不符"
                        out["bad"].append({"container": cont, "flag": flag, "row": row,
                                           "verdict": v,
                                           "note": "解出 %d != 登记 decoded %d（flag %s）"
                                                   % (len(data), dc, flag)})
                    elif c_out:
                        v = "解码有效" if not c_raw else "两边都是内容"
                    else:
                        v = "中立（无魔数数据块）"
                    cnt[v] += 1
                    out["verdicts"][v] = out["verdicts"].get(v, 0) + 1

                    with _lock:
                        _cnt[0] += 1
                        n = _cnt[0]
                    if n % 50000 == 0:
                        info = gate.tick(n, force=True)
                        out["progress"].append(info)
                        if progress:
                            progress({"phase": "run", "rows": n,
                                      "seconds": round(time.time() - t0, 1),
                                      "cpu": (info or {}).get("cpu"),
                                      "fatal": sum(1 for b in out["bad"]
                                                   if b["verdict"].startswith("★")),
                                      "workers": n_workers})
                out["per_group"][key] = dict(cnt)
        return out

    with ThreadPoolExecutor(max_workers=n_workers) as ex:
        futs = {ex.submit(_one_container, c, fl): c for c, fl in per_cont.items()}
        for fut in as_completed(futs):
            r = fut.result()
            rep.sampled += r["sampled"]
            for k, v in r["verdicts"].items():
                rep.verdicts[k] = rep.verdicts.get(k, 0) + v
            rep.bad.extend(r["bad"])
            rep.per_container_flag.update(r["per_group"])
            rep.notes.extend([x for x in r["progress"] if x])
            if max_rows and rep.sampled >= max_rows:
                break

    rep.seconds = time.time() - t0
    rep.notes = list(gate.samples)
    return rep

    # ── 以下是旧串行实现，保留作参照（不会执行） ──
    for cont, flag, total in groups:
        src = Path(res_root) / cont
        key = "%s|%s" % (cont, flag)
        if not src.is_file():
            rep.per_container_flag[key] = {"sampled": 0, "missing_container": True}
            continue
        if full:
            rows = conn.execute(
                "SELECT row_index,payload_offset,packed,decoded FROM entries "
                "WHERE container=? AND flag=? ORDER BY row_index", (cont, flag)).fetchall()
        else:
            step = max(1, total // per_group)
            picked = list(range(0, min(total, per_group * step), step))[:per_group]
            rows = conn.execute(
                "SELECT row_index,payload_offset,packed,decoded FROM entries "
                "WHERE container=? AND flag=? AND row_index IN (%s)"
                % ",".join(map(str, picked)), (cont, flag)).fetchall()
        cnt = collections.Counter()
        # 逐容器打开一次文件，顺序读（全量模式下这样快得多）
        last_off = -1
        with src.open("rb") as handle:
            for row, poff, pk, dc in rows:
                rep.sampled += 1
                cnt["sampled"] += 1
                try:
                    if poff > last_off:
                        handle.seek(poff)
                    else:
                        handle.seek(poff)
                    raw = handle.read(pk)
                    last_off = poff + pk
                    if len(raw) != pk:
                        cnt["读取短读"] += 1
                        rep.bad.append({"container": cont, "flag": flag, "row": row,
                                        "verdict": "读取短读", "note": "%d/%d" % (len(raw), pk)})
                        continue
                    out = unpack(raw, dc, flag)
                except Exception as e:
                    cnt["解码异常"] += 1
                    rep.bad.append({"container": cont, "flag": flag, "row": row,
                                    "verdict": "解码异常",
                                    "note": "%s: %s" % (type(e).__name__, str(e)[:100])})
                    continue

                s_raw, _ = bulk.identify(raw[:4096])
                s_out, _ = bulk.identify(out[:4096])
                c_raw, c_out = _is_content(s_raw), _is_content(s_out)
                compressed = (pk != dc)      # 容器自己声明「有变换」

                if out == raw:
                    v = "无变换直通"
                elif c_raw and not c_out:
                    # 原始本来就是可用内容，解码后反而认不出 ⇒ 解码把它毁了（A38 正是这一类）
                    v = "★解码毁内容"
                    rep.bad.append({"container": cont, "flag": flag, "row": row,
                                    "verdict": v, "raw_type": s_raw, "out_type": s_out,
                                    "note": "原始是 %s，解码后认不出" % s_raw})
                elif compressed and len(out) != dc:
                    v = "★长度不符"
                    rep.bad.append({"container": cont, "flag": flag, "row": row,
                                    "verdict": v,
                                    "note": "解出 %d != 登记 decoded %d（flag %s）" % (len(out), dc, flag)})
                elif c_out:
                    v = "解码有效" if not c_raw else "两边都是内容"
                else:
                    v = "中立（无魔数数据块）"
                cnt[v] += 1
                rep.verdicts[v] = rep.verdicts.get(v, 0) + 1
                if progress and rep.sampled % 200000 == 0:
                    progress({"phase": "run", "rows": rep.sampled,
                              "seconds": round(time.time() - t0, 1),
                              "fatal": len([b for b in rep.bad if b["verdict"].startswith("★")])})
        rep.per_container_flag[key] = dict(cnt)
        done += 1
        if progress and not full and done % 20 == 0:
            progress({"done": done, "total": len(groups), "phase": "run"})
        if max_rows and rep.sampled >= max_rows:
            break

    rep.seconds = time.time() - t0
    return rep
