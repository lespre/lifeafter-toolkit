# -*- coding: utf-8 -*-
"""
明日之后 .nxs 配置表通用解码器
================================
可复用的解码方法，适用于 1B249D5C9984E1B4.nxs 等大型配置表。

解码方法：
1. 直接UTF-8解码提取中文字符串
2. 关键词搜索定位
3. 上下文提取
4. 正则表达式提取结构化数据

使用方法：
    python nxs_config_decoder.py <nxs文件路径> [关键词1] [关键词2] ...
    
示例：
    python nxs_config_decoder.py 1B249D5C9984E1B4.nxs 武器皮肤 极光剑 战神烈火剑
"""

import sys
import os
import re
import json
import struct
from pathlib import Path
from datetime import datetime


class NxsConfigDecoder:
    """.nxs 配置表解码器"""
    
    def __init__(self, nxs_path):
        """初始化解码器
        
        Args:
            nxs_path: .nxs 文件路径
        """
        self.nxs_path = Path(nxs_path)
        self.raw_data = None
        self.decoded_text = None
        self.chinese_strings = []
        self.ascii_strings = []
        
        self._load_file()
    
    def _load_file(self):
        """加载文件"""
        with open(self.nxs_path, 'rb') as f:
            self.raw_data = f.read()
        
        # 尝试UTF-8解码
        try:
            self.decoded_text = self.raw_data.decode('utf-8', errors='ignore')
        except Exception as e:
            print(f"UTF-8解码失败: {e}")
            self.decoded_text = ''
    
    def extract_chinese_strings(self, min_length=2, max_length=200):
        """提取中文字符串
        
        Args:
            min_length: 最小长度
            max_length: 最大长度
            
        Returns:
            中文字符串列表，每个元素包含 text, start, end
        """
        self.chinese_strings = []
        
        # 匹配中文字符串（包含中文和常见标点）
        pattern = rf'[\u4e00-\u9fff][\u4e00-\u9fff\w\s\-\*\+\#\.\,\，\。\：\:\(\)（）\[\]【】\/\\]{{{min_length-1},{max_length-1}}}'
        
        for m in re.finditer(pattern, self.decoded_text):
            text = m.group().strip()
            if len(text) >= min_length:
                self.chinese_strings.append({
                    'text': text,
                    'start': m.start(),
                    'end': m.end()
                })
        
        return self.chinese_strings
    
    def extract_ascii_strings(self, min_length=4):
        """提取ASCII字符串
        
        Args:
            min_length: 最小长度
            
        Returns:
            ASCII字符串列表
        """
        self.ascii_strings = []
        
        pattern = rf'[a-zA-Z_][a-zA-Z0-9_/\\.]{{{min_length-1},}}'
        
        for m in re.finditer(pattern, self.decoded_text):
            text = m.group()
            self.ascii_strings.append({
                'text': text,
                'start': m.start(),
                'end': m.end()
            })
        
        return self.ascii_strings
    
    def search_keyword(self, keyword, context_size=200):
        """搜索关键词并返回上下文
        
        Args:
            keyword: 关键词（中文或英文）
            context_size: 上下文大小（字节）
            
        Returns:
            匹配结果列表，每个元素包含 offset, context
        """
        results = []
        
        # 转换为字节
        if isinstance(keyword, str):
            keyword_bytes = keyword.encode('utf-8')
        else:
            keyword_bytes = keyword
        
        pos = 0
        while True:
            pos = self.raw_data.find(keyword_bytes, pos)
            if pos < 0:
                break
            
            # 提取上下文
            context_start = max(0, pos - context_size)
            context_end = min(len(self.raw_data), pos + len(keyword_bytes) + context_size)
            context_bytes = self.raw_data[context_start:context_end]
            
            try:
                context_text = context_bytes.decode('utf-8', errors='ignore')
                # 清理非打印字符
                context_text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', context_text)
                context_text = re.sub(r'\s+', ' ', context_text).strip()
            except:
                context_text = context_bytes.hex()
            
            results.append({
                'keyword': keyword,
                'offset': pos,
                'context': context_text
            })
            
            pos += 1
        
        return results
    
    def search_multiple_keywords(self, keywords, context_size=200):
        """搜索多个关键词
        
        Args:
            keywords: 关键词列表
            context_size: 上下文大小
            
        Returns:
            字典，key为关键词，value为匹配结果列表
        """
        results = {}
        for keyword in keywords:
            results[keyword] = self.search_keyword(keyword, context_size)
        return results
    
    def extract_pattern(self, pattern, group_index=0):
        """用正则表达式提取结构化数据
        
        Args:
            pattern: 正则表达式（字符串）
            group_index: 捕获组索引
            
        Returns:
            匹配结果列表
        """
        results = []
        
        for m in re.finditer(pattern, self.decoded_text):
            if group_index == 0:
                text = m.group()
            else:
                text = m.group(group_index)
            
            results.append({
                'text': text,
                'start': m.start(),
                'end': m.end(),
                'full_match': m.group()
            })
        
        return results
    
    def extract_weapon_skins(self):
        """提取武器皮肤列表（专门针对"打开可以获得武器皮肤：XXX*1"模式）
        
        Returns:
            武器皮肤列表
        """
        # 匹配模式：打开可以获得武器皮肤：名称*1
        pattern = r'打开可以获得武器皮肤[:：]([^*#\s]+)'
        
        results = self.extract_pattern(pattern, group_index=1)
        
        # 去重
        unique_skins = []
        seen = set()
        for r in results:
            name = r['text']
            if name not in seen:
                seen.add(name)
                unique_skins.append(name)
        
        return unique_skins
    
    def extract_fashion_items(self):
        """提取时装列表（专门针对"打开可以获得XXX-时装*1"或"打开可以获得XXX-衣服*1"模式）
        
        Returns:
            时装列表
        """
        fashion_items = []
        
        # 匹配模式1：XXX-时装
        pattern1 = r'打开可以获得[#\w]*([^#\s]+)-时装'
        results1 = self.extract_pattern(pattern1, group_index=1)
        
        # 匹配模式2：XXX-衣服
        pattern2 = r'打开可以获得[#\w]*([^#\s]+)-衣服'
        results2 = self.extract_pattern(pattern2, group_index=1)
        
        # 合并去重
        seen = set()
        for r in results1 + results2:
            name = r['text']
            if name not in seen and len(name) > 1:
                seen.add(name)
                fashion_items.append(name)
        
        return fashion_items
    
    def get_file_info(self):
        """获取文件信息
        
        Returns:
            文件信息字典
        """
        stat = self.nxs_path.stat()
        
        return {
            'file_name': self.nxs_path.name,
            'file_path': str(self.nxs_path),
            'file_size': stat.st_size,
            'file_size_human': self._human_size(stat.st_size),
            'modify_time': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S'),
            'chinese_string_count': len(self.chinese_strings),
            'ascii_string_count': len(self.ascii_strings),
        }
    
    def _human_size(self, size):
        """人类可读的文件大小"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def export_results(self, output_dir, keywords=None):
        """导出解码结果
        
        Args:
            output_dir: 输出目录
            keywords: 要搜索的关键词列表
            
        Returns:
            输出文件路径字典
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        outputs = {}
        
        # 1. 文件信息
        info = self.get_file_info()
        info_path = output_path / '文件信息.json'
        with open(info_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, ensure_ascii=False, indent=2)
        outputs['file_info'] = str(info_path)
        
        # 2. 中文字符串
        if self.chinese_strings:
            chinese_path = output_path / '中文字符串.txt'
            with open(chinese_path, 'w', encoding='utf-8') as f:
                f.write(f"=== 中文字符串列表（共{len(self.chinese_strings)}个）===\n\n")
                for i, s in enumerate(self.chinese_strings):
                    f.write(f"[{i+1}] 偏移{s['start']}-{s['end']}: {s['text']}\n")
            outputs['chinese_strings'] = str(chinese_path)
        
        # 3. ASCII字符串
        if self.ascii_strings:
            ascii_path = output_path / 'ASCII字符串.txt'
            with open(ascii_path, 'w', encoding='utf-8') as f:
                f.write(f"=== ASCII字符串列表（共{len(self.ascii_strings)}个）===\n\n")
                for i, s in enumerate(self.ascii_strings):
                    f.write(f"[{i+1}] 偏移{s['start']}-{s['end']}: {s['text']}\n")
            outputs['ascii_strings'] = str(ascii_path)
        
        # 4. 关键词搜索结果
        if keywords:
            keyword_results = self.search_multiple_keywords(keywords)
            keyword_path = output_path / '关键词搜索结果.json'
            with open(keyword_path, 'w', encoding='utf-8') as f:
                json.dump(keyword_results, f, ensure_ascii=False, indent=2)
            outputs['keyword_results'] = str(keyword_path)
            
            # 同时导出为可读文本
            keyword_txt_path = output_path / '关键词搜索结果.txt'
            with open(keyword_txt_path, 'w', encoding='utf-8') as f:
                for keyword, results in keyword_results.items():
                    f.write(f"\n{'='*60}\n")
                    f.write(f"关键词: {keyword}（共{len(results)}处）\n")
                    f.write(f"{'='*60}\n\n")
                    for i, r in enumerate(results[:50]):  # 最多50条
                        f.write(f"[{i+1}] 偏移{r['offset']}:\n")
                        f.write(f"    {r['context'][:300]}\n\n")
            outputs['keyword_results_txt'] = str(keyword_txt_path)
        
        # 5. 武器皮肤列表
        weapon_skins = self.extract_weapon_skins()
        if weapon_skins:
            skin_path = output_path / '武器皮肤列表.txt'
            with open(skin_path, 'w', encoding='utf-8') as f:
                f.write(f"=== 武器皮肤列表（共{len(weapon_skins)}个）===\n\n")
                for i, name in enumerate(weapon_skins):
                    f.write(f"{i+1}. {name}\n")
            outputs['weapon_skins'] = str(skin_path)
        
        # 6. 时装列表
        fashion_items = self.extract_fashion_items()
        if fashion_items:
            fashion_path = output_path / '时装列表.txt'
            with open(fashion_path, 'w', encoding='utf-8') as f:
                f.write(f"=== 时装列表（共{len(fashion_items)}个）===\n\n")
                for i, name in enumerate(fashion_items):
                    f.write(f"{i+1}. {name}\n")
            outputs['fashion_items'] = str(fashion_path)
        
        return outputs


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python nxs_config_decoder.py <nxs文件路径> [关键词1] [关键词2] ...")
        print()
        print("示例:")
        print("  python nxs_config_decoder.py 1B249D5C9984E1B4.nxs 武器皮肤 极光剑 战神烈火剑")
        print()
        print("输出:")
        print("  在当前目录创建 nxs_decoded_<文件名>/ 目录，包含:")
        print("    - 文件信息.json")
        print("    - 中文字符串.txt")
        print("    - ASCII字符串.txt")
        print("    - 关键词搜索结果.json / .txt")
        print("    - 武器皮肤列表.txt")
        print("    - 时装列表.txt")
        return
    
    nxs_path = sys.argv[1]
    keywords = sys.argv[2:] if len(sys.argv) > 2 else None
    
    if not os.path.exists(nxs_path):
        print(f"错误: 文件不存在 - {nxs_path}")
        return
    
    print(f"正在解码: {nxs_path}")
    print()
    
    # 创建解码器
    decoder = NxsConfigDecoder(nxs_path)
    
    # 提取字符串
    print("正在提取中文字符串...")
    decoder.extract_chinese_strings()
    print(f"  找到 {len(decoder.chinese_strings)} 个中文字符串")
    
    print("正在提取ASCII字符串...")
    decoder.extract_ascii_strings()
    print(f"  找到 {len(decoder.ascii_strings)} 个ASCII字符串")
    
    # 提取武器皮肤
    print("正在提取武器皮肤...")
    weapon_skins = decoder.extract_weapon_skins()
    print(f"  找到 {len(weapon_skins)} 个武器皮肤")
    for skin in weapon_skins:
        print(f"    - {skin}")
    
    # 提取时装
    print("正在提取时装...")
    fashion_items = decoder.extract_fashion_items()
    print(f"  找到 {len(fashion_items)} 个时装")
    
    # 关键词搜索
    if keywords:
        print(f"\n正在搜索关键词: {keywords}")
        keyword_results = decoder.search_multiple_keywords(keywords)
        for kw, results in keyword_results.items():
            print(f"  '{kw}': 找到 {len(results)} 处")
    
    # 导出结果
    print("\n正在导出结果...")
    base_name = Path(nxs_path).stem
    output_dir = f"nxs_decoded_{base_name}"
    outputs = decoder.export_results(output_dir, keywords)
    
    print("\n导出完成:")
    for name, path in outputs.items():
        print(f"  {name}: {path}")
    
    # 打印文件信息
    print("\n文件信息:")
    info = decoder.get_file_info()
    for key, value in info.items():
        print(f"  {key}: {value}")


if __name__ == '__main__':
    main()
