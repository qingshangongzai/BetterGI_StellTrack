# about_window.py
import sys
import os
from PyQt6.QtWidgets import (QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QPushButton, QTextEdit, QFrame, QGroupBox, QTextBrowser, QPlainTextEdit)
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QIcon, QPixmap, QDesktopServices, QFontDatabase

# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager
from styles import ChineseMessageBox, DialogFactory
from user_agreement import load_user_agreement_html
# 导入调试工具模块
from debug_tools import PasswordDialog, DebugWindow
# 导入资源管理器和图标加载函数（从utils模块）
from utils import get_resource_path, find_resource_file, load_icon_universal, load_logo, get_current_version, get_current_app_info
from styles import WindowIconMixin
# 导入版本管理器
from main import version_manager

# =============================================================================
# 用户协议窗口 - 简化版
# =============================================================================

from styles import StyledMainWindow

class UserAgreementWindow(StyledMainWindow):
    """用户协议窗口"""
    
    def __init__(self, parent=None):
        # 使用基类初始化方法设置窗口属性
        super().__init__(parent,
                       title="用户服务协议与免责声明",
                       size=(800, 600),
                       window_flags=Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 创建头部区域
        self.create_header(main_layout)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        main_layout.addWidget(separator)
        
        # 创建协议内容区域
        self.create_agreement_content(main_layout)
        
        # 创建按钮区域
        self.create_buttons(main_layout)
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)  # 使用UnifiedStyleHelper统一设置字体
        header_layout.addWidget(logo_label)
        
        # 标题区域
        title_layout = QVBoxLayout()
        
        # 中文标题 - 使用得意黑字体
        title_label = QLabel("用户服务协议与免责声明")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 14, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_layout.addWidget(title_label)
        
        # 副标题
        subtitle_label = QLabel("请仔细阅读以下协议内容")
        font_manager = get_global_font_manager()
        subtitle_label.setFont(font_manager.get_source_han_font(11))
        subtitle_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_agreement_content(self, parent_layout):
        """创建协议内容区域"""
        # 创建文本浏览器（自带滚动条）
        self.agreement_browser = QTextBrowser()
        self.agreement_browser.setOpenExternalLinks(True)
        self.agreement_browser.setStyleSheet(UnifiedStyleHelper.get_instance().get_agreement_browser_style())
        
        # 设置协议内容
        self.set_agreement_content()
        
        parent_layout.addWidget(self.agreement_browser)
    
    def create_buttons(self, parent_layout):
        """创建按钮区域"""
        font_manager = get_global_font_manager()
        
        # 使用DialogFactory创建关闭按钮布局
        button_layout = DialogFactory.create_close_button(
            parent=self,
            on_close=self.close,
            text="关闭"
        )
        
        # 获取按钮并设置字体
        close_button = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        close_button.setFont(font_manager.get_source_han_font(10))
        
        parent_layout.addLayout(button_layout)
    
    def set_agreement_content(self):
        """设置协议内容 - 从HTML文件加载"""
        html_content = load_user_agreement_html()
        self.agreement_browser.setHtml(html_content)
    


# =============================================================================
# 关于窗口 - 简化版
# =============================================================================

class AboutWindowQt(StyledMainWindow, WindowIconMixin):
    """基于PyQt6的关于窗口"""
    
    # 定义信号
    manual_requested = pyqtSignal(str)
    
    def __init__(self, parent=None, version=None):
        # 如果未提供版本号，则从全局版本管理器获取
        self.version = version if version is not None else get_current_version()
        # 使用基类初始化方法设置窗口属性
        super().__init__(parent,
                       title=f"关于 BetterGI 星轨",
                       size=(700, 530),
                       window_flags=Qt.WindowType.Window | Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 设置图标修复 - 在窗口显示后调用
        self.setup_icon_fixing()
        
        # 居中显示窗口
        self.center()
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(8)  # 减少间距
        
        # 创建头部区域
        self.create_header(main_layout)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        main_layout.addWidget(separator)
        
        # 创建信息区域
        self.create_info_area(main_layout)
        
        # 创建按钮区域 - 修改为单行居中排列
        self.create_buttons_area(main_layout)
        
        # 创建版权信息
        self.create_copyright(main_layout)
        
        # 设置信号连接 - 确保在所有按钮创建完成后再调用
        self.setup_connections()
        
    def setup_connections(self):
        """设置信号连接"""
        # 按钮连接
        self.dev_button.clicked.connect(lambda: self.open_url("https://b23.tv/KO3m8zU"))
        self.project_button.clicked.connect(lambda: self.open_url("https://github.com/qingshangongzai/BetterGI_Macro"))
        self.agreement_button.clicked.connect(self.show_user_agreement)
        self.manual_button.clicked.connect(self.open_manual)
        self.license_button.clicked.connect(self.open_license)
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = self.load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)  # 使用UnifiedStyleHelper统一设置字体
        header_layout.addWidget(logo_label)
        
        # 标题区域
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)  # 减少主副标题间距，与主窗口一致
        
        # 中文标题 - 使用得意黑字体
        title_label = QLabel("BetterGI 星轨")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 24, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 0px;")
        title_layout.addWidget(title_label)
        
        # 英文标题 - 使用得意黑字体
        english_title = QLabel("BetterGI StellTrack")
        UnifiedStyleHelper.get_instance().set_smiley_font(english_title, 12)  # 使用UnifiedStyleHelper统一设置字体
        english_title.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-top: 0px; margin-bottom: 0px;")
        title_layout.addWidget(english_title)
        
        # 版本信息 - 使用得意黑字体
        version_label = QLabel(f"版本 {self.version}")
        UnifiedStyleHelper.get_instance().set_smiley_font(version_label, 10, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体
        version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']}; margin-top: 0px;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # 添加标语 - 使用SourceHanSerifCN字体
        slogan_label = QLabel("风带来故事的种子，时间使之发芽")
        slogan_label.setStyleSheet(f"""
            QLabel {{
                font-family: "SourceHanSerifCN";
                font-size: 12px;
                color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};
                font-style: italic;
                margin-right: 15px;
                background-color: transparent;
            }}
        """)
        header_layout.addWidget(slogan_label)
        
        parent_layout.addLayout(header_layout)
    
    def create_info_area(self, parent_layout):
        """创建信息显示区域 - 使用QPlainTextEdit完全控制格式"""
        # 创建纯文本编辑器
        self.info_edit = QPlainTextEdit()
        self.info_edit.setReadOnly(True)
        self.info_edit.setStyleSheet(UnifiedStyleHelper.get_instance().get_info_edit_style())
        
        # 设置信息内容
        self.set_info_content()
        
        # 设置固定高度
        self.info_edit.setFixedHeight(300)
        
        parent_layout.addWidget(self.info_edit)
    
    def create_buttons_area(self, parent_layout):
        """创建按钮区域 - 将所有按钮排成一行并居中"""
        # 创建按钮布局容器
        buttons_container = QWidget()
        buttons_h_layout = QHBoxLayout(buttons_container)
        buttons_h_layout.setSpacing(8)
        buttons_h_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加左侧弹性空间
        buttons_h_layout.addStretch()
        
        # 个人主页按钮
        self.dev_button = self.create_action_button("个人主页")
        buttons_h_layout.addWidget(self.dev_button)
        
        # 项目地址按钮
        self.project_button = self.create_action_button("项目地址")
        buttons_h_layout.addWidget(self.project_button)
        
        # 使用说明按钮
        self.manual_button = self.create_action_button("使用说明")
        buttons_h_layout.addWidget(self.manual_button)
        
        # 开源许可按钮
        self.license_button = self.create_action_button("开源许可")
        buttons_h_layout.addWidget(self.license_button)
        
        # 用户协议按钮
        self.agreement_button = self.create_action_button("用户协议")
        buttons_h_layout.addWidget(self.agreement_button)
        
        # 添加右侧弹性空间
        buttons_h_layout.addStretch()
        
        parent_layout.addWidget(buttons_container)
    
    def create_action_button(self, text):
        """创建操作按钮"""
        button = QPushButton(text)
        font_manager = get_global_font_manager()
        button.setFont(font_manager.get_source_han_font(9))
        button.setMinimumHeight(32)
        button.setMinimumWidth(90)  # 设置最小宽度确保按钮大小一致
        button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        return button
    
    def create_copyright(self, parent_layout):
        """创建版权信息 - 减少顶部间距"""
        copyright_layout = QVBoxLayout()
        copyright_layout.setSpacing(2)  # 减少间距
        copyright_layout.setContentsMargins(0, 5, 0, 0)  # 减少顶部边距
        
        copyright_text = QLabel(
            "版权所有 © 2025 HXiaoStudio\n"
            "基于GPL v3开源，仅供学习交流使用，切勿用于商用项目。"
        )
        copyright_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font_manager = get_global_font_manager()
        copyright_text.setFont(font_manager.get_source_han_font(8))
        copyright_text.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};")
        
        copyright_layout.addWidget(copyright_text)
        parent_layout.addLayout(copyright_layout)
    
    def set_info_content(self):
        """设置信息内容 - 使用纯文本格式，仅开头段落首行缩进"""
        content = """　　BetterGI 星轨（BetterGI StellTrack）是一款由 AI 大模型驱动、基于 Python 开发的创新软件，专为 BetterGI（一款《原神》自动化辅助工具）打造，致力于生成强大的键鼠自动化脚本。通过可视化界面，用户可以创建复杂的自动化操作序列，提升游戏体验和效率。


【注意事项】
· 使用本程序生成的自动化脚本可能违反游戏服务条款，存在账号封禁风险，请理性评估后使用；
· 严禁将本程序用于任何影响游戏公平性的场景，因此产生的一切后果由使用者自行承担。


【开发团队】
· 出品：浮晓 HXiao Studio
· 开发：青山公仔
· 代码：Deepseek、智谱清言、Trae、Qoder、CodeBuddy、通义千问
· logo 绘制：青山公仔
· 联系邮箱：qingshangongzai@163.com


【开源项目使用说明】
· 本程序LOGO与标题使用了「得意黑」，基于SIL Open Font License 1.1协议授权。
  设计师：oooooohmygosh
  版权所有：© atelierAnchor 锚坞
  项目地址：https://github.com/atelier-anchor/smiley-sans
  官方网站：https://atelier-anchor.com/typefaces/smiley-sans/
  许可证地址：https://atelier-anchor.com/typefaces/smiley-sans/license/

· 本程序默认字体使用了「思源宋体」，基于SIL Open Font License 1.1协议授权。
  版权所有：版权所有：© 2014-2023 Adobe (http://www.adobe.com/)
  项目地址：https://github.com/adobe-fonts/source-han-serif
  许可证地址：http://scripts.sil.org/OFL


· 本程序基于PyQt6架构开发，许可证：GNU General Public License v3.0 (GPLv3)
  版权所有：Riverbank Computing Limited
  项目地址：https://www.riverbankcomputing.com/software/pyqt/
  许可详情：https://www.riverbankcomputing.com/software/pyqt/license/

· 本程序使用auto-py-to-exe工具打包发行。
  项目地址：https://github.com/brentvollebregt/auto-py-to-exe


【特别鸣谢】
· 感谢BetterGI团队开发的原神辅助工具为玩家提供了便利。
  BetterGI团队：https://b23.tv/8rQCOI5
· 感谢得意黑与思源宋体的版权方设计的开源字体。
· 感谢Deepseek、智谱清言、阿里通义千问开发的大语言模型，阿里Qoder、字节跳动Trae、腾讯CodeBuddy开发的IDE工具为零代码基础人群开发程序提供了便利。"""
    
        self.info_edit.setPlainText(content)
    
    def load_icon(self):
        """加载窗口图标"""
        return load_icon_universal()
    
    def load_logo(self):
        """加载Logo图片"""
        return load_logo()
    
    def open_url(self, url):
        """打开URL链接"""
        QDesktopServices.openUrl(QUrl(url))
    
    def show_user_agreement(self):
        """显示用户协议窗口"""
        agreement_window = UserAgreementWindow(self)
        agreement_window.show()
    
    def open_manual(self):
        """打开使用说明"""
        manual_files = ["使用说明.pdf", "docs/使用说明.pdf", "assets/使用说明.pdf"]
        
        for manual_file in manual_files:
            manual_path = find_resource_file(manual_file)
            if manual_path and os.path.exists(manual_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(manual_path))
                return
        
        # 如果没有找到文件，发射信号
        self.manual_requested.emit("使用说明.pdf")
    
    def open_license(self):
        """打开开源许可"""
        license_files = ["LICENSE.html", "LICENSE", "assets/LICENSE.html"]
        
        for license_file in license_files:
            license_path = find_resource_file(license_file)
            if license_path and os.path.exists(license_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(license_path))
                return
        
        # 如果没有找到文件，发射信号
        self.manual_requested.emit("LICENSE.html")
    
    def center(self):
        """将窗口居中显示"""
        # 获取屏幕几何
        screen_geometry = self.screen().geometry()
        # 获取窗口几何
        window_geometry = self.frameGeometry()
        # 计算中心位置
        window_geometry.moveCenter(screen_geometry.center())
        # 移动窗口
        self.move(window_geometry.topLeft())
