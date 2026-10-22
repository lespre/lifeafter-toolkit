# -*- coding: utf-8 -*-
r"""GPU 版 murmur3：把「候选 → 哈希 → 撞表」搬上显卡。

## 为什么
CPU 侧是**纯 Python 逐字节** murmur3（`path_fid.murmur3_x86_32`）——
89,892 候选 × 8 变体 ≈ 72 万次哈希就要十几分钟，且没法上 10^8 规模。
GPU 版把一个 [N, L] 字节矩阵 + [S] 个 seed 一次算完，撞表用 `searchsorted`。

## 口径必须与 CPU 一字不差
`fid = (murmur3_x86_32(raw, 0x77777777) << 32) | murmur3_x86_32(raw, 0x66666666)`
`self_check()` 是本模块的硬门禁：GPU 结果与 `path_fid.fid_of` 逐条对照，
不过就别用它出结论。

## 实现要点（踩过的坑）
1. **块循环要按每行真实长度掩码**：padding 用 0 填，尾部 k 值不受影响（0 参与或运算没贡献），
   但「h = rotl(h^kmix)*5+const」这一步**不是恒等**，长度不够的行必须 `torch.where` 回滚，
   否则长行会多消费几轮 padding。
2. 全程 int64 存 32 位无符号值（torch 没有 uint32），加减乘后统一 `& 0xFFFFFFFF`。
3. 分块（chunk）控制显存：N×L 字节矩阵按行切，别一次塞满。
"""
from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import torch

M32 = 0xFFFFFFFF
SEED_HI = 0x77777777
SEED_LO = 0x66666666
C1 = 0xCC9E2D51
C2 = 0x1B873593


def _rotl(x: torch.Tensor, r: int) -> torch.Tensor:
    return ((x << r) | (x >> (32 - r))) & M32


def murmur3_x86_32_batch(padded: torch.Tensor, lengths: torch.Tensor,
                         seeds: torch.Tensor) -> torch.Tensor:
    """padded [N, L] int64（值 0..255，0 填充）· lengths [N] · seeds [S] → [S, N]。"""
    dev = padded.device
    n, lmax = padded.shape
    s = seeds.numel()
    h = seeds.view(s, 1).expand(s, n).clone() & M32          # [S, N]
    nblocks = lmax // 4
    for bi in range(nblocks):
        off = bi * 4
        k = (padded[:, off] | (padded[:, off + 1] << 8)
             | (padded[:, off + 2] << 16) | (padded[:, off + 3] << 24))
        k = ((k * C1) & M32)
        k = _rotl(k, 15)
        k = (k * C2) & M32
        valid = lengths >= (off + 4)                          # ★ 长度不够的行别混进这一块
        h2 = (h ^ k.unsqueeze(0))
        h2 = _rotl(h2, 13)
        h2 = (h2 * 5 + 0xE6546B64) & M32
        h = torch.where(valid.unsqueeze(0), h2, h)
    # 尾块：按每行 end=(len//4)*4 起。★ 必须【先攒成一个 k 再 mix 一次】，
    # 逐字节各自 mix 是错的（长度 1/4/5 恰好重合，长度 2/27 就露馅）。
    end = (lengths // 4) * 4
    max_tail = int((lengths - end).max().item()) if n else 0
    if max_tail:
        any_tail = lengths > end
        k = torch.zeros(n, dtype=torch.int64, device=dev)
        for t in range(max_tail):
            idx = end + t
            has = idx < lengths
            byte = padded.gather(1, idx.clamp(max=lmax - 1).view(-1, 1)).view(-1)
            k = torch.where(has, k | ((byte & 0xFF) << (8 * t)), k)
        k = ((k * C1) & M32)
        k = _rotl(k, 15)
        k = (k * C2) & M32
        h = torch.where(any_tail.unsqueeze(0), h ^ k.unsqueeze(0), h)
    h = h ^ lengths.unsqueeze(0)
    h = h ^ (h >> 16)
    h = (h * 0x85EBCA6B) & M32
    h = h ^ (h >> 13)
    h = (h * 0xC2B2AE35) & M32
    h = h ^ (h >> 16)
    return h & M32


def _encode(texts: Sequence[str], encoding: str = "utf-8",
            normalize_sep: bool = True, lower: bool = False,
            max_len: int = 512) -> Tuple[np.ndarray, np.ndarray]:
    """→ (padded [N,L] uint8 numpy, lengths [N] int64)。

    ★ max_len：超过的**直接丢弃**（返回长度 0，由调用方过滤）。
      踩过坑：二进制里抽出的串可长达 24 万字符，padding 到最大长度会申请上百 GB 内存。
    """
    blobs = []
    for t in texts:
        s = t.replace("/", "\\") if normalize_sep else t
        if lower:
            s = s.lower()
        try:
            b = s.encode(encoding)
        except UnicodeEncodeError:
            b = b""
        blobs.append(b if len(b) <= max_len else b"")
    lens = np.fromiter((len(b) for b in blobs), dtype=np.int64, count=len(blobs))
    lmax = int(lens.max()) if len(lens) else 0
    padded = np.zeros((len(blobs), max(lmax, 1)), dtype=np.uint8)
    for i, b in enumerate(blobs):
        padded[i, :len(b)] = np.frombuffer(b, dtype=np.uint8)
    return padded, lens


def fids_gpu(texts: Sequence[str], *, encoding: str = "utf-8",
             normalize_sep: bool = True, lower: bool = False,
             device: Optional[str] = None, chunk: int = 1 << 21,
             chunk_rows: Optional[int] = None, frac: float = 0.5) -> torch.Tensor:
    """候选 → fid 张量 [N] int64（GPU 算）。

    ★ chunk_rows 默认按【可用内存】自动算（throttle.recommend_chunk_rows）：
      单行 = 最长串的字节数 × 8（int64 张量）——64 GB 机器上本来能开很大，
      但遇到 24 万字符的串就会算出上百 GB，所以必须按内存推，不能写死。
    """
    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    seeds = torch.tensor([SEED_HI, SEED_LO], dtype=torch.int64, device=dev)
    padded, lens = _encode(texts, encoding, normalize_sep, lower)
    if chunk_rows is None:
        try:
            from toolkit_core import throttle as _TH
            row_bytes = max(1, padded.shape[1]) * 8 * 2      # int64 + 中间量
            chunk_rows = _TH.recommend_chunk_rows(row_bytes, frac=frac)
        except Exception:                                        # noqa: BLE001
            chunk_rows = 1 << 16
    out = torch.empty(len(texts), dtype=torch.int64, device=dev)
    for i in range(0, len(texts), chunk_rows):
        p = torch.from_numpy(padded[i:i + chunk_rows].astype(np.int64)).to(dev)
        l = torch.from_numpy(lens[i:i + chunk_rows]).to(dev)
        h = murmur3_x86_32_batch(p, l, seeds)                  # [2, n]
        out[i:i + chunk_rows] = (h[0] << 32) | h[1]
    return out


def lookup_hits(fids: torch.Tensor, targets_sorted: torch.Tensor) -> torch.Tensor:
    """在**已排序**目标张量里查命中 → 返回命中位置索引 [H]（未命中 = -1）。

    ★ 口径：fid 一律用「有符号 int64 的位模式」表示（建表走 `decode_fid_table` →
      `hex_to_i64`；查询走 `fids_gpu`）。两侧同口径时，直接按 int64 比较即等价于比位模式。

    ★★ 别用「异或符号位」那套（我试过，反而更错）：XOR 只把有符号序映射成**无符号**序，
      而 `searchsorted` 仍按有符号比较 ⇒ 一半的命中会丢（实测 149/300）。
      正确做法是**不动值**，只保证表真的有序（有序是 searchsorted 的硬前提）。
    """
    if targets_sorted.numel() == 0:
        return torch.empty(0, dtype=torch.int64, device=fids.device)
    t = targets_sorted
    if t.numel() > 1 and not bool(torch.all(t[1:] >= t[:-1])):
        t = torch.sort(t)[0]                 # 容错：调用方没排好序也不出错
    idx = torch.searchsorted(t, fids)
    idx_c = idx.clamp(max=t.numel() - 1)
    ok = t[idx_c] == fids
    idx = torch.where(ok, idx_c, torch.full_like(idx_c, -1))
    return idx[idx >= 0]


def hex_to_i64(h: str) -> int:
    """fid 十六进制 → **有符号 int64 位模式**（≥2^63 要减 2^64，否则 torch 建张量溢出）。"""
    v = int(h, 16) & 0xFFFFFFFFFFFFFFFF
    return v - (1 << 64) if v >= (1 << 63) else v


def i64_to_hex(v: int) -> str:
    return "%016X" % (int(v) & 0xFFFFFFFFFFFFFFFF)


def self_check(device: Optional[str] = None, n: int = 300) -> dict:
    """★ 硬门禁：GPU 结果 vs CPU `path_fid.fid_of` 逐条对照。不过就别用。"""
    from toolkit_core.path_fid import fid_of
    samples = [r"common\env_map\qiangpi.cube", "ui/damoshi_icon/jijianbiaoqing_icon/ku.png",
               r"黑名单\测试表.csv", r"res\model\bigworld\bigworld_01.mesh",
               "documents/script.py314.lc/com/cdata/weapon_skin_data.py",
               r"a", r"", "x" * 500, r"character\players\r_f_1000\r_f_1000.gim"]
    samples += ["%s_%d\\f%d.dds" % ("dir", i, i) for i in range(max(0, n - len(samples)))]
    cpu = []
    for s in samples:
        try:
            cpu.append(fid_of(s))
        except ValueError:
            cpu.append(None)
    idx = [i for i, v in enumerate(cpu) if v is not None]
    got = fids_gpu([samples[i] for i in idx], device=device).cpu().tolist()
    bad = [{"text": samples[i][:60], "cpu": "%016X" % cpu[i], "gpu": i64_to_hex(g)}
           for i, g in zip(idx, got) if (int(g) & 0xFFFFFFFFFFFFFFFF) != cpu[i]]
    return {"n": len(idx), "ok": not bad, "mismatch": bad[:5]}


def decode_fid_table(names_by_fid: Iterable[str], device: Optional[str] = None):
    """fid 十六进制字符串集合 → 已排序 int64 张量（撞表用）。"""
    dev = device or ("cuda" if torch.cuda.is_available() else "cpu")
    vals = sorted(hex_to_i64(x) for x in names_by_fid if x)
    return torch.tensor(vals, dtype=torch.int64, device=dev)


if __name__ == "__main__":
    import time
    print("CUDA:", torch.cuda.is_available())
    r = self_check()
    print("自检:", r["n"], "条 ｜", "✓ 全对" if r["ok"] else "✗ 有错", r["mismatch"][:2])
    if r["ok"]:
        cand = ["dir%d\\sub%d\\file%d.dds" % (i % 97, i % 53, i) for i in range(900_000)]
        t0 = time.time()
        f = fids_gpu(cand)
        dt = time.time() - t0
        print("★ 90 万候选哈希：%.2f s（%.0f 条/秒）" % (dt, len(cand) / dt))
