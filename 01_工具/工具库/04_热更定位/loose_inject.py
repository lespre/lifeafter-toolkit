"""loose_inject.py —— 散文件注入器（把改过的资产送进雷电里的游戏，复用其渲染引擎）
依据（2026-10-02 实测 ✓）：
  · filesystems: <loader name="cloud" opener="sys" root="%DOC_DIR%" />
    ⇒ %DOC_DIR% = /sdcard/Android/data/com.netease.mrzh/files/netease/g66/Documents/
  · Documents/static.json = 散文件清单（{路径: {md5, size}} ✓ 139 条实测）
  · Documents/thd/ · thdext6/ 等 = 清单里那些散文件【真实存在】✓（通道在用 ✓）
  · Documents/file_index/ = 引擎自建索引（会自动重建 ✓ 不用手改）
用法:
  python loose_inject.py push   <本地文件> <包内路径>        # 注入（自动备份 + 改清单）
  python loose_inject.py ls                                # 看当前散文件与清单
  python loose_inject.py restore <包内路径>                 # 回滚
  python loose_inject.py verify                            # 复核清单与磁盘一致
"""
import sys, os, json, hashlib, subprocess, shutil
from pathlib import Path

ADB = r'E:\leidian\LDPlayer14\adb.exe'
DEV = 'emulator-5554'
G = '/sdcard/Android/data/com.netease.mrzh/files/netease/g66'
DOC = G + '/Documents'
TMP = Path(r'C:\emupull_probe')
TMP.mkdir(parents=True, exist_ok=True)
BAK = TMP / 'backup'
BAK.mkdir(parents=True, exist_ok=True)


def sh(cmd, timeout=120):
    r = subprocess.run(cmd, shell=True, capture_output=True, timeout=timeout)
    return r.returncode, (r.stdout or b'').decode('utf-8', 'replace'), (r.stderr or b'').decode('utf-8', 'replace')


def adb(*args, **kw):
    return sh('"%s" -s %s %s' % (ADB, DEV, ' '.join(str(a) for a in args)), **kw)


def md5_of(b):
    return hashlib.md5(b).hexdigest()


def pull(remote, local):
    rc, out, err = adb('pull', '"%s"' % remote, '"%s"' % local)
    return rc == 0 and Path(local).is_file()


def push(local, remote):
    rc, out, err = adb('push', '"%s"' % local, '"%s"' % remote)
    return rc == 0


def get_static():
    """拉 static.json 到本地（并备份一份 ✓）"""
    lp = TMP / 'static.json'
    if not pull(DOC + '/static.json', lp):
        return None
    return json.loads(lp.read_text('utf-8', 'replace'))


def put_static(j):
    lp = TMP / 'static.json'
    lp.write_text(json.dumps(j, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    return push(lp, DOC + '/static.json')


def cmd_ls():
    rc, out, _ = adb('shell', 'ls -la %s | head -40' % DOC)
    print(out)
    j = get_static()
    if j:
        fi = j.get('fileinfo') or {}
        print('static.json 条目 %d ✓' % len(fi))
        for k, v in list(fi.items())[:12]:
            print('   %-46s size=%-9s md5=%s' % (str(k)[:46], v.get('size'), str(v.get('md5'))[:12]))


def cmd_push(local, rel):
    rel = rel.replace('\\', '/').lstrip('/')
    src = Path(local)
    if not src.is_file():
        print('✗ 源文件不在：%s' % src); return 1
    data = src.read_bytes()
    print('① 源 %s（%d B · md5=%s）' % (src.name, len(data), md5_of(data)[:12]))

    # ② 拉清单并备份原文件
    j = get_static()
    if j is None:
        print('✗ 拉不到 static.json'); return 1
    fi = j.setdefault('fileinfo', {})
    old = fi.get(rel)
    remote = DOC + '/' + rel
    bakdir = BAK / rel.replace('/', '__')
    if old is not None:
        pull(remote, str(bakdir))
        print('② 原文件已备份 → %s（size=%s md5=%s）' % (bakdir.name, old.get('size'), str(old.get('md5'))[:12]))
        (BAK / (rel.replace('/', '__') + '.meta.json')).write_text(
            json.dumps(old, ensure_ascii=False), encoding='utf-8')
    else:
        print('② 清单里没有这条 ⇒ 新文件（若是全新路径，引擎可能不认；建议用清单内路径 ✓）')

    # ③ 推文件
    rc, out, err = adb('shell', 'mkdir -p', '"%s"' % str(Path(remote).parent).replace('\\', '/'))
    if not push(str(src), remote):
        print('✗ 推送失败：%s' % err[:120]); return 1
    print('③ 已推送到 %s ✓' % remote)

    # ④ 更新清单
    fi[rel] = {'md5': md5_of(data), 'size': len(data)}
    if not put_static(j):
        print('✗ 清单回写失败'); return 1
    print('④ static.json 已更新（md5=%s size=%d）✓' % (md5_of(data)[:12], len(data)))
    print()
    print('★ 下一步：重启游戏 ⇒ 生效即说明散文件通道通 ✓')
    print('  回滚：python %s restore %s' % (Path(__file__).name, rel))
    return 0


def cmd_restore(rel):
    rel = rel.replace('\\', '/').lstrip('/')
    b = BAK / rel.replace('/', '__')
    m = BAK / (rel.replace('/', '__') + '.meta.json')
    if not b.is_file():
        print('✗ 没有备份：%s' % b); return 1
    remote = DOC + '/' + rel
    if not push(str(b), remote):
        print('✗ 回滚推送失败'); return 1
    j = get_static()
    fi = j.setdefault('fileinfo', {})
    if m.is_file():
        fi[rel] = json.loads(m.read_text('utf-8'))
    put_static(j)
    print('✓ 已回滚 %s（清单同步 ✓）' % rel)
    return 0


def cmd_verify():
    j = get_static()
    if not j:
        print('✗ 拉不到 static.json'); return 1
    fi = j.get('fileinfo') or {}
    print('清单 %d 条 ✓' % len(fi))
    miss = 0
    for k, v in fi.items():
        rc, out, _ = adb('shell', '[ -e "%s/%s" ] && echo Y || echo N' % (DOC, k))
        if 'Y' not in out:
            print('   ✗ 磁盘上没有：%s' % k); miss += 1
    print('磁盘缺失 %d 条' % miss)
    return 0


if __name__ == '__main__':
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit(0)
    c = a[0]
    if c == 'ls':
        sys.exit(cmd_ls())
    elif c == 'push' and len(a) >= 3:
        sys.exit(cmd_push(a[1], a[2]))
    elif c == 'restore' and len(a) >= 2:
        sys.exit(cmd_restore(a[1]))
    elif c == 'verify':
        sys.exit(cmd_verify())
    else:
        print(__doc__); sys.exit(0)
