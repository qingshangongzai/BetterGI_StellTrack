# main_window.py

import sys
import os
import json
import ctypes
import time
from datetime import datetime

from PyQt6.QtWidgets import (
                            QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget,
                            QTableWidgetItem, QTextEdit, QFrame, QGroupBox, QGridLayout,
                            QHeaderView, QScrollArea, QSizePolicy, QSplitter,
                            QMessageBox, QStatusBar, QFileDialog, QDialog, QMenu, QMenuBar,
                            QCheckBox)

from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize

from PyQt6.QtGui import (QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor,
                        QKeyEvent, QDesktopServices, QIntValidator, QAction, QActionGroup, QFontDatabase)


# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager, ChineseMessageBox, ModernGroupBox, ModernLineEdit, ModernComboBox, ModernDoubleSpinBox, StyledMainWindow, StyledDialog, ModernMenuBar, FadeInWindowMixin

from styles import WindowIconMixin, DialogFactory

from utils import VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP, convert_event_type_num_to_str_with_button, generate_key_event_name, load_icon_universal, load_logo, get_current_version, get_current_app_info, get_user_data_dir

# 导入关于窗口模块


from about_window import AboutWindowQt

# 导入更新对话框模块


from update_dialog import UpdateDialog

# 导入事件对话框模块


from event_dialogs import EventEditDialog, PasteOptionsDialog, SimpleCoordinateCapture, DeleteOptionsDialog

# 导入调试工具模块
from debug_tools import PasswordDialog, DebugWindow, get_global_debug_logger
from debug_dialog import CustomInputDialog

# 导入新拆分的模块


from panels import SettingsPanel, OperationsPanel, StatsPanel
from event_manager import EventManager
from script_manager import ScriptManager

from widgets import ModernTableWidget, HeaderWidget

from time_analysis import EventTimeAnalyzerDialog



class MainWindow(FadeInWindowMixin, StyledMainWindow, WindowIconMixin):
    """应用程序主窗口类
    
    作为应用程序的核心界面，管理所有UI组件、事件处理和功能模块。
    负责整合事件管理、脚本生成、面板显示等核心功能。
    
    继承关系：
    - StyledMainWindow: 提供基础样式和布局支持
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
        self.undo_stack = []  # 撤销栈
        self.redo_stack = []  # 重做栈
        self.max_undo_steps = 50  # 最大撤销步骤数
        self._table_changing = False  # 防止表格变化时的递归调用
        self._batch_operation = False  # 批量操作标志
        self.app_icon = None  # 预加载的应用图标
        
        # 时间逻辑设置初始化
        self.delete_logic = 'prompt'  # 删除事件逻辑
        self.paste_logic = 'prompt'  # 粘贴事件逻辑
        self.edit_logic = 'current'  # 编辑事件逻辑
        self.skip_end_events_prompt = True  # 末尾事件操作跳过弹窗

        

        # 撤销延迟保存相关

        self._undo_save_timer = QTimer()

        self._undo_save_timer.setSingleShot(True)

        self._undo_save_timer.setInterval(500)  # 500ms延迟

        self._undo_save_timer.timeout.connect(self._delayed_save_state)

        self._pending_undo_save = False

        

        # 初始化调试日志记录器
        self.debug_logger = get_global_debug_logger()
        # 初始化事件管理器和脚本管理器
        self.event_manager = EventManager(self)
        self.script_manager = ScriptManager(self)
        
        # 初始化自动保存定时器
        self.auto_save_timer = QTimer()
        self.auto_save_timer.setInterval(30000)  # 30秒自动保存一次
        self.auto_save_timer.timeout.connect(self.save_saved_state)
        self.auto_save_timer.start()

        

        try:

            # 获取应用程序信息

            app_info = get_current_app_info()

            version = get_current_version()

            

            # 设置窗口标志为标准主窗口样式，允许移动和调整大小

            self.setWindowFlags(Qt.WindowType.Window)

            

            self.setWindowTitle(f"{app_info['name']} v{version}")
            # 设置主窗口大小
            self.setMinimumSize(1100, 500)
            self.resize(1200, 790)

            

            # 设置窗口图标 - 在应用程序创建后立即设置

            self.set_window_icon()

            

            # 设置应用程序样式 - 纯白色背景

            self.setup_application_style()

            

            # 创建中央部件

            central_widget = QWidget()

            self.setCentralWidget(central_widget)

            

            # 创建主布局

            main_layout = QVBoxLayout(central_widget)

            main_layout.setSpacing(8)

            main_layout.setContentsMargins(12, 12, 12, 12)

            

            # 创建界面

            self.create_menu_bar()

            self.create_header(main_layout)

            self.create_content_area(main_layout)

            self.create_status_bar()

            

            # 连接信号槽

            self.connect_signals()

            

            # 加载时间逻辑设置

            self.load_time_logic_settings()

            

            # 加载保存的状态

            # 加载保存的状态
            loaded_state = self.load_saved_state()

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

            import traceback

            traceback.print_exc()

    

    def create_menu_bar(self):
        """创建应用程序菜单栏
        
        构建包含文件、编辑、工具、设置和帮助等菜单的菜单栏，
        并为每个菜单项连接相应的操作。
        
        使用 ModernMenuBar 以修复 Windows 系统下菜单圆角显示问题。
        """

        # 创建现代化菜单栏，自动为所有菜单应用无边框样式
        menubar = ModernMenuBar(self)
        self.setMenuBar(menubar)

        

        # 文件菜单

        file_menu = menubar.addMenu('文件')

        

        # 新建

        new_action = QAction('新建', self)

        new_action.setShortcut('Ctrl+N')

        new_action.triggered.connect(self.on_new_file)

        file_menu.addAction(new_action)

        

        # 打开

        open_action = QAction('打开', self)

        open_action.setShortcut('Ctrl+O')

        open_action.triggered.connect(self.script_manager.on_import_script)

        file_menu.addAction(open_action)

        

        # 保存

        save_action = QAction('保存', self)

        save_action.setShortcut('Ctrl+S')

        save_action.triggered.connect(self.script_manager.on_save_script)

        file_menu.addAction(save_action)

        

        file_menu.addSeparator()

        

        # 退出

        exit_action = QAction('退出', self)

        exit_action.setShortcut('Ctrl+Q')

        exit_action.triggered.connect(self.close)

        file_menu.addAction(exit_action)

        

        # 编辑菜单

        edit_menu = menubar.addMenu('编辑')

        

        # 撤销

        undo_action = QAction('撤销', self)

        undo_action.setShortcut('Ctrl+Z')

        undo_action.triggered.connect(self.on_undo)

        edit_menu.addAction(undo_action)

        

        # 重做

        redo_action = QAction('重做', self)

        redo_action.setShortcut('Ctrl+Y')

        redo_action.triggered.connect(self.on_redo)

        edit_menu.addAction(redo_action)

        

        edit_menu.addSeparator()

        

        # 添加事件

        add_action = QAction('添加事件', self)

        add_action.setShortcut('Ctrl+I')

        add_action.triggered.connect(self.event_manager.on_add_event)

        edit_menu.addAction(add_action)
        
        # 编辑事件

        edit_action = QAction('编辑事件', self)

        edit_action.setShortcut('Ctrl+E')

        edit_action.triggered.connect(self.event_manager.on_edit_event)

        edit_menu.addAction(edit_action)
        
        edit_menu.addSeparator()
        
        # 剪切

        cut_action = QAction('剪切', self)

        cut_action.setShortcut('Ctrl+X')

        cut_action.triggered.connect(self.event_manager.on_cut_event)

        edit_menu.addAction(cut_action)

        

        # 复制

        copy_action = QAction('复制', self)

        copy_action.setShortcut('Ctrl+C')

        copy_action.triggered.connect(self.event_manager.on_copy_event)

        edit_menu.addAction(copy_action)

        

        # 粘贴

        paste_action = QAction('粘贴', self)

        paste_action.setShortcut('Ctrl+V')

        paste_action.triggered.connect(self.event_manager.on_paste_event)

        edit_menu.addAction(paste_action)

        

        edit_menu.addSeparator()

        

        # 删除

        delete_action = QAction('删除', self)

        delete_action.setShortcut('Delete')

        delete_action.triggered.connect(self.event_manager.on_delete_event)

        edit_menu.addAction(delete_action)

        

        # 全选

        select_all_action = QAction('全选', self)

        select_all_action.setShortcut('Ctrl+A')

        select_all_action.triggered.connect(self.event_manager.on_select_all_events)

        edit_menu.addAction(select_all_action)
        
        # 批量编辑

        batch_edit_action = QAction('批量编辑', self)

        batch_edit_action.setShortcut('Ctrl+B')

        batch_edit_action.triggered.connect(self.event_manager.on_batch_edit)

        edit_menu.addAction(batch_edit_action)

        

        # 新增：时间逻辑菜单

        time_logic_menu = menubar.addMenu('时间逻辑')

        

        # 删除事件逻辑子菜单

        delete_logic_menu = time_logic_menu.addMenu('删除事件逻辑')

        

        # 删除事件逻辑选项

        delete_prompt_action = QAction('每次弹出提示选择', self)

        delete_prompt_action.setCheckable(True)

        delete_prompt_action.triggered.connect(lambda: self.set_delete_logic('prompt'))

        delete_logic_menu.addAction(delete_prompt_action)

        

        delete_current_action = QAction('默认：仅修改当前事件时间', self)

        delete_current_action.setCheckable(True)

        delete_current_action.triggered.connect(lambda: self.set_delete_logic('current'))

        delete_logic_menu.addAction(delete_current_action)

        

        delete_recalculate_action = QAction('默认：重新计算后续事件时间', self)

        delete_recalculate_action.setCheckable(True)

        delete_recalculate_action.triggered.connect(lambda: self.set_delete_logic('recalculate'))

        delete_logic_menu.addAction(delete_recalculate_action)

        

        # 粘贴事件逻辑子菜单

        paste_logic_menu = time_logic_menu.addMenu('粘贴事件逻辑')

        

        # 粘贴事件逻辑选项

        paste_prompt_action = QAction('每次弹出提示选择', self)

        paste_prompt_action.setCheckable(True)

        paste_prompt_action.triggered.connect(lambda: self.set_paste_logic('prompt'))

        paste_logic_menu.addAction(paste_prompt_action)

        

        paste_current_action = QAction('默认：仅修改当前事件时间', self)

        paste_current_action.setCheckable(True)

        paste_current_action.triggered.connect(lambda: self.set_paste_logic('current'))

        paste_logic_menu.addAction(paste_current_action)

        

        paste_recalculate_action = QAction('默认：重新计算后续事件时间', self)

        paste_recalculate_action.setCheckable(True)

        paste_recalculate_action.triggered.connect(lambda: self.set_paste_logic('recalculate'))

        paste_logic_menu.addAction(paste_recalculate_action)
        
        # 编辑事件逻辑子菜单
        edit_logic_menu = time_logic_menu.addMenu('编辑事件逻辑')
        
        # 编辑事件逻辑选项
        edit_current_action = QAction('默认：仅修改当前事件时间', self)
        edit_current_action.setCheckable(True)
        edit_current_action.triggered.connect(lambda: self.set_edit_logic('current'))
        edit_logic_menu.addAction(edit_current_action)
        
        edit_recalculate_action = QAction('默认：重新计算后续事件时间', self)
        edit_recalculate_action.setCheckable(True)
        edit_recalculate_action.triggered.connect(lambda: self.set_edit_logic('recalculate'))
        edit_logic_menu.addAction(edit_recalculate_action)
        
        # 末尾事件操作跳过弹窗开关
        skip_end_events_action = QAction('末尾事件操作跳过弹窗', self)
        skip_end_events_action.setCheckable(True)
        skip_end_events_action.setChecked(True)  # 默认开启
        skip_end_events_action.triggered.connect(self.set_skip_end_events_prompt)
        time_logic_menu.addAction(skip_end_events_action)
        
        # 保存末尾事件开关的引用
        self.skip_end_events_action = skip_end_events_action

        

        # 保存菜单项引用，用于更新选中状态

        self.delete_logic_actions = {

            'prompt': delete_prompt_action,

            'current': delete_current_action,

            'recalculate': delete_recalculate_action

        }

        

        self.paste_logic_actions = {
            'prompt': paste_prompt_action,
            'current': paste_current_action,
            'recalculate': paste_recalculate_action
        }
        
        self.edit_logic_actions = {
            'current': edit_current_action,
            'recalculate': edit_recalculate_action
        }
        
        # 分析菜单

        # 工具菜单

        # 主题菜单
        theme_menu = menubar.addMenu('主题')

        # 主题模式动作组（互斥）
        self.theme_action_group = QActionGroup(self)
        self.theme_action_group.setExclusive(True)

        # 浅色主题
        self.theme_light_action = QAction('浅色主题', self)
        self.theme_light_action.setCheckable(True)
        self.theme_light_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('light'))
        self.theme_action_group.addAction(self.theme_light_action)
        theme_menu.addAction(self.theme_light_action)

        # 深色主题
        self.theme_dark_action = QAction('深色主题', self)
        self.theme_dark_action.setCheckable(True)
        self.theme_dark_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('dark'))
        self.theme_action_group.addAction(self.theme_dark_action)
        theme_menu.addAction(self.theme_dark_action)

        # 跟随系统
        self.theme_system_action = QAction('跟随系统', self)
        self.theme_system_action.setCheckable(True)
        self.theme_system_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('system'))
        self.theme_action_group.addAction(self.theme_system_action)
        theme_menu.addAction(self.theme_system_action)

        # 根据当前主题模式初始化选中状态
        self._initialize_theme_menu_state()

        tools_menu = menubar.addMenu('工具')

        

        # 事件时间分析工具

        time_analysis_action = QAction('事件时间分析', self)

        time_analysis_action.setShortcut('Ctrl+T')

        time_analysis_action.triggered.connect(self.on_event_time_analysis)

        tools_menu.addAction(time_analysis_action)

        

        # 添加分隔线

        tools_menu.addSeparator()

        

        # 调试工具

        debug_action = QAction('调试工具', self)

        debug_action.setShortcut('Ctrl+D')

        debug_action.triggered.connect(self.on_open_debug_tool)

        tools_menu.addAction(debug_action)

        

        # 帮助菜单 - 增加链接

        help_menu = menubar.addMenu('帮助')

        

        # 个人主页

        homepage_action = QAction('个人主页', self)

        homepage_action.triggered.connect(lambda: self.open_url("https://b23.tv/KO3m8zU"))

        help_menu.addAction(homepage_action)

        

        # 项目地址

        project_action = QAction('项目地址', self)

        project_action.triggered.connect(lambda: self.open_url("https://gitee.com/qingshangongzai/BetterGI_StellTrack"))

        help_menu.addAction(project_action)

        

        # 使用说明

        manual_action = QAction('使用说明', self)

        manual_action.triggered.connect(self.open_manual)

        help_menu.addAction(manual_action)

        

        help_menu.addSeparator()

        

        # 检查更新

        check_update_action = QAction('检查更新', self)

        check_update_action.triggered.connect(self.on_check_update)

        help_menu.addAction(check_update_action)

        

        help_menu.addSeparator()

        

        # 关于

        about_action = QAction('关于', self)

        about_action.triggered.connect(self.on_about)

        help_menu.addAction(about_action)

        

        # 用户协议

        agreement_action = QAction('用户协议', self)

        agreement_action.triggered.connect(self.on_user_agreement)

        help_menu.addAction(agreement_action)

        

        # 初始化菜单状态

        self.update_time_logic_menu_state()

    

    def set_delete_logic(self, logic):

        """设置删除事件逻辑"""

        self.delete_logic = logic

        self.update_time_logic_menu_state()

        self.save_time_logic_settings()

        self.status_bar.showMessage(f"✅ 删除事件逻辑已设置为: {self.get_delete_logic_display_name(logic)}")

        self.debug_logger.log_info(f"删除事件逻辑设置为: {logic}")



    def set_paste_logic(self, logic):
        """设置粘贴事件逻辑"""
        self.paste_logic = logic
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.status_bar.showMessage(f"✅ 粘贴事件逻辑已设置为: {self.get_paste_logic_display_name(logic)}")
        self.debug_logger.log_info(f"粘贴事件逻辑设置为: {logic}")

    def set_edit_logic(self, logic):
        """设置编辑事件逻辑"""
        self.edit_logic = logic
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.status_bar.showMessage(f"✅ 编辑事件逻辑已设置为: {self.get_edit_logic_display_name(logic)}")
        self.debug_logger.log_info(f"编辑事件逻辑设置为: {logic}")

    def set_skip_end_events_prompt(self, checked):
        """设置末尾事件操作是否跳过弹窗"""
        self.skip_end_events_prompt = checked
        self.save_time_logic_settings()
        status = "开启" if checked else "关闭"
        self.status_bar.showMessage(f"✅ 末尾事件操作跳过弹窗已{status}")
        self.debug_logger.log_info(f"末尾事件操作跳过弹窗已设置为: {checked}")

    def get_skip_end_events_prompt(self):
        """获取末尾事件操作是否跳过弹窗的设置"""
        return getattr(self, 'skip_end_events_prompt', True)

    def update_time_logic_menu_state(self):
        """更新时间逻辑菜单的选中状态"""
        # 更新删除逻辑菜单状态
        if hasattr(self, 'delete_logic_actions'):
            for logic, action in self.delete_logic_actions.items():
                action.setChecked(getattr(self, 'delete_logic', 'prompt') == logic)
        
        # 更新粘贴逻辑菜单状态
        if hasattr(self, 'paste_logic_actions'):
            for logic, action in self.paste_logic_actions.items():
                action.setChecked(getattr(self, 'paste_logic', 'prompt') == logic)
        
        # 更新编辑逻辑菜单状态
        if hasattr(self, 'edit_logic_actions'):
            for logic, action in self.edit_logic_actions.items():
                action.setChecked(getattr(self, 'edit_logic', 'current') == logic)
        
        # 更新末尾事件操作跳过弹窗开关状态
        if hasattr(self, 'skip_end_events_action'):
            self.skip_end_events_action.setChecked(self.get_skip_end_events_prompt())

    def get_delete_logic_display_name(self, logic):

        """获取删除逻辑的显示名称"""

        names = {

            'prompt': '每次弹出提示选择',

            'current': '仅修改当前事件时间',

            'recalculate': '重新计算后续事件时间'

        }

        return names.get(logic, '每次弹出提示选择')



    def get_paste_logic_display_name(self, logic):
        """获取粘贴逻辑的显示名称"""
        names = {
            'prompt': '每次弹出提示选择',
            'current': '仅修改当前事件时间',
            'recalculate': '重新计算后续事件时间'
        }
        return names.get(logic, '每次弹出提示选择')

    def get_edit_logic_display_name(self, logic):
        """获取编辑逻辑的显示名称"""
        names = {
            'current': '仅修改当前事件时间',
            'recalculate': '重新计算后续事件时间'
        }
        return names.get(logic, '仅修改当前事件时间')

    def get_edit_logic(self):
        """获取当前编辑事件逻辑"""
        return getattr(self, 'edit_logic', 'current')

    def get_delete_logic(self):

        """获取当前删除事件逻辑"""

        return getattr(self, 'delete_logic', 'prompt')



    def get_paste_logic(self):

        """获取当前粘贴事件逻辑"""

        return getattr(self, 'paste_logic', 'prompt')



    def save_time_logic_settings(self):

        """保存时间逻辑设置"""

        try:

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 设置文件路径

            settings_file = os.path.join(app_dir, "BetterGI_StellTrack_settings.json")

            

            # 读取现有设置

            settings = {}

            if os.path.exists(settings_file):

                try:

                    with open(settings_file, 'r', encoding='utf-8') as f:

                        settings = json.load(f)

                except:

                    settings = {}

            

            # 更新时间逻辑设置
            settings['delete_logic'] = self.get_delete_logic()
            settings['paste_logic'] = self.get_paste_logic()
            settings['edit_logic'] = self.get_edit_logic()
            settings['skip_end_events_prompt'] = self.get_skip_end_events_prompt()
            
            # 保存设置
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            
            self.debug_logger.log_info(f"时间逻辑设置已保存: 删除={self.delete_logic}, 粘贴={self.paste_logic}, 编辑={self.edit_logic}")

        except Exception as e:

            self.debug_logger.log_error(f"保存时间逻辑设置失败: {e}")



    def load_time_logic_settings(self):

        """加载时间逻辑设置"""

        try:

            # 获取程序所在目录

            if getattr(sys, 'frozen', False):

                app_dir = os.path.dirname(sys.executable)

            else:

                app_dir = os.path.dirname(os.path.abspath(__file__))

            

            # 设置文件路径

            settings_file = os.path.join(app_dir, "BetterGI_StellTrack_settings.json")

            

            if os.path.exists(settings_file):

                with open(settings_file, 'r', encoding='utf-8') as f:

                    settings = json.load(f)

                

                # 加载时间逻辑设置
                self.delete_logic = settings.get('delete_logic', 'prompt')
                self.paste_logic = settings.get('paste_logic', 'prompt')
                self.edit_logic = settings.get('edit_logic', 'current')
                self.skip_end_events_prompt = settings.get('skip_end_events_prompt', True)
                
                # 更新菜单状态
                self.update_time_logic_menu_state()
                
                self.debug_logger.log_info(f"时间逻辑设置已加载: 删除={self.delete_logic}, 粘贴={self.paste_logic}, 编辑={self.edit_logic}, 跳过末尾事件弹窗={self.skip_end_events_prompt}")
                return True
            else:
                # 设置默认值
                self.delete_logic = 'prompt'
                self.paste_logic = 'prompt'
                self.edit_logic = 'current'
                self.skip_end_events_prompt = True
                self.debug_logger.log_info("使用默认时间逻辑设置")
                return True
            
        except Exception as e:
            self.debug_logger.log_error(f"加载时间逻辑设置失败: {e}")
            # 设置默认值
            self.delete_logic = 'prompt'
            self.paste_logic = 'prompt'
            self.edit_logic = 'current'
            self.skip_end_events_prompt = True
            return False

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

        """主窗口显示事件 - 首次显示时触发淡入动画"""
        if not hasattr(self, "_main_first_show_done"):

            self._main_first_show_done = True

            try:

                self.setWindowOpacity(0.0)

            except Exception:

                pass

        super().showEvent(event)

    def fix_taskbar_icon(self):

        """修复任务栏图标 - 在窗口显示后调用"""

        self._fix_icon_safe()

    def _initialize_theme_menu_state(self):
        """根据当前主题模式初始化菜单选中状态"""
        from styles import UnifiedStyleHelper
        helper = UnifiedStyleHelper.get_instance()
        current_mode = getattr(helper, "theme_mode", "system")
        if current_mode not in ("light", "dark", "system"):
            current_mode = "system"
        self._update_theme_action_state(current_mode)

    def _update_theme_action_state(self, mode: str):
        """更新主题菜单中各选项的选中状态"""
        if hasattr(self, "theme_light_action"):
            self.theme_light_action.setChecked(mode == "light")
        if hasattr(self, "theme_dark_action"):
            self.theme_dark_action.setChecked(mode == "dark")
        if hasattr(self, "theme_system_action"):
            self.theme_system_action.setChecked(mode == "system")

    def _on_theme_mode_selected(self, mode: str):
        """主题模式菜单项被选中时的处理"""
        # 避免重复应用相同模式
        from styles import UnifiedStyleHelper
        helper = UnifiedStyleHelper.get_instance()
        current_mode = getattr(helper, "theme_mode", "system")
        if mode == current_mode:
            self._update_theme_action_state(mode)
            return
        
        # 直接应用新主题（无动画）
        helper.setup_global_style(theme_mode=mode, persist=True)
        self._refresh_theme_styles()
        self._update_theme_action_state(mode)
        self.theme_mode_changed.emit(mode)

    def _refresh_theme_styles(self):
        """刷新主窗口及主要面板的样式以应用当前主题"""
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
        if hasattr(self, "menuBar") and hasattr(self.menuBar(), "refresh_theme_styles"):
            self.menuBar().refresh_theme_styles()

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
        container.setMinimumWidth(250)  # 增加最小宽度，确保控件正常显示
        container.setMaximumWidth(450)
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
        self.settings_panel.interval_input.valueChanged.connect(self.on_loop_settings_changed)
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

    def save_state_to_undo_stack(self):
        """保存当前状态到撤销栈"""
        if self._batch_operation:
            # 如果是批量操作，暂时不保存状态
            return
            
        # 添加到撤销栈
        state = {
            'events': []
        }
        
        # 收集事件数据
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            state['events'].append(event_data)
        
        # 限制撤销栈大小
        self.undo_stack.append(state)
        if len(self.undo_stack) > self.max_undo_steps:
            self.undo_stack.pop(0)
        
        # 清空重做栈
        self.redo_stack.clear()
        
        self.debug_logger.log_info(f"状态已保存到撤销栈，当前撤销栈大小: {len(self.undo_stack)}")

    def _delayed_save_state(self):
        """延迟保存状态到撤销栈"""
        if self._pending_undo_save:
            self.save_state_to_undo_stack()
            self._pending_undo_save = False

    def mark_state_dirty(self):
        """标记状态已更改，延迟保存到撤销栈"""
        if self._batch_operation:
            return
            
        # 延迟保存状态，避免频繁保存
        self._pending_undo_save = True
        self._undo_save_timer.start(500)  # 500ms后保存

    def on_undo(self):
        """撤销操作"""
        if not self.undo_stack:
            self.status_bar.showMessage("⚠️ 没有可撤销的操作")
            return
            
        # 保存当前状态到重做栈
        current_state = {
            'events': []
        }
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            current_state['events'].append(event_data)
        self.redo_stack.append(current_state)
        
        # 恢复上一个状态
        previous_state = self.undo_stack.pop()
        self._restore_state(previous_state)
        
        # 保存状态到文件
        self.save_saved_state()
        
        self.status_bar.showMessage("✅ 已撤销操作")
        self.debug_logger.log_info("已撤销操作")

    def on_redo(self):
        """重做操作"""
        if not self.redo_stack:
            self.status_bar.showMessage("⚠️ 没有可重做的操作")
            return
            
        # 保存当前状态到撤销栈
        current_state = {
            'events': []
        }
        for row in range(self.event_manager.events_table.rowCount()):
            event_data = []
            for col in range(1, 8):  # 跳过行号列
                item = self.event_manager.events_table.item(row, col)
                event_data.append(item.text() if item else "")
            current_state['events'].append(event_data)
        self.undo_stack.append(current_state)
        
        # 恢复下一个状态
        next_state = self.redo_stack.pop()
        self._restore_state(next_state)
        
        # 保存状态到文件
        self.save_saved_state()
        
        self.status_bar.showMessage("✅ 已重做操作")
        self.debug_logger.log_info("已重做操作")

    def _restore_state(self, state):
        """恢复状态"""
        # 清空当前事件
        self.event_manager.events_table.setRowCount(0)
        
        # 开始批量操作
        self._batch_operation = True
        
        try:
            # 恢复事件
            for i, event_data in enumerate(state['events']):
                # 创建行数据，包括行号
                row_data = [str(i + 1)] + event_data
                self.event_manager.add_table_row(row_data)
            
            # 更新统计信息
            self.event_manager.update_stats()
            
            # 立即更新预计总时间
            self.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self._batch_operation = False

    def on_new_file(self):
        """新建文件"""
        # 询问用户是否确认新建
        reply = ChineseMessageBox.show_question(self, "新建文件", "确定要新建一个空的事件列表吗？当前未保存的更改将丢失。")
        if not reply:
            return
            
        # 清空当前事件
        self.event_manager.events_table.setRowCount(0)
        
        # 保存当前状态到撤销栈
        self.save_state_to_undo_stack()
        
        # 保存状态到文件
        self.save_saved_state()
        
        # 立即更新预计总时间
        self.settings_panel.on_calculate_total_time()
        
        self.status_bar.showMessage("✅ 已新建文件")
        self.debug_logger.log_info("已新建文件")

    def load_saved_state(self):
        """加载保存的状态"""
        try:
            # 使用用户数据目录作为日志目录
            logs_dir = os.path.join(get_user_data_dir(), "logs")
            
            # 确保logs目录存在
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
            
            # 设置文件路径
            state_file = os.path.join(logs_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试从 {state_file} 加载保存的状态")
            
            if os.path.exists(state_file):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        state = json.load(f)
                    
                    # 验证状态数据的完整性
                    if isinstance(state, dict):
                        # 恢复事件
                        if 'events' in state and isinstance(state['events'], list):
                            event_count = len(state['events'])
                            self.debug_logger.log_info(f"开始恢复 {event_count} 个事件")
                            
                            for i, event_data in enumerate(state['events']):
                                # 创建行数据，包括行号
                                row_data = [str(i + 1)] + event_data
                                self.event_manager.add_table_row(row_data)
                            
                            self.debug_logger.log_info(f"已成功恢复 {event_count} 个事件")
                        else:
                            self.debug_logger.log_warning(f"状态文件中events字段缺失或格式错误，跳过事件恢复")
                        
                        # 加载设置
                        if 'settings' in state:
                            self.settings_panel.restore_settings(state['settings'])
                            self.debug_logger.log_info(f"已成功加载保存的设置")
                        
                        self.debug_logger.log_info(f"已成功加载保存的状态")
                        return True
                    else:
                        self.debug_logger.log_error(f"状态文件格式不正确，不是有效的字典")
                        return False
                except json.JSONDecodeError as e:
                    self.debug_logger.log_error(f"解析状态文件失败: {e}")
                    return False
                except Exception as e:
                    self.debug_logger.log_error(f"恢复事件数据失败: {e}", exc_info=True)
                    return False
            else:
                self.debug_logger.log_info(f"没有找到保存的状态文件: {state_file}")
                return False
        except Exception as e:
            self.debug_logger.log_error(f"加载保存的状态失败: {e}", exc_info=True)
            return False

    def save_saved_state(self):
        """保存当前状态到文件"""
        try:
            # 使用用户数据目录作为日志目录
            logs_dir = os.path.join(get_user_data_dir(), "logs")
            
            # 确保logs目录存在
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir, exist_ok=True)
            
            # 设置文件路径
            state_file = os.path.join(logs_dir, "BetterGI_StellTrack_state.json")
            self.debug_logger.log_info(f"尝试将状态保存到 {state_file}")
            
            # 构建状态数据
            state = {
                'events': [],
                'settings': {
                    'loop_count': self.settings_panel.loop_count_input.value(),
                    'interval': self.settings_panel.interval_input.value(),
                    'time_unit': self.settings_panel.time_unit_combo.currentText(),
                    'width': self.settings_panel.width_input.text(),
                    'height': self.settings_panel.height_input.text(),
                    'scale': self.settings_panel.scale_combo.currentText()
                }
            }
            
            # 收集事件数据
            table_row_count = self.event_manager.events_table.rowCount()
            self.debug_logger.log_info(f"开始收集 {table_row_count} 个事件的数据")
            
            for row in range(table_row_count):
                event_data = []
                for col in range(1, 8):  # 跳过行号列
                    item = self.event_manager.events_table.item(row, col)
                    event_data.append(item.text() if item else "")
                state['events'].append(event_data)
            
            # 验证收集的数据
            collected_event_count = len(state['events'])
            if collected_event_count != table_row_count:
                self.debug_logger.log_error(f"收集事件数据时出现不一致: 表格中有 {table_row_count} 行，但只收集到 {collected_event_count} 个事件")
                return False
            
            # 确保目录存在
            state_dir = os.path.dirname(state_file)
            if not os.path.exists(state_dir):
                os.makedirs(state_dir)
                self.debug_logger.log_info(f"已创建状态文件目录: {state_dir}")
            
            # 保存到文件
            try:
                with open(state_file, 'w', encoding='utf-8') as f:
                    json.dump(state, f, ensure_ascii=False, indent=2)
                
                self.debug_logger.log_info(f"状态已成功保存到文件: {state_file}，包含 {collected_event_count} 个事件")
                return True
            except IOError as e:
                self.debug_logger.log_error(f"写入状态文件失败: {e}")
                return False
            except json.JSONDecodeError as e:
                self.debug_logger.log_error(f"序列化状态数据失败: {e}")
                return False
        except Exception as e:
            self.debug_logger.log_error(f"保存状态到文件失败: {e}", exc_info=True)
            return False

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
        
        from about_window import UserAgreementWindow
        
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
        self.save_saved_state()
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