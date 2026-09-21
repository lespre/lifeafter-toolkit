#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fashion_display_name_parser v2 — 时装外观表 CHS 富文本展示名解析器（工具库可复用）

形态覆盖（2026-09-03 全池实证 + 用户质疑驱动）：
  富文本:  #cRRGGBB文字#n / 名。#r描述 / 名(永久款)。#r描述
  部件:   名-头饰 / 名-衣服 / 名-套装（PARTS 白名单）
  时限:   名-头饰-N天 / 名-N天 / 名-头饰(N天) / 名-头饰(N天时限/款/日款) / (永久款)
  空格:   名 空格 色系/系列尾（两小无猜 少时凌霄 / 假面骑士 空我 / B站新年限定 - 衣服（30天））
  双括号脏: 三载之伴-衣服((30天)（容忍多余开括号）
v2 变更：
  - raw=名字段（#r/句号截断后），desc 不再混入 raw
  - 拒词缩减为硬信号（路径/内部码/纯色名/desc 模板开头），避免误杀 限定/专属/纪念 等合法名字成分
  - 形态优先匹配（宽松空格、双括号容错）
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional

PARTS = ["头饰", "头发", "发型", "发饰", "衣服", "上衣", "下装", "裤子", "鞋子", "面饰",
         "眼镜", "口罩", "背包", "背饰", "披风", "挂件", "腰饰", "手套", "投影", "套装",
         "帽子", "裙", "手持", "脸饰", "纹身"]
_P = "|".join(sorted(set(PARTS), key=len, reverse=True))
_MARK = r"(?:永久款?|永久|(?:30|7|14|3|5|1)天(?:时限|款)?|(?:30|7|1|3|5|14)日款)"
_CN = r"[一-龥A-Za-z0-9·・★&+×]"
_NAME_LEN = 20

# 硬拒信号（出现在名字段即整条非名字）
_HARD_BAD = (
    "character/", "ui/", "icon_", "b_f_", "b_m_", "h_f_", "h_m_", "cloth_", "5001_",
    ".gim", ".png", "light", "man_name", ";", "：", "。", "，", "！", "？",
)
# desc 模板句开头（这些是说明句不是名字）
_DESC_OPEN = re.compile(
    r"^(一件\d+天时限的时装|新款|拥有|还原|这是|可获得|回收|在下赛季|解锁动作|时装头饰|时装衣服|时装套装|主题限定背包|系列时装|主题系列时装|深海主题|联动限定物品|联动限定外观|联动限定纪念)"
)
# v3: 句子式 desc 特征词——这些词出现在纯名(无部件/时限标记)形态即判定为描述句而非名字。
# 注意: 只对 "plain/paren_mark/spaced(无部件)" 形态生效; 带部件/时限的真名(如 武士意志-衣服)豁免。
_SENTENCE_WORDS = (
    "也许可以", "请不要", "不要", "想要", "抵挡", "侵害", "逃不过", "恶作剧", "吃遍",
    "飘落", "屹立", "守护城市", "全部", "就像", "洒在", "所穿着", "为灵感", "的元素",
    "的纪念衫", "请求", "才美味", "撞进", "的海风", "海水", "方舟市", "远星时光",
    "闪烁的", "小小的脑袋", "大大的", "的疑惑", "的惊叹", "气死本宝宝", "背包外形",
    "特别定制", "为迎接", "为方舟", "呜啊", "嘻嘻", "没病", "糟糕糟糕", "我超凶的",
    "燃烧吧", "密码到底是什么", "我记住你了吗", "尽情释放", "恶魔评选", "想恶作剧",
    "撕裂一切", "无尽深海", "热情是绝杀", "规则是给", "你只会祈求", "是海洋神秘",
    "正面", "看", "为了武士", "不要被", "新款", "的意志", "嘘", "哈哈", "嘿嘿",
    "真的吗", "原来", "其实", "反正", "终于", "居然", "快来", "去吧", "加油",
)
# v3: 长度>=13 的纯名需要以物品词结尾才可信（否则视为长句残头，如"也许可以抵挡…侵害"20字）
_ITEM_TAIL = ("背包", "衣服", "头饰", "时装", "外套", "挂件", "面具", "发饰", "套装",
              "纪念衫", "裙子", "长裙", "帽子", "伞", "制服", "盔甲", "战甲", "装备", "装置")
_PLAIN_LEN_HARD = 12  # 纯名超过此长度且不以物品词结尾 -> desc 句
# 纯色/尾词（单独出现不是时装名）
_COLOR_ONLY = {"天空蓝", "灵动黄", "不羁黄", "生机绿", "清新绿", "纯情粉", "萌动粉", "静墨红",
               "柔情白", "萌萌白", "酷墨黑", "象牙塔", "桃花满枝", "青花问瓷", "少时凌霄",
               "晨光翠茑", "蓬勃海棠", "青春罗兰"}

_CN_ONLY = re.compile(rf"^{_CN}{{1,{_NAME_LEN}}}$")


@dataclass(frozen=True)
class DisplayName:
    base: str
    part: Optional[str]
    duration_days: Optional[int]
    flavor: Optional[str]
    raw: str
    kind: str

    @property
    def display(self) -> str:
        if self.flavor:
            return f"{self.base} {self.flavor}"
        return self.base + (f"-{self.part}" if self.part else "")


def strip_rich(text: str) -> str:
    """剥 #cRRGGBB/#n/#r 与描述句（句号/！/#r 后截断），返回名字段。"""
    s = re.sub(r"#c[0-9a-fA-F]{6,8}", "", text).replace("#n", "")
    s = re.split(r"[。！？!?;\n]|#r", s, maxsplit=1)[0]
    return re.sub(r"\s+", " ", s).strip()


def _dur_of(mark: Optional[str]) -> Optional[int]:
    if not mark:
        return None
    m = re.search(r"(\d+)", mark)
    return int(m.group(1)) if m else None


def _reject(head: str) -> bool:
    if not head or len(head) > 26 or not re.search(r"[一-龥]", head):
        return True
    for bad in _HARD_BAD:
        if bad in head:
            return True
    if _DESC_OPEN.match(head):
        return True
    if head in _COLOR_ONLY:
        return True
    # 残留内部码（纯英文数字下划线）
    if re.fullmatch(r"[A-Za-z0-9_\- ]+", head):
        return True
    return False


def parse_display(text: str) -> Optional[DisplayName]:
    dn = _parse_display_raw(text)
    if dn is None:
        return None
    # v3 desc 防护：只对无部件标记形态（plain/spaced/paren_mark/part_dur）生效，
    # 带部件真名（如 武士意志-衣服）豁免——desc 句子不会长成"名-部件"形态。
    if dn.part is None and _looks_sentence(dn.raw, text, dn):
        return None
    return dn


def _desc_tail(text: str) -> bool:
    """原始文本在名字段截断点（。！？#r 等）之后是否还有实质内容。

    '呜啊！吓你一跳！' -> True（感叹号后是句子）
    '深渊漫步' -> False
    '也许可以抵挡…侵害。' -> False（句号即结尾，需词表兜底）
    """
    s = re.sub(r"#c[0-9a-fA-F]{6,8}", "", text).replace("#n", "").replace("#f(5)", "")
    parts = re.split(r"[。！？!?;\n]|#r", s, maxsplit=1)
    return len(parts) > 1 and bool(parts[1].strip())


def _looks_sentence(head: str, text: str, dn: DisplayName) -> bool:
    """无部件形态的 desc 句三重判定：句子词 / 惊叹截断残头 / 超长纯名。"""
    # 1) 句子特征词（desc 语气/结构词）
    for w in _SENTENCE_WORDS:
        if w in head:
            return True
    # 2) 惊叹/句号后还有内容 -> 名字段是句子残头（呜啊←'呜啊！吓你一跳！'）
    if _desc_tail(text):
        return True
    # 3) 纯名超长且不以物品词结尾（也许可以抵挡…侵害 20字）
    if dn.kind == "plain" and len(head) > _PLAIN_LEN_HARD and not head.endswith(_ITEM_TAIL):
        return True
    return False


def _parse_display_raw(text: str) -> Optional[DisplayName]:
    head = strip_rich(text)
    if _reject(head):
        return None
    h = head
    # 双括号容错：名-部件((30天) -> 名-部件(30天)
    h = re.sub(r"([)）]?)[（(]([（(])", r"\1\2", h)
    h = re.sub(r"([（(])[（(]", r"\1", h)

    # 形态1：名-部件(款型) / 名-部件-N天 / 名-部件（宽松空格）
    m = re.match(rf"^({_CN}{{1,{_NAME_LEN}}})\s*-\s*({_P})\s*[（(]?\s*({_MARK})\s*[)）]?$", h)
    if not m:
        m = re.match(rf"^({_CN}{{1,{_NAME_LEN}}})\s*-\s*({_P})\s*-\s*(30|7|14|3|5|1)天$", h)
    if m:
        dur = _dur_of(m.group(3)) if m.lastindex >= 3 and m.group(3) else None
        return _mk(m.group(1), m.group(2), dur, None, head, "part")
    # 形态1b：B站新年限定 - 衣服（30天）（base 含空格）
    m = re.match(rf"^((?:{_CN}| ){{1,{_NAME_LEN}}})\s*-\s*({_P})\s*[（(]\s*({_MARK})\s*[)）]$", h)
    if m and " " in m.group(1):
        return _mk(m.group(1), m.group(2), _dur_of(m.group(3)), None, head, "part")
    # 形态2：名-部件
    m = re.match(rf"^({_CN}{{1,{_NAME_LEN}}})-({_P})$", h)
    if m:
        return _mk(m.group(1), m.group(2), None, None, head, "part")
    # 形态2b：名-N天（无部件时限版，如 帝皇铠甲-14天 / B站限定-30天）
    m = re.match(rf"^({_CN}{{1,{_NAME_LEN}}})-(30|7|14|3|5|1)天$", h)
    if m:
        return _mk(m.group(1), None, int(m.group(2)), None, head, "part_dur")
    # 形态3：名(款型)（无部件）
    m = re.match(rf"^({_CN}{{1,{_NAME_LEN}}})[（(]({_MARK})[)）]$", h)
    if m:
        return _mk(m.group(1), None, _dur_of(m.group(2)), None, head, "paren_mark")
    # 形态4：名-系列尾（空格）或 名 空格 色尾；容忍尾后时限
    m = re.match(rf"^({_CN}{{1,14}})\s+([一-龥A-Za-z0-9·★]{{1,10}})(?:-(\d+)天|$)", h)
    if m and m.group(1) not in _COLOR_ONLY:
        return _mk(m.group(1), None,
                   int(m.group(3)) if m.group(3) else None,
                   m.group(2), head, "spaced")
    # 形态5：纯名
    if _CN_ONLY.match(h) and not re.fullmatch(r"[A-Za-z0-9_ ;]+", h):
        return _mk(h, None, None, None, head, "plain")
    return None


def _mk(base, part, dur, flavor, raw, kind):
    # 内部对象名/全 ASCII 码拒绝（NPC 等；中文品牌名如 B站/CC 不受影响）
    if not re.search(r"[一-龥]", base):
        return None
    return DisplayName(base, part, dur, flavor, raw, kind)


def best_name_in_row(texts: Iterable[str]) -> Optional[DisplayName]:
    best: Optional[DisplayName] = None
    best_score = -1
    for t in texts:
        dn = parse_display(t)
        if dn is None:
            continue
        score = (4 if dn.part else 0) + (2 if dn.duration_days is not None else 0) + (1 if dn.flavor else 0)
        if score > best_score or (score == best_score and best is not None and len(dn.raw) < len(best.raw)):
            best = dn
            best_score = score
    return best


if __name__ == "__main__":
    samples = [
        "福虎贺岁典藏-头饰(永久款)。#r炮竹声里辞旧岁，福虎新年好运长。",
        "星月落羽典藏-衣服(30天)",
        "幽蓝星愿-头饰-5天", "遇岁之禧-衣服", "深渊漫步", "清凉棒冰·守护",
        "两小无猜 少时凌霄", "假面骑士 空我-14天", "B站新年限定 - 衣服（30天）",
        "NeXT赛事专属时装-头饰(永久款)", "全城热练 清新绿", "天空蓝",
        "三载之伴-衣服((30天)", "黑夜传说 - 衣服(14天)",
        "新款荧光棒，在辐射诡楼S6赛季中成为资深骑士即可获得", "拥有纪念意义的服装",
        "一件1天时限的时装头饰“两小无猜”。",
        "#cffc8a4天枢龙将#n系列科技装置", "天枢龙将主题限定背包",
        "云石粉 - 衣服（30天）", "决胜赛点-头饰(永久款)", "圣诞温情-衣服(永久款)",
        "假面骑士 空我", "CC小黄鸭纸箱头-头饰-7天", "幽蓝星愿-头饰-30天",
        "恶魔优等生-头饰-5天", "战术专家（Resident Evil）",
        # v3 desc 句子反例（用户 2026-09-04 抓出：desc 混入时装名）
        "也许可以抵挡一些对探潮勇士们的信念的侵害。", "呜啊！吓你一跳！",
        "请不要拒绝精灵在槲寄生下提出的所有请求。", "为方舟市每一位市民特别定制的纪念衫。",
        "将背包外形更改为灰格的新款单肩挎包。新背包只会改变背包外形,不会影响背包的容量格子数。",
        "小小的脑袋充满了大大的疑惑。#r生存答人挑战赛专属奖励(7天)",
        "垂光织梦主题限定背包。以藤为经，以蝶为纬，将四月垂落的紫藤花瀑织成背脊的流光。",
        "吃遍全世界的梦想要和你一起才美味！", "海水的清凉和海风的清新一起撞进怀里",
        # 真名豁免（不得误杀）
        "武士意志-衣服", "光影意志-头饰", "CC定制时装", "假面骑士 空我",
        "帝皇铠甲-14天", "深渊漫步", "2024新年纪念背包",
    ]
    for s in samples:
        dn = parse_display(s)
        print(f"{'OK ' if dn else '-- '} {s[:44]:<46} -> {dn}")
