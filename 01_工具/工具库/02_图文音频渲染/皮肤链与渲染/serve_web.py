"""★ 站点服务（放项目里 ✓ 不放 scratch ⇒ 不被清 ✗）
用法: python serve_web.py [port]     默认 8770
做法: 先探活，没活才起；nohup 式后台 + 日志落 03_执行/90_临时/。
"""
import socket
import subprocess
import sys
import time
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8770
WEB = Path(r'E:\la拆包项目\04_站点\web')
LOG = Path(r'E:\la拆包项目\03_执行\90_临时\web_%d.log' % PORT)
PY = r'E:\la拆包项目\.venv\Scripts\python.exe'


def alive():
    s = socket.socket()
    s.settimeout(1.5)
    try:
        s.connect(('127.0.0.1', PORT))
        return True
    except Exception:
        return False
    finally:
        s.close()


def main():
    if alive():
        print('  已在监听 :%d ✓' % PORT)
        return 0
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, 'a', encoding='utf-8') as lg:
        subprocess.Popen(
            [PY, '-m', 'http.server', str(PORT), '--bind', '0.0.0.0',
             '--directory', str(WEB)],
            stdout=lg, stderr=lg,
            creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0)
            | getattr(subprocess, 'DETACHED_PROCESS', 0))
    for _ in range(20):
        time.sleep(0.5)
        if alive():
            print('  已启动 ✓ http://127.0.0.1:%d/  (log %s)' % (PORT, LOG.name))
            return 0
    print('  ✗ 启动失败，看 %s' % LOG)
    return 1


if __name__ == '__main__':
    sys.exit(main())
