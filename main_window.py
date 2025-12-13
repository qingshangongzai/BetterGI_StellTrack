# main_window.py

import sys
import os
import json
import ctypes
import time
from datetime import datetime

from PyQt6.QtWidgets import (
                            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QTextEdit, QFrame, QGroupBox, QGridLayout,
                            QHeaderView, QScrollArea, QSizePolicy, QSplitter,
                            QMessageBox, QStatusBar, QFileDialog, QDialog, QMenu, QMenuBar,
                            QCheckBox)

from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize

from PyQt6.QtGui import (QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor,
                        QKeyEvent, QDesktopServices, QIntValidator, QAction, QFontDatabase)


# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager, ChineseMessageBox, ModernGroupBox, ModernLineEdit, ModernComboBox, ModernDoubleSpinBox, StyledMainWindow, StyledDialog

from styles import WindowIconMixin, DialogFactory

from utils import VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP, convert_event_type_num_to_str_with_button, generate_key_event_name, load_icon_universal, load_logo, get_current_version, get_current_app_info

# 导入关于窗口模块


from about_window import AboutWindowQt

# 导入事件对话框模块


from event_dialogs import EventEditDialog, PasteOptionsDialog, SimpleCoordinateCapture, DeleteOptionsDialog

# 导入调试工具模块


from debug_tools import PasswordDialog, DebugWindow, get_global_debug_logger

# 导入新拆分的模块


from panels import SettingsPanel, OperationsPanel, StatsPanel
from event_manager import EventManager
from script_manager import ScriptManager

# 导入事件时间分析模块


from time_analysis import EventTimeAnalyzerDialog

# 导入版本管理器




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

        self.setFixedSize(485, 400)  # 调整窗口大小，宽度再缩小50px，高度保持不变

        


        layout = QVBoxLayout(self)

        layout.setSpacing(15)

        layout.setContentsMargins(20, 15, 20, 15)

        


        # 标题区域

        title_label = QLabel("批量编辑事件")

        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 16, QFont.Weight.Bold)

        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 10px;")

        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(title_label)

        


        # 操作选项组

        operation_group = ModernGroupBox("操作选项")

        operation_layout = QGridLayout(operation_group)  # 使用GridLayout确保精确对齐

        operation_layout.setSpacing(10)

        operation_layout.setContentsMargins(15, 15, 15, 15)

        


        # 设置统一的输入框宽度
        input_width = 120
        
        # 1. 增减偏移时间
        offset_label = QLabel("增减绝对时间:")
        offset_label.setFixedWidth(120)
        self.offset_input = ModernDoubleSpinBox()
        self.offset_input.setMinimum(-999999)
        self.offset_input.setMaximum(999999)
        self.offset_input.setValue(0)
        self.offset_input.setDecimals(0)
        self.offset_input.setSingleStep(100) 
        self.offset_input.setFixedWidth(input_width)

        offset_label_unit = QLabel("ms")
        offset_label_unit.setFixedWidth(20)
        offset_label_unit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        operation_layout.addWidget(offset_label, 0, 0)
        operation_layout.addWidget(self.offset_input, 0, 1)
        operation_layout.addWidget(offset_label_unit, 0, 2)

        # 2. 统一相对时间
        rel_time_label = QLabel("统一相对时间:")
        rel_time_label.setFixedWidth(120)
        self.rel_time_input = ModernDoubleSpinBox()
        self.rel_time_input.setMinimum(0)
        self.rel_time_input.setMaximum(999999)
        self.rel_time_input.setValue(0)
        self.rel_time_input.setDecimals(0)
        self.rel_time_input.setSingleStep(100) 
        self.rel_time_input.setFixedWidth(input_width)

        rel_time_label_unit = QLabel("ms")
        rel_time_label_unit.setFixedWidth(20)
        rel_time_label_unit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        operation_layout.addWidget(rel_time_label, 1, 0)
        operation_layout.addWidget(self.rel_time_input, 1, 1)
        operation_layout.addWidget(rel_time_label_unit, 1, 2)

        


        # 3. 事件类型替换
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
        
        # 确保old_type_combo宽度一致
        self.old_type_combo = ModernComboBox(width=input_width)
        self.old_type_combo.addItem("不替换类型")
        self.old_type_combo.addItems(base_event_types)
        # 添加具体按键事件到old_type_combo，只显示事件名称
        for event_name in sorted(self.key_events.keys()):
            self.old_type_combo.addItem(event_name)

        type_arrow_label = QLabel("→")
        type_arrow_label.setFixedWidth(20)
        type_arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 确保new_type_combo宽度一致
        self.new_type_combo = ModernComboBox(width=input_width)
        self.new_type_combo.addItems(base_event_types)
        # 添加具体按键事件到new_type_combo，只显示事件名称
        for event_name in sorted(self.key_events.keys()):
            self.new_type_combo.addItem(event_name)

        operation_layout.addWidget(QLabel("事件类型替换:"), 2, 0)
        operation_layout.addWidget(self.old_type_combo, 2, 1)
        operation_layout.addWidget(type_arrow_label, 2, 2)
        operation_layout.addWidget(self.new_type_combo, 2, 3)
        
        # 4. 统一坐标（带开关）
        # 清除之前的所有组件，重新设计布局
        
        # 创建水平布局来容纳统一坐标的所有组件
        unified_coords_layout = QHBoxLayout()
        unified_coords_layout.setContentsMargins(0, 0, 0, 0)
        unified_coords_layout.setSpacing(0)
        
        # 1. 统一坐标复选框
        self.unified_coords_checkbox = QCheckBox()
        unified_coords_layout.addWidget(self.unified_coords_checkbox)
        
        # 2. 统一坐标标签
        unified_label = QLabel("统一坐标:")
        unified_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(unified_label)
        
        # 3. 空白间距
        unified_coords_layout.addSpacing(20)
        
        # 4. x坐标标签
        x_label = QLabel("X坐标:")
        x_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(x_label)
        
        # 5. x坐标输入框
        self.x_input = ModernLineEdit()
        self.x_input.setText("0")
        self.x_input.setFixedWidth(input_width)
        unified_coords_layout.addWidget(self.x_input)
        
        # 6. 空白间距
        unified_coords_layout.addSpacing(3)
        
        # 7. y坐标标签
        y_label = QLabel("Y坐标:")
        y_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(y_label)
        
        # 8. y坐标输入框
        self.y_input = ModernLineEdit()
        self.y_input.setText("0")
        self.y_input.setFixedWidth(input_width)
        unified_coords_layout.addWidget(self.y_input)
        
        # 9. 拉伸空间
        unified_coords_layout.addStretch()
        
        # 将整个水平布局添加到GridLayout中
        operation_layout.addLayout(unified_coords_layout, 3, 0, 1, 5, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 将操作选项组添加到主布局
        layout.addWidget(operation_group)

        # 添加提示信息
        hint_label = QLabel("💡 提示：按键事件替换支持将事件列表中已有的按键事件替换为另一个已有的按键事件")
        hint_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;")
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
        
        # 设置对话框布局
        self.setLayout(layout)

    


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
    
    def get_unified_coordinates(self):
        """获取统一坐标值和应用标志"""
        apply_coords = self.unified_coords_checkbox.isChecked()
        
        try:
            x = int(self.x_input.text())
        except ValueError:
            x = 0
        try:
            y = int(self.y_input.text())
        except ValueError:
            y = 0
        
        return apply_coords, x, y




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

        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 16, QFont.Weight.Bold)

        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 3px;")

        title_layout.addWidget(title_label)

        


        # 副标题 - 使用SourceHanSerifCN字体

        subtitle_label = QLabel("请输入访问密码或特殊文字")

        UnifiedStyleHelper.get_instance().set_source_han_font(subtitle_label, 11)

        subtitle_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']}; margin-bottom: 8px;")

        title_layout.addWidget(subtitle_label)

        


        # 提示信息

        hint_label = QLabel("💡 提示：尝试输入一些有意义的句子")

        hint_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-bottom: 12px;")

        title_layout.addWidget(hint_label)

        layout.addLayout(title_layout)

        


        # 输入区域

        input_layout = QVBoxLayout()

        


        # 输入框标签

        input_label = QLabel("输入内容：")

        UnifiedStyleHelper.get_instance().set_source_han_font(input_label, 10)

        input_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']}; margin-bottom: 3px;")

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

            confirm_dialog.setFixedSize(300, 150)

            confirm_dialog.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                                        Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)

            


            confirm_layout = QVBoxLayout(confirm_dialog)

            confirm_layout.setSpacing(15)

            confirm_layout.setContentsMargins(20, 20, 20, 20)

            



            # 彩蛋信息

            info_label = QLabel("恭喜你发现了彩蛋")

            info_label.setFont(self.font_manager.get_source_han_font(10))

            info_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")

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

                # 用户取消，关闭输入对话框

                self.reject()

        


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




class ModernTableWidget(QTableWidget):

    """现代化的表格控件"""

    def __init__(self, rows=0, columns=0, parent=None):

        super().__init__(rows, columns, parent)

        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_table_style())

        

        

        # 设置表格属性

        self.setAlternatingRowColors(False)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        self.horizontalHeader().setStretchLastSection(True)

        # 调整表头行高
        self.horizontalHeader().setDefaultSectionSize(24)

        

        

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

        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_header_widget_style())

        


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

        UnifiedStyleHelper.get_instance().set_smiley_font(main_title, 24, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体

        main_title.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")

        title_text_layout.addWidget(main_title)

        


        # 副标题 - 英文名 - 使用得意黑字体

        subtitle = QLabel(app_info["name_en"])

        UnifiedStyleHelper.get_instance().set_smiley_font(subtitle, 12)  # 使用UnifiedStyleHelper统一设置字体

        subtitle.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")

        title_text_layout.addWidget(subtitle)

        title_layout.addLayout(title_text_layout)

        title_layout.addStretch()

        


        # 移除版本信息和关于按钮，替换为标语

        slogan_label = QLabel("风带来故事的种子，时间使之发芽")

        slogan_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_slogan_label_style())

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

        self.logo_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_logo_label_style())

        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)




# =============================================================================

# 主窗口类

# =============================================================================




class MainWindow(StyledMainWindow, WindowIconMixin):
    """应用程序主窗口类
    
    作为应用程序的核心界面，管理所有UI组件、事件处理和功能模块。
    负责整合事件管理、脚本生成、面板显示等核心功能。
    
    继承关系：
    - StyledMainWindow: 提供基础样式和布局支持
    - WindowIconMixin: 提供窗口图标设置功能
    """

    


    def __init__(self):
        """初始化主窗口
        
        初始化窗口属性、组件、管理器和信号槽连接。
        设置窗口标题、大小、图标和样式。
        
        主要初始化内容：
        - 核心属性和标志位
        - 撤销/重做系统
        - 调试日志记录器
        - 事件管理器和脚本管理器
        - 自动保存定时器
        - 窗口样式和布局
        """
        super().__init__()
        
        # 核心属性初始化
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
        # 初始化事件管理器和脚本管理器
        self.event_manager = EventManager(self)
        self.script_manager = ScriptManager(self)
        
        # 初始化自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(30000)  # 30秒自动保存一次
        self.auto_save_timer.timeout.connect(self.save_saved_state)
        self.auto_save_timer.start()

        


        try:

            # 获取应用程序信息

            app_info = get_current_app_info()

            version = get_current_version()

            


            # 设置窗口标志为标准主窗口样式，允许移动和调整大小

            self.setWindowFlags(Qt.WindowType.Window)

            


            self.setWindowTitle(f"{app_info['name']} v{version}")

            # 缩小主窗口大小

            self.setMinimumSize(1100, 750)

            self.resize(1200,820)

            


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

            if self.event_manager.events_table.rowCount() == 0:

                self.event_manager.add_sample_data()

            


            # 窗口显示后设置任务栏图标
            QTimer.singleShot(100, self.fix_taskbar_icon)
            
            # 初始化统计信息和预计总时间
            self.stats_panel.update_stats()
            self.on_calculate_total_time()
            
            # 记录窗口创建成功
            self.debug_logger.log_info("主窗口初始化完成")

            


        except Exception as e:

            error_msg = f"主窗口初始化错误: {e}"

            self.debug_logger.log_error(error_msg, exc_info=True)

            print(error_msg)

            import traceback

            traceback.print_exc()

    


    def create_menu_bar(self):
        """创建应用程序菜单栏
        
        构建包含文件、编辑、工具、设置和帮助等菜单的菜单栏，
        并为每个菜单项连接相应的操作。
        """

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
        


        # 添加事件

        add_action = QAction('添加事件', self)

        add_action.setShortcut('Ctrl+I')

        add_action.triggered.connect(self.event_manager.on_add_event)

        edit_menu.addAction(add_action)
        
        # 编辑事件

        edit_action = QAction('编辑事件', self)

        edit_action.setShortcut('Ctrl+E')

        edit_action.triggered.connect(self.event_manager.on_edit_event)

        edit_menu.addAction(edit_action)
        
        edit_menu.addSeparator()
        
        # 剪切

        cut_action = QAction('剪切', self)

        cut_action.setShortcut('Ctrl+X')

        cut_action.triggered.connect(self.event_manager.on_cut_event)

        edit_menu.addAction(cut_action)

        


        # 复制

        copy_action = QAction('复制', self)

        copy_action.setShortcut('Ctrl+C')

        copy_action.triggered.connect(self.event_manager.on_copy_event)

        edit_menu.addAction(copy_action)

        


        # 粘贴

        paste_action = QAction('粘贴', self)

        paste_action.setShortcut('Ctrl+V')

        paste_action.triggered.connect(self.event_manager.on_paste_event)

        edit_menu.addAction(paste_action)

        


        edit_menu.addSeparator()

        


        # 删除

        delete_action = QAction('删除', self)

        delete_action.setShortcut('Delete')

        delete_action.triggered.connect(self.event_manager.on_delete_event)

        edit_menu.addAction(delete_action)

        


        # 全选

        select_all_action = QAction('全选', self)

        select_all_action.setShortcut('Ctrl+A')

        select_all_action.triggered.connect(self.event_manager.on_select_all_events)

        edit_menu.addAction(select_all_action)
        
        # 批量编辑

        batch_edit_action = QAction('批量编辑', self)

        batch_edit_action.setShortcut('Ctrl+B')

        batch_edit_action.triggered.connect(self.event_manager.on_batch_edit)

        edit_menu.addAction(batch_edit_action)

        


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

        


        # 末尾事件操作跳过弹窗开关
        skip_end_events_action = QAction('末尾事件操作跳过弹窗', self)
        skip_end_events_action.setCheckable(True)
        skip_end_events_action.setChecked(True)  # 默认开启
        skip_end_events_action.triggered.connect(self.set_skip_end_events_prompt)
        time_logic_menu.addAction(skip_end_events_action)
        
        # 保存末尾事件开关的引用
        self.skip_end_events_action = skip_end_events_action

        

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


    def set_skip_end_events_prompt(self, checked):
        """设置末尾事件操作是否跳过弹窗"""
        self.skip_end_events_prompt = checked
        self.save_time_logic_settings()
        status = "开启" if checked else "关闭"
        self.status_bar.showMessage(f"✅ 末尾事件操作跳过弹窗已{status}")
        self.debug_logger.log_info(f"末尾事件操作跳过弹窗已设置为: {checked}")


    def get_skip_end_events_prompt(self):
        """获取末尾事件操作是否跳过弹窗的设置"""
        return getattr(self, 'skip_end_events_prompt', True)


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

        
        # 更新末尾事件操作跳过弹窗开关状态
        if hasattr(self, 'skip_end_events_action'):
            self.skip_end_events_action.setChecked(self.get_skip_end_events_prompt())




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
            settings['skip_end_events_prompt'] = self.get_skip_end_events_prompt()

            


            # 保存设置

            with open(settings_file, 'w', encoding='utf-8') as f:

                json.dump(settings, f, ensure_ascii=False, indent=2)

            


            self.debug_logger.log_info(f"时间逻辑设置已保存: 删除={self.delete_logic}, 粘贴={self.paste_logic}")

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
                self.skip_end_events_prompt = settings.get('skip_end_events_prompt', True)

                

                # 更新菜单状态
                self.update_time_logic_menu_state()

                

                self.debug_logger.log_info(f"时间逻辑设置已加载: 删除={self.delete_logic}, 粘贴={self.paste_logic}, 跳过末尾事件弹窗={self.skip_end_events_prompt}")

                return True

            else:

                # 设置默认值

                self.delete_logic = 'prompt'

                self.paste_logic = 'prompt'
                self.skip_end_events_prompt = True

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

            dialog = EventTimeAnalyzerDialog(self, self.event_manager.events_table)

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
        # 使用styles模块中的UnifiedStyleHelper来统一管理应用程序样式
        from styles import UnifiedStyleHelper
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            UnifiedStyleHelper.get_instance().setup_global_style(app)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理过滤类型下拉框的回车键事件"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        
        # 检查是否是过滤类型下拉框的按键事件
        if hasattr(self, 'search_filter_widgets'):
            search_filter_widgets = self.search_filter_widgets
            if obj == search_filter_widgets['filter_combo']:
                if event.type() == QEvent.Type.KeyPress:
                    key_event = QKeyEvent(event)
                    # 检查是否是回车键
                    if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                        # 触发搜索功能
                        search_filter_widgets['search_func']()
                        return True
        
        # 不是我们要处理的事件，交给父类处理
        return super().eventFilter(obj, event)




    def create_header(self, parent_layout):
        """创建窗口顶部标题和信息区域
        
        在指定的父布局中创建应用程序的头部区域，
        包含应用名称、版本信息和操作按钮等。
        
        Args:
            parent_layout: 父布局对象，用于放置头部组件
        """

        self.header_widget = HeaderWidget()

        parent_layout.addWidget(self.header_widget)




    def create_content_area(self, parent_layout):

        """创建内容区域"""

        # 创建水平分割器

        splitter = QSplitter(Qt.Orientation.Horizontal)

        splitter.setChildrenCollapsible(False)

        splitter.setHandleWidth(0)

        splitter.setStyleSheet(UnifiedStyleHelper.get_instance().get_splitter_style())

        


        # 左侧设置面板

        left_panel = self.create_left_panel()

        splitter.addWidget(left_panel)

        


        # 右侧区域（包含事件编辑和统计信息）

        right_panel = self.create_right_panel()

        splitter.addWidget(right_panel)

        


        # 设置分割比例

        splitter.setSizes([250, 1050])

        


        parent_layout.addWidget(splitter, 1)




    def create_left_panel(self):

        """创建左侧设置面板"""

        container = QWidget()

        container.setMaximumWidth(400)

        container.setStyleSheet(UnifiedStyleHelper.get_instance().get_container_bg_style())

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

        container.setStyleSheet(UnifiedStyleHelper.get_instance().get_container_bg_style())

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
        """创建事件编辑器 - 调用事件管理器"""
        return self.event_manager.create_event_editor(parent)




    def create_status_bar(self):

        """创建状态栏 - 修复灰白不一致问题"""

        self.status_bar = QStatusBar()

        self.setStatusBar(self.status_bar)

        


        # 修复状态栏样式 - 纯白色背景

        self.status_bar.setStyleSheet(UnifiedStyleHelper.get_instance().get_status_bar_style())

        


        self.status_bar.showMessage("✅ 就绪")

        


        # 添加时间显示

        self.time_label = QLabel()

        self.time_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; background-color: transparent;")

        self.status_bar.addPermanentWidget(self.time_label)

        


        # 更新时间

        self.update_time()

        self.timer = QTimer()

        self.timer.timeout.connect(self.update_time)

        self.timer.start(1000)

        


        # 更新快捷键提示，包含新的快捷键

        shortcuts_label = QLabel("快捷键: Ctrl+Z撤销 | Ctrl+Y重做 | Ctrl+I添加事件 | Ctrl+E编辑事件 | Ctrl+B批量编辑 | Ctrl+A全选 | Ctrl+X剪切 | Ctrl+C复制 | Ctrl+V粘贴 | Delete删除 | Ctrl+S保存")

        shortcuts_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 9px; margin-right: 10px; background-color: transparent;")

        self.status_bar.addPermanentWidget(shortcuts_label)




    def update_time(self):

        """更新时间显示"""

        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")

        self.time_label.setText(f"🕒 {current_time}")




    def connect_signals(self):
        """连接信号槽"""
        # 操作按钮信号 - 修改为调用面板的方法
        self.operations_panel.generate_btn.clicked.connect(self.script_manager.on_generate_script)
        self.operations_panel.save_btn.clicked.connect(self.script_manager.on_save_script)
        self.operations_panel.preview_btn.clicked.connect(self.operations_panel.on_preview_script)
        self.operations_panel.import_script_btn.clicked.connect(self.script_manager.on_import_script)
        
        # 设置面板信号
        self.settings_panel.detect_screen_btn.clicked.connect(self.on_detect_screen_info)
        self.settings_panel.loop_count_input.valueChanged.connect(self.on_calculate_total_time)
        self.settings_panel.interval_input.valueChanged.connect(self.on_calculate_total_time)
        self.settings_panel.time_unit_combo.currentTextChanged.connect(self.on_calculate_total_time)




    def on_detect_screen_info(self):
        """检测屏幕分辨率和缩放比例"""
        self.debug_logger.log_info("开始检测屏幕信息...")
        
        # 获取屏幕分辨率
        width, height = self.get_screen_resolution()
        
        # 获取系统缩放比例
        scale = self.get_system_scale()
        
        # 更新设置面板
        self.settings_panel.update_screen_settings(width, height, scale)
        
        # 更新统计信息
        self.event_manager.update_stats()
        
        self.status_bar.showMessage(f"✅ 已获取屏幕信息: {width}×{height}, 缩放: {scale}")
        self.debug_logger.log_info(f"屏幕信息获取完成: {width}×{height}, 缩放: {scale}")
    
    def get_screen_resolution(self):
        """获取屏幕分辨率（参考原代码实现）"""
        try:
            user32 = ctypes.windll.user32
            
            # 方法1: 使用GetSystemMetrics获取主显示器分辨率
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
            except Exception as inner_e:
                self.debug_logger.log_debug(f"获取实际分辨率失败: {inner_e}")
            
            return width, height
        except Exception as e:
            self.debug_logger.log_error(f"获取屏幕分辨率失败: {e}")
            return 1920, 1080
    
    def get_system_scale(self):
        """获取系统缩放比例"""
        try:
            user32 = ctypes.windll.user32
            
            # 获取主显示器的DPI
            try:
                hdc = user32.GetDC(0)
                if hdc:
                    # 获取逻辑DPI
                    logical_dpi_x = ctypes.windll.gdi32.GetDeviceCaps(hdc, 88)   # LOGPIXELSX
                    user32.ReleaseDC(0, hdc)
                    
                    # 计算缩放比例（基于96 DPI为100%）
                    if logical_dpi_x > 0:
                        scale_percent = int((logical_dpi_x / 96.0) * 100)
                        
                        # 四舍五入到最接近的标准值
                        standard_scales = [100, 125, 150, 175, 200, 225, 250]
                        
                        # 计算与每个标准值的差值
                        differences = [abs(scale_percent - standard) for standard in standard_scales]
                        
                        # 找到最小差值对应的索引
                        closest_index = differences.index(min(differences))
                        
                        # 获取最接近的标准缩放值
                        scale = standard_scales[closest_index]
                    else:
                        scale = 100
                else:
                    scale = 100
            except Exception as inner_e:
                self.debug_logger.log_debug(f"获取DPI失败: {inner_e}")
                scale = 100
            
            return f"{scale}%"
        except Exception as e:
            self.debug_logger.log_error(f"获取系统缩放比例失败: {e}")
            return "100%"




    def on_calculate_total_time(self):
        """计算并显示总时间"""
        try:
            if self.event_manager.events_table.rowCount() == 0:
                self.settings_panel.update_total_time_display(0)
                return
                
            # 获取最后一个事件的绝对时间
            last_row = self.event_manager.events_table.rowCount() - 1
            last_abs_time_item = self.event_manager.events_table.item(last_row, 7)
            if not last_abs_time_item:
                self.settings_panel.update_total_time_display(0)
                return
                
            single_loop_time_ms = int(last_abs_time_item.text()) if last_abs_time_item.text().isdigit() else 0
            
            # 获取循环次数
            loop_count = self.settings_panel.get_safe_loop_count()
            
            # 获取间隔时间
            interval = self.settings_panel.interval_input.value()
            time_unit = self.settings_panel.time_unit_combo.currentText()
            
            # 转换间隔时间为毫秒
            if time_unit == "s":
                interval_ms = interval * 1000
            elif time_unit == "min":
                interval_ms = interval * 60000
            else:  # ms
                interval_ms = interval
            
            # 计算总时间：单次循环时间 * 循环次数 + 间隔时间 * (循环次数 - 1)
            total_time_ms = single_loop_time_ms * loop_count + interval_ms * (loop_count - 1)
            
            # 更新设置面板的总时间显示
            self.settings_panel.update_total_time_display(total_time_ms)
            
            self.debug_logger.log_info(f"已计算总时间: {total_time_ms}ms (单次循环: {single_loop_time_ms}ms, 循环次数: {loop_count}, 间隔: {interval}{time_unit})")
        except Exception as e:
            error_msg = f"计算总时间失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            # 显示错误信息但不崩溃
            self.settings_panel.update_total_time_display(0)




    def save_state_to_undo_stack(self):
        """保存当前状态到撤销栈"""
        if self._batch_operation:
            # 如果是批量操作，暂时不保存状态
            return
            
        # 添加到撤销栈
        state = {
            'events': []
        }
        
        # 收集事件数据
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            state['events'].append(event_data)
        
        # 限制撤销栈大小
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # 清空重做栈
        self.redo_stack.clear()
        
        self.debug_logger.log_info(f"状态已保存到撤销栈，当前撤销栈大小: {len(self.undo_stack)}")




    def _delayed_save_state(self):
        """延迟保存状态到撤销栈"""
        if self._pending_undo_save:
            self.save_state_to_undo_stack()
            self._pending_undo_save = False




    def mark_state_dirty(self):
        """标记状态已更改，延迟保存到撤销栈"""
        if self._batch_operation:
            return
            
        # 延迟保存状态，避免频繁保存
        self._pending_undo_save = True
        self._undo_save_timer.start(500)  # 500ms后保存




    def on_undo(self):
        """撤销操作"""
        if not self.undo_stack:
            self.status_bar.showMessage("⚠️ 没有可撤销的操作")
            return
            
        # 保存当前状态到重做栈
        current_state = {
            'events': []
        }
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            current_state['events'].append(event_data)
        self.redo_stack.append(current_state)
        
        # 恢复上一个状态
        previous_state = self.undo_stack.pop()
        self._restore_state(previous_state)
        
        # 保存状态到文件
        self.save_saved_state()
        
        self.status_bar.showMessage("✅ 已撤销操作")
        self.debug_logger.log_info("已撤销操作")




    def on_redo(self):
        """重做操作"""
        if not self.redo_stack:
            self.status_bar.showMessage("⚠️ 没有可重做的操作")
            return
            
        # 保存当前状态到撤销栈
        current_state = {
            'events': []
        }
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            current_state['events'].append(event_data)
        self.undo_stack.append(current_state)
        
        # 恢复下一个状态
        next_state = self.redo_stack.pop()
        self._restore_state(next_state)
        
        # 保存状态到文件
        self.save_saved_state()
        
        self.status_bar.showMessage("✅ 已重做操作")
        self.debug_logger.log_info("已重做操作")




    def _restore_state(self, state):
        """恢复状态"""
        # 清空当前事件
        self.event_manager.events_table.setRowCount(0)
        
        # 开始批量操作
        self._batch_operation = True
        
        try:
            # 恢复事件
            for i, event_data in enumerate(state['events']):
                # 创建行数据，包括行号
                row_data = [str(i + 1)] + event_data
                self.event_manager.add_table_row(row_data)
            
            # 更新统计信息
            self.event_manager.update_stats()
            
            # 立即更新预计总时间
            self.on_calculate_total_time()
        finally:
            # 结束批量操作
            self._batch_operation = False




    def on_new_file(self):
        """新建文件"""
        # 询问用户是否确认新建
        reply = ChineseMessageBox.show_question(self, "新建文件", "确定要新建一个空的事件列表吗？当前未保存的更改将丢失。")
        if not reply:
            return
            
        # 清空当前事件
        self.event_manager.events_table.setRowCount(0)
        
        # 保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 保存状态到文件
        self.save_saved_state()
        
        # 立即更新预计总时间
        self.on_calculate_total_time()
        
        self.status_bar.showMessage("✅ 已新建文件")
        self.debug_logger.log_info("已新建文件")




    def on_open_file(self):
        """打开文件"""
        # 询问用户是否确认打开
        reply = ChineseMessageBox.show_question(self, "打开文件", "确定要打开文件吗？当前未保存的更改将丢失。")
        if not reply:
            return
            
        # 打开文件对话框
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "打开文件", 
            "", 
            "BetterGI StellTrack 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            # 清空当前事件
            self.event_manager.events_table.setRowCount(0)
            
            # 保存当前状态到撤销栈
            self.save_state_to_undo_stack()
            
            # 开始批量操作
            self._batch_operation = True
            
            try:
                # 恢复事件
                for i, event_data in enumerate(state['events']):
                    # 创建行数据，包括行号
                    row_data = [str(i + 1)] + event_data
                    self.event_manager.add_table_row(row_data)
                
                # 更新统计信息
                self.event_manager.update_stats()
                
                # 立即更新预计总时间
                self.on_calculate_total_time()
                
                self.status_bar.showMessage(f"✅ 已打开文件: {os.path.basename(file_path)}")
                self.debug_logger.log_info(f"已打开文件: {file_path}")
            finally:
                # 结束批量操作
                self._batch_operation = False
                # 保存状态到文件
                self.save_saved_state()
        except json.JSONDecodeError:
            error_msg = f"无法解析文件: {file_path}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", f"无法解析文件: {file_path}")
        except Exception as e:
            error_msg = f"打开文件失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)




    def on_save_file(self):
        """保存文件"""
        # 打开文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "保存文件", 
            "", 
            "BetterGI StellTrack 文件 (*.json);;所有文件 (*.*)"
        )
        
        if not file_path:
            return
            
        try:
            # 构建状态数据
            state = {
                'events': [],
                'settings': {
                    'loop_count': self.settings_panel.loop_count_input.value(),
                    'interval': self.settings_panel.interval_input.value(),
                    'time_unit': self.settings_panel.time_unit_combo.currentText(),
                    'width': self.settings_panel.width_input.text(),
                    'height': self.settings_panel.height_input.text(),
                    'scale': self.settings_panel.scale_combo.currentText()
                }
            }
            
            # 收集事件数据
            for row in range(self.event_manager.events_table.rowCount()):
                event_data = []
                for col in range(1, 8):  # 跳过行号列
                    item = self.event_manager.events_table.item(row, col)
                    event_data.append(item.text() if item else "")
                state['events'].append(event_data)
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
            
            self.status_bar.showMessage(f"✅ 已保存文件: {os.path.basename(file_path)}")
            self.debug_logger.log_info(f"已保存文件: {file_path}")
            # 保存状态到文件
            self.save_saved_state()
        except Exception as e:
            error_msg = f"保存文件失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)




    def load_saved_state(self):
        """加载保存的状态"""
        try:
            # 获取程序所在目录
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 设置文件路径
            state_file = os.path.join(app_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试从 {state_file} 加载保存的状态")
            
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    # 验证状态数据的完整性
                    if isinstance(state, dict) and 'events' in state and isinstance(state['events'], list):
                        # 恢复事件
                        event_count = len(state['events'])
                        self.debug_logger.log_info(f"开始恢复 {event_count} 个事件")
                        
                        for i, event_data in enumerate(state['events']):
                            # 创建行数据，包括行号
                            row_data = [str(i + 1)] + event_data
                            self.event_manager.add_table_row(row_data)
                        
                        # 加载设置
                        if 'settings' in state:
                            self.settings_panel.restore_settings(state['settings'])
                            self.debug_logger.log_info(f"已成功加载保存的设置")
                        
                        self.debug_logger.log_info(f"已成功加载保存的状态，包含 {event_count} 个事件")
                        return True
                    else:
                        self.debug_logger.log_error(f"状态文件格式不正确，缺少必要的events字段或格式错误")
                        return False
                except json.JSONDecodeError as e:
                    self.debug_logger.log_error(f"解析状态文件失败: {e}")
                    return False
                except Exception as e:
                    self.debug_logger.log_error(f"恢复事件数据失败: {e}", exc_info=True)
                    return False
            else:
                self.debug_logger.log_info(f"没有找到保存的状态文件: {state_file}")
                return False
        except Exception as e:
            self.debug_logger.log_error(f"加载保存的状态失败: {e}", exc_info=True)
            return False




    def save_saved_state(self):
        """保存当前状态到文件"""
        try:
            # 获取程序所在目录
            if getattr(sys, 'frozen', False):
                app_dir = os.path.dirname(sys.executable)
            else:
                app_dir = os.path.dirname(os.path.abspath(__file__))
            
            # 设置文件路径
            state_file = os.path.join(app_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试将状态保存到 {state_file}")
            
            # 构建状态数据
            state = {
                'events': [],
                'settings': {
                    'loop_count': self.settings_panel.loop_count_input.value(),
                    'interval': self.settings_panel.interval_input.value(),
                    'time_unit': self.settings_panel.time_unit_combo.currentText(),
                    'width': self.settings_panel.width_input.text(),
                    'height': self.settings_panel.height_input.text(),
                    'scale': self.settings_panel.scale_combo.currentText()
                }
            }
            
            # 收集事件数据
            table_row_count = self.event_manager.events_table.rowCount()
            self.debug_logger.log_info(f"开始收集 {table_row_count} 个事件的数据")
            
            for row in range(table_row_count):
                event_data = []
                for col in range(1, 8):  # 跳过行号列
                    item = self.event_manager.events_table.item(row, col)
                    event_data.append(item.text() if item else "")
                state['events'].append(event_data)
            
            # 验证收集的数据
            collected_event_count = len(state['events'])
            if collected_event_count != table_row_count:
                self.debug_logger.log_error(f"收集事件数据时出现不一致: 表格中有 {table_row_count} 行，但只收集到 {collected_event_count} 个事件")
                return False
            
            # 确保目录存在
            state_dir = os.path.dirname(state_file)
            if not os.path.exists(state_dir):
                os.makedirs(state_dir)
                self.debug_logger.log_info(f"已创建状态文件目录: {state_dir}")
            
            # 保存到文件
            try:
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
                
                self.debug_logger.log_info(f"状态已成功保存到文件: {state_file}，包含 {collected_event_count} 个事件")
                return True
            except IOError as e:
                self.debug_logger.log_error(f"写入状态文件失败: {e}")
                return False
            except json.JSONDecodeError as e:
                self.debug_logger.log_error(f"序列化状态数据失败: {e}")
                return False
        except Exception as e:
            self.debug_logger.log_error(f"保存状态到文件失败: {e}", exc_info=True)
            return False




    def on_add_event(self):
        """添加事件 - 调用事件管理器"""
        self.event_manager.on_add_event()




    def on_edit_event(self):
        """编辑事件 - 调用事件管理器"""
        self.event_manager.on_edit_event()




    def on_delete_event(self):
        """删除事件 - 调用事件管理器"""
        self.event_manager.on_delete_event()




    def on_copy_event(self):
        """复制事件 - 调用事件管理器"""
        self.event_manager.on_copy_event()




    def on_cut_event(self):
        """剪切事件 - 调用事件管理器"""
        self.event_manager.on_cut_event()




    def on_paste_event(self):
        """粘贴事件 - 调用事件管理器"""
        self.event_manager.on_paste_event()




    def on_select_all_events(self):
        """全选事件 - 调用事件管理器"""
        self.event_manager.on_select_all_events()




    def on_open_debug_tool(self):
        """打开调试工具"""
        try:
            dialog = CustomInputDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.result == "password":
                    # 密码正确，打开调试窗口
                    debug_window = DebugWindow(self)
                    debug_window.show()
                    self.debug_logger.log_info("调试工具已打开")
                elif dialog.result == "easter_egg":
                    # 彩蛋触发，已经在对话框中处理
                    pass
        except Exception as e:
            error_msg = f"打开调试工具失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)




    def on_about(self):
        """打开关于窗口"""
        try:
            about_window = AboutWindowQt(self)
            about_window.show()
        except Exception as e:
            error_msg = f"打开关于窗口失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)




    def on_user_agreement(self):
        """用户协议"""
        self.debug_logger.log_info("打开用户协议窗口")
        
        from about_window import UserAgreementWindow
        
        agreement_window = UserAgreementWindow(self)
        
        agreement_window.show()




    def on_search_filter_changed(self):
        """搜索过滤条件改变时调用"""
        self.event_manager.on_search_filter_changed()




    def on_reset_search_filter(self):
        """重置搜索过滤条件"""
        self.event_manager.on_reset_search_filter()




    def on_batch_edit(self):
        """批量编辑事件"""
        self.event_manager.on_batch_edit()

    def closeEvent(self, event):
        """关闭事件 - 确保状态保存"""
        self.debug_logger.log_info("主窗口关闭中...")
        # 保存当前状态到文件
        self.save_saved_state()
        self.debug_logger.log_info("程序正常关闭")
        event.accept()



# =============================================================================
# 主程序入口
# =============================================================================




if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())