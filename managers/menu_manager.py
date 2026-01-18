# menu_manager.py

# 标准库模块导入
# 无标准库模块导入

# 第三方模块导入
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QAction, QActionGroup
from PyQt6.QtWidgets import QMenu

# 项目模块导入
from styles import ModernMenuBar, UnifiedStyleHelper


class MenuManager:
    """菜单管理器类
    
    负责管理应用程序的菜单栏创建、配置和状态更新。
    包括文件、编辑、时间逻辑、工具、主题和帮助等菜单的管理。
    """
    
    def __init__(self, parent_window):
        """初始化菜单管理器
        
        Args:
            parent_window: 主窗口实例，用于信号连接和状态管理
        """
        self.parent_window = parent_window
        self.debug_logger = parent_window.debug_logger
        
        # 菜单项引用，用于更新选中状态
        self.delete_logic_actions = {}
        self.paste_logic_actions = {}
        self.edit_logic_actions = {}
        
        # 主题动作组
        self.theme_action_group = None
        self.theme_light_action = None
        self.theme_dark_action = None
        self.theme_system_action = None
        
        # 末尾事件操作跳过弹窗开关
        self.skip_end_events_action = None
        
        # 时间单位设置动作组
        self.time_unit_actions = {}
    
    def create_menu_bar(self):
        """创建应用程序菜单栏
        
        构建包含文件、编辑、时间逻辑、工具、主题和帮助等菜单的菜单栏，
        并为每个菜单项连接相应的操作。
        
        使用 ModernMenuBar 以修复 Windows 系统下菜单圆角显示问题。
        
        Returns:
            ModernMenuBar: 创建的菜单栏实例
        """
        # 创建现代化菜单栏，自动为所有菜单应用无边框样式
        menubar = ModernMenuBar(self.parent_window)
        self.parent_window.setMenuBar(menubar)
        
        # 文件菜单
        self._create_file_menu(menubar)
        
        # 编辑菜单
        self._create_edit_menu(menubar)
        
        # 时间逻辑菜单
        self._create_time_logic_menu(menubar)
        
        # 时间单位菜单
        self._create_time_unit_menu(menubar)
        
        # 工具菜单
        self._create_tools_menu(menubar)
        
        # 主题菜单
        self._create_theme_menu(menubar)
        
        # 帮助菜单
        self._create_help_menu(menubar)
        
        # 初始化菜单状态
        self.update_time_logic_menu_state()
        
        return menubar
    
    def _create_file_menu(self, menubar):
        """创建文件菜单
        
        创建包含新建、打开、保存和退出等操作的文件菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加文件菜单
        """
        file_menu = menubar.addMenu('文件')
        
        # 新建
        new_action = QAction('新建', self.parent_window)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.parent_window.on_new_file)
        file_menu.addAction(new_action)
        
        # 打开
        open_action = QAction('打开', self.parent_window)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.parent_window.script_manager.on_import_script)
        file_menu.addAction(open_action)
        
        # 保存
        save_action = QAction('保存', self.parent_window)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.parent_window.script_manager.on_save_script)
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # 退出
        exit_action = QAction('退出', self.parent_window)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.parent_window.close)
        file_menu.addAction(exit_action)
    
    def _create_edit_menu(self, menubar):
        """创建编辑菜单
        
        创建包含撤销、重做、添加事件、编辑事件、剪切、复制、粘贴、删除、全选和批量编辑等操作的编辑菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加编辑菜单
        """
        edit_menu = menubar.addMenu('编辑')
        
        # 撤销
        undo_action = QAction('撤销', self.parent_window)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.parent_window.on_undo)
        edit_menu.addAction(undo_action)
        
        # 重做
        redo_action = QAction('重做', self.parent_window)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.parent_window.on_redo)
        edit_menu.addAction(redo_action)
        
        edit_menu.addSeparator()
        
        # 添加事件
        add_action = QAction('添加事件', self.parent_window)
        add_action.setShortcut('Ctrl+I')
        add_action.triggered.connect(self.parent_window.event_manager.on_add_event)
        edit_menu.addAction(add_action)
        
        # 编辑事件
        edit_action = QAction('编辑事件', self.parent_window)
        edit_action.setShortcut('Ctrl+E')
        edit_action.triggered.connect(self.parent_window.event_manager.on_edit_event)
        edit_menu.addAction(edit_action)
        
        edit_menu.addSeparator()
        
        # 剪切
        cut_action = QAction('剪切', self.parent_window)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.parent_window.event_manager.on_cut_event)
        edit_menu.addAction(cut_action)
        
        # 复制
        copy_action = QAction('复制', self.parent_window)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.parent_window.event_manager.on_copy_event)
        edit_menu.addAction(copy_action)
        
        # 粘贴
        paste_action = QAction('粘贴', self.parent_window)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.parent_window.event_manager.on_paste_event)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # 删除
        delete_action = QAction('删除', self.parent_window)
        delete_action.setShortcut('Delete')
        delete_action.triggered.connect(self.parent_window.event_manager.on_delete_event)
        edit_menu.addAction(delete_action)
        
        # 全选
        select_all_action = QAction('全选', self.parent_window)
        select_all_action.setShortcut('Ctrl+A')
        select_all_action.triggered.connect(self.parent_window.event_manager.on_select_all_events)
        edit_menu.addAction(select_all_action)
        
        # 批量编辑
        batch_edit_action = QAction('批量编辑', self.parent_window)
        batch_edit_action.setShortcut('Ctrl+B')
        batch_edit_action.triggered.connect(self.parent_window.event_manager.on_batch_edit)
        edit_menu.addAction(batch_edit_action)
    
    def _create_time_logic_menu(self, menubar):
        """创建时间逻辑菜单
        
        创建包含删除事件逻辑、粘贴事件逻辑、编辑事件逻辑和末尾事件操作跳过弹窗等设置的时间逻辑菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加时间逻辑菜单
        """
        time_logic_menu = menubar.addMenu('时间逻辑')
        
        # 删除事件逻辑子菜单
        delete_logic_menu = time_logic_menu.addMenu('删除事件逻辑')
        
        # 删除事件逻辑选项 - 创建动作组确保互斥
        delete_logic_group = QActionGroup(self.parent_window)
        
        delete_prompt_action = QAction('每次弹出提示选择', self.parent_window)
        delete_prompt_action.setCheckable(True)
        delete_prompt_action.triggered.connect(lambda: self.set_delete_logic('prompt'))
        delete_logic_group.addAction(delete_prompt_action)
        delete_logic_menu.addAction(delete_prompt_action)
        
        delete_current_action = QAction('默认：仅修改当前事件时间', self.parent_window)
        delete_current_action.setCheckable(True)
        delete_current_action.triggered.connect(lambda: self.set_delete_logic('current'))
        delete_logic_group.addAction(delete_current_action)
        delete_logic_menu.addAction(delete_current_action)
        
        delete_recalculate_action = QAction('默认：重新计算后续事件时间', self.parent_window)
        delete_recalculate_action.setCheckable(True)
        delete_recalculate_action.triggered.connect(lambda: self.set_delete_logic('recalculate'))
        delete_logic_group.addAction(delete_recalculate_action)
        delete_logic_menu.addAction(delete_recalculate_action)
        
        # 粘贴事件逻辑子菜单
        paste_logic_menu = time_logic_menu.addMenu('粘贴事件逻辑')
        
        # 粘贴事件逻辑选项 - 创建动作组确保互斥
        paste_logic_group = QActionGroup(self.parent_window)
        
        paste_prompt_action = QAction('每次弹出提示选择', self.parent_window)
        paste_prompt_action.setCheckable(True)
        paste_prompt_action.triggered.connect(lambda: self.set_paste_logic('prompt'))
        paste_logic_group.addAction(paste_prompt_action)
        paste_logic_menu.addAction(paste_prompt_action)
        
        paste_current_action = QAction('默认：仅修改当前事件时间', self.parent_window)
        paste_current_action.setCheckable(True)
        paste_current_action.triggered.connect(lambda: self.set_paste_logic('current'))
        paste_logic_group.addAction(paste_current_action)
        paste_logic_menu.addAction(paste_current_action)
        
        paste_recalculate_action = QAction('默认：重新计算后续事件时间', self.parent_window)
        paste_recalculate_action.setCheckable(True)
        paste_recalculate_action.triggered.connect(lambda: self.set_paste_logic('recalculate'))
        paste_logic_group.addAction(paste_recalculate_action)
        paste_logic_menu.addAction(paste_recalculate_action)
        
        # 编辑事件逻辑子菜单
        edit_logic_menu = time_logic_menu.addMenu('编辑事件逻辑')
        
        # 编辑事件逻辑选项 - 创建动作组确保互斥
        edit_logic_group = QActionGroup(self.parent_window)
        
        edit_current_action = QAction('默认：仅修改当前事件时间', self.parent_window)
        edit_current_action.setCheckable(True)
        edit_current_action.triggered.connect(lambda: self.set_edit_logic('current'))
        edit_logic_group.addAction(edit_current_action)
        edit_logic_menu.addAction(edit_current_action)
        
        edit_recalculate_action = QAction('默认：重新计算后续事件时间', self.parent_window)
        edit_recalculate_action.setCheckable(True)
        edit_recalculate_action.triggered.connect(lambda: self.set_edit_logic('recalculate'))
        edit_logic_group.addAction(edit_recalculate_action)
        edit_logic_menu.addAction(edit_recalculate_action)
        
        # 末尾事件操作跳过弹窗开关
        skip_end_events_action = QAction('末尾事件操作跳过弹窗', self.parent_window)
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
    
    def _create_tools_menu(self, menubar):
        """创建工具菜单
        
        创建包含事件时间分析和调试工具等操作的菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加工具菜单
        """
        tools_menu = menubar.addMenu('工具')
        
        # 事件时间分析工具
        time_analysis_action = QAction('事件时间分析', self.parent_window)
        time_analysis_action.setShortcut('Ctrl+T')
        time_analysis_action.triggered.connect(self.parent_window.on_event_time_analysis)
        tools_menu.addAction(time_analysis_action)
        
        # 添加分隔线
        tools_menu.addSeparator()
        
        # 调试工具
        debug_action = QAction('调试工具', self.parent_window)
        debug_action.setShortcut('Ctrl+D')
        debug_action.triggered.connect(self.parent_window.on_open_debug_tool)
        tools_menu.addAction(debug_action)
    
    def _create_time_unit_menu(self, menubar):
        """创建时间单位菜单
        
        创建包含编辑事件时间单位设置的时间单位菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加时间单位菜单
        """
        time_unit_menu = menubar.addMenu('时间单位')
        
        # 编辑事件时间单位子菜单
        edit_time_unit_menu = time_unit_menu.addMenu('编辑事件时间单位')
        
        # 时间单位选项 - 创建动作组确保互斥
        time_unit_group = QActionGroup(self.parent_window)
        
        # 系统自动匹配
        auto_unit_action = QAction('系统自动匹配', self.parent_window)
        auto_unit_action.setCheckable(True)
        auto_unit_action.triggered.connect(lambda: self.set_time_unit('auto'))
        time_unit_group.addAction(auto_unit_action)
        edit_time_unit_menu.addAction(auto_unit_action)
        
        # 毫秒
        ms_unit_action = QAction('毫秒（ms）', self.parent_window)
        ms_unit_action.setCheckable(True)
        ms_unit_action.triggered.connect(lambda: self.set_time_unit('ms'))
        time_unit_group.addAction(ms_unit_action)
        edit_time_unit_menu.addAction(ms_unit_action)
        
        # 秒
        s_unit_action = QAction('秒（s）', self.parent_window)
        s_unit_action.setCheckable(True)
        s_unit_action.triggered.connect(lambda: self.set_time_unit('s'))
        time_unit_group.addAction(s_unit_action)
        edit_time_unit_menu.addAction(s_unit_action)
        
        # 分钟
        min_unit_action = QAction('分钟（min）', self.parent_window)
        min_unit_action.setCheckable(True)
        min_unit_action.triggered.connect(lambda: self.set_time_unit('min'))
        time_unit_group.addAction(min_unit_action)
        edit_time_unit_menu.addAction(min_unit_action)
        
        # 保存菜单项引用，用于更新选中状态
        self.time_unit_actions = {
            'auto': auto_unit_action,
            'ms': ms_unit_action,
            's': s_unit_action,
            'min': min_unit_action
        }
    
    def _create_theme_menu(self, menubar):
        """创建主题菜单
        
        创建包含浅色主题、深色主题和跟随系统等选项的主题菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加主题菜单
        """
        theme_menu = menubar.addMenu('主题')
        
        # 主题模式动作组（互斥）
        self.theme_action_group = QActionGroup(self.parent_window)
        self.theme_action_group.setExclusive(True)
        
        # 浅色主题
        self.theme_light_action = QAction('浅色主题', self.parent_window)
        self.theme_light_action.setCheckable(True)
        self.theme_light_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('light'))
        self.theme_action_group.addAction(self.theme_light_action)
        theme_menu.addAction(self.theme_light_action)
        
        # 深色主题
        self.theme_dark_action = QAction('深色主题', self.parent_window)
        self.theme_dark_action.setCheckable(True)
        self.theme_dark_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('dark'))
        self.theme_action_group.addAction(self.theme_dark_action)
        theme_menu.addAction(self.theme_dark_action)
        
        # 跟随系统
        self.theme_system_action = QAction('跟随系统', self.parent_window)
        self.theme_system_action.setCheckable(True)
        self.theme_system_action.triggered.connect(lambda checked=False: self._on_theme_mode_selected('system'))
        self.theme_action_group.addAction(self.theme_system_action)
        theme_menu.addAction(self.theme_system_action)
        
        # 根据当前主题模式初始化选中状态
        self._initialize_theme_menu_state()
    
    def _create_help_menu(self, menubar):
        """创建帮助菜单
        
        创建包含个人主页、项目地址、使用说明、检查更新、关于和用户协议等操作的菜单。
        
        Args:
            menubar: 菜单栏实例，用于添加帮助菜单
        """
        help_menu = menubar.addMenu('帮助')
        
        # 个人主页
        homepage_action = QAction('个人主页', self.parent_window)
        homepage_action.triggered.connect(lambda: self.parent_window.open_url("https://space.bilibili.com/1232406878"))
        help_menu.addAction(homepage_action)
        
        # 项目地址
        project_action = QAction('项目地址', self.parent_window)
        project_action.triggered.connect(lambda: self.parent_window.open_url("https://gitee.com/qingshangongzai/BetterGI_StellTrack"))
        help_menu.addAction(project_action)
        
        # 使用说明
        manual_action = QAction('使用说明', self.parent_window)
        manual_action.triggered.connect(self.parent_window.open_manual)
        help_menu.addAction(manual_action)
        
        help_menu.addSeparator()
        
        # 检查更新
        check_update_action = QAction('检查更新', self.parent_window)
        check_update_action.triggered.connect(self.parent_window.on_check_update)
        help_menu.addAction(check_update_action)
        
        help_menu.addSeparator()
        
        # 关于
        about_action = QAction('关于', self.parent_window)
        about_action.triggered.connect(self.parent_window.on_about)
        help_menu.addAction(about_action)
        
        # 用户协议
        agreement_action = QAction('用户协议', self.parent_window)
        agreement_action.triggered.connect(self.parent_window.on_user_agreement)
        help_menu.addAction(agreement_action)
    
    def set_delete_logic(self, logic):
        """设置删除事件逻辑
        
        设置删除事件时的处理逻辑，并更新菜单状态和保存设置。
        
        Args:
            logic (str): 删除逻辑，可选值为 'prompt'、'current' 或 'recalculate'
        """
        self.parent_window.delete_logic = logic
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.parent_window.status_bar.showMessage(f"✅ 删除事件逻辑已设置为: {self.get_delete_logic_display_name(logic)}")
        self.debug_logger.log_info(f"删除事件逻辑设置为: {logic}")
    
    def set_paste_logic(self, logic):
        """设置粘贴事件逻辑
        
        设置粘贴事件时的处理逻辑，并更新菜单状态和保存设置。
        
        Args:
            logic (str): 粘贴逻辑，可选值为 'prompt'、'current' 或 'recalculate'
        """
        self.parent_window.paste_logic = logic
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.parent_window.status_bar.showMessage(f"✅ 粘贴事件逻辑已设置为: {self.get_paste_logic_display_name(logic)}")
        self.debug_logger.log_info(f"粘贴事件逻辑设置为: {logic}")
    
    def set_edit_logic(self, logic):
        """设置编辑事件逻辑
        
        设置编辑事件时的处理逻辑，并更新菜单状态和保存设置。
        
        Args:
            logic (str): 编辑逻辑，可选值为 'current' 或 'recalculate'
        """
        self.parent_window.edit_logic = logic
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.parent_window.status_bar.showMessage(f"✅ 编辑事件逻辑已设置为: {self.get_edit_logic_display_name(logic)}")
        self.debug_logger.log_info(f"编辑事件逻辑设置为: {logic}")
    
    def set_skip_end_events_prompt(self, checked):
        """设置是否跳过末尾事件操作弹窗
        
        设置在操作末尾事件时是否跳过弹窗提示，并保存设置。
        
        Args:
            checked (bool): 是否跳过弹窗，True 表示跳过，False 表示显示弹窗
        """
        self.parent_window.skip_end_events_prompt = checked
        self.save_time_logic_settings()
        if checked:
            self.parent_window.status_bar.showMessage("✅ 已开启末尾事件操作跳过弹窗")
            self.debug_logger.log_info("已开启末尾事件操作跳过弹窗")
        else:
            self.parent_window.status_bar.showMessage("⚠️ 已关闭末尾事件操作跳过弹窗")
            self.debug_logger.log_info("已关闭末尾事件操作跳过弹窗")
    
    def set_time_unit(self, unit):
        """设置默认时间单位
        
        设置编辑事件时使用的默认时间单位，并更新菜单状态和保存设置。
        
        Args:
            unit (str): 时间单位，可选值为 'auto'、'ms'、's' 或 'min'
        """
        self.parent_window.default_time_unit = unit
        self.update_time_logic_menu_state()
        self.save_time_logic_settings()
        self.parent_window.status_bar.showMessage(f"✅ 默认时间单位已设置为: {self.get_time_unit_display_name(unit)}")
        self.debug_logger.log_info(f"默认时间单位设置为: {unit}")
    
    def get_time_unit(self):
        """获取当前默认时间单位
        
        Returns:
            str: 当前默认时间单位，默认为 'auto'
        """
        return getattr(self.parent_window, 'default_time_unit', 'auto')
    
    def get_time_unit_display_name(self, unit):
        """获取时间单位的显示名称
        
        Args:
            unit (str): 时间单位代码
            
        Returns:
            str: 时间单位的显示名称
        """
        display_names = {
            'auto': '系统自动匹配',
            'ms': '毫秒（ms）',
            's': '秒（s）',
            'min': '分钟（min）'
        }
        return display_names.get(unit, unit)
    
    def update_time_logic_menu_state(self):
        """更新时间逻辑菜单的选中状态
        
        根据当前设置更新时间逻辑菜单中各个菜单项的选中状态，包括：
        - 删除逻辑菜单项
        - 粘贴逻辑菜单项
        - 编辑逻辑菜单项
        - 末尾事件跳过弹窗开关
        - 时间单位菜单项
        """
        # 更新删除逻辑菜单状态
        if hasattr(self.parent_window, 'delete_logic'):
            delete_logic = self.parent_window.delete_logic
            if delete_logic in self.delete_logic_actions:
                self.delete_logic_actions[delete_logic].setChecked(True)
        
        # 更新粘贴逻辑菜单状态
        if hasattr(self.parent_window, 'paste_logic'):
            paste_logic = self.parent_window.paste_logic
            if paste_logic in self.paste_logic_actions:
                self.paste_logic_actions[paste_logic].setChecked(True)
        
        # 更新编辑逻辑菜单状态
        if hasattr(self.parent_window, 'edit_logic'):
            edit_logic = self.parent_window.edit_logic
            if edit_logic in self.edit_logic_actions:
                self.edit_logic_actions[edit_logic].setChecked(True)
        
        # 更新末尾事件跳过弹窗状态
        if hasattr(self.parent_window, 'skip_end_events_prompt') and self.skip_end_events_action:
            self.skip_end_events_action.setChecked(self.parent_window.skip_end_events_prompt)
        
        # 更新时间单位菜单状态
        if hasattr(self.parent_window, 'default_time_unit'):
            time_unit = self.parent_window.default_time_unit
            if time_unit in self.time_unit_actions:
                self.time_unit_actions[time_unit].setChecked(True)
    
    def get_delete_logic_display_name(self, logic):
        """获取删除逻辑的显示名称
        
        Args:
            logic (str): 删除逻辑代码
            
        Returns:
            str: 删除逻辑的显示名称
        """
        display_names = {
            'prompt': '每次弹出提示选择',
            'current': '默认：仅修改当前事件时间',
            'recalculate': '默认：重新计算后续事件时间'
        }
        return display_names.get(logic, logic)
    
    def get_paste_logic_display_name(self, logic):
        """获取粘贴逻辑的显示名称
        
        Args:
            logic (str): 粘贴逻辑代码
            
        Returns:
            str: 粘贴逻辑的显示名称
        """
        display_names = {
            'prompt': '每次弹出提示选择',
            'current': '默认：仅修改当前事件时间',
            'recalculate': '默认：重新计算后续事件时间'
        }
        return display_names.get(logic, logic)
    
    def get_edit_logic_display_name(self, logic):
        """获取编辑逻辑的显示名称
        
        Args:
            logic (str): 编辑逻辑代码
            
        Returns:
            str: 编辑逻辑的显示名称
        """
        display_names = {
            'current': '默认：仅修改当前事件时间',
            'recalculate': '默认：重新计算后续事件时间'
        }
        return display_names.get(logic, logic)
    
    def get_edit_logic(self):
        """获取当前编辑逻辑
        
        Returns:
            str: 当前编辑逻辑，默认为 'current'
        """
        return getattr(self.parent_window, 'edit_logic', 'current')
    
    def get_delete_logic(self):
        """获取当前删除逻辑
        
        Returns:
            str: 当前删除逻辑，默认为 'prompt'
        """
        return getattr(self.parent_window, 'delete_logic', 'prompt')
    
    def get_paste_logic(self):
        """获取当前粘贴逻辑
        
        Returns:
            str: 当前粘贴逻辑，默认为 'prompt'
        """
        return getattr(self.parent_window, 'paste_logic', 'prompt')
    
    def save_time_logic_settings(self):
        """保存时间逻辑设置到配置文件
        
        将以下时间逻辑设置保存到 QSettings 配置文件：
        - 删除事件逻辑
        - 粘贴事件逻辑
        - 编辑事件逻辑
        - 末尾事件操作跳过弹窗开关
        - 默认时间单位
        """
        settings = QSettings("BetterGI", "StellTrack")
        settings.setValue("delete_logic", self.get_delete_logic())
        settings.setValue("paste_logic", self.get_paste_logic())
        settings.setValue("edit_logic", self.get_edit_logic())
        settings.setValue("skip_end_events_prompt", getattr(self.parent_window, 'skip_end_events_prompt', True))
        settings.setValue("default_time_unit", self.get_time_unit())
        self.debug_logger.log_info("时间逻辑设置已保存")
    
    def load_time_logic_settings(self):
        """从配置文件加载时间逻辑设置
        
        从 QSettings 配置文件中加载以下时间逻辑设置：
        - 删除事件逻辑
        - 粘贴事件逻辑
        - 编辑事件逻辑
        - 末尾事件操作跳过弹窗开关
        - 默认时间单位
        
        加载完成后更新菜单项的选中状态。
        """
        settings = QSettings("BetterGI", "StellTrack")
        
        # 加载删除逻辑
        delete_logic = settings.value("delete_logic", "prompt")
        self.parent_window.delete_logic = delete_logic
        
        # 加载粘贴逻辑
        paste_logic = settings.value("paste_logic", "prompt")
        self.parent_window.paste_logic = paste_logic
        
        # 加载编辑逻辑
        edit_logic = settings.value("edit_logic", "current")
        self.parent_window.edit_logic = edit_logic
        
        # 加载末尾事件跳过弹窗设置
        skip_end_events_prompt = settings.value("skip_end_events_prompt", True, type=bool)
        self.parent_window.skip_end_events_prompt = skip_end_events_prompt
        
        # 加载默认时间单位设置
        default_time_unit = settings.value("default_time_unit", "auto")
        self.parent_window.default_time_unit = default_time_unit
        
        # 更新菜单项的选中状态
        self.update_time_logic_menu_state()
        
        self.debug_logger.log_info(f"时间逻辑设置已加载: 删除={delete_logic}, 粘贴={paste_logic}, 编辑={edit_logic}, 跳过末尾事件={skip_end_events_prompt}, 默认时间单位={default_time_unit}")
    
    def _initialize_theme_menu_state(self):
        """初始化主题菜单状态
        
        根据当前主题模式初始化主题菜单中对应菜单项的选中状态。
        """
        helper = UnifiedStyleHelper.get_instance()
        current_mode = helper.theme_mode
        self._update_theme_action_state(current_mode)
    
    def _update_theme_action_state(self, mode: str):
        """更新主题动作状态
        
        根据指定的主题模式更新主题菜单中对应菜单项的选中状态。
        
        Args:
            mode (str): 主题模式，可选值为 'light'、'dark' 或 'system'
        """
        if mode == "light":
            self.theme_light_action.setChecked(True)
        elif mode == "dark":
            self.theme_dark_action.setChecked(True)
        else:  # system
            self.theme_system_action.setChecked(True)
    
    def _on_theme_mode_selected(self, mode: str):
        """主题模式选择处理
        
        处理用户选择的主题模式，应用新主题并更新相关状态。
        包括：
        - 应用新主题样式
        - 刷新所有控件样式
        - 更新菜单状态
        - 发出主题变更信号
        - 显示状态栏提示
        
        Args:
            mode (str): 主题模式，可选值为 'light'、'dark' 或 'system'
        """
        helper = UnifiedStyleHelper.get_instance()
        
        # 避免重复应用相同模式
        current_mode = getattr(helper, "theme_mode", "system")
        if mode == current_mode:
            return
        
        # 直接应用新主题（无动画，快速切换）
        helper.setup_global_style(theme_mode=mode, persist=True)
        
        # 刷新所有控件样式
        self.parent_window._refresh_theme_styles()
        
        # 更新菜单状态
        self._update_theme_action_state(mode)
        
        # 发出主题变更信号
        self.parent_window.theme_mode_changed.emit(mode)
        
        self.parent_window.status_bar.showMessage(f"✅ 主题已切换为: {helper.get_theme_display_name(mode)}")
        self.debug_logger.log_info(f"主题已切换为: {mode}")