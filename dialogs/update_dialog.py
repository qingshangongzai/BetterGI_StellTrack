# update_dialog.py - 检查更新对话框模块
"""
检查更新对话框模块，负责从Gitee仓库获取最新版本信息，
并提供版本比较和跳转功能。
"""

# 标准库模块导入
import re
import webbrowser

# 第三方模块导入
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QProgressBar
)

try:
    import requests
except ImportError:
    requests = None

# 项目模块导入
from version import version_manager
from styles import (
    UnifiedStyleHelper,
    get_global_font_manager,
    FadeInWindowMixin,
    StyledDialog,
    DialogFactory,
    ChineseMessageBox
)
from utils import load_icon_universal


class UpdateCheckThread(QThread):
    """检查更新的后台线程
    
    在后台线程中检查Gitee仓库的最新版本信息，
    避免阻塞主线程。
    """
    
    check_finished = pyqtSignal(bool, str, str)
    
    def __init__(self, current_version):
        """初始化检查更新线程
        
        Args:
            current_version (str): 当前版本号
        """
        super().__init__()
        self.current_version = current_version
        
    def run(self):
        """在后台线程中检查更新"""
        try:
            if requests is None:
                self.check_finished.emit(False, "", "缺少 requests 库，无法检查更新")
                return
            
            api_url = "https://gitee.com/api/v5/repos/qingshangongzai/BetterGI_StellTrack/releases/latest"
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
    """检查更新对话框
    
    提供版本检查功能，显示当前版本和最新版本信息，
    并提供访问发行页面的功能。
    """
    
    def __init__(self, parent=None):
        """初始化检查更新对话框
        
        Args:
            parent: 父窗口对象
        """
        super().__init__(
            parent,
            title="检查更新",
            size=(500, 320),
            window_flags=Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint
        )
        
        self.current_version = version_manager.get_version()
        self.check_thread = None
        
        self.setup_ui()
        self.start_check()
        
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        style_helper = UnifiedStyleHelper.get_instance()
        font_manager = get_global_font_manager()
        
        title_label = QLabel("检查更新")
        style_helper.set_smiley_font(title_label, 16, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {style_helper.COLORS['primary']}; margin-bottom: 8px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        version_layout = QHBoxLayout()
        version_layout.setSpacing(10)
        version_layout.addStretch()
        
        current_label = QLabel("当前版本:")
        current_label.setFont(font_manager.get_source_han_font(10))
        current_label.setStyleSheet(f"color: {style_helper.COLORS['text']};")
        version_layout.addWidget(current_label)
        
        self.current_version_label = QLabel(self.current_version)
        style_helper.set_smiley_font(self.current_version_label, 10, QFont.Weight.Bold)
        self.current_version_label.setStyleSheet(f"color: {style_helper.COLORS['primary']};")
        version_layout.addWidget(self.current_version_label)
        
        version_layout.addStretch()
        layout.addLayout(version_layout)
        
        latest_layout = QHBoxLayout()
        latest_layout.setSpacing(10)
        latest_layout.addStretch()
        
        latest_label = QLabel("最新版本:")
        latest_label.setFont(font_manager.get_source_han_font(10))
        latest_label.setStyleSheet(f"color: {style_helper.COLORS['text']};")
        latest_layout.addWidget(latest_label)
        
        self.latest_version_label = QLabel("检查中...")
        style_helper.set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
        self.latest_version_label.setStyleSheet(f"color: {style_helper.COLORS['text_secondary']};")
        latest_layout.addWidget(self.latest_version_label)
        
        latest_layout.addStretch()
        layout.addLayout(latest_layout)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setStyleSheet(style_helper.get_progress_bar_style())
        self.progress_bar.setFixedHeight(6)
        layout.addWidget(self.progress_bar)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self.status_text.setStyleSheet(style_helper.get_text_edit_style() + """
            QTextEdit {
                text-align: center;
            }
        """)
        self.status_text.setFixedHeight(100)
        self.status_text.setFont(font_manager.get_source_han_font(9))
        from PyQt6.QtGui import QTextOption
        self.status_text.document().setDefaultTextOption(
            QTextOption(Qt.AlignmentFlag.AlignCenter)
        )
        self.status_text.setPlainText("正在连接到 Gitee 仓库...\n请稍候...")
        layout.addWidget(self.status_text)
        
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.addStretch()
        
        self.visit_button = QPushButton("发行页面")
        self.visit_button.setFont(font_manager.get_source_han_font(9))
        self.visit_button.setFixedWidth(100)
        self.visit_button.setFixedHeight(28)
        self.visit_button.setStyleSheet(style_helper.get_button_style(accent=True))
        self.visit_button.clicked.connect(self.open_release_page)
        self.visit_button.setEnabled(True)
        button_layout.addWidget(self.visit_button)
        
        self.recheck_button = QPushButton("重新检查")
        self.recheck_button.setFont(font_manager.get_source_han_font(9))
        self.recheck_button.setFixedWidth(100)
        self.recheck_button.setFixedHeight(28)
        self.recheck_button.setStyleSheet(style_helper.get_button_style())
        self.recheck_button.clicked.connect(self.start_check)
        self.recheck_button.setEnabled(False)
        button_layout.addWidget(self.recheck_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
    def start_check(self):
        """开始检查更新"""
        self.latest_version_label.setText("检查中...")
        self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};")
        self.status_text.setPlainText("正在连接到 Gitee 仓库...\n请稍候...")
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(True)
        self.recheck_button.setEnabled(False)
        
        self.check_thread = UpdateCheckThread(self.current_version)
        self.check_thread.check_finished.connect(self.on_check_finished)
        self.check_thread.start()
        
    def on_check_finished(self, success, latest_version, error_msg):
        """检查完成的回调
        
        Args:
            success (bool): 检查是否成功
            latest_version (str): 最新版本号
            error_msg (str): 错误信息
        """
        self.progress_bar.setVisible(False)
        self.recheck_button.setEnabled(True)
        self.visit_button.setEnabled(True)
        
        if success:
            is_latest = self.compare_versions(self.current_version, latest_version)
            
            self.latest_version_label.setText(latest_version)
            UnifiedStyleHelper.get_instance().set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
            
            if is_latest >= 0:
                self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['success']};")
                if is_latest == 0:
                    status_msg = f"恭喜！您使用的是最新版本 {latest_version}\n\n无需更新。"
                else:
                    status_msg = f"您使用的版本 {self.current_version} 比官方最新版本 {latest_version} 更新\n\n这可能是开发版本或测试版本。"
            else:
                self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
                status_msg = f"发现新版本！\n\n最新版本: {latest_version}\n当前版本: {self.current_version}\n\n建议您更新到最新版本以获得更好的体验和功能。"
            
            self.status_text.setPlainText(status_msg)
        else:
            self.latest_version_label.setText("检查失败")
            UnifiedStyleHelper.get_instance().set_smiley_font(self.latest_version_label, 10, QFont.Weight.Bold)
            self.latest_version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['error']};")
            status_msg = f"检查更新失败\n\n{error_msg}\n\n请检查网络连接后重试，或手动访问项目页面查看最新版本。"
            self.status_text.setPlainText(status_msg)
            
    def compare_versions(self, current, latest):
        """比较版本号
        
        Args:
            current (str): 当前版本号
            latest (str): 最新版本号
            
        Returns:
            int: 0表示版本相同，1表示当前版本更新，-1表示有新版本
        """
        def parse_version(version_str):
            """解析版本号为数字列表"""
            version_str = version_str.lstrip("v")
            parts = re.findall(r'\d+', version_str)
            return [int(p) for p in parts] if parts else [0]
        
        current_parts = parse_version(current)
        latest_parts = parse_version(latest)
        
        max_len = max(len(current_parts), len(latest_parts))
        current_parts.extend([0] * (max_len - len(current_parts)))
        latest_parts.extend([0] * (max_len - len(latest_parts)))
        
        for c, l in zip(current_parts, latest_parts):
            if c > l:
                return 1
            elif c < l:
                return -1
        
        return 0
        
    def open_release_page(self):
        """打开Gitee发行版页面"""
        try:
            url = "https://gitee.com/qingshangongzai/BetterGI_StellTrack/releases"
            result = webbrowser.open(url)
            
            if not result:
                success = QDesktopServices.openUrl(QUrl(url))
                
                if not success:
                    raise Exception("两种方法都无法打开浏览器")
                    
        except Exception as e:
            ChineseMessageBox.show_error(
                self,
                "打开失败",
                f"无法打开浏览器\n\n请手动复制以下链接到浏览器访问:\n{url}\n\n错误信息: {str(e)}"
            )
        
    def showEvent(self, event):
        """对话框显示事件 - 首次显示时居中并触发淡入动画"""
        if not hasattr(self, "_update_dialog_first_show_done"):
            self._update_dialog_first_show_done = True
            try:
                self.center()
            except Exception:
                pass
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
