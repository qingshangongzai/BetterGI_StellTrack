# 标准库模块导入
# 无标准库模块导入

# 第三方模块导入
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QFrame, QHBoxLayout, QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout

# 项目模块导入
from styles import UnifiedStyleHelper, get_global_font_manager
from utils import get_current_app_info, get_current_version, load_logo


class ModernTableWidget(QTableWidget):
    """现代化的表格控件

    提供统一的表格样式和交互行为，支持：
    - 自定义表格样式
    - 行选择模式
    - 自定义右键菜单
    - 主题切换支持

    Args:
        rows (int): 表格行数
        columns (int): 表格列数
        parent: 父窗口组件
    """

    def __init__(self, rows=0, columns=0, parent=None):
        """初始化现代化表格控件

        Args:
            rows (int): 表格行数，默认为0
            columns (int): 表格列数，默认为0
            parent: 父窗口组件，默认为None
        """
        super().__init__(rows, columns, parent)
        self.setup_ui()

    def setup_ui(self):
        """设置表格控件的UI属性"""
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_table_style())

        self.setAlternatingRowColors(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)

        self.horizontalHeader().setDefaultSectionSize(24)
        self.verticalHeader().setDefaultSectionSize(30)
        self.verticalHeader().setVisible(False)

        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def refresh_theme_styles(self):
        """刷新表格的样式，应用当前主题"""
        helper = UnifiedStyleHelper.get_instance()
        self.setStyleSheet(helper.get_table_style())


class HeaderWidget(QFrame):
    """自定义标题栏

    显示应用程序的Logo、主标题、副标题和标语。
    支持主题切换和Logo加载。

    Args:
        parent: 父窗口组件
    """

    def __init__(self, parent=None):
        """初始化自定义标题栏

        Args:
            parent: 父窗口组件，默认为None
        """
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """设置标题栏的UI布局和组件"""
        self.setFixedHeight(80)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_header_widget_style())

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 10)

        title_layout = QHBoxLayout()

        self.logo_label = QLabel()
        self.logo_label.setFixedSize(50, 50)
        self.load_logo()

        title_layout.addWidget(self.logo_label)

        title_text_layout = QVBoxLayout()

        font_manager = get_global_font_manager()
        app_info = get_current_app_info()
        version = get_current_version()

        main_title = QLabel(app_info["name"])
        UnifiedStyleHelper.get_instance().set_smiley_font(main_title, 24, QFont.Weight.Bold)
        main_title.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_text_layout.addWidget(main_title)

        subtitle = QLabel(app_info["name_en"])
        UnifiedStyleHelper.get_instance().set_smiley_font(subtitle, 12)
        subtitle.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_text_layout.addWidget(subtitle)

        title_layout.addLayout(title_text_layout)
        title_layout.addStretch()

        slogan_label = QLabel("风带来故事的种子，时间使之发芽")
        slogan_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_slogan_label_style())
        title_layout.addWidget(slogan_label)

        layout.addLayout(title_layout)

    def load_logo(self):
        """加载Logo图片"""
        try:
            pixmap = load_logo((50, 50))
            if pixmap is not None:
                self.logo_label.setPixmap(pixmap)
            else:
                self.set_fallback_logo()
        except Exception as e:
            print(f"加载Logo失败: {e}")
            self.set_fallback_logo()

    def set_fallback_logo(self):
        """设置备用Logo"""
        self.logo_label.setText("🌌")
        self.logo_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_logo_label_style())
        self.logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
