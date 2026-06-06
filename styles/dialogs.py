# 标准库模块导入
# 无标准库模块导入

# 第三方模块导入
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor, QFont, QPalette, QPixmap
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton, QScrollArea
from qframelesswindow import FramelessDialog

# 项目模块导入
from .themes import UnifiedStyleHelper
from .fonts import get_global_font_manager
from utils import load_icon_universal

# 从 widgets 模块导入 BaseFramelessDialog 和混入类
from .widgets import BaseFramelessDialog, FadeInWindowMixin, TitleBarThemeMixin, ModernButton


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


class AnimatedDialog(FadeInWindowMixin, BaseFramelessDialog):
    """带淡入淡出动画的无边框对话框

    继承自 FadeInWindowMixin 和 BaseFramelessDialog，提供：
    - 窗口打开/关闭时的淡入淡出动画
    - 无边框设计和自定义标题栏
    - Windows 标题栏深色/浅色模式自动切换支持
    - 主题切换适配功能

    Args:
        parent: 父窗口组件
        title: 窗口标题，可选
        size: 窗口大小元组 (width, height)，可选
    """

    def __init__(self, parent=None, title="", size=None):
        """初始化带动画的无边框对话框

        Args:
            parent: 父窗口组件
            title: 窗口标题，可选
            size: 窗口大小元组 (width, height)，可选
        """
        super().__init__(parent=parent, title=title, size=size)


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
            buttons_config: 钮配置列表，每个元素为 (text, accent, slot) 元组

        Returns:
            AnimatedDialog: 配置好的对话框实例
        """
        # 使用 AnimatedDialog 的新构造函数，传入 title 参数
        dialog = AnimatedDialog(parent=parent, title=title)
        # BaseFramelessDialog 已设置图标，无需手动设置

        style_helper = UnifiedStyleHelper.get_instance()
        # 移除样式表设置，BaseFramelessDialog 使用 QPalette 设置背景色

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        # 顶部边距需要为标题栏留出空间
        layout.setContentsMargins(15, 40, 15, 15)

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
            buttons_config=[("确定", True, "accept")]
        )

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
            buttons_config=[("确定", True, "accept")]
        )

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
            buttons_config=[("确定", True, "accept")]
        )

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
                ("是", True, "accept"),
                ("否", False, "reject")
            ]
        )

        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
