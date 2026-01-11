from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QFrame, QLabel, QHBoxLayout, QVBoxLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from styles import UnifiedStyleHelper, get_global_font_manager
from utils import load_logo, get_current_app_info, get_current_version


class ModernTableWidget(QTableWidget):

    """现代化的表格控件"""

    def __init__(self, rows=0, columns=0, parent=None):

        super().__init__(rows, columns, parent)

        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_table_style())

        # 设置表格属性

        self.setAlternatingRowColors(False)

        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)

        self.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        # 调整表头行高
        self.horizontalHeader().setDefaultSectionSize(24)

        # 设置行高

        self.verticalHeader().setDefaultSectionSize(30)

        self.verticalHeader().setVisible(False)

        # 设置右键菜单策略
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        
        # 设置表头右键菜单策略
        self.horizontalHeader().setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

    def refresh_theme_styles(self):
        """刷新表格的样式，应用当前主题"""
        helper = UnifiedStyleHelper.get_instance()
        self.setStyleSheet(helper.get_table_style())



class HeaderWidget(QFrame):

    """自定义标题栏"""

    def __init__(self, parent=None):

        super().__init__(parent)

        self.setFixedHeight(80)

        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_header_widget_style())

        layout = QHBoxLayout(self)

        layout.setContentsMargins(20, 10, 20, 10)

        # Logo和标题

        title_layout = QHBoxLayout()

        # Logo - 尝试加载图片

        self.logo_label = QLabel()

        self.logo_label.setFixedSize(50, 50)

        self.load_logo()

        title_layout.addWidget(self.logo_label)

        # 标题区域 - 修改为垂直布局以显示主标题和副标题

        title_text_layout = QVBoxLayout()

        # 获取字体管理器

        font_manager = get_global_font_manager()

        # 获取版本信息

        app_info = get_current_app_info()

        version = get_current_version()

        # 主标题 - 使用得意黑字体

        main_title = QLabel(app_info["name"])

        UnifiedStyleHelper.get_instance().set_smiley_font(main_title, 24, QFont.Weight.Bold)

        main_title.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")

        title_text_layout.addWidget(main_title)

        # 副标题 - 英文名 - 使用得意黑字体

        subtitle = QLabel(app_info["name_en"])

        UnifiedStyleHelper.get_instance().set_smiley_font(subtitle, 12)

        subtitle.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")

        title_text_layout.addWidget(subtitle)

        title_layout.addLayout(title_text_layout)

        title_layout.addStretch()

        # 移除版本信息和关于按钮，替换为标语

        slogan_label = QLabel("风带来故事的种子，时间使之发芽")

        slogan_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_slogan_label_style())

        title_layout.addWidget(slogan_label)

        layout.addLayout(title_layout)

    def load_logo(self):

        """加载Logo图片"""

        try:

            # 使用统一的Logo加载函数

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
