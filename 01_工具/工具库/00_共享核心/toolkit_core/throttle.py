# -*- coding: utf-8 -*-
"""资源限流：让长任务自动用【不超过 ~80%】的 CPU/GPU，把余量留给系统/浏览器/游戏。

## 为什么有它

`toolkit_core/scheduler.py` 里的 `SmartScheduler` 只**生成计划**（文件里自己写着
「只生成计划；实际执行器必须把取消事件和进度队列传入 worker」），
而 GUI 那个「上限：CPU/GPU 约 80%」的标签**从来没接上执行器** —— 是个标签。
CLI 更是完全没有这个概念（全量体检单线程跑，32 核只用了 1 核）。

本模块补上执行侧，做三件事：
  1. **真读负载**：CPU 走 psutil；GPU 走 nvidia-smi（拿不到就如实返回 None）
  2. **算并行预算**：worker 数 = 核数 × cpu_limit%，即「最多用多少」
  3. **带反馈限流**：跑的过程中采样，一旦实测负载超上限就 sleep 让路（duty cycle）

## GPU 的诚实说明（2026-09-28 核实并更正）

解码线（解压/解密/解码/识别）**在行为上仍全程不碰 GPU**，但理由不是「没有库」：

  · 环境**已有** GPU 能力：venv 里 torch 2.11.0+cu128，
    `torch.cuda.is_available()` = True，RTX 5080 / sm_120；
    `nvidia-smi` 可读（本模块的 gpu_percent 就靠它）。
    （cupy 确实没装 —— 原描述这句是对的。）
  · 真正原因：**全库没有任何代码 import torch / 用 cuda**。
    解压/解密/解码/识别这条路是 numpy + PIL 写的，跑不到 GPU 上。

⇒ 所以 `gpu_limit` 对 kinds=("decode",) 仍不适用——本模块会明说，而不是假装限了。
  它对 kinds=("render","screenshot","glb_gpu") 适用（见 LoadPolicy.gpu_applicable）。
  Chrome 侧一律带 `--disable-gpu --enable-unsafe-swiftshader`（软件渲染），这条属实。

★ **未利用的机会**：torch+CUDA 已就位，但**目前没有任何命令用 kinds=("render",)**。
  若把渲染 / 批量图像处理（如 alpha 内外差这类整型数组统计）挪到 GPU，
  那条分支才有真实场景，`gpu_limit` 也才有实际约束力。
"""
from __future__ import annotations

import os
import subprocess
import time
from dataclasses import dataclass, field
from typing import Optional

try:
    import psutil
except Exception:                                    # pragma: no cover
    psutil = None


# ── 负载读数 ────────────────────────────────────────────────────────────

def cpu_count() -> int:
    return max(1, os.cpu_count() or 1)


def cpu_percent(interval: float = 0.0) -> Optional[float]:
    """整机 CPU 占用 %。psutil 不在时用 Windows 的 GetSystemTimes 兜底。"""
    if psutil is not None:
        try:
            return float(psutil.cpu_percent(interval=interval))
        except Exception:
            pass
    if os.name == "nt":
        try:
            import ctypes

            class _FT(ctypes.Structure):
                _fields_ = [("lo", ctypes.c_ulong), ("hi", ctypes.c_ulong)]

            def v(f):
                return (f.hi << 32) | f.lo

            k = ctypes.windll.kernel32
            a, b, c = _FT(), _FT(), _FT()
            k.GetSystemTimes(ctypes.byref(a), ctypes.byref(b), ctypes.byref(c))
            i0, k0, u0 = v(a), v(b), v(c)
            time.sleep(max(0.1, interval or 0.2))
            k.GetSystemTimes(ctypes.byref(a), ctypes.byref(b), ctypes.byref(c))
            di, dk, du = v(a) - i0, v(b) - k0, v(c) - u0
            tot = dk + du
            return round((tot - di) / tot * 100, 1) if tot else None
        except Exception:
            return None
    return None


_GPU_CACHE: dict = {"t": 0.0, "v": None}


def _has_module(name: str) -> bool:
    """模块是否可导入（用 find_spec，不真的 import —— import torch 太慢）。"""
    import importlib.util
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def gpu_percent(ttl: float = 1.0) -> Optional[float]:
    """NVIDIA GPU 利用率 %。拿不到就返回 None（不猜）。

    只用 nvidia-smi —— 本机是 RTX 5080，可用；AMD 无对应 CLI 计数器的就返回 None。
    """
    now = time.time()
    if now - _GPU_CACHE["t"] < ttl:
        return _GPU_CACHE["v"]
    val = None
    try:
        pr = subprocess.run(
            ["nvidia-smi", "--query-gpu=utilization.gpu", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=4, encoding="utf-8", errors="replace")
        if pr.returncode == 0:
            first = (pr.stdout or "").strip().splitlines()
            if first:
                val = float(first[0].strip())
    except Exception:
        val = None
    _GPU_CACHE.update({"t": now, "v": val})
    return val


# ── ★ 硬件探测（智能调度的输入）─────────────────────────────────────────

_HW_CACHE: dict = {}


def probe(refresh: bool = False) -> dict:
    """探测本机硬件能力，作为调度决策的输入。结果缓存（硬件不会变）。

    返回（拿不到的字段如实为 None，不猜）：
      cpu_logical / cpu_physical / mem_total_gb / mem_avail_gb
      gpu_name / gpu_mem_gb / gpu_sm / gpu_cc / cuda / torch_version
      disk_read_mbps（不给就 None —— 要实测才填）
    """
    if _HW_CACHE and not refresh:
        out = dict(_HW_CACHE)
        out.update(_live_mem())          # ★ 内存是【活的】：硬件可缓存，可用内存不行
        return out
    info: dict = {
        "cpu_logical": os.cpu_count(),
        "cpu_physical": None,
        "mem_total_gb": None, "mem_avail_gb": None,
        "gpu_name": None, "gpu_mem_gb": None, "gpu_sm": None, "gpu_cc": None,
        "cuda": False, "torch_version": None,
    }
    if psutil is not None:
        try:
            info["cpu_physical"] = psutil.cpu_count(logical=False)
            vm = psutil.virtual_memory()
            info["mem_total_gb"] = round(vm.total / 2 ** 30, 1)
            info["mem_avail_gb"] = round(vm.available / 2 ** 30, 1)
        except Exception:
            pass
    # GPU：先问 torch（快且准），拿不到再退回 nvidia-smi
    try:
        import torch                                    # noqa: PLC0415
        info["torch_version"] = torch.__version__
        if torch.cuda.is_available():
            p = torch.cuda.get_device_properties(0)
            info.update({"cuda": True, "gpu_name": p.name,
                         "gpu_mem_gb": round(p.total_memory / 2 ** 30, 1),
                         "gpu_sm": p.multi_processor_count,
                         "gpu_cc": "sm_%d%d" % (p.major, p.minor)})
    except Exception:
        pass
    if not info["gpu_name"]:
        try:
            pr = subprocess.run(
                ["nvidia-smi", "--query-gpu=name,memory.total,compute_cap",
                 "--format=csv,noheader,nounits"],
                capture_output=True, text=True, timeout=5, encoding="utf-8", errors="replace")
            if pr.returncode == 0 and pr.stdout.strip():
                parts = [x.strip() for x in pr.stdout.strip().splitlines()[0].split(",")]
                info["gpu_name"] = parts[0]
                if len(parts) > 1:
                    try:
                        info["gpu_mem_gb"] = round(float(parts[1]) / 1024, 1)
                    except ValueError:
                        pass
                if len(parts) > 2:
                    info["gpu_cc"] = "sm_" + parts[2].replace(".", "")
        except Exception:
            pass
    _HW_CACHE.update(info)
    return dict(info)


def _live_mem() -> dict:
    """实时内存读数（每次现读，绝不缓存）。拿不到就空 dict。"""
    if psutil is None:
        return {}
    try:
        vm = psutil.virtual_memory()
        sm = psutil.swap_memory()
        return {"mem_total_gb": round(vm.total / 2 ** 30, 1),
                "mem_avail_gb": round(vm.available / 2 ** 30, 1),
                "mem_used_pct": vm.percent,
                "swap_used_gb": round(sm.used / 2 ** 30, 2)}
    except Exception:                                                # noqa: BLE001
        return {}


def ram_budget_gb(frac: float = 0.5, reserve_gb: float = 2.0) -> float:
    """★ 给某任务的内存预算：可用内存 × frac，再留 reserve_gb 兜底。

    frac 用法约定（按风险）：
      0.5  常规批处理（默认）· 0.7 一次性的重活 · 0.3 与其它任务并行时
    """
    avail = _live_mem().get("mem_avail_gb")
    if avail is None:
        return 4.0                       # 读不到内存时给个保守值，不假装很多
    return max(0.5, min(avail * float(frac), avail - reserve_gb))


def recommend_chunk_rows(row_bytes: int, frac: float = 0.5,
                         min_rows: int = 4096, max_rows: int = 1 << 22) -> int:
    """★ 按【单行字节数 + 可用内存】算分块行数（避免一次性申请上百 GB）。

    实测教训：二进制里抽出的串可长达 24 万字符，把 [N, maxlen] padding 成 int64
    一次要 118 GiB —— 分块必须按内存算，不能按固定行数写死。
    """
    if row_bytes <= 0:
        return min_rows
    budget = ram_budget_gb(frac) * (2 ** 30)
    rows = int(budget // max(1, row_bytes))
    return max(min_rows, min(max_rows, rows))


def recommend_workers(kind: str = "scan", cpu_limit: float | None = None,
                      ram_mb_per_worker: float | None = None) -> int:
    """★ 按【任务类型 + 硬件 + 内存】给并行数 —— 取代「写死 24」这种。

    kind 的取值与理由（都基于实测，不是拍脑袋）：
      "io"      文件遍历/读盘/解包：线程就够（GIL 在 I/O 时释放），
                但盘是瓶颈 ⇒ 核数的 1/2，上限 16（再多只会让磁头打转）
      "cpu"     CPU 密集（哈希/解码/统计）：进程池才有效，
                但 Python 进程有启动开销 ⇒ 核数的 3/4，上限 物理核数×2
      "mixed"   读 + 算（最典型：批量解码）：线程池，核数的 3/4
      "light"   极轻量（查索引）：核数 - 1
      "gpu"     GPU 高负载：CPU 只做喂数据 ⇒ 核数 1/4（免得跟 GPU 抢总线）
      "mem"     ★ 内存吃重型（大张量/大字典/百万级对象）：按 ram_mb_per_worker 卡，
                不按核数 —— 否则会把机器打到 swap（64 GB 也就 64 个 1 GB 的工人）
    """
    lim = 80.0 if cpu_limit is None else float(cpu_limit)
    n = cpu_count()
    phys = probe().get("cpu_physical") or max(1, n // 2)
    budget = max(1, int(n * lim / 100.0))
    table = {
        "io":    max(1, min(16, budget // 2)),
        "cpu":   max(1, min(phys * 2, int(budget * 0.75))),
        "mixed": max(1, int(budget * 0.75)),
        "light": max(1, budget - 1),
        "gpu":   max(1, budget // 4),
        "mem":   max(1, int(budget * 0.75)),
    }
    w = table.get(kind, table["mixed"])
    if ram_mb_per_worker:                # ★ 内存硬上限：工人数 × 每人占用 ≤ 预算
        room = ram_budget_gb(0.6) * 1024.0 / float(ram_mb_per_worker)
        w = max(1, min(w, int(room)))
    return w


def gpu_capable(kind: str) -> tuple[bool, str]:
    """★ 某类任务【到底能不能】上 GPU —— 给理由，禁止假承诺。

    诚实清单（2026-09-29 核实）：
      ✅ image_stats   批量像素统计（alpha 判据/饱和度判据/尺寸规整）→ torch 张量
      ✅ image_resize  批量缩放/拼接 → torch interpolate
      ✅ bc_decode     BC1/BC7 块解码 → 可写 GPU kernel（工程量：中等）
      ❌ decompress    解压（zstd/zlib）→ 无 GPU 实现
      ❌ decrypt       解密（AES-ECB）→ 有无，但本项目数据量不是瓶颈
      ✅ hash_batch   ★ 批量哈希（murmur3）**能**上 GPU —— 实测 90 万条 0.73 秒（124 万条/秒），
                     比纯 Python CPU 快 500~1000 倍（toolkit_core/gpu_hash.py，自检硬门禁）
      ❌ hash        单条/逐次调用不值得（每次 H2D/D2H 开销 > 收益）—— 要批就整批搬
      ❌ walk          文件遍历 → 系统调用，GPU 无关
    """
    yes = {
        "image_stats": "numpy 数组 → torch 张量，整批一次算（697~7445 张量级收益明显）",
        "image_resize": "torch.nn.functional.interpolate 批量缩放",
        "bc_decode": "BC 块解码是逐块独立运算，天然适合 GPU（需自写 kernel）",
        "render": "渲染/出图本身可上 GPU",
        "hash_batch": "★ 批量 murmur3：90 万条 0.73 秒（124 万条/秒），见 toolkit_core/gpu_hash.py",
    }
    no = {
        "decompress": "zstd/zlib 无 GPU 实现",
        "decrypt": "AES 有 GPU 实现但本项目瓶颈不在这",
        "hash": "单条/逐次调用不值得（H2D/D2H 开销 > 收益）；★ 批量哈希用 hash_batch 走 GPU",
        "walk": "文件遍历是系统调用，GPU 无关",
    }
    if kind in yes:
        return True, yes[kind]
    return False, no.get(kind, "未归类，按不可上 GPU 处理（宁可不做也不假装）")


# ── ★ 全局策略（main() 从命令行一次性设好，各命令读它）─────────────────

_GLOBAL: dict = {"policy": None, "jobs": None, "gpu_mode": "auto",
                 "throttle": True, "from_cli": False}


def set_global(*, jobs=None, cpu_limit=None, gpu_limit=None,
               gpu_mode: str = "auto", throttle: bool = True) -> LoadPolicy:
    """★ 由 CLI 的 main() 调用一次，之后全项目用 `global_policy()` 取。"""
    pol = LoadPolicy(cpu_limit=80.0 if cpu_limit is None else float(cpu_limit),
                     gpu_limit=80.0 if gpu_limit is None else float(gpu_limit),
                     kinds=("decode",))
    _GLOBAL.update({"policy": pol, "jobs": jobs, "gpu_mode": gpu_mode,
                    "throttle": bool(throttle), "from_cli": True})
    return pol


def global_policy() -> LoadPolicy:
    pol = _GLOBAL.get("policy")
    return pol if pol is not None else LoadPolicy()


def global_jobs(kind: str = "mixed") -> int:
    """★ 各命令取并行数都走这里：显式 --jobs 优先，否则按任务类型智能推荐。

    这样「写死 24」就没了 —— 换台机器（8 核笔记本 / 64 核服务器）自动适配。
    """
    j = _GLOBAL.get("jobs")
    if j in (None, "auto", "", "0"):
        return recommend_workers(kind, global_policy().cpu_limit)
    try:
        return max(1, int(j))
    except (TypeError, ValueError):
        return recommend_workers(kind, global_policy().cpu_limit)


def global_gpu_ok() -> bool:
    """GPU 是否可用且允许用（--gpu off 时一律 False）。"""
    if _GLOBAL.get("gpu_mode") == "off":
        return False
    return bool(probe().get("cuda"))


def global_snapshot() -> dict:
    """供报告/`sched` 命令输出的统一快照。

    ★ `--jobs N` 给了就覆盖【所有档位】—— 快照必须反映实际会生效的值，
    否则 `sched` 显示的是一套、真正跑的是另一套（实测踩到过：`--jobs 8`
    给了，快照仍报自动值 12/18/18/24/6）。
    """
    hw = probe()
    pol = global_policy()
    override = _GLOBAL.get("jobs")
    if override in (None, "auto", "", "0"):
        jobs = {k: recommend_workers(k, pol.cpu_limit)
                for k in ("io", "cpu", "mixed", "light", "gpu", "mem")}
        src = "auto"
    else:
        try:
            n = max(1, int(override))
        except (TypeError, ValueError):
            n = recommend_workers("mixed", pol.cpu_limit)
        jobs = {k: n for k in ("io", "cpu", "mixed", "light", "gpu", "mem")}
        src = "--jobs %d 覆盖" % n
    return {"hardware": hw,
            "ram": _live_mem(),
            "ram_budget_gb": {"常规(0.5)": round(ram_budget_gb(0.5), 1),
                              "重活(0.7)": round(ram_budget_gb(0.7), 1),
                              "并行(0.3)": round(ram_budget_gb(0.3), 1)},
            "cpu_percent": cpu_percent(), "gpu_percent": gpu_percent(),
            "policy": {"cpu_limit": pol.cpu_limit, "gpu_limit": pol.gpu_limit},
            "jobs": jobs, "jobs_source": src,
            "jobs_override": override,
            "gpu_mode": _GLOBAL.get("gpu_mode"),
            "throttle": _GLOBAL.get("throttle"),
            "from_cli": _GLOBAL.get("from_cli")}


# ── 预算 ────────────────────────────────────────────────────────────────

@dataclass
class LoadPolicy:
    cpu_limit: float = 80.0          # 最多用整机 CPU 的百分之几
    gpu_limit: float = 80.0          # 最多用 GPU 的百分之几（解码线不适用，见模块 docstring）
    kinds: tuple = ("decode",)       # 当前任务类型，用于判断 GPU 是否适用

    def workers(self, *, reserve_one: bool = False) -> int:
        """并行 worker 数 = 核数 × cpu_limit%。至少 1。

        reserve_one：再留 1 核给系统（小机器上更稳）。
        """
        n = cpu_count()
        w = int(n * self.cpu_limit / 100.0)
        if reserve_one:
            w -= 1
        return max(1, min(w, n))

    def gpu_applicable(self) -> bool:
        """本任务是否真的用 GPU。解码线不用 ⇒ False。"""
        return any(k in ("render", "screenshot", "glb_gpu") for k in self.kinds)

    def snapshot(self) -> dict:
        return {"cpu_percent": cpu_percent(),
                "gpu_percent": gpu_percent(),
                "cpu_count": cpu_count(),
                "gpu_applicable": self.gpu_applicable(),
                "cpu_limit": self.cpu_limit, "gpu_limit": self.gpu_limit,
                # ★ torch 装了但没人用它 —— 报告里说清楚，避免「有 GPU 就该在跑」的误判
                "torch_present": _has_module("torch")}


@dataclass
class LoadGate:
    """跑到一半的反馈限流：采样实测负载，超上限就 sleep 让路。

    用法：
        gate = LoadGate(policy, every=20000)
        ... 每处理完一条就 gate.tick(i)   # 内部只在 i 达到采样点时动作
    """
    policy: LoadPolicy
    every: int = 20000
    sleep_s: float = 0.25
    samples: list = field(default_factory=list)

    def tick(self, counter: int, *, force: bool = False) -> Optional[dict]:
        if not force and (counter % max(1, self.every) != 0):
            return None
        cpu = cpu_percent()
        gpu = gpu_percent()
        over = (cpu is not None and cpu > self.policy.cpu_limit)
        if self.policy.gpu_applicable() and gpu is not None and gpu > self.policy.gpu_limit:
            over = True
        info = {"at": counter, "cpu": cpu, "gpu": gpu, "over": bool(over)}
        self.samples.append(info)
        if over:
            # duty cycle：睡一小会儿再看，最多连续 8 次，避免长任务把机器占满
            for _ in range(8):
                time.sleep(self.sleep_s)
                cpu2 = cpu_percent()
                if cpu2 is None or cpu2 <= self.policy.cpu_limit:
                    break
        return info

    def summary(self) -> dict:
        if not self.samples:
            return {"samples": 0}
        cpus = [s["cpu"] for s in self.samples if s["cpu"] is not None]
        return {"samples": len(self.samples),
                "cpu_max": max(cpus) if cpus else None,
                "cpu_avg": round(sum(cpus) / len(cpus), 1) if cpus else None,
                "over_limit_times": sum(1 for s in self.samples if s["over"])}
