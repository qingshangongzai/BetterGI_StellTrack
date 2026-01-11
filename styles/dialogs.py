from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QVBoxLayout, QLabel, QPushButton

from .themes import UnifiedStyleHelper
from .widgets import FadeInWindowMixin, TitleBarThemeMixin, ModernButton
from utils import load_icon_universal


class DialogFactory:
    """对话框UI组件工厂，封装重复的UI创建模式"""

    @staticmethod
    def create_ok_cancel_buttons(parent, on_ok, on_cancel, ok_text="确定", cancel_text="取消", button_class=None):
        """创建确定和取消按钮布局

        参数:
            parent: 父窗口组件
            on_ok: 确定按钮点击事件处理函数
            on_cancel: 取消按钮点击事件处理函数
            ok_text: 确定按钮文本，默认为"确定"
            cancel_text: 取消按钮文本，默认为"取消"
            button_class: 自定义按钮类，默认为None（使用ModernButton）

        返回:
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

        参数:
            parent: 父窗口组件
            on_close: 关闭按钮点击事件处理函数
            text: 关闭按钮文本，默认为"关闭"

        返回:
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
    """带淡入淡出动画的基础对话框"""

    def __init__(self, parent=None):
        super().__init__(parent)


class ChineseMessageBox:
    """自定义消息框，确保按钮显示中文"""

    @staticmethod
    def show_warning(parent, title, message):
        """显示警告消息"""
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)

        dialog.setStyleSheet(f"QDialog {{ background-color: {UnifiedStyleHelper.get_instance().COLORS['bg']}; border-radius: 8px; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"QLabel {{ font-size: 13px; color: {UnifiedStyleHelper.get_instance().COLORS['text']}; }}")
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)

        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted

    @staticmethod
    def show_error(parent, title, message):
        """显示错误消息"""
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)

        dialog.setStyleSheet(f"QDialog {{ background-color: {UnifiedStyleHelper.get_instance().COLORS['bg']}; border-radius: 8px; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"QLabel {{ font-size: 13px; color: {UnifiedStyleHelper.get_instance().COLORS['text']}; }}")
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)

        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        dialog.exec()

    @staticmethod
    def show_info(parent, title, message):
        """显示信息消息"""
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)

        dialog.setStyleSheet(f"QDialog {{ background-color: {UnifiedStyleHelper.get_instance().COLORS['bg']}; border-radius: 8px; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"QLabel {{ font-size: 13px; color: {UnifiedStyleHelper.get_instance().COLORS['text']}; }}")
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)

        button_layout.addWidget(ok_button)

        layout.addLayout(button_layout)

        dialog.exec()

    @staticmethod
    def show_question(parent, title, message):
        """显示询问消息"""
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)

        dialog.setStyleSheet(f"QDialog {{ background-color: {UnifiedStyleHelper.get_instance().COLORS['bg']}; border-radius: 8px; }}")

        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet(f"QLabel {{ font-size: 13px; color: {UnifiedStyleHelper.get_instance().COLORS['text']}; }}")
        layout.addWidget(message_label)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(10)

        yes_button = QPushButton("是")
        yes_button.setFixedWidth(100)
        yes_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        yes_button.clicked.connect(dialog.accept)

        no_button = QPushButton("否")
        no_button.setFixedWidth(100)
        no_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        no_button.clicked.connect(dialog.reject)

        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)

        layout.addLayout(button_layout)

        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
