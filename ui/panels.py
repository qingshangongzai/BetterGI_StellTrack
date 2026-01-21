# 标准库模块导入
import ctypes
import json
import os
from datetime import datetime

# 第三方模块导入
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QComboBox, QDialog, QGroupBox, QGridLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QScrollArea, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
)

# 项目模块导入
from dialogs.debug_tools import get_global_debug_logger
from utils import convert_time_to_ms
from styles import (
    AnimatedDialog,
    ChineseMessageBox,
    DialogFactory,
    ModernComboBox,
    ModernDoubleSpinBox,
    ModernGroupBox,
    ModernLineEdit,
    ModernSpinBox,
    UnifiedStyleHelper
)


# =============================================================================
# 设置面板 - 循环设置和窗口设置
# =============================================================================

class SettingsPanel(QWidget):
    """应用程序设置面板

    管理应用程序的核心设置，包括：
    - 循环设置：控制脚本执行的循环次数和间隔时间
    - 屏幕设置：管理目标屏幕分辨率和缩放比例

    提供UI界面用于设置调整和显示，以及相关的辅助方法。

    Args:
        parent: 父窗口或部件实例
    """

    def __init__(self, parent=None):
        """初始化设置面板

        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()

    def setup_ui(self):
        """设置面板的UI布局和组件

        创建并布局面板的主要组件，包括：
        - 循环设置区域
        - 屏幕设置区域

        使用垂直布局组织所有设置组。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        self.groups = []

        self.create_loop_settings(layout)
        self.create_screen_settings(layout)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    def create_loop_settings(self, parent_layout):
        """创建循环设置组

        Args:
            parent_layout: 父布局对象
        """
        group = ModernGroupBox("🔄 循环设置")
        self.groups.append(group)
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setColumnMinimumWidth(0, 70)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        loop_count_label = QLabel("循环次数")
        loop_count_label.setFixedWidth(70)
        loop_count_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(loop_count_label, 0, 0)

        self.loop_count_input = ModernSpinBox()
        self.loop_count_input.setMinimum(1)
        self.loop_count_input.setMaximum(999999)
        self.loop_count_input.setValue(1)
        self.loop_count_input.setSingleStep(1)
        self.loop_count_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.loop_count_input, 0, 1)

        interval_label = QLabel("间隔时间")
        interval_label.setFixedWidth(70)
        interval_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(interval_label, 1, 0)

        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(8)

        self.interval_input = ModernDoubleSpinBox()
        self.interval_input.setMinimum(0)
        self.interval_input.setMaximum(999999)
        self.interval_input.setValue(3)
        self.interval_input.setDecimals(2)
        self.interval_input.update_step_based_on_unit("s")
        self.interval_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.time_unit_combo = ModernComboBox()
        self.time_unit_combo.addItems(["ms", "s", "min"])
        self.time_unit_combo.setCurrentText("s")
        self.time_unit_combo.setFixedWidth(60)
        self.time_unit_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        self.time_unit_combo.currentTextChanged.connect(
            lambda unit: self.interval_input.update_step_based_on_unit(unit)
        )

        time_layout.addWidget(self.interval_input)
        time_layout.addWidget(self.time_unit_combo)
        layout.addLayout(time_layout, 1, 1)

        total_time_label = QLabel("预计总时间")
        total_time_label.setFixedWidth(70)
        total_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(total_time_label, 2, 0)

        self.total_time_display = QLabel("0.0 s")
        self.total_time_display.setStyleSheet(UnifiedStyleHelper.get_instance().get_total_time_label_style())
        self.total_time_display.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.total_time_display, 2, 1)

        parent_layout.addWidget(group)

    def get_safe_loop_count(self):
        """安全获取循环次数，确保总是返回有效值

        Returns:
            int: 循环次数，最小值为1
        """
        return self.loop_count_input.value()

    def create_screen_settings(self, parent_layout):
        """创建窗口设置组

        Args:
            parent_layout: 父布局对象
        """
        group = ModernGroupBox("🖥️ 窗口设置")
        self.groups.append(group)
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setColumnMinimumWidth(0, 70)
        layout.setColumnStretch(0, 0)
        layout.setColumnStretch(1, 1)

        width_label = QLabel("窗口宽度")
        width_label.setFixedWidth(70)
        width_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(width_label, 0, 0)

        self.width_input = ModernLineEdit("1920")
        self.width_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.width_input, 0, 1)

        height_label = QLabel("窗口高度")
        height_label.setFixedWidth(70)
        height_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(height_label, 1, 0)

        self.height_input = ModernLineEdit("1080")
        self.height_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.height_input, 1, 1)

        scale_label = QLabel("缩放比例")
        scale_label.setFixedWidth(70)
        scale_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(scale_label, 2, 0)

        self.scale_combo = ModernComboBox()
        self.scale_combo.addItems(["100%", "125%", "150%", "175%", "200%", "225%", "250%"])
        self.scale_combo.setCurrentText("100%")
        self.scale_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        self.scale_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.scale_combo, 2, 1)

        self.detect_screen_btn = QPushButton("📏 获取屏幕分辨率和缩放")
        self.detect_screen_btn.setFixedHeight(32)
        self.detect_screen_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.detect_screen_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.detect_screen_btn, 3, 0, 1, 2)

        parent_layout.addWidget(group)

    def update_total_time_display(self, total_ms):
        """更新总时间显示

        Args:
            total_ms (int): 总时间（毫秒）
        """
        if total_ms < 1000:
            self.total_time_display.setText(f"{int(total_ms)} ms")
        elif total_ms < 60000:
            seconds = total_ms / 1000
            self.total_time_display.setText(f"{seconds:.1f} s")
        else:
            minutes = total_ms / 60000
            self.total_time_display.setText(f"{minutes:.1f} min")

    def update_screen_settings(self, width, height, scale):
        """更新屏幕设置

        Args:
            width (int): 窗口宽度
            height (int): 窗口高度
            scale (str): 缩放比例
        """
        self.width_input.setText(str(width))
        self.height_input.setText(str(height))
        self.scale_combo.setCurrentText(scale)

    def reset_settings(self):
        """重置设置"""
        self.loop_count_input.setValue(1)
        self.interval_input.setValue(3)
        self.time_unit_combo.setCurrentText("s")
        self.width_input.setText("1920")
        self.height_input.setText("1080")
        self.scale_combo.setCurrentText("100%")
        self.total_time_display.setText("0.0 s")

    def restore_settings(self, state):
        """从状态恢复设置

        Args:
            state (dict): 设置状态字典
        """
        try:
            loop_count = int(state.get('loop_count', '1'))
            self.loop_count_input.setValue(loop_count)
        except (ValueError, TypeError):
            self.loop_count_input.setValue(1)

        try:
            interval = float(state.get('interval', '3'))
            self.interval_input.setValue(interval)
        except (ValueError, TypeError):
            self.interval_input.setValue(3)

        self.time_unit_combo.setCurrentText(state.get('time_unit', 's'))
        self.width_input.setText(state.get('width', '1920'))
        self.height_input.setText(state.get('height', '1080'))
        self.scale_combo.setCurrentText(state.get('scale', '100%'))

    def on_detect_screen_info(self):
        """检测屏幕分辨率和缩放比例"""
        self.debug_logger.log_info("开始检测屏幕信息...")

        width, height = self.get_screen_resolution()
        scale = self.get_system_scale()

        self.update_screen_settings(width, height, scale)

        if self.parent_window and hasattr(self.parent_window, 'event_manager'):
            self.parent_window.event_manager.update_stats()

        if self.parent_window and hasattr(self.parent_window, 'status_bar'):
            self.parent_window.status_bar.showMessage(f"✅ 已获取屏幕信息: {width}×{height}, 缩放: {scale}")

        self.debug_logger.log_info(f"屏幕信息获取完成: {width}×{height}, 缩放: {scale}")

    def get_screen_resolution(self):
        """获取屏幕分辨率

        Returns:
            tuple: (宽度, 高度)
        """
        try:
            user32 = ctypes.windll.user32

            width = user32.GetSystemMetrics(0)
            height = user32.GetSystemMetrics(1)

            try:
                hdc = user32.GetDC(0)
                if hdc:
                    actual_width = ctypes.windll.gdi32.GetDeviceCaps(hdc, 118)
                    actual_height = ctypes.windll.gdi32.GetDeviceCaps(hdc, 117)

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
        """获取系统缩放比例

        Returns:
            str: 缩放比例，如"100%"
        """
        try:
            class MONITORINFOEX(ctypes.Structure):
                _fields_ = [
                    ("cbSize", ctypes.c_ulong),
                    ("rcMonitor", ctypes.c_long * 4),
                    ("rcWork", ctypes.c_long * 4),
                    ("dwFlags", ctypes.c_ulong),
                    ("szDevice", ctypes.c_wchar * 32)
                ]

            MDT_EFFECTIVE_DPI = 0

            user32 = ctypes.windll.user32
            gdi32 = ctypes.windll.gdi32
            shcore = ctypes.windll.shcore

            scale = 100

            try:
                try:
                    monitor = user32.MonitorFromWindow(0, 1)

                    if monitor:
                        dpi_x = ctypes.c_uint()
                        dpi_y = ctypes.c_uint()

                        result = shcore.GetDpiForMonitor(monitor, MDT_EFFECTIVE_DPI, ctypes.byref(dpi_x), ctypes.byref(dpi_y))

                        if result == 0:
                            logical_dpi_x = dpi_x.value
                        else:
                            logical_dpi_x = 96
                except Exception as inner_e:
                    self.debug_logger.log_debug(f"GetDpiForMonitor调用失败: {inner_e}")
                    logical_dpi_x = 96

                if logical_dpi_x == 96:
                    try:
                        hdc = user32.GetDC(0)
                        if hdc:
                            logical_dpi_x = gdi32.GetDeviceCaps(hdc, 88)
                            user32.ReleaseDC(0, hdc)
                    except Exception as inner_e:
                        self.debug_logger.log_debug(f"GetDeviceCaps获取DPI失败: {inner_e}")
                        logical_dpi_x = 96

                if logical_dpi_x > 0:
                    scale_percent = int((logical_dpi_x / 96.0) * 100)

                    standard_scales = [100, 125, 150, 175, 200, 225, 250]
                    differences = [abs(scale_percent - standard) for standard in standard_scales]
                    closest_index = differences.index(min(differences))
                    scale = standard_scales[closest_index]
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
            if not self.parent_window or not hasattr(self.parent_window, 'event_manager'):
                self.update_total_time_display(0)
                return

            events_table = self.parent_window.event_manager.events_table

            if events_table.rowCount() == 0:
                self.update_total_time_display(0)
                return

            last_row = events_table.rowCount() - 1
            last_abs_time_item = events_table.item(last_row, 7)
            if not last_abs_time_item:
                self.update_total_time_display(0)
                return

            single_loop_time_ms = int(last_abs_time_item.text()) if last_abs_time_item.text().isdigit() else 0

            loop_count = self.get_safe_loop_count()

            interval = self.interval_input.value()
            time_unit = self.time_unit_combo.currentText()
            interval_ms = convert_time_to_ms(interval, time_unit)

            total_time_ms = single_loop_time_ms * loop_count + interval_ms * (loop_count - 1)

            self.update_total_time_display(total_time_ms)

            self.debug_logger.log_info(f"已计算总时间: {total_time_ms}ms (单次循环: {single_loop_time_ms}ms, 循环次数: {loop_count}, 间隔: {interval}{time_unit})")
        except Exception as e:
            error_msg = f"计算总时间失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            self.update_total_time_display(0)

    def refresh_theme_styles(self):
        """根据当前主题重新应用设置面板样式"""
        helper = UnifiedStyleHelper.get_instance()

        self.setStyleSheet(f"background-color: {helper.COLORS['bg']};")

        for group in self.groups:
            group.setStyleSheet(helper.get_group_box_style())

        if hasattr(self, "loop_count_input"):
            self.loop_count_input.setStyleSheet(helper.get_spin_box_style())
        if hasattr(self, "interval_input"):
            self.interval_input.setStyleSheet(helper.get_spin_box_style())

        if hasattr(self, "time_unit_combo"):
            self.time_unit_combo.setStyleSheet(helper.get_centered_combo_box_style())
        if hasattr(self, "scale_combo"):
            self.scale_combo.setStyleSheet(helper.get_centered_combo_box_style())

        if hasattr(self, "width_input"):
            self.width_input.setStyleSheet(helper.get_line_edit_style())
        if hasattr(self, "height_input"):
            self.height_input.setStyleSheet(helper.get_line_edit_style())

        if hasattr(self, "detect_screen_btn"):
            self.detect_screen_btn.setStyleSheet(helper.get_button_style())

        if hasattr(self, "total_time_display"):
            self.total_time_display.setStyleSheet(helper.get_total_time_label_style())


# =============================================================================
# 操作面板 - 包含操作按钮和预览功能
# =============================================================================

class OperationsPanel(QWidget):
    """应用程序操作面板

    提供应用程序的核心操作按钮，包括：
    - 生成脚本：创建BetterGI可执行的脚本
    - 保存脚本：将生成的脚本保存到文件
    - 预览脚本：查看生成的脚本内容
    - 导入脚本：从文件导入现有脚本

    所有操作按钮都与父窗口的对应方法绑定。

    Args:
        parent: 父窗口或部件实例
    """

    def __init__(self, parent=None):
        """初始化操作面板

        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()

    def setup_ui(self):
        """设置操作面板的UI布局和组件

        创建并布局操作面板的主要组件，包括：
        - 生成脚本按钮
        - 保存脚本按钮
        - 预览脚本按钮
        - 导入脚本按钮

        使用垂直布局组织所有操作按钮，强调主要操作。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        self.groups = []

        group = ModernGroupBox("⚡ 操作")
        self.groups.append(group)
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(10, 15, 10, 10)

        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)

        self.generate_btn = QPushButton("🚀 生成脚本")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        self.generate_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.generate_btn.setMinimumWidth(150)

        self.save_btn = QPushButton("💾 保存脚本")
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.save_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.save_btn.setMinimumWidth(150)

        self.preview_btn = QPushButton("👁️ 预览脚本")
        self.preview_btn.setFixedHeight(35)
        self.preview_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.preview_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.preview_btn.setMinimumWidth(150)

        self.import_script_btn = QPushButton("📥 导入脚本")
        self.import_script_btn.setFixedHeight(35)
        self.import_script_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.import_script_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.import_script_btn.setMinimumWidth(150)

        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addWidget(self.import_script_btn)

        group_layout.addLayout(buttons_layout)
        layout.addWidget(group)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

    def refresh_theme_styles(self):
        """根据当前主题重新应用按钮样式"""
        helper = UnifiedStyleHelper.get_instance()

        self.setStyleSheet(f"background-color: {helper.COLORS['bg']};")

        for group in self.groups:
            group.setStyleSheet(helper.get_group_box_style())

        if hasattr(self, "generate_btn"):
            self.generate_btn.setStyleSheet(helper.get_button_style(accent=True))
        if hasattr(self, "save_btn"):
            self.save_btn.setStyleSheet(helper.get_button_style())
        if hasattr(self, "preview_btn"):
            self.preview_btn.setStyleSheet(helper.get_button_style())
        if hasattr(self, "import_script_btn"):
            self.import_script_btn.setStyleSheet(helper.get_button_style())

    def on_preview_script(self):
        """预览脚本 - 从主窗口转移过来的功能"""
        try:
            if not self.parent_window or not self.parent_window.script:
                self.debug_logger.log_warning("尝试预览但未生成脚本")
                ChineseMessageBox.show_warning(self, "警告", "请先生成脚本")
                return

            event_count = self.parent_window.event_manager.events_table.rowCount()
            loop_count = self.parent_window.settings_panel.get_safe_loop_count()
            total_events = event_count * loop_count

            if total_events > 10000:
                self.debug_logger.log_warning(f"事件总数过多({total_events}个事件)，无法进行预览")
                ChineseMessageBox.show_warning(self, "警告", "事件总数过多，无法进行预览")
                return

            preview_dialog = AnimatedDialog(self)
            preview_dialog.setWindowTitle("脚本预览")
            preview_dialog.resize(500, 700)

            layout = QVBoxLayout(preview_dialog)

            script_text = QTextEdit()
            script_text.setReadOnly(True)
            script_text.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
            script_text.setStyleSheet(UnifiedStyleHelper.get_instance().get_script_text_style())
            script_text.setPlainText(json.dumps(self.parent_window.script, ensure_ascii=False, indent=2))
            layout.addWidget(script_text)

            button_layout = DialogFactory.create_close_button(
                parent=preview_dialog,
                on_close=preview_dialog.close,
                text="关闭"
            )
            layout.addLayout(button_layout)

            self.debug_logger.log_info("打开脚本预览对话框")
            preview_dialog.exec()

        except Exception as e:
            error_msg = f"预览脚本失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def on_generate_script(self):
        """生成脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_generate_script()

    def on_save_script(self):
        """保存脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_save_script()

    def on_import_script(self):
        """导入脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_import_script()


# =============================================================================
# 统计信息面板 - 集成计算逻辑
# =============================================================================

class StatsPanel(QWidget):
    """应用程序统计信息面板

    显示脚本和事件的统计信息，包括：
    - 事件数量统计
    - 执行时间计算
    - 循环设置信息
    - 屏幕设置信息

    实时更新以反映当前的脚本配置和事件数据。

    Args:
        parent: 父窗口或部件实例
    """

    def __init__(self, parent=None):
        """初始化统计信息面板

        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()

    def setup_ui(self):
        """设置统计信息面板的UI布局和组件

        创建并布局统计信息面板的主要组件，包括：
        - 统计信息显示区域（带滚动条）

        使用垂直布局组织所有统计信息组件。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)

        self.groups = []

        group = ModernGroupBox("📊 统计信息")
        self.groups.append(group)
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(10, 15, 10, 10)

        self.stats_label = QLabel()
        self.stats_label.setWordWrap(True)
        self.stats_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.stats_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_explanation_text_edit_style())
        UnifiedStyleHelper.get_instance().set_source_han_font(self.stats_label, 8)
        self.stats_label.setText(f"脚本信息将在此显示...\n\n• 总事件数: 0\n• 按键事件: 0\n• 鼠标事件: 0  \n• 总执行时间: 0ms\n• 循环次数: 1\n• 循环间隔: 0ms\n\n窗口设置:\n• 分辨率: 1920x1080\n• 缩放比例: 100%")

        self.stats_scroll_area = QScrollArea()
        self.stats_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.stats_scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.stats_scroll_area.setWidgetResizable(True)
        self.stats_scroll_area.setWidget(self.stats_label)
        self.stats_scroll_area.setStyleSheet(f"QScrollArea {{ border: none; background-color: {UnifiedStyleHelper.get_instance().COLORS['bg']}; }}")

        group_layout.addWidget(self.stats_scroll_area)
        layout.addWidget(group)

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)

    def refresh_theme_styles(self):
        """根据当前主题重新应用统计信息面板样式"""
        helper = UnifiedStyleHelper.get_instance()

        self.setStyleSheet(f"background-color: {helper.COLORS['bg']};")

        for group in self.groups:
            group.setStyleSheet(helper.get_group_box_style())

        if hasattr(self, "stats_label"):
            self.stats_label.setStyleSheet(helper.get_explanation_text_edit_style())

        if hasattr(self, "stats_scroll_area"):
            self.stats_scroll_area.setStyleSheet(f"QScrollArea {{ border: none; background-color: {helper.COLORS['bg']}; }}")

    def update_stats(self):
        """更新统计信息"""
        try:
            if not self.parent_window:
                return

            event_manager = getattr(self.parent_window, 'event_manager', None)
            settings_panel = getattr(self.parent_window, 'settings_panel', None)

            if not event_manager or not settings_panel:
                self.debug_logger.log_warning("无法获取事件管理器或设置面板")
                return

            row_count = event_manager.events_table.rowCount()

            single_loop_time_ms = self.calculate_single_loop_time_ms(event_manager)

            loop_count = settings_panel.get_safe_loop_count()

            interval = settings_panel.interval_input.value()

            time_unit = settings_panel.time_unit_combo.currentText()
            interval_ms = convert_time_to_ms(interval, time_unit)

            total_time_ms = self.calculate_total_time_ms(single_loop_time_ms, loop_count, interval_ms)

            key_press_count, key_release_count, mouse_move_count, mouse_click_count = self.count_events(event_manager)

            width = settings_panel.width_input.text() or "1920"
            height = settings_panel.height_input.text() or "1080"
            scale = settings_panel.scale_combo.currentText()

            avg_interval = 0
            if row_count > 1:
                avg_interval = single_loop_time_ms / (row_count - 1)

            stats_text = self.generate_stats_text(
                row_count,
                key_press_count,
                key_release_count,
                mouse_move_count,
                mouse_click_count,
                single_loop_time_ms,
                total_time_ms,
                avg_interval,
                loop_count,
                interval,
                time_unit,
                width,
                height,
                scale
            )

            self.stats_label.setText(stats_text)

            if hasattr(self.parent_window, 'settings_panel'):
                self.parent_window.settings_panel.on_calculate_total_time()

        except Exception as e:
            error_msg = f"更新统计信息时出错: {e}"
            self.debug_logger.log_error(error_msg)
            self.stats_label.setText(f"统计信息更新失败: {error_msg}")

    def count_events(self, event_manager):
        """统计各类事件数量

        Args:
            event_manager: 事件管理器对象

        Returns:
            tuple: (按键按下数, 按键释放数, 鼠标移动数, 鼠标点击数)
        """
        key_press_count = 0
        key_release_count = 0
        mouse_move_count = 0
        mouse_click_count = 0

        for row in range(event_manager.events_table.rowCount()):
            type_item = event_manager.events_table.item(row, 2)
            if type_item:
                event_type = type_item.text()
                if event_type == "按键按下":
                    key_press_count += 1
                elif event_type == "按键释放":
                    key_release_count += 1
                elif event_type == "指针移动" or event_type == "平行移动":
                    mouse_move_count += 1
                elif event_type in ["左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放"]:
                    mouse_click_count += 1
                elif event_type == "鼠标滚轮":
                    mouse_move_count += 1

        return key_press_count, key_release_count, mouse_move_count, mouse_click_count

    def generate_stats_text(self, row_count, key_press_count, key_release_count, mouse_move_count,
                          mouse_click_count, single_loop_time_ms, total_time_ms, avg_interval,
                          loop_count, interval, time_unit, width, height, scale):
        """生成统计信息文本

        Args:
            row_count (int): 总事件数
            key_press_count (int): 按键按下数
            key_release_count (int): 按键释放数
            mouse_move_count (int): 鼠标移动数
            mouse_click_count (int): 鼠标点击数
            single_loop_time_ms (int): 单次循环时间（毫秒）
            total_time_ms (int): 总执行时间（毫秒）
            avg_interval (float): 平均事件间隔（毫秒）
            loop_count (int): 循环次数
            interval (float): 循环间隔
            time_unit (str): 时间单位
            width (str): 窗口宽度
            height (str): 窗口高度
            scale (str): 缩放比例

        Returns:
            str: 格式化的统计信息文本
        """
        return f"""═══════════
📊 脚本统计信息
═══════════

🔢 事件统计:
• 总事件数: {row_count}
  ├─ 按键按下: {key_press_count}
  ├─ 按键释放: {key_release_count}
  ├─ 鼠标移动: {mouse_move_count}
  └─ 鼠标点击: {mouse_click_count}

⏱️ 时间统计:
• 单次循环时间: {self.format_time_display(single_loop_time_ms)}
• 总执行时间: {self.format_time_display(total_time_ms)}
• 平均事件间隔: {self.format_time_display(avg_interval)}
• 循环次数: {loop_count}
• 循环间隔: {interval} {time_unit}

🖥️ 窗口设置:
• 分辨率: {width}×{height}
• 缩放比例: {scale}
• 像素总数: {int(width) * int(height):,}

💾 脚本信息:
• 预计文件大小: ~{row_count * 50} bytes
• 事件密度: {row_count / (single_loop_time_ms / 1000) if single_loop_time_ms > 0 else 0:.1f} 事件/秒
• 脚本复杂度: {'简单' if row_count < 10 else '中等' if row_count < 50 else '复杂'}

📝 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""

    def format_time_display(self, time_ms):
        """格式化时间显示

        Args:
            time_ms (float): 时间（毫秒）

        Returns:
            str: 格式化的时间字符串
        """
        if time_ms < 1000:
            return f"{time_ms:.0f} ms"
        elif time_ms < 60000:
            seconds = time_ms / 1000
            return f"{time_ms:.0f} ms ({seconds:.1f} s)"
        else:
            minutes = time_ms / 60000
            return f"{time_ms:.0f} ms ({minutes:.1f} min)"

    def calculate_single_loop_time_ms(self, event_manager):
        """计算单次循环的总时间（毫秒）

        Args:
            event_manager: 事件管理器对象

        Returns:
            int: 单次循环总时间（毫秒）
        """
        try:
            if event_manager.events_table.rowCount() == 0:
                return 0
            last_row = event_manager.events_table.rowCount() - 1
            time_item = event_manager.events_table.item(last_row, 7)
            if time_item and time_item.text().isdigit():
                return int(time_item.text())
            else:
                return 0
        except Exception as e:
            self.debug_logger.log_error(f"计算单次循环时间失败: {e}")
            return 0

    def calculate_total_time_ms(self, single_loop_time, loop_count, interval_ms):
        """计算整个脚本的总时间（毫秒）

        Args:
            single_loop_time (int): 单次循环时间（毫秒）
            loop_count (int): 循环次数
            interval_ms (int): 间隔时间（毫秒）

        Returns:
            int: 总时间（毫秒）
        """
        try:
            total_time = single_loop_time * loop_count + interval_ms * (loop_count - 1)
            return total_time
        except Exception as e:
            self.debug_logger.log_error(f"计算总时间失败: {e}")
            return 0

    def update_stats_display(self, stats_text):
        """更新统计信息显示 - 保持向后兼容

        Args:
            stats_text (str): 统计信息文本
        """
        self.stats_label.setText(stats_text)
