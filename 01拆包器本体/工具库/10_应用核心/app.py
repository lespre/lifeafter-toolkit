# -*- coding: utf-8 -*-
"""明日之后 PC 离线资源拆包器 — 新 GUI。
只读 E:/mrzh、E:/lifeafter；所有派生产物默认写 E:/la拆包项目/03拆包产物，或由用户显式选择外置目录。
"""
from __future__ import annotations

import os
import json
import shutil
from pathlib import Path
from threading import Event
import sys

HERE = Path(__file__).resolve().parent
FROZEN = bool(getattr(sys, "frozen", False))
# one-file 模式下资源可在 _MEI 临时目录，但用户可见 output 必须贴着 EXE。
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", HERE.parent)) if FROZEN else HERE.parent
APP_HOME = Path(sys.executable).resolve().parent if FROZEN else HERE.parents[2]
INDEX_HOME = Path(sys.executable).resolve().parent if FROZEN else HERE.parents[1]  # exe 同级（内置索引/资产）
sys.path.insert(0, str(HERE))

from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QFileDialog, QFormLayout, QFrame, QHBoxLayout, QLabel,
    QLineEdit, QMainWindow, QMessageBox, QPlainTextEdit, QProgressBar,
    QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout,
    QWidget, QHeaderView,
)
from toolkit_core.job_runner import PackageJob, run_package_jobs
from toolkit_core.paths import DEFAULT_OUTPUT_ROOT, OutputPolicy, resolve_index_database
from toolkit_core.scheduler import JobKind, SmartScheduler
from toolkit_core.skin_chain import SkinCatalog
from toolkit_core.unified_index import IndexHit, IndexNotReady, UnifiedFileIndex
from toolkit_core.lines import DIRECTIONS, DataLine, classify_package, direction_by_key, select_containers

TOOLKIT = RESOURCE_ROOT
DEFAULT_GAME = Path("E:/mrzh")
DEFAULT_OUTPUT = DEFAULT_OUTPUT_ROOT
BEHAVIOR_EVIDENCE = Path("C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/体验服皮肤_behavior_res_Type5已验证链_001/体验服皮肤_behavior_res_Type5已验证链_001.json")
PHYSICAL_EVIDENCE = Path("C:/Users/Administrator/AppData/Local/hermes/mrzh_weapon_skin_audit/run_002/物理实体链路_001/物理资源链接摘要.json")


class Worker(QThread):
    log = Signal(str)
    progress = Signal(int, int, str)
    jobstart = Signal(int, int, str)
    done = Signal(bool, str)

    def __init__(self, jobs: list[PackageJob], readable: bool = False) -> None:
        super().__init__()
        self.jobs = jobs
        self.readable = readable
        self.pause_event, self.cancel_event = Event(), Event()

    def run(self) -> None:
        self._completed = 0

        def _progress(n, t, name):
            self._completed = n
            self.progress.emit(n, t, name)

        try:
            run_package_jobs(self.jobs, pause_event=self.pause_event, cancel_event=self.cancel_event,
                             on_progress=_progress, on_log=self.log.emit,
                             on_job_start=lambda n, t, name: self.jobstart.emit(n, t, name),
                             readable=self.readable)
            ok = not self.cancel_event.is_set()
            self.done.emit(ok, ("完成" if ok else "已取消") + f"（{self._completed}/{len(self.jobs)}）")
        except Exception as exc:
            self.done.emit(False, f"失败：{exc}（已完成 {self._completed}/{len(self.jobs)}）")


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("明日之后 PC 离线资源拆包器")
        self.resize(1120, 760)
        self.worker: Worker | None = None
        self.files: list[Path] = []
        self.file_lines: dict[Path, str] = {}
        self.index_hits: list[IndexHit] = []
        self.catalog = SkinCatalog()
        self._build()
        self._index_brief()
        QTimer.singleShot(0, self._auto_pick_by_direction)
        self.timer = QTimer(self); self.timer.timeout.connect(self._refresh_load); self.timer.start(1500)
        QTimer.singleShot(0, self._refresh_skins)

    def _build(self) -> None:
        root = QWidget(); self.setCentralWidget(root); layout = QVBoxLayout(root)
        title = QLabel("明日之后 PC 离线资源拆包器"); title.setObjectName("titleLabel")
        layout.addWidget(title)
        self.load_label = QLabel("资源监控：读取中…（上限：CPU/GPU 约 80%）"); self.load_label.setObjectName("mutedLabel")
        layout.addWidget(self.load_label)
        self.tabs = QTabWidget(); layout.addWidget(self.tabs, 1)
        self._build_jobs_tab(); self._build_skin_tab(); self._build_log_tab()
        self.statusBar().showMessage("就绪｜原始游戏目录只读｜output 外置")

    def _path_row(self, value: Path, on_browse) -> tuple[QLineEdit, QWidget]:
        edit = QLineEdit(str(value)); button = QPushButton("浏览…"); button.clicked.connect(lambda: on_browse(edit))
        row = QWidget(); lay = QHBoxLayout(row); lay.setContentsMargins(0, 0, 0, 0); lay.addWidget(edit, 1); lay.addWidget(button)
        return edit, row

    def _build_jobs_tab(self) -> None:
        tab = QWidget(); layout = QVBoxLayout(tab)
        form = QFormLayout()
        self.game_edit, game_row = self._path_row(DEFAULT_GAME, self._browse_dir)
        self.output_edit, output_row = self._path_row(DEFAULT_OUTPUT, self._browse_dir)
        form.addRow("游戏根目录（只读）", game_row); form.addRow("外置输出目录", output_row)
        layout.addLayout(form)
        hint = QLabel("防呆流程：勾选拆包方向 → 自动从内置索引选取待拆容器；可勾除个别包、双击『线路』格改线。大 FPK/GPK 同盘顺序解包；暂停/取消在当前包结束的安全边界生效。")
        hint.setWordWrap(True); hint.setObjectName("mutedLabel"); layout.addWidget(hint)
        self.index_info = QLabel("索引：检查中…"); self.index_info.setObjectName("mutedLabel"); layout.addWidget(self.index_info)
        direction = QHBoxLayout()
        self.dir_boxes: dict[str, QCheckBox] = {}
        for spec in DIRECTIONS:
            box = QCheckBox(spec.label); box.setChecked(True); box.setToolTip(spec.hint)
            self.dir_boxes[spec.key] = box; direction.addWidget(box)
        repick = QPushButton("重新选取"); repick.clicked.connect(self._auto_pick_by_direction)
        self.pick_summary = QLabel("待按方向自动选取…"); self.pick_summary.setObjectName("mutedLabel")
        self.readable_box = QCheckBox("解包后自动转可读"); self.readable_box.setToolTip("图像→PNG；bin/二进制→字符串表；原文件保留，产物写入 _readable/ 子目录")
        direction.addWidget(repick); direction.addWidget(self.readable_box); direction.addWidget(self.pick_summary, 1)
        layout.addLayout(direction)
        for box in self.dir_boxes.values(): box.stateChanged.connect(lambda *_: self._auto_pick_by_direction())
        controls = QHBoxLayout()
        add_btn = QPushButton("手动添加…"); add_btn.clicked.connect(self._add_files)
        clear_btn = QPushButton("清空队列"); clear_btn.clicked.connect(self._clear_files)
        self.start_btn = QPushButton("开始拆包"); self.start_btn.setObjectName("primaryButton"); self.start_btn.clicked.connect(self._start)
        self.pause_btn = QPushButton("暂停"); self.pause_btn.clicked.connect(self._toggle_pause); self.pause_btn.setEnabled(False)
        self.cancel_btn = QPushButton("取消"); self.cancel_btn.setObjectName("dangerButton"); self.cancel_btn.clicked.connect(self._cancel); self.cancel_btn.setEnabled(False)
        for b in (add_btn, clear_btn, self.start_btn, self.pause_btn, self.cancel_btn): controls.addWidget(b)
        controls.addStretch(); layout.addLayout(controls)
        self.file_table = QTableWidget(0, 5); self.file_table.setHorizontalHeaderLabels(["选", "文件", "格式", "大小", "线路"])
        self.file_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.file_table.setColumnWidth(0, 40); self.file_table.setColumnWidth(4, 96)
        self.file_table.cellDoubleClicked.connect(self._toggle_file_line)
        layout.addWidget(self.file_table, 1)
        self.progress = QProgressBar(); self.progress.setValue(0); layout.addWidget(self.progress)
        self.tabs.addTab(tab, "拆包任务")

    def _build_skin_tab(self) -> None:
        tab = QWidget(); layout = QVBoxLayout(tab)
        note = QLabel("专题：武器皮肤定位链 —— 以 3D 素材目录为起点、内置索引为定位器；逐皮肤列源引用与容器命中，可一键生成 Markdown 报告。双击一行＝打开该皮肤的 3D 预览。")
        note.setWordWrap(True); note.setObjectName("mutedLabel"); layout.addWidget(note)
        top = QHBoxLayout(); self.search_edit = QLineEdit(); self.search_edit.setPlaceholderText("按皮肤 ID / 名称过滤")
        search = QPushButton("过滤"); search.clicked.connect(self._search_skins)
        reload = QPushButton("刷新"); reload.clicked.connect(self._refresh_skins)
        report = QPushButton("生成报告"); report.clicked.connect(self._generate_skin_report)
        viewer = QPushButton("打开 3D 预览器"); viewer.clicked.connect(lambda: self._open_3d_viewer())
        top.addWidget(self.search_edit, 1); top.addWidget(search); top.addWidget(reload); top.addWidget(report); top.addWidget(viewer); layout.addLayout(top)
        self.skin_status = QLabel("皮肤数据：未载入"); self.skin_status.setObjectName("mutedLabel"); layout.addWidget(self.skin_status)
        self.skin_table = QTableWidget(0, 6)
        self.skin_table.setHorizontalHeaderLabels(["皮肤 ID", "名称", "3D 数据", "源引用", "索引命中", "状态"])
        self.skin_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.skin_table.cellDoubleClicked.connect(self._on_skin_double)
        layout.addWidget(self.skin_table, 1)
        self.tabs.addTab(tab, "皮肤定位链")

    def _index_database(self) -> Path:
        meipass = Path(sys._MEIPASS) if getattr(sys, "_MEIPASS", None) else None
        return resolve_index_database(output_dir=Path(self.output_edit.text()).resolve(), exe_dir=INDEX_HOME,
                                      default_root=DEFAULT_OUTPUT_ROOT, meipass=meipass)

    def _build_index_tab(self) -> None:
        tab = QWidget(); layout = QVBoxLayout(tab)
        note = QLabel("按逻辑路径查询统一 SQLite 索引。多命中会全部列出；提取前必须选择具体容器行。重建索引请运行：python run_all.py index build")
        note.setWordWrap(True); note.setObjectName("mutedLabel"); layout.addWidget(note)
        top = QHBoxLayout(); self.index_query = QLineEdit(); self.index_query.setPlaceholderText(r"例如 common\env_map\qiangpi.cube")
        query = QPushButton("查询"); query.clicked.connect(self._query_index)
        status = QPushButton("索引状态"); status.clicked.connect(self._index_status)
        extract = QPushButton("提取选中项…"); extract.clicked.connect(self._extract_index_hit)
        top.addWidget(self.index_query, 1); top.addWidget(query); top.addWidget(status); top.addWidget(extract); layout.addLayout(top)
        self.index_status = QLabel("尚未检查索引"); self.index_status.setWordWrap(True); layout.addWidget(self.index_status)
        self.index_table = QTableWidget(0, 7)
        self.index_table.setHorizontalHeaderLabels(["格式", "容器", "原始行", "压缩", "解压", "flag", "fid"])
        self.index_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        layout.addWidget(self.index_table, 1); self.tabs.addTab(tab, "文件索引")

    def _open_index(self) -> UnifiedFileIndex:
        return UnifiedFileIndex(self._index_database(), res_root=Path(self.game_edit.text()))

    def _index_brief(self) -> None:
        path = self._index_database()
        if path.is_file():
            size_gb = path.stat().st_size / (1024 ** 3)
            where = "已内置" if str(path).lower().startswith(str(INDEX_HOME).lower()) else "已定位"
            self.index_info.setText(f"索引：{where}｜{path}｜{size_gb:.2f} GB｜自动选包与皮肤定位均以它为准")
        else:
            self.index_info.setText("索引：未找到｜可在外置 output 下重建（python run_all.py index build）")

    def _index_status(self) -> None:
        try:
            with self._open_index() as index:
                status = index.status()
            text = (f"{status['rows']:,} 行｜quick_check={status['quick_check']}｜"
                    f"失败容器={status['failed_containers']}｜stale={status['stale']}")
            self.index_status.setText(text); self._log(f"索引状态：{text}")
        except (IndexNotReady, OSError, ValueError) as exc:
            self.index_status.setText(f"索引不可用：{exc}")

    def _query_index(self) -> None:
        logical = self.index_query.text().strip()
        if not logical:
            return QMessageBox.warning(self, "缺少路径", "请输入完整逻辑路径。")
        try:
            with self._open_index() as index:
                result = index.find(logical)
        except (IndexNotReady, OSError, ValueError) as exc:
            self.index_hits = []; self.index_table.setRowCount(0)
            return QMessageBox.critical(self, "查询失败", str(exc))
        self.index_hits = list(result.hits); self.index_table.setRowCount(len(self.index_hits))
        for i, hit in enumerate(self.index_hits):
            values = (hit.kind.upper(), hit.container, str(hit.row), str(hit.packed),
                      str(hit.decoded), str(hit.flag), hit.fid_hex)
            for j, value in enumerate(values): self.index_table.setItem(i, j, QTableWidgetItem(value))
        self.index_status.setText(f"{result.status}｜{len(result.hits)} 个物理候选｜fid 变体 {len(result.candidates)} 个")

    def _extract_index_hit(self) -> None:
        row = self.index_table.currentRow()
        if row < 0 or row >= len(self.index_hits):
            return QMessageBox.warning(self, "未选择条目", "请先查询并选择一个具体物理候选。")
        logical = self.index_query.text().strip(); name = Path(logical.replace("\\", "/")).stem + ".bin"
        default = Path(self.output_edit.text()).resolve() / "exports" / "indexed" / name
        selected, _ = QFileDialog.getSaveFileName(self, "保存解码后的资源", str(default), "所有文件 (*)")
        if not selected: return
        destination = Path(selected)
        if destination.exists():
            answer = QMessageBox.question(self, "确认覆盖", f"文件已存在：\n{destination}\n\n是否覆盖？")
            if answer != QMessageBox.Yes: return
        try:
            with self._open_index() as index:
                report = index.extract_hit(self.index_hits[row], destination, overwrite=destination.exists())
        except (IndexNotReady, OSError, ValueError, RuntimeError) as exc:
            return QMessageBox.critical(self, "提取失败", str(exc))
        self._log(f"索引提取：{logical} → {destination}｜{report['bytes']} B｜sha256={report['sha256']}")
        QMessageBox.information(self, "提取完成", f"已保存 {report['bytes']} B\nSHA256: {report['sha256']}")

    def _build_log_tab(self) -> None:
        tab = QWidget(); layout = QVBoxLayout(tab)
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); layout.addWidget(self.log_box)
        open_out = QPushButton("打开外置 output"); open_out.clicked.connect(self._open_output); layout.addWidget(open_out, alignment=Qt.AlignLeft)
        self.tabs.addTab(tab, "日志与产物")

    def _browse_dir(self, edit: QLineEdit) -> None:
        selected = QFileDialog.getExistingDirectory(self, "选择目录", edit.text())
        if selected: edit.setText(selected)

    def _add_files(self) -> None:
        paths, _ = QFileDialog.getOpenFileNames(self, "选择资源包", str(Path(self.game_edit.text()) / "res"), "资源包 (*.gpk *.fpk *.npk *.idx)")
        self.files.extend(Path(p) for p in paths if Path(p).is_file())
        self.files = list(dict.fromkeys(self.files))
        for p in self.files: self.file_lines.setdefault(p, classify_package(p).value)
        self._refresh_files()

    def _clear_files(self) -> None:
        if self.worker and self.worker.isRunning(): return
        self.files.clear(); self._refresh_files()

    def _refresh_files(self) -> None:
        self.file_table.setRowCount(len(self.files))
        for i, p in enumerate(self.files):
            line = self.file_lines.setdefault(p, classify_package(p).value)
            check = QTableWidgetItem(); check.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            check.setCheckState(Qt.CheckState.Checked)
            self.file_table.setItem(i, 0, check)
            for offset, text in enumerate((p.name, p.suffix.lower().lstrip("."), f"{p.stat().st_size / 1024 / 1024:.1f} MB", line)):
                item = QTableWidgetItem(text)
                if offset == 3: item.setToolTip("双击切换 文字线 / 渲染线")
                self.file_table.setItem(i, offset + 1, item)

    def _checked_files(self) -> list:
        out = []
        for i, p in enumerate(self.files):
            item = self.file_table.item(i, 0)
            if item is None or item.checkState() == Qt.CheckState.Checked:
                out.append(p)
        return out

    def _auto_pick_by_direction(self) -> None:
        keys = [k for k, box in self.dir_boxes.items() if box.isChecked()]
        game = Path(self.game_edit.text())
        try:
            with self._open_index() as index:
                rows = index.containers()
        except Exception as exc:
            self.pick_summary.setText(f"自动选取失败：{exc}")
            return
        names = [r["container"] for r in rows if r.get("status") == "ok"]
        picked = select_containers(names, keys)
        self.files = [game / name.replace("\\", "/") for name in picked]
        self.files = [p for p in self.files if p.is_file()]
        for p in self.files: self.file_lines.setdefault(p, classify_package(p).value)
        self._refresh_files()
        total = sum(p.stat().st_size for p in self.files) / 1024 ** 3
        labels = "＋".join((direction_by_key(k).line.folder if direction_by_key(k) else k) for k in keys) if keys else "未选方向"
        self.pick_summary.setText(f"方向 {labels}：已自动选取 {len(self.files)} 个容器（{total:.2f} GB）")
        self._log(f"按方向自动选取：{labels} → {len(self.files)} 个容器")

    def _toggle_file_line(self, row: int, col: int) -> None:
        if col != 4 or row < 0 or row >= len(self.files):
            return
        p = self.files[row]
        current = self.file_lines.get(p, classify_package(p).value)
        nxt = DataLine.RENDER.value if current == DataLine.TEXT.value else DataLine.TEXT.value
        self.file_lines[p] = nxt
        self.file_table.setItem(row, 4, QTableWidgetItem(nxt))
        self._log(f"分线切换：{p.name} → {nxt}")

    def _start(self) -> None:
        selected = self._checked_files()
        if not selected: return QMessageBox.warning(self, "未选择任务", "先勾选拆包方向自动选取，或在表格里勾选至少一个容器。")
        try:
            output = OutputPolicy(exe_dir=APP_HOME).resolve(self.output_edit.text(), source_root=self.game_edit.text())
        except (ValueError, OSError) as exc:
            return QMessageBox.critical(self, "输出目录无效", str(exc))
        jobs = [PackageJob(p, output, self.file_lines.get(p, classify_package(p).value)) for p in selected]
        text_n = sum(1 for j in jobs if j.line == DataLine.TEXT.value)
        self._log(f"分线：文字线 {text_n} 个｜渲染线 {len(jobs) - text_n} 个")
        kinds = [(JobKind.LARGE_ARCHIVE_READ if p.suffix.lower() in (".fpk", ".gpk") else JobKind.SMALL_SCAN, p, output) for p in self.files]
        plan = SmartScheduler(cpu_percent=self._cpu(), gpu_percent=0).plan(kinds)
        self._log(f"调度：CPU 上限 {plan.max_cpu_workers}，大包并发 {plan.large_archive_workers}，队列 {plan.queue_size}；output={output}")
        self._log(f"可读化：{'开' if self.readable_box.isChecked() else '关'}")
        self.worker = Worker(jobs, readable=self.readable_box.isChecked()); self.worker.log.connect(self._log); self.worker.progress.connect(self._on_progress); self.worker.jobstart.connect(self._on_job_start); self.worker.done.connect(self._done)
        self.start_btn.setEnabled(False); self.pause_btn.setEnabled(True); self.cancel_btn.setEnabled(True); self.worker.start()

    def _toggle_pause(self) -> None:
        if not self.worker: return
        if self.worker.pause_event.is_set(): self.worker.pause_event.clear(); self.pause_btn.setText("暂停"); self._log("恢复：下一个安全边界继续")
        else: self.worker.pause_event.set(); self.pause_btn.setText("继续"); self._log("暂停请求已登记：当前包完成后暂停")

    def _cancel(self) -> None:
        if self.worker: self.worker.cancel_event.set(); self._log("取消请求已登记：不会中断当前写入，当前包结束后停止")

    def _on_job_start(self, n: int, total: int, name: str) -> None:
        self.progress.setRange(0, 0)  # 大包解包期间走马灯：进度条可见地在动
        self.statusBar().showMessage(f"正在拆包 {n}/{total}：{name}（大包耗时长，完成后推进）")

    def _on_progress(self, n: int, total: int, name: str) -> None:
        self.progress.setRange(0, total); self.progress.setValue(n); self.statusBar().showMessage(f"已完成 {n}/{total}：{name}")

    def _done(self, ok: bool, text: str) -> None:
        self._log(("✅ " if ok else "⚠️ ") + text)
        self.progress.setRange(0, 100); self.progress.setValue(100 if ok else 0)
        self.statusBar().showMessage(text)
        self.start_btn.setEnabled(True); self.pause_btn.setEnabled(False); self.cancel_btn.setEnabled(False); self.pause_btn.setText("暂停")

    def _skin_assets_root(self) -> Path:
        return INDEX_HOME / "3D预览器" / "poster" / "assets" / "3d" / "weapon_skin"

    def _refresh_skins(self) -> None:
        from toolkit_core.skin_report import collect_skins, locate_refs
        root = self._skin_assets_root()
        try:
            self.skin_rows = collect_skins(root)
        except Exception as exc:
            self.skin_status.setText(f"皮肤数据载入失败：{exc}")
            return
        try:
            with self._open_index() as index:
                locate_refs(self.skin_rows, index)
        except Exception as exc:
            self._log(f"索引定位跳过：{exc}")
        self._render_skin_rows(self.skin_rows)
        total = sum(r.get("path_total", 0) for r in self.skin_rows)
        ok = sum(r.get("path_hits", 0) for r in self.skin_rows)
        self.skin_status.setText(f"皮肤 {len(self.skin_rows)} 个｜路径定位 {ok}/{total}｜双击一行＝打开 3D 预览")

    def _render_skin_rows(self, rows) -> None:
        self.skin_table.setRowCount(len(rows))
        for i, r in enumerate(rows):
            values = (r["skin_id"], r.get("title") or "—", r.get("data_summary") or "—",
                      str(len(r.get("refs", []))), r.get("hit_summary") or "—", r.get("state") or "")
            for j, v in enumerate(values):
                self.skin_table.setItem(i, j, QTableWidgetItem(str(v)))

    def _search_skins(self) -> None:
        q = self.search_edit.text().strip().lower()
        rows = [r for r in getattr(self, "skin_rows", [])
                if not q or q in r["skin_id"].lower() or q in (r.get("title") or "").lower()]
        self._render_skin_rows(rows)

    def _on_skin_double(self, row: int, _col: int) -> None:
        rows = getattr(self, "skin_rows", [])
        if 0 <= row < len(rows):
            self._open_3d_viewer(rows[row]["skin_id"])

    def _generate_skin_report(self) -> None:
        from toolkit_core.skin_report import build_markdown_report
        if not getattr(self, "skin_rows", None):
            return QMessageBox.warning(self, "暂无数据", "先「刷新」载入皮肤数据。")
        try:
            with self._open_index() as index:
                out = build_markdown_report(self.skin_rows, index, log=self._log)
        except Exception as exc:
            return QMessageBox.warning(self, "报告失败", str(exc))
        self._log(f"📄 报告已生成：{out}")
        QMessageBox.information(self, "报告已生成", str(out))

    def _open_3d_viewer(self, skin_id=None) -> None:
        root = INDEX_HOME / "3D预览器" / "poster"
        if not (root / "index.html").exists():
            return QMessageBox.warning(self, "未找到预览器", f"缺少：{root}")
        try:
            url = start_viewer_server(root)
            target = f"{url}/index.html" + (f"?open={skin_id}" if skin_id else "")
            self._log(f"3D 预览器（本地服务）：{target}")
            QTimer.singleShot(300, lambda u=target: os.startfile(u))
        except Exception as exc:
            QMessageBox.warning(self, "预览器启动失败", str(exc))

    def _open_output(self) -> None:
        target = Path(self.output_edit.text())
        target.mkdir(parents=True, exist_ok=True); os.startfile(target)

    def _log(self, message: str) -> None:
        self.log_box.appendPlainText(message)

    def _cpu(self) -> float:
        try:
            import psutil; return psutil.cpu_percent(interval=None)
        except Exception: return 0.0

    def _refresh_load(self) -> None:
        self.load_label.setText(f"资源监控：CPU {self._cpu():.0f}%｜GPU 监控：未接入驱动计数器｜策略：最多使用约 80% CPU，FPK/GPK 顺序读取")


def start_viewer_server(root: Path) -> str:
    """本地只读小服务：3D 预览器 fetch/模块导入走 http；按缝合指南补齐 .glb/.dds 等 MIME。"""
    import functools, http.server, socket, socketserver, threading

    class _Handler(http.server.SimpleHTTPRequestHandler):
        extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
                          ".glb": "model/gltf-binary", ".gltf": "model/gltf+json",
                          ".dds": "image/vnd-ms.dds", ".ktx": "image/ktx",
                          ".wasm": "application/wasm", ".js": "text/javascript",
                          ".json": "application/json"}

    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0)); port = probe.getsockname()[1]
    handler = functools.partial(_Handler, directory=str(root))
    httpd = socketserver.ThreadingTCPServer(("127.0.0.1", port), handler)
    httpd.daemon_threads = True
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}"


def main() -> int:
    # 冻结版自检不依赖 GUI；必须在 QApplication 之前执行，避免平台插件或
    # 参数处理干扰无人值守验收。
    launch_args = set(sys.argv[1:])
    smoke_mode = os.environ.get("LIFEAFTER_SMOKE", "").strip().lower()
    if "--smoke" in launch_args or smoke_mode == "basic":
        # 仅用于打包后验证：证明 output 不会落在 _MEIPASS，不读游戏数据。
        output = OutputPolicy(exe_dir=APP_HOME).resolve(None, source_root=DEFAULT_GAME)
        proof = output / "logs" / "exe_smoke.json"
        proof.write_text(json.dumps({"status": "SMOKE_OK", "output": str(output), "frozen": FROZEN}, ensure_ascii=False), encoding="utf-8")
        print(f"SMOKE_OK output={output}", flush=True)
        return 0
    if "--index-smoke" in launch_args or smoke_mode == "index":
        output = OutputPolicy(exe_dir=APP_HOME).resolve(None, source_root=DEFAULT_GAME)
        proof = output / "logs" / "exe_index_smoke.json"
        try:
            meipass = Path(sys._MEIPASS) if getattr(sys, "_MEIPASS", None) else None
            database = resolve_index_database(output_dir=output, exe_dir=INDEX_HOME,
                                              default_root=DEFAULT_OUTPUT_ROOT, meipass=meipass)
            with UnifiedFileIndex(database, res_root=DEFAULT_GAME) as index:
                result = index.find(r"common\env_map\qiangpi.cube")
                chosen = next(h for h in result.hits if h.container.lower() == "res.npk" and h.row == 14213)
                extracted = index.extract_hit(chosen, output / "logs" / "exe_index_smoke_qiangpi.dds", overwrite=True)
            passed = extracted["sha256"] == "173d52990b3ab8364a43ac6367c362d63b21bdaf8b8dc1b2a760ec5c13aee609"
            report = {"status": "PASS" if passed else "FAIL", "database": str(database), "hits": len(result.hits), "extract": extracted}
        except Exception as exc:
            passed = False; report = {"status": "ERROR", "error": repr(exc)}
        proof.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"INDEX_SMOKE_{report['status']} proof={proof}", flush=True)
        return 0 if passed else 4
    if "--viewer-smoke" in launch_args or smoke_mode == "viewer":
        root = INDEX_HOME / "3D预览器" / "poster"
        proof = DEFAULT_OUTPUT_ROOT / "logs" / "exe_viewer_smoke.json"
        try:
            url = start_viewer_server(root)
            import urllib.request
            body = urllib.request.urlopen(url + "/index.html", timeout=15).read()
            passed = len(body) > 1000
            report = {"status": "PASS" if passed else "FAIL", "url": url, "bytes": len(body), "root": str(root)}
        except Exception as exc:
            passed = False; report = {"status": "ERROR", "error": repr(exc), "root": str(root)}
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"VIEWER_SMOKE_{report['status']} proof={proof}", flush=True)
        return 0 if passed else 4
    if "--unpack-smoke" in launch_args or smoke_mode == "unpack":
        from threading import Event
        src = Path(r"E:\mrzh\res\scene_bw\bigworld\bigworld_cut_content.npk")
        out_root = DEFAULT_OUTPUT_ROOT / "logs" / "_unpack_smoke"
        proof = DEFAULT_OUTPUT_ROOT / "logs" / "exe_unpack_smoke.json"
        try:
            if out_root.exists(): shutil.rmtree(out_root)
            run_package_jobs([PackageJob(src, out_root, "文字线")], pause_event=Event(), cancel_event=Event(),
                             on_progress=lambda *a: None, on_log=lambda *a: None, readable=True)
            files = [p for p in out_root.rglob("*") if p.is_file()]
            passed = len(files) >= 1
            readable_files = [p for p in out_root.rglob('*') if p.is_file() and '_readable' in p.parts]
            report = {"status": "PASS" if passed else "FAIL", "files": len(files),
                      "readable_files": len(readable_files),
                      "source": str(src), "output": str(out_root)}
        except Exception as exc:
            passed = False; report = {"status": "ERROR", "error": repr(exc)}
        proof.parent.mkdir(parents=True, exist_ok=True)
        proof.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"UNPACK_SMOKE_{report['status']} proof={proof}", flush=True)
        return 0 if passed else 4
    app = QApplication(sys.argv)
    qss = TOOLKIT / "08_GUI界面" / "shadcn.qss"
    if qss.exists(): app.setStyleSheet(qss.read_text(encoding="utf-8"))
    window = MainWindow(); window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
