# -*- coding: utf-8 -*-
r"""回归测试：Locator 的线程安全（防「并行退化成单线程」重现）。

★ 背景（2026-09-28 实测）：
  `hotfix bundle --png` 跑了 7 分钟 0 落盘、0 CPU、24 线程 24 个 Wait。
  真因 = `Locator._ensure_dir` 慢路径【没有锁】：
  N 个线程同时首次访问同一目录 ⇒ 各自把几万文件的目录列一遍（N 遍）+ 同时写同一缓存文件。
  实测并行度 1.79 核 / 32 核。
  修法 = 双检锁。本测试钉的就是「多个线程并发首次访问，目录只被列一次」。
"""
import sys
import threading
import time
from pathlib import Path

import pytest

PROJ = Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))

from toolkit_core import artifact_locator as AL  # noqa: E402


@pytest.fixture()
def fake_root(tmp_path):
    """造一个假产物根：2 个容器目录，各 200 个 8 位行号文件。

    ★ 目录名必须是 Locator.dir_of 认的【规范化名】（把分隔符换成 __ 且去扩展名）：
      `gres\\0000.gpk` → `gres__0000` ；`res\\ui_01.gpk` → `res__ui_01`
    """
    for c in ("gres__0000", "res__ui_01"):
        d = tmp_path / c
        d.mkdir()
        for i in range(200):
            (d / ("%08d.bin" % i)).write_bytes(b"x" * 8)
    return tmp_path


def test_并发首次访问只列一次目录(fake_root):
    """★ 核心断言：N 个线程同时首次访问，目录列举次数 == 容器数（不是 N×容器数）。

    ★ 计法要点：必须数【真正执行的 iterdir 次数】，不能在锁外面数「谁想建」——
      后者 24 个线程都会 +1（它们都看到缓存里还没有），测的是意图不是事实（我第一版就错在这）。
    """
    loc = AL.Locator(root=fake_root, cache_dir=fake_root / "_cache")
    # 包 Path.iterdir 来数【实际列目录次数】（_ensure_dir 内部就是调它）
    calls = {"iter": 0}
    real_iterdir = Path.iterdir

    def counted_iterdir(self):
        calls["iter"] += 1
        return real_iterdir(self)

    Path.iterdir = counted_iterdir          # type: ignore[assignment]
    try:
        errs = []

        def worker(i):
            try:
                for row in range(200):
                    p = loc.path("gres\\0000.gpk", row)
                    assert p is not None
            except Exception as e:                              # noqa: BLE001
                errs.append("%s: %s" % (type(e).__name__, e))

        ts = [threading.Thread(target=worker, args=(i,)) for i in range(24)]
        t0 = time.time()
        for t in ts:
            t.start()
        for t in ts:
            t.join()
        dt = time.time() - t0
    finally:
        Path.iterdir = real_iterdir         # type: ignore[assignment]

    assert not errs, errs
    # ★ 关键：目录只被列【一次】（不是 24 次）
    assert calls["iter"] == 1, (
        "★ 并发下目录被列了 %d 次（应 ==1）—— 锁没生效" % calls["iter"])
    print("\n  24 线程 × 200 行 用时 %.2fs ｜ 实际列目录 %d 次" % (dt, calls["iter"]))


def test_并发访问不同容器不互相阻塞(fake_root):
    """两个容器并发访问都要成功（锁不能把不同目录也串死）。"""
    loc = AL.Locator(root=fake_root, cache_dir=fake_root / "_cache")
    out = {}

    def worker(name):
        p = loc.path(name, 7)
        out[name] = str(p) if p else None

    ts = [threading.Thread(target=worker, args=("gres\\0000.gpk",)),
          threading.Thread(target=worker, args=("res\\ui_01.gpk",))]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert all(v is not None for v in out.values()), out


def test_dir_of_并发安全(fake_root):
    """dir_of 并发写 _cmap 不能炸。"""
    loc = AL.Locator(root=fake_root, cache_dir=fake_root / "_cache")
    errs = []

    def worker(i):
        try:
            for _ in range(50):
                loc.dir_of("gres\\0000.gpk")
                loc.dir_of("res\\ui_01.gpk")
        except Exception as e:                                  # noqa: BLE001
            errs.append(str(e))

    ts = [threading.Thread(target=worker, args=(i,)) for i in range(16)]
    for t in ts:
        t.start()
    for t in ts:
        t.join()
    assert not errs, errs
