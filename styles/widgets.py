# 标准库模块导入
import os

# PyQt6模块导入
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QRectF, QPropertyAnimation
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPainter, QPainterPath, QPen, QRegion, QBitmap, QPalette, QColor
from PyQt6.QtWidgets import (QGroupBox, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
                           QListView, QPushButton, QWidget, QDialog, QMainWindow,
                           QMenu, QMenuBar, QLabel)

# 项目模块导入
from .themes import UnifiedStyleHelper, COLORS, SHADOWS
from .fonts import get_global_font_manager
from utils import fix_windows_taskbar_icon_for_window, load_icon_universal

# 第三方模块导入
from qframelesswindow import FramelessMainWindow, TitleBar, FramelessDialog


class StyledWidget(QWidget):
    """基础样式控件类，自动初始化字体管理器"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.font_manager = get_global_font_manager()


class BaseFramelessDialog(FramelessDialog):
    """无边框对话框基类（纯 PyQt6 版本）

    提供统一的自定义标题栏和主题适配功能。
    子类只需调用 _setup_title_bar() 和 _update_styles() 即可。

    使用示例:
        class MyDialog(BaseFramelessDialog):
            def __init__(self, parent=None):
                super().__init__(parent)
                self.setWindowTitle("我的对话框")
                self.setFixedSize(400, 300)

                # 设置界面
                self.setup_ui()

            def setup_ui(self):
                layout = QVBoxLayout(self)
                # 顶部边距40px为标题栏留出空间
                layout.setContentsMargins(20, 40, 20, 20)
                # ... 其他控件
    """

    def __init__(self, parent=None, title="", size=None, icon_path=None):
        """初始化无边框对话框基类

        Args:
            parent: 父窗口对象
            title: 窗口标题
            size: 窗口大小元组 (width, height)
            icon_path: Logo 图标路径，可选
        """
        super().__init__(parent)
        self._title_label = None
        self.font_manager = get_global_font_manager()

        if title:
            self.setWindowTitle(title)

        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width > 0 and height > 0:
                    self.setFixedSize(width, height)

        # 设置窗口图标
        try:
            icon = load_icon_universal()
            if icon:
                self.setWindowIcon(icon)
        except Exception:
            pass

        # 设置标题栏和样式
        self._setup_title_bar(icon_path)
        self._update_styles()

        # 注册标题栏主题回调
        QTimer.singleShot(0, self._register_title_bar_callback)

    def _register_title_bar_callback(self):
        """注册标题栏主题更新回调（延迟调用以避免循环导入）"""
        try:
            helper = UnifiedStyleHelper.get_instance()
            helper.register_title_bar_theme_callback(self)
        except Exception as e:
            print(f"[DEBUG] 注册标题栏主题回调失败: {e}")

    def _setup_title_bar(self, icon_path=None):
        """设置自定义 Fluent Design 风格标题栏

        Args:
            icon_path: Logo 图标路径，可选
        """
        title_bar = self.titleBar
        h_layout = title_bar.layout()
        if not h_layout:
            return

        # 获取主题颜色
        text_color = self._get_text_color()
        text_color_str = text_color.name()

        # 1. 左边距
        left_spacer = QLabel(title_bar)
        left_spacer.setFixedWidth(10)

        # 2. Logo（可选）
        logo_label = None
        pixmap = None

        # 尝试加载指定的 icon_path
        if icon_path:
            pixmap = QPixmap(icon_path)

        # 如果没有指定 icon_path 或加载失败，尝试加载默认 logo
        if not pixmap or pixmap.isNull():
            pixmap = QPixmap("logo/logo.png")

        # 如果成功加载 pixmap，创建 logo_label
        if pixmap and not pixmap.isNull():
            logo_label = QLabel(title_bar)
            logo_label.setPixmap(pixmap.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))

        # 3. Logo和标题之间的间距
        spacer_label = QLabel(title_bar)
        spacer_label.setFixedWidth(8)

        # 4. 标题
        title_label = QLabel(self.windowTitle(), title_bar)
        title_label.setFont(self.font_manager.get_source_han_font(11, QFont.Weight.Medium))
        title_label.setStyleSheet(
            f"color: {text_color_str}; font-size: 13px; font-weight: 500;"
        )

        # 按顺序插入到布局开头（倒序插入）
        for widget in [title_label, spacer_label, logo_label, left_spacer]:
            if widget:
                h_layout.insertWidget(0, widget)
                h_layout.setAlignment(widget, Qt.AlignmentFlag.AlignVCenter)

        # 保存标题标签引用，以便主题切换时更新
        self._title_label = title_label

    def _get_text_color(self):
        """获取当前主题文本颜色

        通过 UnifiedStyleHelper 获取当前主题模式，自动返回合适的文字颜色。

        Returns:
            QColor: 文本颜色
        """
        if self._is_dark_theme():
            return QColor(255, 255, 255)  # 深色主题使用白色文字
        else:
            return QColor(40, 40, 40)  # 浅色主题使用深色文字

    def _get_bg_color(self):
        """获取当前主题背景颜色

        Returns:
            QColor: 背景颜色
        """
        return QColor(32, 32, 32) if self._is_dark_theme() else QColor(255, 255, 255)

    def _is_dark_theme(self):
        """检测当前是否为深色主题

        Returns:
            bool: True 为深色主题，False 为浅色主题
        """
        helper = UnifiedStyleHelper.get_instance()
        if helper.theme_mode == "dark":
            return True
        elif helper.theme_mode == "light":
            return False
        else:
            # system 模式，通过调色板检测
            palette = self.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            brightness = (window_color.red() * 299 +
                         window_color.green() * 587 +
                         window_color.blue() * 114) / 1000
            return brightness < 128

    def _update_close_button_color(self, text_color):
        """更新关闭按钮颜色以适配主题

        Args:
            text_color: 文本颜色 (QColor)
        """
        title_bar = self.titleBar
        if hasattr(title_bar, 'closeBtn') and title_bar.closeBtn:
            close_btn = title_bar.closeBtn
            close_btn.setNormalColor(text_color)
            # 注意：部分版本的 PyQt6-Frameless-Window 可能不支持以下方法
            if hasattr(close_btn, 'setHoverColor'):
                close_btn.setHoverColor(QColor(255, 255, 255))
                close_btn.setHoverBackgroundColor(QColor(196, 43, 28))
                close_btn.setPressedColor(QColor(255, 255, 255))

    def _update_styles(self):
        """更新样式以适配主题"""
        text_color = self._get_text_color()
        text_color_str = text_color.name()
        bg_color = self._get_bg_color()

        # 使用 QPalette 设置窗口背景色（样式表对 FramelessDialog 不生效）
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 设置 QLabel 文字颜色样式表
        self.setStyleSheet(f"""
            QLabel {{
                color: {text_color_str};
                background-color: transparent;
            }}
        """)

        # 更新标题标签颜色（如果存在）
        if self._title_label:
            self._title_label.setStyleSheet(
                f"color: {text_color_str}; font-size: 13px; font-weight: 500;"
            )

        # 更新关闭按钮颜色
        self._update_close_button_color(text_color)

        # 更新标题栏背景色
        self._update_title_bar_style(bg_color, text_color)

    def _update_title_bar_style(self, bg_color, text_color):
        """更新标题栏样式

        Args:
            bg_color: 背景颜色 (QColor)
            text_color: 文本颜色 (QColor)
        """
        title_bar = self.titleBar
        if title_bar:
            # 设置标题栏背景色
            title_bar.setStyleSheet(f"""
                background-color: {bg_color.name()};
            """)
            # 更新标题栏上的所有 QLabel
            for child in title_bar.findChildren(QLabel):
                child.setStyleSheet(f"""
                    color: {text_color.name()};
                    background-color: transparent;
                """)

    def apply_title_bar_theme(self):
        """应用标题栏主题

        根据当前主题模式自动设置窗口标题栏的深色/浅色模式。
        此方法会从 UnifiedStyleHelper 获取当前主题，并调用 Windows API 设置标题栏。
        """
        try:
            from utils import set_window_title_bar_theme
            helper = UnifiedStyleHelper.get_instance()

            is_dark = helper.theme_mode == "dark"
            if helper.theme_mode == "system":
                from utils import get_system_theme_mode
                is_dark = get_system_theme_mode() == "dark"

            set_window_title_bar_theme(self, is_dark)
        except Exception as e:
            print(f"[DEBUG] 应用标题栏主题失败: {e}")

    def showEvent(self, event):
        """窗口显示时自动应用标题栏主题"""
        super().showEvent(event)
        QTimer.singleShot(50, self.apply_title_bar_theme)

    def refresh_theme_styles(self):
        """刷新控件的样式，应用当前主题"""
        self._update_styles()

        # 递归刷新所有子控件
        from PyQt6.QtWidgets import QWidget
        for child in self.findChildren(QWidget):
            if hasattr(child, 'refresh_theme_styles'):
                child.refresh_theme_styles()

    def closeEvent(self, event):
        """关闭事件：注销标题栏主题回调"""
        try:
            helper = UnifiedStyleHelper.get_instance()
            helper.unregister_title_bar_theme_callback(self)
        except Exception:
            pass
        super().closeEvent(event)



class TitleBarThemeMixin:
    """标题栏主题混入类，为窗口提供 Windows 10+ 标题栏深色/浅色模式支持"""

    def __init__(self, *args, **kwargs):
        """初始化混入类"""
        super().__init__(*args, **kwargs)
        self._title_bar_theme_applied = False
        self._callback_registered = False

        QTimer.singleShot(0, self._register_title_bar_callback)

    def _register_title_bar_callback(self):
        """注册标题栏主题更新回调（延迟调用以避免循环导入）"""
        try:
            from .themes import UnifiedStyleHelper
            helper = UnifiedStyleHelper.get_instance()
            helper.register_title_bar_theme_callback(self)
            self._callback_registered = True
        except Exception as e:
            print(f"[DEBUG] 注册标题栏主题回调失败: {e}")

    def __del__(self):
        """析构时注销回调"""
        try:
            if self._callback_registered:
                from .themes import UnifiedStyleHelper
                helper = UnifiedStyleHelper.get_instance()
                helper.unregister_title_bar_theme_callback(self)
        except Exception:
            pass

    def apply_title_bar_theme(self):
        """
        应用标题栏主题

        根据当前主题模式自动设置窗口标题栏的深色/浅色模式。
        此方法会从 UnifiedStyleHelper 获取当前主题，并调用 Windows API 设置标题栏。
        """
        try:
            from utils import set_window_title_bar_theme
            from .themes import UnifiedStyleHelper
            helper = UnifiedStyleHelper.get_instance()

            is_dark = helper.theme_mode == "dark"
            if helper.theme_mode == "system":
                from utils import get_system_theme_mode
                is_dark = get_system_theme_mode() == "dark"

            success = set_window_title_bar_theme(self, is_dark)
            self._title_bar_theme_applied = success

            return success

        except Exception as e:
            print(f"[DEBUG] 应用标题栏主题失败: {e}")
            return False

    def showEvent(self, event):
        """窗口显示时自动应用标题栏主题"""
        super().showEvent(event)

        if not self._title_bar_theme_applied:
            QTimer.singleShot(50, self.apply_title_bar_theme)


class StyledDialog(BaseFramelessDialog):
    """无边框对话框基类，继承自 BaseFramelessDialog

    提供无边框设计和自定义标题栏，自动初始化字体管理器和窗口基本设置。
    BaseFramelessDialog 已包含标题栏主题切换功能，无需 TitleBarThemeMixin。

    Args:
        parent: 父窗口组件
        title: 窗口标题，可选
        size: 窗口大小元组 (width, height)，可选
        icon_path: Logo 图标路径，可选
    """

    def __init__(self, parent=None, title="", size=None, icon_path=None):
        """初始化无边框对话框

        Args:
            parent: 父窗口组件
            title: 窗口标题，可选
            size: 窗口大小元组 (width, height)，可选
            icon_path: Logo 图标路径，可选
        """
        # BaseFramelessDialog 已处理 title、size、icon_path
        super().__init__(parent=parent, title=title, size=size, icon_path=icon_path)
        # font_manager 已在 BaseFramelessDialog 中初始化


class StyledMainWindow(TitleBarThemeMixin, QMainWindow):
    """基础样式主窗口类，自动初始化字体管理器和窗口基本设置"""

    def __init__(self, parent=None, title="", size=None, window_flags=None, icon=None):
        super().__init__(parent)
        self.font_manager = get_global_font_manager()

        if title:
            self.setWindowTitle(title)

        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width > 0 and height > 0:
                    self.setFixedSize(width, height)

        if window_flags:
            self.setWindowFlags(window_flags)

        if icon:
            self.setWindowIcon(icon)
        elif hasattr(self, 'load_icon'):
            try:
                icon = self.load_icon()
                if icon:
                    self.setWindowIcon(icon)
            except Exception:
                pass


class StyledFramelessMainWindow(TitleBarThemeMixin, FramelessMainWindow):
    """无边框主窗口基类，提供自定义标题栏和主题适配功能"""

    TITLE_BAR_HEIGHT = 32  # qframelesswindow 标题栏默认高度

    def __init__(self, parent=None, title="", size=None):
        super().__init__(parent)
        self.font_manager = get_global_font_manager()
        self._title_label = None

        if title:
            self.setWindowTitle(title)

        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width > 0 and height > 0:
                    self.setFixedSize(width, height)

        # 设置窗口图标
        icon_obj = load_icon_universal()
        if icon_obj:
            self.setWindowIcon(icon_obj)

        # 使用基础 TitleBar + 自定义布局（与 BaseFramelessDialog 一致）
        self.setTitleBar(TitleBar(self))
        self._setup_title_bar()
        # 手动调整标题栏大小（setTitleBar 后 resizeEvent 不会立即触发）
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.titleBar.raise_()

        # 设置标题栏样式
        self._update_styles()

    def _setup_title_bar(self):
        """设置自定义标题栏布局"""
        title_bar = self.titleBar
        title_bar.setObjectName("titleBar")

        h_layout = title_bar.layout()
        if not h_layout:
            return

        text_color = self._get_text_color()

        h_layout.insertSpacing(0, 10)

        logo_label = QLabel(title_bar)
        pixmap = QPixmap("logo/logo.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaled(
                20, 20,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        h_layout.insertWidget(1, logo_label)
        h_layout.setAlignment(logo_label, Qt.AlignmentFlag.AlignVCenter)

        h_layout.insertSpacing(2, 8)

        title_label = QLabel(self.windowTitle(), title_bar)
        title_label.setFont(self.font_manager.get_source_han_font(11, QFont.Weight.Medium))
        title_label.setStyleSheet(
            f"color: {text_color.name()}; font-size: 13px; font-weight: 500;"
        )
        h_layout.insertWidget(3, title_label)
        h_layout.setAlignment(title_label, Qt.AlignmentFlag.AlignVCenter)

        self._title_label = title_label

    def _is_dark_theme(self):
        """检测当前是否为深色主题"""
        helper = UnifiedStyleHelper.get_instance()
        if helper.theme_mode == "dark":
            return True
        elif helper.theme_mode == "light":
            return False
        else:
            palette = self.palette()
            window_color = palette.color(QPalette.ColorRole.Window)
            brightness = (window_color.red() * 299 +
                         window_color.green() * 587 +
                         window_color.blue() * 114) / 1000
            return brightness < 128

    def _get_text_color(self):
        """获取当前主题文本颜色"""
        return QColor(255, 255, 255) if self._is_dark_theme() else QColor(40, 40, 40)

    def _get_bg_color(self):
        """获取当前主题背景颜色"""
        return QColor(32, 32, 32) if self._is_dark_theme() else QColor(255, 255, 255)

    def _update_styles(self):
        """更新样式以适配主题"""
        text_color = self._get_text_color()
        bg_color = self._get_bg_color()

        # 使用 QPalette 设置窗口背景色（样式表对 FramelessWindow 不生效）
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, bg_color)
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # 更新标题栏样式
        self._update_title_bar_style(bg_color, text_color)

    def _update_title_bar_style(self, bg_color, text_color):
        """更新标题栏样式

        使用 #titleBar 选择器只设置标题栏本身的背景色，不影响子控件（按钮）。
        """
        # 只设置标题栏背景色，不影响按钮
        self.titleBar.setStyleSheet(f"#titleBar {{ background-color: {bg_color.name()}; }}")

        # 更新标题标签颜色（使用 !important 强制覆盖全局样式表）
        if self._title_label:
            self._title_label.setStyleSheet(
                f"color: {text_color.name()} !important; font-size: 13px; font-weight: 500;"
            )

        # 更新标题栏按钮颜色以适配主题
        self._update_title_bar_buttons_color(text_color)

    def _update_title_bar_buttons_color(self, text_color):
        """更新标题栏按钮颜色以适配主题"""
        title_bar = self.titleBar
        title_bar.minBtn.setNormalColor(text_color)
        title_bar.maxBtn.setNormalColor(text_color)
        title_bar.closeBtn.setNormalColor(text_color)
        title_bar.closeBtn.setHoverColor(QColor(255, 255, 255))
        title_bar.closeBtn.setHoverBackgroundColor(QColor(196, 43, 28))
        title_bar.closeBtn.setPressedColor(QColor(255, 255, 255))

    def setCentralWidget(self, widget):
        """设置中央部件，确保标题栏始终在最上层"""
        super().setCentralWidget(widget)
        self.titleBar.raise_()

    def refresh_theme_styles(self):
        """刷新控件的样式，应用当前主题"""
        self._update_styles()

        # 递归刷新所有子控件
        for child in self.findChildren(QWidget):
            if hasattr(child, 'refresh_theme_styles'):
                child.refresh_theme_styles()


class StyleManager:
    """样式管理器 - 管理应用程序的样式"""

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StyleManager()
        return cls._instance

    def __init__(self):
        """初始化样式管理器"""
        pass


class FadeInWindowMixin:
    """窗口淡入/淡出动画混入类，用于在打开和关闭时添加简单的过渡动画"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_show_animation_done = False
        self._closing_via_animation = False
        self.setWindowOpacity(0.0)

    def showEvent(self, event):
        """在窗口首次显示时播放淡入动画"""
        if not self._first_show_animation_done:
            self._first_show_animation_done = True
            try:
                self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
                self._fade_anim.setDuration(180)
                self._fade_anim.setStartValue(0.0)
                self._fade_anim.setEndValue(1.0)
                self._fade_anim.start()
            except Exception:
                self.setWindowOpacity(1.0)

        super().showEvent(event)

    def closeEvent(self, event):
        """在窗口关闭时播放淡出动画"""
        if self._closing_via_animation:
            return super().closeEvent(event)

        event.ignore()
        self._closing_via_animation = True
        try:
            start_opacity = self.windowOpacity()
            self._fade_out_anim = QPropertyAnimation(self, b"windowOpacity", self)
            self._fade_out_anim.setDuration(180)
            self._fade_out_anim.setStartValue(start_opacity)
            self._fade_out_anim.setEndValue(0.0)

            def _on_fade_out_finished():
                try:
                    super(type(self), self).close()
                finally:
                    self._closing_via_animation = False

            self._fade_out_anim.finished.connect(_on_fade_out_finished)
            self._fade_out_anim.start()
        except Exception:
            self._closing_via_animation = False
            super().closeEvent(event)


class WindowIconMixin:
    """窗口图标修复混入类，提供统一的任务栏图标修复功能"""

    icon_fixed = pyqtSignal(bool)

    def __init__(self, *args, **kwargs):
        """初始化混入类"""
        super().__init__(*args, **kwargs)
        self._icon_fixed = False
        self._fix_timer = None

    def setup_icon_fixing(self, delay_ms=100):
        """
        设置图标修复，在窗口显示后调用

        Args:
            delay_ms: 延迟时间（毫秒），默认100ms
        """
        if not hasattr(self, '_icon_fixed'):
            self._icon_fixed = False
        if not hasattr(self, '_fix_timer'):
            self._fix_timer = None

        if self._icon_fixed:
            return

        if os.name == 'nt':
            self._fix_timer = QTimer()
            self._fix_timer.setSingleShot(True)
            self._fix_timer.timeout.connect(self._fix_icon_safe)
            self._fix_timer.start(delay_ms)

    def _fix_icon_safe(self):
        """安全修复任务栏图标"""
        try:
            if hasattr(self, '_icon_fixed') and self._icon_fixed:
                return True

            success = fix_windows_taskbar_icon_for_window(self)
            if hasattr(self, '_icon_fixed'):
                self._icon_fixed = True

            if hasattr(self, 'debug_logger') and hasattr(self.debug_logger, 'log_info'):
                self.debug_logger.log_info("任务栏图标修复完成")
            self.icon_fixed.emit(success)
            return success
        except Exception as e:
            error_msg = f"任务栏图标修复失败: {e}"
            if hasattr(self, 'debug_logger') and hasattr(self.debug_logger, 'log_error'):
                self.debug_logger.log_error(error_msg)
            else:
                print(f"[ERROR] {error_msg}")
            self.icon_fixed.emit(False)
            return False

    def fix_taskbar_icon(self):
        """
        修复任务栏图标 - 兼容旧接口

        为了保持向后兼容性，提供此方法
        """
        if not hasattr(self, '_icon_fixed'):
            self._icon_fixed = False
        if not hasattr(self, '_fix_timer'):
            self._fix_timer = None
        return self._fix_icon_safe()

    def _fix_taskbar_icon_safe(self):
        """
        安全修复任务栏图标 - 兼容旧接口

        为了保持向后兼容性，提供此方法
        """
        return self._fix_icon_safe()

    def cleanup_icon_fixing(self):
        """清理图标修复相关的资源"""
        if hasattr(self, '_fix_timer') and self._fix_timer and self._fix_timer.isActive():
            self._fix_timer.stop()
            self._fix_timer = None


class ModernMenu(QMenu):
    """现代化的菜单，使用 setMask 修复 Windows 系统下圆角显示问题"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.Popup |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)

        style_helper = UnifiedStyleHelper.get_instance()
        menu_style = f"""
            QMenu {{ 
                background-color: {style_helper.COLORS['bg']};
                border: 1px solid {style_helper.COLORS['border']};
                padding: 6px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 8px;
                margin: 2px 2px;
            }}
            QMenu::item:selected {{
                background-color: {style_helper.COLORS['primary_hover']};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {style_helper.COLORS['border_light']};
                margin: 4px 8px;
            }}
        """
        self.setStyleSheet(menu_style)

    def showEvent(self, event):
        """菜单显示时设置圆角遮罩"""
        super().showEvent(event)

        if os.name == 'nt':
            try:
                import ctypes

                hwnd = int(self.winId())

                GWL_STYLE = -16
                GWL_EXSTYLE = -20
                WS_POPUP = 0x80000000
                WS_BORDER = 0x00800000
                WS_DLGFRAME = 0x00400000
                WS_THICKFRAME = 0x00040000
                WS_EX_DLGMODALFRAME = 0x00000001
                WS_EX_WINDOWEDGE = 0x00000100
                WS_EX_CLIENTEDGE = 0x00000200
                WS_EX_STATICEDGE = 0x00020000

                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)

                style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME)
                style |= WS_POPUP
                ex_style &= ~(WS_EX_DLGMODALFRAME | WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE)

                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)

                SWP_FRAMECHANGED = 0x0020
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOZORDER = 0x0004
                ctypes.windll.user32.SetWindowPos(
                    hwnd, 0, 0, 0, 0, 0,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
                )
            except Exception:
                pass

        QTimer.singleShot(0, self._update_rounded_mask)

    def resizeEvent(self, event):
        """窗口大小改变时更新遮罩"""
        super().resizeEvent(event)
        QTimer.singleShot(0, self._update_rounded_mask)

    def _update_rounded_mask(self):
        """更新圆角遮罩，使用 QBitmap 创建光滑的圆角"""
        if self.width() <= 0 or self.height() <= 0:
            return

        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.GlobalColor.color0)

        painter = QPainter(bitmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.GlobalColor.color1)
        painter.setPen(Qt.PenStyle.NoPen)

        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 8.0, 8.0)
        painter.end()

        self.setMask(bitmap)

    def addMenu(self, *args):
        """重写 addMenu 方法，确保子菜单也使用 ModernMenu"""
        if len(args) == 1:
            if isinstance(args[0], str):
                submenu = ModernMenu(self)
                submenu.setTitle(args[0])
                action = super().addMenu(submenu)
                return submenu
            elif isinstance(args[0], QMenu):
                menu = args[0]
                menu.setWindowFlags(
                    Qt.WindowType.Popup |
                    Qt.WindowType.FramelessWindowHint |
                    Qt.WindowType.NoDropShadowWindowHint
                )
                menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                return super().addMenu(menu)
        return super().addMenu(*args)


class ModernMenuBar(QMenuBar):
    """现代化的菜单栏，为其创建的菜单自动应用无边框样式"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def addMenu(self, *args):
        """重写 addMenu 方法，创建 ModernMenu 实例"""
        if len(args) == 1:
            if isinstance(args[0], str):
                menu = ModernMenu(self)
                menu.setTitle(args[0])
                action = super().addMenu(menu)
                return menu
            elif isinstance(args[0], QMenu):
                menu = args[0]
                menu.setWindowFlags(
                    Qt.WindowType.Popup |
                    Qt.WindowType.FramelessWindowHint |
                    Qt.WindowType.NoDropShadowWindowHint
                )
                menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                return super().addMenu(menu)
        return super().addMenu(*args)

    def refresh_theme_styles(self):
        """刷新菜单栏及所有菜单的样式，应用当前主题"""
        from .themes import UnifiedStyleHelper
        helper = UnifiedStyleHelper.get_instance()

        self.setStyleSheet(f""
            f"QMenuBar {{\n"
            f"    background-color: {helper.COLORS['bg']};\n"
            f"    color: {helper.COLORS['text']};\n"
            f"    border: none;\n"
            f"    border-radius: 8px;\n"
            f"    padding: 0px 4px 4px 4px;\n"
            f"}}\n"
            f"QMenuBar::item {{\n"
            f"    padding: 4px 8px;\n"
            f"    border-radius: 8px;\n"
            f"}}\n"
            f"QMenuBar::item:selected {{\n"
            f"    background-color: {helper.COLORS['primary_hover']};\n"
            f"    color: white;\n"
            f"}}\n"
        )

        menu_style = """QMenu {{
    background-color: {0};
    color: {1};
    border: 1px solid {2};
    padding: 6px;
}}
QMenu::item {{
    padding: 6px 16px;
    border-radius: 8px;
    margin: 2px 2px;
}}
QMenu::item:selected {{
    background-color: {3};
    color: white;
}}
QMenu::separator {{
    height: 1px;
    background-color: {4};
    margin: 4px 8px;
}}
"""
        menu_style = menu_style.format(
            helper.COLORS['bg'],
            helper.COLORS['text'],
            helper.COLORS['border'],
            helper.COLORS['primary_hover'],
            helper.COLORS['border_light']
        )

        def update_menu_styles(menu):
            if menu:
                menu.setStyleSheet(menu_style)
                for action in menu.actions():
                    sub_menu = action.menu()
                    if sub_menu:
                        update_menu_styles(sub_menu)

        for action in self.actions():
            menu = action.menu()
            if menu:
                update_menu_styles(menu)


class ModernGroupBox(QGroupBox):
    """现代化的分组框"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_group_box_style())

    def refresh_theme_styles(self):
        """刷新分组框的样式，应用当前主题"""
        helper = UnifiedStyleHelper.get_instance()
        self.setStyleSheet(helper.get_group_box_style())


class ModernLineEdit(QLineEdit):
    """现代化的输入框，内容居中显示"""
    def __init__(self, text="", parent=None, width=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_line_edit_style())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)


class ModernComboBox(QComboBox):
    """现代化的下拉框，内容居中显示"""
    def __init__(self, parent=None, width=None):
        super().__init__(parent)
        if width:
            self.setFixedWidth(width)

        combo_style = UnifiedStyleHelper.get_instance().get_combo_box_style() + "\n"
        combo_style += "QComboBox {\n"
        combo_style += "    text-align: center;\n"
        combo_style += "    padding: 6px 12px;\n"
        combo_style += "}\n"
        self.setStyleSheet(combo_style)

        view = self.view()
        if view:
            view.setStyleSheet("""
                 QListView::item {
                     padding: 4px 8px;
                     min-height: 18px;
                     text-align: center;
                 }
             """)

    def addItem(self, text):
        super().addItem(text)
        self.setItemData(self.count() - 1, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

    def addItems(self, texts):
        super().addItems(texts)
        for i in range(self.count()):
            self.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

    def wheelEvent(self, event):
        """屏蔽鼠标滚轮事件，防止误触"""
        event.ignore()


class ModernSpinBox(QSpinBox):
    """现代化的整数输入框，带上下按钮，内容居中显示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_spin_box_style())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)


class ModernDoubleSpinBox(QDoubleSpinBox):
    """现代化的浮点数输入框，带上下按钮，内容居中显示，根据时间单位动态调整步长"""
    def __init__(self, parent=None, width=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)
        if width:
            self.setFixedWidth(width)
        self.setSingleStep(1.0)  # 默认步长为1.0
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_spin_box_style())
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
    
    def update_step_based_on_unit(self, time_unit):
        """根据时间单位更新步长
        
        Args:
            time_unit (str): 时间单位，可以是 'ms', 's', 'min'
        """
        if time_unit == "ms":
            self.setSingleStep(100.0)  # 毫秒单位时，步长为100
        else:
            self.setSingleStep(1.0)    # 秒或分钟单位时，步长为1


class CenteredComboBox(QComboBox):
    """完全居中的组合框"""
    def __init__(self, parent=None):
        super().__init__(parent)

        base_style = UnifiedStyleHelper.get_instance().get_centered_combo_box_style()
        enhanced_style = base_style + """
            QComboBox {
                min-height: 18px;
                max-height: 18px;
            }
        """
        self.setStyleSheet(enhanced_style)

        self.setEditable(False)

        view = self.view()
        if view:
            view.setStyleSheet("""
                QListView::item {
                    padding: 4px 8px;
                    min-height: 18px;
                }
            """)

    def addItems(self, items):
        """添加项目并确保居中"""
        super().addItems(items)
        for i in range(self.count()):
            self.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)

    def wheelEvent(self, event):
        """屏蔽鼠标滚轮事件，防止误触"""
        event.ignore()


class CenteredLineEdit(QLineEdit):
    """居中对齐的单行文本编辑器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        base_style = UnifiedStyleHelper.get_instance().get_line_edit_style()
        enhanced_style = base_style + """
            QLineEdit {
                min-height: 18px;
                max-height: 18px;
            }
        """
        self.setStyleSheet(enhanced_style)


class TimeOffsetSpinBox(QSpinBox):
    """时间偏移输入框，带上下调节按钮，根据时间单位动态调整步长"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.setMinimum(0)
        self.setMaximum(999999)
        self.setSingleStep(100)  # 默认步长为100（毫秒单位）
        self.setValue(0)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        base_style = UnifiedStyleHelper.get_instance().get_time_offset_spin_box_style()
        enhanced_style = base_style + """
            QSpinBox {
                min-height: 18px;
                max-height: 18px;
            }
        """
        self.setStyleSheet(enhanced_style)
    
    def update_step_based_on_unit(self, time_unit):
        """根据时间单位更新步长
        
        Args:
            time_unit (str): 时间单位，可以是 'ms', 's', 'min'
        """
        if time_unit == "ms":
            self.setSingleStep(100)  # 毫秒单位时，步长为100
        else:
            self.setSingleStep(1)    # 秒或分钟单位时，步长为1


class AnimatedButton(QPushButton):
    """带动画效果的按钮控件"""

    def __init__(self, text="", parent=None, accent=False, disabled=False):
        super().__init__(text, parent)
        self.accent = accent
        self.disabled = disabled
        self.pressed_color = None
        self.animation_duration = 100

        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent, disabled))

        self.original_style = UnifiedStyleHelper.get_instance().get_button_style(accent, disabled)

        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)

    def _on_pressed(self):
        """按钮按下时的处理"""
        if not self.disabled:
            if self.accent:
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['primary_pressed']};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-weight: bold;
                        font-size: 11px;
                        {SHADOWS['small']}
                        min-height: 18px;
                        max-height: 18px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['primary_pressed']};
                    }}
                """
            else:
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['secondary_pressed']};
                        color: {COLORS['text']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-size: 11px;
                        {SHADOWS['small']}
                        min-height: 18px;
                        max-height: 18px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['secondary_pressed']};
                    }}
                """
            self.setStyleSheet(pressed_style)

    def _on_released(self):
        """按钮释放时的处理"""
        self.setStyleSheet(self.original_style)


class ModernButton(AnimatedButton):
    """现代化的按钮，带有动画效果"""
    def __init__(self, text="", parent=None, accent=False, disabled=False):
        super().__init__(text, parent, accent, disabled)


class EventEditButton(AnimatedButton):
    """事件编辑对话框专用按钮，带有动画效果"""
    def __init__(self, text, accent=False, parent=None, fixed_width=None):
        super().__init__(text, parent, accent, False)

        self.setFixedHeight(20)

        if fixed_width:
            self.setFixedWidth(fixed_width)

        base_style = UnifiedStyleHelper.get_instance().get_button_style(accent)
        enhanced_style = base_style + "\n"
        enhanced_style += "QPushButton {\n"
        enhanced_style += "    min-height: 18px;\n"
        enhanced_style += "    max-height: 18px;\n"
        enhanced_style += "}"
        self.setStyleSheet(enhanced_style)

        self.original_style = enhanced_style
