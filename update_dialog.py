# update_dialog.py - 检查更新对话框模块
"""
检查更新对话框模块，负责从Gitee仓库获取最新版本信息，
并提供版本比较和跳转功能。
"""

import sys
import re
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices

# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager, FadeInWindowMixin, StyledDialog, DialogFactory
from utils import load_icon_universal
from version import version_manager

try:
    import requests
except ImportError:
    requests = None


class UpdateCheckThread(QThread):
    """检查更新的后台线程"""
    
    # 定义信号
    check_finished = pyqtSignal(bool, str, str)  # (成功, 最新版本, 错误信息)
    
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        
    def run(self):
        """在后台线程中检查更新"""
        try:
            if requests is None:
                self.check_finished.emit(False, "", "缺少 requests 库，无法检查更新")
                return
            
            # Gitee API URL - 获取最新发行版
            api_url = "https://gitee.com/api/v5/repos/qingshangongzai/BetterGI_StellTrack/releases/latest"
            
            # 设置超时时间为10秒
            response = requests.get(api_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                latest_version = data.get("tag_name", "").lstrip("v")
                
                if latest_version:
                    self.check_finished.emit(True, latest_version, "")
                else:
                    self.check_finished.emit(False, "", "无法解析版本信息")
            else:
                self.check_finished.emit(False, "", f"获取版本信息失败: HTTP {response.status_code}")
                
        except requests.exceptions.Timeout:
            self.check_finished.emit(False, "", "连接超时，请检查网络连接")
        except requests.exceptions.ConnectionError:
            self.check_finished.emit(False, "", "网络连接失败，请检查网络设置")
        except Exception as e:
            self.check_finished.emit(False, "", f"检查更新时出错: {str(e)}")


class UpdateDialog(FadeInWindowMixin, StyledDialog):
    """检查更新对话框"""
    
    def __init__(self, parent=None):
        super().__init__(
            parent,
            title="检查更新",
            size=(380, 320),
            window_flags=Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
        )
        
        # 获取当前版本
        self.current_version = version_manager.get_version()
        
        # 检查更新线程
        self.check_thread = None
        
        # 设置UI
        self.setup_ui()
        
        # 自动开始检查
        self.start_check()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("检查更新")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 16, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 8px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 当前版本信息
        version_layout = QHBoxLayout()
        version_layout.setSpacing(10)
        version_layout.addStretch()  # 左侧弹簧
        
        current_label = QLabel("当前版本:")
        font_manager = get_global_font_manager()
        current_label.setFont(font_manager.get_source_han_font(10))
        current_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        version_layout.addWidget(current_label)
        
        self.current_version_label = QLabel(self.current_version)
        UnifiedStyleHelper.get_instance().set_smiley_font(self.current_version_label, 10, QFont.Weight.Bold)
        self.current_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        version_layout.addWidget(self.current_version_label)
        
        version_layout.addStretch()  # 右侧弹簧
        layout.addLayout(version_layout)
        
        # 最新版本信息
        latest_layout = QHBoxLayout()
        latest_layout.setSpacing(10)
        latest_layout.addStretch()  # 左侧弹簧
        
        latest_label = QLabel("最新版本:")
        latest_label.setFont(font_manager.get_source_han_font(10))
        latest_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        latest_layout.addWidget(latest_label)
        
        self.latest_version_label = QLabel("检查中...")
        UnifiedStyleHelper.get_instance().set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
        self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};")
        latest_layout.addWidget(self.latest_version_label)
        
        latest_layout.addStretch()  # 右侧弹簧
        layout.addLayout(latest_layout)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # 不确定进度
        self.progress_bar.setStyleSheet(UnifiedStyleHelper.get_instance().get_progress_bar_style())
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
        # 状态信息文本框
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setStyleSheet(UnifiedStyleHelper.get_instance().get_text_edit_style() + """
            QTextEdit {
                text-align: center;
            }
        """)
        self.status_text.setFixedHeight(100)
        self.status_text.setFont(font_manager.get_source_han_font(9))
        # 设置文本居中对齐
        from PyQt6.QtGui import QTextOption
        self.status_text.document().setDefaultTextOption(
            QTextOption(Qt.AlignmentFlag.AlignCenter)
        )
        self.status_text.setPlainText("正在连接到 Gitee 仓库...\n请稍候...")
        layout.addWidget(self.status_text)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()  # 左侧弹簧使按钮居中
        
        # 访问发行页面按钮
        self.visit_button = QPushButton("访问发行页面")
        self.visit_button.setFont(font_manager.get_source_han_font(9))
        self.visit_button.setFixedSize(100, 28)
        self.visit_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        self.visit_button.clicked.connect(self.open_release_page)
        self.visit_button.setEnabled(True)  # 默认启用，允许用户随时访问
        button_layout.addWidget(self.visit_button)
        
        # 重新检查按钮
        self.recheck_button = QPushButton("重新检查")
        self.recheck_button.setFont(font_manager.get_source_han_font(9))
        self.recheck_button.setFixedSize(80, 28)
        self.recheck_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.recheck_button.clicked.connect(self.start_check)
        self.recheck_button.setEnabled(False)
        button_layout.addWidget(self.recheck_button)
        
        button_layout.addStretch()  # 右侧弹簧使按钮居中
        layout.addLayout(button_layout)
        
    def start_check(self):
        """开始检查更新"""
        # 重置UI状态
        self.latest_version_label.setText("检查中...")
        self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};")
        self.status_text.setPlainText("正在连接到 Gitee 仓库...\n请稍候...")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        # self.visit_button.setEnabled(False)  # 不禁用按钮，允许用户随时访问
        self.recheck_button.setEnabled(False)
        
        # 创建并启动检查线程
        self.check_thread = UpdateCheckThread(self.current_version)
        self.check_thread.check_finished.connect(self.on_check_finished)
        self.check_thread.start()
        
    def on_check_finished(self, success, latest_version, error_msg):
        """检查完成的回调"""
        # 停止进度条
        self.progress_bar.setVisible(False)
        self.recheck_button.setEnabled(True)
        self.visit_button.setEnabled(True)  # 始终启用访问按钮
        
        if success:
            # 比较版本
            is_latest = self.compare_versions(self.current_version, latest_version)
            
            self.latest_version_label.setText(latest_version)
            UnifiedStyleHelper.get_instance().set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
            
            if is_latest >= 0:
                # 当前版本是最新或更新
                self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['success']};")
                if is_latest == 0:
                    status_msg = f"恭喜！您使用的是最新版本 {latest_version}\n\n无需更新。"
                else:
                    status_msg = f"您使用的版本 {self.current_version} 比官方最新版本 {latest_version} 更新\n\n这可能是开发版本或测试版本。"
            else:
                # 有新版本
                self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
                status_msg = f"发现新版本！\n\n最新版本: {latest_version}\n当前版本: {self.current_version}\n\n建议您更新到最新版本以获得更好的体验和功能。"
            
            self.status_text.setPlainText(status_msg)
        else:
            # 检查失败
            self.latest_version_label.setText("检查失败")
            UnifiedStyleHelper.get_instance().set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
            self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['error']};")
            status_msg = f"检查更新失败\n\n{error_msg}\n\n请检查网络连接后重试，或手动访问项目页面查看最新版本。"
            self.status_text.setPlainText(status_msg)
            
    def compare_versions(self, current, latest):
        """
        比较版本号
        返回值: 
        - 0: 版本相同
        - 1: 当前版本更新
        - -1: 有新版本
        """
        def parse_version(version_str):
            """解析版本号为数字列表"""
            # 移除可能的v前缀
            version_str = version_str.lstrip("v")
            # 提取数字部分
            parts = re.findall(r'\d+', version_str)
            return [int(p) for p in parts] if parts else [0]
        
        current_parts = parse_version(current)
        latest_parts = parse_version(latest)
        
        # 补齐长度
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        # 逐位比较
        for c, l in zip(current_parts, latest_parts):
            if c > l:
                return 1
            elif c < l:
                return -1
        
        return 0
        
    def open_release_page(self):
        """打开Gitee发行版页面"""
        print("[调试] 点击了访问发行版页面按钮")  # 调试信息
        try:
            url = "https://gitee.com/qingshangongzai/BetterGI_StellTrack/releases"
            print(f"[调试] 尝试打开URL: {url}")  # 调试信息
            
            # 直接使用 webbrowser ，更稳定
            import webbrowser
            result = webbrowser.open(url)
            print(f"[调试] webbrowser.open 返回值: {result}")  # 调试信息
            
            if not result:
                # 如果 webbrowser 失败，尝试 QDesktopServices
                print("[调试] webbrowser 失败，尝试 QDesktopServices")  # 调试信息
                success = QDesktopServices.openUrl(QUrl(url))
                print(f"[调试] QDesktopServices.openUrl 返回值: {success}")  # 调试信息
                
                if not success:
                    raise Exception("两种方法都无法打开浏览器")
                    
        except Exception as e:
            print(f"[调试] 异常: {str(e)}")  # 调试信息
            # 如果出现异常，记录错误并提示用户
            from utils import ChineseMessageBox
            ChineseMessageBox.show_error(
                self,
                "打开失败",
                f"无法打开浏览器\n\n请手动复制以下链接到浏览器访问:\n{url}\n\n错误信息: {str(e)}"
            )
        
    def showEvent(self, event):
        """对话框显示事件 - 首次显示时居中并触发淡入动画"""
        if not hasattr(self, "_update_dialog_first_show_done"):
            self._update_dialog_first_show_done = True
            # 首次显示前进行居中
            try:
                self.center()
            except Exception:
                pass
            # 确保动画从完全透明开始
            try:
                self.setWindowOpacity(0.0)
            except Exception:
                pass
        super().showEvent(event)
        
    def center(self):
        """将窗口居中显示"""
        if self.parent():
            parent_geometry = self.parent().geometry()
            x = parent_geometry.x() + (parent_geometry.width() - self.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - self.height()) // 2
            self.move(x, y)
