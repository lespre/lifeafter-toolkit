# -*- coding: utf-8 -*-
"""FPK 场景对象提取器（明日之后 / NeoX OpenWorld 流式包）。

用途：
  013/020/021 等非标准 FPK 不是“加密网格”，而是 NeoX OpenWorld 大世界场景包：
    - zstd 对象帧：序列化场景对象，明文含 .gim 模型路径 / 材质 / shader / AABB 等，可直接读；
    - raw 几何帧：自研几何压缩（位打包，卡方非均匀、非密码学加密），解压算法在客户端 exe 内，
      本工具只记录大小与统计指纹，不强解。
  普通 FPK（001 等）同样可用，逐帧分类并导出对象引用。

只读源包；产物写 DEFAULT_OUTPUT_ROOT/fpk_scene/<包名>/：
  - frame_manifest.json   每帧 storage/大小/对象引用数/raw 指纹
  - model_refs.csv        场景引用的 .gim/.mesh 等模型路径与次数
  - asset_refs.csv        材质/shader/纹理等其他资源引用与次数
  - strings.txt           对象帧全部 ASCII(>=4) 字符串，便于回查
  - report.md             人读汇总

用法：
  python fpk_scene_extractor.py <fpk文件> [--max-frames N]
  python fpk_scene_extractor.py --batch 013,020,021
"""
from __future__ import annotations
import argparse, csv, collections, math, re, sys, json
from pathlib import Path

APP_CORE = Path(__file__).resolve().parent.parent / "10_应用核心"
if str(APP_CORE) not in sys.path:
    sys.path.insert(0, str(APP_CORE))
from toolkit_core.fpk_frames import iter_fpk_frames
from toolkit_core.paths import DEFAULT_OUTPUT_ROOT

RES = Path(r"E:/mrzh/res")
STR_RE = re.compile(rb"[\x20-\x7e]{4,}")
MODEL_RE = re.compile(rb"[A-Za-z0-9_./\-]+\.(?:gim|mesh|model)")
ASSET_RE = re.compile(rb"[A-Za-z0-9_./\-]+\.(?:fx|tga|dds|png|jpg|material|mat|anim|shader|phy|nav)")


def shannon_entropy(b: bytes) -> float:
    if not b:
        return 0.0
    c = collections.Counter(b); n = len(b)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def chi2_uniform(b: bytes) -> float:
    """与均匀分布的卡方距离（df=255：随机≈255，>360 显著非均匀）。"""
    c = collections.Counter(b); n = len(b); e = n / 256
    if e == 0:
        return 0.0
    return round(sum((c.get(i, 0) - e) ** 2 / e for i in range(256)), 1)


def classify_frame(out: bytes) -> str:
    if out.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if out.startswith(b"DDS "):
        return "dds"
    if out[:1] in (b"{", b"["):
        return "json"
    if MODEL_RE.search(out[:4096]) or b"lod1model" in out[:8192] or b"Cluster" in out[:8192]:
        return "scene_object"
    return "other"


def extract_one(fpk: Path, max_frames: int | None = None) -> dict:
    out_dir = DEFAULT_OUTPUT_ROOT / "fpk_scene" / fpk.stem
    out_dir.mkdir(parents=True, exist_ok=True)

    frames = []
    model_refs = collections.Counter()
    asset_refs = collections.Counter()
    strings_dump = []
    raw_total = 0
    zstd_total = 0

    for fi, (fr, out) in enumerate(iter_fpk_frames(fpk)):
        if max_frames and fi >= max_frames:
            break
        row = {
            "idx": fr.index, "storage": fr.storage,
            "packed": fr.packed_size, "out": fr.output_size,
        }
        if fr.storage == "raw":
            raw_total += len(out)
            row["kind"] = "raw_geometry"
            row["entropy"] = round(shannon_entropy(out[:65536]), 3)
            row["chi2"] = chi2_uniform(out[:65536])
        else:
            zstd_total += len(out)
            kind = classify_frame(out)
            row["kind"] = kind
            ss = [m.group(0) for m in STR_RE.finditer(out)]  # bytes
            row["str_count"] = len(ss)
            for s in ss:
                sl = s.lower()
                for mm in MODEL_RE.findall(sl):
                    model_refs[mm.decode("ascii", "ignore")] += 1
                for am in ASSET_RE.findall(sl):
                    asset_refs[am.decode("ascii", "ignore")] += 1
            if kind in ("scene_object", "json", "other") and ss:
                strings_dump.append(f"\n===== frame#{fr.index} ({kind}) =====")
                strings_dump.extend(x.decode("ascii", "ignore") for x in ss)
        frames.append(row)

    # 模型引用 CSV（折叠 lod0/lod1 到同一基模）
    with (out_dir / "model_refs.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["resource_path", "ref_count"])
        for k, v in sorted(model_refs.items(), key=lambda x: -x[1]):
            w.writerow([k, v])
    with (out_dir / "asset_refs.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f); w.writerow(["resource_path", "ref_count"])
        for k, v in sorted(asset_refs.items(), key=lambda x: -x[1]):
            w.writerow([k, v])
    (out_dir / "frame_manifest.json").write_text(
        json.dumps({"source": str(fpk), "frames": frames}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    (out_dir / "strings.txt").write_text("\n".join(strings_dump), encoding="utf-8", errors="replace")

    kinds = collections.Counter(r["kind"] for r in frames)
    report = [
        f"# {fpk.name} 场景对象提取报告", "",
        f"- 源文件：`{fpk}`（只读）",
        f"- 总帧数：{len(frames)}；类型分布：{dict(kinds)}",
        f"- zstd 对象帧合计 {zstd_total/1024/1024:.1f}MB；raw 几何帧合计 {raw_total/1024/1024:.1f}MB",
        f"- 模型引用去重后 {len(model_refs)} 个；其他资源引用 {len(asset_refs)} 个", "",
        "## 说明",
        "- raw_geometry 为 NeoX 自研几何压缩（卡方非均匀=非加密，位打包高紧凑），解压依赖客户端 exe，本工具不强解。",
        "- scene_object 帧可直接读取模型/材质引用，是场景构成的可读入口。", "",
        "## Top 模型引用",
    ]
    for k, v in sorted(model_refs.items(), key=lambda x: -x[1])[:30]:
        report.append(f"- `{k}` ×{v}")
    (out_dir / "report.md").write_text("\n".join(report), encoding="utf-8")

    return {
        "fpk": fpk.name, "frames": len(frames), "kinds": dict(kinds),
        "models": len(model_refs), "assets": len(asset_refs),
        "raw_mb": round(raw_total/1024/1024, 1), "zstd_mb": round(zstd_total/1024/1024, 1),
        "out_dir": str(out_dir),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("fpk", nargs="?", help="单个 fpk 文件路径")
    ap.add_argument("--batch", help="逗号分隔的包名，如 013,020,021")
    ap.add_argument("--max-frames", type=int, default=None)
    a = ap.parse_args()
    targets = []
    if a.batch:
        targets = [RES / f"{n.strip().zfill(3)}.fpk" for n in a.batch.split(",")]
    elif a.fpk:
        targets = [Path(a.fpk)]
    else:
        ap.print_help(); return
    for t in targets:
        if not t.exists():
            print("缺失:", t); continue
        print(f"处理 {t.name} ...")
        info = extract_one(t, a.max_frames)
        print(json.dumps(info, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
