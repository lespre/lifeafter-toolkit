"""一次性拆分脚本：把 board.html 巨石拆成 CSS / JS 模块。

执行后 board.html 只保留结构骨架，产物为：
  assets/board_base.css     —— 基础布局与组件样式（来自原内联 <style>）
  assets/board_dict.js      —— 字段中文名 / 取值中文名等纯字典
  assets/board_core.js      —— 主渲染逻辑
  assets/board_plugins.js   —— 尾部 4 个独立增强块

幂等：检测到已拆分过（存在 <!-- board:split --> 标记）则直接退出。
"""
import pathlib
import re
import shutil

WEB = pathlib.Path(__file__).resolve().parents[2]      # 02_wiki/web
HTML = WEB / "board.html"
ASSETS = WEB / "assets"

SPLIT_MARK = "<!-- board:split -->"


def extract_style(s: str) -> tuple[str, str]:
    """取出第一个 <style>...</style> 块内容。"""
    m = re.search(r"<style>(.*?)</style>", s, re.S)
    if not m:
        raise SystemExit("未找到内联 <style> 块")
    return s[: m.start()] + s[m.end():], m.group(1)


def extract_scripts(s: str) -> tuple[str, list[str]]:
    """取出所有无 src 的内联 <script> 块，返回 (剩余 HTML, [块内容...])。"""
    blocks: list[str] = []
    out = []
    pos = 0
    pattern = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
    for m in pattern.finditer(s):
        out.append(s[pos:m.start()])
        blocks.append(m.group(1))
        pos = m.end()
    out.append(s[pos:])
    return "".join(out), blocks


DICT_HEADER = (
    "/* 字段中文名 / 取值中文名等纯字典（从 board.html 拆出，勿含逻辑）。\n"
    "   拆分时间：2026-10-30 · 由 tools/build/split_board_html.py 生成 */\n"
)
CORE_HEADER = (
    "/* board.html 主渲染逻辑（从 board.html 内联 <script> 拆出，2026-10-30）。\n"
    "   依赖：assets/board_dict.js（字典）须先加载。 */\n"
)


def split_dict(core: str) -> tuple[str, str, list]:
    """把顶层的字典类常量抽到独立文件。

    判定：顶层 `const NAME={...}` 且 NAME 属于字典命名约定。
    用括号配平扫描（跳过字符串/模板串内容）定位完整字面量边界。

    返回 (字典文件内容, 剩余 core 内容)，并保证「字典 + 剩余 == 原文」
    在语义上可逆：每个字典块原样保留（含前后空白），仅在文件层重新排布。
    """
    dict_names = []
    for m in re.finditer(r"^const ([A-Za-z_$][\w$]*)\s*=", core, re.M):
        name = m.group(1)
        if (
            name.endswith("_CN")
            or name.endswith("_LABEL")
            or name.endswith("_COLORS")
            or name in {"VALUE_CN", "TERM_CN", "TITLE_CN", "FIELD_CN", "EV_CN"}
        ):
            dict_names.append(name)

    if not dict_names:
        return "", core

    # 逐个定位字面量区间
    spans: list[tuple[int, int, str]] = []  # (start, end, text)
    consumed: list[tuple[int, int]] = []
    for name in dict_names:
        m = re.search(rf"^const {re.escape(name)}\s*=", core, re.M)
        if not m:
            continue
        # 跳过已被前一个块覆盖的区间
        if any(m.start() >= a and m.start() < b for a, b in consumed):
            continue
        # ★ 必须确认 '=' 后紧跟的是 '{' 或 '['，否则这是字符串常量（如 WB_OFFLINE_LABEL="..."），
        #   若继续往下找括号会匹配到几百行外的别处，切出垃圾。
        k = m.end()
        while k < len(core) and core[k] in " \t":
            k += 1
        if k >= len(core) or core[k] not in "{[":
            continue
        open_ch = core[k]
        close_ch = "}" if open_ch == "{" else "]"
        start = m.start()
        i = k
        depth = 0
        j = i
        in_str = None
        while j < len(core):
            ch = core[j]
            if in_str:
                if ch == "\\":
                    j += 2
                    continue
                if ch == in_str:
                    in_str = None
            elif ch in "\"'`":
                in_str = ch
            elif ch == open_ch:
                depth += 1
            elif ch == close_ch:
                depth -= 1
                if depth == 0:
                    break
            j += 1
        end = j + 1
        # 包含尾随分号（不包含换行，避免吃掉块间空行）
        if end < len(core) and core[end] == ";":
            end += 1
        spans.append((start, end, core[start:end]))
        consumed.append((start, end))

    spans.sort()

    # 还原校验：把 spans 按原位【插回】，必须逐字节等于 core
    rebuilt = []
    prev = 0
    for a, b, text in spans:
        rebuilt.append(core[prev:a])
        rebuilt.append(text)
        prev = b
    rebuilt.append(core[prev:])
    if "".join(rebuilt) != core:
        raise SystemExit("字典切分破坏了原文（还原校验失败），已中止")

    # 生成剩余 core：删掉这些区间。
    # ⚠ 关键：删除 span 时必须「用空串替换」而不是「跳过」——
    #   两种写法对 rest 的内容其实等价，但下面 body 的拼接方式决定了守恒性。
    #   这里采用「rest 里保留 span 之间的原始空白（换行/缩进）」，
    #   字典文件里则原样保留每个 span 的文本，两者相加即可还原原文。
    remaining = []
    prev = 0
    for a, b, _ in spans:
        remaining.append(core[prev:a])
        prev = b
    remaining.append(core[prev:])
    rest = "".join(remaining)

    # 字典文件：每个 span 原样保留（含其后的分号），块间用原文里 span 末尾到下一个 span 起始
    # 之间的空白连接 —— 但那段空白已在 rest 中，因此这里直接紧邻拼接即可。
    body = "".join(t for _, _, t in spans)
    return DICT_HEADER + body + "\n", rest, spans


def main() -> int:
    if SPLIT_MARK in HTML.read_text(encoding="utf-8"):
        print("board.html 已拆分过，跳过。")
        return 0

    src = HTML.read_text(encoding="utf-8")
    backup = HTML.with_suffix(".html.bak_split")
    shutil.copy2(HTML, backup)

    html, css = extract_style(src)
    html, scripts = extract_scripts(html)
    if len(scripts) != 5:
        raise SystemExit(f"预期 5 个内联 script 块，实际 {len(scripts)}")

    core = scripts[0]
    plugins = "\n".join(scripts[1:])

    dict_js, core_js, _last_spans = split_dict(core)

    # ── 内容守恒校验 ────────────────────────────────────────
    # 字典块原本与逻辑代码交错，拆出后必然重排 ⇒ 顺序无关的「字符守恒」才是正确判据：
    #   去空白后，拆出文件的字符多重集必须与原文完全一致（不增不减不改）。
    # 顺序可逆性已由 split_dict 内部的「原位插回 == 原文」保证。
    from collections import Counter

    # ★ split_dict 返回的 dict_js 已含 DICT_HEADER；core_js 是「剩余正文」，
    #   写盘时才补 CORE_HEADER —— 所以这里 core_js 直接就是正文，不能再切头部。
    dict_body = dict_js[len(DICT_HEADER):] if dict_js else ""
    core_body = core_js
    strip = lambda s: "".join(ch for ch in s if not ch.isspace())
    c_orig = Counter(strip(core))
    c_new = Counter(strip(dict_body) + strip(core_body))
    if c_orig != c_new:
        lost = c_orig - c_new
        gained = c_new - c_orig
        # 诊断：定位是哪个块丢了
        diag = []
        for a, b, text in _last_spans:
            nm = text.split("=", 1)[0].strip()[:24]
            t = Counter(strip(text))
            if t - c_new:
                diag.append(f"{nm}: 缺 {sum((t - c_new).values())} 字符")
        raise SystemExit(
            "内容不守恒：\n"
            f"  丢失字符: {dict(lost.most_common(8))}\n"
            f"  多出字符: {dict(gained.most_common(8))}\n"
            f"  逐块诊断: {diag[:6]}"
        )
    print(f"内容守恒 ✓ 去空白后 {sum(c_orig.values()):,} 字符多重集完全一致")

    # ── 写文件 ──────────────────────────────────────────────
    (ASSETS / "board_base.css").write_text(
        "/* board.html 基础布局与组件样式（从 board.html 内联 <style> 拆出，2026-10-30）。\n"
        "   板型专属样式在 board_theme_*.css，板型专属渲染在 board_core.js。 */\n" + css.lstrip(),
        encoding="utf-8",
    )
    if dict_js:
        (ASSETS / "board_dict.js").write_text(dict_js, encoding="utf-8")
    (ASSETS / "board_core.js").write_text(CORE_HEADER + core_js, encoding="utf-8")
    (ASSETS / "board_plugins.js").write_text(
        "/* board.html 尾部增强块：性能条 / 分类导航 / 技术详情 / 窄列宽（2026-10-30 拆出）。 */\n"
        + plugins.strip(),
        encoding="utf-8",
    )

    # ── 回填 HTML ───────────────────────────────────────────
    # CSS：必须插在「原内联 <style> 所在位置」，否则层叠顺序会变。
    # 原顺序：shadcn → aftermath → official → [内联 <style>] → dusk → board_ui.js
    html = html.replace(
        '<link rel="stylesheet" href="assets/board_theme_official.css?v=20261019p">',
        '<link rel="stylesheet" href="assets/board_theme_official.css?v=20261019p">\n'
        '<link rel="stylesheet" href="assets/board_base.css?v=20261030-01">',
        1,
    )

    # JS：主块放在原主块位置（body 末尾），字典先于主块，插件块在最后
    # ⚠ 定位必须用结构锚点，不能用 rindex("</div>") —— 脚本块内有 300+ 处 </div> 字符串。
    anchor = '<div class="grid" id="grid"></div>\n</div>\n'
    ai = html.find(anchor)
    if ai == -1:
        raise SystemExit("未找到 grid 锚点，无法定位主脚本插入点")
    cut = ai + len(anchor)
    js_tags = (
        "\n<!-- board:split -->\n"
        '<script src="assets/board_dict.js?v=20261030-01"></script>\n'
        '<script src="assets/board_core.js?v=20261030-01"></script>\n'
    )
    html = html[:cut] + js_tags + html[cut:]

    # 插件块：追加到 </body> 之前
    html = html.replace(
        "</body>",
        '<script src="assets/board_plugins.js?v=20261030-01"></script>\n</body>',
        1,
    )

    HTML.write_text(html, encoding="utf-8")

    print(f"board.html: {len(src):,} → {len(html):,} 字节")
    for f in ["board_base.css", "board_dict.js", "board_core.js", "board_plugins.js"]:
        p = ASSETS / f
        print(f"  assets/{f}: {p.stat().st_size:,} 字节")
    print(f"备份: {backup.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
