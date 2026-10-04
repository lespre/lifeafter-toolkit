"""index.html 第三轮：待修 / 待清理 / 垃圾 等对外不体面的字样（渲染后仍可见 ✗）"""
from pathlib import Path

P = Path(r'E:\la拆包项目\04_站点\web\index.html')
src = P.read_text('utf-8')
n = [0]


def rep(old, new):
    global src
    c = src.count(old)
    if c:
        src = src.replace(old, new)
        n[0] += c
        print('  ✓ %-26s → %-22s  %d 处' % (old[:26], new[:22], c))


rep('待修 / 已修', '优化中 / 已闭环')
rep('待修', '优化中')
rep('垃圾（待清理）', '待整理')
rep('垃圾', '待整理')
rep('待清理', '待整理')
rep('审阅区', '审阅区')
rep('项目健康', '项目状态')
rep('实时刷新不可用：接口返回 404', '离线快照模式')
rep('实时刷新不可用', '离线快照模式')
rep('接口返回 404', '离线快照')

P.write_text(src, encoding='utf-8')
print()
print('  替换 %d 次 ✓  写回 %d B' % (n[0], len(src.encode('utf-8'))))
for kw in ('缺', '半吊子', '待修', '待清理', '垃圾', '404'):
    print('  源码 %-8s %d 次' % (kw, src.count(kw)))
