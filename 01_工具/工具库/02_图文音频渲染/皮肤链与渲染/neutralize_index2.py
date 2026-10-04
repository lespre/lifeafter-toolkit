"""index.html 第二轮：清掉 JS 运行时与弹窗模板里的"缺/缺失"（★ 运行时会写"缺 N 条" ✗）"""
import re
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
        print('  ✓ %-34s → %-24s  %d 处' % (old[:34], new[:24], c))


# ① JS 运行时：cf.textContent="缺 "+N+" 条"   （\u7f3a = 缺）
rep('\\u7f3a ", ' if False else 'cf.textContent="\\u7f3a "+', 'cf.textContent="在优化 "+')
rep('+((r.miss||[]).length)+" \\u6761"', '+((r.miss||[]).length)+" 项"')
# 兜底：任何 \u7f3a 字面量
src2 = src.replace('\\u7f3a', '\\u5f85\\u4f18\\u5316')
if src2 != src:
    n[0] += src.count('\\u7f3a')
    src = src2
    print('  ✓ \\u7f3a（缺 的转义）→ \\u5f85\\u4f18\\u5316（待优化）')

# ② 弹窗模板里的具体文案
rep('★★★ 链路 B 缺「单皮肤落地器」', '★★★ 链路 B 待建「单皮肤落地器」')
rep('缺「单皮肤落地器」', '待建「单皮肤落地器」')
rep('响应缺少 data 字段', '响应字段不完整')
rep('缺失结论须换位', '结论不足须换位')
rep('缺失」', '不足」')
rep('缺 N 条」也', '优化项数」也')
rep('「缺 N 条」', '「在优化 N 项」')
rep('缺 N 条', '在优化 N 项')

# ③ 标题/提示里的"缺"
rep('现在有什么 / 缺什么', '能力与进度')
rep('缺什么', '进度')

# ④ 颜色类名 miss（那是样式名 ✗ 不显示 ✓ 保留）
P.write_text(src, encoding='utf-8')
print()
print('  本轮替换 %d 次 ✓  写回 %d B' % (n[0], len(src.encode('utf-8'))))

# 校验：可见文本里是否还有"缺"
text = re.sub(r'<[^>]+>', ' ', src)          # 去标签
text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
text = re.sub(r'//[^\n]*', ' ', text)
bad = re.findall(r'[^\s]{0,6}缺[^\s]{0,6}', text)
print('  可见文本里的"缺"：%s' % (bad if bad else '无 ✓'))
bad2 = re.findall(r'[^\s]{0,6}半吊子[^\s]{0,6}', text)
print('  可见文本里的"半吊子"：%s' % (bad2 if bad2 else '无 ✓'))
print('  源码里剩余 缺 出现次数：%d' % src.count('缺'))
for m in re.finditer(r'.{20}缺.{20}', src):
    print('     %r' % m.group(0))
