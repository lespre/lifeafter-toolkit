"""index.html 显示层去"缺/半吊子"（只改文案 ✓ 不动数据与布局 ✓）
   ★ 用 Python 直读写（emoji/反斜杠用 patch 易误判 ✗）
   ★ 同时改：title 提示 / 卡片状态 / 底部计数 / 弹窗文案"""
import re
from pathlib import Path

P = Path(r'E:\la拆包项目\04_站点\web\index.html')
src = P.read_text('utf-8')
BAK = P.with_suffix('.html.bak_before_neutral')
if not BAK.is_file():
    BAK.write_text(src, encoding='utf-8')
    print('  ✓ 备份 .bak_before_neutral')

n = [0]


def rep(old, new, expect=None):
    global src
    c = src.count(old)
    if c:
        src = src.replace(old, new)
        n[0] += c
        print('  ✓ %-28s → %-18s  %d 处' % (old, new, c))
    elif expect:
        print('  · 未出现: %s' % old)
    return c


# ── 状态标签 ──────────────────────────────────────────────
rep('⚠️ 半吊子', '🔸 在优化')
rep('✗ 缺', '🔸 在优化')
rep('✅ 健康', '✅ 已通')
rep('半吊子', '在优化')          # 兜底（无 emoji 前缀的）
rep('✗ ', '🔸 ')

# ── 底部计数「缺 N 条」→「待优化 N」；「缺 0 条」→「已闭环」──────
src = re.sub(r'缺\s*0\s*条', '已闭环', src)
src = re.sub(r'缺\s*(\d+)\s*条', r'在优化 \1 项', src)
n[0] += 1

# ── 提示语「缺什么」→「进度」─────────────────────────────
rep('点开看：现在有什么 / 缺什么', '点开看：能力与进度')
rep('现在有什么 / 缺什么', '能力与进度')
rep('缺什么', '进度')
rep('缺项', '优化项')

# ── 汇总行 ✗ 计数 → 中性 ────────────────────────────────
rep('<span class="s miss">✗ ', '<span class="s warn">🔸 ')

P.write_text(src, encoding='utf-8')
print()
print('  共替换 %d 次 ✓' % n[0])
print('  写回 %d B' % len(src.encode('utf-8')))

# 校验
left = []
for kw in ('半吊子', '缺 '):
    c = src.count(kw)
    if c:
        left.append('%s ×%d' % (kw, c))
print('  残留检查：%s' % ('、'.join(left) if left else '无 ✓'))
for m in re.finditer(r'缺[^<"\n]{0,6}', src):
    print('    残留上下文: %r' % m.group(0))
