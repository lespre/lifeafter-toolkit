# -*- coding: utf-8 -*-
"""生成站点主页 index.html —— LifeAfter 拆包项目 · 左侧信息块 + 右侧三线三带。

设计约束：
  · 所有指标在生成时从真实来源读取，页面不写死；
  · 只读；产物 = 04_站点/web/index.html（静态、离线、不引外部 CDN）；
  · 任何一项采集失败都如实标注「读取失败」，不编造数值；
  · 布局：桌面视口整页一屏装完（不出现纵向滚动条）——
      顶栏（站名 + 门户入口，横贯整宽）
      左信息块（大块标题 + 实时指标 + 各区体积 + 项目健康状态，固定宽 238~312px）
      右主区（① ② ③ 三线各占一行 + D / Q 两带各占一行）
      段块宽度有上限（clamp 到 232px），超宽屏也不拉伸抽满整宽；
  · 段的详情走弹层（不撑开主布局）。

用法：  python gen_home.py            # 采集 + 生成
        python gen_home.py --json     # 只打印采集结果
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

PROJECT = Path(r"E:\la拆包项目")
WEB = PROJECT / "04_站点" / "web"
TOOLS = PROJECT / "01_工具"
OUT = WEB / "index.html"
# run_all.py index status 的同步产物（sidecar）；命令 stdout 无 JSON 时回退读它
STATUS_SIDECAR = PROJECT / "03_执行" / "10_索引" / "indexes" / "lifeafter_files_status.json"
# ★ 2026-09-28：①-4 名字规模/覆盖率 与 ①-5 热更增量摘要是「重活」，
#   主页只读 sidecar（15 秒轮询不能现算）。生成器：tools/refresh_sidecars.py
NAMES_SIDECAR = PROJECT / "03_执行" / "10_索引" / "names" / "coverage_latest.json"
DELTA_SIDECAR = PROJECT / "03_执行" / "10_索引" / "patch_manifests" / "delta_latest.json"
PY312 = Path(r"C:\Users\<user>\py312_env\Scripts\python.exe")
PY310_FALLBACK = Path(r"C:\Users\<user>\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe")

FAILS: list[str] = []
INDEX_FROM = ""  # 记录索引状态实际来源，供技术详情如实标注

# 大件目录：百万文件级，任何无差别遍历都会被拖死（25_全量拆包 ≈ 230 万文件 / ~204 GB）。
# 登记在 00_治理/规范/目录规范.md；这里是代码侧守卫，防止后来人加上扫它们的采集器。
BULK_DIRS = {"25_全量拆包", "20_提取", "site_data", "site_analysis", "site_artifacts"}


def is_bulk(path) -> bool:
    """路径任意一段命中 BULK_DIRS ⇒ 大件，不做无差别递归。"""
    return any(seg in BULK_DIRS for seg in Path(path).parts)


# ---------------------------------------------------------------- 采集
def run(cmd, cwd=None, timeout=600):
    exe = str(PY312 if PY312.exists() else PY310_FALLBACK)
    p = subprocess.run([exe] + cmd, cwd=str(cwd or TOOLS),
                       capture_output=True, timeout=timeout)
    out = p.stdout.decode("utf-8", "replace")
    err = p.stderr.decode("utf-8", "replace")
    return p.returncode, out, err


def collect_index():
    """索引状态。**优先读 sidecar，比索引库旧才起子进程重跑。**

    为什么改成这样（2026-09-26 实测）：原实现串着起两个子进程
    （`index status --no-sidecar` 与 `index status`），合计 **3.0 秒**，
    占 `collect()` 4.37s 的 68%；而 sidecar `lifeafter_files_status.json`
    本来就是 `index status` 的同步产物、每次 build/status/verify 都会刷新。
    主页是 15 秒轮询，读文件即可满足新鲜度要求。

    `INDEX_FROM` 如实标注来源，不把读文件说成现场跑。
    """
    global INDEX_FROM
    # ① 快路：sidecar 存在且不比索引库旧 ⇒ 直接读
    try:
        if STATUS_SIDECAR.is_file():
            db = STATUS_SIDECAR.parent / "lifeafter_files.sqlite3"
            side_m = STATUS_SIDECAR.stat().st_mtime
            db_m = db.stat().st_mtime if db.is_file() else 0.0
            if side_m >= db_m:
                d = json.loads(STATUS_SIDECAR.read_text(encoding="utf-8"))
                INDEX_FROM = "同步产物 %s（不比索引库旧，直接读）" % STATUS_SIDECAR.name
                return d
    except Exception as e:  # noqa: BLE001
        # 快路失败不致命，落回子进程路径；把原因留痕
        FAILS.append(f"索引 sidecar 快读失败（落回子进程）：{type(e).__name__}: {e}")

    last = None
    for cmd, tag in ((["run_all.py", "index", "status", "--no-sidecar"], "统一入口 index status"),
                     (["run_all.py", "index", "status"], "统一入口 index status（sidecar 同步）")):
        try:
            rc, out, err = run(cmd)
            m = re.search(r"\{.*\}", out, re.S)
            if m:
                d = json.loads(m.group(0))
                INDEX_FROM = tag
                return d
            last = (err or out).strip()[:200]
        except Exception as e:  # noqa: BLE001
            last = str(e)[:200]
    try:
        d = json.loads(STATUS_SIDECAR.read_text(encoding="utf-8"))
        INDEX_FROM = f"统一入口 index status 的同步产物 {STATUS_SIDECAR.name}"
        return d
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"索引状态读取失败：命令输出「{last or '空'}」/ 同步产物 {e}")
        INDEX_FROM = "读取失败"
        return {}


def collect_tool_count():
    try:
        base = TOOLS / "工具库"
        return sum(1 for p in base.rglob("*.py") if "__pycache__" not in p.parts)
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"工具数统计失败：{e}")
        return None


_SUBS_CACHE: list = []          # 进程内只枚举一次


def _cli_subcommands() -> list:
    """枚举统一 CLI 的子命令（含 index 的二级）。

    ★ 为什么不再起子进程跑 `run_all.py --help` 再正则匹配：
      2026-09-26 把 run_all.py 收敛成薄壳后，帮助文本由 toolkit_cli 产生、
      格式全变 ⇒ 原正则匹配不到，字段直接变成「读取失败」；
      而且每次采集都要起一个子进程 + 加载解析器，把 collect() 从 1.5s 拖到 5.9s，
      而主页是 15 秒轮询。改成直接问解析器，毫秒级且不会因文案改动而失配。
    """
    if _SUBS_CACHE:
        return _SUBS_CACHE[0]
    import importlib.util
    import sys as _sys
    try:
        core = TOOLS / "工具库" / "00_共享核心"
        for p in (str(core / "命令行"), str(core)):
            if p not in _sys.path:
                _sys.path.insert(0, p)
        spec = importlib.util.spec_from_file_location(
            "_gh_toolkit_cli", core / "命令行" / "toolkit_cli.py")
        m = importlib.util.module_from_spec(spec)
        _sys.modules["_gh_toolkit_cli"] = m
        spec.loader.exec_module(m)
        parser = m.build_parser()
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"统一入口列表读取失败：{type(e).__name__}: {e}")
        _SUBS_CACHE.append([])
        return []
    order = []
    for act in parser._actions:
        if act.__class__.__name__ == "_SubParsersAction":
            for name, sub in act.choices.items():
                if name not in order:
                    order.append(name)
                for a2 in sub._actions:
                    if a2.__class__.__name__ == "_SubParsersAction":
                        for n2 in a2.choices:
                            tag = "%s %s" % (name, n2)
                            if tag not in order:
                                order.append(tag)
    _SUBS_CACHE.append(order)
    return order


def collect_entries():
    """统一入口子命令列表：直接问解析器（不再起子进程、不再正则匹配文本）。"""
    return _cli_subcommands()


# 清单里每个条目的编号 / 勾选状态 / 标题 / 星级
# 清单里编号有两种写法，都要认（实测踩过：只认第一种会漏掉 D1/D3/E2）：
#   ① `- [ ] **A6 索引 sidecar 三份 json 的生成脚本找不到**（2026-…）`  编号+标题一起加粗
#   ② `- [ ] **D1** `04_站点\web\` 根目录 40+ 个…`                      只加粗编号
_CODE_RE_A = re.compile(r"^\s*-\s*\[([ x])\]\s*\*\*([A-Z]+\d+[a-z]?)\s+([^*]+)\*\*", re.M)
_CODE_RE_B = re.compile(r"^\s*-\s*\[([ x])\]\s*\*\*([A-Z]+\d+[a-z]?)\*\*\s*(.+)$", re.M)


def _clean_title(s):
    """去掉标题里的 markdown 残留：反引号、加粗星号、折叠空白、过长截断。

    ★ 实测踩过：清单里把编号单独加粗（如 **D1** 后面跟正文）时，
      直接抓正文会把 markdown 的反引号、星号带进页面。
    """
    s = re.sub(r"\s+", " ", s or "").strip()
    s = s.replace("`", "").replace("**", "")
    s = re.sub(r"\s+", " ", s).strip(" ·-—")
    return (s[:110] + "…") if len(s) > 110 else s


def parse_backlog_entries(md):
    """→ {编号: (是否已闭环, 标题)}。两种写法都收，B 先跑、A 覆盖（A 的标题更完整）。"""
    got = {}
    for m in _CODE_RE_B.finditer(md):
        code = m.group(2).upper()
        title = re.sub(r"\s+", " ", m.group(3)).strip()
        got[code] = (m.group(1) == "x", _clean_title(title))
    for m in _CODE_RE_A.finditer(md):
        code = m.group(2).upper()
        got[code] = (m.group(1) == "x", _clean_title(m.group(3)))
    return got
# 散文里引用编号的写法（中英文括号都收，支持「A1 / A2」并列）—— 旧散文格式，仅兼容用
REF_RE = re.compile(r"[（(]\s*待修\s*([A-Za-z]+\d+[a-z]?(?:\s*/\s*[A-Za-z]+\d+[a-z]?)*)\s*[）)]")
# 台账里的引用写法
LEDGER_PATH = PROJECT / "00_治理" / "台账" / "三线台账.md"
SEG_RE = re.compile(r"^##\s+(\S+)\s+(.+?)\s*$")
REF_CODE_RE = re.compile(r"#([A-Za-z]+\d+[a-z]?)")
REF_KEY_RE = re.compile(r"\{([A-Za-z_][A-Za-z0-9_.]*)\}")
REF_CHECK_RE = re.compile(r"@([a-z_][a-z0-9_]*)")   # 台账里的「可核判据」引用

_CHECKS_MOD = None
_CHECKS_SIG = None


def _checks_module():
    """惰性加载 tools/checks.py（判据注册表）；文件变了就重载。

    ★ 与 wiki_server 的 _load_gen_home 同一个理由：模块被 sys.modules 缓存，
      改了判据不重载就不生效。
    """
    global _CHECKS_MOD, _CHECKS_SIG
    import importlib.util
    p = Path(__file__).resolve().parent / "checks.py"
    try:
        st = p.stat()
        sig = (st.st_mtime_ns, st.st_size)
    except OSError:
        return None
    if _CHECKS_MOD is None or sig != _CHECKS_SIG:
        spec = importlib.util.spec_from_file_location("_home_checks", p)
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        _CHECKS_MOD, _CHECKS_SIG = m, sig
    return _CHECKS_MOD


def collect_checks(data):
    """执行台账里的可核判据（快速档现跑 + 慢速档读缓存）。"""
    mod = _checks_module()
    if mod is None:
        FAILS.append("判据模块 checks.py 缺失")
        return {}
    try:
        return mod.collect_all(data)
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"判据执行失败：{e}")
        return {}


def collect_backlog():
    """待修清单的开/闭条数。

    ★ 2026-09-28 修：原先 `open`/`done` 用【全文正则数 `[ ]` / `[x]`】，
      而 `state` 用【解析出的条目】—— 两套口径，实测对不上
      （open 21 + done 45 = 66，而解析出 65 条）。
      现在统一从 `state` 派生：一处口径，页面上的数不会自相矛盾。
    """
    try:
        md = (PROJECT / "00_治理" / "台账" / "待修问题清单.md").read_text(encoding="utf-8")
        parsed = parse_backlog_entries(md)
        state = {c: v[0] for c, v in parsed.items()}
        title = {c: v[1] for c, v in parsed.items()}
        return {"open": sum(1 for v in state.values() if v is False),
                "done": sum(1 for v in state.values() if v is True),
                "total": len(state),
                "state": state, "title": title}
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"待修清单读取失败：{e}")
        return {"open": None, "done": None, "total": None, "state": {}, "title": {}}


# ---------------------------------------------------------------- 三线台账
# 「有什么 / 缺什么」的唯一事实源：00_治理/台账/三线台账.md
# 页面不再持有内容，只持有引用 —— 台账改字、清单勾选，下一次轮询（15 秒）就反映。
def band_seg_id(b):
    """带的台账段 id：与段标题一字对应（`## 带H 热更定位带` ⇒ `带H`）。

    ★ 为什么不直接用 mark（"H"）：段 id 就是台账里的段标题，一一对应、不做隐式换算。
      台账里看到 `## 带H …`，页面上的 `带H` 段就是它 —— 少一层映射就少一处漂移。
    """
    return "带%s" % b["mark"]


def all_bands():
    """上游带（渲染在三条线之前）+ 横切带（渲染在三条线之后），顺序与页面渲染一致。"""
    return BAND_UP + BANDS


def collect_ledger():
    """读台账 → {段id: {"has": [...], "miss": [...]}}。

    ★ 2026-09-28：带的「有什么 / 缺什么」也搬进台账（原先写死在 BAND_UP / BANDS 里），
      于是段的合法集合不再只有三条线的段位 —— 带的段必须一并登记，
      否则会被当成「未登记的段」而整段被忽略。
    """
    try:
        md = LEDGER_PATH.read_text(encoding="utf-8")
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"三线台账读取失败：{e}")
        return {}
    valid = {n["id"] for lane in LANES for n in lane["nodes"]}
    valid |= {band_seg_id(b) for b in all_bands()}
    out, seg, cur = {}, None, None
    unknown_seg = []
    for raw in md.splitlines():
        s = raw.strip()
        m = SEG_RE.match(s)
        if m:
            sid = m.group(1)
            if sid not in valid:
                # ★ 台账里写了段标题、但 LANES / 带都没登记它 ⇒ 以前的写法是【不当作新段】，
                #   于是它下面的条目会被静默并进上一段（实测 ①-3 的 5 条并进了 ①-2，
                #   页面上看不出问题、只是内容错位）。现在明确报出来。
                if sid not in unknown_seg:
                    unknown_seg.append(sid)
                continue
            seg, cur = sid, None
            out[seg] = {"has": [], "miss": [], "desc": "", "gates": [], "flow": [], "role": ""}
            continue
        if seg is None:
            continue
        if s.startswith("desc:"):
            # ★ 段的一句话描述：弹层里那句。唯一来源是台账，代码里不再写死。
            #   支持 {键} / #编号 / @判据，与 has:/miss: 条目同一套求值路径。
            out[seg]["desc"] = s[5:].strip()
            continue
        if s.startswith("role:"):
            # ★ 一级页那行小字。与 desc 分开写是因为【两处都要显示】且必须一致 ——
            #   写死在代码里就会和 desc 打架（实测踩过：role 还在说「三条线的入口」）。
            out[seg]["role"] = s[5:].strip()
            continue
        if s in ("has:", "miss:", "gates:", "flow:"):
            cur = s[:-1]
            continue
        if cur == "gates" and s.startswith("- "):
            # `序号 | 名字 | 描述`；只收三段齐全的，缺段就跳过（不猜）
            parts = [p.strip() for p in s[2:].split("|")]
            if len(parts) == 3:
                out[seg]["gates"].append({"no": parts[0], "name": parts[1], "desc": parts[2]})
            continue
        if cur == "flow" and s.startswith("- "):
            # ★ 带的流转步骤：顺序即显示顺序；代码里不再写死（写死必过时）
            out[seg]["flow"].append(s[2:].strip())
            continue
        if cur and s.startswith("- "):
            out[seg][cur].append(s[2:].strip())
    if unknown_seg:
        FAILS.append("台账里有未登记的段：%s（它们的内容会被并进上一段，请在 LANES / 带里登记）"
                     % "、".join(unknown_seg))
    # 带段落缺失 ⇒ 页面不能崩（回退到「未采集」），但要如实报出来：
    # 否则「唯一事实源」断了一截却没人知道，页面看着正常、内容其实是空的。
    for b in all_bands():
        if band_seg_id(b) not in out:
            FAILS.append("台账缺少「%s」段落（%s 的「有什么 / 缺什么」将显示为未采集）"
                         % (band_seg_id(b), b["name"]))
    return out


def _dig(data, key):
    cur = data
    for part in key.split("."):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(part)
        if cur is None:
            return None
    return cur


# 这些键的值是【字节数】→ 用 human()；其余整数是【计数】→ 千分位。
# ★ 实测踩过：一律套 human() 会把行数 2,300,843 渲染成「2 MB 行」。
_BYTE_KEYS = {"size_deliver", "size_source", "size_review", "size_clean"}

# 这些键的值是【整句摘要】→ 原样给出，不按长值截断。
# ★ 2026-09-28（带 H 用 {delta_line} 时实测）：delta_line = 「09-15→09-23 新增 19 · 变更 0 · 删除 0 包」
#   超过 24 字符 ⇒ 被截成「09-15→09-23 新增 19 · …」，把「变更/删除」两个数字吃掉了 ——
#   摘要被截断后只剩前半句，等于没给结论。整个键本就只服务台账的句级摘要。
_VERBATIM_KEYS = {"delta_line"}


def _fmtv(v, key=""):
    if v is None:
        return "读取失败"
    if isinstance(v, bool):
        return "是" if v else "否"
    if isinstance(v, (list, tuple)):
        return "、".join(str(x) for x in v) if v else "无"
    if isinstance(v, int):
        if key.split(".")[-1] in _BYTE_KEYS:
            return human(v)
        return f"{v:,}"
    s = str(v)
    # 路径要完整给出（截断了就没法照着去找）；整句摘要也给全（截了就没了结论）；
    # 其余长值（如 64 位指纹）截断
    _tail = key.split(".")[-1]
    if _tail in _VERBATIM_KEYS or _tail.endswith(("root", "dir", "path", "db")):
        return s
    return (s[:20] + "…") if len(s) > 24 else s


def _resolve_item(raw, data, state, title, side, checks=None):
    """把一条台账条目求值。返回 (文本, 是否丢弃)。

    side="has"  ：引用【成立/已闭环】才显示（没做到的不算「有」）
    side="miss" ：引用【不成立/未闭环】才显示（补上了就自动从这里消失）

    三种引用：
      #编号  待修清单条目（成立 = 已闭环）
      @判据  tools/checks.py 里的可核断言（成立 = 判据通过）
      其它   人工判断，原样显示
    """
    checks = checks or {}
    cm = REF_CHECK_RE.fullmatch(raw)
    if cm:  # 整条就是判据引用
        name = cm.group(1)
        info = checks.get(name)
        if not info:
            return (f"⚠ 台账引用了未注册的判据 @{name}", False)
        ok = bool(info.get("ok"))
        if (side == "has" and not ok) or (side == "miss" and ok):
            return ("", True)
        label = info.get("label") or name
        detail = info.get("detail") or ""
        txt = f"{label} —— {detail}" if detail else label
        if not info.get("live", True):
            txt += "（慢判据，读缓存）"
        return (txt, False)
    m = REF_CODE_RE.fullmatch(raw)
    if m:  # 整条就是引用
        code = m.group(1).upper()
        if code not in state:
            return (f"⚠ 台账引用了清单里不存在的编号 #{code}", False)
        closed = state[code]
        if (side == "has" and not closed) or (side == "miss" and closed):
            return ("", True)
        # 「有什么」侧的已闭环条目：清单标题写的是【当初的问题】，直接当成就读会绕。
        # 加前缀说明「已闭环」，原题留作凭据。
        if side == "has":
            return (f"已闭环 {code} · {title.get(code) or ''}".strip(" ·"), False)
        return (title.get(code) or f"#{code}", False)
    # 普通条目：把 {键} 求值；行内的 #编号 也替换成标题
    txt = raw
    for mm in list(REF_KEY_RE.finditer(raw)):
        txt = txt.replace(mm.group(0), _fmtv(_dig(data, mm.group(1)), mm.group(1)))
    for mm in list(REF_CODE_RE.finditer(raw)):
        code = mm.group(1).upper()
        txt = txt.replace(mm.group(0), (title.get(code) or f"#{code}"))
    return (txt, False)


def resolve_ledger(ledger, data, backlog, checks=None):
    """求值台账 → {段id: {has, miss, st}}。st 由缺项自动派生，不再手写。"""
    state = (backlog or {}).get("state") or {}
    title = (backlog or {}).get("title") or {}
    checks = checks or {}
    out = {}
    def _closed_line(code):
        return (f"已闭环 {code} · {title.get(code) or ''}".strip(" ·"))

    for seg, blk in ledger.items():
        has, miss, severity = [], [], 0
        has_codes = set()
        for raw in blk.get("has", []):
            mc = REF_CODE_RE.fullmatch(raw)
            if mc:
                has_codes.add(mc.group(1).upper())
            txt, drop = _resolve_item(raw, data, state, title, "has", checks)
            if not drop:
                has.append(txt)
        for raw in blk.get("miss", []):
            # @判据 成立时自动迁到「有什么」（与 #编号 闭环同理）
            mch = REF_CHECK_RE.fullmatch(raw)
            if mch and (checks.get(mch.group(1)) or {}).get("ok"):
                info = checks[mch.group(1)]
                t2, drop = _resolve_item(raw, data, state, title, "has", checks)
                if not drop and t2 not in has:
                    has.append(t2)
                continue
            mc = REF_CODE_RE.fullmatch(raw)
            if mc:
                code = mc.group(1).upper()
                # ★ 已闭环的编号 ⇒ 直接消失，【不迁移】。
                #   2026-09-26 修：原先闭环就迁进「有什么」，结果能力清单里混进
                #   「已闭环 A6 · 索引 sidecar 三份 json 的生成脚本找不到」这类条目 ——
                #   那是【历史修复】，不是【当前能力】，两者混在一起整段就读不懂了。
                #   「补上了什么」的痕迹去 `待修问题清单.md` 看，不该占主页。
                if state.get(code) is True:
                    continue
                lvl = title.get(code, "")
                severity = max(severity, 2 if "★★★" in lvl else 1)
            txt, drop = _resolve_item(raw, data, state, title, "miss", checks)
            if not drop:
                miss.append(txt)
        # 派生优先级：有 ★★★ 未闭环引用 → miss；只要还有缺项 → warn；一条缺项都没有 → ok。
        # ★ 实测踩过：只看「有没有 # 引用」会让 ①-1 / ③-2 这种纯人工判断的缺项被误报 ok。
        if severity >= 2:
            st = "miss"
        elif miss:
            st = "warn"
        else:
            st = "ok"
        # ★ 段描述：与 has 条目同一套求值（{键} / #编号 / @判据 都支持）。
        #   求不出来（或台账没写 desc）就留空 —— 页面会显示「未采集」，不拿旧文本充数。
        desc_raw = (blk.get("desc") or "").strip()
        desc_txt = ""
        if desc_raw:
            t, _drop = _resolve_item(desc_raw, data, state, title, "has", checks)
            desc_txt = t
        # ★ 闸门描述：同样从台账来，逐条求值（#编号 / @判据 会跟着状态变）
        gates_txt = []
        for g in blk.get("gates") or []:
            dtxt, _dp = _resolve_item(g.get("desc") or "", data, state, title, "has", checks)
            gates_txt.append({"no": g.get("no", ""), "name": g.get("name", ""), "desc": dtxt})
        out[seg] = {"has": has, "miss": miss, "st": st, "desc": desc_txt,
                    "gates": gates_txt, "flow": list(blk.get("flow") or []),
                    "role": blk.get("role") or ""}
    return out


def ledger_ref_warnings(ledger=None, backlog=None, checks=None):
    """校验台账里的 #编号 是否都真实存在于待修清单。

    ★ 与旧版 lane_ref_warnings 的区别：
      旧版是「手写散文引用了清单编号，两边各写各的 ⇒ 会漂移」——只能事后报警。
      现在引用由 resolve_ledger() 现场求值：清单勾选一变，页面自动跟着变（不再漂移）。
      所以这里只剩一件事要查：【编号拼错了】。拼错会让引用永远求不到值。
    """
    st = (backlog or {}).get("state") or {}
    out = []
    for seg, blk in (ledger or {}).items():
        for side in ("has", "miss"):
            for item in blk.get(side, []):
                for m in REF_CODE_RE.finditer(item):
                    c = m.group(1).upper()
                    if c not in st:
                        out.append(f"{seg} 的「{side}」引用了清单里不存在的编号 #{c}")
                for m in REF_CHECK_RE.finditer(item):
                    if m.group(1) not in (checks or {}):
                        out.append(f"{seg} 的「{side}」引用了未注册的判据 @{m.group(1)}")
    return out


def collect_pages():
    try:
        files = sorted(p.name for p in WEB.glob("*.html")
                       if not p.name.startswith("_") and not p.name.startswith(".")
                       and not p.name.startswith("board.html."))
        return files
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"页面清单读取失败：{e}")
        return []


def collect_skin_assets():
    try:
        base = WEB / "assets" / "3d" / "weapon_skin"
        return sum(1 for p in base.iterdir() if p.is_dir())
    except Exception as e:  # noqa: BLE001
        FAILS.append(f"皮肤资产目录统计失败：{e}")
        return None


def count_files(path: Path, budget=60.0):
    """递归文件数；超预算返回 None（不阻塞生成）。

    与 dir_size 同源危害，共用 BULK_DIRS 守卫：大件目录不递归（起点命中 ⇒ None）。
    """
    t0 = time.time()
    n = 0
    stack = [path]
    if is_bulk(path):                     # 守卫①：起点就在大件目录里 ⇒ 不扫
        return None
    try:
        while stack:
            if time.time() - t0 > budget:
                return None
            cur = stack.pop()
            with os.scandir(cur) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            if is_bulk(e.path):        # 守卫②：递归时就地剪枝
                                continue
                            stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            n += 1
                    except OSError:
                        continue
    except OSError as e:
        FAILS.append(f"文件数统计失败 {path.name}：{e}")
        return None
    return n


def dir_size(path: Path, budget=90.0):
    """目录体积（字节）；超预算或不存在返回 None（不阻塞生成）。

    ★ 大件守卫：命中 BULK_DIRS 的目录**一律不递归**（起点命中 ⇒ 直接返回 None）。
      百万文件级的目录被无差别遍历会把生成拖死 —— 见 00_治理/规范/目录规范.md。
    """
    t0 = time.time()
    total = 0
    stack = [path]
    if not path.exists():
        FAILS.append(f"体积统计失败 {path}：目录不存在")
        return None
    if is_bulk(path):                     # 守卫①：起点就在大件目录里 ⇒ 不扫
        return None
    try:
        while stack:
            if time.time() - t0 > budget:
                return None
            cur = stack.pop()
            with os.scandir(cur) as it:
                for e in it:
                    try:
                        if e.is_dir(follow_symlinks=False):
                            if is_bulk(e.path):        # 守卫②：递归时就地剪枝
                                continue
                            stack.append(e.path)
                        elif e.is_file(follow_symlinks=False):
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
    except OSError as e:
        FAILS.append(f"体积统计失败 {path.name}：{e}")
        return None
    return total


def human(n):
    if n is None:
        return "读取失败"
    if n >= 1 << 30:
        return f"{n / (1 << 30):.1f} GB"
    if n >= 1 << 20:
        return f"{n / (1 << 20):.0f} MB"
    return f"{n} B"


def collect_names():
    """①-4 名字字典规模与覆盖率 —— **只读 sidecar**。

    为什么不现算：覆盖率要把 105 万条字典与 230 万行索引对一遍，实测 2~4 秒；
    主页是 15 秒轮询，扛不住。sidecar 由
    `python 04_站点/web/tools/refresh_sidecars.py` 生成（也可由 names stats 同步）。
    读不到就如实返回空，页面显示「未采集」，不编数字。
    """
    try:
        if NAMES_SIDECAR.is_file():
            d = json.loads(NAMES_SIDECAR.read_text(encoding="utf-8"))
            d["_from"] = "同步产物 %s" % NAMES_SIDECAR.name
            return d
    except Exception as e:  # noqa: BLE001
        FAILS.append("名字 sidecar 快读失败：%s: %s" % (type(e).__name__, e))
    return {}


def collect_delta():
    """①-5 热更增量摘要 —— **只读 sidecar**（由 `run_all.py delta diff --out` 落盘）。"""
    try:
        if DELTA_SIDECAR.is_file():
            d = json.loads(DELTA_SIDECAR.read_text(encoding="utf-8"))
            return d
    except Exception as e:  # noqa: BLE001
        FAILS.append("增量 sidecar 快读失败：%s: %s" % (type(e).__name__, e))
    return {}


def collect_names_summary():
    """给台账 `{names_count}` / `{names_coverage}` 用的两个短串。

    读不到就返回「未采集」—— 不编数字，也不显示未展开的占位符。
    ★ 2026-09-28 加 `{unnamed_rows}` / `{unnamed_pct}`：
      台账里「未命名仍是多数（约 127 万行）」这类数字写死会漂移
      （实测 1,265,527 ≈ 126.6 万，写「127 万」是四舍五入的旧值）。
    """
    n = collect_names()
    if not n:
        return {"names_count": "未采集", "names_coverage": "未采集",
                "unnamed_rows": "未采集", "unnamed_pct": "未采集"}
    cnt = n.get("dict_size")
    cov = n.get("coverage_pct")
    tot = n.get("total_rows")
    covered = n.get("covered_rows")
    un = None
    if isinstance(tot, int) and isinstance(covered, int):
        un = tot - covered
    return {
        "names_count": ("{:,}".format(cnt) if isinstance(cnt, int) else "未采集"),
        "names_coverage": ("%.2f%%" % cov if isinstance(cov, (int, float)) else "未采集"),
        "unnamed_rows": ("{:,}".format(un) if isinstance(un, int) else "未采集"),
        "unnamed_pct": ("%.1f%%" % ((un / tot * 100) if isinstance(un, int) and tot else 0)
                        if isinstance(un, int) and isinstance(tot, int) and tot else "未采集"),
    }


def collect_delta_summary():
    """给台账 `{delta_line}` 用的一句话摘要。

    ★ 刻意短：卡面里被 CSS 截断，写长了后面看不见（实测踩过）。
    版本串只取日期（20260915_220933_release_newpc → 09-15）。
    """
    d = collect_delta()
    t = (d or {}).get("totals") or {}
    if not t:
        return {"delta_line": "未采集（跑 `run_all.py delta diff` 后刷新）"}

    def short(x):
        v = str((x or {}).get("version") or "")
        return "%s-%s" % (v[4:6], v[6:8]) if len(v) >= 8 else v[:6]

    a = d.get("a") or {}
    b = d.get("b") or {}
    return {"delta_line": "%s→%s 新增 %d · 变更 %d · 删除 %d 包" % (
        short(a), short(b), t.get("added", 0), t.get("changed", 0), t.get("removed", 0))}


def collect():
    FAILS.clear()  # 每次采集从零开始：失败项只反映本次（8765 的 /api/home/snapshot 会反复调用本函数）
    idx = collect_index()
    rows = idx.get("rows")
    quick = idx.get("quick_check")
    stale = idx.get("stale")
    built = idx.get("built_at")
    inv = idx.get("current_inventory_file_count")
    totals = idx.get("row_totals") or {}
    data = {
        "rows": rows,
        "quick": quick,
        "stale": stale,
        "built_at": built,
        "inventory_files": inv,
        "row_gpk": totals.get("gpk"),
        "row_fpk": totals.get("fpk"),
        "row_npk": totals.get("npk"),
        "failed_containers": idx.get("failed_containers"),
        "db": idx.get("database"),
        "schema_version": idx.get("schema_version"),
        "fingerprint": idx.get("stored_inventory_fingerprint"),
        "index_from": INDEX_FROM,
        "tools": collect_tool_count(),
        "entries": collect_entries(),
        "backlog": collect_backlog(),
        "pages": collect_pages(),
        "skin_assets": collect_skin_assets(),
        # ★ ①-4 / ①-5：只读 sidecar，读不到就如实说「未采集」
        **collect_names_summary(),
        **collect_delta_summary(),
        # 各区体积（全部现读）
        "size_deliver": dir_size(PROJECT / "02_资料" / "交付"),
        "size_source": dir_size(PROJECT / "02_资料" / "源包"),
        "files_source": count_files(PROJECT / "02_资料" / "源包"),
        "size_review": dir_size(PROJECT / "03_执行" / "96_审阅区"),
        "size_clean": dir_size(PROJECT / "03_执行" / "95_待清理"),
        "skin_root": str(WEB / "assets" / "3d" / "weapon_skin"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "generated_at_full": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fails": FAILS,
    }
    # 三线台账：内容随每次采集求值 ⇒ 台账改字 / 清单勾选，下一次轮询就反映
    data["ledger"] = collect_ledger()
    data["checks"] = collect_checks(data)
    data["lanes"] = resolve_ledger(data["ledger"], data, data["backlog"], data["checks"])
    # 带（H/D/Q）的内容与三条线走同一条路：台账 → resolved → 渲染。
    # ★ 带的段状态仍是代码里的静态口径（搬走的只有「有什么 / 缺什么」），
    #   这里把它写回 lanes —— 15 秒轮询的 applyLanes 读的就是 d.lanes，
    #   不写回的话页面刷一次、带的颜色就会从「代码口径」跳成「派生口径」。
    for _b in all_bands():
        _k = band_seg_id(_b)
        if isinstance(data["lanes"].get(_k), dict):
            data["lanes"][_k]["st"] = _b["st"]
    data["bands"] = merge_bands(data["lanes"])
    data["ref_warnings"] = ledger_ref_warnings(data["ledger"], data["backlog"], data["checks"])
    return data


# ---------------------------------------------------------------- 页面内容
def status_chip(st):
    return {"ok": ("✅", "健康", "ok"), "warn": ("⚠️", "半吊子", "warn"),
            "miss": ("✗", "缺", "miss")}[st]


def merge_lanes(resolved=None):
    """把静态元数据（LANES）与台账解析结果合并成渲染用的结构。

    ★ 内容全部来自 resolved（= 00_治理/台账/三线台账.md 现场求值）：
      页面/模块里【不再有任何 has/miss 文字】，改字只需改台账。
    """
    resolved = resolved or {}
    out = []
    for lane in LANES:
        nodes = []
        for n in lane["nodes"]:
            r = dict(n)
            r.update(resolved.get(n["id"]) or {})
            r.setdefault("has", [])
            r.setdefault("miss", [])
            r.setdefault("st", "ok")
            nodes.append(r)
        out.append({"mark": lane["mark"], "name": lane["name"],
                    "sub": lane["sub"], "nodes": nodes})
    return out


def merge_bands(resolved=None):
    """把静态元数据（BAND_UP / BANDS）与台账解析结果合并成渲染用的结构。

    ★ 与 merge_lanes 同一条规矩：带的「有什么 / 缺什么」全部来自
      resolved（= 00_治理/台账/三线台账.md 现场求值）；代码只留定位元数据
      （mark / name / st / role / line / flow / gates）。
    ★ 带的段状态 st 仍由代码给 —— 它不是「有什么 / 缺什么」，且闸门各自带状态，
      不参与台账的自动派生（否则 Q 带的颜色会被闸门状态和缺项两套口径来回拽）。
    ★ 台账里没有这个带的段落 ⇒ 页面不崩、也不编内容：如实显示「未采集」。
      （collect_ledger() 会同时把这件事记进 FAILS，不静默。）
    """
    resolved = resolved or {}
    out = []
    for b in all_bands():
        r = dict(b)
        blk = resolved.get(band_seg_id(b)) or {}
        if blk:
            r["has"] = list(blk.get("has") or [])
            r["miss"] = list(blk.get("miss") or [])
            r["desc"] = blk.get("desc") or ""            # ★ 描述也来自台账
            r["flow"] = list(blk.get("flow") or [])      # ★ 流转也来自台账
            if blk.get("role"):
                r["role"] = blk["role"]                  # ★ 一级页那行小字也来自台账
            r["from_ledger"] = True
            # ★ 闸门的【描述】从台账来；【序号/名字/状态】仍用代码里的结构（见 BANDS 注释）
            g_from = blk.get("gates") or []
            if r.get("gates") and g_from:
                merged = []
                for i, g in enumerate(r["gates"]):
                    g2 = dict(g)
                    if i < len(g_from):
                        g2["desc"] = g_from[i].get("desc") or ""
                    merged.append(g2)
                r["gates"] = merged
        else:
            r["has"] = ["未采集：台账 00_治理/台账/三线台账.md 里没有「%s」段落"
                        % band_seg_id(b)]
            r["miss"] = []
            r["desc"] = ""
            r["from_ledger"] = False
        out.append(r)
    return out


def split_bands(bands_full):
    """按【上游带 / 横切带】切开（渲染位置不同：H 在三条线之前，D/Q 在之后）。"""
    n_up = len(BAND_UP)
    return list(bands_full)[:n_up], list(bands_full)[n_up:]


def health_report(d):
    """项目健康状态：索引校验 / 数据新鲜 / 失败容器 / 待修条数，取最差一项。"""
    bl = d["backlog"]
    checks = []
    idx_ok = d["quick"] == "ok"
    checks.append(("索引校验", "通过" if idx_ok else "未通过", "ok" if idx_ok else "miss"))
    if d["stale"] is False:
        checks.append(("数据新鲜", "无过期", "ok"))
    elif d["stale"] is True:
        checks.append(("数据新鲜", "存在过期项", "warn"))
    else:
        checks.append(("数据新鲜", "读取失败", "miss"))
    fc = d["failed_containers"]
    if fc is None:
        checks.append(("失败容器", "读取失败", "miss"))
    else:
        checks.append(("失败容器", f"{fc} 个", "ok" if fc == 0 else "warn"))
    op = bl["open"]
    if op is None:
        checks.append(("待修问题", "读取失败", "miss"))
    else:
        checks.append(("待修问题", f"{op} 条未闭环", "ok" if op == 0 else "warn"))
    # 台账引用校验：现在引用是现场求值的（不会再漂移），只剩「编号拼错」要抓
    refw = d.get("ref_warnings") or []
    checks.append(("台账引用", "全部有效" if not refw else f"{len(refw)} 处无效",
                   "ok" if not refw else "warn"))

    order = {"ok": 0, "warn": 1, "miss": 2}
    worst = max((c[2] for c in checks), key=lambda k: order[k])
    return worst, {"ok": "良好", "warn": "注意", "miss": "异常"}[worst], checks


LANES = [
    {
        "mark": '①', "name": '解码定位复原线',
        "sub": '从物理包到场内事实 —— 文件在哪、这一行是什么',
        "nodes": [
            # ★ 2026-09-28 结构调整（用户口径）：原 ①-1 定位复原 / ①-2 解析复原 / ①-4 名字还原
            #   合成一段「定位与复原」；批量质检移到链的最后；热更增量升为「带 H」。
            # ★ 2026-09-28 二次（用户口径）：卡片上那句描述【不再写在代码里】——
            #   唯一来源是 00_治理/台账/三线台账.md 每段的 `desc:`（现场求值，支持 {键}/#编号/@判据）。
            #   代码这里只留定位元数据（id / name），description 一律从台账来。
            {"id": '①-0', "name": '索引地基'},
            {"id": '①-1', "name": '定位与复原'},
            {"id": '①-2', "name": '批量质检'},
        ],
    },
    {
        "mark": '②', "name": '图文音频渲染线',
        "sub": '把资源找出来、变成能看能听的东西（贴图与音频是现成成品，做的是定位不是复原）',
        "nodes": [
            # ★ 2026-09-28 重构（用户口径）：贴图/音频本来就是【成品】，不是「复原」出来的
            #   ⇒ 删掉「复原」这个说法，两段合并为「媒体定位」；
            #   出图校色改叫「三维出图校准」—— 只有三维渲染图需要单独校准。
            {"id": '②-1', "name": '三维装配'},
            {"id": '②-2', "name": '媒体定位'},
            {"id": '②-3', "name": '三维出图校准'},
        ],
    },
    {
        "mark": '③', "name": '前端展示交互线',
        "sub": '数据怎么变页面、页面怎么发给别人看',
        "nodes": [
            {"id": '③-1', "name": '页面与看板'},
            {"id": '③-2', "name": '服务与契约'},
            {"id": '③-3', "name": '资产落地与投影'},
        ],
    },
]

# ★ 2026-09-28：带分两类，渲染位置不同。
#   BAND_UP = 【上游带】：它是三条线的入口（先知道「哪里变了」才知道去哪找），
#             所以渲染在三条线【之前】。
#   BANDS   = 【横切带】：接口与闸门，渲染在三条线【之后】。
# ★ 描述（desc）/ 流转（flow）/「有什么 / 缺什么」全部在台账：
#   `## 带H …` / `## 带D …` / `## 带Q …` 段的 desc: / flow: / has: / miss:
#   代码这里【只留定位元数据】—— 写死的描述与流转必过时（实测踩过两次）。
BAND_UP = [
    {
        "mark": "H", "name": "热更定位带", "st": "warn",
    },
]

BANDS = [
    {
        "mark": "D", "name": "数据契约带", "st": "warn",
    },
    {
        "mark": "Q", "name": "质量·交付·治理带", "st": "warn",
        "gates": [
            {"no": "闸门一", "name": "发布门禁", "st": "warn"},
            {"no": "闸门二", "name": "数据契约校验", "st": "warn"},
            {"no": "闸门三", "name": "交付打包", "st": "miss"},
        ],
    },
]

# 子界面入口（门户）—— 顶栏横排；手机上收进抽屉
PORTALS = [
    ("图鉴首页", "wiki.html", "ok"),
    ("斩神系列专题", "zhanshen.html", "ok"),
    ("板块浏览", "board.html", "ok"),
    ("外观三维预览", "skin3d.html", "ok"),
    ("武器模型", "weapon_models.html", "ok"),
    ("工作台状态", "workbench_status.html", "warn"),
    ("本轮进展", "进展.html", "ok"),
]


def _short_ver(ver):
    """把 20260923_164313_playertest_newpc 压成 09-23 16:43 · playertest。"""
    s = str(ver or "")
    m = re.match(r"^(\d{4})(\d{2})(\d{2})_(\d{2})(\d{2})(\d{2})_?(.*)$", s)
    if not m:
        return s[:22]
    y, mo, d, hh, mm, _ss, tail = m.groups()
    tail = (tail or "").replace("_newpc", "").replace("playertest", "test")
    return f"{mo}-{d} {hh}:{mm}" + (f" {tail[:12]}" if tail else "")


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            .replace('"', "&quot;"))


def num(v):
    return "读取失败" if v is None else f"{v:,}"


def dline(x):
    """段（节点/带）的一句话描述。

    ★ 唯一来源是台账的 `desc:`（见 00_治理/台账/三线台账.md）。
      这里【故意不设 fallback 死文本】—— 台账没写就如实显示「未采集」，
      不拿代码里的旧句子充数。用户口径：不要固定的死文本。
    """
    d = (x.get("desc") or "").strip()
    return d if d else "未采集（台账未写 desc:）"


def render_chip(n, key):
    ic, label, klass = status_chip(n["st"])
    return (f'<button type="button" class="chip {klass}" data-pop="{esc(key)}"'
            f' data-id="{esc(n["id"])}" data-name="{esc(n["name"])}"'
            f' data-st="{ic} {esc(label)}" data-klass="{klass}"'
            f' aria-haspopup="dialog" title="点开看：现在有什么 / 缺什么">'
            f'<span class="crow"><span class="cid">{esc(n["id"])}</span>'
            f'<span class="cst">{ic} {esc(label)}</span></span>'
            f'<span class="cname">{esc(n["name"])}</span>'
            f'<span class="cline">{esc(dline(n))}</span>'
            f'<span class="cfoot">缺 {len(n["miss"])} 条</span>'
            f'</button>')


def render_lane(lane):
    cnt = {"ok": 0, "warn": 0, "miss": 0}
    for n in lane["nodes"]:
        cnt[n["st"]] += 1
    chips = []
    for i, n in enumerate(lane["nodes"]):
        if i:
            chips.append('<span class="arw" aria-hidden="true"></span>')
        chips.append(render_chip(n, f"{lane['mark']}-{i}"))
    stats = (f'<span class="s ok">✅ {cnt["ok"]}</span>'
             f'<span class="s warn">⚠️ {cnt["warn"]}</span>'
             f'<span class="s miss">✗ {cnt["miss"]}</span>')
    return f"""
  <section class="lane" id="line-{lane['mark']}">
    <div class="llabel">
      <span class="row1"><span class="mk">{lane['mark']}</span><span class="nm">{esc(lane['name'])}</span></span>
      <span class="lsub">{esc(lane['sub'])}</span>
    </div>
    <div class="chain">{''.join(chips)}<span class="rail" aria-hidden="true"></span></div>
    <span class="lstat">{stats}</span>
  </section>"""


def render_band(b, key, i):
    ic, label, klass = status_chip(b["st"])
    if b.get("gates"):
        inner = "".join(
            f'<span class="gate {status_chip(g["st"])[2]}"><b>{esc(g["no"])}</b>'
            f'<span class="gname">{esc(g["name"])}</span>'
            f'<span class="gs">{status_chip(g["st"])[0]} {esc(status_chip(g["st"])[1])}</span></span>'
            for g in b["gates"])
    else:
        flow = list(b.get("flow") or [])
        inner = "".join(
            f'<span class="floww">{esc(x)}</span>'
            + ('<span class="arw sm" aria-hidden="true"></span>' if j < len(flow) - 1 else "")
            for j, x in enumerate(flow))
    return f"""
  <button type="button" class="row-band {klass}" id="band-{b['mark']}" data-pop="{esc(key)}"
          data-id="{b['mark']}" data-name="{esc(b['name'])}" data-st="{ic} {esc(label)}"
          data-klass="{klass}" aria-haspopup="dialog" title="点开看：现在有什么 / 缺什么">
    <span class="blabel">
      <span class="row1"><span class="mk v">{b['mark']}</span><span class="nm">{esc(b['name'])}</span></span>
      <span class="role">{esc(b['role'])}</span>
    </span>
    <span class="bgates">{inner}<span class="rail" aria-hidden="true"></span></span>
    <span class="bst">{ic} {esc(label)}</span>
    <span class="bhint">缺 {len(b['miss'])} 条</span>
  </button>"""


def render_portals(css="plink"):
    out = []
    for name, href, st in PORTALS:
        ic, label, klass = status_chip(st)
        out.append(f'<a class="{css}" href="{esc(href)}" title="{esc(name)} · {ic} {esc(label)}">'
                   f'<span class="dot {klass}"></span>{esc(name)}</a>')
    return "\n".join(out)


def render_left(d, hworst, checks):
    """左信息块：大块标题 + 实时指标 + 各区体积 + 项目健康状态。"""
    bl = d["backlog"]
    src_n = d["files_source"]
    src_txt = (f"{human(d['size_source'])} · {src_n} 文件" if src_n is not None
               else human(d["size_source"]))

    def kv(label, value, cls="", key=None):
        k = f' data-k="{esc(key)}"' if key else ""
        return (f'<div class="kv"><span>{esc(label)}</span>'
                f'<b class="{cls}"{k}>{esc(value)}</b></div>')

    # ★ 服务器版本与服务器时间（数据来自 03_执行/30_分析/服务器状态_20260928/servers.json
    #   经脚本写入 04_站点/web/data/servers.json，由 netease 版本清单 + HTTP Date 头得到）
    servers_rows = ""
    servers_meta = ""
    try:
        _sv = json.loads((WEB / "data" / "servers.json").read_text(encoding="utf-8"))
        for s in _sv.get("servers", []):
            ver = s.get("version") or "读取失败"
            stime = s.get("server_time") or ""
            servers_rows += (
                f'<div class="kv svrow"><span>{esc(s.get("label") or s.get("key"))}</span>'
                f'<b title="{esc(ver)}">{esc(_short_ver(ver))}</b>'
                f'<i class="svtime" data-sv="{esc(s.get("key"))}">{esc(stime[11:19] if len(stime) >= 19 else stime)}</i></div>')
        servers_meta = _sv.get("updated_at") or ""
    except Exception:
        servers_rows = '<div class="kv"><span>服务器清单</span><b class="g">读取失败</b></div>'

    metrics = "".join([
        kv("索引行数", num(d["rows"]), key="rows"),
        kv("工具", num(d["tools"]), key="tools"),
        kv("统一入口", str(len(d["entries"])) if d["entries"] else "读取失败", key="entries"),
        kv("待修", str(bl["open"]) if bl["open"] is not None else "读取失败", "g", key="backlog_open"),
        kv("已修", str(bl["done"]) if bl["done"] is not None else "读取失败", key="backlog_done"),
        kv("站点页面", str(len(d["pages"])) if d["pages"] else "读取失败", key="pages"),
        kv("皮肤资产", num(d["skin_assets"]), key="skin_assets"),
    ])
    sizes = "".join([
        kv("交付", human(d["size_deliver"]), key="size_deliver"),
        kv("源包", src_txt, key="size_source"),
        kv("审阅区", human(d["size_review"]), key="size_review"),
        kv("垃圾（待清理）", human(d["size_clean"]), "g", key="size_clean"),
    ])
    ck = "".join(
        f'<span class="hck {k}"><span class="dot {k}"></span>{esc(n)} {esc(v)}</span>'
        for n, v, k in checks)
    lamp = {"ok": "良好", "warn": "注意", "miss": "异常"}[hworst]
    return f"""
  <aside id="left" aria-label="项目信息">
    <div class="ltop">
      <div class="leyebrow">LIFEAFTER · 拆包工程</div>
      <h1 class="bigtitle">LifeAfter<br>拆包项目</h1>
      <div class="lsub">三线三带 · 拆包状态总览</div>
    </div>
    <div class="lsec">
      <h4>实时指标</h4>
      {metrics}
    </div>
    <div class="lsec">
      <h4>各区体积</h4>
      {sizes}
    </div>
    <div class="lsec">
      <h4>服务器版本 <span class="svhint" title="版本号来自网易版本清单；时刻为服务器 HTTP 时间">{servers_meta}</span></h4>
      {servers_rows}
    </div>
    <div class="health {hworst}" id="health">
      <span class="lamp" aria-hidden="true"></span>
      <div class="hbody">
        <b id="healthLabel">项目健康：{lamp}</b>
        <div class="hcks" id="healthCks">{ck}</div>
      </div>
    </div>
  </aside>"""


# ---- 弹层内容（不进主布局，点段才注入）
def _miss_li(item, state):
    """渲染一条「缺什么」。若它引用的编号已闭环，加标注（不删条目 —— 删了就看不出漂移）。"""
    refs = []
    for m in REF_RE.finditer(item):
        for c in re.split(r"\s*/\s*", m.group(1)):
            c = c.strip().upper()
            if c:
                refs.append(c)
    closed = [c for c in refs if state.get(c) is True]
    gone = [c for c in refs if c not in state]
    if not closed and not gone:
        return f"<li>{esc(item)}</li>"
    note = []
    if closed:
        note.append("引用的待修 " + "、".join(closed) + " 已闭环，此条待复核")
    if gone:
        note.append("引用的待修 " + "、".join(gone) + " 在清单里找不到")
    return (f'<li class="refstale">{esc(item)}'
            f'<span class="refnote">⚠ {"；".join(note)}</span></li>')


def tpl_node(n, key, state=None):
    state = state or {}
    has = "".join(f"<li>{esc(x)}</li>" for x in n["has"])
    miss = "".join(_miss_li(x, state) for x in n["miss"])
    return (f'<template id="p{esc(key)}"><p class="popline">{esc(dline(n))}</p>'
            f'<div class="cols">'
            f'<div class="col"><h4><span class="dot ok"></span>现在有什么</h4><ul class="yes">{has}</ul></div>'
            f'<div class="col"><h4><span class="dot miss"></span>缺什么</h4><ul class="no">{miss}</ul></div>'
            f'</div></template>')


def tpl_band(b, key):
    has = "".join(f"<li>{esc(x)}</li>" for x in b["has"])
    miss = "".join(f"<li>{esc(x)}</li>" for x in b["miss"])
    gates = ""
    if b.get("gates"):
        gates = '<div class="gates">' + "".join(
            f'<div class="gate {status_chip(g["st"])[2]}"><div class="gno">{esc(g["no"])} · '
            f'{status_chip(g["st"])[0]} {esc(status_chip(g["st"])[1])}</div>'
            f'<div class="gname">{esc(g["name"])}</div>'
            f'<div class="gline">{esc(g.get("desc") or "")}</div></div>' for g in b["gates"]) + "</div>"
    return (f'<template id="p{esc(key)}"><p class="popline">{esc(dline(b))}</p>{gates}'
            f'<div class="cols">'
            f'<div class="col"><h4><span class="dot ok"></span>现在有什么</h4><ul class="yes">{has}</ul></div>'
            f'<div class="col"><h4><span class="dot miss"></span>缺什么</h4><ul class="no">{miss}</ul></div>'
            f'</div></template>')


def build(d, collect_seconds=None):
    hworst, htxt, checks = health_report(d)
    bl = d["backlog"]
    lanes_full = merge_lanes(d.get("lanes"))
    # 带（H/D/Q）的内容同样来自台账：d["bands"] = collect() 里 merge_bands() 的结果。
    # d 里没有这个键（例如别处以最小字典构造 d）⇒ 就地从 lanes 合并一次，保持可用。
    bands_full = d.get("bands") or merge_bands(d.get("lanes"))
    bands_up, bands_x = split_bands(bands_full)
    pages_n = len(d["pages"])
    entries_txt = " / ".join(d["entries"]) if d["entries"] else "读取失败"
    # 顶部时间戳：说清楚「这份数据是什么时候采的、采了多久」
    gen_full = d.get("generated_at_full") or d["generated_at"]
    sec_txt = f"用时 {collect_seconds:.1f} 秒" if isinstance(collect_seconds, (int, float)) else "用时未记录"
    stamp = f"数据采集于 {gen_full[11:]}（{sec_txt}）· 每 15 秒自动刷新"

    # 段的弹层（键 = 线标-序号 / 带的台账段 id）
    # ★ 带的键用【台账段 id】（`带H`）而不是 mark（`H`）：applyLanes() 拿到 d.lanes 后
    #   直接去找 `#p<键>`，键取段 id 才能让 H/D/Q 的「有什么 / 缺什么」跟着 15 秒轮询刷新。
    tpls = []
    for lane in lanes_full:
        for i, n in enumerate(lane["nodes"]):
            tpls.append(tpl_node(n, f"{lane['mark']}-{i}", bl.get("state")))
    for b in bands_full:
        tpls.append(tpl_band(b, band_seg_id(b)))
    if d["fails"]:
        fl = "".join(f"<li>{esc(x)}</li>" for x in d["fails"])
        tpls.append(f'<template id="pFAIL"><p class="popline">以下项目本次采集失败，页面按「读取失败」如实标注，未编造数值。</p>'
                    f'<div class="cols one"><div class="col"><h4><span class="dot miss"></span>失败项</h4>'
                    f'<ul class="no">{fl}</ul></div></div></template>')

    # 「技术详情」= 从右侧滑出的悬浮抽屉。
    # 根因（CDP 实测）：面板原先放在 .topR 里，而祖先 #top 带 backdrop-filter:blur(10px)，
    # 会让 position:fixed 后代的「包含块」变成 #top（与 transform / filter / will-change 同效），
    # 于是 .tbody{position:fixed;right:12px;bottom:12px} 相对 48px 高的顶栏定位，
    # 实测被顶到视口上方 523px（y=-523），用户只看到顶栏那一条缝。
    # 修法：触发器留在顶栏（static 定位，不受影响），面板本身提到 body 级 #techDrawer，
    # 祖先链上没有 transform / filter / backdrop-filter，fixed 定位回到视口。
    tech_btn = ('<button type="button" class="tech-btn" id="techBtn" aria-haspopup="dialog"'
                ' aria-controls="techDrawer" aria-expanded="false">技术详情</button>')

    tech_panel = f"""<div id="techDrawer" aria-hidden="true">
  <div class="tech-mask" id="techMask"></div>
  <aside class="tech-panel" id="techPanel" role="dialog" aria-modal="true" aria-label="技术详情">
    <div class="tech-top">
      <span class="tech-title">技术详情</span>
      <span class="tech-hint">Esc / 点面板外 / 点「✕ 关闭」都能收起</span>
      <button type="button" class="tech-x" id="techX" aria-label="关闭技术详情">✕ 关闭</button>
    </div>
    <div class="tech-body" id="techBody">
      <pre>索引库路径      : <span data-k="t_db">{esc(d['db'] or '读取失败')}</span>
索引状态来源    : <span data-k="t_index_from">{esc(d['index_from'] or '读取失败')}</span>
索引行数        : <span data-k="rows">{esc(num(d['rows']))}</span>
库完整性校验    : <span data-k="t_quick">{esc('通过' if d['quick'] == 'ok' else '未通过')}</span>
数据是否过期    : <span data-k="t_stale">{esc('否' if d['stale'] is False else ('是' if d['stale'] is True else '读取失败'))}</span>
建库时间        : <span data-k="t_built">{esc(d['built_at'] or '读取失败')}</span>
容器登记数      : <span data-k="t_inv">{esc(str(d['inventory_files']))}</span>
分段行数        : <span data-k="t_split">图形包 {esc(num(d['row_gpk']))} / 资源包 {esc(num(d['row_fpk']))} / 数据包 {esc(num(d['row_npk']))}</span>
失败容器        : <span data-k="t_fc">{esc(str(d['failed_containers']))}</span>
登记结构版本    : <span data-k="t_schema">{esc(str(d['schema_version']))}</span>
库存指纹        : <span data-k="t_fingerprint">{esc((d['fingerprint'] or '')[:32])}…</span>
工具数          : <span data-k="tools">{esc(num(d['tools']))}</span>（01_工具/工具库/*.py）
统一入口子命令  : <span data-k="t_entries">{esc(entries_txt)}</span>
待修清单        : <span data-k="t_backlog">未修 {esc(str(bl['open']))} / 已修 {esc(str(bl['done']))}</span>
站点页面(去实验页): <span data-k="pages">{pages_n}</span>
皮肤资产目录    : <span data-k="skin_assets">{esc(num(d['skin_assets']))}</span> 套 · <span data-k="t_skin_root">{esc(d['skin_root'])}</span>
交付区体积      : <span data-k="size_deliver">{esc(human(d['size_deliver']))}</span>（02_资料/交付）
源包区体积      : <span data-k="size_source">{esc(human(d['size_source']))} · {esc(str(d['files_source']))} 文件</span>（02_资料/源包）
审阅区体积      : <span data-k="size_review">{esc(human(d['size_review']))}</span>（03_执行/96_审阅区）
待清理区体积    : <span data-k="size_clean">{esc(human(d['size_clean']))}</span>（03_执行/95_待清理，即垃圾）
项目健康        : <span data-k="t_health">{esc(htxt)}（{'；'.join(f'{n}{v}' for n, v, _ in checks)}）</span>
生成时间        : <span data-k="t_gen">{esc(d['generated_at'])}</span>
数据来源        : 统一入口 index status ｜ 01_工具/工具库/*.py 计数 ｜ 统一入口 --help 子命令
                  00_治理/台账/待修问题清单.md ｜ 04_站点/web/*.html ｜ assets/3d/weapon_skin/*
                  02_资料/交付、02_资料/源包、03_执行/96_审阅区、03_执行/95_待清理 的目录体积
生成脚本        : 04_站点/web/tools/gen_home.py（只读采集；重跑即刷新本页）
实时数据        : 页面打开后会向 /api/home/snapshot 取数（15 秒一次，页面切到后台自动暂停）；
                  拿不到就保留本页生成时写死的静态值，右上角「↻ 刷新」可强制立即重取</pre>
    </div>
  </aside>
</div>"""

    failchip = ""
    if d["fails"]:
        failchip = (f'<button type="button" class="fail" data-pop="FAIL" data-id="采集"'
                    f' data-name="本次采集失败项" data-st="✗ 需人工核对" data-klass="miss"'
                    f' aria-haspopup="dialog">采集失败 {len(d["fails"])} 项</button>')

    drawer_info = (
        '<h4>项目信息</h4>'
        f'<div class="dkv"><span>索引行数</span><b data-k="rows">{esc(num(d["rows"]))}</b></div>'
        f'<div class="dkv"><span>工具 / 统一入口</span><b data-k="d_tools_entries">{esc(num(d["tools"]))} / '
        f'{esc(str(len(d["entries"])) if d["entries"] else "读取失败")}</b></div>'
        f'<div class="dkv"><span>待修 / 已修</span><b data-k="d_backlog">{esc(str(bl["open"]))} / {esc(str(bl["done"]))}</b></div>'
        f'<div class="dkv"><span>交付</span><b data-k="size_deliver">{esc(human(d["size_deliver"]))}</b></div>'
        f'<div class="dkv"><span>源包</span><b data-k="d_source">{esc(human(d["size_source"]))}</b></div>'
        f'<div class="dkv"><span>审阅区</span><b data-k="size_review">{esc(human(d["size_review"]))}</b></div>'
        f'<div class="dkv"><span>垃圾（待清理）</span><b data-k="size_clean">{esc(human(d["size_clean"]))}</b></div>'
        f'<div class="dkv"><span>项目健康</span><b data-k="d_health">{esc(htxt)}</b></div>')

    html = TEMPLATE
    repl = {
        "@@LEFT@@": render_left(d, hworst, checks),
        "@@GEN@@": d["generated_at"],
        "@@BUILT@@": d["built_at"] or "读取失败",
        "@@STAMP@@": stamp,
        "@@LANES@@": "".join(render_lane(l) for l in lanes_full),
        # ★ 上游带（入口）渲染在线【之前】；横切带（D/Q）渲染在线【之后】。
        "@@BAND_UP@@": "".join(render_band(b, band_seg_id(b), i) for i, b in enumerate(bands_up)),
        "@@BANDS@@": "".join(render_band(b, band_seg_id(b), i) for i, b in enumerate(bands_x)),
        "@@PORTALS@@": render_portals(),
        "@@TPLS@@": "\n".join(tpls),
        "@@TECH@@": tech_btn,
        "@@TECH_PANEL@@": tech_panel,
        "@@FAILCHIP@@": failchip,
        "@@NAV@@": "\n".join(f'<a href="{esc(h)}">{esc(n)}</a>' for n, h, *_ in PORTALS),
        "@@JUMP@@": "".join(f'<a href="#line-{l["mark"]}">{l["mark"]} {esc(l["name"])}</a>' for l in LANES)
                    # ★ 2026-09-28 修：这里原是硬编码 BANDS[0]/BANDS[1]，
                    #   再加一个带就会漏链（第三个带不出现在导航里）。
                    #   改成遍历，且上游带排在前面（与页面渲染顺序一致）。
                    + "".join(f'<a href="#band-{b["mark"]}">{b["mark"]} {esc(b["name"])}</a>'
                              for b in bands_full),
        "@@DRAWER_INFO@@": drawer_info,
    }
    for k, v in repl.items():
        html = html.replace(k, v)
    return html, entries_txt


TEMPLATE = r"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>LifeAfter 拆包项目 · 三线状态</title>
<style>
  :root{
    --bg:#05070c; --bg2:#080c14; --panel:#0b1220; --line:#1c2c44;
    --fg:#dcebff; --dim:#7d93b0; --dim2:#5b7392;
    --cyan:#22e0ff; --mag:#ff2e97; --violet:#9d7bff;
    --ok:#8dff5a; --warn:#ffc02e; --miss:#ff4d6d;
    /* 引用了已闭环编号的「缺什么」条目：整条压暗 + 右侧备注。
       不删条目 —— 保留可见性才能看出散文与清单的漂移。 */
    .no li.refstale{color:#8a94a6;text-decoration:line-through;text-decoration-color:rgba(255,192,46,.5)}
    .no li.refstale .refnote{display:block;margin-top:2px;font-size:11px;line-height:1.5;
      color:var(--warn);text-decoration:none;opacity:.95}
    --mono:ui-monospace,SFMono-Regular,Consolas,"Cascadia Mono","Microsoft YaHei",monospace;
    /* 技术详情面板专用：中文字形由等宽中文字体提供，且【排在】无中文字形的
       Consolas / Cascadia Mono 之前；本机没装 Sarasa Mono SC / Noto Sans Mono CJK SC
       时按回落到 Consolas(西文) + Microsoft YaHei(中文) 渲染，与原观感一致。 */
    --mono-cjk:"Sarasa Mono SC","Noto Sans Mono CJK SC",Consolas,"Cascadia Mono",
      "Microsoft YaHei","Microsoft YaHei UI","PingFang SC",monospace;
    --safe-t:env(safe-area-inset-top); --safe-b:env(safe-area-inset-bottom);
    --top-h:48px;
    /* 紧凑尺度：随视口高度缩放，保证桌面一屏装完 */
    --g:clamp(4px,0.9vh,12px);
    --py:clamp(4px,0.95vh,11px);
    --fs-id:clamp(9.5px,1.15vh,12.5px);
    --fs-nm:clamp(11.5px,1.5vh,17px);
    --fs-sm:clamp(10px,1.45vh,14.5px);
    --fs-lg:clamp(11px,1.3vh,14.5px);
    /* 段块宽度上限：超宽屏也绝不拉伸抽满整宽 */
    --chw:clamp(152px,14.5vw,232px);
    --bw:clamp(126px,10.5vw,190px);
    --leftw:clamp(238px,21vw,312px);
    /* 箭头占位；段块按 4 列栅格定宽，三线跨行同宽对齐 */
    --arw:clamp(13px,1.9vw,32px);
    --slot:min(var(--chw), calc((100% - 3 * var(--arw)) / 4));
  }
  *{box-sizing:border-box;-webkit-tap-highlight-color:transparent}
  html,body{margin:0;padding:0;background:var(--bg);color:var(--fg);
    font-family:system-ui,"Microsoft YaHei",-apple-system,"Segoe UI",sans-serif;
    -webkit-text-size-adjust:100%}
  body{overflow-x:hidden}
  body.popon{overflow:hidden}
  /* 背景：网格 + 双色光晕 + 扫描线 */
  body::before{content:"";position:fixed;inset:0;z-index:0;pointer-events:none;
    background:
      radial-gradient(900px 500px at 12% -8%,rgba(34,224,255,.16),transparent 60%),
      radial-gradient(760px 460px at 92% 4%,rgba(255,46,151,.13),transparent 62%),
      radial-gradient(700px 500px at 50% 108%,rgba(157,123,255,.12),transparent 60%),
      repeating-linear-gradient(0deg,rgba(34,224,255,.055) 0 1px,transparent 1px 44px),
      repeating-linear-gradient(90deg,rgba(34,224,255,.055) 0 1px,transparent 1px 44px),
      linear-gradient(180deg,var(--bg) 0%,var(--bg2) 100%)}
  body::after{content:"";position:fixed;inset:0;z-index:1;pointer-events:none;
    background:repeating-linear-gradient(180deg,rgba(0,0,0,.20) 0 1px,transparent 1px 3px);
    opacity:.5;animation:scan 7s linear infinite}
  @keyframes scan{from{transform:translateY(0)}to{transform:translateY(3px)}}
  @media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}

  /* ---------- 顶栏：站名 + 门户入口（横贯整宽） ---------- */
  #top{position:fixed;left:0;right:0;top:0;min-height:var(--top-h);z-index:60;
    display:flex;align-items:center;gap:clamp(8px,1vw,16px);
    padding:0 clamp(10px,1vw,16px);padding-top:var(--safe-t);
    background:rgba(6,10,18,.9);backdrop-filter:blur(10px);
    border-bottom:1px solid rgba(34,224,255,.35);
    box-shadow:0 0 24px rgba(34,224,255,.16),inset 0 -1px 0 rgba(34,224,255,.18)}
  #top .brand{display:flex;align-items:center;gap:8px;min-width:0;flex:0 0 auto}
  #top .logo{width:20px;height:20px;flex:0 0 20px;position:relative}
  #top .logo i{position:absolute;inset:0;border:1px solid var(--cyan);border-radius:4px;
    box-shadow:0 0 10px rgba(34,224,255,.6),inset 0 0 8px rgba(34,224,255,.28)}
  #top .logo i:nth-child(2){inset:4px;border-color:var(--mag);box-shadow:0 0 8px rgba(255,46,151,.6)}
  #top h1{margin:0;font-size:13px;font-weight:800;letter-spacing:.4px;white-space:nowrap;
    overflow:hidden;text-overflow:ellipsis;
    background:linear-gradient(92deg,var(--cyan),#ffffff 45%,var(--mag));
    -webkit-background-clip:text;background-clip:text;color:transparent}
  #top h1 .short{display:none}
  /* 门户入口：横排、不换行（不撑高顶栏），过窄时可横向滑动 */
  #portalNav{display:flex;flex-wrap:nowrap;align-items:center;gap:clamp(5px,0.55vw,9px);
    min-width:0;flex:1 1 auto;overflow-x:auto;overflow-y:hidden;
    scrollbar-width:none;-ms-overflow-style:none}
  #portalNav::-webkit-scrollbar{display:none}
  .plink{display:inline-flex;align-items:center;gap:6px;text-decoration:none;color:var(--fg);
    font-size:var(--fs-lg);border:1px solid var(--line);border-radius:999px;white-space:nowrap;
    padding:clamp(3px,0.7vh,7px) clamp(8px,0.9vw,13px);background:rgba(11,18,32,.82);
    transition:transform .14s,border-color .14s,box-shadow .14s,color .14s;flex:0 0 auto}
  .plink:hover{border-color:rgba(34,224,255,.65);color:var(--cyan);transform:translateY(-1px);
    box-shadow:0 0 16px rgba(34,224,255,.25)}
  #top .topR{margin-left:auto;display:flex;align-items:center;gap:8px;flex:0 0 auto}
  #top .tstamp{font-family:var(--mono);font-size:11px;color:var(--dim2);white-space:nowrap}
  /* 「↻ 刷新」：强制跳过 15 秒缓存立即重取（与 tstamp 同高，不撑高顶栏） */
  #top .rfbtn{font-family:var(--mono);font-size:11px;line-height:1;color:var(--cyan);
    background:rgba(34,224,255,.08);border:1px solid rgba(34,224,255,.42);border-radius:7px;
    padding:4px 7px;cursor:pointer;white-space:nowrap;flex:0 0 auto}
  #top .rfbtn:hover{background:rgba(34,224,255,.18)}
  #top .rfbtn[disabled]{opacity:.45;cursor:progress}
  #burger{margin-left:auto;display:none;border:1px solid rgba(34,224,255,.5);background:rgba(11,18,32,.9);
    color:var(--cyan);border-radius:8px;padding:6px 12px;font:inherit;font-size:13px;cursor:pointer}
  #mask{display:none}

  /* ---------- 抽屉（手机） ---------- */
  #drawer{position:fixed;left:0;top:var(--top-h);bottom:0;width:86vw;max-width:340px;z-index:55;
    background:linear-gradient(180deg,#070c16,#0a1120);border-right:1px solid rgba(34,224,255,.35);
    box-shadow:8px 0 30px rgba(0,0,0,.7);transform:translateX(-104%);transition:transform .24s ease;
    overflow-y:auto;padding:14px 12px calc(20px + var(--safe-b))}
  body.nav #drawer{transform:translateX(0)}
  #drawer h4{margin:14px 4px 8px;font-size:11px;letter-spacing:1.4px;color:var(--dim2)}
  #drawer h4:first-child{margin-top:2px}
  #drawer a{display:block;text-decoration:none;color:var(--fg);font-size:13.5px;padding:10px 12px;
    border:1px solid var(--line);border-radius:8px;margin-bottom:7px;background:rgba(14,23,40,.75)}
  #drawer a:active{border-color:var(--cyan);color:var(--cyan)}
  .dkv{display:flex;justify-content:space-between;gap:8px;font-size:12.5px;padding:5px 4px;
    border-bottom:1px dashed rgba(28,44,68,.8)}
  .dkv span{color:var(--dim)} .dkv b{font-family:var(--mono);color:#fff}

  /* ---------- 主区：左信息块 + 右三线三带 ---------- */
  /* align-content:center → 左块与右区作为一整块在视口内垂直居中；
     高视口下留白落在整块外，而不是让卡片内部空掉或把左块拉成一张长条 */
  main{position:relative;z-index:2;max-width:1560px;margin:0 auto;
    min-height:100vh;display:grid;grid-template-columns:var(--leftw) minmax(0,1fr);
    align-items:stretch;align-content:center;gap:clamp(7px,0.9vh,13px);
    padding:calc(var(--top-h) + var(--safe-t) + var(--g)) clamp(10px,1vw,16px) calc(var(--g) + var(--safe-b))}

  /* 左信息块：固定宽度，不随屏幕拉伸；两块指标吃到剩余高度，行高自然撑开 */
  #left{display:flex;flex-direction:column;gap:var(--g);
    min-width:0;overflow:hidden;border:1px solid var(--line);border-radius:14px;
    padding:clamp(10px,1.5vh,18px) clamp(10px,0.9vw,16px);
    background:linear-gradient(180deg,rgba(11,18,32,.94),rgba(7,11,20,.9));
    box-shadow:inset 0 1px 0 rgba(34,224,255,.1)}
  #left .ltop,#left .health{flex:0 0 auto}
  #left .lsec{flex:1 1 auto;display:flex;flex-direction:column;justify-content:space-between;min-height:0}
  #left .lsec h4{flex:0 0 auto}
  .ltop{min-width:0}
  .leyebrow{font-family:var(--mono);font-size:10px;letter-spacing:2.4px;color:var(--dim2);
    white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .bigtitle{margin:clamp(3px,0.7vh,8px) 0 0;font-weight:900;letter-spacing:.5px;
    font-size:clamp(21px,3.5vh,33px);line-height:1.14;
    background:linear-gradient(96deg,var(--cyan),#ffffff 46%,var(--mag));
    -webkit-background-clip:text;background-clip:text;color:transparent}
  .lsub{margin-top:clamp(3px,0.7vh,7px);font-size:var(--fs-lg);color:var(--dim)}
  .lsec{min-width:0}
  .lsec h4{margin:0 0 clamp(2px,0.5vh,6px);font-size:10px;letter-spacing:1.6px;
    color:var(--dim2);font-weight:600}
  .kv{display:flex;align-items:baseline;justify-content:space-between;gap:8px;
    padding:clamp(2px,0.45vh,5px) 0;font-size:var(--fs-lg);
    border-bottom:1px dashed rgba(28,44,68,.75)}
  .kv:last-child{border-bottom:0;padding-bottom:0}
  .kv span{color:var(--dim);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .kv b{font-family:var(--mono);font-size:clamp(12px,1.45vh,15px);color:#fff;font-weight:700;
    font-variant-numeric:tabular-nums;white-space:nowrap;flex:0 0 auto}
  .kv b.g{color:#ffd8a8}
  .kv.svrow{align-items:center}
  .kv.svrow b{font-size:clamp(11px,1.35vh,14px);text-align:right;flex:1 1 auto;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .kv.svrow .svtime{font-family:var(--mono);font-style:normal;font-size:10px;color:var(--dim);flex:0 0 auto;margin-left:6px}
  .svhint{font-size:9px;letter-spacing:0;color:var(--dim);font-weight:400;text-transform:none}
  .health{display:flex;align-items:center;gap:10px;border-radius:12px;min-width:0;
    padding:clamp(6px,1.1vh,11px) clamp(8px,0.7vw,12px);border:1px solid var(--line)}
  .health.ok{border-color:rgba(141,255,90,.5);background:linear-gradient(90deg,rgba(141,255,90,.15),rgba(141,255,90,.02))}
  .health.warn{border-color:rgba(255,192,46,.55);background:linear-gradient(90deg,rgba(255,192,46,.15),rgba(255,192,46,.02))}
  .health.miss{border-color:rgba(255,77,109,.6);background:linear-gradient(90deg,rgba(255,77,109,.17),rgba(255,77,109,.02))}
  .lamp{width:13px;height:13px;border-radius:50%;flex:0 0 13px}
  .health.ok .lamp{background:var(--ok);box-shadow:0 0 14px var(--ok),0 0 0 4px rgba(141,255,90,.16)}
  .health.warn .lamp{background:var(--warn);box-shadow:0 0 14px var(--warn),0 0 0 4px rgba(255,192,46,.16)}
  .health.miss .lamp{background:var(--miss);box-shadow:0 0 14px var(--miss),0 0 0 4px rgba(255,77,109,.18)}
  .hbody{min-width:0}
  .hbody b{font-size:clamp(12.5px,1.65vh,16px);font-weight:800;white-space:nowrap}
  .health.ok .hbody b{color:var(--ok)} .health.warn .hbody b{color:var(--warn)} .health.miss .hbody b{color:var(--miss)}
  .hcks{display:flex;flex-wrap:wrap;gap:3px 9px;margin-top:3px}
  .hck{display:inline-flex;align-items:center;gap:4px;font-size:10px;color:var(--dim);
    font-family:var(--mono);white-space:nowrap}
  .hck.warn{color:#ffd98a} .hck.miss{color:#ffb3bf}

  /* 右主区：三线 + 两带（行高有上限，富余高度变成上下留白，不摊进卡片里） */
  #flow{display:flex;flex-direction:column;justify-content:center;gap:clamp(6px,1.1vh,14px);
    min-width:0;overflow:hidden;min-height:min(80vh,780px)}

  .lane{flex:1 1 0;min-height:0;max-height:min(210px,24vh);position:relative;overflow:hidden;
    display:flex;align-items:stretch;gap:clamp(6px,0.8vw,14px);
    border:1px solid var(--line);border-radius:12px;padding:var(--py) clamp(8px,0.9vw,14px);
    background:linear-gradient(180deg,rgba(11,18,32,.9),rgba(7,11,20,.86))}
  .lane::before{content:"";position:absolute;left:0;top:10px;bottom:10px;width:2px;border-radius:2px;
    background:repeating-linear-gradient(180deg,var(--cyan) 0 12px,rgba(34,224,255,.05) 12px 26px);
    box-shadow:0 0 12px rgba(34,224,255,.5);animation:rail 1.3s linear infinite}
  @keyframes rail{to{background-position:0 26px}}
  .llabel{flex:0 0 clamp(122px,11.5vw,180px);min-width:0;display:flex;flex-direction:column;
    justify-content:center;gap:clamp(2px,0.5vh,5px);padding-left:9px}
  .row1{display:flex;align-items:center;gap:6px;min-width:0}
  .mk{font-family:var(--mono);font-size:clamp(13px,1.7vh,16px);font-weight:800;color:var(--cyan);
    border:1px solid rgba(34,224,255,.5);border-radius:7px;width:clamp(22px,2.8vh,27px);height:clamp(22px,2.8vh,27px);
    display:grid;place-items:center;background:rgba(34,224,255,.08);flex:0 0 auto}
  .mk.v{color:var(--violet);border-color:rgba(157,123,255,.6);background:rgba(157,123,255,.1)}
  .nm{font-size:var(--fs-nm);font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .llabel .lsub{font-size:10px;color:var(--dim2);line-height:1.45;
    display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
  .lstat{display:flex;gap:5px;flex-wrap:wrap;align-items:center;flex:0 0 auto;
    padding-left:6px;border-left:1px dashed rgba(34,224,255,.28)}
  .lstat .s{font-size:10.5px;font-family:var(--mono);opacity:.92;white-space:nowrap}
  .lstat .s.ok{color:var(--ok)} .lstat .s.warn{color:var(--warn)} .lstat .s.miss{color:var(--miss)}
  /* 段链：按 4 列栅格定宽（--slot），不伸不抽满；lane 2 恰满，lane 1/3 第 4 格留白 */
  .chain{flex:1 1 0;display:flex;align-items:stretch;gap:0;min-width:0;overflow:hidden}
  .chip{flex:0 1 var(--slot);max-width:var(--chw);min-width:0;appearance:none;font:inherit;
    text-align:left;cursor:pointer;color:var(--fg);overflow:hidden;
    display:flex;flex-direction:column;gap:clamp(2px,0.45vh,5px);
    padding:var(--py) calc(var(--py) + 3px);
    border:1px solid var(--line);border-left-width:3px;border-radius:10px;
    background:linear-gradient(180deg,rgba(14,23,40,.92),rgba(8,13,24,.92));
    transition:transform .14s,border-color .14s,box-shadow .14s}
  .chip.ok{border-left-color:var(--ok)} .chip.warn{border-left-color:var(--warn)} .chip.miss{border-left-color:var(--miss)}
  .chip:hover,.chip:focus-visible{border-color:rgba(34,224,255,.65);box-shadow:0 0 18px rgba(34,224,255,.2);
    transform:translateY(-1px);outline:none}
  .crow{display:flex;align-items:center;justify-content:space-between;gap:6px;min-width:0}
  .cid{font-family:var(--mono);font-size:var(--fs-id);color:var(--cyan);letter-spacing:.6px}
  .cst{font-size:var(--fs-sm);color:var(--dim);white-space:nowrap}
  .chip.ok .cst{color:var(--ok)} .chip.warn .cst{color:var(--warn)} .chip.miss .cst{color:var(--miss)}
  .cname{font-size:var(--fs-nm);font-weight:800;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .cline{flex:1 1 auto;font-size:var(--fs-sm);line-height:1.5;color:var(--dim);min-height:0;
    display:-webkit-box;-webkit-line-clamp:4;-webkit-box-orient:vertical;overflow:hidden}
  .cfoot{flex:0 0 auto;font-family:var(--mono);font-size:10px;color:var(--dim2);
    border-top:1px dashed rgba(28,44,68,.9);padding-top:clamp(2px,0.4vh,4px)}
  .arw{position:relative;flex:0 0 var(--arw);height:2px;align-self:center;margin:0 1px;
    border-radius:2px;background:linear-gradient(90deg,rgba(34,224,255,.12),rgba(34,224,255,.75))}
  .arw::after{content:"";position:absolute;right:-1px;top:-3.5px;width:7px;height:7px;
    border-right:2px solid var(--cyan);border-top:2px solid var(--cyan);transform:rotate(45deg);opacity:.9}
  .arw::before{content:"";position:absolute;top:-1px;width:4px;height:4px;border-radius:50%;
    background:var(--cyan);box-shadow:0 0 8px var(--cyan);animation:dot 1.5s linear infinite}
  @keyframes dot{from{left:0;opacity:0}20%{opacity:1}90%{opacity:1}to{left:100%;opacity:0}}
  .arw.sm{flex:0 0 clamp(9px,1.2vw,18px)}
  /* 段链内尾部的虚线填充：把「第 4 格留白」画成导轨，宽度不摊给卡片 */
  .rail{flex:1 1 auto;min-width:0;align-self:center;height:0;
    border-top:1px dashed rgba(34,224,255,.22)}

  /* 两条横切带 */
  .row-band{width:100%;appearance:none;font:inherit;text-align:left;cursor:pointer;color:var(--fg);
    display:flex;align-items:center;gap:clamp(6px,0.8vw,14px);flex:0 0 auto;
    border:1px dashed rgba(157,123,255,.55);border-radius:12px;
    padding:var(--py) clamp(8px,0.9vw,14px);
    background:linear-gradient(90deg,rgba(157,123,255,.10),rgba(34,224,255,.06),rgba(255,46,151,.08));
    position:relative;overflow:hidden;transition:box-shadow .14s,border-color .14s}
  .row-band::before{content:"";position:absolute;left:0;right:0;top:0;height:1px;
    background:repeating-linear-gradient(90deg,var(--violet) 0 10px,transparent 10px 20px);
    background-size:20px 1px;animation:flow 1.4s linear infinite;opacity:.85}
  @keyframes flow{to{background-position:20px 0}}
  .row-band:hover,.row-band:focus-visible{border-color:rgba(157,123,255,.9);
    box-shadow:0 0 22px rgba(157,123,255,.22);outline:none}
  .blabel{flex:0 0 clamp(132px,11.5vw,180px);min-width:0;display:flex;flex-direction:column;gap:2px;
    border-right:1px dashed rgba(157,123,255,.4);padding-right:10px}
  .blabel .nm{font-size:clamp(11.5px,1.4vh,14px)}
  .role{font-size:10.5px;color:var(--cyan);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  /* 带内闸门：与段块同一套 4 列栅格，跨行同宽对齐 */
  .bgates{flex:1 1 0;display:flex;align-items:stretch;gap:0;min-width:0;overflow:hidden}
  .gate,.floww{flex:0 1 var(--slot);max-width:var(--slot);min-width:0;display:flex;align-items:center;
    gap:6px;flex-wrap:wrap;border:1px solid var(--line);border-radius:9px;
    padding:calc(var(--py) - 2px) calc(var(--py) + 1px);background:rgba(8,13,24,.7)}
  .gate.warn{border-color:rgba(255,192,46,.42)} .gate.miss{border-color:rgba(255,77,109,.5)}
  .gate b,.gate .gname{font-size:var(--fs-sm);font-weight:700;white-space:nowrap}
  .gate b{font-family:var(--mono);font-size:10px;font-weight:600;color:var(--cyan)}
  .gate .gname{overflow:hidden;text-overflow:ellipsis}
  .gate .gs{font-size:10px;white-space:nowrap;margin-left:auto}
  .gate.warn .gs{color:var(--warn)} .gate.miss .gs{color:var(--miss)}
  .floww{font-size:var(--fs-sm);justify-content:center;color:#cfe6ff}
  .bst,.bhint{font-size:var(--fs-sm);white-space:nowrap;flex:0 0 auto}
  .bst{color:var(--warn)} .bhint{font-family:var(--mono);color:var(--dim2)}

  .dot{width:7px;height:7px;border-radius:50%;display:inline-block;flex:0 0 auto}
  .dot.ok{background:var(--ok);box-shadow:0 0 7px var(--ok)}
  .dot.warn{background:var(--warn);box-shadow:0 0 7px var(--warn)}
  .dot.miss{background:var(--miss);box-shadow:0 0 7px var(--miss)}

  /* ---------- 技术详情：右侧滑出抽屉（body 级固定层） ----------
     ⚠ 祖先陷阱：任何带 transform / filter / backdrop-filter / will-change 的祖先
     都会成为 position:fixed 后代的包含块。顶栏 #top 有 backdrop-filter:blur(10px)，
     所以放在 #top 里的 fixed 元素会相对「48px 高的顶栏」而不是视口定位（曾经把面板
     顶到视口上方 523px）。#techDrawer 是 body 的直接子元素，祖先链干净，
     以后要是有新的浮层，一律挂在 body 级，别塞进顶栏。 */
  .tech-btn{cursor:pointer;list-style:none;color:var(--cyan);border:1px solid rgba(34,224,255,.4);
    border-radius:999px;padding:3px 10px;font:inherit;font-size:11.5px;background:rgba(11,18,32,.8);
    white-space:nowrap;flex:0 0 auto}
  .tech-btn:hover{background:rgba(34,224,255,.16);box-shadow:0 0 14px rgba(34,224,255,.25)}
  .tech-btn::before{content:"▸ ";font-size:10px}
  body.techon .tech-btn::before{content:"▾ "}
  #techDrawer{position:fixed;inset:0;z-index:110;visibility:hidden;pointer-events:none}
  #techDrawer.show{visibility:visible;pointer-events:auto}
  .tech-mask{position:absolute;inset:0;background:rgba(2,5,10,.6);opacity:0;cursor:pointer;
    transition:opacity .22s ease}
  #techDrawer.show .tech-mask{opacity:1}
  /* 面板：独立浮层，不参与主布局 ⇒ 展开不改变主内容区高度 */
  .tech-panel{position:absolute;top:calc(var(--top-h) + 10px);right:12px;
    bottom:calc(12px + var(--safe-b));width:min(620px,94vw);
    display:flex;flex-direction:column;min-height:0;
    border:1px solid rgba(34,224,255,.45);border-radius:14px;
    background:linear-gradient(180deg,#0b1220,#070b14);
    box-shadow:-18px 0 60px rgba(0,0,0,.78),0 0 30px rgba(34,224,255,.12);
    transform:translateX(calc(100% + 24px));transition:transform .26s ease}
  #techDrawer.show .tech-panel{transform:none}
  .tech-top{display:flex;align-items:center;gap:10px;flex:0 0 auto;padding:9px 12px;
    border-bottom:1px solid var(--line);background:rgba(9,14,26,.92);border-radius:14px 14px 0 0}
  .tech-title{font-size:13px;font-weight:800;color:var(--fg);white-space:nowrap}
  .tech-hint{font-family:var(--mono-cjk);font-size:11px;color:var(--dim2);min-width:0;
    overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
  .tech-x{margin-left:auto;appearance:none;cursor:pointer;color:var(--fg);font:inherit;font-size:13px;
    border:1px solid rgba(34,224,255,.5);background:rgba(12,20,36,.95);border-radius:9px;
    padding:7px 13px;min-height:34px;flex:0 0 auto}
  .tech-x:hover{color:var(--cyan);box-shadow:0 0 14px rgba(34,224,255,.3)}
  /* 面板内部可滚动（技术详情约 20 行，比一屏高） */
  .tech-body{flex:1 1 auto;min-height:0;overflow:auto;overscroll-behavior:contain;
    padding:10px 13px calc(12px + var(--safe-b))}
  .tech-body pre{font-family:var(--mono-cjk);font-size:11.5px;line-height:1.7;color:#9fd8ff;
    white-space:pre-wrap;word-break:break-all;margin:0}
  .fail{border:1px solid rgba(255,77,109,.6);background:rgba(255,77,109,.12);color:#ffd7de;
    border-radius:999px;padding:3px 10px;font:inherit;font-size:11.5px;cursor:pointer;white-space:nowrap}

  /* ---------- 弹层（详情不进主布局） ---------- */
  #pop{position:fixed;inset:0;z-index:120;display:none}
  #pop.show{display:flex;align-items:center;justify-content:center;padding:16px}
  .pop-mask{position:absolute;inset:0;background:rgba(2,5,10,.74);backdrop-filter:blur(3px);cursor:pointer}
  .pop-box{position:relative;z-index:1;width:min(960px,96vw);max-height:min(80vh,780px);overflow:auto;
    border:1px solid rgba(34,224,255,.5);border-radius:14px;background:linear-gradient(180deg,#0b1220,#070b14);
    box-shadow:0 24px 70px rgba(0,0,0,.85)}
  .pop-top{position:sticky;top:0;z-index:2;display:flex;align-items:center;gap:10px;flex-wrap:wrap;
    padding:10px 14px;background:rgba(9,14,26,.985);border-bottom:1px solid var(--line)}
  .ptag{font-family:var(--mono);font-size:11.5px;color:var(--cyan);border:1px solid rgba(34,224,255,.45);
    border-radius:7px;padding:2px 8px;background:rgba(34,224,255,.08)}
  .pname{font-size:16px;font-weight:800}
  .pst{font-size:11.5px;border-radius:999px;padding:2px 10px;border:1px solid var(--line)}
  .pst.ok{color:var(--ok);border-color:rgba(141,255,90,.45);background:rgba(141,255,90,.08)}
  .pst.warn{color:var(--warn);border-color:rgba(255,192,46,.45);background:rgba(255,192,46,.08)}
  .pst.miss{color:var(--miss);border-color:rgba(255,77,109,.45);background:rgba(255,77,109,.08)}
  #popX{margin-left:auto;appearance:none;cursor:pointer;color:var(--fg);font:inherit;font-size:13px;
    border:1px solid rgba(34,224,255,.5);background:rgba(12,20,36,.95);border-radius:9px;
    padding:8px 14px;min-height:36px}
  #popX:hover{color:var(--cyan);box-shadow:0 0 14px rgba(34,224,255,.3)}
  .popBody{padding:10px 14px 14px}
  .popline{margin:0 0 10px;font-size:13px;color:var(--dim);line-height:1.65}
  .cols{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .cols.one{grid-template-columns:1fr}
  .col h4{margin:0 0 6px;font-size:12.5px;color:var(--dim);display:flex;align-items:center;gap:6px}
  .col ul{margin:0;padding-left:18px;font-size:13px;line-height:1.72}
  .col ul.yes li::marker{color:var(--ok)}
  .col ul.no li::marker{color:var(--miss)}
  .col ul.no{color:#ffd3db}
  .gates{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:0 0 12px}
  .gates .gate{display:block;flex:none;max-width:none;border-radius:10px;padding:10px 12px;background:rgba(8,13,24,.8)}
  .gno{font-family:var(--mono);font-size:11px;color:var(--cyan);letter-spacing:.6px}
  .gates .gname{display:block;font-size:14px;font-weight:700;margin:4px 0 3px}
  .gline{font-size:12.5px;color:var(--dim);line-height:1.6}
  .gates .gate.warn{border-color:rgba(255,192,46,.45)} .gates .gate.miss{border-color:rgba(255,77,109,.5)}

  /* ---------- 窄屏：≤1180 收起时间戳 ---------- */
  @media (max-width:1180px){ #top .tstamp{display:none} }

  /* ---------- 手机 / 小平板：左块改上下堆叠 ---------- */
  @media (max-width:820px){
    :root{--top-h:46px}
    #burger{display:block}
    #top h1 .full{display:none} #top h1 .short{display:inline}
    #portalNav{display:none}
    body.nav #mask{display:block;position:fixed;left:0;right:0;top:var(--top-h);bottom:0;z-index:50;
      background:rgba(2,5,10,.55);backdrop-filter:blur(2px)}
    main{min-height:0;grid-template-columns:minmax(0,1fr);padding-left:10px;padding-right:10px}
    #left{gap:10px}
    .bigtitle{font-size:clamp(24px,6.4vw,34px)}
    #left .lsec{display:grid;grid-template-columns:1fr 1fr;gap:0 14px}
    #left .lsec h4{grid-column:1/-1}
    .lane{flex:none;max-height:none;flex-direction:column;align-items:stretch;gap:7px;padding:9px 10px}
    .llabel{flex:none;flex-direction:row;align-items:center;gap:8px;flex-wrap:wrap;
      border-right:0;border-bottom:1px dashed var(--line);padding:0 0 7px}
    .llabel .lsub{display:none}
    .chain{display:grid;grid-template-columns:1fr 1fr;gap:7px;flex:none;max-width:none;overflow:visible}
    .chip{max-width:none;flex:none;padding:9px 10px}
    .arw,.arw.sm{display:none}
    .rail,.lstat{display:none}
    .row-band{flex-direction:column;align-items:stretch;gap:7px;padding:9px 10px}
    .blabel{flex:none;border-right:0;border-bottom:1px dashed rgba(157,123,255,.4);padding:0 0 7px}
    .bgates{display:grid;grid-template-columns:1fr 1fr;gap:7px;flex:none;max-width:none;overflow:visible}
    .gate,.floww{max-width:none}
    .bst,.bhint{display:none}
    #flow{justify-content:flex-start;min-height:0}
    #pop.show{align-items:flex-end;padding:0}
    .cols{grid-template-columns:1fr}
    .pop-box{width:100%;max-width:100%;max-height:86vh;border-radius:14px 14px 0 0}
    .popBody{padding-bottom:calc(16px + var(--safe-b))}
    .tech-panel{left:8px;right:8px;width:auto;top:calc(var(--top-h) + 8px);bottom:calc(8px + var(--safe-b))}
  }
  @media (max-width:400px){
    .chain{grid-template-columns:1fr}
    .bgates{grid-template-columns:1fr}
    #left .lsec{grid-template-columns:1fr}
  }
</style></head><body>
<div id="top">
  <div class="brand">
    <span class="logo" aria-hidden="true"><i></i><i></i></span>
    <h1><span class="full">LifeAfter 拆包项目 · 三线三带状态</span><span class="short">拆包状态</span></h1>
  </div>
  <nav id="portalNav" aria-label="子界面入口">
@@PORTALS@@
  </nav>
  <div class="topR">
    <span class="tstamp" data-k="stamp">@@STAMP@@</span>
    <button type="button" id="rfbtn" class="rfbtn" title="立即重新采集（跳过 15 秒缓存）" aria-label="立即刷新数据">↻ 刷新</button>
    @@FAILCHIP@@
    @@TECH@@
    <button id="burger" aria-label="打开菜单" aria-expanded="false">菜单</button>
  </div>
</div>
<div id="drawer" aria-label="站点导航">
  <h4>子界面</h4>
@@NAV@@
  <h4>跳转生产线 / 横切带</h4>
@@JUMP@@
@@DRAWER_INFO@@
</div>
<div id="mask"></div>

<main>
@@LEFT@@
  <section id="flow" aria-label="三线三带">
@@BAND_UP@@
@@LANES@@
@@BANDS@@
  </section>
</main>

<div id="pop" role="dialog" aria-modal="true" aria-label="段详情">
  <div class="pop-mask" id="popMask"></div>
  <div class="pop-box">
    <div class="pop-top">
      <span class="ptag" id="popTag"></span>
      <span class="pname" id="popName"></span>
      <span class="pst" id="popSt"></span>
      <button type="button" id="popX" aria-label="关闭详情">✕ 关闭</button>
    </div>
    <div class="popBody" id="popBody"></div>
  </div>
</div>

@@TECH_PANEL@@

@@TPLS@@

<script>
(function(){
  "use strict";
  try{
    var body=document.body, burger=document.getElementById('burger'),
        mask=document.getElementById('mask'), drawer=document.getElementById('drawer'),
        pop=document.getElementById('pop'), popBody=document.getElementById('popBody'),
        popX=document.getElementById('popX');
    function closeNav(){ body.classList.remove('nav'); burger.setAttribute('aria-expanded','false'); }
    burger.addEventListener('click',function(){
      var on=body.classList.toggle('nav');
      burger.setAttribute('aria-expanded', on?'true':'false');
    });
    mask.addEventListener('click',closeNav);
    Array.prototype.forEach.call(drawer.querySelectorAll('a'),function(a){
      a.addEventListener('click',function(){ if(window.innerWidth<=820) closeNav(); });
    });
    function closePop(){
      pop.classList.remove('show'); body.classList.remove('popon');
      popBody.innerHTML=''; pop.setAttribute('aria-hidden','true');
    }
    var openKey=null;  // 当前打开的段键；轮询重建模板后用它把弹层内容一起刷新
    function openPop(key,el){
      var t=document.getElementById('p'+key); if(!t) return;
      openKey=key;
      popBody.innerHTML='';
      popBody.appendChild(t.content.cloneNode(true));
      document.getElementById('popTag').textContent=el.getAttribute('data-id')||'';
      document.getElementById('popName').textContent=el.getAttribute('data-name')||'';
      var st=document.getElementById('popSt');
      st.textContent=el.getAttribute('data-st')||'';
      st.className='pst '+(el.getAttribute('data-klass')||'');
      pop.classList.add('show'); body.classList.add('popon');
      pop.setAttribute('aria-hidden','false');
      try{ popX.focus(); }catch(e){}
    }
    Array.prototype.forEach.call(document.querySelectorAll('[data-pop]'),function(el){
      el.addEventListener('click',function(e){
        e.preventDefault();
        openPop(el.getAttribute('data-pop'),el);
      });
    });
    popX.addEventListener('click',closePop);
    document.getElementById('popMask').addEventListener('click',closePop);

    /* 技术详情：右侧滑出抽屉（body 级 #techDrawer）
       关闭方式三种：右上角「✕ 关闭」/ 点面板外的遮罩 / Esc。
       面板挂在 body 级、不是 #top 的后代 —— 祖先链上没有 backdrop-filter，
       所以 fixed/absolute 定位相对视口解析（旧版放在顶栏里，被顶到视口上方 523px）。 */
    var techDrawer=document.getElementById('techDrawer'),
        techBtn=document.getElementById('techBtn'),
        techX=document.getElementById('techX'),
        techMask=document.getElementById('techMask');
    function techOpen(){ return !!techDrawer && techDrawer.classList.contains('show'); }
    function openTech(){
      if(!techDrawer) return;
      techDrawer.classList.add('show');
      techDrawer.setAttribute('aria-hidden','false');
      if(techBtn) techBtn.setAttribute('aria-expanded','true');
      body.classList.add('techon');
    }
    function closeTech(){
      if(!techDrawer) return;
      techDrawer.classList.remove('show');
      techDrawer.setAttribute('aria-hidden','true');
      if(techBtn) techBtn.setAttribute('aria-expanded','false');
      body.classList.remove('techon');
    }
    if(techBtn){
      techBtn.addEventListener('click',function(e){
        e.preventDefault();
        if(techOpen()) closeTech(); else openTech();
      });
    }
    if(techX) techX.addEventListener('click',closeTech);
    if(techMask) techMask.addEventListener('click',closeTech);
    window.__tech={isOpen:techOpen,open:openTech,close:closeTech};

    document.addEventListener('keydown',function(e){
      if(e.key==='Escape'){
        if(techOpen()) closeTech();
        else if(pop.classList.contains('show')) closePop();
        else closeNav();
      }
    });

    /* ==================== 主页实时更新 ====================
       每 15 秒拉一次 /api/home/snapshot（服务端复用 gen_home.collect() 取数，带 15 秒缓存与并发锁）。
       拿到 → 就地更新页面数字与顶部时间；拿不到 → 原样保留生成时写死的静态值（离线 / 服务没起也能看）。
       页面切到后台自动暂停轮询，切回来立刻刷新一次并恢复；「↻ 刷新」= 跳过缓存强制重取。 */
    var HOME_POLL_MS=15000;
    var stampEl=document.querySelector('#top .tstamp');
    var staticStamp=stampEl?stampEl.textContent:"";
    var rfBtn=document.getElementById('rfbtn');
    var pollTimer=null,inFlight=false;
    function pad2(n){ return (n<10?"0":"")+n; }
    function numTxt(v){ if(v===null||v===undefined) return "读取失败";
      return String(v).replace(/\B(?=(\d{3})+(?!\d))/g,","); }
    function roundHalfEven(x,d){ var m=Math.pow(10,d),v=x*m,f=Math.floor(v),r=v-f;
      if(r>0.5||(r===0.5&&(f%2===1))) f+=1; return f/m; }
    function humanTxt(n){ if(n===null||n===undefined) return "读取失败";
      if(n>=1073741824) return roundHalfEven(n/1073741824,1).toFixed(1)+" GB";
      if(n>=1048576) return roundHalfEven(n/1048576,0).toFixed(0)+" MB";
      return n+" B"; }
    function txt(v){ return (v===null||v===undefined||v==="")?"读取失败":String(v); }
    var keySeen=0,keyChanged=0;
    function setKey(k,v){ var els=document.querySelectorAll('[data-k="'+k+'"]'),n=0; keySeen+=els.length;
      for(var i=0;i<els.length;i++){ if(els[i].textContent!==v){ els[i].textContent=v; n++; } }
      keyChanged+=n; return n; }
    function healthOf(d){
      var bl=d.backlog||{},c=[],idxOk=(d.quick==="ok");
      c.push(["索引校验",idxOk?"通过":"未通过",idxOk?"ok":"miss"]);
      if(d.stale===false) c.push(["数据新鲜","无过期","ok"]);
      else if(d.stale===true) c.push(["数据新鲜","存在过期项","warn"]);
      else c.push(["数据新鲜","读取失败","miss"]);
      var fc=d.failed_containers;
      if(fc===null||fc===undefined) c.push(["失败容器","读取失败","miss"]);
      else c.push(["失败容器",fc+" 个",fc===0?"ok":"warn"]);
      var op=bl.open;
      if(op===null||op===undefined) c.push(["待修问题","读取失败","miss"]);
      else c.push(["待修问题",op+" 条未闭环",op===0?"ok":"warn"]);
      var order={ok:0,warn:1,miss:2},worst="ok";
      for(var i=0;i<c.length;i++){ if(order[c[i][2]]>order[worst]) worst=c[i][2]; }
      return {worst:worst,label:{ok:"良好",warn:"注意",miss:"异常"}[worst],checks:c};
    }
    function escHtml(s){
      return String(s==null?"":s).replace(/[&<>"']/g,function(c){
        return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c];});
    }
    var ST_MAP={ok:["\u2705","\u5065\u5eb7","ok"],warn:["\u26a0\ufe0f","\u534a\u540a\u5b50","warn"],miss:["\u2717","\u7f3a","miss"]};
    // 三线十段的内容现在来自台账（服务端每次采集现场求值），轮询必须把它一起刷上去，
    // 否则「改台账 / 勾清单」得重新生成 index.html 才看得见 —— 那就不是实时了。
    function applyLanes(lanes){
      lanes=lanes||{}; var n=0,open=openKey;
      for(var id in lanes){
        var r=lanes[id]||{}, tpl=document.getElementById("p"+id);
        if(tpl&&tpl.content){
          var yes=tpl.content.querySelector("ul.yes"), no=tpl.content.querySelector("ul.no");
          if(yes) yes.innerHTML=(r.has||[]).map(function(x){return "<li>"+escHtml(x)+"</li>";}).join("");
          if(no) no.innerHTML=(r.miss||[]).map(function(x){return "<li>"+escHtml(x)+"</li>";}).join("");
        }
        var chip=document.querySelector('.chip[data-pop="'+id+'"]');
        if(chip){
          var m=ST_MAP[r.st||"ok"]||ST_MAP.ok;
          chip.className="chip "+m[2];
          chip.setAttribute("data-klass",m[2]);
          chip.setAttribute("data-st",m[0]+" "+m[1]);
          var cs=chip.querySelector(".cst"); if(cs) cs.textContent=m[0]+" "+m[1];
          var cf=chip.querySelector(".cfoot"); if(cf) cf.textContent="\u7f3a "+((r.miss||[]).length)+" \u6761";
        }
        // 带（H/D/Q）：内容与状态同样来路，状态徽记与「缺 N 条」也要跟着刷。
        // ★ 带的元素是 button.row-band（不是 .chip），上面那个分支选不到它 —— 少这一支，
        //   D/Q 的缺项数在页面上会一直停在生成时的值，看着像台账没生效。
        var band=document.querySelector('.row-band[data-pop="'+id+'"]');
        if(band){
          var mb=ST_MAP[r.st||"warn"]||ST_MAP.warn;
          band.className="row-band "+mb[2];
          band.setAttribute("data-klass",mb[2]);
          band.setAttribute("data-st",mb[0]+" "+mb[1]);
          var bs=band.querySelector(".bst"); if(bs) bs.textContent=mb[0]+" "+mb[1];
          var bh=band.querySelector(".bhint"); if(bh) bh.textContent="\u7f3a "+((r.miss||[]).length)+" \u6761";
        }
        n++;
      }
      // 弹层正开着 ⇒ 用重建后的模板再克隆一次，内容跟着走
      if(open && document.getElementById("p"+open) && pop.classList.contains("show")){
        // 触发器既可能是段块（.chip）也可能是带（.row-band）⇒ 按 data-pop 通用取
        var el=document.querySelector('[data-pop="'+open+'"]');
        if(el) openPop(open,el);
      }
      return n;
    }
    function applyHome(d,meta){
      d=d||{}; var bl=d.backlog||{},hit=0; keySeen=0; keyChanged=0;
      // 段内容跟着一起刷（来自 d.lanes，服务端现场解台账）
      if(typeof applyLanes==="function"){ try{ applyLanes(d.lanes); }catch(e){} }
      var en=(d.entries&&d.entries.length)?String(d.entries.length):"读取失败";
      var pn=(d.pages&&d.pages.length)?String(d.pages.length):"读取失败";
      hit+=setKey("rows",numTxt(d.rows));
      hit+=setKey("tools",numTxt(d.tools));
      hit+=setKey("entries",en);
      hit+=setKey("backlog_open",txt(bl.open));
      hit+=setKey("backlog_done",txt(bl.done));
      hit+=setKey("pages",pn);
      hit+=setKey("skin_assets",numTxt(d.skin_assets));
      hit+=setKey("size_deliver",humanTxt(d.size_deliver));
      hit+=setKey("size_source",(d.files_source===null||d.files_source===undefined)
        ?humanTxt(d.size_source):humanTxt(d.size_source)+" · "+numTxt(d.files_source)+" 文件");
      hit+=setKey("size_review",humanTxt(d.size_review));
      hit+=setKey("size_clean",humanTxt(d.size_clean));
      hit+=setKey("d_tools_entries",numTxt(d.tools)+" / "+en);
      hit+=setKey("d_backlog",txt(bl.open)+" / "+txt(bl.done));
      hit+=setKey("d_source",humanTxt(d.size_source));
      hit+=setKey("t_db",txt(d.db));
      hit+=setKey("t_index_from",txt(d.index_from));
      hit+=setKey("t_quick",d.quick==="ok"?"通过":"未通过");
      hit+=setKey("t_stale",d.stale===false?"否":(d.stale===true?"是":"读取失败"));
      hit+=setKey("t_built",txt(d.built_at));
      hit+=setKey("t_inv",txt(d.inventory_files));
      hit+=setKey("t_split","图形包 "+numTxt(d.row_gpk)+" / 资源包 "+numTxt(d.row_fpk)+" / 数据包 "+numTxt(d.row_npk));
      hit+=setKey("t_fc",txt(d.failed_containers));
      hit+=setKey("t_schema",txt(d.schema_version));
      hit+=setKey("t_fingerprint",d.fingerprint?String(d.fingerprint).slice(0,32)+"…":"读取失败");
      hit+=setKey("t_entries",(d.entries&&d.entries.length)?d.entries.join(" / "):"读取失败");
      hit+=setKey("t_backlog","未修 "+txt(bl.open)+" / 已修 "+txt(bl.done));
      hit+=setKey("t_skin_root",txt(d.skin_root));
      var h=healthOf(d);
      hit+=setKey("t_health",h.label+"（"+h.checks.map(function(x){return x[0]+x[1];}).join("；")+"）");
      hit+=setKey("d_health",h.label);
      var hw=document.getElementById("health");
      if(hw){
        hw.className="health "+h.worst;
        var hl=document.getElementById("healthLabel");
        if(hl) hl.textContent="项目健康："+h.label;
        var hc=document.getElementById("healthCks");
        if(hc){ hc.innerHTML=h.checks.map(function(x){
          return '<span class="hck '+x[2]+'"><span class="dot '+x[2]+'"></span>'+x[0]+' '+x[1]+'</span>'; }).join(""); hit+=1; }
      }
      hit+=setKey("t_gen",(meta&&meta.collected_at?meta.collected_at:"读取失败")+"（实时采集）");
      var sec=(meta&&typeof meta.collect_seconds==="number")?meta.collect_seconds.toFixed(1):"—";
      var cacheTxt=(meta&&meta.cache&&meta.cache.hit&&meta.cache.age_seconds>=1)
        ?" · 缓存 "+Math.round(meta.cache.age_seconds)+" 秒前":"";
      var now=new Date();
      var when=(meta&&meta.collected_at&&meta.collected_at.length>=19)
        ?meta.collected_at.slice(11):(pad2(now.getHours())+":"+pad2(now.getMinutes())+":"+pad2(now.getSeconds()));
      hit+=setKey("stamp","数据采集于 "+when+"（用时 "+sec+" 秒"+cacheTxt+"）· 每 15 秒自动刷新");
      return {changed:keyChanged,seen:keySeen};
    }
    function homeStatic(reason){
      if(stampEl) stampEl.textContent=(staticStamp||"数据采集于 —")+" · 实时刷新不可用："+reason;
      window.__homeLive={mode:"static",reason:reason,stamp:stampEl?stampEl.textContent:""};
    }
    function loadHome(force){
      if(inFlight||!window.fetch) return;
      inFlight=true;
      fetch("/api/home/snapshot"+(force?"?force=1":""),{cache:"no-store"})
        .then(function(r){ if(!r.ok) throw new Error("接口返回 "+r.status); return r.json(); })
        .then(function(j){
          if(!j||!j.data||!j.data.backlog) throw new Error("响应缺少 data 字段");
          var applied=applyHome(j.data,{collected_at:j.collected_at,collect_seconds:j.collect_seconds,cache:j.cache});
          window.__homeLive={mode:"live",collected_at:j.collected_at,collect_seconds:j.collect_seconds,
            cache_hit:!!(j.cache&&j.cache.hit),nodes_changed:applied.changed,nodes_seen:applied.seen,
            unreadable_fields:((j.failed_items||{}).unreadable_fields)||[],
            values:{rows:j.data.rows,pages:(j.data.pages||[]).length,backlog_open:(j.data.backlog||{}).open,
                    size_clean:j.data.size_clean,skin_assets:j.data.skin_assets},
            stamp:stampEl?stampEl.textContent:""};
        })
        .catch(function(e){ homeStatic(String(e&&e.message?e.message:e)); })
        .then(function(){ inFlight=false; });
    }
    function stopPoll(){ if(pollTimer){ clearInterval(pollTimer); pollTimer=null; } }
    function startPoll(){ stopPoll(); if(!document.hidden) pollTimer=setInterval(function(){ loadHome(false); },HOME_POLL_MS); }
    if(rfBtn){
      rfBtn.addEventListener('click',function(){
        rfBtn.disabled=true;
        loadHome(true);
        setTimeout(function(){ rfBtn.disabled=false; },1500);
      });
    }
    document.addEventListener('visibilitychange',function(){
      if(document.hidden) stopPoll(); else { loadHome(true); startPoll(); }
    });
    loadHome(false);
    startPoll();

    // 自检钩子（与站点其他页面一致）
    window.__loaded=(window.__loaded||0)+1;
    window.addEventListener('error',function(e){ window.__err=String(e.message||e); });
  }catch(e){ window.__err=String(e); }
})();
/* ★ 服务器时间实时刷新：从 /api/server_time 拉各服 HTTP Date（20s 缓存） */
(function(){
  var cells = document.querySelectorAll('.svtime[data-sv]');
  if (!cells.length) return;
  function tick(){
    fetch('/api/server_time', {cache:'no-store'}).then(function(r){return r.json();}).then(function(d){
      var by = {};
      (d.servers||[]).forEach(function(s){ by[s.key] = s; });
      cells.forEach(function(el){
        var s = by[el.getAttribute('data-sv')];
        if (!s) return;
        if (s.ok && s.local) {
          var t = s.local.slice(11, 19);
          var d2 = s.delta_seconds;
          el.textContent = t + (d2 ? (d2 > 0 ? ' +'+d2+'s' : ' '+d2+'s') : '');
          el.title = '服务器(HTTP Date)：' + s.utc + ' UTC\\n本地对比：' + (d2===0 ? '一致' : (d2>0?'快 '+d2+' 秒':'慢 '+(0-d2)+' 秒'));
          el.style.color = (d2 === 0) ? '' : '#ffd8a8';
        } else if (s.error) {
          el.textContent = '抓取失败';
          el.title = s.error;
        }
      });
    }).catch(function(){});
  }
  tick();
  setInterval(tick, 15000);
})();
</script>
</body></html>
"""


def main():
    t0 = time.time()
    d = collect()
    collect_seconds = time.time() - t0
    if "--json" in sys.argv:
        print(json.dumps(d, ensure_ascii=False, indent=2))
        return 0
    html, entries_txt = build(d, collect_seconds=collect_seconds)
    OUT.write_text(html, encoding="utf-8")
    print(f"[ok] 已生成 {OUT}")
    print(f"     大小 {OUT.stat().st_size} 字节")
    print(f"     采集耗时 {collect_seconds:.2f} 秒")
    print(f"     索引来源={d['index_from']}")
    print(f"     索引行数={d['rows']} 工具数={d['tools']} 入口={entries_txt} "
          f"待修 {d['backlog']['open']}/已修 {d['backlog']['done']} 页面={len(d['pages'])}")
    print(f"     交付={human(d['size_deliver'])} 源包={human(d['size_source'])}({d['files_source']} 文件) "
          f"审阅区={human(d['size_review'])} 垃圾={human(d['size_clean'])}")
    print(f"     项目健康={health_report(d)[1]}")
    if d["fails"]:
        print("     [warn] 采集失败项：" + " | ".join(d["fails"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
