# -*- coding: utf-8 -*-
"""
明日之后资源定位器
封装武器皮肤、人物时装的完整定位流程，可复用。

核心思路：
1. 文件名/目录名关键词扫描 → 快速定位候选目录
2. 多编码内容字符串搜索（UTF-8/GBK/UTF-16LE/BE）→ 挖明文文本
3. 关键词链式扩展 → 从已知词扩展到相邻文本中的新词
4. 与正式服对比 → 筛选体验服独有（未上线）内容
5. 结果汇总输出 → 带路径、命中词、上下文

用法：
    from resource_locator import ResourceLocator
    locator = ResourceLocator(r"E:/mrzh/gpk_unpacked", official_dir=r"E:/lifeafter_unpacked")
    # 武器皮肤
    weapons = locator.locate_weapon_skins()
    # 人物时装
    fashions = locator.locate_fashion()
    # 自定义搜索
    results = locator.scan_by_content(["战神烈火剑", "极光剑"])
"""

import os
import re
import json
import time
from multiprocessing import Pool, cpu_count
from functools import partial


# ============================================================
# 预设关键词库
# ============================================================

# 武器皮肤相关关键词（文件名 + 内容）
WEAPON_FILENAME_KEYWORDS = [
    "wpn", "weapon", "skin", "tuzhuang", "coat", "gun",
    "rifle", "sniper", "shotgun", "melee", "bow",
    "aug", "m4", "ak", "95", "g36", "mp5", "ump",
]

WEAPON_CONTENT_KEYWORDS = [
    "武器皮肤", "涂装", "枪皮", "武器外观", "枪械皮肤",
    "沙海月鸣", "极光剑", "帝皇裁决", "战神烈火剑", "疾影枪",
    "AUG", "突击步枪", "狙击枪", "霰弹枪", "冷兵器",
]

# 人物时装相关关键词
FASHION_FILENAME_KEYWORDS = [
    "shizhuang", "fashion", "cloth", "clothes", "avatar",
    "character", "suit", "outfit", "dress", "hair",
    "head", "body", "hand", "foot", "back",
]

FASHION_CONTENT_KEYWORDS = [
    "时装", "套装", "外观", "衣服", "发型", "头饰",
    "背饰", "挂件", "表情", "动作", "坐姿",
    "典藏", "幻彩", "限定", "联名", "联动",
]

# 铠甲勇士联动专属关键词
ARMOR_KEYWORDS = [
    "铠甲勇士", "刑天", "飞影", "帝皇", "金刚", "风鹰", "黑犀",
    "地虎", "雪獒", "炎龙", "五行", "铠甲合体", "帝皇驹",
]

# 搜索时使用的编码
DEFAULT_ENCODINGS = ["utf-8", "gbk", "utf-16-le", "utf-16-be"]


# ============================================================
# 工具函数
# ============================================================

def _scan_file_content(args):
    """多进程 worker：扫描单个文件的内容，返回命中结果"""
    filepath, keywords, encodings, context_size = args
    results = []
    try:
        with open(filepath, "rb") as f:
            data = f.read()
    except Exception:
        return results

    for enc in encodings:
        try:
            text = data.decode(enc, errors="ignore")
        except Exception:
            continue
        for kw in keywords:
            # 大小写不敏感搜索
            pattern = re.compile(re.escape(kw), re.IGNORECASE)
            for m in pattern.finditer(text):
                start = max(0, m.start() - context_size)
                end = min(len(text), m.end() + context_size)
                context = text[start:end].replace("\x00", " ").replace("\n", " ").strip()
                # 清理多余空白
                context = re.sub(r"\s+", " ", context)
                results.append({
                    "file": filepath,
                    "keyword": kw,
                    "encoding": enc,
                    "offset": m.start(),
                    "context": context[:300],  # 限制上下文长度
                })
    return results


def _get_all_files(root_dir, extensions=None):
    """递归获取目录下所有文件"""
    files = []
    for root, dirs, filenames in os.walk(root_dir):
        for fn in filenames:
            fp = os.path.join(root, fn)
            if extensions:
                ext = os.path.splitext(fn)[1].lower()
                if ext not in extensions:
                    continue
            files.append(fp)
    return files


# ============================================================
# 资源定位器主类
# ============================================================

class ResourceLocator:
    """明日之后资源定位器：武器皮肤 + 人物时装完整定位流程"""

    def __init__(self, unpack_dir, official_dir=None, output_dir=None, workers=None):
        """
        Args:
            unpack_dir: 体验服解包后的根目录（如 E:\\mrzh\\gpk_unpacked）
            official_dir: 正式服解包后的根目录（可选，用于对比找独有内容）
            output_dir: 结果输出目录（默认在 unpack_dir 同级 _定位结果）
            workers: 多进程数（默认 CPU 核数的一半，留余量）
        """
        self.unpack_dir = unpack_dir
        self.official_dir = official_dir
        self.output_dir = output_dir or os.path.join(os.path.dirname(unpack_dir), "_定位结果")
        os.makedirs(self.output_dir, exist_ok=True)
        self.workers = workers or max(1, cpu_count() // 2)
        self._all_files = None

    # --------------------------------------------------------
    # 第一层：文件名/目录名扫描
    # --------------------------------------------------------

    def scan_by_filename(self, keywords, extensions=None):
        """
        按文件名/目录名关键词扫描，快速定位候选文件。

        Args:
            keywords: 关键词列表
            extensions: 只搜指定扩展名（如 ['.bin', '.dds', '.png']），None 表示全部

        Returns:
            list: 命中的文件路径列表
        """
        print("[文件名扫描] 关键词: %s" % ", ".join(keywords))
        hits = []
        files = self._get_files(extensions)
        for fp in files:
            rel = os.path.relpath(fp, self.unpack_dir).lower()
            if any(kw.lower() in rel for kw in keywords):
                hits.append(fp)
        print("  命中 %d 个文件" % len(hits))
        return hits

    # --------------------------------------------------------
    # 第二层：多编码内容字符串搜索
    # --------------------------------------------------------

    def scan_by_content(self, keywords, extensions=None, encodings=None,
                        context_size=80, workers=None):
        """
        多编码内容字符串搜索，返回命中文件+上下文。

        Args:
            keywords: 关键词列表
            extensions: 只搜指定扩展名（默认 ['.bin', '.txt', '.json', '.xml', '.nxs']）
            encodings: 编码列表（默认 UTF-8/GBK/UTF-16LE/BE）
            context_size: 关键词前后上下文字节数
            workers: 进程数

        Returns:
            list: 命中结果，每项含 file/keyword/encoding/offset/context
        """
        if extensions is None:
            extensions = [".bin", ".txt", ".json", ".xml", ".nxs", ".csv", ".lua", ".py"]
        if encodings is None:
            encodings = DEFAULT_ENCODINGS

        print("[内容搜索] 关键词: %s | 编码: %s | 进程数: %d" % (
            ", ".join(keywords), ", ".join(encodings), workers or self.workers))

        files = self._get_files(extensions)
        print("  待扫描文件: %d 个" % len(files))

        args_list = [(fp, keywords, encodings, context_size) for fp in files]
        worker_count = workers or self.workers

        t0 = time.time()
        all_results = []
        if worker_count <= 1:
            for args in args_list:
                all_results.extend(_scan_file_content(args))
        else:
            with Pool(processes=worker_count) as pool:
                for result in pool.imap_unordered(_scan_file_content, args_list, chunksize=50):
                    all_results.extend(result)

        elapsed = time.time() - t0
        print("  完成，耗时 %.1fs，命中 %d 条" % (elapsed, len(all_results)))
        return all_results

    # --------------------------------------------------------
    # 第三层：关键词链式扩展
    # --------------------------------------------------------

    def chain_expand(self, seed_keywords, depth=2, extensions=None, top_n=50):
        """
        关键词链式扩展：从种子词出发，搜索命中文件中的相邻文本，提取潜在新词。

        原理：武器皮肤/时装名通常成组出现（如"极光剑"附近会有"极光盾""帝皇裁决"），
              从已知词的上下文里提取高频中文词，就能发现同系列的其他名称。

        Args:
            seed_keywords: 种子关键词列表（如 ["极光剑", "帝皇裁决"]）
            depth: 扩展轮数（默认 2 轮）
            extensions: 搜索的文件扩展名
            top_n: 每轮保留前 N 个高频新词

        Returns:
            dict: {轮次: [新词列表]}，含每轮发现的词
        """
        print("[链式扩展] 种子词: %s | 深度: %d" % (", ".join(seed_keywords), depth))

        all_discovered = {}
        current_keywords = list(seed_keywords)
        known_words = set(kw.lower() for kw in seed_keywords)

        for round_idx in range(1, depth + 1):
            print("  第 %d 轮，搜索词: %s" % (round_idx, ", ".join(current_keywords)))
            results = self.scan_by_content(current_keywords, extensions=extensions, context_size=120)

            # 从上下文中提取 2-8 字的中文词
            new_words = {}
            chinese_pattern = re.compile(r"[\u4e00-\u9fff]{2,8}")
            for r in results:
                for word in chinese_pattern.findall(r["context"]):
                    wl = word.lower()
                    if wl not in known_words and len(word) >= 2:
                        new_words[word] = new_words.get(word, 0) + 1

            # 按频率排序，取前 N 个
            sorted_words = sorted(new_words.items(), key=lambda x: -x[1])[:top_n]
            discovered = [w for w, cnt in sorted_words if cnt >= 2]  # 至少出现 2 次
            all_discovered["round_%d" % round_idx] = discovered
            print("    发现新词 %d 个: %s" % (len(discovered), ", ".join(discovered[:20])))

            # 更新已知词和下一轮搜索词
            for w in discovered:
                known_words.add(w.lower())
            current_keywords = discovered
            if not current_keywords:
                print("    无新词，停止扩展")
                break

        return all_discovered

    # --------------------------------------------------------
    # 第四层：与正式服对比
    # --------------------------------------------------------

    def diff_official(self, extensions=None):
        """
        与正式服解包目录对比，找出体验服独有文件（未上线内容）。

        对比方式：相对路径 + 文件大小。路径不同或大小不同都算独有/变更。

        Args:
            extensions: 只对比指定扩展名

        Returns:
            dict: {"only_in_test": [...], "size_changed": [...], "only_in_official": [...]}
        """
        if not self.official_dir:
            print("[正式服对比] 未提供正式服目录，跳过")
            return {}

        print("[正式服对比] 体验服: %s | 正式服: %s" % (self.unpack_dir, self.official_dir))

        test_files = self._get_file_map(self.unpack_dir, extensions)
        official_files = self._get_file_map(self.official_dir, extensions)

        only_in_test = []
        size_changed = []
        only_in_official = []

        for rel, info in test_files.items():
            if rel not in official_files:
                only_in_test.append(info["path"])
            elif info["size"] != official_files[rel]["size"]:
                size_changed.append({"test": info["path"], "official": official_files[rel]["path"],
                                     "test_size": info["size"], "official_size": official_files[rel]["size"]})

        for rel in official_files:
            if rel not in test_files:
                only_in_official.append(official_files[rel]["path"])

        print("  体验服独有: %d | 大小变更: %d | 正式服独有: %d" % (
            len(only_in_test), len(size_changed), len(only_in_official)))
        return {"only_in_test": only_in_test, "size_changed": size_changed,
                "only_in_official": only_in_official}

    # --------------------------------------------------------
    # 封装流程：武器皮肤定位
    # --------------------------------------------------------

    def locate_weapon_skins(self, include_armor=True, diff=True):
        """
        武器皮肤完整定位流程。

        流程：
        1. 文件名扫描（wpn/weapon/skin 等）→ 候选目录
        2. 内容搜索（武器皮肤/涂装/已知武器名）→ 明文文本
        3. 链式扩展（从已知武器名扩展同系列皮肤）
        4. 正式服对比 → 筛选未上线新皮肤
        5. 结果汇总输出

        Args:
            include_armor: 是否包含铠甲勇士联动关键词
            diff: 是否与正式服对比

        Returns:
            dict: 定位结果汇总
        """
        print("\n" + "=" * 60)
        print("武器皮肤定位开始")
        print("=" * 60)

        result = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

        # 1. 文件名扫描
        filename_hits = self.scan_by_filename(WEAPON_FILENAME_KEYWORDS)
        result["filename_hits"] = filename_hits
        self._save_list(filename_hits, "武器皮肤_文件名命中.txt")

        # 2. 内容搜索
        content_keywords = list(WEAPON_CONTENT_KEYWORDS)
        if include_armor:
            content_keywords.extend(ARMOR_KEYWORDS)
        content_hits = self.scan_by_content(content_keywords)
        result["content_hits"] = content_hits
        self._save_results(content_hits, "武器皮肤_内容命中.json")

        # 3. 链式扩展（从已知联动武器名出发）
        seed = ["战神烈火剑", "极光剑", "帝皇裁决", "疾影枪", "沙海月鸣"]
        chain = self.chain_expand(seed, depth=2)
        result["chain_expand"] = chain
        self._save_json(chain, "武器皮肤_链式扩展.json")

        # 4. 正式服对比
        if diff and self.official_dir:
            diff_result = self.diff_official(extensions=[".bin", ".dds", ".png", ".json"])
            # 只保留武器相关的独有文件
            weapon_only = [f for f in diff_result["only_in_test"]
                           if any(kw in f.lower() for kw in ["wpn", "weapon", "skin", "gun"])]
            result["official_diff"] = {"only_in_test_weapon": weapon_only,
                                        "total_only_in_test": len(diff_result["only_in_test"])}
            self._save_list(weapon_only, "武器皮肤_体验服独有.txt")

        # 5. 汇总
        summary = self._extract_weapon_names(content_hits, chain)
        result["summary"] = summary
        self._save_json(result, "武器皮肤_定位结果_汇总.json")

        print("\n[武器皮肤定位完成]")
        print("  文件名命中: %d" % len(filename_hits))
        print("  内容命中: %d" % len(content_hits))
        print("  提取武器名: %s" % ", ".join(summary[:30]))
        print("  结果目录: %s" % self.output_dir)
        return result

    # --------------------------------------------------------
    # 封装流程：人物时装定位
    # --------------------------------------------------------

    def locate_fashion(self, include_armor=True, diff=True):
        """
        人物时装完整定位流程。

        流程：
        1. 文件名扫描（shizhuang/fashion/cloth/character 等）
        2. 内容搜索（时装/套装/典藏/限定 等）
        3. 链式扩展（从已知时装名扩展同系列）
        4. 正式服对比 → 筛选未上线新时装
        5. 结果汇总输出

        Args:
            include_armor: 是否包含铠甲勇士联动关键词
            diff: 是否与正式服对比

        Returns:
            dict: 定位结果汇总
        """
        print("\n" + "=" * 60)
        print("人物时装定位开始")
        print("=" * 60)

        result = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S")}

        # 1. 文件名扫描
        filename_hits = self.scan_by_filename(FASHION_FILENAME_KEYWORDS)
        result["filename_hits"] = filename_hits
        self._save_list(filename_hits, "人物时装_文件名命中.txt")

        # 2. 内容搜索
        content_keywords = list(FASHION_CONTENT_KEYWORDS)
        if include_armor:
            content_keywords.extend(ARMOR_KEYWORDS)
        content_hits = self.scan_by_content(content_keywords)
        result["content_hits"] = content_hits
        self._save_results(content_hits, "人物时装_内容命中.json")

        # 3. 链式扩展
        seed = ["典藏", "幻彩", "限定", "联动", "铠甲勇士"]
        chain = self.chain_expand(seed, depth=2)
        result["chain_expand"] = chain
        self._save_json(chain, "人物时装_链式扩展.json")

        # 4. 正式服对比
        if diff and self.official_dir:
            diff_result = self.diff_official(extensions=[".bin", ".dds", ".png", ".json"])
            fashion_only = [f for f in diff_result["only_in_test"]
                            if any(kw in f.lower() for kw in
                                   ["shizhuang", "fashion", "cloth", "character", "avatar", "suit"])]
            result["official_diff"] = {"only_in_test_fashion": fashion_only,
                                        "total_only_in_test": len(diff_result["only_in_test"])}
            self._save_list(fashion_only, "人物时装_体验服独有.txt")

        # 5. 汇总
        summary = self._extract_fashion_names(content_hits, chain)
        result["summary"] = summary
        self._save_json(result, "人物时装_定位结果_汇总.json")

        print("\n[人物时装定位完成]")
        print("  文件名命中: %d" % len(filename_hits))
        print("  内容命中: %d" % len(content_hits))
        print("  提取时装名: %s" % ", ".join(summary[:30]))
        print("  结果目录: %s" % self.output_dir)
        return result

    # --------------------------------------------------------
    # 内部工具
    # --------------------------------------------------------

    def _get_files(self, extensions=None):
        """获取解包目录下所有文件（带缓存）"""
        if self._all_files is None:
            self._all_files = _get_all_files(self.unpack_dir, extensions)
            print("  索引文件: %d 个" % len(self._all_files))
        if extensions:
            return [f for f in self._all_files
                    if os.path.splitext(f)[1].lower() in extensions]
        return self._all_files

    @staticmethod
    def _get_file_map(root_dir, extensions=None):
        """构建 {相对路径: {path, size}} 映射，用于对比"""
        m = {}
        for root, dirs, files in os.walk(root_dir):
            for fn in files:
                fp = os.path.join(root, fn)
                if extensions:
                    ext = os.path.splitext(fn)[1].lower()
                    if ext not in extensions:
                        continue
                rel = os.path.relpath(fp, root_dir).lower()
                try:
                    m[rel] = {"path": fp, "size": os.path.getsize(fp)}
                except OSError:
                    pass
        return m

    @staticmethod
    def _extract_weapon_names(content_hits, chain):
        """从内容命中和链式扩展结果中提取武器皮肤名称"""
        names = set()
        # 从上下文提取 2-6 字中文词，过滤常见非武器词
        stop = {"武器", "皮肤", "涂装", "外观", "伤害", "攻击", "暴击", "护甲",
                "获得", "使用", "装备", "升级", "强化", "改造", "转移", "简单",
                "生存", "经典", "会员", "体验", "正式", "更新", "活动", "奖励"}
        chinese = re.compile(r"[\u4e00-\u9fff]{2,6}")
        for r in content_hits:
            for w in chinese.findall(r["context"]):
                if w not in stop and ("剑" in w or "枪" in w or "盾" in w or
                                       "刀" in w or "弓" in w or "炮" in w or
                                       "刃" in w or "斧" in w or "锤" in w):
                    names.add(w)
        # 加入链式扩展结果
        for round_words in chain.values():
            names.update(round_words)
        return sorted(names)

    @staticmethod
    def _extract_fashion_names(content_hits, chain):
        """从内容命中和链式扩展结果中提取时装名称"""
        names = set()
        stop = {"时装", "套装", "外观", "衣服", "发型", "头饰", "背饰",
                "挂件", "表情", "动作", "获得", "使用", "装备", "升级",
                "典藏", "幻彩", "限定", "联动", "活动", "奖励", "简单生存"}
        chinese = re.compile(r"[\u4e00-\u9fff]{2,8}")
        for r in content_hits:
            for w in chinese.findall(r["context"]):
                if w not in stop and len(w) >= 3:
                    # 时装名通常 3-8 字，含特定字
                    if any(c in w for c in ["衣", "裙", "袍", "甲", "盔", "靴",
                                             "帽", "巾", "纱", "绒", "皮", "布",
                                             "金", "银", "玉", "钻", "晶", "幻",
                                             "夜", "星", "月", "花", "雪", "冰"]):
                        names.add(w)
        for round_words in chain.values():
            names.update(round_words)
        return sorted(names)

    def _save_list(self, data, filename):
        fp = os.path.join(self.output_dir, filename)
        with open(fp, "w", encoding="utf-8") as f:
            for item in data:
                f.write(item + "\n")
        print("  已保存: %s (%d 条)" % (filename, len(data)))

    def _save_results(self, results, filename):
        fp = os.path.join(self.output_dir, filename)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print("  已保存: %s (%d 条)" % (filename, len(results)))

    def _save_json(self, data, filename):
        fp = os.path.join(self.output_dir, filename)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# ============================================================
# 命令行入口
# ============================================================

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("用法:")
        print("  python resource_locator.py <解包目录> [正式服目录] [模式]")
        print("  模式: weapon / fashion / all（默认 all）")
        print()
        print("示例:")
        print("  python resource_locator.py E:/mrzh/gpk_unpacked E:/lifeafter_unpacked weapon")
        sys.exit(1)

    unpack = sys.argv[1]
    official = sys.argv[2] if len(sys.argv) > 2 else None
    mode = sys.argv[3] if len(sys.argv) > 3 else "all"

    locator = ResourceLocator(unpack, official_dir=official)

    if mode in ("weapon", "all"):
        locator.locate_weapon_skins()
    if mode in ("fashion", "all"):
        locator.locate_fashion()
