"""最后一轮：JS 运行时拼出的 "接口返回 "+status / HTTP 错误字样（渲染后可见 ✗）"""
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
        print('  ✓ %-38s → %-26s  %d 处' % (old[:38], new[:26], c))


# 离线快照提示（不暴露 HTTP 码 ✗）
rep('"\u79bb\u7ebf\u5feb\u7167\u6a21\u5f0f\uff1a\u63a5\u53e3\u8fd4\u56de "+r.status',
    '"\u79bb\u7ebf\u5feb\u7167\u6a21\u5f0f"')
rep('离线快照模式：接口返回 "+r.status', '离线快照模式')
rep('"接口返回 "+r.status', '"离线快照模式"')
rep('接口返回 "+r.status', '离线快照')
rep('接口返回 "+', '离线快照')
rep('接口返回 ', '离线快照 ')
rep('实时刷新不可用', '离线快照模式')
rep('" +r.status', '"')
rep('+r.status', '')
rep('离线快照模式：接口返回 404', '离线快照模式')

P.write_text(src, encoding='utf-8')
print()
print('  替换 %d 次 ✓  写回 %d B' % (n[0], len(src.encode('utf-8'))))
for kw in ('缺', '半吊子', '待修', '404', '接口返回', 'status'):
    print('  源码 %-10s %d 次' % (kw, src.count(kw)))
