# debug_dialog.py

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QDialog
)
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices, QFont

from styles import (
    UnifiedStyleHelper, ModernLineEdit, StyledDialog, 
    FadeInWindowMixin, DialogFactory, ChineseMessageBox
)
from utils import load_icon_universal


class AnimatedConfirmDialog(FadeInWindowMixin, StyledDialog):
    """带动画效果的确认对话框"""
    
    def __init__(self, parent=None, title="确认", message="", ok_text="确定", cancel_text="取消"):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(300, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                            Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 信息标签
        info_label = QLabel(message)
        info_label.setFont(self.font_manager.get_source_han_font(10))
        info_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # 使用DialogFactory创建确定和取消按钮布局
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text=ok_text,
            cancel_text=cancel_text
        )
        
        layout.addLayout(button_layout)
        
        # 获取按钮引用并设置固定尺寸
        self.ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        self.cancel_btn = button_layout.itemAt(2).widget()
        
        self.ok_btn.setFixedHeight(30)
        self.cancel_btn.setFixedHeight(30)


class CustomInputDialog(FadeInWindowMixin, StyledDialog):
    """自定义输入对话框，与程序风格保持一致"""
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # 字体管理器已通过StyledDialog自动获取
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("调试工具入口")
        self.setFixedSize(500, 320)  # 增加高度，确保内容完全显示
        
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
        self.ok_btn.setMinimumHeight(30)
        
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
            confirm_dialog = AnimatedConfirmDialog(
                parent=self,
                title="彩蛋确认",
                message="恭喜你发现了彩蛋",
                ok_text="打开视频",
                cancel_text="取消"
            )
            
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