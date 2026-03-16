# 标准库模块导入
# 无标准库模块导入

# 第三方模块导入
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPalette, QPixmap
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea
from qframelesswindow import FramelessDialog

# 项目模块导入
from .themes import UnifiedStyleHelper
from .widgets import FadeInWindowMixin, TitleBarThemeMixin, ModernButton
from .fonts import get_global_font_manager
from utils import load_icon_universal


class DialogFactory:
    """对话框UI组件工厂，封装重复的UI创建模式

    提供统一的对话框按钮布局创建方法，确保对话框样式的一致性。
    """

    @staticmethod
    def create_ok_cancel_buttons(parent, on_ok, on_cancel, ok_text="确定", cancel_text="取消", button_class=None):
        """创建确定和取消按钮布局

        Args:
            parent: 父窗口组件
            on_ok: 确定按钮点击事件处理函数
            on_cancel: 取消按钮点击事件处理函数
            ok_text: 确定按钮文本，默认为"确定"
            cancel_text: 取消按钮文本，默认为"取消"
            button_class: 自定义按钮类，默认为None（使用ModernButton）

        Returns:
            QHBoxLayout: 包含确定和取消按钮的水平布局
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        if button_class is None:
            button_class = ModernButton

        ok_btn = button_class(ok_text, parent=parent, accent=True)
        cancel_btn = button_class(cancel_text, parent=parent)

        ok_btn.setFixedWidth(100)
        cancel_btn.setFixedWidth(100)

        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(on_cancel)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()

        return button_layout

    @staticmethod
    def create_close_button(parent, on_close, text="关闭"):
        """创建关闭按钮布局

        Args:
            parent: 父窗口组件
            on_close: 关闭按钮点击事件处理函数
            text: 关闭按钮文本，默认为"关闭"

        Returns:
            QHBoxLayout: 包含关闭按钮的水平布局
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        close_btn = ModernButton(text, parent=parent)

        close_btn.setFixedWidth(100)

        close_btn.clicked.connect(on_close)

        button_layout.addWidget(close_btn)
        button_layout.addStretch()

        return button_layout


class AnimatedDialog(FadeInWindowMixin, TitleBarThemeMixin, QDialog):
    """带淡入淡出动画的基础对话框

    继承自 FadeInWindowMixin 和 TitleBarThemeMixin，提供：
    - 窗口打开/关闭时的淡入淡出动画
    - Windows 标题栏深色/浅色模式自动切换支持

    Args:
        parent: 父窗口组件
    """

    def __init__(self, parent=None):
        """初始化带动画的对话框

        Args:
            parent: 父窗口组件
        """
        super().__init__(parent)


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
        if icon_path:
            logo_label = QLabel(title_bar)
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                logo_label.setPixmap(pixmap.scaled(
                    20, 20,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
        else:
            # 尝试使用默认logo
            try:
                logo_label = QLabel(title_bar)
                pixmap = QPixmap("logo/logo.png")
                if not pixmap.isNull():
                    logo_label.setPixmap(pixmap.scaled(
                        20, 20,
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    ))
            except Exception:
                logo_label = None

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


class ChineseMessageBox:
    """自定义消息框，确保按钮显示中文

    提供统一的对话框样式和中文按钮文本，包括：
    - 警告消息框
    - 错误消息框
    - 信息消息框
    - 询问消息框
    """

    @staticmethod
    def _create_message_dialog(parent, title, message, buttons_config=None):
        """创建消息对话框的通用辅助方法

        Args:
            parent: 父窗口组件
            title: 对话框标题
            message: 消息内容
            buttons_config: 按钮配置列表，每个元素为 (text, accent, slot) 元组

        Returns:
            AnimatedDialog: 配置好的对话框实例
        """
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())

        style_helper = UnifiedStyleHelper.get_instance()
        dialog.setStyleSheet(f"QDialog {{ background-color: {style_helper.COLORS['bg']}; border-radius: 8px; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setMaximumHeight(200)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet(f"QScrollArea {{ border: none; background-color: {style_helper.COLORS['bg']}; }}")

        # 创建消息标签
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"QLabel {{ font-size: 13px; color: {style_helper.COLORS['text']}; }}")

        # 将消息标签放入滚动区域
        scroll_area.setWidget(message_label)
        layout.addWidget(scroll_area)

        # 创建按钮布局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        if buttons_config:
            for text, accent, slot in buttons_config:
                button = QPushButton(text)
                button.setFixedWidth(100)
                button.setStyleSheet(style_helper.get_button_style(accent=accent))
                button.clicked.connect(slot)
                button_layout.addWidget(button)

        layout.addLayout(button_layout)

        dialog.adjustSize()
        dialog.setFixedWidth(min(dialog.width() + 20, 400))
        dialog.setMaximumHeight(310)

        return dialog

    @staticmethod
    def show_warning(parent, title, message):
        """显示警告消息

        Args:
            parent: 父窗口组件
            title: 对话框标题
            message: 警告消息内容

        Returns:
            bool: 用户是否点击了确定按钮
        """
        dialog = ChineseMessageBox._create_message_dialog(
            parent, title, message,
            buttons_config=[("确定", True, lambda: None)]
        )
        # 重新连接确定按钮到 accept
        for child in dialog.findChildren(QPushButton):
            if child.text() == "确定":
                child.clicked.disconnect()
                child.clicked.connect(dialog.accept)
                break

        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def show_error(parent, title, message):
        """显示错误消息

        Args:
            parent: 父窗口组件
            title: 对话框标题
            message: 错误消息内容
        """
        dialog = ChineseMessageBox._create_message_dialog(
            parent, title, message,
            buttons_config=[("确定", True, lambda: None)]
        )
        # 重新连接确定按钮到 accept
        for child in dialog.findChildren(QPushButton):
            if child.text() == "确定":
                child.clicked.disconnect()
                child.clicked.connect(dialog.accept)
                break

        dialog.exec()

    @staticmethod
    def show_info(parent, title, message):
        """显示信息消息

        Args:
            parent: 父窗口组件
            title: 对话框标题
            message: 信息消息内容
        """
        dialog = ChineseMessageBox._create_message_dialog(
            parent, title, message,
            buttons_config=[("确定", True, lambda: None)]
        )
        # 重新连接确定按钮到 accept
        for child in dialog.findChildren(QPushButton):
            if child.text() == "确定":
                child.clicked.disconnect()
                child.clicked.connect(dialog.accept)
                break

        dialog.exec()

    @staticmethod
    def show_question(parent, title, message):
        """显示询问消息

        Args:
            parent: 父窗口组件
            title: 对话框标题
            message: 询问消息内容

        Returns:
            bool: 用户是否点击了"是"按钮
        """
        dialog = ChineseMessageBox._create_message_dialog(
            parent, title, message,
            buttons_config=[
                ("是", True, lambda: None),
                ("否", False, lambda: None)
            ]
        )
        # 重新连接按钮信号
        for child in dialog.findChildren(QPushButton):
            if child.text() == "是":
                child.clicked.disconnect()
                child.clicked.connect(dialog.accept)
            elif child.text() == "否":
                child.clicked.disconnect()
                child.clicked.connect(dialog.reject)

        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
