# main_window.py

# 标准库模块导入
import sys
import os
import json
import ctypes
import time
import traceback
from datetime import datetime

# PyQt6模块导入
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
    QTableWidgetItem, QTextEdit, QFrame, QGroupBox, QGridLayout,
    QHeaderView, QScrollArea, QSizePolicy, QSplitter,
    QMessageBox, QStatusBar, QFileDialog, QDialog, QMenu, QMenuBar,
    QCheckBox
)
from PyQt6.QtGui import (
    QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor,
    QKeyEvent, QDesktopServices, QIntValidator, QAction, QActionGroup, QFontDatabase
)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QScreen

# 导入共享模块
from styles import (
    UnifiedStyleHelper, get_global_font_manager, ChineseMessageBox,
    ModernGroupBox, ModernLineEdit, ModernComboBox, ModernDoubleSpinBox,
    StyledFramelessMainWindow, StyledDialog, ModernMenuBar, FadeInWindowMixin,
    WindowIconMixin, DialogFactory
)

from utils import (
    VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP,
    convert_event_type_num_to_str_with_button, generate_key_event_name,
    load_icon_universal, load_logo, get_current_version,
    get_current_app_info, get_user_data_dir, calculate_adaptive_height
)

# 导入对话框模块
from dialogs.about_window import AboutWindowQt
from dialogs.update_dialog import UpdateDialog
from dialogs import (
    EventEditDialog, PasteOptionsDialog, SimpleCoordinateCapture,
    DeleteOptionsDialog, CustomInputDialog
)
from dialogs.debug_tools import PasswordDialog, DebugWindow, get_global_debug_logger
from dialogs.time_analysis import EventTimeAnalyzerDialog

# 导入UI模块
from ui import SettingsPanel, OperationsPanel, StatsPanel, ModernTableWidget, HeaderWidget

# 导入管理器模块
from managers import EventManager, ScriptManager, MenuManager, StateManager



class MainWindow(FadeInWindowMixin, StyledFramelessMainWindow, WindowIconMixin):
    """应用程序主窗口类

    作为应用程序的核心界面，管理所有UI组件、事件处理和功能模块。
    负责整合事件管理、脚本生成、面板显示等核心功能。

    继承关系：
    - StyledFramelessMainWindow: 提供无边框窗口基础样式和布局支持
    - WindowIconMixin: 提供窗口图标设置功能
    """

    # 主题模式切换信号（"light"、"dark"、"system"）
    theme_mode_changed = pyqtSignal(str)

    def __init__(self):
        """初始化主窗口
        
        初始化窗口属性、组件、管理器和信号槽连接。
        设置窗口标题、大小、图标和样式。
        
        主要初始化内容：
        - 核心属性和标志位
        - 撤销/重做系统
        - 调试日志记录器
        - 事件管理器和脚本管理器
        - 自动保存定时器
        - 窗口样式和布局
        """
        super().__init__()
        
        # 核心属性初始化
        self.script = None  # 存储生成的脚本
        self.copied_events = []  # 存储复制的事件
        self._table_changing = False  # 防止表格变化时的递归调用
        self.app_icon = None  # 预加载的应用图标
        
        # 时间逻辑设置初始化
        self.delete_logic = 'prompt'  # 删除事件逻辑
        self.paste_logic = 'prompt'  # 粘贴事件逻辑
        self.edit_logic = 'current'  # 编辑事件逻辑
        self.skip_end_events_prompt = True  # 末尾事件操作跳过弹窗
        self.default_time_unit = 'auto'  # 默认时间单位
        
        # 事件检查设置初始化
        self.check_pairing = True  # 检查事件成对性
        self.check_simultaneous = True  # 检查同时执行
        self.check_simultaneous_mode = 'strict'  # 同时执行检查模式（strict=严格模式，loose=宽松模式）

        # 初始化调试日志记录器
        self.debug_logger = get_global_debug_logger()
        # 初始化事件管理器和脚本管理器
        self.event_manager = EventManager(self)
        self.script_manager = ScriptManager(self)
        
        # 初始化菜单管理器
        self.menu_manager = MenuManager(self)
        
        # 初始化状态管理器
        self.state_manager = StateManager(self)

        try:
            # 获取应用程序信息
            app_info = get_current_app_info()
            version = get_current_version()

            self.setWindowTitle(f"{app_info['name']} v{version}")
            # 更新标题栏标题文本（_setup_title_bar 在 super().__init__ 中调用时 windowTitle 为空）
            self._title_label.setText(self.windowTitle())
            # 设置主窗口大小
            self.setMinimumSize(1100, 500)
            
            # 计算自适应窗口高度
            adaptive_height = calculate_adaptive_height(790, self)
            self.resize(1200, adaptive_height)

            # 居中窗口（无边框窗口不会自动居中）
            screen = QApplication.primaryScreen()
            if screen:
                geometry = screen.availableGeometry()
                x = (geometry.width() - self.width()) // 2
                y = (geometry.height() - self.height()) // 2
                self.move(x, y)

            # 设置窗口图标 - 在应用程序创建后立即设置
            self.set_window_icon()

            # 设置应用程序样式 - 纯白色背景
            self.setup_application_style()

            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 创建主布局
            main_layout = QVBoxLayout(central_widget)
            main_layout.setSpacing(4)
            # 顶部边距紧贴标题栏底部（标题栏是浮动的，不需要额外间距）
            main_layout.setContentsMargins(12, StyledFramelessMainWindow.TITLE_BAR_HEIGHT, 12, 12)

            # 创建界面
            # 菜单栏作为布局控件添加（不通过 setMenuBar，避免与浮动标题栏重叠）
            self._menu_bar_widget = self.menu_manager.create_menu_bar(use_set_menu_bar=False)
            main_layout.addWidget(self._menu_bar_widget)
            self.create_header(main_layout)
            self.create_content_area(main_layout)
            self.create_status_bar()

            # 连接信号槽
            self.connect_signals()

            # 加载时间逻辑设置
            self.menu_manager.load_time_logic_settings()

            # 加载保存的状态
            loaded_state = self.state_manager.load_saved_state()

            # 如果没有加载到事件数据，添加示例数据用于测试
            if self.event_manager.events_table.rowCount() == 0:
                self.event_manager.add_sample_data()
                self.debug_logger.log_info("未加载到事件数据，已添加示例数据")

            # 立即设置任务栏图标，不使用延迟
            self.fix_taskbar_icon()

            # 初始化统计信息和预计总时间
            self.stats_panel.update_stats()
            self.settings_panel.on_calculate_total_time()

            # 记录窗口创建成功
            self.debug_logger.log_info("主窗口初始化完成")

        except Exception as e:
            error_msg = f"主窗口初始化错误: {e}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            print(error_msg)
            traceback.print_exc()

    



    def adjust_window_size_for_dpi_change(self):
        """响应DPI变化，调整窗口大小"""
        try:
            # 获取当前窗口大小
            current_size = self.size()
            current_width = current_size.width()
            
            # 计算新的自适应高度
            new_height = calculate_adaptive_height(790, self)
            
            # 调整窗口大小，保持当前宽度
            self.resize(current_width, new_height)
            
            # 记录调试信息
            self.debug_logger.log_debug(
                f"DPI变化后调整窗口大小: 新高度={new_height}"
            )
            
        except Exception as e:
            self.debug_logger.log_error(f"DPI变化后调整窗口大小失败: {e}")

    def set_delete_logic(self, logic):
        """设置删除事件逻辑"""
        self.menu_manager.set_delete_logic(logic)



    def set_paste_logic(self, logic):
        """设置粘贴事件逻辑"""
        self.menu_manager.set_paste_logic(logic)

    def set_edit_logic(self, logic):
        """设置编辑事件逻辑"""
        self.menu_manager.set_edit_logic(logic)

    def set_skip_end_events_prompt(self, checked):
        """设置末尾事件操作是否跳过弹窗"""
        self.menu_manager.set_skip_end_events_prompt(checked)

    def get_skip_end_events_prompt(self):
        """获取末尾事件操作是否跳过弹窗的设置"""
        return getattr(self, 'skip_end_events_prompt', True)

    def update_time_logic_menu_state(self):
        """更新时间逻辑菜单的选中状态"""
        self.menu_manager.update_time_logic_menu_state()

    def get_delete_logic_display_name(self, logic):
        """获取删除逻辑的显示名称"""
        return self.menu_manager.get_delete_logic_display_name(logic)

    def get_paste_logic_display_name(self, logic):
        """获取粘贴逻辑的显示名称"""
        return self.menu_manager.get_paste_logic_display_name(logic)

    def get_edit_logic_display_name(self, logic):
        """获取编辑逻辑的显示名称"""
        return self.menu_manager.get_edit_logic_display_name(logic)

    def get_edit_logic(self):
        """获取当前编辑事件逻辑"""
        return self.menu_manager.get_edit_logic()

    def get_delete_logic(self):
        """获取当前删除事件逻辑"""
        return self.menu_manager.get_delete_logic()

    def get_paste_logic(self):
        """获取当前粘贴事件逻辑"""
        return self.menu_manager.get_paste_logic()

    def save_time_logic_settings(self):
        """保存时间逻辑设置"""
        self.menu_manager.save_time_logic_settings()

    def load_time_logic_settings(self):
        """加载时间逻辑设置"""
        self.menu_manager.load_time_logic_settings()

    def open_url(self, url):
        """打开URL链接"""
        try:
            QDesktopServices.openUrl(QUrl(url))
            self.debug_logger.log_info(f"已打开链接: {url}")
        except Exception as e:
            error_msg = f"打开链接失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", f"无法打开链接:\n{url}")

    def open_manual(self):
        """打开使用说明"""
        try:
            # 使用资源管理器查找使用说明文件
            from utils import find_resource_file
            manual_files = ["使用说明.pdf"]

            for manual_file in manual_files:
                manual_path = find_resource_file(manual_file)
                if manual_path and os.path.exists(manual_path):
                    QDesktopServices.openUrl(QUrl.fromLocalFile(manual_path))
                    self.debug_logger.log_info(f"已打开使用说明: {manual_path}")
                    return

            # 如果没有找到本地文件，提示用户
            ChineseMessageBox.show_info(self, "提示", "未找到本地使用说明文件，请查看项目文档或联系开发者")
            self.debug_logger.log_warning("未找到使用说明文件")

        except Exception as e:
            error_msg = f"打开使用说明失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def on_event_time_analysis(self):
        """打开事件时间分析对话框"""
        try:
            dialog = EventTimeAnalyzerDialog(self, self.event_manager.events_table)
            dialog.exec()
            self.debug_logger.log_info("事件时间分析对话框已打开")
        except Exception as e:
            error_msg = f"打开事件时间分析对话框失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def set_app_icon(self, icon):
        """设置应用图标
        
        Args:
            icon: 预加载的应用图标
        """
        self.app_icon = icon
        # 立即设置窗口图标，避免延迟
        self.setWindowIcon(icon)
        self.debug_logger.log_info("使用预加载图标设置窗口图标成功")
    
    def set_window_icon(self):
        """设置窗口图标"""
        try:
            # 优先使用预加载的图标，否则重新加载
            if self.app_icon:
                icon = self.app_icon
                self.debug_logger.log_info("使用预加载图标设置窗口图标")
            else:
                icon = load_icon_universal()
                self.debug_logger.log_info("重新加载图标设置窗口图标")
            
            self.setWindowIcon(icon)
        except Exception as e:
            error_msg = f"设置窗口图标失败: {e}"
            self.debug_logger.log_error(error_msg)
            print(error_msg)

    def showEvent(self, event):
        super().showEvent(event)

    def fix_taskbar_icon(self):
        """修复任务栏图标 - 在窗口显示后调用"""
        self._fix_icon_safe()

    def _initialize_theme_menu_state(self):
        """根据当前主题模式初始化菜单选中状态"""
        self.menu_manager._initialize_theme_menu_state()

    def _update_theme_action_state(self, mode: str):
        """更新主题菜单中各选项的选中状态"""
        self.menu_manager._update_theme_action_state(mode)

    def _on_theme_mode_selected(self, mode: str):
        """主题模式菜单项被选中时的处理"""
        self.menu_manager._on_theme_mode_selected(mode)

    def _refresh_theme_styles(self):
        """刷新主窗口及主要面板的样式以应用当前主题"""
        # 先调用父类的刷新（更新标题栏背景、标题颜色、按钮颜色）
        super().refresh_theme_styles()

        from styles import UnifiedStyleHelper
        helper = UnifiedStyleHelper.get_instance()

        # 状态栏样式
        if hasattr(self, "status_bar"):
            self.status_bar.setStyleSheet(helper.get_status_bar_style())
        # 时间标签
        if hasattr(self, "time_label"):
            self.time_label.setStyleSheet(f"color: {helper.COLORS['text_secondary']}; font-size: 10px; background-color: transparent;")

        # 标题栏（HeaderWidget）
        if hasattr(self, "header_widget"):
            self.header_widget.setStyleSheet(helper.get_header_widget_style())

        # 菜单栏样式
        if hasattr(self, "_menu_bar_widget") and hasattr(self._menu_bar_widget, "refresh_theme_styles"):
            self._menu_bar_widget.refresh_theme_styles()

        # 中央部件样式（大容器）
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.setStyleSheet(f"background-color: {helper.COLORS['bg']};")
            
            # 主布局中的分割器和其他容器
            for i in range(central_widget.layout().count()):
                item = central_widget.layout().itemAt(i)
                if item.widget():
                    widget = item.widget()
                    # 分割器样式
                    if hasattr(widget, "childrenCollapsible"):  # 分割器
                        widget.setStyleSheet(helper.get_splitter_style())
                        
                        # 刷新分割器中的所有子部件
                        for j in range(widget.count()):
                            splitter_widget = widget.widget(j)
                            if splitter_widget:
                                # 刷新滚动区域
                                if hasattr(splitter_widget, "widgetResizable"):  # 滚动区域
                                    splitter_widget.setStyleSheet(f"QScrollArea {{ background-color: {helper.COLORS['bg']}; border: none; }}")
                                    # 刷新滚动区域中的容器
                                    scroll_widget = splitter_widget.widget()
                                    if scroll_widget:
                                        scroll_widget.setStyleSheet(helper.get_container_bg_style())
                                # 刷新普通部件
                                else:
                                    splitter_widget.setStyleSheet(helper.get_container_bg_style())
                    else:
                        widget.setStyleSheet(f"background-color: {helper.COLORS['bg']};")

        # 设置和操作面板
        if hasattr(self, "settings_panel") and hasattr(self.settings_panel, "refresh_theme_styles"):
            self.settings_panel.refresh_theme_styles()
        if hasattr(self, "operations_panel") and hasattr(self.operations_panel, "refresh_theme_styles"):
            self.operations_panel.refresh_theme_styles()
        if hasattr(self, "stats_panel") and hasattr(self.stats_panel, "refresh_theme_styles"):
            self.stats_panel.refresh_theme_styles()
        # 事件编辑区域
        if hasattr(self, "event_manager") and hasattr(self.event_manager, "refresh_theme_styles"):
            self.event_manager.refresh_theme_styles()
        
        # 直接刷新事件表格样式，确保边框设置正确
        if hasattr(self, "event_manager") and hasattr(self.event_manager, "events_table"):
            self.event_manager.events_table.refresh_theme_styles()

    def setup_application_style(self):
        """设置应用程序样式 - 使用全局样式管理器"""
        # 使用styles模块中的UnifiedStyleHelper来统一管理应用程序样式
        from styles import UnifiedStyleHelper
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            UnifiedStyleHelper.get_instance().setup_global_style(app)
    
    def eventFilter(self, obj, event):
        """事件过滤器，处理过滤类型下拉框的回车键事件"""
        from PyQt6.QtCore import QEvent
        from PyQt6.QtGui import QKeyEvent
        
        # 检查是否是过滤类型下拉框的按键事件
        if hasattr(self, 'search_filter_widgets'):
            search_filter_widgets = self.search_filter_widgets
            if obj == search_filter_widgets['filter_combo']:
                if event.type() == QEvent.Type.KeyPress:
                    key_event = QKeyEvent(event)
                    # 检查是否是回车键
                    if key_event.key() == Qt.Key.Key_Return or key_event.key() == Qt.Key.Key_Enter:
                        # 触发搜索功能
                        search_filter_widgets['search_func']()
                        return True
        
        # 不是我们要处理的事件，交给父类处理
        return super().eventFilter(obj, event)

    def create_header(self, parent_layout):
        """创建窗口顶部标题和信息区域

        在指定的父布局中创建应用程序的头部区域，
        包含应用名称、版本信息和操作按钮等。

        Args:
            parent_layout: 父布局对象，用于放置头部组件
        """
        self.header_widget = HeaderWidget()
        parent_layout.addWidget(self.header_widget)

    def create_content_area(self, parent_layout):
        """创建内容区域"""
        # 创建水平分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(0)
        splitter.setStyleSheet(UnifiedStyleHelper.get_instance().get_splitter_style())

        # 左侧设置面板
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)

        # 右侧区域（包含事件编辑和统计信息）
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)

        # 设置分割比例，使用相对比例而非固定数值
        # 总宽度会根据窗口大小自动调整
        parent_layout.addWidget(splitter, 1)

    def create_left_panel(self):
        """创建左侧设置面板"""
        from PyQt6.QtWidgets import QScrollArea

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(250)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        container = QWidget()
        container.setMinimumWidth(250)
        container.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        container.setStyleSheet(UnifiedStyleHelper.get_instance().get_container_bg_style())

        layout = QVBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # 创建设置面板实例，传递主窗口引用
        self.settings_panel = SettingsPanel(self)
        layout.addWidget(self.settings_panel)

        # 创建操作面板实例，传递主窗口引用
        self.operations_panel = OperationsPanel(self)
        layout.addWidget(self.operations_panel)

        layout.addStretch()

        scroll_area.setWidget(container)
        return scroll_area

    def create_right_panel(self):
        """创建右侧面板（包含事件编辑和统计信息）"""
        container = QWidget()
        container.setStyleSheet(UnifiedStyleHelper.get_instance().get_container_bg_style())

        # 使用水平布局，左边是事件编辑，右边是统计信息
        layout = QHBoxLayout(container)
        layout.setSpacing(12)
        layout.setContentsMargins(8, 8, 8, 8)

        # 事件编辑区域（占据大部分空间）
        event_editor = self.create_event_editor()
        layout.addWidget(event_editor, 4)  # 权重为4

        # 统计信息面板（占据较小空间，放在最右边）
        self.stats_panel = StatsPanel(self)
        layout.addWidget(self.stats_panel, 1)  # 权重为1

        return container

    def create_event_editor(self, parent=None):
        """创建事件编辑器 - 调用事件管理器"""
        return self.event_manager.create_event_editor(parent)

    def create_status_bar(self):
        """创建状态栏 - 修复灰白不一致问题"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # 修复状态栏样式 - 纯白色背景
        self.status_bar.setStyleSheet(UnifiedStyleHelper.get_instance().get_status_bar_style())
        self.status_bar.showMessage("✅ 就绪")

        # 添加时间显示
        self.time_label = QLabel()
        self.time_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; background-color: transparent;")
        self.status_bar.addPermanentWidget(self.time_label)

        # 更新时间
        self.update_time()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

        # 更新快捷键提示，包含新的快捷键
        shortcuts_label = QLabel("快捷键: Ctrl+Z撤销 | Ctrl+Y重做 | Ctrl+I添加事件 | Ctrl+E编辑事件 | Ctrl+B批量编辑 | Ctrl+A全选 | Ctrl+X剪切 | Ctrl+C复制 | Ctrl+V粘贴 | Delete删除 | Ctrl+S保存")
        shortcuts_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 9px; margin-right: 10px; background-color: transparent;")
        self.status_bar.addPermanentWidget(shortcuts_label)

    def update_time(self):
        """更新时间显示"""
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss")
        self.time_label.setText(f"🕒 {current_time}")

    def connect_signals(self):
        """连接信号槽"""
        # 操作按钮信号 - 修改为调用面板的方法
        self.operations_panel.generate_btn.clicked.connect(self.script_manager.on_generate_script)
        self.operations_panel.save_btn.clicked.connect(self.script_manager.on_save_script)
        self.operations_panel.preview_btn.clicked.connect(self.operations_panel.on_preview_script)
        self.operations_panel.import_script_btn.clicked.connect(self.script_manager.on_import_script)

        # 设置面板信号 - 修改为调用面板的方法
        self.settings_panel.detect_screen_btn.clicked.connect(self.settings_panel.on_detect_screen_info)

        # 循环设置更改时同时更新设置面板的总时间和统计面板的信息
        self.settings_panel.loop_count_input.valueChanged.connect(self.on_loop_settings_changed)
        self.settings_panel.interval_input_double.valueChanged.connect(self.on_loop_settings_changed)
        self.settings_panel.interval_input_int.valueChanged.connect(self.on_loop_settings_changed)
        self.settings_panel.time_unit_combo.currentTextChanged.connect(self.on_loop_settings_changed)

    def on_loop_settings_changed(self):
        """循环设置更改时的处理函数

        当循环次数、间隔时间或时间单位更改时，同时更新：
        1. 设置面板中的预计总时间
        2. 统计面板中的统计信息
        """
        # 更新设置面板的总时间
        self.settings_panel.on_calculate_total_time()

        # 更新统计面板的信息
        if hasattr(self, 'stats_panel'):
            self.stats_panel.update_stats()

    def on_new_file(self):
        """新建文件 - 调用状态管理器"""
        self.state_manager.on_new_file()

    def on_undo(self):
        """撤销操作 - 调用状态管理器"""
        self.state_manager.on_undo()

    def on_redo(self):
        """重做操作 - 调用状态管理器"""
        self.state_manager.on_redo()

    def on_add_event(self):
        """添加事件 - 调用事件管理器"""
        self.event_manager.on_add_event()

    def on_edit_event(self):
        """编辑事件 - 调用事件管理器"""
        self.event_manager.on_edit_event()

    def on_delete_event(self):
        """删除事件 - 调用事件管理器"""
        self.event_manager.on_delete_event()

    def on_copy_event(self):
        """复制事件 - 调用事件管理器"""
        self.event_manager.on_copy_event()

    def on_cut_event(self):
        """剪切事件 - 调用事件管理器"""
        self.event_manager.on_cut_event()

    def on_paste_event(self):
        """粘贴事件 - 调用事件管理器"""
        self.event_manager.on_paste_event()

    def on_select_all_events(self):
        """全选事件 - 调用事件管理器"""
        self.event_manager.on_select_all_events()

    def on_open_debug_tool(self):
        """打开调试工具"""
        try:
            dialog = CustomInputDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                if dialog.result == "password":
                    # 密码正确，打开调试窗口
                    debug_window = DebugWindow(self)
                    debug_window.show()
                    self.debug_logger.log_info("调试工具已打开")
                elif dialog.result == "easter_egg":
                    # 彩蛋触发，已经在对话框中处理
                    pass
        except Exception as e:
            error_msg = f"打开调试工具失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def on_about(self):
        """打开关于窗口"""
        try:
            about_window = AboutWindowQt(self)
            about_window.show()
        except Exception as e:
            error_msg = f"打开关于窗口失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def on_user_agreement(self):
        """用户协议"""
        self.debug_logger.log_info("打开用户协议窗口")
        from dialogs.about_window import UserAgreementWindow
        agreement_window = UserAgreementWindow(self)
        agreement_window.show()

    def on_check_update(self):
        """检查更新"""
        try:
            self.debug_logger.log_info("打开检查更新对话框")
            update_dialog = UpdateDialog(self)
            update_dialog.show()
        except Exception as e:
            error_msg = f"打开检查更新对话框失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)

    def on_search_filter_changed(self):
        """搜索过滤条件改变时调用"""
        self.event_manager.on_search_filter_changed()

    def on_reset_search_filter(self):
        """重置搜索过滤条件"""
        self.event_manager.on_reset_search_filter()

    def on_batch_edit(self):
        """批量编辑事件"""
        self.event_manager.on_batch_edit()

    def closeEvent(self, event):
        """关闭事件 - 确保状态保存"""
        self.debug_logger.log_info("主窗口关闭中...")
        # 保存当前状态到文件
        self.state_manager.save_saved_state()
        self.debug_logger.log_info("程序正常关闭")
        event.accept()


# =============================================================================

# 主程序入口

# =============================================================================


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())