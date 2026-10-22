# -*- coding: utf-8 -*-
"""
announce_calibrate.py —— 官方更新公告校准源抓取（mrzh.163.com）

背景（27.104）：conf 期次表行序≠时间序（幽灵行/漏登记），期次↔时间窗的权威外部源
=官方每周更新公告「限定芯片/核芯」活动段（含精确起止日期 + 当期芯片前 2 名名单）。
本工具把公告流抓成结构化锚表，供期次时间校准/名单指纹匹配复用（核芯 72 期、芯片 30 期、
载具期同法）。

用法：
  python tools/announce_calibrate.py --kw 芯片 --pages 6          # 默认输出到 stdout
  python tools/announce_calibrate.py --kw 核芯 --pages 6 --json -o data/external_refs/announce_nucleus.json

注意：官网 news/update 列表只保留 ~2 年（2024-06 起）；更早（2023-05~2024-05）已清档
（key1-8 期需高手游/玩家转载）；2025-07 起公告不再宣传芯片活动（需游戏内记录）。抓取=curl，
无第三方依赖；每页 ~10 条公告，全量约 10-12 页。
"""
import argparse
import html as ihtml
import json
import re
import subprocess
import sys
import time

BASE = "https://mrzh.163.com/news/update"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
SERVER = r"(经典服|简单生存专服|简单生存服|会员甄选服)"


def fetch(url: str) -> str:
    for _ in range(2):
        try:
            r = subprocess.run(["curl", "-s", "-m", "25", url, "-A", UA],
                               capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=30)
            if r.stdout:
                return r.stdout
        except Exception:
            pass
        time.sleep(1)
    return ""


def list_urls(max_pages: int):
    urls = []
    for p in [""] + [f"_{i}" for i in range(2, max_pages + 1)]:
        h = fetch(f"{BASE}/index{p}.html")
        got = re.findall(r'href="(https://mrzh\.163\.com/news/update/\d{8}/[^"]+\.html)"', h)
        if not got:
            break
        urls += got
    seen, uniq = set(), []
    for u in urls:
        if u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq


def extract(url: str, kw: str = "芯片"):
    """提取一篇公告的：标题日期/服务器 + 活动段列表（kw 关键词匹配段落文本）。"""
    h = fetch(url)
    if not h:
        return None
    txt = ihtml.unescape(re.sub(r"<[^>]+>", "", h))
    title = re.search(rf"(\d{{4}}年\d{{1,2}}月\d{{1,2}}日{SERVER}[^公告]{{0,6}}更新公告)", txt)
    date = re.search(r"(\d{4})-(\d{2})-(\d{2})", url.split("/")[-2] + "000000")  # URL 日期目录
    segs = []
    for m in re.finditer(rf"([^。\n]{{0,14}}(?:{kw}|限定(?:芯片|核芯))[^。\n]{{0,240}})", txt):
        segs.append(m.group(1).strip())
    dm = re.search(r"/update/(\d{8})/", url)
    date = f"{dm.group(1)[:4]}-{dm.group(1)[4:6]}-{dm.group(1)[6:8]}" if dm else "?"
    return {"date": date, "title": title.group(0) if title else "", "url": url, "segments": segs[:4]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kw", default="芯片", help="关键词：芯片/核芯/载具（默认 芯片）")
    ap.add_argument("--pages", type=int, default=14, help="抓列表页数（每页约 10 条公告，默认 14≈覆盖官网保留的 ~2 年）")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("-o", "--out", default=None, help="输出 JSON 文件（默认 stdout）")
    args = ap.parse_args()

    print(f"抓取公告列表（{args.pages} 页）…", file=sys.stderr)
    urls = list_urls(args.pages)
    print(f"共 {len(urls)} 篇，逐个提取「限定{args.kw}」段…", file=sys.stderr)
    hits = []
    for i, u in enumerate(urls):
        rec = extract(u, args.kw)
        if not rec:
            continue
        segs = [s for s in rec["segments"] if args.kw in s]
        if segs:
            rec["segments"] = segs
            hits.append(rec)
        if (i + 1) % 20 == 0:
            print(f"  …{i + 1}/{len(urls)}", file=sys.stderr)
    hits.sort(key=lambda r: r["date"])

    out = {"source": f"{BASE}/", "fetched_at": time.strftime("%Y-%m-%d %H:%M"),
           "kw": args.kw, "announcements": hits}
    if args.out:
        import pathlib
        pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        pathlib.Path(args.out).write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"已写 {args.out}（{len(hits)} 条命中）")
    else:
        print(json.dumps(out, ensure_ascii=False, indent=1) if args.json else
              "\n".join(f"{r['date']} | {r['title'][:34]} | {' || '.join(r['segments'])[:120]}" for r in hits))


if __name__ == "__main__":
    main()
