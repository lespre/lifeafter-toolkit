# -*- coding: utf-8 -*-
"""
明日之后资源拆包器 v2.0 (PySide6/Qt 版)
功能：拆包 / 预览 / 属性
"""
import sys, os, json, time, struct, threading, io, re

# 把拆包器目录加入路径（同目录即可，无需额外路径）
UNPACKER_DIR = os.path.dirname(os.path.abspath(__file__))
if UNPACKER_DIR not in sys.path:
    sys.path.insert(0, UNPACKER_DIR)

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QPushButton, QRadioButton, QCheckBox,
    QButtonGroup, QProgressBar, QTextEdit, QTreeView, QSplitter,
    QScrollArea, QGroupBox, QFormLayout, QDoubleSpinBox, QFileDialog,
    QMessageBox, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QSize
from PySide6.QtGui import QPixmap, QImage, QFont, QIcon, QPainter, QColor, QBrush

try:
    from lifeafter_unpacker_full import (
        extract_gpk, extract_fpk_full, search_fpk, search_all_fpk,
        extract_npk, dds2png, ext_of
    )
    UNPACKER_READY = True
    UNPACKER_ERROR = ""
except Exception as e:
    UNPACKER_READY = False
    UNPACKER_ERROR = str(e)

DEFAULT_GAME_DIR = r'E:\mrzh'
DEFAULT_RES_DIR = r'E:\mrzh\res'
DEFAULT_OFFICIAL_DIR = r'E:\lifeafter\res'
DEFAULT_OUTPUT_DIR = r'E:\la拆包项目\03拆包产物'


class UnpackWorker(QThread):
    """拆包工作线程"""
    log_signal = Signal(str)
    progress_signal = Signal(int)
    finished_signal = Signal()

    def __init__(self, mode, res_dir, output_dir, file_types, keywords=None):
        super().__init__()
        self.mode = mode
        self.res_dir = res_dir
        self.output_dir = output_dir
        self.file_types = file_types
        self.keywords = keywords or []
        self.running = True

    def stop(self):
        self.running = False

    def log(self, msg):
        self.log_signal.emit("[%s] %s" % (time.strftime("%H:%M:%S"), msg))

    def run(self):
        try:
            self.log("模式: %s" % self.mode)
            self.log("资源目录: %s" % self.res_dir)
            self.log("输出目录: %s" % self.output_dir)
            self.log("文件类型: %s" % self.file_types)

            if self.mode == "定向搜索":
                self.log("关键词: %s" % self.keywords)
                if "fpk" in self.file_types or "全部" in self.file_types:
                    self.log("开始搜索体验服独有 fpk...")
                    search_all_fpk(self.res_dir, self.keywords,
                                   os.path.join(self.output_dir, 'fpk_search'),
                                   only_exclusive=True, official_dir=DEFAULT_OFFICIAL_DIR)
                if "gpk" in self.file_types or "全部" in self.file_types:
                    self._scan_gpk()

            elif self.mode == "全量拆包":
                files = [f for f in os.listdir(self.res_dir)
                        if any(f.lower().endswith('.'+t) for t in self.file_types)]
                self.log("待解包文件: %d 个" % len(files))
                for i, f in enumerate(files):
                    if not self.running: break
                    fp = os.path.join(self.res_dir, f)
                    ext = os.path.splitext(f)[1].lower()
                    self.log("[%d/%d] 解包 %s..." % (i+1, len(files), f))
                    try:
                        if ext == '.gpk':
                            extract_gpk(fp, os.path.join(self.output_dir, 'gpk', f[:-4]))
                        elif ext == '.fpk':
                            extract_fpk_full(fp, os.path.join(self.output_dir, 'fpk', f[:-4]))
                        elif ext == '.npk':
                            extract_npk(fp, os.path.join(self.output_dir, 'npk', f[:-4]))
                    except Exception as e:
                        self.log("  失败: %s" % str(e)[:100])
                    self.progress_signal.emit(int((i+1)/len(files)*100))

            elif self.mode == "近30天内更新":
                import time as _time
                cutoff = _time.time() - 30 * 86400
                files = []
                for f in os.listdir(self.res_dir):
                    fp = os.path.join(self.res_dir, f)
                    if os.path.getmtime(fp) > cutoff and any(f.lower().endswith('.'+t) for t in self.file_types):
                        files.append(f)
                self.log("近30天更新文件: %d 个" % len(files))
                for i, f in enumerate(files):
                    if not self.running: break
                    self.log("[%d/%d] 解包 %s..." % (i+1, len(files), f))
                    ext = os.path.splitext(f)[1].lower()
                    try:
                        if ext == '.gpk':
                            extract_gpk(os.path.join(self.res_dir, f), os.path.join(self.output_dir, 'gpk', f[:-4]))
                        elif ext == '.fpk':
                            extract_fpk_full(os.path.join(self.res_dir, f), os.path.join(self.output_dir, 'fpk', f[:-4]))
                    except Exception as e:
                        self.log("  失败: %s" % str(e)[:100])
                    self.progress_signal.emit(int((i+1)/len(files)*100))

            self.log("拆包完成!")
        except Exception as e:
            self.log("错误: %s" % str(e))
        finally:
            self.finished_signal.emit()

    def _scan_gpk(self):
        """扫描 gpk 明文签名"""
        os.makedirs(os.path.join(self.output_dir, 'gpk_search'), exist_ok=True)
        gpks = [f for f in os.listdir(self.res_dir) if f.lower().endswith('.gpk')]
        self.log("扫描 %d 个 gpk 文件..." % len(gpks))
        total = 0
        for gi, gname in enumerate(gpks):
            if not self.running: break
            try:
                data = open(os.path.join(self.res_dir, gname), 'rb').read()
                png_count = len([m for m in re.finditer(b'\x89PNG', data)])
                dds_count = len([m for m in re.finditer(b'DDS ', data)])
                self.log("  %s: PNG=%d DDS=%d" % (gname, png_count, dds_count))
                total += png_count + dds_count
            except Exception as e:
                self.log("  %s: 扫描失败 %s" % (gname, str(e)[:50]))
            self.progress_signal.emit(int((gi+1)/len(gpks)*100))
        self.log("gpk 签名扫描完成，共 %d 个纹理签名" % total)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("明日之后资源拆包器 v2.0")
        self.resize(1280, 820)
        self.setMinimumSize(1000, 700)
        self.worker = None
        self._build_ui()
        self._log("拆包器已启动" + ("" if UNPACKER_READY else "（模块加载失败: %s）" % UNPACKER_ERROR))

    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(14)

        # 标题区
        title_row = QHBoxLayout()
        title_col = QVBoxLayout()
        title_label = QLabel("明日之后资源拆包器")
        title_label.setObjectName("titleLabel")
        title_col.addWidget(title_label)
        subtitle_label = QLabel("gpk / fpk / npk / nxs 全格式解包 · 定向搜索 · 贴图预览")
        subtitle_label.setObjectName("subtitleLabel")
        title_col.addWidget(subtitle_label)
        title_row.addLayout(title_col)
        title_row.addStretch()
        main_layout.addLayout(title_row)

        # 顶部路径栏
        path_group = QGroupBox("路径设置")
        path_layout = QFormLayout(path_group)
        path_layout.setHorizontalSpacing(12)
        path_layout.setVerticalSpacing(8)
        self.game_dir_edit = QLineEdit(DEFAULT_GAME_DIR)
        self.output_dir_edit = QLineEdit(DEFAULT_OUTPUT_DIR)
        path_layout.addRow("游戏目录:", self._browse_row(self.game_dir_edit))
        path_layout.addRow("输出目录:", self._browse_row(self.output_dir_edit))
        main_layout.addWidget(path_group)

        # 标签页
        self.notebook = QTabWidget()
        main_layout.addWidget(self.notebook, 1)
        self._build_unpack_tab()
        self._build_preview_tab()

        # 状态栏
        self.status_label = QLabel("就绪")
        self.statusBar().addWidget(self.status_label)

    def _browse_row(self, line_edit):
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(line_edit, 1)
        btn = QPushButton("浏览")
        btn.clicked.connect(lambda: self._browse_dir(line_edit))
        lay.addWidget(btn)
        return w

    def _browse_dir(self, line_edit):
        d = QFileDialog.getExistingDirectory(self, "选择目录", line_edit.text())
        if d:
            line_edit.setText(d)

    def _build_unpack_tab(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        # 左侧控制面板
        left = QWidget()
        left.setFixedWidth(310)
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(12)

        # --- 拆包模式卡片 ---
        mode_card = self._make_card("拆包模式")
        mode_lay = mode_card.layout()
        self.mode_group = QButtonGroup(self)
        for i, mode in enumerate(["全量拆包", "近30天内更新", "定向搜索"]):
            rb = QRadioButton(mode)
            rb.setMinimumHeight(28)
            if i == 2: rb.setChecked(True)
            self.mode_group.addButton(rb, i)
            rb.toggled.connect(self._on_mode_change)
            mode_lay.addWidget(rb)
        left_lay.addWidget(mode_card)

        # --- 文件类型卡片 ---
        type_card = self._make_card("文件类型")
        type_lay = type_card.layout()
        self.type_checks = {}
        # 两行三列布局，避免垂直重叠
        type_grid = QVBoxLayout()
        type_grid.setSpacing(6)
        row1 = QHBoxLayout()
        row2 = QHBoxLayout()
        row1.setSpacing(4)
        row2.setSpacing(4)
        for idx, ft in enumerate(["gpk", "fpk", "npk", "nxs", "wpk", "全部"]):
            cb = QCheckBox(ft.upper())
            cb.setMinimumHeight(28)
            if ft == "全部": cb.setChecked(True)
            self.type_checks[ft] = cb
            (row1 if idx < 3 else row2).addWidget(cb)
        type_grid.addLayout(row1)
        type_grid.addLayout(row2)
        type_lay.addLayout(type_grid)
        left_lay.addWidget(type_card)

        # --- 搜索关键词卡片 ---
        self.kw_group = self._make_card("搜索关键词")
        kw_lay = self.kw_group.layout()
        self.kw_edit = QLineEdit("战神烈火剑 极光剑 帝皇裁决 AUG 武器皮肤")
        self.kw_edit.setMinimumHeight(32)
        kw_lay.addWidget(self.kw_edit)
        left_lay.addWidget(self.kw_group)

        # 按钮
        self.start_btn = QPushButton("开始拆包")
        self.start_btn.setObjectName("primaryButton")
        self.start_btn.setMinimumHeight(38)
        self.start_btn.clicked.connect(self._start_unpack)
        left_lay.addWidget(self.start_btn)
        self.stop_btn = QPushButton("停止")
        self.stop_btn.setObjectName("dangerButton")
        self.stop_btn.setMinimumHeight(34)
        self.stop_btn.clicked.connect(self._stop_unpack)
        self.stop_btn.setEnabled(False)
        left_lay.addWidget(self.stop_btn)

        # 进度
        progress_label = QLabel("进度")
        progress_label.setObjectName("mutedLabel")
        left_lay.addWidget(progress_label)
        self.progress = QProgressBar()
        self.progress.setMinimumHeight(24)
        left_lay.addWidget(self.progress)
        left_lay.addStretch()

        lay.addWidget(left)

        # 右侧日志
        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(8)
        log_label = QLabel("运行日志")
        log_label.setObjectName("mutedLabel")
        right_lay.addWidget(log_label)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        right_lay.addWidget(self.log_text, 1)
        lay.addWidget(right, 1)

        self.notebook.addTab(tab, "拆包")

    def _make_card(self, title):
        """创建带标题的卡片容器"""
        card = QFrame()
        card.setObjectName("card")
        lay = QVBoxLayout(card)
        lay.setContentsMargins(14, 12, 14, 14)
        lay.setSpacing(10)
        title_label = QLabel(title)
        title_label.setObjectName("cardTitle")
        lay.addWidget(title_label)
        return card

    def _build_preview_tab(self):
        tab = QWidget()
        lay = QHBoxLayout(tab)

        # 左侧文件浏览器
        left = QWidget()
        left.setFixedWidth(350)
        left_lay = QVBoxLayout(left)
        btn_row = QHBoxLayout()
        load_btn = QPushButton("加载目录")
        load_btn.clicked.connect(self._load_preview_dir)
        btn_row.addWidget(load_btn)
        refresh_btn = QPushButton("刷新")
        refresh_btn.clicked.connect(self._refresh_preview)
        btn_row.addWidget(refresh_btn)
        left_lay.addLayout(btn_row)

        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(False)
        left_lay.addWidget(self.file_tree, 1)
        lay.addWidget(left)

        # 右侧预览
        right = QWidget()
        right_lay = QVBoxLayout(right)
        self.preview_info = QLabel("选择文件查看预览")
        self.preview_info.setStyleSheet("color:gray;")
        right_lay.addWidget(self.preview_info)

        self.preview_scroll = QScrollArea()
        self.preview_scroll.setWidgetResizable(True)
        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("background:#222;color:#888;padding:20px;")
        self.preview_label.setText("图片预览区")
        self.preview_scroll.setWidget(self.preview_label)
        right_lay.addWidget(self.preview_scroll, 1)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        right_lay.addWidget(self.preview_text)

        lay.addWidget(right, 1)
        self.notebook.addTab(tab, "预览")
        self._preview_model = None

    # ==================== 拆包功能 ====================
    def _on_mode_change(self):
        mode = self.mode_group.checkedButton().text() if self.mode_group.checkedButton() else ""
        self.kw_group.setVisible(mode == "定向搜索")

    def _start_unpack(self):
        if self.worker and self.worker.isRunning():
            return
        if not UNPACKER_READY:
            QMessageBox.critical(self, "错误", "拆包器模块加载失败:\n" + UNPACKER_ERROR)
            return
        mode = self.mode_group.checkedButton().text()
        game_dir = self.game_dir_edit.text()
        # 自动识别资源目录：游戏目录下的 res 子目录
        res_dir = os.path.join(game_dir, 'res')
        if not os.path.exists(res_dir):
            # 尝试直接用游戏目录作为资源目录
            res_dir = game_dir
        output_dir = self.output_dir_edit.text()
        file_types = [k for k, v in self.type_checks.items() if v.isChecked()]
        keywords = self.kw_edit.text().split() if mode == "定向搜索" else None

        self.worker = UnpackWorker(mode, res_dir, output_dir, file_types, keywords)
        self.worker.log_signal.connect(self._log)
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished_signal.connect(self._on_unpack_finished)
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.worker.start()

    def _stop_unpack(self):
        if self.worker:
            self.worker.stop()
            self._log("用户停止拆包")

    def _on_unpack_finished(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.progress.setValue(0)
        self.status_label.setText("就绪")

    # ==================== 预览功能 ====================
    def _load_preview_dir(self):
        d = QFileDialog.getExistingDirectory(self, "选择预览目录", self.output_dir_edit.text())
        if d:
            self._preview_root = d
            self._refresh_preview()

    def _refresh_preview(self):
        if not hasattr(self, '_preview_root') or not os.path.exists(self._preview_root):
            return
        from PySide6.QtWidgets import QFileSystemModel
        if self._preview_model is None:
            self._preview_model = QFileSystemModel()
            self._preview_model.setRootPath(self._preview_root)
            self.file_tree.setModel(self._preview_model)
            self.file_tree.setRootIndex(self._preview_model.index(self._preview_root))
            self.file_tree.clicked.connect(self._on_file_select)
        else:
            self._preview_model.setRootPath(self._preview_root)
            self.file_tree.setRootIndex(self._preview_model.index(self._preview_root))

    def _on_file_select(self, index):
        path = self._preview_model.filePath(index)
        if not os.path.isfile(path):
            return
        ext = os.path.splitext(path)[1].lower()
        size = os.path.getsize(path)
        self.preview_info.setText("%s (%.1f KB)" % (os.path.basename(path), size/1024))

        if ext in ('.png', '.jpg', '.jpeg', '.bmp', '.gif'):
            self._show_image(path)
        elif ext == '.dds':
            tmp = os.path.join(os.environ.get('TEMP', '/tmp'), '_preview_dds.png')
            if dds2png(path, tmp):
                self._show_image(tmp)
            else:
                self.preview_text.setText("DDS 解码失败")
        elif ext in ('.txt', '.json', '.xml', '.csv', '.md'):
            try:
                data = open(path, 'r', encoding='utf-8', errors='ignore').read(10000)
                self.preview_text.setText(data)
                self.preview_label.setText("文本文件")
                self.preview_label.setPixmap(QPixmap())
            except Exception as e:
                self.preview_text.setText("读取失败: %s" % str(e))
        else:
            self.preview_text.setText("不支持的格式: %s\n\n十六进制预览:\n" % ext)
            try:
                data = open(path, 'rb').read(256)
                self.preview_text.insertPlainText(data.hex())
            except:
                pass
            self.preview_label.setText("二进制文件")
            self.preview_label.setPixmap(QPixmap())

    def _show_image(self, path):
        pix = QPixmap(path)
        if pix.isNull():
            self.preview_label.setText("图片加载失败")
            return
        scaled = pix.scaled(self.preview_scroll.width() - 40, self.preview_scroll.height() - 40,
                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.preview_label.setPixmap(scaled)
        self.preview_label.setText("")
        self.preview_label.setStyleSheet("background:#222;")
        self.preview_text.setText("图片尺寸: %dx%d" % (pix.width(), pix.height()))

    # ==================== 日志 ====================
    def _log(self, msg):
        self.log_text.append(msg)
        self.status_label.setText(msg[:60])


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    # 加载 shadcn 风格 QSS
    qss_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'shadcn.qss')
    if os.path.exists(qss_path):
        with open(qss_path, 'r', encoding='utf-8') as f:
            app.setStyleSheet(f.read())
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
