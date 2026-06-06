# about_window.py - 关于窗口和用户协议模块
"""
关于窗口和用户协议模块，提供应用程序信息展示、
用户协议显示和相关链接访问功能。
"""

# 标准库模块导入
import os

# 第三方模块导入
from PyQt6.QtCore import Qt, pyqtSignal, QUrl
from PyQt6.QtGui import QFont, QDesktopServices
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QFrame, 
    QTextBrowser, QPlainTextEdit
)

# 项目模块导入
from styles import (
    UnifiedStyleHelper,
    get_global_font_manager,
    BaseFramelessDialog,
    DialogFactory
)
from .user_agreement import load_user_agreement_html
from .debug_tools import PasswordDialog, DebugWindow
from utils import (
    find_resource_file,
    load_logo,
    get_current_version
)


class UserAgreementWindow(BaseFramelessDialog):
    """用户协议窗口
    
    显示用户服务协议与免责声明内容。
    """
    
    def __init__(self, parent=None):
        """初始化用户协议窗口
        
        Args:
            parent: 父窗口对象
        """
        super().__init__(
            parent=parent,
            title="用户服务协议与免责声明",
            size=(800, 600)
        )
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 40, 15, 15)  # 顶部40px为标题栏留空间
        main_layout.setSpacing(10)
        
        self.create_header(main_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        main_layout.addWidget(separator)
        
        self.create_agreement_content(main_layout)
        self.create_buttons(main_layout)
        
    def create_header(self, parent_layout):
        """创建头部区域
        
        Args:
            parent_layout: 父布局对象
        """
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)
        header_layout.addWidget(logo_label)
        
        title_layout = QVBoxLayout()
        
        title_label = QLabel("用户服务协议与免责声明")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 14, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("请仔细阅读以下协议内容")
        font_manager = get_global_font_manager()
        subtitle_label.setFont(font_manager.get_source_han_font(11))
        subtitle_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_agreement_content(self, parent_layout):
        """创建协议内容区域
        
        Args:
            parent_layout: 父布局对象
        """
        self.agreement_browser = QTextBrowser()
        self.agreement_browser.setOpenExternalLinks(True)
        self.agreement_browser.setStyleSheet(UnifiedStyleHelper.get_instance().get_agreement_browser_style())
        self.agreement_browser.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        self.set_agreement_content()
        
        parent_layout.addWidget(self.agreement_browser)
    
    def create_buttons(self, parent_layout):
        """创建按钮区域
        
        Args:
            parent_layout: 父布局对象
        """
        font_manager = get_global_font_manager()
        
        button_layout = DialogFactory.create_close_button(
            parent=self,
            on_close=self.close,
            text="关闭"
        )
        
        close_button = button_layout.itemAt(1).widget()
        close_button.setFont(font_manager.get_source_han_font(10))
        
        parent_layout.addLayout(button_layout)
    
    def set_agreement_content(self):
        """设置协议内容 - 从HTML文件加载"""
        html_content = load_user_agreement_html()
        self.agreement_browser.setHtml(html_content)
    
    def refresh_theme_styles(self):
        """刷新主题样式，重新加载HTML内容以应用当前主题"""
        super().refresh_theme_styles()  # 调用基类的样式刷新
        self.set_agreement_content()  # 重新加载HTML内容
        self.agreement_browser.setStyleSheet(UnifiedStyleHelper.get_instance().get_agreement_browser_style())


class AboutWindowQt(BaseFramelessDialog):
    """关于窗口
    
    显示应用程序信息、版本信息、开发团队信息
    和相关链接。
    """
    
    manual_requested = pyqtSignal(str)
    
    def __init__(self, parent=None, version=None):
        """初始化关于窗口
        
        Args:
            parent: 父窗口对象
            version: 版本号，如果为None则从版本管理器获取
        """
        self.version = version if version is not None else get_current_version()
        super().__init__(
            parent=parent,
            title=f"关于 BetterGI 星轨",
            size=(600, 530)
        )
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 40, 15, 15)  # 顶部40px为标题栏留空间
        main_layout.setSpacing(8)
        
        self.create_header(main_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        main_layout.addWidget(separator)
        
        self.create_info_area(main_layout)
        self.create_buttons_area(main_layout)
        self.create_copyright(main_layout)
        
        self.setup_connections()
        
    def setup_connections(self):
        """设置信号连接"""
        self.dev_button.clicked.connect(lambda: self.open_url("https://space.bilibili.com/1232406878"))
        self.project_button.clicked.connect(lambda: self.open_url("https://gitee.com/qingshangongzai/BetterGI_StellTrack"))
        self.agreement_button.clicked.connect(self.show_user_agreement)
        self.manual_button.clicked.connect(self.open_manual)
        self.license_button.clicked.connect(self.open_license)
        
    def create_header(self, parent_layout):
        """创建头部区域
        
        Args:
            parent_layout: 父布局对象
        """
        header_layout = QHBoxLayout()
        
        logo_label = QLabel()
        logo_pixmap = load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)
        header_layout.addWidget(logo_label)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("BetterGI 星轨")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 24, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 0px;")
        title_layout.addWidget(title_label)
        
        english_title = QLabel("BetterGI StellTrack")
        UnifiedStyleHelper.get_instance().set_smiley_font(english_title, 12)
        english_title.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-top: 0px; margin-bottom: 0px;")
        title_layout.addWidget(english_title)
        
        version_label = QLabel(f"版本 {self.version}")
        UnifiedStyleHelper.get_instance().set_smiley_font(version_label, 10, QFont.Weight.Bold)
        version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']}; margin-top: 0px;")
        title_layout.addWidget(version_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
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
        """创建信息显示区域
        
        Args:
            parent_layout: 父布局对象
        """
        self.info_edit = QPlainTextEdit()
        self.info_edit.setReadOnly(True)
        self.info_edit.setStyleSheet(UnifiedStyleHelper.get_instance().get_info_edit_style())
        UnifiedStyleHelper.get_instance().set_source_han_font(self.info_edit, 12)
        self.info_edit.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        
        self.set_info_content()
        
        self.info_edit.setFixedHeight(300)
        
        parent_layout.addWidget(self.info_edit)
    
    def create_buttons_area(self, parent_layout):
        """创建按钮区域 - 将所有按钮排成一行并居中
        
        Args:
            parent_layout: 父布局对象
        """
        buttons_container = QWidget()
        buttons_h_layout = QHBoxLayout(buttons_container)
        buttons_h_layout.setSpacing(8)
        buttons_h_layout.setContentsMargins(0, 0, 0, 0)
        
        buttons_h_layout.addStretch()
        
        self.dev_button = self.create_action_button("个人主页")
        buttons_h_layout.addWidget(self.dev_button)
        
        self.project_button = self.create_action_button("项目地址")
        buttons_h_layout.addWidget(self.project_button)
        
        self.manual_button = self.create_action_button("使用说明")
        buttons_h_layout.addWidget(self.manual_button)
        
        self.license_button = self.create_action_button("开源许可")
        buttons_h_layout.addWidget(self.license_button)
        
        self.agreement_button = self.create_action_button("用户协议")
        buttons_h_layout.addWidget(self.agreement_button)
        
        buttons_h_layout.addStretch()
        
        parent_layout.addWidget(buttons_container)
    
    def create_action_button(self, text):
        """创建操作按钮
        
        Args:
            text (str): 按钮文本
            
        Returns:
            QPushButton: 创建的按钮对象
        """
        button = QPushButton(text)
        font_manager = get_global_font_manager()
        button.setFont(font_manager.get_source_han_font(9))
        button.setMinimumHeight(32)
        button.setMinimumWidth(90)
        button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        return button
    
    def create_copyright(self, parent_layout):
        """创建版权信息
        
        Args:
            parent_layout: 父布局对象
        """
        copyright_layout = QVBoxLayout()
        copyright_layout.setSpacing(2)
        copyright_layout.setContentsMargins(0, 5, 0, 0)
        
        copyright_text = QLabel(
            "版权所有 © 2025-2026 HXiaoStudio\n"
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
        content = """　　BetterGI 星轨（BetterGI StellTrack）是一款专为 BetterGI（一款《原神》自动化辅助工具）打造的键鼠脚本生成与管理工具，致力于生成强大的键鼠自动化脚本。本工具基于 PyQt6 开发，提供了直观的可视化界面，允许用户创建复杂的自动化操作序列。其核心初衷是实现游戏内的延时摄影——通过自动控制图片的截取和保存，创作出如电影般壮丽的视觉诗篇，是一个为你手中的"留影机"赋予生命的工具。


【注意事项】
· 使用本程序生成的自动化脚本可能违反游戏服务条款，存在账号封禁风险，请理性评估后使用；
· 严禁将本程序用于任何影响游戏公平性的场景，因此产生的一切后果由使用者自行承担。


【开发团队】
· 出品：浮晓 HXiao Studio
· 开发：青山公仔
· 代码：Deepseek、智谱清言、Trae、Qoder、CodeBuddy、通义千问
· logo 绘制：青山公仔
· 联系邮箱：hxiao_studio@163.com


【开源项目使用说明】

【字体】
  • 本程序LOGO与标题使用了「得意黑」
    版权所有：© atelier-anchor
    许可证：SIL Open Font License 1.1
    项目地址：https://github.com/atelier-anchor/smiley-sans
    官方网站：https://atelier-anchor.com/typefaces/smiley-sans/

  • 本程序默认字体使用了「思源宋体」
    版权所有：© 2014-2023 Adobe (http://www.adobe.com/)
    许可证：SIL Open Font License 1.1
    项目地址：https://github.com/adobe-fonts/source-han-serif

【核心框架】
  • 本程序基于 PyQt6 架构开发
    版权所有：Riverbank Computing Limited
    许可证：GNU General Public License v3.0 (GPL-3.0-only)
    项目地址：https://www.riverbankcomputing.com/software/pyqt/

【运行时依赖库】
  • 本程序使用 requests 库进行网络请求
    版权所有：Kenneth Reitz
    许可证：Apache License 2.0
    项目地址：https://github.com/psf/requests

  • 本程序使用 psutil 库进行系统信息获取
    版权所有：Giampaolo Rodola
    许可证：BSD 3-Clause License
    项目地址：https://github.com/giampaolo/psutil

  • 本程序使用 pywin32 库进行 Windows 系统接口调用
    版权所有：Python Software Foundation
    许可证：PSF License
    项目地址：https://github.com/mhammond/pywin32

【开发工具链】
  • 本程序使用 auto-py-to-exe 工具打包为独立的可执行文件
    版权所有：Brent Vollebregt
    许可证：MIT License
    项目地址：https://github.com/brentvollebregt/auto-py-to-exe

  • 本程序使用 UPX 工具压缩可执行文件体积
    版权所有：UPX Team
    许可证：GNU General Public License v2.0 or later (GPL-2.0+)
    官网：https://upx.github.io/

  • 本程序使用 Inno Setup 工具将独立的可执行文件打包为安装程序
    版权所有：Jordan Russell
    许可证：基于修改的 BSD 许可证 (Modified BSD)
    官网：https://jrsoftware.org/isinfo.php

【开发依赖库】
  • 本程序使用 pytest 测试框架进行单元测试
    版权所有：Holger Krekel
    许可证：MIT License
    项目地址：https://github.com/pytest-dev/pytest

  • 本程序使用 pytest-qt 插件进行 Qt 应用测试
    版权所有：Bruno Oliveira
    许可证：MIT License
    项目地址：https://github.com/pytest-dev/pytest-qt

  • 本程序使用 pytest-cov 插件进行测试覆盖率分析
    版权所有：Marc Schlaich
    许可证：MIT License
    项目地址：https://github.com/pytest-dev/pytest-cov

  • 本程序使用 flake8 工具进行代码风格检查
    版权所有：Tarek Ziade
    许可证：MIT License
    项目地址：https://github.com/pycqa/flake8

  • 本程序使用 black 工具进行代码格式化
    版权所有：Łukasz Langa
    许可证：MIT License
    项目地址：https://github.com/psf/black

  • 本程序使用 isort 工具进行导入排序
    版权所有：Timothy Crosley
    许可证：MIT License
    项目地址：https://github.com/PyCQA/isort

  • 本程序使用 mypy 工具进行静态类型检查
    版权所有：Jukka Lehtosalo
    许可证：MIT License
    项目地址：https://github.com/python/mypy

  • 本程序使用 setuptools 工具进行包管理
    版权所有：Python Packaging Authority
    许可证：MIT License
    项目地址：https://github.com/pypa/setuptools

  • 本程序使用 build 工具进行项目构建
    版权所有：Filipe Laíns
    许可证：MIT License
    项目地址：https://github.com/pypa/build

  • 本程序使用 wheel 工具进行 wheel 包构建
    版权所有：Daniel Holth
    许可证：MIT License
    项目地址：https://github.com/pypa/wheel

【特别鸣谢】
· 感谢BetterGI团队开发的原神辅助工具为玩家提供了便利。感谢BetterGI团队开发了这款优秀的原神辅助工具，为玩家提供了便利
  BetterGI团队：https://b23.tv/8rQCOI5
· 感谢得意黑与思源宋体的版权方设计的开源字体，为项目提供了精美的视觉呈现
· 感谢深度求索（Deepseek）、阿里巴巴、智谱华章（智谱清言/GML）、字节跳动、腾讯等厂商开发的AI大模型（LLM）和AI IDE工具为零代码基础人群开发程序提供了便利。"""

        self.info_edit.setPlainText(content)
    
    def open_url(self, url):
        """打开URL链接
        
        Args:
            url (str): 要打开的URL地址
        """
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
        
        self.manual_requested.emit("使用说明.pdf")
    
    def open_license(self):
        """打开开源许可"""
        license_files = ["LICENSE.html", "LICENSE", "assets/LICENSE.html"]
        
        for license_file in license_files:
            license_path = find_resource_file(license_file)
            if license_path and os.path.exists(license_path):
                QDesktopServices.openUrl(QUrl.fromLocalFile(license_path))
                return
        
        self.manual_requested.emit("LICENSE.html")
