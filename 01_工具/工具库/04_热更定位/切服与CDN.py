#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""切服与CDN.py — 明日之后 版本清单 / CDN / 切服工具（只读为主）

用法:
  # 1) 列出所有已知清单的版本（对照各服）
  python 切服与CDN.py list

  # 2) 取某份清单并保存
  python 切服与CDN.py fetch npk_version_android4_playertest [--out DIR]

  # 3) 监控：与上次快照比，报告哪份清单变了（测试服更新预警）
  python 切服与CDN.py watch [--snap FILE]

  # 4) 生成"切到目标服"的待推文件（**只生成到本地目录，不碰客户端**）
  python 切服与CDN.py gen --line playertest --tier android --out DIR
      tier: pc | android      line: release | playertest | futuretest

  # 5) 判断某个客户端目录属于哪条线（读 update.ini / cloud.json）
  python 切服与CDN.py which <客户端根目录 或 Documents 目录>

说明:
  · 网络部分只做【只读 GET】（服务端公开内容 ✓ 无风险）
  · gen 只写本地文件；推送/改客户端由人来决定（见 00_治理/规范/服务器切换与CDN体系_20261002.md §3）
"""
import argparse
import json
import ssl
import sys
import urllib.request
from pathlib import Path

CDN = 'https://g66.update.netease.com/pl/'
GPH = 'https://g66.gph.netease.com/'
DRPF = 'https://drpf-g66.proxima.nie.netease.com/'

TIERS = {'pc': 'newpc4', 'android': 'android4'}
LINES = ['', '_playertest', '_futuretest', '_playertest_kol_zy', '_playertest_bisai']

# 已实测可取到的（作为对照基线；watch 用这个列表）
# ★ tier 是 TIERS 的键（'pc' / 'android'），不是清单家族名
KNOWN = [('pc', s) for s in LINES] + [('android', s) for s in LINES]

_ctx = ssl.create_default_context()
_ctx.check_hostname = False
_ctx.verify_mode = ssl.CERT_NONE


def http_get(url, timeout=40):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout, context=_ctx) as r:
        return r.status, r.read()


def manifest_name(tier, line):
    sfx = line if line.startswith('_') or line == '' else ('_' + line)
    return 'npk_version_%s%s' % (TIERS[tier], sfx)


def fetch(name, quiet=False):
    try:
        st, data = http_get(CDN + name)
    except Exception as e:
        if not quiet:
            print('  ✗ %-40s %s' % (name, str(e)[:60]))
        return None
    try:
        o = json.loads(data.decode('utf-8'))
    except Exception:
        o = None
    if not quiet:
        ver = o.get('version') if isinstance(o, dict) else '?'
        svn = o.get('svn_branch') if isinstance(o, dict) else '?'
        print('  ✓ %-40s %9d B  version=%-38s svn=%s' % (name, len(data), ver, svn))
    return (len(data), o, data)


def cmd_list(args):
    print('══ 已知清单对照（%s）══' % CDN)
    for tier, sfx in KNOWN:
        fetch(manifest_name(tier, sfx))
    print()
    print('（后缀含义：空=正式服 · _playertest=玩家测试 · _futuretest=未来测 ·'
          ' _playertest_kol_zy=KOL测 · _playertest_bisai=比赛测）')


def cmd_fetch(args):
    r = fetch(args.name)
    if not r:
        return 1
    out = Path(args.out or '.')
    out.mkdir(parents=True, exist_ok=True)
    p = out / args.name
    p.write_bytes(r[2])
    print('已保存 %s (%d B)' % (p, r[0]))
    return 0


def cmd_watch(args):
    snap_p = Path(args.snap or (Path(__file__).with_suffix('').as_posix() + '_snap.json'))
    cur = {}
    for tier, sfx in KNOWN:
        n = manifest_name(tier, sfx)
        r = fetch(n, quiet=True)
        cur[n] = None if not r or not isinstance(r[1], dict) else {
            'version': r[1].get('version'), 'revision': r[1].get('revision'),
            'size': r[0],
        }
    old = {}
    if snap_p.is_file():
        try:
            old = json.loads(snap_p.read_text('utf-8'))
        except Exception:
            old = {}
    changed = []
    for k, v in cur.items():
        if k not in old:
            continue
        if old[k] != v:
            changed.append((k, old[k], v))
    print('══ 监控报告 ══')
    if not old:
        print('  （首次运行，已建快照 ✓ 下次起报告变化）')
    elif not changed:
        print('  ✓ 全部清单均未变化')
    else:
        for k, o, n in changed:
            print('  ★ %s' % k)
            print('      旧: %s' % (o and o.get('version')))
            print('      新: %s' % (n and n.get('version')))
    snap_p.write_text(json.dumps(cur, ensure_ascii=False, indent=1), encoding='utf-8')
    print('  快照 → %s' % snap_p)
    return 0


def cmd_gen(args):
    tier, line = args.tier, args.line
    n = manifest_name(tier, line)
    r = fetch(n)
    if not r or not isinstance(r[1], dict):
        print('✗ 取不到 %s，无法生成' % n)
        return 1
    ver = str(r[1].get('version') or '')          # 形如 20260923_164313_playertest_android
    parts = ver.split('_')
    if len(parts) < 2 or len(parts[0]) != 8:
        print('✗ version 格式意外：%s' % ver)
        return 1
    ymd, hm = parts[0], parts[1]                   # 20260923 / 164313
    tag = '%s%s' % (ymd[2:], hm[:3])               # 260923164  （与 update.ini 的写法一致）
    out = Path(args.out or '.')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'update.ini').write_bytes(
        ('[Setting]\nversion = 0.%s.1\nsubversion = 0\n' % tag).encode('utf-8'))
    cloud = {
        "fname_case_sensitive": 0, "update_mode": 0, "downloader_connect_num": 2,
        "downloader_running_num": 64, "downloader_timeout": 2000,
        "combo_patch_dir": "cloudfile_%s/" % tag,
        "combo_patch_path": "temp_cache/res.zip",
        "zipres_repo_enable": True, "enable_namehash_check": True,
    }
    (out / 'cloud.json').write_text(json.dumps(cloud, indent=1), encoding='utf-8')
    if line == 'playertest':
        (out / 'download_playertest_patch').write_bytes(b'1')   # ★ 1 字节开关
    (out / 'MANIFEST.txt').write_text(
        '清单=%s\nversion=%s\nrevision=%s\ncombo_patch_dir=cloudfile_%s/\n'
        % (n, ver, r[1].get('revision'), tag), encoding='utf-8')
    print('══ 已生成待推文件 → %s ══' % out)
    print('   update.ini   version = 0.%s.1' % tag)
    print('   cloud.json   combo_patch_dir = cloudfile_%s/' % tag)
    if line == 'playertest':
        print('   download_playertest_patch  (1 字节 "1")   ← ★ 切服开关')
    print()
    print('   推送（人工确认后执行；改客户端有协议风险，见规范文档 §6）：')
    print('     adb push %s/update.ini    <DOC>/' % out.as_posix())
    print('     adb push %s/cloud.json    <DOC>/' % out.as_posix())
    if line == 'playertest':
        print('     adb push %s/download_playertest_patch <DOC>/' % out.as_posix())
    return 0


def cmd_which(args):
    root = Path(args.path)
    doc = root if root.name.lower() == 'documents' else (root / 'Documents')
    if not doc.is_dir():
        print('✗ 找不到 Documents 目录：%s' % doc)
        return 1
    print('══ %s ══' % doc)
    up = doc / 'update.ini'
    cj = doc / 'cloud.json'
    fl = doc / 'download_playertest_patch'
    if up.is_file():
        print('   update.ini      : %s' % up.read_text('utf-8', 'replace').replace('\n', ' ').strip())
    if cj.is_file():
        try:
            o = json.loads(cj.read_text('utf-8'))
            print('   combo_patch_dir : %s' % o.get('combo_patch_dir'))
        except Exception:
            pass
    print('   playertest 标记 : %s' % ('★ 有（测试服线）' if fl.is_file() else '✗ 无'))
    print('   ⇒ 判据见规范文档 §2/§5')
    return 0


def main():
    ap = argparse.ArgumentParser(description='明日之后 版本清单 / CDN / 切服工具')
    sub = ap.add_subparsers(dest='cmd')

    p = sub.add_parser('list', help='列出所有已知清单的版本')
    p.set_defaults(func=cmd_list)

    p = sub.add_parser('fetch', help='取一份清单')
    p.add_argument('name')
    p.add_argument('--out', default=None)
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser('watch', help='与快照比对，报告变化（测试服更新预警）')
    p.add_argument('--snap', default=None)
    p.set_defaults(func=cmd_watch)

    p = sub.add_parser('gen', help='生成切服待推文件（只写本地）')
    p.add_argument('--tier', choices=list(TIERS), default='android')
    p.add_argument('--line', choices=['release', 'playertest', 'futuretest'], default='playertest')
    p.add_argument('--out', default=None)
    p.set_defaults(func=cmd_gen)

    p = sub.add_parser('which', help='判断某客户端属于哪条线')
    p.add_argument('path')
    p.set_defaults(func=cmd_which)

    args = ap.parse_args()
    if not getattr(args, 'func', None):
        ap.print_help()
        return 2
    return args.func(args) or 0


if __name__ == '__main__':
    sys.exit(main())
