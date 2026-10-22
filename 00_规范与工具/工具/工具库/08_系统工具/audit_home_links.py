# -*- coding: utf-8 -*-
"""渲染主页，抽出所有链接，逐个实测（HTTP + 渲染后字数）。"""
import re
import subprocess
import urllib.request

CHROME = r"C:/Program Files/Google/Chrome/Application/chrome.exe"
BASE = "http://127.0.0.1:8765/"


def dom(url: str) -> str:
    p = subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
                        "--virtual-time-budget=5000", "--dump-dom", url],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", timeout=90)
    return p.stdout or ""


def text_len(url: str) -> int:
    html = dom(url)
    body = html.split("<body", 1)[-1]
    body = re.sub(r"<script.*?</script>", " ", body, flags=re.S | re.I)
    body = re.sub(r"<style.*?</style>", " ", body, flags=re.S | re.I)
    return len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).strip())


home = dom(BASE + "index.html")
links = re.findall(r'<a[^>]+href="([^"#]+)"[^>]*>(.*?)</a>', home, flags=re.S)
seen = []
for href, label in links:
    href = href.strip()
    if href.startswith(("http", "//", "mailto:", "javascript:")):
        continue
    name = re.sub(r"<[^>]+>", "", label)
    name = re.sub(r"\s+", " ", name).strip()[:24]
    if href in [h for h, _ in seen]:
        continue
    seen.append((href, name))

print("主页链接 %d 条" % len(seen))
for href, name in seen:
    url = BASE + href.lstrip("/")
    try:
        code = urllib.request.urlopen(url, timeout=20).getcode()
    except Exception as exc:  # noqa: BLE001
        code = getattr(exc, "code", "ERR")
    if code != 200:
        print("%-34s %-16s HTTP %s" % (href, name, code), flush=True)
        continue
    n = text_len(url)
    flag = "空壳" if n < 120 else ("偏少" if n < 400 else "有内容")
    print("%-34s %-16s %6d 字  %s" % (href, name, n, flag), flush=True)
