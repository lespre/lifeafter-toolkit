# 环境依赖（Environment）

这个目录放**跑项目需要的运行时**，不放业务数据。

```
环境/
├ python/            自带 Python 3.12（从系统安装复制，466 MB）
├ venv/              项目虚拟环境（5.2 GB，依赖已装好）
├ spine-player/      Spine 3.8 WebGL 运行时（站点通过 junction 引用）
├ everything/        Everything + es.exe（MFT 秒级扫盘，便携版）
└ requirements.lock.txt   依赖清单（重建 venv 用）
```

## 解释器怎么选

```
推荐  00_规范与工具/环境/venv/Scripts/python.exe
备用  00_规范与工具/环境/python/python.exe
```

> ⚠️ `venv/pyvenv.cfg` 里的 `home` 指向 `E:\py312`（一个 ASCII 路径的 junction，
> 指向本目录的 `python/`）。原因：CPython 启动器解析不了含中文的 `home`，
> 写成 `E:\la拆包项目\...` 会直接报 `No Python at ...`。
> **别删 E:\py312 这个 junction**，删了 venv 就起不来。

## 重建 venv

```bash
cd E:/la拆包项目
00_规范与工具/环境/python/python.exe -m venv 00_规范与工具/环境/venv
00_规范与工具/环境/venv/Scripts/python.exe -m pip install -r 00_规范与工具/环境/requirements.lock.txt
# 重建后记得把 pyvenv.cfg 的 home 改回 E:\py312
```

## spine-player

站点页面 `02_wiki/web/spine_view.html` 通过相对路径
`assets/spine_runtime/3.8/...` 加载运行时。该路径是指向本目录 `spine-player/` 的
**目录 junction**，所以运行时只有一份，站点照常访问。

## everything

```bash
# 启动索引（挂后台，别用管道，会挂死）
00_规范与工具/环境/everything/everything.exe &
# 查询：按大小导出 CSV（注意 es.exe 输出是 GBK）
00_规范与工具/环境/everything/es.exe "size:>100mb" -path 'E:\' \
    -sort size-descending -n 1500 -csv -size -size-format 1 > big.csv
```

细节与坑（IPC 未启动、CSV 编码、`-reverse` 无效等）见技能 `windows-storage-cleanup`。
