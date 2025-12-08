# main_window.py

import sys

import os

import json

import ctypes

from datetime import datetime

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 

                            QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 

                            QTableWidgetItem, QTextEdit, QFrame, QGroupBox, QGridLayout,

                            QHeaderView, QScrollArea, QSizePolicy, QSplitter,

                            QMessageBox, QStatusBar, QFileDialog, QDialog, QMenu, QMenuBar)

from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize

from PyQt6.QtGui import (QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor, 

                        QKeyEvent, QDesktopServices, QIntValidator, QAction, QFontDatabase)



# 导入共享模块

from styles import StyleHelper, get_global_font_manager, ChineseMessageBox, ModernGroupBox, ModernLineEdit, ModernComboBox, ModernDoubleSpinBox, StyledMainWindow, StyledDialog

from styles import WindowIconMixin, DialogFactory

from utils import VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP, convert_event_type_num_to_str_with_button, generate_key_event_name, load_icon_universal, load_logo

# 导入关于窗口模块

from about_window import AboutWindowQt

# 导入事件对话框模块

from event_dialogs import EventEditDialog, PasteOptionsDialog, SimpleCoordinateCapture, DeleteOptionsDialog

# 导入调试工具模块

from debug_tools import PasswordDialog, DebugWindow, get_global_debug_logger

# 导入新拆分的模块

from panels import SettingsPanel, OperationsPanel, StatsPanel

# 导入事件时间分析模块

from time_analysis import EventTimeAnalyzerDialog

# 导入版本管理器

from utils import get_current_version, get_current_app_info



# =============================================================================

# 常量定义

# =============================================================================



# 排序提示文本 - 修复语法错误

SORT_TIP_TEXT = "💡 提示：为避免计算出现异常，若添加事件、编辑事件、粘贴事件后相对时间出现负数，请点击'事件排序'"



# =============================================================================

# 自定义输入对话框

# =============================================================================







class BatchEditDialog(StyledDialog):

    """批量编辑对话框"""

    

    def __init__(self, parent=None, selected_rows=None, events_table=None):

        super().__init__(parent)

        self.selected_rows = selected_rows or []
        self.events_table = events_table

        self.setup_ui()

    

    def setup_ui(self):

        """设置UI界面"""

        self.setWindowTitle("批量编辑事件")

        self.setFixedSize(450, 350)  # 调整窗口大小，使其与其他窗口保持一致

        

        layout = QVBoxLayout(self)

        layout.setSpacing(15)

        layout.setContentsMargins(20, 15, 20, 15)

        

        # 标题区域

        title_label = QLabel("批量编辑事件")

        StyleHelper.set_smiley_font(title_label, 16, QFont.Weight.Bold)

        title_label.setStyleSheet(f"color: {StyleHelper.COLORS['primary']}; margin-bottom: 10px;")

        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)

        

        # 操作选项组

        operation_group = ModernGroupBox("操作选项")

        operation_layout = QGridLayout(operation_group)  # 使用GridLayout确保精确对齐

        operation_layout.setSpacing(10)

        operation_layout.setContentsMargins(15, 15, 15, 15)

        

        # 1. 增减偏移时间

        offset_label = QLabel("增减偏移时间:")

        offset_label.setFixedWidth(120)

        self.offset_input = ModernDoubleSpinBox()

        self.offset_input.setMinimum(-999999)

        self.offset_input.setMaximum(999999)

        self.offset_input.setValue(0)

        self.offset_input.setDecimals(0)

        self.offset_input.setSingleStep(100)  # 设置上下按钮变化幅度为100

        self.offset_input.setFixedWidth(100)

        offset_label_unit = QLabel("ms")

        offset_label_unit.setFixedWidth(20)

        offset_label_unit.setAlignment(Qt.AlignmentFlag.AlignLeft)

        

        operation_layout.addWidget(offset_label, 0, 0)

        operation_layout.addWidget(self.offset_input, 0, 1)

        operation_layout.addWidget(offset_label_unit, 0, 2)

        operation_layout.setColumnStretch(3, 1)

        

        # 2. 统一相对时间

        rel_time_label = QLabel("统一相对时间:")

        rel_time_label.setFixedWidth(120)

        self.rel_time_input = ModernDoubleSpinBox()

        self.rel_time_input.setMinimum(0)

        self.rel_time_input.setMaximum(999999)

        self.rel_time_input.setValue(0)

        self.rel_time_input.setDecimals(0)

        self.rel_time_input.setSingleStep(100)  # 设置上下按钮变化幅度为100

        self.rel_time_input.setFixedWidth(100)

        rel_time_label_unit = QLabel("ms")

        rel_time_label_unit.setFixedWidth(20)

        rel_time_label_unit.setAlignment(Qt.AlignmentFlag.AlignLeft)

        

        operation_layout.addWidget(rel_time_label, 1, 0)

        operation_layout.addWidget(self.rel_time_input, 1, 1)

        operation_layout.addWidget(rel_time_label_unit, 1, 2)

        

        # 3. 事件类型替换

        type_label = QLabel("事件类型替换:")

        type_label.setFixedWidth(120)

        # 提取所有按键事件（使用字典保存，事件名称为键，(event_type, keycode)为值）
        self.key_events = {}
        if self.events_table:
            for row in range(self.events_table.rowCount()):
                event_name_item = self.events_table.item(row, 1)
                event_type_item = self.events_table.item(row, 2)
                keycode_item = self.events_table.item(row, 3)
                if event_name_item and event_type_item and keycode_item:
                    event_name = event_name_item.text()
                    event_type = event_type_item.text()
                    keycode = keycode_item.text()
                    if event_type in ["按键按下", "按键释放"] and keycode:
                        # 只保存每个事件名称对应的事件类型和键码
                        self.key_events[event_name] = (event_type, keycode)
        
        # 基本事件类型（移除了"按键按下"和"按键释放"）
        base_event_types = ["鼠标移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
        
        self.old_type_combo = ModernComboBox()
        self.old_type_combo.addItem("不替换类型")
        self.old_type_combo.addItems(base_event_types)
        # 添加具体按键事件到old_type_combo，只显示事件名称
        for event_name in sorted(self.key_events.keys()):
            self.old_type_combo.addItem(event_name)
        self.old_type_combo.setFixedWidth(100)  # 恢复原始宽度

        type_arrow_label = QLabel("→")
        type_arrow_label.setFixedWidth(20)
        type_arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.new_type_combo = ModernComboBox()
        self.new_type_combo.addItems(base_event_types)
        # 添加具体按键事件到new_type_combo，只显示事件名称
        for event_name in sorted(self.key_events.keys()):
            self.new_type_combo.addItem(event_name)
        self.new_type_combo.setFixedWidth(100)  # 恢复原始宽度

        

        operation_layout.addWidget(type_label, 2, 0)

        operation_layout.addWidget(self.old_type_combo, 2, 1)  # 与时间输入框同一列

        operation_layout.addWidget(type_arrow_label, 2, 2)

        operation_layout.addWidget(self.new_type_combo, 2, 3)

        

        layout.addWidget(operation_group)

        # 添加提示信息
        hint_label = QLabel("💡 提示：按键事件替换支持将事件列表中已有的按键事件替换为另一个已有的按键事件")
        hint_label.setStyleSheet(f"color: {StyleHelper.COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(hint_label)

        

        # 按钮区域

        button_layout = DialogFactory.create_ok_cancel_buttons(

            parent=self,

            on_ok=self.accept,

            on_cancel=self.reject,

            ok_text="应用",

            cancel_text="取消"

        )

        layout.addLayout(button_layout)

    

    def get_offset_adjustment(self):

        """获取偏移调整值"""

        return int(self.offset_input.value())

    

    def get_unified_rel_time(self):

        """获取统一相对时间值"""

        return int(self.rel_time_input.value())

    

    def get_type_replacement(self):

        """获取类型替换信息"""

        old_type_text = self.old_type_combo.currentText()

        new_type_text = self.new_type_combo.currentText()

        if old_type_text == "不替换类型":

            return None, None
        
        # 解析旧类型
        old_type = old_type_text
        old_keycode = None
        
        # 检查是否是按键事件名称
        if old_type in self.key_events:
            # 从key_events字典中获取事件类型和键码
            old_type, old_keycode = self.key_events[old_type]
        
        # 解析新类型
        new_type = new_type_text
        new_keycode = None
        
        # 检查是否是按键事件名称
        if new_type in self.key_events:
            # 从key_events字典中获取事件类型和键码
            new_type, new_keycode = self.key_events[new_type]
        
        return (old_type, old_keycode), (new_type, new_keycode)





class CustomInputDialog(StyledDialog):

    """自定义输入对话框，与程序风格保持一致"""

    

    def __init__(self, parent=None):

        super().__init__(parent)

        # 字体管理器已通过StyledDialog自动获取

        self.setup_ui()

        

    def setup_ui(self):

        """设置UI界面"""

        self.setWindowTitle("调试工具入口")

        self.setFixedSize(480, 320)  # 增加高度，确保内容完全显示

        

        # 设置窗口标志，删除最小化和最大化按钮

        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 

                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

        

        # 设置窗口图标

        self.setWindowIcon(load_icon_universal())

        

        layout = QVBoxLayout(self)

        layout.setSpacing(15)  # 减少间距

        layout.setContentsMargins(25, 20, 25, 20)  # 调整边距

        

        # 标题区域

        title_layout = QVBoxLayout()

        

        # 主标题 - 使用得意黑字体

        title_label = QLabel("🔐 调试工具入口")

        StyleHelper.set_smiley_font(title_label, 16, QFont.Weight.Bold)

        title_label.setStyleSheet(f"color: {StyleHelper.COLORS['primary']}; margin-bottom: 3px;")

        title_layout.addWidget(title_label)

        

        # 副标题 - 使用SourceHanSerifCN字体

        subtitle_label = QLabel("请输入访问密码或特殊文字")

        StyleHelper.set_source_han_font(subtitle_label, 11)

        subtitle_label.setStyleSheet(f"color: {StyleHelper.COLORS['text']}; margin-bottom: 8px;")

        title_layout.addWidget(subtitle_label)

        

        # 提示信息

        hint_label = QLabel("💡 提示：尝试输入一些有意义的句子...")

        hint_label.setStyleSheet(f"color: {StyleHelper.COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-bottom: 12px;")

        title_layout.addWidget(hint_label)

        

        layout.addLayout(title_layout)

        

        # 输入区域

        input_layout = QVBoxLayout()

        

        # 输入框标签

        input_label = QLabel("输入内容：")

        StyleHelper.set_source_han_font(input_label, 10)

        input_label.setStyleSheet(f"color: {StyleHelper.COLORS['text']}; margin-bottom: 3px;")

        input_layout.addWidget(input_label)

        

        # 输入框

        self.input_edit = ModernLineEdit()

        self.input_edit.setFixedHeight(32)  # 减少高度

        self.input_edit.setPlaceholderText("请输入密码或特殊文字...")

        input_layout.addWidget(self.input_edit)

        

        layout.addLayout(input_layout)

        

        # 添加弹性空间，确保按钮在底部

        layout.addStretch()

        

        # 按钮区域

        # 使用DialogFactory创建确定和取消按钮布局

        button_layout = DialogFactory.create_ok_cancel_buttons(

            parent=self,

            on_ok=self.on_ok_clicked,

            on_cancel=self.reject,

            ok_text="确定",

            cancel_text="取消"

        )

        

        layout.addLayout(button_layout)

        

        # 获取按钮引用并设置固定尺寸

        self.ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch

        self.cancel_btn = button_layout.itemAt(2).widget()

        

        self.cancel_btn.setMinimumHeight(30)

        self.cancel_btn.setFixedWidth(70)

        self.ok_btn.setMinimumHeight(30)

        self.ok_btn.setFixedWidth(80)

        

        # 设置焦点到输入框

        self.input_edit.setFocus()

        

        # 连接回车键

        self.input_edit.returnPressed.connect(self.on_ok_clicked)

    



    

    def get_text(self):

        """获取输入的文本"""

        return self.input_edit.text().strip()

    

    def set_text(self, text):

        """设置输入框的文本"""

        self.input_edit.setText(text)

    

    def on_ok_clicked(self):

        """确定按钮点击事件 - 增加确认逻辑"""

        text = self.get_text()

        

        # 检查彩蛋文字

        easter_eggs = {

            "当你的天空突然下起了大雨": "https://www.bilibili.com/video/BV18X4y1N7Yh?vd_source=8eb122854e92913741ace2b5024fe442"

        }

        

        if text in easter_eggs:

            # 彩蛋触发，显示确认对话框

            confirm_dialog = QDialog(self)

            confirm_dialog.setWindowTitle("彩蛋确认")

            confirm_dialog.setFixedSize(400, 200)

            confirm_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 

                                        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

            

            confirm_layout = QVBoxLayout(confirm_dialog)

            confirm_layout.setSpacing(15)

            confirm_layout.setContentsMargins(20, 20, 20, 20)

            

            # 彩蛋图标和标题

            header_layout = QHBoxLayout()

            icon_label = QLabel("🎬")

            StyleHelper.set_smiley_font(icon_label, 24)  # 使用StyleHelper统一设置字体

            header_layout.addWidget(icon_label)

            

            title_label = QLabel("发现彩蛋！")

            StyleHelper.set_smiley_font(title_label, 14, QFont.Weight.Bold)  # 使用StyleHelper统一设置字体

            title_label.setStyleSheet(f"color: {StyleHelper.COLORS['primary']};")

            header_layout.addWidget(title_label)

            header_layout.addStretch()

            

            confirm_layout.addLayout(header_layout)

            

            # 彩蛋信息

            info_label = QLabel(f"恭喜你发现了隐藏彩蛋！\n\n输入的文字：{text}\n\n是否打开相关视频？")

            info_label.setFont(self.font_manager.get_source_han_font(10))

            info_label.setStyleSheet(f"color: {StyleHelper.COLORS['text']};")

            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

            confirm_layout.addWidget(info_label)

            

            # 使用DialogFactory创建确定和取消按钮布局

            button_layout = DialogFactory.create_ok_cancel_buttons(

                parent=confirm_dialog,

                on_ok=confirm_dialog.accept,

                on_cancel=confirm_dialog.reject,

                ok_text="打开视频",

                cancel_text="取消"

            )

            

            confirm_layout.addLayout(button_layout)

            

            # 获取按钮引用并设置固定尺寸

            yes_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch

            no_btn = button_layout.itemAt(2).widget()

            

            no_btn.setFixedHeight(30)

            no_btn.setFixedWidth(70)

            yes_btn.setFixedHeight(30)

            yes_btn.setFixedWidth(80)

            

            # 显示确认对话框

            if confirm_dialog.exec() == QDialog.DialogCode.Accepted:

                # 用户确认打开视频

                url = easter_eggs[text]

                QDesktopServices.openUrl(QUrl(url))

                

                # 存储结果供主窗口使用

                self.result = "easter_egg"

                self.url = url

                self.accept()

            else:

                # 用户取消，不关闭输入对话框

                return

        

        elif text == "39782877":

            # 密码正确，直接设置结果并接受

            self.result = "password"

            self.accept()

        else:

            # 密码错误，显示错误提示但不关闭对话框

            ChineseMessageBox.show_error(

                self, 

                "访问失败", 

                f"输入的内容不正确。\n\n你输入的是：{text}\n\n请输入正确的密码或尝试彩蛋文字。"

            )

            # 清空输入框并重新获得焦点

            self.input_edit.clear()

            self.input_edit.setFocus()

            return  # 不关闭对话框



# =============================================================================

# 自定义控件

# =============================================================================



class ModernTableWidget(QTableWidget):

    """现代化的表格控件"""

    def __init__(self, rows=0, columns=0, parent=None):

        super().__init__(rows, columns, parent)

        self.setStyleSheet(StyleHelper.get_table_style())

        

        # 设置表格属性

        self.setAlternatingRowColors(True)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        self.horizontalHeader().setStretchLastSection(True)

        

        # 设置行高

        self.verticalHeader().setDefaultSectionSize(32)

        self.verticalHeader().setVisible(False)

        

        # 设置右键菜单策略

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)



class HeaderWidget(QFrame):

    """自定义标题栏"""

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setFixedHeight(80)

        self.setStyleSheet(StyleHelper.get_header_widget_style())

        

        layout = QHBoxLayout(self)

        layout.setContentsMargins(20, 10, 20, 10)

        

        # Logo和标题

        title_layout = QHBoxLayout()

        

        # Logo - 尝试加载图片

        self.logo_label = QLabel()

        self.logo_label.setFixedSize(50, 50)

        self.load_logo()

        title_layout.addWidget(self.logo_label)

        

        # 标题区域 - 修改为垂直布局以显示主标题和副标题

        title_text_layout = QVBoxLayout()

        

        # 获取字体管理器

        font_manager = get_global_font_manager()

        

        # 获取版本信息

        app_info = get_current_app_info()

        version = get_current_version()

        

        # 主标题 - 使用得意黑字体

        main_title = QLabel(app_info["name"])

        StyleHelper.set_smiley_font(main_title, 24, QFont.Weight.Bold)  # 使用StyleHelper统一设置字体

        main_title.setStyleSheet(f"color: {StyleHelper.COLORS['primary']};")

        title_text_layout.addWidget(main_title)

        

        # 副标题 - 英文名 - 使用得意黑字体

        subtitle = QLabel(app_info["name_en"])

        StyleHelper.set_smiley_font(subtitle, 12)  # 使用StyleHelper统一设置字体

        subtitle.setStyleSheet(f"color: {StyleHelper.COLORS['primary']};")

        title_text_layout.addWidget(subtitle)

        

        title_layout.addLayout(title_text_layout)

        title_layout.addStretch()

        

        # 移除版本信息和关于按钮，替换为标语

        slogan_label = QLabel("风带来故事的种子，时间使之发芽")

        slogan_label.setStyleSheet(StyleHelper.get_slogan_label_style())

        title_layout.addWidget(slogan_label)

        

        layout.addLayout(title_layout)

    

    def load_logo(self):

        """加载Logo图片"""

        try:

            # 使用统一的Logo加载函数

            pixmap = load_logo((50, 50))

            if pixmap is not None:

                self.logo_label.setPixmap(pixmap)

            else:

                self.set_fallback_logo()

        except Exception as e:

            print(f"加载Logo失败: {e}")

            self.set_fallback_logo()

    

    def set_fallback_logo(self):

        """设置备用Logo"""

        self.logo_label.setText("🌌")

        self.logo_label.setStyleSheet(StyleHelper.get_logo_label_style())

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)



# =============================================================================

# 主窗口类

# =============================================================================



class MainWindow(StyledMainWindow, WindowIconMixin):

    """主窗口类"""

    

    def __init__(self):

        super().__init__()

        self.script = None  # 存储生成的脚本

        self.copied_events = []  # 存储复制的事件

        self.undo_stack = []  # 撤销栈

        self.redo_stack = []  # 重做栈

        self.max_undo_steps = 50  # 最大撤销步骤数

        self._table_changing = False  # 防止表格变化时的递归调用

        self._batch_operation = False  # 批量操作标志

        

        # 撤销延迟保存相关

        self._undo_save_timer = QTimer()

        self._undo_save_timer.setSingleShot(True)

        self._undo_save_timer.setInterval(500)  # 500ms延迟

        self._undo_save_timer.timeout.connect(self._delayed_save_state)

        self._pending_undo_save = False

        

        # 初始化调试日志记录器

        self.debug_logger = get_global_debug_logger()

        

        try:

            # 获取应用程序信息

            app_info = get_current_app_info()

            version = get_current_version()

            

            # 设置窗口标志为标准主窗口样式，允许移动和调整大小

            self.setWindowFlags(Qt.WindowType.Window)

            

            self.setWindowTitle(f"{app_info['name']} v{version}")

            # 缩小主窗口大小

            self.setMinimumSize(1200, 700)

            self.resize(1300, 800)

            

            # 设置窗口图标 - 在应用程序创建后立即设置

            self.set_window_icon()

            

            # 设置应用程序样式 - 纯白色背景

            self.setup_application_style()

            

            # 创建中央部件

            central_widget = QWidget()

            self.setCentralWidget(central_widget)

            

            # 创建主布局

            main_layout = QVBoxLayout(central_widget)

            main_layout.setSpacing(8)

            main_layout.setContentsMargins(12, 12, 12, 12)

            

            # 创建界面

            self.create_menu_bar()

            self.create_header(main_layout)

            self.create_content_area(main_layout)

            self.create_status_bar()

            

            # 连接信号槽

            self.connect_signals()

            

            # 加载时间逻辑设置

            self.load_time_logic_settings()

            

            # 加载保存的状态

            self.load_saved_state()

            

            # 如果没有加载到保存的状态，添加示例数据用于测试

            if self.events_table.rowCount() == 0:

                self.add_sample_data()

            

            # 窗口显示后设置任务栏图标

            QTimer.singleShot(100, self.fix_taskbar_icon)

            

            # 记录窗口创建成功

            self.debug_logger.log_info("主窗口初始化完成")

            

        except Exception as e:

            error_msg = f"主窗口初始化错误: {e}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            print(error_msg)

            import traceback

            traceback.print_exc()

    

    def create_menu_bar(self):

        """创建菜单栏"""

        menubar = self.menuBar()

        

        # 文件菜单

        file_menu = menubar.addMenu('文件')

        

        # 新建

        new_action = QAction('新建', self)

        new_action.setShortcut('Ctrl+N')

        new_action.triggered.connect(self.on_new_file)

        file_menu.addAction(new_action)

        

        # 打开

        open_action = QAction('打开', self)

        open_action.setShortcut('Ctrl+O')

        open_action.triggered.connect(self.on_open_file)

        file_menu.addAction(open_action)

        

        # 保存

        save_action = QAction('保存', self)

        save_action.setShortcut('Ctrl+S')

        save_action.triggered.connect(self.on_save_file)

        file_menu.addAction(save_action)

        

        file_menu.addSeparator()

        

        # 退出

        exit_action = QAction('退出', self)

        exit_action.setShortcut('Ctrl+Q')

        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        

        # 编辑菜单

        edit_menu = menubar.addMenu('编辑')

        

        # 撤销

        undo_action = QAction('撤销', self)

        undo_action.setShortcut('Ctrl+Z')

        undo_action.triggered.connect(self.on_undo)

        edit_menu.addAction(undo_action)

        

        # 重做

        redo_action = QAction('重做', self)

        redo_action.setShortcut('Ctrl+Y')

        redo_action.triggered.connect(self.on_redo)

        edit_menu.addAction(redo_action)

        

        edit_menu.addSeparator()

        

        # 剪切

        cut_action = QAction('剪切', self)

        cut_action.setShortcut('Ctrl+X')

        cut_action.triggered.connect(self.on_cut_event)

        edit_menu.addAction(cut_action)

        

        # 复制

        copy_action = QAction('复制', self)

        copy_action.setShortcut('Ctrl+C')

        copy_action.triggered.connect(self.on_copy_event)

        edit_menu.addAction(copy_action)

        

        # 粘贴

        paste_action = QAction('粘贴', self)

        paste_action.setShortcut('Ctrl+V')

        paste_action.triggered.connect(self.on_paste_event)

        edit_menu.addAction(paste_action)

        

        edit_menu.addSeparator()

        

        # 删除

        delete_action = QAction('删除', self)

        delete_action.setShortcut('Delete')

        delete_action.triggered.connect(self.on_delete_event)

        edit_menu.addAction(delete_action)

        

        # 全选

        select_all_action = QAction('全选', self)

        select_all_action.setShortcut('Ctrl+A')

        select_all_action.triggered.connect(self.on_select_all_events)

        edit_menu.addAction(select_all_action)

        

        # 新增：时间逻辑菜单

        time_logic_menu = menubar.addMenu('时间逻辑')

        

        # 删除事件逻辑子菜单

        delete_logic_menu = time_logic_menu.addMenu('删除事件逻辑')

        

        # 删除事件逻辑选项

        delete_prompt_action = QAction('每次弹出提示选择', self)

        delete_prompt_action.setCheckable(True)

        delete_prompt_action.triggered.connect(lambda: self.set_delete_logic('prompt'))

        delete_logic_menu.addAction(delete_prompt_action)

        

        delete_current_action = QAction('默认：仅修改当前事件时间', self)

        delete_current_action.setCheckable(True)

        delete_current_action.triggered.connect(lambda: self.set_delete_logic('current'))

        delete_logic_menu.addAction(delete_current_action)

        

        delete_recalculate_action = QAction('默认：重新计算后续事件时间', self)

        delete_recalculate_action.setCheckable(True)

        delete_recalculate_action.triggered.connect(lambda: self.set_delete_logic('recalculate'))

        delete_logic_menu.addAction(delete_recalculate_action)

        

        # 粘贴事件逻辑子菜单

        paste_logic_menu = time_logic_menu.addMenu('粘贴事件逻辑')

        

        # 粘贴事件逻辑选项

        paste_prompt_action = QAction('每次弹出提示选择', self)

        paste_prompt_action.setCheckable(True)

        paste_prompt_action.triggered.connect(lambda: self.set_paste_logic('prompt'))

        paste_logic_menu.addAction(paste_prompt_action)

        

        paste_current_action = QAction('默认：仅修改当前事件时间', self)

        paste_current_action.setCheckable(True)

        paste_current_action.triggered.connect(lambda: self.set_paste_logic('current'))

        paste_logic_menu.addAction(paste_current_action)

        

        paste_recalculate_action = QAction('默认：重新计算后续事件时间', self)

        paste_recalculate_action.setCheckable(True)

        paste_recalculate_action.triggered.connect(lambda: self.set_paste_logic('recalculate'))

        paste_logic_menu.addAction(paste_recalculate_action)

        

        # 保存菜单项引用，用于更新选中状态

        self.delete_logic_actions = {

            'prompt': delete_prompt_action,

            'current': delete_current_action,

            'recalculate': delete_recalculate_action

        }

        

        self.paste_logic_actions = {

            'prompt': paste_prompt_action,

            'current': paste_current_action,

            'recalculate': paste_recalculate_action

        }

        

        # 分析菜单

        # 工具菜单

        tools_menu = menubar.addMenu('工具')

        

        # 事件时间分析工具

        time_analysis_action = QAction('事件时间分析', self)

        time_analysis_action.setShortcut('Ctrl+T')

        time_analysis_action.triggered.connect(self.on_event_time_analysis)

        tools_menu.addAction(time_analysis_action)

        

        # 添加分隔线

        tools_menu.addSeparator()

        

        # 调试工具

        debug_action = QAction('调试工具', self)

        debug_action.setShortcut('Ctrl+D')

        debug_action.triggered.connect(self.on_open_debug_tool)

        tools_menu.addAction(debug_action)

        

        # 帮助菜单 - 增加链接

        help_menu = menubar.addMenu('帮助')

        

        # 个人主页

        homepage_action = QAction('个人主页', self)

        homepage_action.triggered.connect(lambda: self.open_url("https://b23.tv/KO3m8zU"))

        help_menu.addAction(homepage_action)

        

        # 项目地址

        project_action = QAction('项目地址', self)

        project_action.triggered.connect(lambda: self.open_url("https://github.com/qingshangongzai/BetterGI_StellTrack"))

        help_menu.addAction(project_action)

        

        # 使用说明

        manual_action = QAction('使用说明', self)

        manual_action.triggered.connect(self.open_manual)

        help_menu.addAction(manual_action)

        

        help_menu.addSeparator()

        

        # 关于

        about_action = QAction('关于', self)

        about_action.triggered.connect(self.on_about)

        help_menu.addAction(about_action)

        

        # 用户协议

        agreement_action = QAction('用户协议', self)

        agreement_action.triggered.connect(self.on_user_agreement)

        help_menu.addAction(agreement_action)

        

        # 初始化菜单状态

        self.update_time_logic_menu_state()

    

    def set_delete_logic(self, logic):

        """设置删除事件逻辑"""

        self.delete_logic = logic

        self.update_time_logic_menu_state()

        self.save_time_logic_settings()

        self.status_bar.showMessage(f"✅ 删除事件逻辑已设置为: {self.get_delete_logic_display_name(logic)}")

        self.debug_logger.log_info(f"删除事件逻辑设置为: {logic}")



    def set_paste_logic(self, logic):

        """设置粘贴事件逻辑"""

        self.paste_logic = logic

        self.update_time_logic_menu_state()

        self.save_time_logic_settings()

        self.status_bar.showMessage(f"✅ 粘贴事件逻辑已设置为: {self.get_paste_logic_display_name(logic)}")

        self.debug_logger.log_info(f"粘贴事件逻辑设置为: {logic}")



    def update_time_logic_menu_state(self):

        """更新时间逻辑菜单的选中状态"""

        # 更新删除逻辑菜单状态

        if hasattr(self, 'delete_logic_actions'):

            for logic, action in self.delete_logic_actions.items():

                action.setChecked(getattr(self, 'delete_logic', 'prompt') == logic)

        

        # 更新粘贴逻辑菜单状态

        if hasattr(self, 'paste_logic_actions'):

            for logic, action in self.paste_logic_actions.items():

                action.setChecked(getattr(self, 'paste_logic', 'prompt') == logic)



    def get_delete_logic_display_name(self, logic):

        """获取删除逻辑的显示名称"""

        names = {

            'prompt': '每次弹出提示选择',

            'current': '仅修改当前事件时间',

            'recalculate': '重新计算后续事件时间'

        }

        return names.get(logic, '每次弹出提示选择')



    def get_paste_logic_display_name(self, logic):

        """获取粘贴逻辑的显示名称"""

        names = {

            'prompt': '每次弹出提示选择',

            'current': '仅修改当前事件时间',

            'recalculate': '重新计算后续事件时间'

        }

        return names.get(logic, '每次弹出提示选择')



    def get_delete_logic(self):

        """获取当前删除事件逻辑"""

        return getattr(self, 'delete_logic', 'prompt')



    def get_paste_logic(self):

        """获取当前粘贴事件逻辑"""

        return getattr(self, 'paste_logic', 'prompt')



    def save_time_logic_settings(self):

        """保存时间逻辑设置"""

        try:

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 设置文件路径

            settings_file = os.path.join(app_dir, "BetterGI_StellTrack_settings.json")

            

            # 读取现有设置

            settings = {}

            if os.path.exists(settings_file):

                try:

                    with open(settings_file, 'r', encoding='utf-8') as f:

                        settings = json.load(f)

                except:

                    settings = {}

            

            # 更新时间逻辑设置

            settings['delete_logic'] = self.get_delete_logic()

            settings['paste_logic'] = self.get_paste_logic()

            

            # 保存设置

            with open(settings_file, 'w', encoding='utf-8') as f:

                json.dump(settings, f, ensure_ascii=False, indent=2)

            

            self.debug_logger.log_info("时间逻辑设置已保存")

            

        except Exception as e:

            self.debug_logger.log_error(f"保存时间逻辑设置失败: {e}")



    def load_time_logic_settings(self):

        """加载时间逻辑设置"""

        try:

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 设置文件路径

            settings_file = os.path.join(app_dir, "BetterGI_StellTrack_settings.json")

            

            if os.path.exists(settings_file):

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

                

                # 加载时间逻辑设置

                self.delete_logic = settings.get('delete_logic', 'prompt')

                self.paste_logic = settings.get('paste_logic', 'prompt')

                

                self.debug_logger.log_info(f"时间逻辑设置已加载: 删除={self.delete_logic}, 粘贴={self.paste_logic}")

                return True

            else:

                # 设置默认值

                self.delete_logic = 'prompt'

                self.paste_logic = 'prompt'

                self.debug_logger.log_info("使用默认时间逻辑设置")

                return False

                

        except Exception as e:

            self.debug_logger.log_error(f"加载时间逻辑设置失败: {e}")

            # 设置默认值

            self.delete_logic = 'prompt'

            self.paste_logic = 'prompt'

            return False

    

    def open_url(self, url):

        """打开URL链接"""

        try:

            QDesktopServices.openUrl(QUrl(url))

            self.debug_logger.log_info(f"已打开链接: {url}")

        except Exception as e:

            error_msg = f"打开链接失败: {str(e)}"

            self.debug_logger.log_error(error_msg)

            ChineseMessageBox.show_error(self, "错误", f"无法打开链接:\n{url}")



    def open_manual(self):

        """打开使用说明"""

        try:

            # 使用资源管理器查找使用说明文件

            from utils import find_resource_file

            manual_files = ["使用说明.pdf"]

            

            for manual_file in manual_files:

                manual_path = find_resource_file(manual_file)

                if manual_path and os.path.exists(manual_path):

                    QDesktopServices.openUrl(QUrl.fromLocalFile(manual_path))

                    self.debug_logger.log_info(f"已打开使用说明: {manual_path}")

                    return

            

            # 如果没有找到本地文件，提示用户

            ChineseMessageBox.show_info(self, "提示", "未找到本地使用说明文件，请查看项目文档或联系开发者")

            self.debug_logger.log_warning("未找到使用说明文件")

            

        except Exception as e:

            error_msg = f"打开使用说明失败: {str(e)}"

            self.debug_logger.log_error(error_msg)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_event_time_analysis(self):

        """打开事件时间分析对话框"""

        try:

            dialog = EventTimeAnalyzerDialog(self, self.events_table)

            dialog.exec()

            self.debug_logger.log_info("事件时间分析对话框已打开")

        except Exception as e:

            error_msg = f"打开事件时间分析对话框失败: {str(e)}"

            self.debug_logger.log_error(error_msg)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def set_window_icon(self):

        """设置窗口图标"""

        try:

            icon = load_icon_universal()

            self.setWindowIcon(icon)

            self.debug_logger.log_info("窗口图标设置成功")

        except Exception as e:

            error_msg = f"设置窗口图标失败: {e}"

            self.debug_logger.log_error(error_msg)

            print(error_msg)

    

    def fix_taskbar_icon(self):

        """修复任务栏图标 - 在窗口显示后调用"""

        self._fix_icon_safe()

    

    def setup_application_style(self):

        """设置应用程序样式 - 使用全局样式管理器"""

        # 使用styles模块中的StyleHelper来统一管理应用程序样式

        from styles import StyleHelper

        from PyQt6.QtWidgets import QApplication

        app = QApplication.instance()

        if app:

            StyleHelper.setup_global_style(app)

    

    def create_header(self, parent_layout):

        """创建标题栏"""

        self.header_widget = HeaderWidget()

        parent_layout.addWidget(self.header_widget)

    

    def create_content_area(self, parent_layout):

        """创建内容区域"""

        # 创建水平分割器

        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.setChildrenCollapsible(False)

        splitter.setHandleWidth(2)

        splitter.setStyleSheet(StyleHelper.get_splitter_style())

        

        # 左侧设置面板

        left_panel = self.create_left_panel()

        splitter.addWidget(left_panel)

        

        # 右侧区域（包含事件编辑和统计信息）

        right_panel = self.create_right_panel()

        splitter.addWidget(right_panel)

        

        # 设置分割比例

        splitter.setSizes([350, 950])

        

        parent_layout.addWidget(splitter, 1)

    

    def create_left_panel(self):

        """创建左侧设置面板"""

        container = QWidget()

        container.setMaximumWidth(400)

        container.setStyleSheet(StyleHelper.get_container_bg_style())

        layout = QVBoxLayout(container)

        layout.setSpacing(12)

        layout.setContentsMargins(8, 8, 8, 8)

        

        # 创建设置面板实例，传递主窗口引用

        self.settings_panel = SettingsPanel(self)

        layout.addWidget(self.settings_panel)

        

        # 创建操作面板实例，传递主窗口引用

        self.operations_panel = OperationsPanel(self)

        layout.addWidget(self.operations_panel)

        

        layout.addStretch()

        

        return container

    

    def create_right_panel(self):

        """创建右侧面板（包含事件编辑和统计信息）"""

        container = QWidget()

        container.setStyleSheet(StyleHelper.get_container_bg_style())

        # 使用水平布局，左边是事件编辑，右边是统计信息

        layout = QHBoxLayout(container)

        layout.setSpacing(12)

        layout.setContentsMargins(8, 8, 8, 8)

        

        # 事件编辑区域（占据大部分空间）

        event_editor = self.create_event_editor()

        layout.addWidget(event_editor, 4)  # 权重为4

        

        # 统计信息面板（占据较小空间，放在最右边）

        self.stats_panel = StatsPanel(self)

        layout.addWidget(self.stats_panel, 1)  # 权重为1

        

        return container

    

    def create_event_editor(self, parent=None):

        """创建事件编辑器"""

        if parent is None:

            parent = QWidget()

            parent.setStyleSheet(StyleHelper.get_container_bg_style())

        

        layout = QVBoxLayout(parent)

        layout.setSpacing(12)

        layout.setContentsMargins(0, 0, 0, 0)

        

        group = ModernGroupBox("📋 事件编辑")

        group_layout = QVBoxLayout(group)

        group_layout.setSpacing(12)

        group_layout.setContentsMargins(15, 20, 15, 15)

        

        # 搜索和过滤组件

        self.create_search_filter_widgets(group_layout)

        

        # 事件表格

        self.create_event_table(group_layout)

        

        # 事件操作按钮

        self.create_event_buttons(group_layout)

        

        layout.addWidget(group)

        return parent

    

    def create_search_filter_widgets(self, parent_layout):

        """创建搜索和过滤组件"""

        # 创建搜索和过滤区域

        search_container = QWidget()

        search_container.setStyleSheet(StyleHelper.get_search_container_style())

        search_layout = QHBoxLayout(search_container)

        search_layout.setSpacing(8)

        search_layout.setContentsMargins(10, 10, 10, 10)

        

        # 搜索标签

        search_label = QLabel("🔍 搜索:")

        search_label.setStyleSheet(f"color: {StyleHelper.COLORS['text']}; font-size: 12px;")

        search_layout.addWidget(search_label)

        

        # 搜索输入框

        self.search_input = ModernLineEdit()

        self.search_input.setPlaceholderText("按事件名称、类型、键码搜索...")

        self.search_input.setStyleSheet(StyleHelper.get_search_input_style())

        search_layout.addWidget(self.search_input)

        

        # 事件类型过滤

        self.filter_type_combo = ModernComboBox()

        self.filter_type_combo.addItem("全部事件类型")

        self.filter_type_combo.addItems(["按键按下", "按键释放", "鼠标移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"])

        self.filter_type_combo.setStyleSheet(StyleHelper.get_filter_combo_style())

        self.filter_type_combo.setFixedWidth(150)

        search_layout.addWidget(self.filter_type_combo)

        

        # 搜索按钮

        search_btn = QPushButton("搜索")

        search_btn.setFixedHeight(30)

        search_btn.setStyleSheet(StyleHelper.get_button_style(accent=True))

        search_btn.setFixedWidth(70)

        search_layout.addWidget(search_btn)

        

        # 重置按钮

        reset_btn = QPushButton("重置")

        reset_btn.setFixedHeight(30)

        reset_btn.setStyleSheet(StyleHelper.get_button_style())

        reset_btn.setFixedWidth(70)

        search_layout.addWidget(reset_btn)

        

        parent_layout.addWidget(search_container)

        

        # 连接信号

        # 移除实时过滤，只在点击搜索按钮时过滤

        # self.search_input.textChanged.connect(self.on_search_filter_changed)

        # self.filter_type_combo.currentTextChanged.connect(self.on_search_filter_changed)

        search_btn.clicked.connect(self.on_search_filter_changed)

        reset_btn.clicked.connect(self.on_reset_search_filter)

    

    def create_event_table(self, parent_layout):

        """创建事件表格"""

        # 创建表格

        self.events_table = ModernTableWidget(0, 8)  # 8列：行号 + 原有7列

        headers = ["序号", "事件名称", "事件类型", "键码", "X坐标", "Y坐标", "相对偏移时间", "绝对偏移时间"]

        self.events_table.setHorizontalHeaderLabels(headers)

        

        # 优化列宽分配 - 事件名称和事件类型都设为100

        self.events_table.setColumnWidth(0, 50)   # 序号

        self.events_table.setColumnWidth(1, 100)  # 事件名称 - 与事件类型列宽一致

        self.events_table.setColumnWidth(2, 100)  # 事件类型

        self.events_table.setColumnWidth(3, 70)   # 键码

        self.events_table.setColumnWidth(4, 70)   # X坐标

        self.events_table.setColumnWidth(5, 70)   # Y坐标

        self.events_table.setColumnWidth(6, 90)   # 相对偏移

        self.events_table.setColumnWidth(7, 90)   # 绝对偏移 - 与相对偏移一致

        

        # 连接右键菜单信号

        self.events_table.customContextMenuRequested.connect(self.on_show_event_context_menu)

        

        parent_layout.addWidget(self.events_table, 1)

    

    def create_event_buttons(self, parent_layout):

        """创建事件操作按钮"""

        # 整合所有按钮到一行并居中排列

        buttons_layout = QHBoxLayout()

        buttons_layout.setSpacing(6)

        

        # 创建所有按钮

        self.add_event_btn = QPushButton("➕ 添加事件")

        self.edit_event_btn = QPushButton("✏️ 编辑事件")

        self.clear_events_btn = QPushButton("🧹 清空事件")

        self.undo_btn = QPushButton("↩️ 撤销")

        self.redo_btn = QPushButton("↪️ 重做")

        self.sort_events_btn = QPushButton("🔃 事件排序")

        

        # 设置所有按钮的基本样式

        all_buttons = [self.add_event_btn, self.edit_event_btn, self.clear_events_btn, 

                     self.undo_btn, self.redo_btn, self.sort_events_btn]

        

        for btn in all_buttons:

            btn.setFixedHeight(32)

            btn.setFixedWidth(100)  # 设置统一的固定宽度，确保按钮宽度一致

            btn.setStyleSheet(StyleHelper.get_button_style())

        

        # 设置强调色按钮

        self.add_event_btn.setStyleSheet(StyleHelper.get_button_style(accent=True))

        self.sort_events_btn.setStyleSheet(StyleHelper.get_button_style(accent=True))

        

        # 添加拉伸和按钮，实现居中效果

        buttons_layout.addStretch()

        buttons_layout.addWidget(self.add_event_btn)

        buttons_layout.addWidget(self.edit_event_btn)

        buttons_layout.addWidget(self.clear_events_btn)

        buttons_layout.addWidget(self.undo_btn)

        buttons_layout.addWidget(self.redo_btn)

        buttons_layout.addWidget(self.sort_events_btn)

        buttons_layout.addStretch()

        

        parent_layout.addLayout(buttons_layout)

        

        # 排序提示 - 修复语法错误，使用常量

        sort_tip = QLabel(SORT_TIP_TEXT)

        sort_tip.setStyleSheet(f"color: {StyleHelper.COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;")

        sort_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 设置提示文本居中显示

        parent_layout.addWidget(sort_tip)

    

    def create_status_bar(self):

        """创建状态栏 - 修复灰白不一致问题"""

        self.status_bar = QStatusBar()

        self.setStatusBar(self.status_bar)

        

        # 修复状态栏样式 - 纯白色背景

        self.status_bar.setStyleSheet(StyleHelper.get_status_bar_white_style())

        

        self.status_bar.showMessage("✅ 就绪")

        

        # 添加时间显示

        self.time_label = QLabel()

        self.time_label.setStyleSheet(f"color: {StyleHelper.COLORS['text_secondary']}; font-size: 10px; background-color: transparent;")

        self.status_bar.addPermanentWidget(self.time_label)

        

        # 更新时间

        self.update_time()

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_time)

        self.timer.start(1000)

        

        # 更新快捷键提示，包含新的快捷键

        shortcuts_label = QLabel("快捷键: Ctrl+Z撤销 | Ctrl+Y重做 | Ctrl+A全选 | Ctrl+X剪切 | Ctrl+C复制 | Ctrl+V粘贴 | Delete删除 | Ctrl+S保存")

        shortcuts_label.setStyleSheet(f"color: {StyleHelper.COLORS['text_secondary']}; font-size: 9px; margin-right: 10px; background-color: transparent;")

        self.status_bar.addPermanentWidget(shortcuts_label)

    

    def update_time(self):

        """更新时间显示"""

        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")

        self.time_label.setText(f"🕒 {current_time}")

    

    def connect_signals(self):

        """连接信号槽"""

        # 操作按钮信号 - 修改为调用面板的方法

        self.operations_panel.generate_btn.clicked.connect(self.operations_panel.on_generate_script)

        self.operations_panel.save_btn.clicked.connect(self.operations_panel.on_save_script)

        self.operations_panel.preview_btn.clicked.connect(self.operations_panel.on_preview_script)  # 修改这里

        self.operations_panel.import_script_btn.clicked.connect(self.operations_panel.on_import_script)

        

        # 设置面板信号

        self.settings_panel.detect_screen_btn.clicked.connect(self.on_detect_screen_info)

        self.settings_panel.loop_count_input.textChanged.connect(self.on_calculate_total_time)

        self.settings_panel.interval_input.textChanged.connect(self.on_calculate_total_time)

        self.settings_panel.time_unit_combo.currentTextChanged.connect(self.on_calculate_total_time)

        

        # 事件操作按钮信号

        self.add_event_btn.clicked.connect(self.on_add_event)

        self.edit_event_btn.clicked.connect(self.on_edit_event)

        self.clear_events_btn.clicked.connect(self.on_clear_events)

        self.sort_events_btn.clicked.connect(self.on_sort_events)

        self.undo_btn.clicked.connect(self.on_undo)

        self.redo_btn.clicked.connect(self.on_redo)

        

        # 表格变化信号 - 用于撤销重做

        self.events_table.itemChanged.connect(self.on_table_changed)

        self.events_table.itemSelectionChanged.connect(self.update_stats)

    

    def on_show_event_context_menu(self, position):

        """显示事件表格的右键菜单"""

        context_menu = QMenu(self)

        

        # 获取选中的行

        selected_rows = self.events_table.selectionModel().selectedRows()

        

        # 添加"添加事件"菜单项

        add_action = QAction("➕ 添加事件", self)

        add_action.triggered.connect(self.on_add_event)

        context_menu.addAction(add_action)

        

        # 添加"编辑事件"菜单项（如果有选中行）

        if selected_rows:

            edit_action = QAction("✏️ 编辑事件", self)

            edit_action.triggered.connect(self.on_edit_event)

            context_menu.addAction(edit_action)

            context_menu.addSeparator()

        else:

            context_menu.addSeparator()

        

        # 添加复制事件菜单项

        copy_action = QAction("📋 复制事件", self)

        copy_action.setShortcut("Ctrl+C")

        copy_action.triggered.connect(self.on_copy_event)

        context_menu.addAction(copy_action)

        

        # 添加剪切事件菜单项

        cut_action = QAction("✂️ 剪切事件", self)

        cut_action.setShortcut("Ctrl+X")

        cut_action.triggered.connect(self.on_cut_event)

        context_menu.addAction(cut_action)

        

        # 添加粘贴事件菜单项

        paste_action = QAction("📎 粘贴事件", self)

        paste_action.setShortcut("Ctrl+V")

        paste_action.triggered.connect(self.on_paste_event)

        context_menu.addAction(paste_action)

        

        context_menu.addSeparator()

        

        # 添加批量编辑菜单项（如果有选中行）

        if selected_rows:

            batch_edit_action = QAction("🔧 批量编辑", self)

            batch_edit_action.triggered.connect(self.on_batch_edit)

            context_menu.addAction(batch_edit_action)

        

        # 添加删除事件菜单项

        delete_action = QAction("🗑️ 删除事件", self)

        delete_action.setShortcut("Delete")

        delete_action.triggered.connect(self.on_delete_event)

        context_menu.addAction(delete_action)

        

        context_menu.addSeparator()

        

        # 添加全选事件菜单项

        select_all_action = QAction("☑️ 全选事件", self)

        select_all_action.setShortcut("Ctrl+A")

        select_all_action.triggered.connect(self.on_select_all_events)

        context_menu.addAction(select_all_action)

        

        # 显示菜单

        context_menu.exec(self.events_table.viewport().mapToGlobal(position))

    

    def on_search_filter_changed(self):
        """搜索过滤条件改变时调用 - 使用行隐藏/显示优化"""
        search_text = self.search_input.text().lower()
        filter_type = self.filter_type_combo.currentText()
        
        # 批量更新优化：禁用中间重绘
        self.events_table.setUpdatesEnabled(False)
        
        try:
            # 遍历所有行，根据条件隐藏或显示
            for row in range(self.events_table.rowCount()):
                # 获取当前行的事件类型
                type_item = self.events_table.item(row, 2)
                event_type = type_item.text() if type_item else ""
                
                # 获取当前行的事件名称
                name_item = self.events_table.item(row, 1)
                event_name = name_item.text().lower() if name_item else ""
                
                # 获取当前行的键码
                keycode_item = self.events_table.item(row, 3)
                key_code = keycode_item.text().lower() if keycode_item else ""
                
                # 搜索条件匹配
                matches_search = True
                if search_text:
                    if search_text not in event_name and search_text not in event_type.lower() and search_text not in key_code:
                        matches_search = False
                
                # 类型过滤匹配
                matches_type = True
                if filter_type != "全部事件类型":
                    if event_type != filter_type:
                        matches_type = False
                
                # 根据匹配结果隐藏或显示行
                should_show = matches_search and matches_type
                self.events_table.setRowHidden(row, not should_show)
            
            # 更新统计信息
            self.update_stats()
        finally:
            # 确保重新启用重绘
            self.events_table.setUpdatesEnabled(True)



    def on_reset_search_filter(self):
        """重置搜索过滤条件 - 使用行隐藏/显示优化"""
        # 批量更新优化：禁用中间重绘
        self.events_table.setUpdatesEnabled(False)
        
        try:
            # 显示所有行
            for row in range(self.events_table.rowCount()):
                self.events_table.setRowHidden(row, False)
            
            # 清空搜索输入和过滤类型
            self.search_input.clear()
            self.filter_type_combo.setCurrentIndex(0)
            
            # 清除原始数据缓存（如果存在）
            if hasattr(self, 'original_events_data'):
                self.original_events_data = None
            
            # 更新统计信息
            self.update_stats()
        finally:
            # 确保重新启用重绘
            self.events_table.setUpdatesEnabled(True)
        
        # 显示状态消息
        self.status_bar.showMessage("✅ 搜索过滤已重置")
        self.debug_logger.log_info("搜索过滤已重置")



    def on_batch_edit(self):

        """批量编辑事件"""

        # 获取选中的行

        selected_rows = self.events_table.selectionModel().selectedRows()

        if not selected_rows:

            ChineseMessageBox.show_info(self, "提示", "请先选择要编辑的事件")

            return

        

        # 保存选中的行

        self.selected_rows = selected_rows

        

        # 打开批量编辑对话框
        dialog = BatchEditDialog(self, selected_rows, self.events_table)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用批量编辑
            self.apply_batch_edit(dialog)

            

            # 更新统计信息

            self.update_stats()

            

            # 记录操作

            self.debug_logger.log_info(f"已批量编辑 {len(selected_rows)} 个事件")

    

    def apply_batch_edit(self, dialog):

        """应用批量编辑"""

        # 获取编辑参数

        offset = dialog.get_offset_adjustment()

        unified_rel_time = dialog.get_unified_rel_time()

        old_type_info, new_type_info = dialog.get_type_replacement()

        

        # 获取选中的行索引

        selected_row_indices = [row.row() for row in self.selected_rows]

        selected_row_indices.sort()  # 从小到大排序，确保后续事件时间计算正确

        

        # 保存当前状态到撤销栈

        self.save_state_to_undo_stack()

        

        # 开始批量操作

        self._batch_operation = True

        

        try:

            # 处理每个选中的事件

            for row_idx in selected_row_indices:

                # 1. 处理增减偏移时间

                if offset != 0:

                    # 调整绝对偏移时间

                    abs_time_item = self.events_table.item(row_idx, 7)

                    if abs_time_item:

                        abs_time = int(abs_time_item.text()) if abs_time_item.text().isdigit() else 0

                        new_abs_time = abs_time + offset

                        abs_time_item.setText(str(new_abs_time))

                

                # 2. 处理事件类型替换

                if old_type_info and new_type_info:

                    old_type, old_keycode = old_type_info
                    new_type, new_keycode = new_type_info
                    
                    type_item = self.events_table.item(row_idx, 2)
                    current_event_type = type_item.text() if type_item else ""
                    
                    # 如果旧类型是基本类型，匹配当前事件类型
                    # 如果旧类型是具体按键事件，匹配当前事件类型和键码
                    match = False
                    if old_keycode:
                        # 具体按键事件匹配
                        keycode_item = self.events_table.item(row_idx, 3)
                        current_keycode = keycode_item.text() if keycode_item else ""
                        match = (current_event_type == old_type) and (current_keycode == old_keycode)
                    else:
                        # 基本类型匹配
                        match = (current_event_type == old_type)
                    
                    if match:
                        # 更新事件类型
                        type_item.setText(new_type)
                        
                        # 检查是否需要清除键码（按键事件替换为鼠标事件时）
                        keycode_item = self.events_table.item(row_idx, 3)
                        if keycode_item:
                            # 鼠标事件类型列表
                            mouse_event_types = ["鼠标移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
                            # 按键事件类型列表
                            key_event_types = ["按键按下", "按键释放"]
                            
                            # 如果从按键事件替换为鼠标事件，清除键码
                            if old_type in key_event_types and new_type in mouse_event_types:
                                keycode_item.setText("")
                            # 如果新类型是具体按键事件，更新键码
                            elif new_keycode:
                                keycode_item.setText(new_keycode)
                        
                        # 更新事件名称以反映新的事件类型和键码
                        name_item = self.events_table.item(row_idx, 1)
                        if name_item:
                            # 获取当前键码（可能已更新或清除）
                            keycode_item = self.events_table.item(row_idx, 3)
                            current_keycode = keycode_item.text() if keycode_item else ""
                            # 使用generate_key_event_name生成新名称
                            from utils import generate_key_event_name
                            new_name = generate_key_event_name(new_type, current_keycode)
                            name_item.setText(new_name)

            

            # 3. 处理统一相对时间

            if unified_rel_time > 0:

                # 对每个选中的事件设置统一的相对时间

                for row_idx in selected_row_indices:

                    # 设置相对时间

                    rel_time_item = self.events_table.item(row_idx, 6)

                    rel_time_item.setText(str(unified_rel_time))

                    

                    # 根据相对时间重新计算当前事件的绝对时间

                    if row_idx > 0:

                        prev_abs_time_item = self.events_table.item(row_idx - 1, 7)

                        prev_abs_time = int(prev_abs_time_item.text()) if prev_abs_time_item.text().isdigit() else 0

                    else:

                        prev_abs_time = 0

                    

                    new_abs_time = prev_abs_time + unified_rel_time

                    abs_time_item = self.events_table.item(row_idx, 7)

                    abs_time_item.setText(str(new_abs_time))

            

            # 如果涉及时间修改，只重新计算相对时间，保持后续事件绝对时间不变

            if offset != 0 or unified_rel_time > 0:

                # 重新计算所有相对时间，保持绝对时间不变

                self.recalculate_relative_times()

            

            # 清除撤销栈

            self.redo_stack.clear()

            

            # 更新统计信息

            self.update_stats()

            

            # 更新状态栏消息

            self.status_bar.showMessage(f"✅ 已批量编辑 {len(self.selected_rows)} 个事件")

            

            # 立即更新预计总时间

            self.on_calculate_total_time()

        finally:

            # 结束批量操作

            self._batch_operation = False

    

    def add_sample_data(self):

        """添加示例数据用于测试"""

        sample_data = [

            [1, "按下回车", "按键按下", "13", "0", "0", "0", "0"],

            [2, "释放回车", "按键释放", "13", "0", "0", "100", "100"],

            [3, "鼠标移动", "鼠标移动", "", "500", "500", "300", "400"],

            [4, "左键按下", "左键按下", "", "500", "500", "500", "900"],

            [5, "左键释放", "左键释放", "", "500", "500", "600", "1500"]

        ]

        

        for row_data in sample_data:

            self.add_table_row(row_data)

        

        self.update_stats()

        self.debug_logger.log_info("示例数据已添加")

    

    def add_table_row(self, row_data):

        """添加表格行"""

        row_position = self.events_table.rowCount()

        self.events_table.insertRow(row_position)

        

        for col, data in enumerate(row_data):

            item = QTableWidgetItem(str(data))

            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.events_table.setItem(row_position, col, item)

    

    def add_table_rows(self, rows_data):

        """批量添加表格行 - 高性能版本"""

        if not rows_data:

            return

        

        # 获取当前行数量

        current_row_count = self.events_table.rowCount()

        # 计算新的行数量

        new_row_count = current_row_count + len(rows_data)

        

        # 一次性设置行数量，避免多次调整数据结构

        self.events_table.setRowCount(new_row_count)

        

        # 填充数据

        for i, row_data in enumerate(rows_data):

            row_position = current_row_count + i

            for col, data in enumerate(row_data):

                item = QTableWidgetItem(str(data))

                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.events_table.setItem(row_position, col, item)

    

    def update_stats(self):

        """更新统计信息 - 调用面板的方法"""

        if hasattr(self, 'stats_panel'):

            self.stats_panel.update_stats()

    

    def sort_events_by_absolute_time(self):

        """按绝对时间对事件进行排序"""

        # 获取所有事件数据

        events = []

        for row in range(self.events_table.rowCount()):

            event_data = []

            for col in range(self.events_table.columnCount()):

                item = self.events_table.item(row, col)

                event_data.append(item.text() if item else "")

            events.append(event_data)

        

        # 按绝对时间排序

        events.sort(key=lambda x: int(x[7]) if x[7].isdigit() else 0)

        

        # 清空表格

        self.events_table.setRowCount(0)

        

        # 重新添加排序后的事件

        for event_data in events:

            self.add_table_row(event_data)

    

    def recalculate_all_times(self):

        """重新计算所有事件的相对时间和绝对时间"""

        if self.events_table.rowCount() == 0:

            return

        

        # 第一个事件的绝对时间为0

        first_abs_time_item = self.events_table.item(0, 7)

        first_abs_time_item.setText("0")

        

        # 从第二个事件开始，根据相对时间重新计算绝对时间

        prev_abs_time = 0

        for i in range(0, self.events_table.rowCount()):

            # 获取相对时间

            rel_time_item = self.events_table.item(i, 6)

            rel_time = int(rel_time_item.text()) if rel_time_item.text().isdigit() else 0

            

            # 计算当前事件的绝对时间

            curr_abs_time = prev_abs_time + rel_time

            

            # 更新绝对时间

            abs_time_item = self.events_table.item(i, 7)

            abs_time_item.setText(str(curr_abs_time))

            

            # 更新前一个绝对时间

            prev_abs_time = curr_abs_time

    

    def recalculate_relative_times(self):

        """重新计算所有事件的相对时间，保持绝对时间不变"""

        if self.events_table.rowCount() == 0:

            return

        

        # 从第二个事件开始，根据绝对时间计算相对时间

        for i in range(1, self.events_table.rowCount()):

            # 获取前一个事件的绝对时间

            prev_abs_time_item = self.events_table.item(i-1, 7)

            prev_abs_time = int(prev_abs_time_item.text()) if prev_abs_time_item.text().isdigit() else 0

            

            # 获取当前事件的绝对时间

            curr_abs_time_item = self.events_table.item(i, 7)

            curr_abs_time = int(curr_abs_time_item.text()) if curr_abs_time_item.text().isdigit() else 0

            

            # 计算相对时间

            rel_time = curr_abs_time - prev_abs_time

            

            # 更新相对时间

            rel_time_item = self.events_table.item(i, 6)

            rel_time_item.setText(str(rel_time))

    

    def get_screen_resolution(self):

        """获取屏幕分辨率（参考原代码实现）"""

        try:

            # 方法1: 使用GetSystemMetrics获取主显示器分辨率

            user32 = ctypes.windll.user32

            width = user32.GetSystemMetrics(0)  # SM_CXSCREEN

            height = user32.GetSystemMetrics(1)  # SM_CYSCREEN

            

            # 方法2: 使用GetDeviceCaps获取更准确的分辨率（考虑DPI缩放）

            try:

                hdc = user32.GetDC(0)

                if hdc:

                    # 获取实际像素分辨率

                    actual_width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)  # HORZRES

                    actual_height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)  # VERTRES

                    

                    # 如果获取到了实际分辨率，使用它

                    if actual_width > 0 and actual_height > 0:

                        width, height = actual_width, actual_height

                    

                    user32.ReleaseDC(0, hdc)

            except Exception:

                pass  # 如果方法2失败，继续使用方法1的结果

            

            self.debug_logger.log_info(f"获取屏幕分辨率: {width}×{height}")

            return width, height

            

        except Exception as e:

            error_msg = f"Windows API获取分辨率失败: {e}"

            self.debug_logger.log_error(error_msg)

            # 如果Windows API方法失败，回退到Qt方法

            try:

                screen = QApplication.primaryScreen()

                rect = screen.availableGeometry()

                width, height = rect.width(), rect.height()

                self.debug_logger.log_info(f"Qt获取屏幕分辨率: {width}×{height}")

                return width, height

            except Exception as qt_e:

                self.debug_logger.log_error(f"Qt获取分辨率失败: {qt_e}")

                return 1920, 1080  # 默认分辨率

    

    def get_system_scale(self):

        """获取系统缩放比例"""

        try:

            # 使用Windows API获取系统缩放比例

            user32 = ctypes.windll.user32

            

            # 获取主显示器的DPI

            try:

                hdc = user32.GetDC(0)

                if hdc:

                    # 获取逻辑DPI和物理DPI

                    logical_dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)   # LOGPIXELSX

                    logical_dpi_y = ctypes.windll.gdi32.GetDeviceCaps(hdc, 90)   # LOGPIXELSY

                    

                    user32.ReleaseDC(0, hdc)

                    

                    # 计算缩放比例（基于96 DPI为100%）

                    if logical_dpi_x > 0:

                        scale_percent = int((logical_dpi_x / 96.0) * 100)

                        # 四舍五入到最接近的标准值

                        standard_scales = [100, 125, 150, 175, 200, 225, 250]

                        closest_scale = min(standard_scales, key=lambda x: abs(x - scale_percent))

                        self.debug_logger.log_info(f"获取系统缩放比例: {closest_scale}%")

                        return f"{closest_scale}%"

            except Exception:

                pass

            

            # 备用方法：使用GetDpiForSystem (Windows 10+)

            try:

                if hasattr(user32, 'GetDpiForSystem'):

                    dpi = user32.GetDpiForSystem()

                    scale_percent = int((dpi / 96.0) * 100)

                    standard_scales = [100, 125, 150, 175, 200, 225, 250]

                    closest_scale = min(standard_scales, key=lambda x: abs(x - scale_percent))

                    self.debug_logger.log_info(f"获取系统缩放比例(备用): {closest_scale}%")

                    return f"{closest_scale}%"

            except Exception:

                pass

            

            self.debug_logger.log_warning("使用默认缩放比例: 100%")

            return "100%"  # 默认值

            

        except Exception as e:

            error_msg = f"获取系统缩放比例失败: {e}"

            self.debug_logger.log_error(error_msg)

            return "100%"  # 默认值

    

    def convert_event_type_str_to_num(self, type_str):

        """将字符串事件类型转换为数字"""

        return EVENT_TYPE_MAP.get(type_str, 0)

    

    def on_generate_script(self):

        """生成脚本"""

        try:

            self.debug_logger.log_info("开始生成脚本...")

            

            # 检查事件成对性 - 只保留一次检测

            if not self.check_event_pairing():

                # 如果成对性检查失败，直接返回，不再显示额外的警告

                self.debug_logger.log_warning("事件成对性检查失败，脚本生成取消")

                return

            

            # 收集事件数据

            events = []

            for row in range(self.events_table.rowCount()):

                event_data = []

                for col in range(1, 8):  # 跳过行号列

                    item = self.events_table.item(row, col)

                    if item:

                        event_data.append(item.text())

                    else:

                        event_data.append("")

                

                if event_data[0]:  # 如果事件名称不为空

                    # 转换为脚本格式

                    event_type_num = self.convert_event_type_str_to_num(event_data[1])

                    script_event = {

                        "type": event_type_num,

                        "mouseX": int(event_data[3]) if event_data[3] else 0,

                        "mouseY": int(event_data[4]) if event_data[4] else 0,

                        "time": int(event_data[6]) if event_data[6] else 0  # 使用绝对偏移时间

                    }

                    

                    # 如果是键盘事件，添加keyCode

                    if event_data[1] in ["按键按下", "按键释放"] and event_data[2]:

                        script_event["keyCode"] = int(event_data[2])

                    

                    # 如果是鼠标点击事件，添加mouseButton

                    if event_data[1] in ["左键按下", "左键释放"]:

                        script_event["mouseButton"] = "Left"

                    elif event_data[1] in ["右键按下", "右键释放"]:

                        script_event["mouseButton"] = "Right"

                    

                    events.append(script_event)

            

            if not events:

                self.debug_logger.log_warning("没有事件可生成脚本")

                ChineseMessageBox.show_warning(self, "警告", "没有事件可生成脚本")

                return

            

            # 获取循环次数 - 使用安全获取方法

            loop_count = self.settings_panel.get_safe_loop_count()

            

            # 获取间隔时间

            interval = self.settings_panel.interval_input.value()

            

            # 转换时间单位为毫秒

            time_unit = self.settings_panel.time_unit_combo.currentText()

            if time_unit == "s":

                interval_ms = int(interval * 1000)

            elif time_unit == "min":

                interval_ms = int(interval * 60000)

            else:  # ms

                interval_ms = int(interval)

            

            # 生成完整的事件序列（考虑循环）

            full_events = []

            last_event_time = 0

            

            for loop in range(loop_count):

                for i, event in enumerate(events):

                    # 复制事件

                    new_event = event.copy()

                    

                    # 确保时间值为整数

                    event_time = int(event["time"])

                    

                    # 如果是第一个循环，使用原始时间

                    if loop == 0:

                        new_event["time"] = event_time

                    else:

                        # 后续循环：时间 = 原始时间 + (循环索引 * (最后一个事件时间 + 间隔时间))

                        new_event["time"] = event_time + loop * (last_event_time + interval_ms)

                    

                    full_events.append(new_event)

                

                # 更新最后一个事件的时间

                if events:

                    last_event_time = int(events[-1]["time"])

            

            # 获取缩放比例并转换为小数

            scale_str = self.settings_panel.scale_combo.currentText()

            try:

                record_dpi = float(scale_str.strip('%')) / 100.0

            except ValueError:

                record_dpi = 1.0  # 如果转换失败，使用默认值1.0

            

            # 获取应用信息用于脚本描述

            app_info = get_current_app_info()

            version = get_current_version()

            

            # 脚本结构

            self.script = {

                "macroEvents": full_events,

                "info": {

                    "description": "由BetterGI StellTrack创建",

                    "x": 0,

                    "y": 0,

                    "width": int(self.settings_panel.width_input.text()),

                    "height": int(self.settings_panel.height_input.text()),

                    "recordDpi": record_dpi

                }

            }

            

            # 生成默认文件名

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

            default_filename = f"BetterGI_GCM_{timestamp}.json"

            

            # 更新统计信息

            self.update_stats()

            

            self.status_bar.showMessage("✅ 脚本生成成功")

            self.debug_logger.log_info(f"脚本生成成功: {len(full_events)} 个事件, {loop_count} 次循环")

            ChineseMessageBox.show_info(self, "成功", f"脚本已成功生成！\n包含 {len(full_events)} 个事件 ({loop_count} 次循环)\n文件名: {default_filename}")

            

        except Exception as e:

            error_msg = f"生成脚本失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def check_event_pairing(self):

        """检查事件成对性 - 修复版：显示中文名称"""

        pressed_keys = set()  # 记录按下的按键

        pressed_mouse_buttons = set()  # 记录按下的鼠标按钮

        issues = []

        

        for row in range(self.events_table.rowCount()):

            type_item = self.events_table.item(row, 2)  # 事件类型列

            keycode_item = self.events_table.item(row, 3)  # 键码列

            

            if not type_item:

                continue

                

            event_type = type_item.text()

            keycode = keycode_item.text() if keycode_item else ""

            

            # 检查按键事件

            if event_type == "按键按下":

                if keycode in pressed_keys:

                    # 获取按键的中文名称

                    key_name_cn = self.get_key_chinese_name(keycode)

                    issues.append(f"第{row+1}行: 按键{key_name_cn}重复按下")

                else:

                    pressed_keys.add(keycode)

            elif event_type == "按键释放":

                if keycode not in pressed_keys:

                    # 获取按键的中文名称

                    key_name_cn = self.get_key_chinese_name(keycode)

                    issues.append(f"第{row+1}行: 按键{key_name_cn}未按下就释放")

                else:

                    pressed_keys.remove(keycode)

            

            # 检查鼠标事件

            elif event_type == "左键按下":

                if "Left" in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 左键重复按下")

                else:

                    pressed_mouse_buttons.add("Left")

            elif event_type == "左键释放":

                if "Left" not in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 左键未按下就释放")

                else:

                    pressed_mouse_buttons.remove("Left")

                    

            elif event_type == "右键按下":

                if "Right" in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 右键重复按下")

                else:

                    pressed_mouse_buttons.add("Right")

            elif event_type == "右键释放":

                if "Right" not in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 右键未按下就释放")

                else:

                    pressed_mouse_buttons.remove("Right")

                    

            elif event_type == "中键按下":

                if "Middle" in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 中键重复按下")

                else:

                    pressed_mouse_buttons.add("Middle")

            elif event_type == "中键释放":

                if "Middle" not in pressed_mouse_buttons:

                    issues.append(f"第{row+1}行: 中键未按下就释放")

                else:

                    pressed_mouse_buttons.remove("Middle")

        

        # 检查未释放的按键

        for key in pressed_keys:

            key_name_cn = self.get_key_chinese_name(key)

            issues.append(f"按键{key_name_cn}被按下但未释放")

        for button in pressed_mouse_buttons:

            button_name = "左键" if button == "Left" else "右键"

            issues.append(f"鼠标{button_name}按钮被按下但未释放")

        

        if issues:

            # 显示详细的问题信息，并询问是否继续

            message = "检测到以下事件成对性问题：\n\n" + "\n".join(issues) + "\n\n是否继续生成脚本？"

            self.debug_logger.log_warning(f"事件成对性问题: {issues}")

            return ChineseMessageBox.show_question(self, "事件成对性检查", message)

        

        self.debug_logger.log_info("事件成对性检查通过")

        return True



    def get_key_chinese_name(self, keycode):

        """获取按键的中文名称"""

        if not keycode:

            return "未知"

        

        try:

            keycode_int = int(keycode)

            # 使用虚拟键码映射获取按键名称

            key_name = VK_MAPPING.get(keycode_int, f"键码:{keycode}")

            # 转换为中文名称

            key_name_cn = KEY_NAME_MAPPING.get(key_name, key_name)

            return key_name_cn

        except (ValueError, TypeError):

            # 如果键码不是数字，返回原值

            return keycode

    

    def on_save_script(self):

        """保存脚本"""

        try:

            if not self.script:

                self.debug_logger.log_warning("尝试保存但未生成脚本")

                ChineseMessageBox.show_warning(self, "警告", "请先生成脚本")

                return

            

            # 生成默认文件名

            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]

            default_filename = f"BetterGI_GCM_{timestamp}.json"

            

            filename, _ = QFileDialog.getSaveFileName(

                self,

                "保存脚本",

                default_filename,

                "JSON文件 (*.json);;所有文件 (*.*)"

            )

            

            if not filename:

                self.debug_logger.log_info("用户取消保存脚本")

                return

            

            with open(filename, 'w', encoding='utf-8') as f:

                json.dump(self.script, f, ensure_ascii=False, separators=(',', ':'))

            

            self.status_bar.showMessage(f"✅ 脚本已保存到: {filename}")

            self.debug_logger.log_info(f"脚本已保存到: {filename}")

            ChineseMessageBox.show_info(self, "成功", f"脚本已保存到:\n{filename}")

            

        except Exception as e:

            error_msg = f"保存脚本失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_about(self):

        """关于"""

        self.debug_logger.log_info("打开关于窗口")

        # 移除版本参数，使用版本管理器

        about_window = AboutWindowQt(parent=self)

        about_window.show()

    

    def on_user_agreement(self):

        """用户协议"""

        self.debug_logger.log_info("打开用户协议窗口")

        from about_window import UserAgreementWindow

        agreement_window = UserAgreementWindow(self)

        agreement_window.show()

    

    def on_open_debug_tool(self):

        """打开调试工具 - 增强版：支持彩蛋文字，使用自定义对话框"""

        try:

            self.debug_logger.log_info("尝试打开调试工具")

            

            # 使用自定义输入对话框

            dialog = CustomInputDialog(self)

            if dialog.exec() == QDialog.DialogCode.Accepted:

                # 检查结果类型

                if hasattr(dialog, 'result'):

                    if dialog.result == "easter_egg":

                        # 彩蛋触发，更新状态栏和日志，不再显示额外提示

                        self.status_bar.showMessage("🎬 发现彩蛋！正在打开视频...")

                        self.debug_logger.log_info(f"彩蛋触发，打开链接: {dialog.url}")

                        return  # 直接返回，不再显示额外提示窗口

                        

                    elif dialog.result == "password":

                        # 密码验证正确，直接打开调试工具，不再要求二次输入

                        debug_window = DebugWindow(self)

                        debug_window.exec()

                        self.debug_logger.log_info("调试工具已关闭")

                        return

                else:

                    # 兼容旧逻辑

                    text = dialog.get_text()

                    if text == "39782877":

                        # 密码验证正确，直接打开调试工具

                        debug_window = DebugWindow(self)

                        debug_window.exec()

                        self.debug_logger.log_info("调试工具已关闭")

                        return

            else:

                self.debug_logger.log_info("用户取消输入")

                

        except Exception as e:

            error_msg = f"打开调试工具失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_new_file(self):

        """新建文件"""

        try:

            if self.events_table.rowCount() > 0:

                if not ChineseMessageBox.show_question(self, "确认", "确定要新建文件吗？当前未保存的数据将丢失。"):

                    return

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 清空表格

                self.events_table.setRowCount(0)

                self.script = None

                

                # 重置设置

                self.settings_panel.reset_settings()

                

                self.update_stats()

                self.status_bar.showMessage("✅ 已新建文件")

                self.debug_logger.log_info("已新建文件")

                

            finally:

                # 结束批量操作

                self._batch_operation = False

                

        except Exception as e:

            self._batch_operation = False

            error_msg = f"新建文件失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_open_file(self):

        """打开文件 - 调用导入脚本功能"""

        self.on_import_script()

    

    def on_save_file(self):

        """保存文件 - 调用保存脚本功能"""

        self.on_save_script()

    

    def on_add_event(self):

        """添加事件 - 在指定位置插入"""

        try:

            # 获取插入位置 - 关键修复：正确识别插入位置

            selected_rows = self.get_selected_event_rows()

            if selected_rows:

                # 有选中事件：在第一个选中事件后插入

                insert_position = selected_rows[0] + 1

                insert_after_item = selected_rows[0]  # 在这个事件后插入

            else:

                # 没有选中事件：在最后插入

                insert_position = self.events_table.rowCount()

                insert_after_item = None  # 在最后插入

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 创建事件编辑对话框，传入插入位置信息

                dialog = EventEditDialog(

                    self, 

                    is_edit_mode=False, 

                    insert_position=insert_position,

                    insert_after_item=insert_after_item

                )

                

                # 更新插入位置信息

                dialog.update_insert_position_info(insert_position, insert_after_item)

                

                if dialog.exec() == QDialog.DialogCode.Accepted:

                    event_data = dialog.get_event_data()

                    time_option = dialog.get_time_option()

                    

                    # 获取前一个事件的绝对时间

                    if insert_position == 0:

                        prev_absolute_time = 0

                    else:

                        prev_item = self.events_table.item(insert_position - 1, 7)  # 绝对偏移列

                        prev_absolute_time = int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0

                    

                    # 获取下一个事件的绝对时间（如果存在）

                    next_absolute_time = None

                    if insert_position < self.events_table.rowCount():

                        next_item = self.events_table.item(insert_position, 7)  # 绝对偏移列

                        if next_item and next_item.text().isdigit():

                            next_absolute_time = int(next_item.text())

                    

                    # 获取新事件的相对时间（从对话框获取的已经是毫秒）

                    relative_time = int(event_data[5]) if event_data[5] else 100

                    

                    # 计算新事件的绝对时间：前一个事件的绝对时间 + 相对时间

                    new_absolute_time = prev_absolute_time + relative_time

                    

                    # 插入新行

                    self.events_table.insertRow(insert_position)

                    new_row_data = [

                        str(insert_position + 1),  # 行号，后面会重新编号

                        event_data[0],  # 事件名称

                        event_data[1],  # 事件类型

                        event_data[2],  # 键码

                        event_data[3],  # X坐标

                        event_data[4],  # Y坐标

                        str(relative_time),  # 相对偏移（相对时间）保持不变

                        str(new_absolute_time)  # 绝对偏移（绝对时间）重新计算

                    ]

                    

                    for col, data in enumerate(new_row_data):

                        item = QTableWidgetItem(str(data))

                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.events_table.setItem(insert_position, col, item)

                    

                    # 更新行号

                    self.update_row_numbers()

                    

                    # 根据时间修改选项调整后续事件

                    if time_option == "仅修改当前事件时间":

                        if next_absolute_time is not None:

                            # 调整下一个事件的相对时间：下一个事件的绝对时间 - 新事件的绝对时间

                            next_relative_time = next_absolute_time - new_absolute_time

                            next_item = self.events_table.item(insert_position + 1, 6)  # 相对偏移列

                            if next_item:

                                next_item.setText(str(next_relative_time))

                    else:  # 修改后重新计算后续事件时间

                        # 重新计算后续所有事件的绝对时间

                        self.recalculate_time_from_row(insert_position + 1)

                    

                    self.update_stats()

                    self.status_bar.showMessage("✅ 已添加新事件")

                    self.debug_logger.log_info(f"已添加新事件: {event_data[0]}")

                    

                    # 立即更新预计总时间

                    self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

                

        except Exception as e:

            self._batch_operation = False

            error_msg = f"添加事件错误: {e}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", f"添加事件失败: {str(e)}")

    

    def on_edit_event(self):

        """编辑事件 - 修复版：与添加事件保持一致的时间计算逻辑"""

        try:

            selected_rows = self.get_selected_event_rows()

            if not selected_rows:

                self.debug_logger.log_warning("尝试编辑事件但未选择事件")

                ChineseMessageBox.show_warning(self, "警告", "请先选择要编辑的事件")

                return

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 只编辑第一个选中的事件

                row = selected_rows[0]

                

                # 获取当前事件数据

                event_data = []

                for col in range(1, 8):  # 跳过行号列

                    item = self.events_table.item(row, col)

                    if item:

                        event_data.append(item.text())

                    else:

                        event_data.append("")

                

                # 打开编辑对话框

                dialog = EventEditDialog(self, event_data=event_data, is_edit_mode=True)

                if dialog.exec() == QDialog.DialogCode.Accepted:

                    new_event_data = dialog.get_event_data()

                    time_option = dialog.get_time_option()

                    

                    # ===== 关键修复：与添加事件保持一致的时间计算逻辑 =====

                    

                    # 1. 获取前一个事件的绝对时间

                    if row == 0:

                        prev_absolute_time = 0

                    else:

                        prev_item = self.events_table.item(row - 1, 7)  # 绝对偏移列

                        prev_absolute_time = int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0

                    

                    # 2. 获取下一个事件的绝对时间（如果存在）

                    next_absolute_time = None

                    if row + 1 < self.events_table.rowCount():

                        next_item = self.events_table.item(row + 1, 7)  # 绝对偏移列

                        if next_item and next_item.text().isdigit():

                            next_absolute_time = int(next_item.text())

                    

                    # 3. 获取编辑后事件的相对时间

                    relative_time = int(new_event_data[5]) if new_event_data[5] else 100

                    

                    # 4. 计算编辑后事件的绝对时间：前一个事件的绝对时间 + 相对时间

                    current_absolute_time = prev_absolute_time + relative_time

                    

                    # 5. 更新当前事件的数据（跳过绝对时间列）

                    for col in range(1, 7):  # 只更新1-6列

                        item = QTableWidgetItem(new_event_data[col-1])

                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.events_table.setItem(row, col, item)

                    

                    # 6. 更新当前事件的绝对时间

                    absolute_item = QTableWidgetItem(str(current_absolute_time))

                    absolute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                    self.events_table.setItem(row, 7, absolute_item)

                    

                    # 7. 根据时间修改选项调整后续事件（与添加事件逻辑一致）

                    if time_option == "仅修改当前事件时间":

                        if next_absolute_time is not None:

                            # 调整下一个事件的相对时间：下一个事件的绝对时间 - 当前事件的绝对时间

                            next_relative_time = next_absolute_time - current_absolute_time

                            # 修复：正确创建和设置下一个事件的相对时间项

                            next_relative_item = QTableWidgetItem(str(next_relative_time))

                            next_relative_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            self.events_table.setItem(row + 1, 6, next_relative_item)

                    else:  # 修改后重新计算后续事件时间

                        # 重新计算后续所有事件的绝对时间

                        self.recalculate_time_from_row(row + 1)

                    

                    self.update_stats()

                    self.status_bar.showMessage(f"✅ 已编辑事件: 第{row + 1}行")

                    self.debug_logger.log_info(f"已编辑事件: 第{row + 1}行 - {new_event_data[0]}")

                    

                    # 立即更新预计总时间

                    self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

                

        except Exception as e:

            self._batch_operation = False

            error_msg = f"编辑事件错误: {e}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", f"编辑事件失败: {str(e)}")

    

    def on_delete_event(self):

        """删除事件 - 增强版：根据菜单设置决定行为"""

        selected_rows = self.get_selected_event_rows()

        if not selected_rows:

            self.debug_logger.log_warning("尝试删除事件但未选择事件")

            ChineseMessageBox.show_warning(self, "警告", "请先选择要删除的事件")

            return

        

        # 获取删除逻辑设置

        delete_logic = self.get_delete_logic()

        time_option = None

        

        # 根据设置决定是否弹出提示

        if delete_logic == 'prompt':

            # 显示删除选项对话框

            delete_dialog = DeleteOptionsDialog(self)

            if delete_dialog.exec() != QDialog.DialogCode.Accepted:

                self.debug_logger.log_info("用户取消删除事件")

                return

            time_option = delete_dialog.get_time_option()

        else:

            # 使用默认设置

            time_option = "仅修改当前事件时间" if delete_logic == 'current' else "修改后重新计算后续事件时间"

            self.debug_logger.log_info(f"使用默认删除逻辑: {time_option}")

        

        # 保存当前状态到撤销栈

        self.save_state_to_undo_stack()

        

        # 开始批量操作

        self._batch_operation = True

        

        try:

            # 获取删除前的表行数和最后一行索引
            rows_before_delete = self.events_table.rowCount()
            last_row_before_delete = rows_before_delete - 1
            
            # 找出第一个和最后一个被删除事件的索引
            first_deleted_index = min(selected_rows)
            last_deleted_index = max(selected_rows)

            # 检测是否删除的是末尾事件
            is_deleting_end_events = last_deleted_index == last_row_before_delete

            # 执行删除
            for row in sorted(selected_rows, reverse=True):
                self.events_table.removeRow(row)

            # 只有当不是删除末尾事件时，才需要处理时间计算
            if not is_deleting_end_events:
                # 获取删除前的事件数据，用于计算（只收集必要的列）
                all_events_before_delete = []
                for row in range(rows_before_delete):
                    event_data = []
                    for col in [0, 7]:  # 只收集行号和绝对时间列
                        item = self.events_table.item(row, col)
                        event_data.append(item.text() if item else "")
                    all_events_before_delete.append(event_data)
                
                # 获取被删除事件之前的最后一个事件的绝对时间
                prev_absolute_time = 0
                if first_deleted_index > 0:
                    prev_event = all_events_before_delete[first_deleted_index - 1]
                    prev_absolute_time = int(prev_event[1]) if prev_event[1].isdigit() else 0
                
                if time_option == "仅修改当前事件时间":
                    # 仅重新计算删除位置后一个事件的相对时间
                    next_row_index = first_deleted_index
                    if next_row_index < self.events_table.rowCount():
                        # 获取删除位置后一个事件的原始绝对时间
                        next_absolute_time = None
                        for event in all_events_before_delete:
                            if event[0].isdigit() and int(event[0]) > first_deleted_index + 1:  # 找到删除后的第一个事件
                                next_absolute_time = int(event[1]) if event[1].isdigit() else 0
                                break
                    
                    if next_absolute_time is not None:
                        # 计算新的相对时间
                        new_relative_time = next_absolute_time - prev_absolute_time
                        next_relative_item = QTableWidgetItem(str(new_relative_time))
                        next_relative_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.events_table.setItem(next_row_index, 6, next_relative_item)
                else:
                    # 重新计算后续所有事件的绝对时间
                    self._recalculate_times_from_index(first_deleted_index, prev_absolute_time)

            

            self.update_row_numbers()

            self.update_stats()

            self.status_bar.showMessage(f"✅ 已删除 {len(selected_rows)} 个事件")

            self.debug_logger.log_info(f"已删除 {len(selected_rows)} 个事件，使用逻辑: {time_option}")

            

            # 立即更新预计总时间

            self.on_calculate_total_time()

        finally:

            # 结束批量操作

            self._batch_operation = False

    

    def on_copy_event(self):

        """复制事件"""

        selected_rows = self.get_selected_event_rows()

        if selected_rows:

            self.copied_events = []

            for row in selected_rows:

                event_data = []

                for col in range(1, 8):  # 跳过行号列

                    item = self.events_table.item(row, col)

                    if item:

                        event_data.append(item.text())

                    else:

                        event_data.append("")

                self.copied_events.append(event_data)

            

            self.status_bar.showMessage(f"📋 已复制 {len(selected_rows)} 个事件")

            self.debug_logger.log_info(f"已复制 {len(selected_rows)} 个事件")

        else:

            self.debug_logger.log_warning("尝试复制事件但未选择事件")

            ChineseMessageBox.show_warning(self, "警告", "请先选择要复制的事件")

    

    def on_cut_event(self):

        """剪切事件 - 先复制再删除"""

        try:

            selected_rows = self.get_selected_event_rows()

            if not selected_rows:

                self.debug_logger.log_warning("尝试剪切事件但未选择事件")

                ChineseMessageBox.show_warning(self, "警告", "请先选择要剪切的事件")

                return

            

            # 先复制事件

            self.on_copy_event()

            

            # 然后删除事件

            self.on_delete_event()

            

            self.status_bar.showMessage(f"✂️ 已剪切 {len(selected_rows)} 个事件")

            self.debug_logger.log_info(f"已剪切 {len(selected_rows)} 个事件")

            

        except Exception as e:

            error_msg = f"剪切事件失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_paste_event(self):

        """粘贴事件 - 增强版：根据菜单设置决定行为"""

        if not self.copied_events:

            self.debug_logger.log_warning("尝试粘贴但没有复制的事件")

            ChineseMessageBox.show_warning(self, "警告", "没有可粘贴的事件")

            return

        

        try:

            # 获取插入位置 - 关键修复：正确识别插入位置

            selected_rows = self.get_selected_event_rows()

            if selected_rows:

                # 有选中事件：在第一个选中事件后插入

                insert_position = selected_rows[0] + 1

                insert_after_item = selected_rows[0]  # 在这个事件后插入

            else:

                # 没有选中事件：在最后插入

                insert_position = self.events_table.rowCount()

                insert_after_item = None  # 在最后插入

            

            # 获取粘贴逻辑设置

            paste_logic = self.get_paste_logic()

            time_option = None

            

            # 根据设置决定是否弹出提示

            if paste_logic == 'prompt':

                # 显示粘贴选项对话框

                paste_dialog = PasteOptionsDialog(self)

                if paste_dialog.exec() != QDialog.DialogCode.Accepted:

                    self.debug_logger.log_info("用户取消粘贴事件")

                    return

                time_option = paste_dialog.get_time_option()

            else:

                # 使用默认设置

                time_option = "仅修改当前事件时间" if paste_logic == 'current' else "修改后重新计算后续事件时间"

                self.debug_logger.log_info(f"使用默认粘贴逻辑: {time_option}")

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 获取前一个事件的绝对时间

                if insert_position == 0:

                    prev_absolute_time = 0

                else:

                    prev_item = self.events_table.item(insert_position - 1, 7)  # 绝对偏移列

                    prev_absolute_time = int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0

                

                # 获取下一个事件的绝对时间（如果存在）

                next_absolute_time = None

                if insert_position < self.events_table.rowCount():

                    next_item = self.events_table.item(insert_position, 7)  # 绝对偏移列

                    if next_item and next_item.text().isdigit():

                        next_absolute_time = int(next_item.text())

                

                # 关键修复：依次计算每个粘贴事件的绝对时间

                current_absolute_time = prev_absolute_time

                for i, event_data in enumerate(self.copied_events):

                    # 使用复制事件原有的相对时间（相对偏移）

                    original_relative_time = int(event_data[5]) if event_data[5] and event_data[5].isdigit() else 100

                    

                    # 计算当前粘贴事件的绝对时间：前一个事件的绝对时间 + 当前事件的相对时间

                    current_absolute_time += original_relative_time

                    

                    # 插入新行

                    self.events_table.insertRow(insert_position + i)

                    new_row_data = [

                        str(insert_position + i + 1),  # 行号，后面会重新编号

                        event_data[0],  # 事件名称

                        event_data[1],  # 事件类型

                        event_data[2],  # 键码

                        event_data[3],  # X坐标

                        event_data[4],  # Y坐标

                        str(original_relative_time),  # 相对偏移（相对时间）使用复制事件原有的相对时间

                        str(current_absolute_time)  # 绝对偏移（绝对时间）重新计算

                    ]

                    

                    for col, data in enumerate(new_row_data):

                        item = QTableWidgetItem(str(data))

                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                        self.events_table.setItem(insert_position + i, col, item)

                

                # 更新行号

                self.update_row_numbers()

                

                # 根据时间修改选项调整后续事件

                if time_option == "仅修改当前事件时间":

                    # 粘贴后原先下一个事件的绝对时间不变，计算相对时间

                    if next_absolute_time is not None:

                        next_row = insert_position + len(self.copied_events)

                        if next_row < self.events_table.rowCount():

                            # 计算新的相对时间：下一个事件的绝对时间 - 最后一个粘贴事件的绝对时间

                            new_relative_time = next_absolute_time - current_absolute_time

                            # 更新下一个事件的相对时间

                            next_relative_item = QTableWidgetItem(str(new_relative_time))

                            next_relative_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                            self.events_table.setItem(next_row, 6, next_relative_item)

                else:  # 修改后重新计算后续事件时间

                    # 重新计算后续所有事件的绝对时间

                    self.recalculate_time_from_row(insert_position + len(self.copied_events))

                

                self.update_stats()

                self.status_bar.showMessage(f"📎 已粘贴 {len(self.copied_events)} 个事件")

                self.debug_logger.log_info(f"已粘贴 {len(self.copied_events)} 个事件，使用逻辑: {time_option}")

                

                # 立即更新预计总时间

                self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

                

        except Exception as e:

            self._batch_operation = False

            error_msg = f"粘贴事件错误: {e}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", f"粘贴事件失败: {str(e)}")

    

    def on_clear_events(self):

        """清空事件 - 修复问题2：确保清空操作正确执行"""

        if self.events_table.rowCount() == 0:

            self.debug_logger.log_info("事件列表已经是空的")

            ChineseMessageBox.show_info(self, "提示", "事件列表已经是空的")

            return

            

        if ChineseMessageBox.show_question(self, "确认", "确定要清空所有事件吗？"):

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 修复问题2：确保清空操作正确执行

                self.events_table.setRowCount(0)

                self.update_stats()

                self.status_bar.showMessage("✅ 已清空所有事件")

                self.debug_logger.log_info("已清空所有事件")

                

                # 修复：清空事件后立即保存状态

                QTimer.singleShot(100, self.save_state)

                

                # 立即更新预计总时间

                self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

    

    def on_import_script(self):

        """导入脚本 - 修复版：正确显示事件名称"""

        try:

            filename, _ = QFileDialog.getOpenFileName(

                self,

                "导入脚本",

                "",

                "JSON文件 (*.json);;所有文件 (*.*)"

            )

            

            if not filename:

                self.debug_logger.log_info("用户取消导入脚本")

                return

            

            with open(filename, 'r', encoding='utf-8') as f:

                events_data = json.load(f)

            

            # 兼容不同格式的导入

            events = []

            if isinstance(events_data, dict):

                if "macroEvents" in events_data:

                    events = events_data["macroEvents"]

                elif "events" in events_data:

                    events = events_data["events"]

                else:

                    events = events_data

            elif isinstance(events_data, list):

                events = events_data

            else:

                self.debug_logger.log_error(f"导入脚本格式不正确: {type(events_data)}")

                ChineseMessageBox.show_error(self, "错误", "文件格式不正确")

                return

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 清空现有事件

                self.events_table.setRowCount(0)

                

                # 导入新事件

                converted_events = []

                for i, event in enumerate(events):

                    if isinstance(event, dict):

                        # 获取事件类型和鼠标按钮

                        event_type_num = event.get("type", 0)

                        mouse_button = event.get("mouseButton")

                        

                        # 使用新函数转换事件类型

                        event_type_str = convert_event_type_num_to_str_with_button(event_type_num, mouse_button)

                        

                        # 获取键码

                        keycode = str(event.get("keyCode", ""))

                        

                        # 生成包含按键名称的事件名称

                        event_name = generate_key_event_name(event_type_str, keycode)

                        

                        x = str(event.get("mouseX", 0))

                        y = str(event.get("mouseY", 0))

                        absolute_time = str(int(event.get("time", 0)))  # 确保是整数

                        

                        # 计算相对时间

                        if i > 0:

                            prev_time = int(events[i-1].get("time", 0))

                            relative_time = str(int(absolute_time) - prev_time)

                        else:

                            relative_time = "0"

                        

                        converted_events.append((i+1, event_name, event_type_str, keycode, x, y, relative_time, absolute_time))

                        

                        # 记录导入日志

                        self.debug_logger.log_info(f"导入事件 {i+1}: {event_name} (类型: {event_type_str}, 键码: {keycode})")

                

                for event in converted_events:

                    self.add_table_row(event)

                

                self.update_stats()

                self.status_bar.showMessage(f"✅ 已导入 {len(converted_events)} 个事件")

                self.debug_logger.log_info(f"已导入 {len(converted_events)} 个事件")

                

                # 立即更新预计总时间

                self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

            

        except Exception as e:

            self._batch_operation = False

            error_msg = f"导入脚本失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_sort_events(self):

        """事件排序 - 修正版：先按绝对时间排序，再重新计算相对时间"""

        try:

            if self.events_table.rowCount() == 0:

                self.debug_logger.log_warning("尝试排序但没有事件")

                ChineseMessageBox.show_warning(self, "警告", "没有可排序的事件")

                return

            

            # 保存当前状态到撤销栈

            self.save_state_to_undo_stack()

            

            # 开始批量操作

            self._batch_operation = True

            

            try:

                # 获取所有事件数据

                events = []

                for row in range(self.events_table.rowCount()):

                    event_data = []

                    for col in range(8):  # 包括行号列

                        item = self.events_table.item(row, col)

                        if item:

                            event_data.append(item.text())

                        else:

                            event_data.append("")

                    events.append(event_data)

                

                # 关键修正：按绝对时间（第7列，索引为7）排序

                events.sort(key=lambda x: int(x[7]) if x[7].isdigit() else 0)

                

                # 清空表格

                self.events_table.setRowCount(0)

                

                # 重新计算相对时间并插入

                prev_absolute_time = 0

                for i, event in enumerate(events):

                    # 获取当前事件的绝对时间

                    current_absolute_time = int(event[7]) if event[7].isdigit() else 0

                    

                    # 计算新的相对时间 = 当前绝对时间 - 前一个事件的绝对时间

                    relative_time = current_absolute_time - prev_absolute_time

                    

                    # 更新事件数据

                    event[0] = str(i + 1)  # 更新行号

                    event[6] = str(relative_time)  # 更新相对时间

                    # 绝对时间保持不变（event[7]）

                    

                    # 插入事件

                    self.add_table_row(event)

                    

                    # 更新前一个事件的绝对时间

                    prev_absolute_time = current_absolute_time

                

                self.update_stats()

                self.status_bar.showMessage(f"✅ 已对 {len(events)} 个事件进行排序")

                self.debug_logger.log_info(f"已对 {len(events)} 个事件进行排序")

                

                # 立即更新预计总时间

                self.on_calculate_total_time()

            finally:

                # 结束批量操作

                self._batch_operation = False

            

        except Exception as e:

            self._batch_operation = False

            error_msg = f"事件排序失败: {str(e)}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            ChineseMessageBox.show_error(self, "错误", error_msg)

    

    def on_select_all_events(self):

        """全选事件"""

        self.events_table.selectAll()

        self.status_bar.showMessage("✅ 已全选所有事件")

        self.debug_logger.log_info("已全选所有事件")

    

    def on_undo(self):

        """撤销"""

        if self.undo_stack:

            # 保存当前状态到重做栈

            current_state = self.get_current_state()

            self.redo_stack.append(current_state)

            

            # 恢复到上一个状态

            state = self.undo_stack.pop()

            self.restore_state(state)

            

            self.status_bar.showMessage("↩️ 已撤销操作")

            self.debug_logger.log_info("已撤销操作")

            self.update_undo_redo_buttons()

            

            # 立即更新预计总时间

            self.on_calculate_total_time()

        else:

            self.status_bar.showMessage("↩️ 没有可撤销的操作")

            self.debug_logger.log_info("尝试撤销但没有可撤销的操作")

    

    def on_redo(self):

        """重做"""

        if self.redo_stack:

            # 保存当前状态到撤销栈

            current_state = self.get_current_state()

            self.undo_stack.append(current_state)

            

            # 恢复到重做状态

            state = self.redo_stack.pop()

            self.restore_state(state)

            

            self.status_bar.showMessage("↪️ 已重做操作")

            self.debug_logger.log_info("已重做操作")

            self.update_undo_redo_buttons()

            

            # 立即更新预计总时间

            self.on_calculate_total_time()

        else:

            self.status_bar.showMessage("↪️ 没有可重做的操作")

            self.debug_logger.log_info("尝试重做但没有可重做的操作")

    

    def save_state_to_undo_stack(self):

        """保存当前状态到撤销栈"""

        state = self.get_current_state()

        self.undo_stack.append(state)

        

        # 限制撤销栈大小

        if len(self.undo_stack) > self.max_undo_steps:

            self.undo_stack.pop(0)

        

        # 清空重做栈

        self.redo_stack.clear()

        

        self.update_undo_redo_buttons()

    

    def save_state_to_redo_stack(self):

        """保存当前状态到重做栈"""

        state = self.get_current_state()

        self.redo_stack.append(state)

        

        # 限制重做栈大小

        if len(self.redo_stack) > self.max_undo_steps:

            self.redo_stack.pop(0)

    

    def get_current_state(self):

        """获取当前状态"""

        state = {

            'events': [],

            'loop_count': str(self.settings_panel.loop_count_input.value()),

            'interval': str(self.settings_panel.interval_input.value()),

            'time_unit': self.settings_panel.time_unit_combo.currentText(),

            'width': self.settings_panel.width_input.text(),

            'height': self.settings_panel.height_input.text(),

            'scale': self.settings_panel.scale_combo.currentText(),

            'delete_logic': self.get_delete_logic(),

            'paste_logic': self.get_paste_logic()

        }

        

        # 保存事件数据

        for row in range(self.events_table.rowCount()):

            event_data = []

            for col in range(8):  # 包括所有列

                item = self.events_table.item(row, col)

                if item:

                    event_data.append(item.text())

                else:

                    event_data.append("")

            state['events'].append(event_data)

        

        return state

    

    def restore_state(self, state):

        """恢复状态"""

        # 开始批量操作

        self._batch_operation = True

        

        try:

            # 恢复事件数据

            self.events_table.setRowCount(0)

            # 批量添加事件数据

            self.add_table_rows(state['events'])

            

            # 恢复其他设置

            self.settings_panel.restore_settings(state)

            

            # 恢复时间逻辑设置

            self.delete_logic = state.get('delete_logic', 'prompt')

            self.paste_logic = state.get('paste_logic', 'prompt')

            self.update_time_logic_menu_state()

            

            self.update_stats()

            self.on_calculate_total_time()

        finally:

            # 结束批量操作

            self._batch_operation = False

    

    def update_undo_redo_buttons(self):

        """更新撤销重做按钮状态"""

        self.undo_btn.setEnabled(len(self.undo_stack) > 0)

        self.redo_btn.setEnabled(len(self.redo_stack) > 0)

    

    def on_table_changed(self, item):

        """表格内容变化时更新统计"""

        # 防止递归调用和批量操作

        if self._table_changing or self._batch_operation:

            return

        

        self._table_changing = True

        

        # 如果是行号列，确保行号正确

        if item.column() == 0:

            self.update_row_numbers()

        

        # 延迟保存状态到撤销栈，将连续的单元格变化合并为一个撤销状态

        self._pending_undo_save = True

        self._undo_save_timer.start()

        

        self.update_stats()

        self._table_changing = False

        

        # 立即更新预计总时间

        self.on_calculate_total_time()

    

    def _delayed_save_state(self):

        """延迟保存状态到撤销栈"""

        if self._pending_undo_save:

            self.save_state_to_undo_stack()

            self._pending_undo_save = False

            self.debug_logger.log_debug("延迟保存撤销状态")

    

    def _recalculate_times_from_index(self, start_index, start_absolute_time):

        """从指定索引开始重新计算所有事件的相对时间和绝对时间"""

        try:

            if start_index < 0 or start_index >= self.events_table.rowCount():

                return



            current_absolute_time = start_absolute_time

            # 临时禁用UI更新，减少卡顿
            self.events_table.setUpdatesEnabled(False)
            
            try:
                for row in range(start_index, self.events_table.rowCount()):

                    # 获取当前行的相对时间
                    relative_time_item = self.events_table.item(row, 6)  # 相对时间列
                    relative_time = 0
                    if relative_time_item and relative_time_item.text().isdigit():
                        relative_time = int(relative_time_item.text())

                    # 计算当前行的绝对时间
                    current_absolute_time += relative_time

                    # 更新绝对时间
                    absolute_time_item = QTableWidgetItem(str(current_absolute_time))
                    absolute_time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.events_table.setItem(row, 7, absolute_time_item)
            finally:
                # 重新启用UI更新并刷新
                self.events_table.setUpdatesEnabled(True)
                self.events_table.viewport().update()

        except Exception as e:

            error_msg = f"重新计算时间失败: {e}"

            self.debug_logger.log_error(error_msg)
            # 确保UI更新被重新启用
            self.events_table.setUpdatesEnabled(True)

    

    def on_detect_screen_info(self):

        """检测屏幕分辨率和缩放比例"""

        self.debug_logger.log_info("开始检测屏幕信息...")

        width, height = self.get_screen_resolution()

        scale = self.get_system_scale()

        

        # 更新输入框和下拉列表

        self.settings_panel.update_screen_settings(width, height, scale)

        

        self.update_stats()

        self.status_bar.showMessage(f"✅ 已获取屏幕信息: {width}×{height}, 缩放: {scale}")

        self.debug_logger.log_info(f"屏幕信息获取完成: {width}×{height}, 缩放: {scale}")

    

    def on_calculate_total_time(self):

        """计算总时间 - 调用面板的方法"""

        try:

            # 调用统计面板的计算方法

            if hasattr(self, 'stats_panel'):

                total_ms = self.stats_panel.calculate_total_time_ms()

                self.settings_panel.update_total_time_display(total_ms)

                

        except Exception as e:

            self.debug_logger.log_error(f"计算总时间失败: {e}")

            self.settings_panel.update_total_time_display(0)

    

    def get_selected_event_rows(self):

        """获取选中的事件行"""

        selected_rows = []

        for item in self.events_table.selectedItems():

            if item.row() not in selected_rows:

                selected_rows.append(item.row())

        return sorted(selected_rows)

    

    def update_row_numbers(self):

        """更新行号"""

        for row in range(self.events_table.rowCount()):

            item = QTableWidgetItem(str(row + 1))

            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            self.events_table.setItem(row, 0, item)

    

    def recalculate_time_from_row(self, start_row):

        """从指定行开始重新计算时间"""

        try:

            if start_row < 0 or start_row >= self.events_table.rowCount():

                return

            

            # 获取前一行的绝对时间

            if start_row == 0:

                prev_absolute_time = 0

            else:

                prev_item = self.events_table.item(start_row - 1, 7)  # 绝对时间列

                prev_absolute_time = int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0

            

            # 从指定行开始重新计算所有事件的绝对时间

            for row in range(start_row, self.events_table.rowCount()):

                # 获取相对时间

                relative_item = self.events_table.item(row, 6)  # 相对时间列

                if relative_item and relative_item.text().isdigit():

                    relative_time = int(relative_item.text())

                else:

                    relative_time = 0

                

                # 计算新的绝对时间

                new_absolute_time = prev_absolute_time + relative_time

                

                # 更新绝对时间

                absolute_item = QTableWidgetItem(str(new_absolute_time))

                absolute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

                self.events_table.setItem(row, 7, absolute_item)

                

                # 更新前一个绝对时间

                prev_absolute_time = new_absolute_time

            

            self.update_stats()

            

        except Exception as e:

            error_msg = f"重新计算时间错误: {e}"

            self.debug_logger.log_error(error_msg)

    

    def keyPressEvent(self, event):

        """键盘按键事件处理"""

        # 处理快捷键

        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:

            if event.key() == Qt.Key.Key_X:  # Ctrl+X - 剪切

                self.on_cut_event()

                event.accept()

                return

            elif event.key() == Qt.Key.Key_C:  # Ctrl+C - 复制

                self.on_copy_event()

                event.accept()

                return

            elif event.key() == Qt.Key.Key_V:  # Ctrl+V - 粘贴

                self.on_paste_event()

                event.accept()

                return

            elif event.key() == Qt.Key.Key_A:  # Ctrl+A - 全选

                self.on_select_all_events()

                event.accept()

                return

            elif event.key() == Qt.Key.Key_Z:  # Ctrl+Z - 撤销

                self.on_undo()

                event.accept()

                return

            elif event.key() == Qt.Key.Key_Y:  # Ctrl+Y - 重做

                self.on_redo()

                event.accept()

                return

        

        # Delete 键 - 删除

        elif event.key() == Qt.Key.Key_Delete:

            self.on_delete_event()

            event.accept()

            return

        

        # 其他按键交给父类处理

        super().keyPressEvent(event)

    

    def save_state(self):

        """保存程序状态到程序目录"""

        try:

            state = self.get_current_state()

            

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 保存状态到程序目录

            state_file = os.path.join(app_dir, "BetterGI_StellTrack_state.json")

            with open(state_file, 'w', encoding='utf-8') as f:

                json.dump(state, f, ensure_ascii=False, indent=2)

            

            # 记录操作日志

            self.debug_logger.log_info("程序状态已保存")

            

            return True

        except Exception as e:

            error_msg = f"保存状态失败: {e}"

            self.debug_logger.log_error(error_msg)

            return False

    

    def load_saved_state(self):

        """从程序目录加载保存的程序状态"""

        try:

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 状态文件路径

            state_file = os.path.join(app_dir, "BetterGI_StellTrack_state.json")

            

            if os.path.exists(state_file):

                with open(state_file, 'r', encoding='utf-8') as f:

                    state = json.load(f)

                

                self.restore_state(state)

                self.debug_logger.log_info("程序状态已加载")

                self.status_bar.showMessage("✅ 已加载保存的状态")

                return True

            else:

                self.debug_logger.log_info("未找到保存的状态文件")

        except Exception as e:

            error_msg = f"加载状态失败: {e}"

            self.debug_logger.log_error(error_msg)

        

        return False

    

    def resizeEvent(self, event):

        """窗口大小改变事件 - 保存窗口状态"""

        super().resizeEvent(event)

        # 延迟保存状态，避免频繁保存

        if hasattr(self, '_resize_timer'):

            self._resize_timer.stop()

        else:

            self._resize_timer = QTimer()

            self._resize_timer.setSingleShot(True)

            self._resize_timer.timeout.connect(self.save_state)

        

        self._resize_timer.start(500)  # 500毫秒后保存状态

    

    def closeEvent(self, event):

        """关闭事件 - 保存状态"""

        self.debug_logger.log_info("主窗口关闭中...")

        if self.save_state():

            self.status_bar.showMessage("✅ 状态已保存")

            self.debug_logger.log_info("程序正常关闭")

        else:

            self.status_bar.showMessage("⚠️ 状态保存失败")

            self.debug_logger.log_error("程序关闭时状态保存失败")

        

        event.accept()
