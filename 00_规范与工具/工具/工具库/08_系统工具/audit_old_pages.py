# -*- coding: utf-8 -*-
"""用无头 Chrome 渲染每个页面，判断是不是空壳/报错。"""
import re
import subprocess
import sys

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
BASE = "http://127.0.0.1:8765/"
PAGES = ["workbench.html", "workbench_items.html", "workbench_lottery.html",
         "workbench_status.html", "live_reader.html", "skeletons.html",
         "skeleton_preview.html", "weapon_models.html", "skin3d.html",
         "zhanshen.html", "进展.html"]


def text_of(url: str) -> tuple[int, str]:
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=5000", "--dump-dom", url],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       timeout=90)
    html = p.stdout or ""
    body = html.split("<body", 1)[-1]
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    txt = re.sub(r"<[^>]+>", " ", body)
    txt = re.sub(r"\s+", " ", txt).strip()
    return len(txt), txt[:110]


for pg in PAGES:
    try:
        n, head = text_of(BASE + pg)
        flag = "空壳" if n < 120 else ("偏少" if n < 400 else "有内容")
        print("%-24s %6d 字  %-4s  %s" % (pg, n, flag, head), flush=True)
    except Exception as exc:  # noqa: BLE001
        print("%-24s 失败 %r" % (pg, exc), flush=True)
