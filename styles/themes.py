# 标准库模块导入
import weakref

# 第三方模块导入
from PyQt6.QtCore import Qt, QTimer, QSettings
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

# 项目模块导入
from .fonts import get_global_font_manager
from utils import get_system_theme_mode


LIGHT_COLORS = {
    'bg': "#ffffff",
    'card_bg': "#ffffff",
    'primary': "#66ccff",
    'primary_hover': "#66ccff",
    'primary_pressed': "#3399ff",
    'secondary': "#ffffff",
    'secondary_hover': "#f5f5f5",
    'secondary_pressed': "#e5e5e5",
    'text': "#323130",
    'text_secondary': "#666666",
    'success': "#107c10",
    'error': "#d13438",
    'warning': "#ff8c00",
    'border': "#d0d0d0",
    'border_light': "#e0e0e0",
    'grid': "#e8e8e8"
}

DARK_COLORS = {
    'bg': "#000000",
    'card_bg': "#000000",
    'primary': "#66ccff",
    'primary_hover': "#66ccff",
    'primary_pressed': "#3399ff",
    'secondary': "#1A1A1A",
    'secondary_hover': "#2A2A2A",
    'secondary_pressed': "#3A3A3A",
    'text': "#E0E0E0",
    'text_secondary': "#B3B3B3",
    'success': "#4caf50",
    'error': "#ef5350",
    'warning': "#ffb74d",
    'border': "#2A2A2A",
    'border_light': "#3A3A3A",
    'grid': "#1A1A1A"
}

COLORS = dict(LIGHT_COLORS)

SHADOWS = {
    'small': '',
    'medium': '',
    'large': ''
}


class UnifiedStyleHelper:
    """统一样式助手类，使用单例模式管理所有控件样式

    提供统一的样式管理功能，支持浅色和深色主题切换。
    所有控件样式都通过此类获取，确保样式的一致性和主题切换的便捷性。

    主要功能：
    - 单例模式，全局唯一实例
    - 主题管理（浅色/深色/系统主题）
    - 提供各种控件的样式方法
    - 标题栏主题回调管理
    - 样式表缓存机制

    Attributes:
        COLORS (dict): 当前主题的颜色字典
        SHADOWS (dict): 阴影样式字典
        theme_mode (str): 当前主题模式（"light"、"dark"或"system"）
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        """获取单例实例

        Returns:
            UnifiedStyleHelper: 样式助手类的单例实例
        """
        if not cls._instance:
            cls._instance = UnifiedStyleHelper()
        return cls._instance

    def __init__(self):
        """初始化样式助手

        初始化颜色、阴影、主题模式等属性。
        """
        self.COLORS = COLORS
        self.SHADOWS = SHADOWS
        self.theme_mode = "light"
        self._title_bar_theme_windows = []
        self._light_stylesheet = None
        self._dark_stylesheet = None
        self._style_cache = {}
        self._current_theme_cache_key = None

    def _get_style_from_cache(self, style_key, generate_func):
        """从缓存获取样式，如果缓存失效则重新生成

        Args:
            style_key (str): 样式缓存键
            generate_func (callable): 样式生成函数

        Returns:
            str: 样式表字符串
        """
        cache_key = f"{self.theme_mode}_{style_key}"

        if self._current_theme_cache_key != self.theme_mode:
            self._style_cache.clear()
            self._current_theme_cache_key = self.theme_mode

        if cache_key not in self._style_cache:
            self._style_cache[cache_key] = generate_func()

        return self._style_cache[cache_key]

    def _generate_button_style(self, accent=False, disabled=False):
        """生成按钮样式

        Args:
            accent (bool): 是否使用强调色（主色调），默认为False
            disabled (bool): 是否为禁用状态，默认为False

        Returns:
            str: 按钮的样式表字符串
        """
        if disabled:
            return f"""
                QPushButton {{
                    background-color: #f5f5f5;
                    color: #999999;
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 11px;
                    min-height: 18px;
                    max-height: 18px;
                    {self.SHADOWS['small']}
                }}
            """

        if accent:
            return f"""
                QPushButton {{
                    background-color: {self.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                    min-height: 18px;
                    max-height: 18px;
                    {self.SHADOWS['small']}
                }}
                QPushButton:hover {{
                    background-color: {self.COLORS['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.COLORS['primary_pressed']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {self.COLORS['secondary']};
                    color: {self.COLORS['text']};
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 11px;
                    min-height: 18px;
                    max-height: 18px;
                    {self.SHADOWS['small']}
                }}
                QPushButton:hover {{
                    background-color: {self.COLORS['secondary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.COLORS['secondary_pressed']};
                }}
            """

    def _generate_line_edit_style(self):
        """生成输入框样式

        Returns:
            str: 输入框的样式表字符串
        """
        return f"""
            QLineEdit {{ 
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px 8px;
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                {self.SHADOWS['small']}
                min-height: 18px;
                max-height: 18px;
            }}
            QLineEdit:focus {{ 
                border-color: {self.COLORS['primary']};
            }}
            QLineEdit:hover {{ 
                border-color: #a0a0a0;
            }}
        """

    def _generate_combo_box_style(self):
        """生成下拉框样式

        Returns:
            str: 下拉框的样式表字符串
        """
        return f"""
            QComboBox {{ 
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px 8px;
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                font-size: 11px;
                min-width: 80px;
                {self.SHADOWS['small']}
                min-height: 18px;
                max-height: 18px;
            }}
            QComboBox::drop-down {{ 
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{ 
                width: 12px;
                height: 12px;
                border: none;
            }}
            QComboBox QAbstractItemView {{ 
                border: 1px solid {self.COLORS['border']}; 
                border-radius: 8px; 
                background-color: {self.COLORS['card_bg']}; 
                selection-background-color: {self.COLORS['primary']}; 
                selection-color: white; 
                font-size: 11px; 
                padding: 0px;
                {self.SHADOWS['small']} 
            }}
            QComboBox:hover {{ 
                border-color: #a0a0a0;
            }}
            QComboBox:focus {{ 
                border-color: {self.COLORS['primary']};
            }}
        """

    def _generate_table_style(self):
        """生成表格样式

        Returns:
            str: 表格的样式表字符串
        """
        return f"""
            QTableWidget {{ 
                border: none;
                border-radius: 8px;
                background-color: {self.COLORS['card_bg']};
                gridline-color: {self.COLORS['grid']};
                font-size: 11px;
                outline: none;
                {self.SHADOWS['medium']}
            }}
            QTableWidget::item {{ 
                padding: 6px 8px;
                border: none;
                text-align: center;
            }}
            QTableWidget::item:selected {{ 
                background-color: {self.COLORS['primary']};
                color: white;
            }}
            QTableWidget::item:hover {{ 
                background-color: #CAE9FF;
            }}
            QHeaderView::section {{ 
                background-color: {self.COLORS['card_bg']};
                padding: 4px 10px;
                border: none;
                border-right: 1px solid {self.COLORS['border_light']};
                border-bottom: 1px solid {self.COLORS['border_light']};
                font-weight: bold;
                font-size: 12px;
                color: {self.COLORS['text']};
                text-align: center;
                min-height: 20px;
            }}
            QHeaderView::section:last {{ 
                border-right: none;
            }}
            QTableCornerButton::section {{ 
                background-color: {self.COLORS['card_bg']};
                border: none;
                border-right: 1px solid {self.COLORS['border_light']};
                border-bottom: 1px solid {self.COLORS['border_light']};
            }}
        """

    def _generate_group_box_style(self):
        """生成分组框样式 - 已去掉灰色底纹

        Returns:
            str: 分组框的样式表字符串
        """
        return f"""
            QGroupBox {{ 
                font-size: 12px;
                font-weight: bold;
                color: {self.COLORS['primary']};
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                {self.SHADOWS['medium']}
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px 0 8px;
            }}
        """

    def _generate_spin_box_style(self):
        """生成整数和浮点数输入框样式

        Returns:
            str: 整数和浮点数输入框的样式表字符串
        """
        return f"""
            QSpinBox, QDoubleSpinBox {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px 4px 6px 4px;
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                text-align: center;
                {self.SHADOWS['small']}
                min-height: 18px;
                max-height: 18px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {self.COLORS['primary']};
                border-width: 1.5px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: #a0a0a0;
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                height: 15px;
                border: none;
                border-top-right-radius: 7px;
                background-color: transparent;
                margin: 1px 1px 0px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                height: 15px;
                border: none;
                border-bottom-right-radius: 7px;
                background-color: transparent;
                margin: 0px 1px 1px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
        """

    def _generate_time_offset_spin_box_style(self):
        """生成时间偏移输入框样式

        Returns:
            str: 时间偏移输入框的样式表字符串
        """
        return f"""
            QSpinBox {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px 8px;
                background-color: {self.COLORS['card_bg']};
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                text-align: center;
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
            }}
            QSpinBox:focus {{
                border-color: {self.COLORS['primary']};
                background-color: {self.COLORS['secondary_hover']};
                border-width: 1.5px;
            }}
            QSpinBox:hover {{
                border-color: #a0a0a0;
                background-color: {self.COLORS['secondary_hover']};
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                height: 15px;
                border: none;
                border-top-right-radius: 7px;
                background-color: transparent;
                margin: 1px 1px 0px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::up-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::up-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                height: 15px;
                border: none;
                border-bottom-right-radius: 7px;
                background-color: transparent;
                margin: 0px 1px 1px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::down-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::down-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
        """

    def _generate_explanation_text_edit_style(self):
        """生成说明文本编辑器样式

        Returns:
            str: 说明文本编辑器的样式表字符串
        """
        return f"""
            QTextEdit {{
                background-color: {self.COLORS['card_bg']};
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 6px;
                padding: 6px;
                font-size: 10px;
                {self.SHADOWS['small']}
            }}
        """

    def _generate_capture_status_style(self, status="inactive"):
        """生成捕获状态样式

        Args:
            status (str): 状态类型，可选值为 "active"、"inactive" 或 "bold"，默认为 "inactive"

        Returns:
            str: 捕获状态的样式表字符串
        """
        if status == "active":
            return f"color: {self.COLORS['primary']};"
        elif status == "inactive":
            return f"color: {self.COLORS['text_secondary']};"
        elif status == "bold":
            return f"color: {self.COLORS['primary']}; font-weight: bold;"
        return f"color: {self.COLORS['text_secondary']};"

    def _generate_checkbox_style(self):
        """生成复选框样式

        Returns:
            str: 复选框的样式表字符串
        """
        return f"""
            QCheckBox {{
                color: {self.COLORS['text']};
                spacing: 6px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """

    def register_title_bar_theme_callback(self, window):
        """注册标题栏主题更新回调

        将窗口添加到标题栏主题更新回调列表中，当主题切换时会自动通知该窗口。

        Args:
            window: 需要注册的窗口对象
        """
        window_ref = weakref.ref(window)
        if window_ref not in self._title_bar_theme_windows:
            self._title_bar_theme_windows.append(window_ref)

    def unregister_title_bar_theme_callback(self, window):
        """注销标题栏主题更新回调

        从标题栏主题更新回调列表中移除指定的窗口。

        Args:
            window: 需要注销的窗口对象
        """
        for window_ref in self._title_bar_theme_windows:
            if window_ref() is window:
                self._title_bar_theme_windows.remove(window_ref)
                break

    def _notify_title_bar_theme_changed(self):
        """通知所有注册的回调函数标题栏主题已变更（批量优化）

        使用 QTimer.singleShot 批量更新所有注册窗口的标题栏主题，
        避免频繁调用导致的性能问题。
        """
        def batch_update_title_bars():
            from utils import set_window_title_bar_theme
            helper = UnifiedStyleHelper.get_instance()

            is_dark = helper.theme_mode == "dark"
            if helper.theme_mode == "system":
                from utils import get_system_theme_mode
                is_dark = get_system_theme_mode() == "dark"

            valid_windows = []
            for window_ref in helper._title_bar_theme_windows:
                window = window_ref()
                if window is not None:
                    valid_windows.append(window_ref)

            helper._title_bar_theme_windows = valid_windows

            for window_ref in helper._title_bar_theme_windows:
                window = window_ref()
                if window is not None:
                    try:
                        set_window_title_bar_theme(window, is_dark)
                    except (OSError, ValueError) as e:
                        print(f"[DEBUG] 更新窗口标题栏失败: {e}")

        QTimer.singleShot(0, batch_update_title_bars)

    def get_button_style(self, accent=False, disabled=False):
        """获取按钮样式

        Args:
            accent (bool): 是否使用强调色（主色调），默认为False
            disabled (bool): 是否为禁用状态，默认为False

        Returns:
            str: 按钮的样式表字符串
        """
        style_key = f"button_accent_{accent}_disabled_{disabled}"
        return self._get_style_from_cache(style_key, lambda: self._generate_button_style(accent, disabled))

    def get_line_edit_style(self):
        """获取输入框样式

        Returns:
            str: 输入框的样式表字符串
        """
        return self._get_style_from_cache("line_edit", self._generate_line_edit_style)

    def get_combo_box_style(self):
        """获取下拉框样式

        Returns:
            str: 下拉框的样式表字符串
        """
        return self._get_style_from_cache("combo_box", self._generate_combo_box_style)

    def get_table_style(self):
        """获取表格样式

        Returns:
            str: 表格的样式表字符串
        """
        return self._get_style_from_cache("table", self._generate_table_style)

    def get_group_box_style(self):
        """获取分组框样式 - 已去掉灰色底纹

        Returns:
            str: 分组框的样式表字符串
        """
        return self._get_style_from_cache("group_box", self._generate_group_box_style)

    def get_header_widget_style(self):
        """获取标题栏样式"""
        return f"""
            HeaderWidget {{
                background-color: {self.COLORS['bg']};
                border-bottom: 1px solid {self.COLORS['border']};
            }}
        """

    def get_slogan_label_style(self):
        """获取标语标签样式"""
        return f"""
            QLabel {{
                font-size: 12px;
                color: {self.COLORS['text_secondary']};
                font-style: italic;
                margin-right: 15px;
                background-color: transparent;
            }}
        """

    def get_absolute_time_info_style(self):
        """获取绝对时间信息标签样式

        Returns:
            str: 绝对时间信息标签的样式表字符串
        """
        return f"color: {self.COLORS['text_secondary']}; font-size: 9px;"

    def get_logo_label_style(self):
        """获取Logo标签样式"""
        return "font-size: 28px; background-color: transparent;"

    def get_container_bg_style(self):
        """获取容器背景样式"""
        return f"background-color: {self.COLORS['card_bg']};"

    def get_quick_keys_label_style(self):
        """获取快速按键标签样式"""
        return "font-size: 10px;"

    def get_total_time_label_style(self):
        """获取总时间标签样式"""
        return f"""
            QLabel {{
                font-weight: bold; 
                color: {self.COLORS['primary']};
                font-size: 12px;
                background-color: transparent;
            }}
        """

    def get_script_text_style(self):
        """获取脚本文本样式"""
        return f"""
            QTextEdit {{ 
                font-family: SourceHanSerifCN;
                font-size: 12px;
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
                padding: 6px;
            }}
        """

    def get_log_display_style(self):
        """获取日志显示样式"""
        return f"""
            QTextEdit {{ 
                font-family: SourceHanSerifCN;
                font-size: 10px;
                background-color: {self.COLORS['bg']};
                color: {self.COLORS['text']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px;
            }}
        """

    def get_agreement_browser_style(self):
        """获取协议浏览器样式"""
        return f"""
            QTextBrowser {{ 
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 6px;
                font-size: 10px;
                line-height: 1.3;
            }}
            QTextBrowser a {{ 
                color: {self.COLORS['primary']};
                text-decoration: none;
            }}
            QTextBrowser a:hover {{ 
                color: {self.COLORS['primary_hover']};
                text-decoration: underline;
            }}
        """

    def get_info_edit_style(self):
        """获取信息编辑框样式"""
        return f"""
            QPlainTextEdit {{ 
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                line-height: 1.3;
            }}
        """

    def get_status_bar_style(self):
        """获取状态栏样式"""
        return f"""
            QStatusBar {{ 
                background-color: {self.COLORS['bg']};
                color: {self.COLORS['text']};
                border-top: 1px solid {self.COLORS['border']};
                font-size: 10px;
            }}
        """

    def get_text_browser_style(self):
        """获取文本浏览器样式"""
        return f"""
            QTextBrowser {{
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
                padding: 10px;
                font-size: 10px;
                line-height: 1.3;
                {self.SHADOWS['small']}
            }}
            QTextBrowser a {{
                color: {self.COLORS['primary']};
                text-decoration: none;
            }}
            QTextBrowser a:hover {{
                color: {self.COLORS['primary_hover']};
                text-decoration: underline;
            }}
        """

    def get_spin_box_style(self):
        """获取整数和浮点数输入框样式

        Returns:
            str: 整数和浮点数输入框的样式表字符串
        """
        return self._get_style_from_cache("spin_box", self._generate_spin_box_style)

    def get_progress_bar_style(self):
        """获取进度条样式"""
        return f"""
            QProgressBar {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                background-color: {self.COLORS['card_bg']};
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {self.COLORS['primary']};
                border-radius: 3px;
            }}
        """

    def get_text_edit_style(self):
        """获取文本编辑框样式"""
        return f"""
            QTextEdit {{
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: none;
                border-radius: 8px;
                padding: 8px;
                font-size: 10px;
                line-height: 1.3;
                {self.SHADOWS['small']}
            }}
        """

    def get_coordinate_capture_label_style(self):
        """获取坐标捕获标签样式"""
        return f"""
            QLabel {{
                border: 2px solid {self.COLORS['border']};
                background-color: {self.COLORS['card_bg']};
            }}
        """

    def get_centered_combo_box_style(self):
        """获取居中组合框样式"""
        return f"""
            QComboBox {{
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px 8px;
                font-size: 11px;
                text-align: center;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                background-color: {self.COLORS['card_bg']};
                selection-background-color: {self.COLORS['primary']};
                selection-color: white;
                font-size: 11px;
                padding: 0px;
                {self.SHADOWS['small']}
            }}
        """

    def get_splitter_style(self):
        """获取分割器样式"""
        return """
            QSplitter::handle {
                background-color: transparent;
                width: 6px;
                height: 6px;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background-color: transparent;
            }
        """

    def get_search_container_style(self):
        """获取搜索容器样式"""
        return """
            QWidget {
                background-color: %s;
                border: none;
                border-radius: 8px;
                %s
            }
        """ % (self.COLORS['card_bg'], self.SHADOWS['small'])

    def get_search_input_style(self):
        """获取搜索输入框样式"""
        return """
            QLineEdit {{ 
                border: 1px solid %s;
                border-radius: 8px;
                padding: 6px 8px;
                background-color: %s;
                color: %s;
                font-size: 11px;
                selection-background-color: %s;
                %s
                min-height: 30px;
                max-height: 30px;
            }}
            QLineEdit:focus {{ 
                border-color: %s;
            }}
            QLineEdit:hover {{ 
                border-color: #a0a0a0;
            }}
        """ % (self.COLORS['border'], self.COLORS['card_bg'], self.COLORS['text'], self.COLORS['primary'], self.SHADOWS['small'], self.COLORS['primary'])

    def get_filter_combo_style(self):
        """获取过滤组合框样式"""
        return """
            QComboBox {{ 
                border: 1px solid %s;
                border-radius: 8px;
                padding: 6px 8px;
                background-color: %s;
                color: %s;
                font-size: 11px;
                min-width: 80px;
                %s
                min-height: 30px;
                max-height: 30px;
            }}
            QComboBox::drop-down {{ 
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{ 
                width: 12px;
                height: 12px;
                border: none;
            }}
            QComboBox QAbstractItemView {{ 
                border: 1px solid %s; 
                border-radius: 8px; 
                background-color: %s; 
                selection-background-color: %s; 
                selection-color: white; 
                font-size: 11px; 
                padding: 0px;
                %s 
            }}
            QComboBox:hover {{ 
                border-color: #a0a0a0;
            }}
            QComboBox:focus {{ 
                border-color: %s;
            }}
        """ % (self.COLORS['border'], self.COLORS['card_bg'], self.COLORS['text'], self.SHADOWS['small'], self.COLORS['border'], self.COLORS['card_bg'], self.COLORS['primary'], self.SHADOWS['small'], self.COLORS['primary'])

    def get_scroll_bar_style(self):
        """获取滚动条样式 - Fluent Design风格"""
        return """
            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 10px 0;
            }
            
            QScrollBar::groove:vertical {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
                margin: 0 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: %s;
                border-radius: 5px;
                min-height: 20px;
                margin: 0 4px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: %s;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: %s;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
            
            QScrollBar:horizontal {
                background-color: transparent;
                height: 10px;
                margin: 0 10px;
            }
            
            QScrollBar::groove:horizontal {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
                margin: 4px 0;
            }
            
            QScrollBar::handle:horizontal {
                background-color: %s;
                border-radius: 5px;
                min-width: 20px;
                margin: 4px 0;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: %s;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: %s;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background-color: transparent;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            
            QAbstractScrollArea {
                background-color: transparent;
            }
        """ % (
            self.COLORS['border'],
            self.COLORS['primary_hover'],
            self.COLORS['primary_pressed'],
            self.COLORS['border'],
            self.COLORS['primary_hover'],
            self.COLORS['primary_pressed']
        )

    def get_centered_combobox_listview_style(self):
        """获取居中组合框列表视图样式"""
        return f"""
            QListView {{ 
                background-color: {self.COLORS['card_bg']}; 
                color: {self.COLORS['text']}; 
                font-family: "SourceHanSerifCN";
                font-size: 11px;
                outline: none;
                show-decoration-selected: 0;
            }}
            QListView::item {{ 
                padding: 4px 8px;
                text-align: center;
                border: none;
            }}
            QListView::item:selected {{ 
                background-color: {self.COLORS['primary']}; 
                color: white;
            }}
        """

    def get_absolute_time_edit_style(self):
        """获取绝对偏移时间显示框样式

        Returns:
            str: 绝对偏移时间显示框的样式表字符串
        """
        return f"""
            QLineEdit {{ 
                border: 1px solid {self.COLORS['border']}; 
                border-radius: 8px;
                padding: 6px 8px;
                background-color: {self.COLORS['bg']};
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                min-height: 18px;
                max-height: 18px;
                {self.SHADOWS['small']}
            }}
        """

    def set_smiley_font(self, widget, size=12, weight=QFont.Weight.Normal):
        """为组件设置得意黑字体

        Args:
            widget: 需要设置字体的组件
            size (int): 字体大小，默认为12
            weight: 字体粗细，默认为QFont.Weight.Normal
        """
        font_manager = get_global_font_manager()
        if font_manager.is_smiley_font_available():
            widget.setFont(font_manager.get_smiley_font(size, weight))
        else:
            widget.setFont(QFont("sans-serif", size, weight))

    def set_source_han_font(self, widget, size=12, weight=QFont.Weight.Normal):
        """为组件设置思源宋体字体

        Args:
            widget: 需要设置字体的组件
            size (int): 字体大小，默认为12
            weight: 字体粗细，默认为QFont.Weight.Normal
        """
        font_manager = get_global_font_manager()
        widget.setFont(font_manager.get_source_han_font(size, weight))

    def get_time_offset_spin_box_style(self):
        """获取时间偏移输入框样式

        Returns:
            str: 时间偏移输入框的样式表字符串
        """
        return self._get_style_from_cache("time_offset_spin_box", self._generate_time_offset_spin_box_style)

    def get_explanation_text_edit_style(self):
        """获取说明文本编辑器样式

        Returns:
            str: 说明文本编辑器的样式表字符串
        """
        return self._get_style_from_cache("explanation_text_edit", self._generate_explanation_text_edit_style)

    def get_absolute_time_info_style(self):
        """获取绝对时间信息标签样式

        Returns:
            str: 绝对时间信息标签的样式表字符串
        """
        return f"color: {self.COLORS['text_secondary']}; font-size: 9px;"

    def get_capture_status_style(self, status="inactive"):
        """获取捕获状态样式

        Args:
            status (str): 状态类型，可选值为 "active"、"inactive" 或 "bold"，默认为 "inactive"

        Returns:
            str: 捕获状态的样式表字符串
        """
        style_key = f"capture_status_{status}"
        return self._get_style_from_cache(style_key, lambda: self._generate_capture_status_style(status))

    def get_checkbox_style(self):
        """获取复选框样式

        Returns:
            str: 复选框的样式表字符串
        """
        return self._get_style_from_cache("checkbox", self._generate_checkbox_style)

    def get_theme_display_name(self, mode):
        """获取主题模式的显示名称

        Args:
            mode (str): 主题模式，可选值为 "light"、"dark" 或 "system"

        Returns:
            str: 主题模式的显示名称
        """
        theme_names = {
            "light": "浅色",
            "dark": "深色",
            "system": "跟随系统"
        }
        return theme_names.get(mode, mode)

    def setup_global_style(self, app=None, theme_mode=None, persist=False):
        """设置全局样式

        Args:
            app: 应用程序实例，默认为None
            theme_mode (str): 主题模式，可选值为 "light"、"dark" 或 "system"，默认为None
            persist (bool): 是否持久化保存主题设置，默认为False
        """
        settings = QSettings()
        if theme_mode is None:
            theme_mode = settings.value("ui/theme_mode", "system")
        if theme_mode not in ("light", "dark", "system"):
            theme_mode = "system"

        self.theme_mode = theme_mode

        effective_mode = theme_mode
        if theme_mode == "system":
            try:
                effective_mode = get_system_theme_mode()
            except (OSError, ValueError):
                effective_mode = "light"

        if effective_mode == "dark":
            selected_colors = DARK_COLORS
        else:
            selected_colors = LIGHT_COLORS

        global COLORS
        COLORS = dict(selected_colors)
        self.COLORS = COLORS

        if effective_mode == "dark" and self._dark_stylesheet:
            global_stylesheet = self._dark_stylesheet
        elif effective_mode == "light" and self._light_stylesheet:
            global_stylesheet = self._light_stylesheet
        else:
            scroll_bar_style = self.get_scroll_bar_style()
            
            global_stylesheet = f"""
                    QWidget {{
                        background-color: {self.COLORS['bg']};
                        color: {self.COLORS['text']};
                    }}
                    QGroupBox {{
                        background-color: {self.COLORS['bg']};
                    }}
                    QMenuBar {{
                        background-color: {self.COLORS['bg']};
                        color: {self.COLORS['text']};
                        border: none;
                        border-radius: 8px;
                        padding: 0px 4px 4px 4px;
                    }}
                    QMenuBar::item {{
                        padding: 4px 8px;
                        border-radius: 8px;
                    }}
                    QMenuBar::item:selected {{
                        background-color: {self.COLORS['primary_hover']};
                        color: white;
                    }}
                    QMenu {{ 
                        background-color: {self.COLORS['bg']};
                        color: {self.COLORS['text']};
                        border: 1px solid {self.COLORS['border']};
                        border-radius: 8px;
                        padding: 6px;
                        {self.SHADOWS['small']}
                    }}
                    QMenu::item {{
                        padding: 6px 16px;
                        border-radius: 8px;
                        margin: 2px 2px;
                    }}
                    QMenu::item:selected {{
                        background-color: {self.COLORS['primary_hover']};
                        color: white;
                    }}
                    QMenu::separator {{
                        height: 1px;
                        background-color: {self.COLORS['border_light']};
                        margin: 4px 8px;
                    }}
                    QAction::hover {{
                        background-color: {self.COLORS['primary_hover']};
                        color: white;
                    }}
                    
                    QCheckBox {{
                        color: {self.COLORS['text']};
                        spacing: 6px;
                    }}
                    
                    QCheckBox::indicator {{
                        width: 18px;
                        height: 18px;
                    }}
                    
                    {scroll_bar_style}
                """
            
            if effective_mode == "dark":
                self._dark_stylesheet = global_stylesheet
            else:
                self._light_stylesheet = global_stylesheet

        if persist:
            settings.setValue("ui/theme_mode", theme_mode)

        font_manager = get_global_font_manager()
        q_app = QApplication.instance()
        if q_app:
            q_app.setFont(font_manager.get_source_han_font(9))

        if q_app and hasattr(q_app, 'setStyleSheet'):
            q_app.setStyleSheet(global_stylesheet)
        elif app is not None and hasattr(app, 'setStyleSheet'):
            app.setStyleSheet(global_stylesheet)
        
        self._notify_title_bar_theme_changed()


class DarkStyleHelper(UnifiedStyleHelper):
    """深色主题样式助手，继承自UnifiedStyleHelper

    专门用于深色主题的样式管理，继承自 UnifiedStyleHelper。
    提供深色主题的默认样式配置。

    主要功能：
    - 继承 UnifiedStyleHelper 的所有功能
    - 默认使用深色主题颜色
    - 单例模式，全局唯一实例
    """
    _instance = None

    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = DarkStyleHelper()
        return cls._instance

    def __init__(self):
        super().__init__()
        self.COLORS = dict(DARK_COLORS)
