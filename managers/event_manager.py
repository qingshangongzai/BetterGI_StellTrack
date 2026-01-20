# 标准库模块导入
from datetime import datetime

# 第三方模块导入
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtWidgets import (
    QDialog, QGroupBox, QGridLayout, QHBoxLayout, QLabel, 
    QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
    QHeaderView
)

# 项目模块导入
from styles import (
    UnifiedStyleHelper,
    ChineseMessageBox,
    ModernGroupBox,
    ModernLineEdit,
    ModernComboBox,
    ModernMenu
)
from utils import (
    VK_MAPPING,
    KEY_NAME_MAPPING,
    EVENT_TYPE_MAP,
    generate_key_event_name,
    SORT_TIP_TEXT,
    get_event_data_from_table
)
from dialogs import (
    EventEditDialog,
    PasteOptionsDialog,
    DeleteOptionsDialog,
    BatchEditDialog
)
from dialogs.debug_tools import get_global_debug_logger
from ui import ModernTableWidget

# =============================================================================
# 线程类定义
# =============================================================================

class SortEventsThread(QThread):
    """事件排序线程类，负责在后台对事件进行排序"""
    
    # 信号定义
    sort_complete = pyqtSignal(list)  # 排序完成信号
    sort_failed = pyqtSignal(str)  # 排序失败信号
    
    def __init__(self, events_table):
        super().__init__()
        self.events_table = events_table
        self.debug_logger = get_global_debug_logger()
    
    def run(self):
        """线程运行方法，执行事件排序逻辑"""
        try:
            # 获取所有事件数据
            events = []
            for row in range(self.events_table.rowCount()):
                event_data = []
                for col in range(self.events_table.columnCount()):
                    item = self.events_table.item(row, col)
                    event_data.append(item.text() if item else "")
                events.append(event_data)
            
            # 按绝对时间排序
            events.sort(key=lambda x: int(x[7]) if x[7].isdigit() else 0)
            
            # 重新计算相对时间
            prev_absolute_time = 0
            for i, event in enumerate(events):
                # 获取当前事件的绝对时间
                current_absolute_time = int(event[7]) if event[7].isdigit() else 0
                
                # 计算新的相对时间
                relative_time = current_absolute_time - prev_absolute_time
                
                # 更新事件数据
                event[0] = str(i + 1)  # 更新行号
                event[6] = str(relative_time)  # 更新相对时间
                
                # 更新前一个绝对时间为当前绝对时间
                prev_absolute_time = current_absolute_time
            
            # 发送排序完成信号
            self.sort_complete.emit(events)
            
        except Exception as e:
            error_msg = f"排序事件失败: {str(e)}"
            self.sort_failed.emit(error_msg)


class BatchEditThread(QThread):
    """批量编辑线程类，负责在后台对事件进行批量编辑"""
    
    # 信号定义
    edit_complete = pyqtSignal(list, int, object, object, int, int, bool)  # 编辑完成信号，添加应用标志
    edit_failed = pyqtSignal(str)  # 排序失败信号编辑失败信号
    
    def __init__(self, events_table, selected_row_indices, offset, unified_rel_time, old_type_info, new_type_info, unified_x, unified_y, apply_coords):
        super().__init__()
        self.events_table = events_table
        self.selected_row_indices = selected_row_indices
        self.offset = offset
        self.unified_rel_time = unified_rel_time
        self.old_type_info = old_type_info
        self.new_type_info = new_type_info
        self.unified_x = unified_x
        self.unified_y = unified_y
        self.apply_coords = apply_coords
        self.debug_logger = get_global_debug_logger()
    
    def run(self):
        """线程运行方法，执行批量编辑逻辑"""
        try:
            # 获取需要调整的行索引
            rows_to_adjust = []
            
            # 处理每个选中的事件
            for row_idx in self.selected_row_indices:
                # 1. 处理增减偏移时间
                if self.offset != 0:
                    # 获取当前行的绝对偏移时间
                    abs_time_item = self.events_table.item(row_idx, 7)
                    if abs_time_item:
                        abs_time = int(abs_time_item.text()) if abs_time_item.text().isdigit() else 0
                        new_abs_time = abs_time + self.offset
                        
                        # 添加到需要调整的行列表
                        rows_to_adjust.append(row_idx)
                
                # 2. 处理事件类型替换
                if self.old_type_info and self.new_type_info:
                    old_type, old_keycode = self.old_type_info
                    new_type, new_keycode = self.new_type_info
                    
                    type_item = self.events_table.item(row_idx, 2)
                    if type_item:
                        current_event_type = type_item.text()
                        
                        # 匹配逻辑
                        match = False
                        if old_keycode:
                            # 具体按键事件匹配
                            keycode_item = self.events_table.item(row_idx, 3)
                            current_keycode = keycode_item.text() if keycode_item else ""
                            match = (current_event_type == old_type) and (current_keycode == old_keycode)
                        else:
                            # 基本类型匹配
                            match = (current_event_type == old_type)
                        
                        if match:
                            # 添加到需要调整的行列表
                            rows_to_adjust.append(row_idx)
            
            # 3. 处理统一相对时间
            if self.unified_rel_time > 0:
                # 添加所有选中行到需要调整的行列表
                rows_to_adjust.extend(self.selected_row_indices)
            
            # 4. 处理统一坐标
            # 只要设置了应用标志，就需要调整所有选中行
            if self.apply_coords:
                rows_to_adjust.extend(self.selected_row_indices)
            
            # 去重并排序
            rows_to_adjust = sorted(list(set(rows_to_adjust)))
            
            # 发送编辑完成信号
            self.edit_complete.emit(
                rows_to_adjust,
                self.offset,
                self.old_type_info,
                self.new_type_info,
                self.unified_x,
                self.unified_y,
                self.apply_coords
            )
            
        except Exception as e:
            error_msg = f"批量编辑事件失败: {str(e)}"
            self.edit_failed.emit(error_msg)


class SearchFilterThread(QThread):
    """搜索过滤线程类，负责在后台对事件进行搜索过滤"""
    
    # 信号定义
    filter_complete = pyqtSignal(list, list)  # 过滤完成信号
    filter_failed = pyqtSignal(str)  # 过滤失败信号
    
    def __init__(self, events_table, search_text, filter_type):
        super().__init__()
        self.events_table = events_table
        self.search_text = search_text.lower()
        self.filter_type = filter_type
        self.debug_logger = get_global_debug_logger()
    
    def run(self):
        """线程运行方法，执行搜索过滤逻辑 - 优化版本"""
        try:
            show_rows = []
            hide_rows = []

            for row in range(self.events_table.rowCount()):
                row_data = []
                for col in range(1, 4):
                    item = self.events_table.item(row, col)
                    row_data.append(item.text() if item else "")

                event_name = row_data[0].lower() if row_data[0] else ""
                event_type = row_data[1] if row_data[1] else ""
                key_code = row_data[2].lower() if row_data[2] else ""

                matches_search = True
                if self.search_text:
                    if self.search_text not in event_name and self.search_text not in event_type.lower() and self.search_text not in key_code:
                        matches_search = False

                matches_type = True
                if self.filter_type != "全部事件类型":
                    if event_type != self.filter_type:
                        matches_type = False

                if matches_search and matches_type:
                    show_rows.append(row)
                else:
                    hide_rows.append(row)

            self.filter_complete.emit(show_rows, hide_rows)

        except Exception as e:
            error_msg = f"搜索过滤事件失败: {str(e)}"
            self.filter_failed.emit(error_msg)


# =============================================================================
# 事件管理类
# =============================================================================

class EventManager:
    """事件管理类，负责所有与事件相关的操作
    
    核心功能包括：
    - 事件表格的创建和管理
    - 事件的添加、编辑、删除和复制
    - 事件的排序和搜索过滤
    - 事件的批量编辑
    - 事件数据的导入和导出
    
    使用多线程处理耗时操作，确保UI响应流畅。
    """
    
    def __init__(self, main_window):
        """初始化事件管理器
        
        Args:
            main_window: 主窗口实例，用于访问其他组件和功能
        """
        self.main_window = main_window
        self.debug_logger = get_global_debug_logger()
        self.events_table = None
        
        # UI 引用（用于主题刷新）
        self.event_editor_root = None
        self.search_container = None
        self.search_label = None
        self.search_btn = None
        self.reset_btn = None
        self.sort_tip_label = None
        
        # 线程实例，用于处理耗时操作
        self.sort_events_thread = None
        self.batch_edit_thread = None
        self.search_filter_thread = None
        
    def create_event_editor(self, parent=None):
        """创建事件编辑器组件
        
        创建包含搜索过滤、事件表格和操作按钮的完整事件编辑界面。
        
        Args:
            parent: 父部件，如果为None则创建新的QWidget
        
        Returns:
            QWidget: 包含完整事件编辑功能的部件
        """
        if parent is None:
            parent = QWidget()
        # 保存事件编辑器根部件引用，便于主题刷新
        self.event_editor_root = parent
        # 应用容器背景样式
        parent.setStyleSheet(UnifiedStyleHelper.get_instance().get_container_bg_style())
        
        layout = QVBoxLayout(parent)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.event_edit_group = ModernGroupBox("📋 事件编辑")
        group = self.event_edit_group
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        group_layout.setContentsMargins(0, 20, 0, 15)
        
        # 搜索和过滤组件
        self.create_search_filter_widgets(group_layout)
        
        # 事件表格
        self.create_event_table(group_layout)
        
        # 事件操作按钮
        self.create_event_buttons(group_layout)
        
        layout.addWidget(group)
        return parent
    
    def create_search_filter_widgets(self, parent_layout):
        """创建搜索和过滤组件
        
        创建用于事件搜索和类型过滤的UI组件，包括搜索输入框、
        事件类型下拉框和相关按钮。
        
        Args:
            parent_layout: 父布局，用于放置搜索过滤组件
        """
        # 创建搜索和过滤区域
        search_container = QWidget()
        search_container.setStyleSheet(UnifiedStyleHelper.get_instance().get_search_container_style())
        self.search_container = search_container
        search_layout = QHBoxLayout(search_container)
        search_layout.setSpacing(8)
        search_layout.setContentsMargins(10, 10, 10, 10)
        
        # 搜索标签
        search_label = QLabel("🔍 搜索:")
        search_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']}; font-size: 12px;")
        self.search_label = search_label
        search_layout.addWidget(search_label)
        
        # 搜索输入框
        self.search_input = ModernLineEdit()
        self.search_input.setPlaceholderText("按事件名称、类型、键码搜索...")
        search_layout.addWidget(self.search_input)
        
        # 事件类型过滤
        self.filter_type_combo = ModernComboBox(width=150)
        self.filter_type_combo.addItem("全部事件类型")
        self.filter_type_combo.addItems(["按键按下", "按键释放", "指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"])
        search_layout.addWidget(self.filter_type_combo)
        
        # 搜索按钮
        search_btn = QPushButton("搜索")
        search_btn.setFixedHeight(30)
        search_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        search_btn.setFixedWidth(70)
        self.search_btn = search_btn
        search_layout.addWidget(search_btn)
        
        # 重置按钮
        reset_btn = QPushButton("重置")
        reset_btn.setFixedHeight(30)
        reset_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        reset_btn.setFixedWidth(70)
        self.reset_btn = reset_btn
        search_layout.addWidget(reset_btn)
        
        parent_layout.addWidget(search_container)
        
        # 连接信号
        search_btn.clicked.connect(self.on_search_filter_changed)
        reset_btn.clicked.connect(self.on_reset_search_filter)
        # 为搜索输入框添加回车键支持
        self.search_input.returnPressed.connect(self.on_search_filter_changed)
        # 为过滤类型下拉框添加焦点事件，允许用户按回车键触发搜索
        # 使用自定义的按键处理
        self.filter_type_combo.keyPressEvent = lambda event: self.on_combo_key_press(event)
    
    def create_event_table(self, parent_layout):
        """创建事件表格组件
        
        创建用于显示和编辑事件的表格，设置列头、列宽和右键菜单。
        
        Args:
            parent_layout: 父布局，用于放置事件表格
        """
        # 创建表格
        self.events_table = ModernTableWidget(0, 8)  # 8列：行号 + 原有7列
        headers = ["序号", "事件名称", "事件类型", "键码", "X坐标", "Y坐标", "相对偏移时间", "绝对偏移时间"]
        self.events_table.setHorizontalHeaderLabels(headers)
        
        # 禁用表格的双击编辑功能
        self.events_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # 设置列宽和拉伸因子，保持原有比例关系
        # 序号: 50px → 拉伸因子 5
        # 事件名称: 100px → 拉伸因子 10
        # 事件类型: 100px → 拉伸因子 10
        # 键码: 70px → 拉伸因子 7
        # X坐标: 70px → 拉伸因子 7
        # Y坐标: 70px → 拉伸因子 7
        # 相对偏移时间: 90px → 拉伸因子 9
        # 绝对偏移时间: 90px → 拉伸因子 9
        header = self.events_table.horizontalHeader()
        
        # 设置初始列宽
        self.events_table.setColumnWidth(0, 50)   # 序号
        self.events_table.setColumnWidth(1, 100)  # 事件名称
        self.events_table.setColumnWidth(2, 100)  # 事件类型
        self.events_table.setColumnWidth(3, 70)   # 键码
        self.events_table.setColumnWidth(4, 70)   # X坐标
        self.events_table.setColumnWidth(5, 70)   # Y坐标
        self.events_table.setColumnWidth(6, 90)   # 相对偏移
        self.events_table.setColumnWidth(7, 90)   # 绝对偏移
        
        # 设置拉伸因子，确保各列按比例自适应窗口大小
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # 序号列根据内容调整
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)  # 事件名称列自动拉伸
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)  # 事件类型列自动拉伸
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # 键码列根据内容调整
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # X坐标列根据内容调整
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Y坐标列根据内容调整
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.Stretch)  # 相对偏移列自动拉伸
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # 绝对偏移列自动拉伸
        
        # 连接右键菜单信号
        self.events_table.customContextMenuRequested.connect(self.on_show_event_context_menu)
        
        # 连接表头右键菜单信号
        self.events_table.horizontalHeader().customContextMenuRequested.connect(self.on_show_header_context_menu)
        
        parent_layout.addWidget(self.events_table, 1)
    
    def create_event_buttons(self, parent_layout):
        """创建事件操作按钮
        
        创建事件操作按钮区域，包括添加、编辑、清空、撤销、重做和排序按钮。
        
        Args:
            parent_layout: 父布局，用于放置操作按钮
        """
        # 整合所有按钮到一行并居中排列
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(6)
        
        # 创建所有按钮
        self.add_event_btn = QPushButton("➕ 添加事件")
        self.edit_event_btn = QPushButton("✏️ 编辑事件")
        self.clear_events_btn = QPushButton("🧹 清空事件")
        self.undo_btn = QPushButton("↩️ 撤销")
        self.redo_btn = QPushButton("↪️ 重做")
        self.sort_events_btn = QPushButton("🔃 事件排序")
        
        # 设置所有按钮的基本样式
        all_buttons = [self.add_event_btn, self.edit_event_btn, self.clear_events_btn, 
                     self.undo_btn, self.redo_btn, self.sort_events_btn]
        
        for btn in all_buttons:
            btn.setFixedHeight(32)
            btn.setFixedWidth(100)  # 设置统一的固定宽度
            btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        
        # 设置强调色按钮
        self.add_event_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        self.sort_events_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        # 添加拉伸和按钮，实现居中效果
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.add_event_btn)
        buttons_layout.addWidget(self.edit_event_btn)
        buttons_layout.addWidget(self.clear_events_btn)
        buttons_layout.addWidget(self.undo_btn)
        buttons_layout.addWidget(self.redo_btn)
        buttons_layout.addWidget(self.sort_events_btn)
        buttons_layout.addStretch()
        
        parent_layout.addLayout(buttons_layout)
        
        # 排序提示
        sort_tip = QLabel(SORT_TIP_TEXT)
        sort_tip.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;")
        sort_tip.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sort_tip_label = sort_tip
        parent_layout.addWidget(sort_tip)
        
        # 连接信号槽
        self.add_event_btn.clicked.connect(self.on_add_event)
        self.edit_event_btn.clicked.connect(self.on_edit_event)
        self.clear_events_btn.clicked.connect(self.on_clear_events)
        self.undo_btn.clicked.connect(self.main_window.state_manager.on_undo)
        self.redo_btn.clicked.connect(self.main_window.state_manager.on_redo)
        self.sort_events_btn.clicked.connect(self.sort_events_by_absolute_time)
    
    def refresh_theme_styles(self):
        """根据当前主题重新应用事件编辑区域的样式
        
        刷新事件编辑器中所有UI组件的样式，包括：
        - 根容器背景
        - 事件编辑 GroupBox
        - 搜索区域（容器、标签、输入框、下拉框、按钮）
        - 事件表格
        - 操作按钮和排序提示
        """
        helper = UnifiedStyleHelper.get_instance()

        # 根容器背景
        if hasattr(self, "event_editor_root") and self.event_editor_root is not None:
            self.event_editor_root.setStyleSheet(helper.get_container_bg_style())
        
        # 事件编辑 GroupBox
        if hasattr(self, "event_edit_group") and self.event_edit_group is not None:
            self.event_edit_group.refresh_theme_styles()

        # 搜索区域
        if hasattr(self, "search_container") and self.search_container is not None:
            self.search_container.setStyleSheet(helper.get_search_container_style())
        if hasattr(self, "search_label") and self.search_label is not None:
            self.search_label.setStyleSheet(
                f"color: {helper.COLORS['text']}; font-size: 12px;"
            )
        if hasattr(self, "search_input") and self.search_input is not None:
            # 直接创建样式，确保使用当前主题的颜色值
            line_edit_style = f""
            line_edit_style += f"QLineEdit {{ "
            line_edit_style += f"    border: 1px solid {helper.COLORS['border']}; "
            line_edit_style += f"    border-radius: 8px; "
            line_edit_style += f"    padding: 6px 8px; "
            line_edit_style += f"    background-color: {helper.COLORS['card_bg']}; "
            line_edit_style += f"    color: {helper.COLORS['text']}; "
            line_edit_style += f"    font-size: 11px; "
            line_edit_style += f"    selection-background-color: {helper.COLORS['primary']}; "
            line_edit_style += f"}} "
            line_edit_style += f"QLineEdit:focus {{ "
            line_edit_style += f"    border-color: {helper.COLORS['primary']}; "
            line_edit_style += f"}} "
            line_edit_style += f"QLineEdit:hover {{ "
            line_edit_style += f"    border-color: #a0a0a0; "
            line_edit_style += f"}} "
            self.search_input.setStyleSheet(line_edit_style)
        if hasattr(self, "filter_type_combo") and self.filter_type_combo is not None:
            # 直接创建样式，确保使用当前主题的颜色值
            combo_style = f""
            combo_style += f"QComboBox {{ "
            combo_style += f"    border: 1px solid {helper.COLORS['border']}; "
            combo_style += f"    border-radius: 8px; "
            combo_style += f"    padding: 6px 8px; "
            combo_style += f"    background-color: {helper.COLORS['card_bg']}; "
            combo_style += f"    color: {helper.COLORS['text']}; "
            combo_style += f"    font-size: 11px; "
            combo_style += f"    min-width: 80px; "
            combo_style += f"    text-align: center; "
            combo_style += f"    padding-left: 15px; "
            combo_style += f"}} "
            combo_style += f"QComboBox::drop-down {{ "
            combo_style += f"    border: none; "
            combo_style += f"    width: 20px; "
            combo_style += f"}} "
            combo_style += f"QComboBox::down-arrow {{ "
            combo_style += f"    width: 12px; "
            combo_style += f"    height: 12px; "
            combo_style += f"    border: none; "
            combo_style += f"}} "
            combo_style += f"QComboBox QAbstractItemView {{ "
            combo_style += f"    border: 1px solid {helper.COLORS['border']}; "
            combo_style += f"    border-radius: 8px; "
            combo_style += f"    background-color: {helper.COLORS['card_bg']}; "
            combo_style += f"    selection-background-color: {helper.COLORS['primary']}; "
            combo_style += f"    selection-color: white; "
            combo_style += f"    font-size: 11px; "
            combo_style += f"    padding: 4px; "
            combo_style += f"}} "
            combo_style += f"QComboBox:hover {{ "
            combo_style += f"    border-color: #a0a0a0; "
            combo_style += f"}} "
            combo_style += f"QComboBox:focus {{ "
            combo_style += f"    border-color: {helper.COLORS['primary']}; "
            combo_style += f"}} "
            self.filter_type_combo.setStyleSheet(combo_style)
        if hasattr(self, "search_btn") and self.search_btn is not None:
            self.search_btn.setStyleSheet(helper.get_button_style(accent=True))
        if hasattr(self, "reset_btn") and self.reset_btn is not None:
            self.reset_btn.setStyleSheet(helper.get_button_style())

        # 事件表格
        if self.events_table is not None:
            self.events_table.setStyleSheet(helper.get_table_style())

        # 操作按钮和排序提示
        if hasattr(self, "add_event_btn"):
            all_buttons = [
                self.add_event_btn,
                self.edit_event_btn,
                self.clear_events_btn,
                self.undo_btn,
                self.redo_btn,
                self.sort_events_btn,
            ]
            for btn in all_buttons:
                btn.setStyleSheet(helper.get_button_style())
            # 强调色按钮
            self.add_event_btn.setStyleSheet(helper.get_button_style(accent=True))
            self.sort_events_btn.setStyleSheet(helper.get_button_style(accent=True))

        if hasattr(self, "sort_tip_label") and self.sort_tip_label is not None:
            self.sort_tip_label.setStyleSheet(
                f"color: {helper.COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;"
            )
    
    def on_show_event_context_menu(self, position):
        """显示事件表格的右键菜单
        
        使用 ModernMenu 以修复 Windows 系统下菜单圆角显示问题。
        菜单项根据选中状态条件显示：
        - 始终显示：添加事件、复制事件、剪切事件、粘贴事件、全选事件
        - 有选中事件时显示：编辑事件、批量编辑、删除事件
        
        Args:
            position: 鼠标右键点击位置
        """
        # 使用 ModernMenu 代替 QMenu
        context_menu = ModernMenu(self.main_window)
        
        # 获取选中的行
        selected_rows = self.get_selected_event_rows()
        
        # 添加"添加事件"菜单项
        add_action = QAction("➕ 添加事件", self.main_window)
        add_action.setShortcut("Ctrl+I")
        add_action.triggered.connect(self.on_add_event)
        context_menu.addAction(add_action)
        
        # 添加"编辑事件"菜单项（如果有选中行）
        if selected_rows:
            edit_action = QAction("✏️ 编辑事件", self.main_window)
            edit_action.setShortcut("Ctrl+E")
            edit_action.triggered.connect(self.on_edit_event)
            context_menu.addAction(edit_action)
            context_menu.addSeparator()
        else:
            context_menu.addSeparator()
        
        # 添加复制事件菜单项
        copy_action = QAction("📋 复制事件", self.main_window)
        copy_action.setShortcut("Ctrl+C")
        copy_action.triggered.connect(self.on_copy_event)
        context_menu.addAction(copy_action)
        
        # 添加剪切事件菜单项
        cut_action = QAction("✂️ 剪切事件", self.main_window)
        cut_action.setShortcut("Ctrl+X")
        cut_action.triggered.connect(self.on_cut_event)
        context_menu.addAction(cut_action)
        
        # 添加粘贴事件菜单项
        paste_action = QAction("📎 粘贴事件", self.main_window)
        paste_action.setShortcut("Ctrl+V")
        paste_action.triggered.connect(self.on_paste_event)
        context_menu.addAction(paste_action)
        
        context_menu.addSeparator()
        
        # 添加批量编辑菜单项（如果有选中行）
        if selected_rows:
            batch_edit_action = QAction("🔧 批量编辑", self.main_window)
            batch_edit_action.setShortcut("Ctrl+B")
            batch_edit_action.triggered.connect(self.on_batch_edit)
            context_menu.addAction(batch_edit_action)
        
        # 添加删除事件菜单项（如果有选中行）
        if selected_rows:
            delete_action = QAction("🗑️ 删除事件", self.main_window)
            delete_action.setShortcut("Delete")
            delete_action.triggered.connect(self.on_delete_event)
            context_menu.addAction(delete_action)
        
        context_menu.addSeparator()
        
        # 添加全选事件菜单项
        select_all_action = QAction("☑️ 全选事件", self.main_window)
        select_all_action.setShortcut("Ctrl+A")
        select_all_action.triggered.connect(self.on_select_all_events)
        context_menu.addAction(select_all_action)
        
        # 显示菜单
        context_menu.exec(self.events_table.viewport().mapToGlobal(position))
    
    def on_show_header_context_menu(self, position):
        """显示表头区域的右键菜单
        
        当用户点击表头区域时，显示一个菜单，允许用户添加事件或粘贴事件到列表的第一个位置。
        
        Args:
            position: 鼠标点击位置
        """
        # 使用 ModernMenu 代替 QMenu
        context_menu = ModernMenu(self.main_window)
        
        # 添加"添加到第一个位置"菜单项
        add_to_first_action = QAction("➕ 添加到第一个位置", self.main_window)
        add_to_first_action.triggered.connect(self.on_add_to_first_position)
        context_menu.addAction(add_to_first_action)
        
        # 添加粘贴到第一个位置菜单项
        paste_to_first_action = QAction("📎 粘贴到第一个位置", self.main_window)
        paste_to_first_action.triggered.connect(self.on_paste_to_first_position)
        context_menu.addAction(paste_to_first_action)
        
        # 显示菜单
        context_menu.exec(self.events_table.horizontalHeader().mapToGlobal(position))
    
    def on_search_filter_changed(self):
        """搜索过滤条件改变时调用
        
        获取当前搜索文本和过滤类型，创建并启动搜索过滤线程。
        """
        search_text = self.search_input.text().lower()
        filter_type = self.filter_type_combo.currentText()
        
        # 创建并启动搜索过滤线程
        self.search_filter_thread = SearchFilterThread(self.events_table, search_text, filter_type)
        self.search_filter_thread.filter_complete.connect(self.on_search_filter_complete)
        self.search_filter_thread.filter_failed.connect(self.on_search_filter_failed)
        self.search_filter_thread.start()
    
    def on_search_filter_complete(self, show_rows, hide_rows):
        """搜索过滤完成回调
        
        根据搜索过滤结果批量更新表格行的显示状态。
        
        Args:
            show_rows (list): 需要显示的行索引列表
            hide_rows (list): 需要隐藏的行索引列表
        """
        show_rows_set = set(show_rows)
        self.events_table.setUpdatesEnabled(False)
        
        try:
            for row in range(self.events_table.rowCount()):
                should_show = row in show_rows_set
                self.events_table.setRowHidden(row, not should_show)
            
            self.update_stats()
        finally:
            self.events_table.setUpdatesEnabled(True)
    
    def on_search_filter_failed(self, error_msg):
        """搜索过滤失败回调
        
        记录错误日志并显示错误消息框。
        
        Args:
            error_msg (str): 错误消息
        """
        self.debug_logger.log_error(error_msg)
        ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_combo_key_press(self, event):
        """处理过滤类型下拉框的按键事件
        
        调用原有的keyPressEvent方法，确保其他功能正常。
        如果是回车键，触发搜索功能。
        
        Args:
            event: 按键事件对象
        """
        from PyQt6.QtCore import Qt
        # 调用原有的keyPressEvent方法，确保其他功能正常
        super(self.filter_type_combo.__class__, self.filter_type_combo).keyPressEvent(event)
        
        # 检查是否是回车键
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            # 触发搜索功能
            self.on_search_filter_changed()
    
    def on_reset_search_filter(self):
        """重置搜索过滤条件
        
        显示所有行，清空搜索输入和过滤类型，更新统计信息。
        """
        # 批量更新优化：禁用中间重绘
        self.events_table.setUpdatesEnabled(False)
        
        try:
            # 显示所有行
            for row in range(self.events_table.rowCount()):
                self.events_table.setRowHidden(row, False)
            
            # 清空搜索输入和过滤类型
            self.search_input.clear()
            self.filter_type_combo.setCurrentIndex(0)
            
            # 更新统计信息
            self.update_stats()
        finally:
            # 确保重新启用重绘
            self.events_table.setUpdatesEnabled(True)
        
        # 显示状态消息
        self.main_window.status_bar.showMessage("✅ 搜索过滤已重置")
        self.debug_logger.log_info("搜索过滤已重置")
    
    def on_batch_edit(self):
        """批量编辑事件
        
        获取选中的行，打开批量编辑对话框。
        如果用户确认编辑，应用批量编辑并更新统计信息。
        """
        # 获取选中的行
        selected_rows = self.get_selected_event_rows()
        if not selected_rows:
            ChineseMessageBox.show_info(self.main_window, "提示", "请先选择要编辑的事件")
            return
        
        # 保存选中的行
        self.selected_rows = selected_rows
        
        # 打开批量编辑对话框
        dialog = BatchEditDialog(self.main_window, selected_rows, self.events_table)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 应用批量编辑
            self.apply_batch_edit(dialog)
            
            # 更新统计信息
            self.update_stats()
            
            # 记录操作
            self.debug_logger.log_info(f"已批量编辑 {len(selected_rows)} 个事件")
    
    def apply_batch_edit(self, dialog):
        """应用批量编辑
        
        从批量编辑对话框获取编辑参数，保存当前状态到撤销栈，
        创建并启动批量编辑线程。
        
        Args:
            dialog: 批量编辑对话框实例
        """
        # 获取编辑参数
        offset = dialog.get_offset_adjustment()
        unified_rel_time = dialog.get_unified_rel_time()
        old_type_info, new_type_info = dialog.get_type_replacement()
        apply_coords, unified_x, unified_y = dialog.get_unified_coordinates()
        
        # 获取选中的行索引
        selected_row_indices = [row.row() for row in self.selected_rows]
        selected_row_indices.sort()  # 从小到大排序
        
        # 保存当前状态到撤销栈
        self.main_window.state_manager.save_state_to_undo_stack()
        
        # 创建并启动批量编辑线程
        self.batch_edit_thread = BatchEditThread(
            self.events_table,
            selected_row_indices,
            offset,
            unified_rel_time,
            old_type_info,
            new_type_info,
            unified_x,
            unified_y,
            apply_coords
        )
        self.batch_edit_thread.edit_complete.connect(lambda rows, off, old, new, ux, uy, app: self.on_batch_edit_complete(rows, off, old, new, selected_row_indices, unified_rel_time, ux, uy, app))
        self.batch_edit_thread.edit_failed.connect(self.on_batch_edit_failed)
        self.batch_edit_thread.start()
    
    def on_batch_edit_complete(self, rows_to_adjust, offset, old_type_info, new_type_info, selected_row_indices, unified_rel_time, unified_x, unified_y, apply_coords):
        """批量编辑完成回调
        
        应用批量编辑结果到表格，包括：
        - 增减偏移时间
        - 事件类型替换
        - 统一相对时间
        - 统一坐标
        
        Args:
            rows_to_adjust (list): 需要调整的行索引列表
            offset (int): 时间偏移量
            old_type_info (tuple): 旧事件类型信息 (类型, 键码)
            new_type_info (tuple): 新事件类型信息 (类型, 键码)
            selected_row_indices (list): 选中的行索引列表
            unified_rel_time (int): 统一的相对时间
            unified_x (int): 统一的X坐标
            unified_y (int): 统一的Y坐标
            apply_coords (bool): 是否应用统一坐标
        """
        # 开始批量操作
        self.main_window._batch_operation = True
        
        try:
            # 处理每个选中的事件
            for row_idx in selected_row_indices:
                # 1. 处理增减偏移时间
                if offset != 0:
                    # 调整绝对偏移时间
                    abs_time_item = self.events_table.item(row_idx, 7)
                    if abs_time_item:
                        abs_time = int(abs_time_item.text()) if abs_time_item.text().isdigit() else 0
                        new_abs_time = abs_time + offset
                        abs_time_item.setText(str(new_abs_time))
                
                # 2. 处理事件类型替换
                if old_type_info and new_type_info:
                    old_type, old_keycode = old_type_info
                    new_type, new_keycode = new_type_info
                    
                    type_item = self.events_table.item(row_idx, 2)
                    current_event_type = type_item.text() if type_item else ""
                    
                    # 匹配逻辑
                    match = False
                    if old_keycode:
                        # 具体按键事件匹配
                        keycode_item = self.events_table.item(row_idx, 3)
                        current_keycode = keycode_item.text() if keycode_item else ""
                        match = (current_event_type == old_type) and (current_keycode == old_keycode)
                    else:
                        # 基本类型匹配
                        match = (current_event_type == old_type)
                    
                    if match:
                        # 更新事件类型
                        type_item.setText(new_type)
                        
                        # 检查是否需要清除键码
                        keycode_item = self.events_table.item(row_idx, 3)
                        if keycode_item:
                            # 鼠标事件类型列表
                            mouse_event_types = ["指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
                            # 按键事件类型列表
                            key_event_types = ["按键按下", "按键释放"]
                            
                            # 如果从按键事件替换为鼠标事件，清除键码
                            if old_type in key_event_types and new_type in mouse_event_types:
                                keycode_item.setText("")
                            # 如果新类型是具体按键事件，更新键码
                            elif new_keycode:
                                keycode_item.setText(new_keycode)
                        
                        # 更新事件名称
                        name_item = self.events_table.item(row_idx, 1)
                        if name_item:
                            # 获取当前键码
                            keycode_item = self.events_table.item(row_idx, 3)
                            current_keycode = keycode_item.text() if keycode_item else ""
                            # 生成新名称
                            new_name = generate_key_event_name(new_type, current_keycode)
                            name_item.setText(new_name)
                
                # 3. 处理统一相对时间
                if unified_rel_time > 0:
                    # 设置相对时间
                    rel_time_item = self.events_table.item(row_idx, 6)
                    rel_time_item.setText(str(unified_rel_time))
                    
                    # 根据相对时间重新计算当前事件的绝对时间
                    if row_idx > 0:
                        prev_abs_time_item = self.events_table.item(row_idx - 1, 7)
                        prev_abs_time = int(prev_abs_time_item.text()) if prev_abs_time_item.text().isdigit() else 0
                    else:
                        prev_abs_time = 0
                    
                    new_abs_time = prev_abs_time + unified_rel_time
                    abs_time_item = self.events_table.item(row_idx, 7)
                    abs_time_item.setText(str(new_abs_time))
                
                # 4. 处理统一坐标
                # 使用应用标志判断是否需要应用统一坐标
                if apply_coords:
                    # 更新X坐标
                    x_item = self.events_table.item(row_idx, 4)
                    if x_item:
                        x_item.setText(str(unified_x))
                    
                    # 更新Y坐标
                    y_item = self.events_table.item(row_idx, 5)
                    if y_item:
                        y_item.setText(str(unified_y))
            
            # 4. 根据修改调整后续事件时间
            if offset != 0 or unified_rel_time > 0:
                # 重新计算所有事件的相对时间
                self.recalculate_relative_times()
            
            # 清除撤销栈
            self.main_window.redo_stack.clear()
            
            # 更新统计信息
            self.update_stats()
            
            # 立即更新预计总时间
            self.main_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self.main_window._batch_operation = False
    
    def on_batch_edit_failed(self, error_msg):
        """批量编辑失败回调
        
        记录错误日志并显示错误消息框。
        
        Args:
            error_msg (str): 错误消息
        """
        self.debug_logger.log_error(error_msg)
        ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def add_sample_data(self):
        """添加示例数据用于测试
        
        添加5个示例事件到表格中，包括按键事件、平行移动和鼠标事件。
        """
        sample_data = [
            [1, "按下回车", "按键按下", "13", "0", "0", "0", "0"],
            [2, "释放回车", "按键释放", "13", "0", "0", "100", "100"],
            [3, "平行移动", "平行移动", "", "500", "500", "300", "400"],
            [4, "左键按下", "左键按下", "", "500", "500", "500", "900"],
            [5, "左键释放", "左键释放", "", "500", "500", "600", "1500"]
        ]
        
        for row_data in sample_data:
            self.add_table_row(row_data)
        
        self.update_stats()
        self.debug_logger.log_info("示例数据已添加")
    
    def add_table_row(self, row_data):
        """添加表格行
        
        在表格末尾添加一行数据。
        
        Args:
            row_data (list): 行数据列表，包含8列数据
        """
        row_position = self.events_table.rowCount()
        self.events_table.insertRow(row_position)
        
        for col, data in enumerate(row_data):
            item = QTableWidgetItem(str(data))
            item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.events_table.setItem(row_position, col, item)
    
    def add_table_rows(self, rows_data):
        """批量添加表格行 - 高性能版本
        
        一次性设置表格行数并填充数据，避免频繁的插入操作。
        
        Args:
            rows_data (list): 行数据列表，每个元素是一个包含8列数据的列表
        """
        if not rows_data:
            return
        
        # 获取当前行数量
        current_row_count = self.events_table.rowCount()
        # 计算新的行数量
        new_row_count = current_row_count + len(rows_data)
        
        # 一次性设置行数量
        self.events_table.setRowCount(new_row_count)
        
        # 填充数据
        for i, row_data in enumerate(rows_data):
            row_position = current_row_count + i
            for col, data in enumerate(row_data):
                item = QTableWidgetItem(str(data))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.events_table.setItem(row_position, col, item)
    
    def update_stats(self):
        """更新统计信息
        
        调用统计面板的update_stats方法更新事件统计信息。
        """
        if hasattr(self.main_window, 'stats_panel'):
            self.main_window.stats_panel.update_stats()
    
    def sort_events_by_absolute_time(self):
        """按绝对时间对事件进行排序，并重新计算相对时间
        
        如果表格为空，显示提示信息。
        否则保存当前状态到撤销栈，创建并启动事件排序线程。
        """
        if self.events_table.rowCount() == 0:
            ChineseMessageBox.show_info(self.main_window, "提示", "没有可排序的事件")
            return
        
        # 保存当前状态到撤销栈
        self.main_window.state_manager.save_state_to_undo_stack()
        
        # 创建并启动事件排序线程
        self.sort_events_thread = SortEventsThread(self.events_table)
        self.sort_events_thread.sort_complete.connect(self.on_sort_complete)
        self.sort_events_thread.sort_failed.connect(self.on_sort_failed)
        self.sort_events_thread.start()
    
    def on_sort_complete(self, sorted_events):
        """事件排序完成回调
        
        清空表格，插入排序后的事件，更新统计信息。
        
        Args:
            sorted_events (list): 排序后的事件列表
        """
        # 开始批量操作
        self.main_window._batch_operation = True
        
        try:
            # 清空表格
            self.events_table.setRowCount(0)
            
            # 插入排序后的事件
            for event in sorted_events:
                self.add_table_row(event)
            
            # 更新统计信息
            self.update_stats()
            
            self.main_window.status_bar.showMessage("✅ 已按绝对时间排序事件并重新计算相对时间")
            self.debug_logger.log_info("已按绝对时间排序事件并重新计算相对时间")
            
            # 立即更新预计总时间
            self.main_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self.main_window._batch_operation = False
    
    def on_sort_failed(self, error_msg):
        """事件排序失败回调
        
        记录错误日志并显示错误消息框。
        
        Args:
            error_msg (str): 错误消息
        """
        self.debug_logger.log_error(error_msg)
        ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def recalculate_relative_times(self):
        """重新计算所有事件的相对时间，保持绝对时间不变
        
        第一个事件的相对时间等于绝对时间。
        从第二个事件开始，根据绝对时间计算相对时间：
        相对时间(n) = 绝对时间(n) - 绝对时间(n-1)
        """
        if self.events_table.rowCount() == 0:
            return
        
        self.events_table.setUpdatesEnabled(False)
        
        try:
            # 处理第一个事件：相对时间 = 绝对时间
            first_abs_time_item = self.events_table.item(0, 7)
            first_rel_time_item = self.events_table.item(0, 6)
            if first_abs_time_item and first_rel_time_item:
                first_abs_time = int(first_abs_time_item.text()) if first_abs_time_item.text().isdigit() else 0
                first_rel_time_item.setText(str(first_abs_time))
            
            # 从第二个事件开始，根据绝对时间计算相对时间
            for i in range(1, self.events_table.rowCount()):
                # 获取前一个事件的绝对时间
                prev_abs_time_item = self.events_table.item(i-1, 7)
                prev_abs_time = int(prev_abs_time_item.text()) if prev_abs_time_item and prev_abs_time_item.text().isdigit() else 0
                
                # 获取当前事件的绝对时间
                curr_abs_time_item = self.events_table.item(i, 7)
                curr_abs_time = int(curr_abs_time_item.text()) if curr_abs_time_item and curr_abs_time_item.text().isdigit() else 0
                
                # 计算并更新相对时间
                rel_time = curr_abs_time - prev_abs_time
                rel_time_item = self.events_table.item(i, 6)
                rel_time_item.setText(str(rel_time))
        finally:
            self.events_table.setUpdatesEnabled(True)
    
    def recalculate_time_from_row(self, start_row):
        """从指定行开始重新计算时间
        
        根据相对时间重新计算从指定行开始的所有事件的绝对时间：
        绝对时间(n) = 绝对时间(n-1) + 相对时间(n)
        
        Args:
            start_row (int): 开始重新计算的行索引
        """
        total_rows = self.events_table.rowCount()
        if total_rows <= start_row:
            return
        
        # 获取前一个事件的绝对时间
        prev_abs_time = 0
        if start_row > 0:
            prev_abs_time_item = self.events_table.item(start_row - 1, 7)
            prev_abs_time = int(prev_abs_time_item.text()) if prev_abs_time_item and prev_abs_time_item.text().isdigit() else 0
        
        # 重新计算后续事件的绝对时间
        for i in range(start_row, total_rows):
            # 获取相对时间
            rel_time_item = self.events_table.item(i, 6)
            rel_time = int(rel_time_item.text()) if rel_time_item and rel_time_item.text().isdigit() else 0
            
            # 计算并更新绝对时间
            curr_abs_time = prev_abs_time + rel_time
            abs_time_item = self.events_table.item(i, 7)
            abs_time_item.setText(str(curr_abs_time))
            
            # 更新前一个绝对时间
            prev_abs_time = curr_abs_time
    
    def recalculate_all_times(self):
        """重新计算所有事件的相对时间和绝对时间
        
        第一个事件的绝对时间设为0。
        从第二个事件开始重新计算所有时间。
        """
        if self.events_table.rowCount() == 0:
            return
        
        # 第一个事件的绝对时间为0
        first_abs_time_item = self.events_table.item(0, 7)
        if first_abs_time_item:
            first_abs_time_item.setText("0")
        
        # 从第二个事件开始重新计算
        self.recalculate_time_from_row(1)
    
    def get_selected_event_rows(self):
        """获取选中的事件行
        
        获取表格中当前选中的事件行,自动过滤掉隐藏的行。
        这样可以确保在筛选模式下,只返回可见的选中行。
        
        Returns:
            list: 可见的选中行索引列表(QModelIndex对象)
        """
        # 获取所有选中的行
        all_selected_rows = self.events_table.selectionModel().selectedRows()
        
        # 过滤掉隐藏的行,只返回可见的行
        visible_selected_rows = [
            row for row in all_selected_rows 
            if not self.events_table.isRowHidden(row.row())
        ]
        
        return visible_selected_rows
    
    def update_row_numbers(self):
        """更新行号"""
        self.events_table.setUpdatesEnabled(False)
        
        try:
            for row in range(self.events_table.rowCount()):
                item = self.events_table.item(row, 0)
                if item:
                    item.setText(str(row + 1))
                else:
                    item = QTableWidgetItem(str(row + 1))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.events_table.setItem(row, 0, item)
        finally:
            self.events_table.setUpdatesEnabled(True)
    
    def get_prev_absolute_time(self, current_row):
        """获取当前行前一个事件的绝对时间
        
        Args:
            current_row (int): 当前行索引
        
        Returns:
            int: 前一个事件的绝对时间，如果是第一行则返回0
        """
        if current_row == 0:
            return 0
        prev_item = self.events_table.item(current_row - 1, 7)
        return int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0
    
    def get_next_absolute_time(self, current_row):
        """获取当前行后一个事件的绝对时间
        
        Args:
            current_row (int): 当前行索引
        
        Returns:
            int: 后一个事件的绝对时间，如果是最后一行则返回None
        """
        total_rows = self.events_table.rowCount()
        if current_row >= total_rows - 1:
            return None
        next_item = self.events_table.item(current_row + 1, 7)
        return int(next_item.text()) if next_item and next_item.text().isdigit() else None
    
    def adjust_next_event_relative_time(self, current_row, new_current_absolute_time):
        """调整当前行后一个事件的相对时间
        
        根据当前事件的新绝对时间，重新计算后一个事件的相对时间：
        相对时间(n+1) = 绝对时间(n+1) - 新绝对时间(n)
        
        Args:
            current_row (int): 当前行索引
            new_current_absolute_time (int): 当前事件的新绝对时间
        """
        next_absolute_time = self.get_next_absolute_time(current_row)
        if next_absolute_time is not None:
            next_row = current_row + 1
            new_relative_time = next_absolute_time - new_current_absolute_time
            rel_time_item = self.events_table.item(next_row, 6)
            if rel_time_item:
                rel_time_item.setText(str(new_relative_time))
            else:
                # 如果不存在，创建新的相对时间项
                new_rel_item = QTableWidgetItem(str(new_relative_time))
                new_rel_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.events_table.setItem(next_row, 6, new_rel_item)
    
    def get_event_absolute_time(self, row):
        """获取指定行事件的绝对时间
        
        Args:
            row (int): 行索引
        
        Returns:
            int: 事件的绝对时间
        """
        abs_time_item = self.events_table.item(row, 7)
        return int(abs_time_item.text()) if abs_time_item and abs_time_item.text().isdigit() else 0
    
    def update_app_state(self):
        """更新应用状态
        
        更新统计信息和预计总时间。
        """
        self.update_stats()
        self.main_window.settings_panel.on_calculate_total_time()
    
    def on_add_event(self):
        """添加事件 - 在指定位置插入
        
        根据选中状态确定插入位置：
        - 有选中事件：在第一个选中事件后插入
        - 没有选中事件：在最后插入
        
        打开事件编辑对话框，用户确认后插入新事件并更新时间。
        """
        try:
            # 获取插入位置
            selected_rows = self.get_selected_event_rows()
            if selected_rows:
                # 有选中事件：在第一个选中事件后插入
                index = selected_rows[0]  # 获取QModelIndex对象
                insert_position = index.row() + 1
                insert_after_item = index.row()  # 在这个事件后插入
            else:
                # 没有选中事件：在最后插入
                insert_position = self.events_table.rowCount()
                insert_after_item = None  # 在最后插入
            
            # 保存当前状态到撤销栈
            self.main_window.state_manager.save_state_to_undo_stack()
            
            # 开始批量操作
            self.main_window._batch_operation = True
            
            try:
                # 获取前一个事件的绝对时间，用于计算绝对偏移时间
                prev_absolute_time = self.get_prev_absolute_time(insert_position)
                
                # 创建事件编辑对话框，传入插入位置信息和前一个事件的绝对时间
                dialog = EventEditDialog(
                    self.main_window, 
                    is_edit_mode=False, 
                    insert_position=insert_position,
                    insert_after_item=insert_after_item,
                    prev_absolute_time=prev_absolute_time,
                    edit_logic=self.main_window.get_edit_logic(),
                    default_time_unit=self.main_window.menu_manager.get_time_unit()
                )
                
                # 更新插入位置信息
                dialog.update_insert_position_info(insert_position, insert_after_item)
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    event_data = dialog.get_event_data()
                    time_option = dialog.get_time_option()
                    
                    # 获取前一个事件的绝对时间
                    prev_absolute_time = self.get_prev_absolute_time(insert_position)
                    
                    # 获取新事件的相对时间
                    relative_time = int(event_data[5]) if event_data[5] else 100
                    
                    # 计算新事件的绝对时间
                    new_absolute_time = prev_absolute_time + relative_time
                    
                    # 插入新行
                    self.events_table.insertRow(insert_position)
                    new_row_data = [
                        str(insert_position + 1),  # 行号
                        event_data[0],  # 事件名称
                        event_data[1],  # 事件类型
                        event_data[2],  # 键码
                        event_data[3],  # X坐标
                        event_data[4],  # Y坐标
                        str(relative_time),  # 相对偏移
                        str(new_absolute_time)  # 绝对偏移
                    ]
                    
                    for col, data in enumerate(new_row_data):
                        item = QTableWidgetItem(str(data))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.events_table.setItem(insert_position, col, item)
                    
                    # 更新行号
                    self.update_row_numbers()
                    
                    # 根据时间修改选项调整后续事件
                    if time_option == "仅修改当前事件时间":
                        self.adjust_next_event_relative_time(insert_position, new_absolute_time)
                    else:  # 修改后重新计算后续事件时间
                        self.recalculate_time_from_row(insert_position + 1)
                    
                    # 更新应用状态
                    self.update_app_state()
                    
                    self.main_window.status_bar.showMessage("✅ 已添加新事件")
                    self.debug_logger.log_info(f"已添加新事件: {event_data[0]}")
            finally:
                # 结束批量操作
                self.main_window._batch_operation = False
        except Exception as e:
            self.main_window._batch_operation = False
            error_msg = f"添加事件错误: {e}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", f"添加事件失败: {str(e)}")
    
    def on_edit_event(self):
        """编辑事件
        
        获取第一个选中的事件，打开事件编辑对话框。
        用户确认后更新事件数据并调整时间。
        """
        try:
            selected_rows = self.get_selected_event_rows()
            if not selected_rows:
                self.debug_logger.log_warning("尝试编辑事件但未选择事件")
                ChineseMessageBox.show_warning(self.main_window, "警告", "请先选择要编辑的事件")
                return
            
            # 保存当前状态到撤销栈
            self.main_window.state_manager.save_state_to_undo_stack()
            
            # 开始批量操作
            self.main_window._batch_operation = True
            
            try:
                # 只编辑第一个选中的事件
                index = selected_rows[0]  # 获取QModelIndex对象
                row = index.row()  # 获取整数行号
                
                # 获取当前事件数据
                event_data = get_event_data_from_table(self.events_table, row)
                
                # 获取前一个事件的绝对时间，用于计算绝对偏移时间
                prev_absolute_time = self.get_prev_absolute_time(row)
                
                # 打开编辑对话框，传入前一个事件的绝对时间和当前行号
                dialog = EventEditDialog(
                    self.main_window, 
                    event_data=event_data, 
                    is_edit_mode=True,
                    prev_absolute_time=prev_absolute_time,
                    current_row=row,
                    edit_logic=self.main_window.get_edit_logic(),
                    default_time_unit=self.main_window.menu_manager.get_time_unit()
                )
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    new_event_data = dialog.get_event_data()
                    time_option = dialog.get_time_option()
                    
                    # 获取前一个事件的绝对时间
                    prev_absolute_time = self.get_prev_absolute_time(row)
                    
                    # 获取编辑后事件的相对时间
                    relative_time = int(new_event_data[5]) if new_event_data[5] else 100
                    
                    # 计算编辑后事件的绝对时间
                    current_absolute_time = prev_absolute_time + relative_time
                    
                    # 更新当前事件的数据（跳过绝对时间列）
                    for col in range(1, 7):  # 只更新1-6列
                        item = QTableWidgetItem(new_event_data[col-1])
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.events_table.setItem(row, col, item)
                    
                    # 更新当前事件的绝对时间
                    absolute_item = QTableWidgetItem(str(current_absolute_time))
                    absolute_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.events_table.setItem(row, 7, absolute_item)
                    
                    # 根据时间修改选项调整后续事件
                    if time_option == "仅修改当前事件时间":
                        self.adjust_next_event_relative_time(row, current_absolute_time)
                    else:  # 修改后重新计算后续事件时间
                        self.recalculate_time_from_row(row + 1)
                    
                    # 更新应用状态
                    self.update_app_state()
                    
                    self.main_window.status_bar.showMessage(f"✅ 已编辑事件: 第{row + 1}行")
                    self.debug_logger.log_info(f"已编辑事件: 第{row + 1}行 - {new_event_data[0]}")
            finally:
                # 结束批量操作
                self.main_window._batch_operation = False
        except Exception as e:
            self.main_window._batch_operation = False
            error_msg = f"编辑事件错误: {e}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", f"编辑事件失败: {str(e)}")
    
    def on_delete_event(self):
        """删除事件
        
        获取选中的事件，根据设置决定是否显示删除选项对话框。
        执行删除操作后更新行号、统计信息和时间。
        """
        selected_rows = self.get_selected_event_rows()
        if not selected_rows:
            self.debug_logger.log_warning("尝试删除事件但未选择事件")
            ChineseMessageBox.show_warning(self.main_window, "警告", "请先选择要删除的事件")
            return
        
        # 获取删除前的表行数和最后一行索引，用于判断是否删除的是末尾事件
        rows_before_delete = self.events_table.rowCount()
        last_row_before_delete = rows_before_delete - 1
        
        # 找出第一个和最后一个被删除事件的索引
        selected_row_numbers = [row.row() for row in selected_rows]
        first_deleted_index = min(selected_row_numbers)
        last_deleted_index = max(selected_row_numbers)
        
        # 检测是否删除的是末尾事件：必须满足两个条件
        # 1. 最后一个被删除的事件是表格的最后一行
        # 2. 所有选中的事件必须是从某位置到末尾的连续事件
        is_deleting_end_events = False
        if last_deleted_index == last_row_before_delete:
            # 检查是否是连续的末尾事件
            expected_rows = set(range(first_deleted_index, last_row_before_delete + 1))
            actual_rows = set(selected_row_numbers)
            is_deleting_end_events = (expected_rows == actual_rows)
        
        # 获取删除逻辑设置和跳过弹窗开关
        delete_logic = self.main_window.get_delete_logic()
        skip_prompt = self.main_window.get_skip_end_events_prompt()
        time_option = None
        
        # 根据设置决定是否弹出提示
        if delete_logic == 'prompt':
            # 如果开关开启且删除的是末尾事件，则跳过弹窗
            if skip_prompt and is_deleting_end_events:
                # 直接使用默认设置
                time_option = "仅修改当前事件时间"
                self.debug_logger.log_info("删除末尾事件，跳过弹窗，使用默认时间选项")
            else:
                # 显示删除选项对话框
                delete_dialog = DeleteOptionsDialog(self.main_window)
                if delete_dialog.exec() != QDialog.DialogCode.Accepted:
                    self.debug_logger.log_info("用户取消删除事件")
                    return
                time_option = delete_dialog.get_time_option()
        else:
            # 使用默认设置
            time_option = "仅修改当前事件时间" if delete_logic == 'current' else "修改后重新计算后续事件时间"
        
        # 保存当前状态到撤销栈
        self.main_window.state_manager.save_state_to_undo_stack()
        
        # 开始批量操作
        self.main_window._batch_operation = True
        
        try:
            # 获取删除前的表行数和最后一行索引
            rows_before_delete = self.events_table.rowCount()
            last_row_before_delete = rows_before_delete - 1
            
            # 找出第一个和最后一个被删除事件的索引
            selected_row_numbers = [row.row() for row in selected_rows]
            first_deleted_index = min(selected_row_numbers)
            last_deleted_index = max(selected_row_numbers)

            # 检测是否删除的是末尾事件：必须满足两个条件
            # 1. 最后一个被删除的事件是表格的最后一行
            # 2. 所有选中的事件必须是从某位置到末尾的连续事件
            is_deleting_end_events = False
            if last_deleted_index == last_row_before_delete:
                # 检查是否是连续的末尾事件
                expected_rows = set(range(first_deleted_index, last_row_before_delete + 1))
                actual_rows = set(selected_row_numbers)
                is_deleting_end_events = (expected_rows == actual_rows)

            # 执行删除
            for row in sorted(selected_row_numbers, reverse=True):
                self.events_table.removeRow(row)

            # 只有当不是删除末尾事件时，才需要处理时间计算
            if not is_deleting_end_events:
                # 获取删除前的事件数据，用于计算（只收集必要的列）
                all_events_before_delete = []
                for row in range(rows_before_delete):
                    event_data = []
                    for col in [0, 7]:  # 只收集行号和绝对时间列
                        item = self.events_table.item(row, col)
                        event_data.append(item.text() if item else "")
                    all_events_before_delete.append(event_data)
                
                # 获取被删除事件之前的最后一个事件的绝对时间
                prev_absolute_time = 0
                if first_deleted_index > 0:
                    prev_event = all_events_before_delete[first_deleted_index - 1]
                    prev_absolute_time = int(prev_event[1]) if prev_event[1].isdigit() else 0
                
                if time_option == "仅修改当前事件时间":
                    # 仅重新计算被删除事件后第一个未被删除事件的相对时间
                    # 找出所有被删除的行号（删除前的行号，从1开始）
                    deleted_row_nums = [row + 1 for row in selected_row_numbers]
                    deleted_row_nums.sort()
                    
                    # 获取删除前的事件数据，用于计算
                    # 转换为 {行号: 绝对时间} 的映射，方便查找
                    row_absolute_time_map = {}
                    for event in all_events_before_delete:
                        if event[0].isdigit():
                            row_num = int(event[0])
                            absolute_time = int(event[1]) if event[1].isdigit() else 0
                            row_absolute_time_map[row_num] = absolute_time
                    
                    # 找出所有需要更新相对时间的行号
                    # 这些行号是被删除事件后的第一个未被删除事件
                    rows_to_update = []
                    
                    # 遍历所有被删除的行号
                    for deleted_row_num in deleted_row_nums:
                        # 从当前被删除行号开始向后查找，找到第一个未被删除的行
                        next_row_num = None
                        for row_num in range(deleted_row_num, len(all_events_before_delete) + 1):
                            if row_num not in deleted_row_nums and row_num in row_absolute_time_map:
                                next_row_num = row_num
                                break
                        
                        # 如果找到了未被删除的行，并且不在待更新列表中，则添加到待更新列表
                        if next_row_num is not None and next_row_num not in rows_to_update:
                            rows_to_update.append(next_row_num)
                    
                    # 对需要更新的行号进行排序，确保按顺序处理
                    rows_to_update.sort()
                    
                    # 更新每个需要更新的行的相对时间
                    for next_row_num in rows_to_update:
                        # 找出当前行之前的最后一个未被删除的行
                        prev_row_num = None
                        # 从当前行号开始向前查找，找到第一个未被删除的行
                        for row_num in range(next_row_num - 1, 0, -1):
                            if row_num not in deleted_row_nums and row_num in row_absolute_time_map:
                                prev_row_num = row_num
                                break
                        
                        # 获取前一个事件的绝对时间
                        prev_absolute_time = 0
                        if prev_row_num is not None:
                            prev_absolute_time = row_absolute_time_map[prev_row_num]
                        
                        # 获取当前事件的绝对时间
                        current_absolute_time = row_absolute_time_map[next_row_num]
                        
                        # 计算新的相对时间
                        new_relative_time = current_absolute_time - prev_absolute_time
                        
                        # 计算当前行在表格中的行索引
                        # 计算方法：当前行号 - 前面被删除的行数 - 1（因为行号从1开始，索引从0开始）
                        deleted_rows_before = len([dr for dr in deleted_row_nums if dr < next_row_num])
                        table_row_index = next_row_num - 1 - deleted_rows_before
                        
                        # 更新相对时间到表格中
                        if table_row_index < self.events_table.rowCount():
                            relative_item = QTableWidgetItem(str(new_relative_time))
                            relative_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                            self.events_table.setItem(table_row_index, 6, relative_item)
                else:
                    # 重新计算后续所有事件的绝对时间
                    self.recalculate_time_from_row(first_deleted_index)
            
            self.update_row_numbers()
            self.update_stats()
            
            self.main_window.status_bar.showMessage(f"✅ 已删除 {len(selected_rows)} 个事件")
            self.debug_logger.log_info(f"已删除 {len(selected_rows)} 个事件，使用逻辑: {time_option}")
            
            # 立即更新预计总时间
            self.main_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self.main_window._batch_operation = False
    
    def on_copy_event(self):
        """复制事件
        
        获取选中的事件，将事件数据复制到剪贴板。
        """
        selected_rows = self.get_selected_event_rows()
        if selected_rows:
            self.main_window.copied_events = []
            
            for row_index in selected_rows:
                row = row_index.row()  # 获取整数行号
                event_data = get_event_data_from_table(self.events_table, row)
                self.main_window.copied_events.append(event_data)
            
            self.main_window.status_bar.showMessage(f"📋 已复制 {len(selected_rows)} 个事件")
            self.debug_logger.log_info(f"已复制 {len(selected_rows)} 个事件")
        else:
            self.debug_logger.log_warning("尝试复制事件但未选择事件")
            ChineseMessageBox.show_warning(self.main_window, "警告", "请先选择要复制的事件")
    
    def on_cut_event(self):
        """剪切事件 - 先复制再删除
        
        先复制选中的事件到剪贴板，然后删除这些事件。
        """
        try:
            selected_rows = self.get_selected_event_rows()
            if not selected_rows:
                self.debug_logger.log_warning("尝试剪切事件但未选择事件")
                ChineseMessageBox.show_warning(self.main_window, "警告", "请先选择要剪切的事件")
                return
            
            # 先复制事件
            self.on_copy_event()
            
            # 然后删除事件
            self.on_delete_event()
            
            self.main_window.status_bar.showMessage(f"✂️ 已剪切 {len(selected_rows)} 个事件")
            self.debug_logger.log_info(f"已剪切 {len(selected_rows)} 个事件")
            
        except Exception as e:
            error_msg = f"剪切事件失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_paste_event(self):
        """粘贴事件
        
        根据选中状态确定粘贴位置：
        - 有选中事件：在第一个选中事件后粘贴
        - 没有选中事件：在最后粘贴
        
        根据设置决定是否显示粘贴选项对话框。
        执行粘贴操作后更新行号、统计信息和时间。
        """
        if not self.main_window.copied_events:
            self.debug_logger.log_warning("尝试粘贴但没有复制的事件")
            ChineseMessageBox.show_warning(self.main_window, "警告", "没有可粘贴的事件")
            return
        
        # 获取粘贴位置，用于判断是否粘贴到末尾
        selected_rows = self.get_selected_event_rows()
        paste_position = None
        if selected_rows:
            # 有选中事件：在第一个选中事件后粘贴
            paste_position = selected_rows[0].row() + 1
        else:
            # 没有选中事件：在最后粘贴
            paste_position = self.events_table.rowCount()
        
        # 判断是否粘贴到末尾
        is_pasting_to_end = paste_position == self.events_table.rowCount()
        
        # 获取粘贴逻辑设置和跳过弹窗开关
        paste_logic = self.main_window.get_paste_logic()
        skip_prompt = self.main_window.get_skip_end_events_prompt()
        time_option = None
        
        # 根据设置决定是否弹出提示
        if paste_logic == 'prompt':
            # 如果开关开启且粘贴到末尾，则跳过弹窗
            if skip_prompt and is_pasting_to_end:
                # 直接使用默认设置
                time_option = "仅修改当前事件时间"
                self.debug_logger.log_info("粘贴到末尾，跳过弹窗，使用默认时间选项")
            else:
                # 显示粘贴选项对话框
                paste_dialog = PasteOptionsDialog(self.main_window)
                if paste_dialog.exec() != QDialog.DialogCode.Accepted:
                    self.debug_logger.log_info("用户取消粘贴事件")
                    return
                time_option = paste_dialog.get_time_option()
        else:
            # 使用默认设置
            time_option = "仅修改当前事件时间" if paste_logic == 'current' else "修改后重新计算后续事件时间"
        
        # 保存当前状态到撤销栈
        self.main_window.state_manager.save_state_to_undo_stack()
        
        # 开始批量操作
        self.main_window._batch_operation = True
        
        try:
            # 获取粘贴位置
            selected_rows = self.get_selected_event_rows()
            if selected_rows:
                # 有选中事件：在第一个选中事件后粘贴
                paste_position = selected_rows[0].row() + 1
            else:
                # 没有选中事件：在最后粘贴
                paste_position = self.events_table.rowCount()
            
            # 获取前一个事件的绝对时间
            if paste_position == 0:
                prev_absolute_time = 0
            else:
                prev_item = self.events_table.item(paste_position - 1, 7)  # 绝对偏移列
                prev_absolute_time = int(prev_item.text()) if prev_item and prev_item.text().isdigit() else 0
            
            # 粘贴事件
            for i, event_data in enumerate(self.main_window.copied_events):
                # 计算新事件的相对时间
                relative_time = int(event_data[5]) if event_data[5] else 100
                
                # 计算新事件的绝对时间
                new_absolute_time = prev_absolute_time + relative_time
                
                # 插入新行 - 修复：每次插入到当前位置，确保事件顺序正确
                insert_position = paste_position + i
                self.events_table.insertRow(insert_position)
                new_row_data = [
                    str(insert_position + 1),  # 行号
                    event_data[0],  # 事件名称
                    event_data[1],  # 事件类型
                    event_data[2],  # 键码
                    event_data[3],  # X坐标
                    event_data[4],  # Y坐标
                    str(relative_time),  # 相对偏移
                    str(new_absolute_time)  # 绝对偏移
                ]
                
                for col, data in enumerate(new_row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.events_table.setItem(insert_position, col, item)
                
                # 更新前一个事件的绝对时间
                prev_absolute_time = new_absolute_time
            
            # 更新行号
            self.update_row_numbers()
            
            # 根据时间修改选项调整后续事件
            if time_option == "修改后重新计算后续事件时间":
                # 重新计算后续所有事件的绝对时间
                self.recalculate_time_from_row(paste_position + len(self.main_window.copied_events))
            elif time_option == "仅修改当前事件时间":
                # 仅重新计算粘贴位置后一个事件的相对时间
                next_row_index = paste_position + len(self.main_window.copied_events)
                if next_row_index < self.events_table.rowCount():
                    # 获取粘贴位置后一个事件的绝对时间
                    next_item = self.events_table.item(next_row_index, 7)  # 绝对偏移列
                    if next_item and next_item.text().isdigit():
                        next_absolute_time = int(next_item.text())
                        # 获取粘贴的最后一个事件的绝对时间
                        last_paste_item = self.events_table.item(next_row_index - 1, 7)  # 绝对偏移列
                        if last_paste_item and last_paste_item.text().isdigit():
                            last_paste_absolute_time = int(last_paste_item.text())
                            # 计算新的相对时间
                            new_relative_time = next_absolute_time - last_paste_absolute_time
                            # 更新相对时间
                            rel_time_item = self.events_table.item(next_row_index, 6)  # 相对偏移列
                            if rel_time_item:
                                rel_time_item.setText(str(new_relative_time))
            
            self.update_stats()
            
            self.main_window.status_bar.showMessage(f"✅ 已粘贴 {len(self.main_window.copied_events)} 个事件")
            self.debug_logger.log_info(f"已粘贴 {len(self.main_window.copied_events)} 个事件，使用逻辑: {time_option}")
            
            # 立即更新预计总时间
            self.main_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self.main_window._batch_operation = False
    
    def on_paste_to_first_position(self):
        """粘贴事件到第一个位置
        
        将剪贴板中的事件粘贴到事件列表的第一个位置（位置0）。
        此功能通常由表头右键菜单触发。
        """
        if not self.main_window.copied_events:
            self.debug_logger.log_warning("尝试粘贴但没有复制的事件")
            ChineseMessageBox.show_warning(self.main_window, "警告", "没有可粘贴的事件")
            return
        
        # 粘贴到第一个位置不在末尾，需要根据设置决定是否显示弹窗
        paste_logic = self.main_window.get_paste_logic()
        time_option = None
        
        # 根据设置决定是否弹出提示
        if paste_logic == 'prompt':
            # 显示粘贴选项对话框
            paste_dialog = PasteOptionsDialog(self.main_window)
            if paste_dialog.exec() != QDialog.DialogCode.Accepted:
                self.debug_logger.log_info("用户取消粘贴事件到第一个位置")
                return
            time_option = paste_dialog.get_time_option()
        else:
            # 使用默认设置
            time_option = "仅修改当前事件时间" if paste_logic == 'current' else "修改后重新计算后续事件时间"
        
        # 保存当前状态到撤销栈
        self.main_window.state_manager.save_state_to_undo_stack()
        
        # 开始批量操作
        self.main_window._batch_operation = True
        
        try:
            # 粘贴位置固定为0（第一个位置）
            paste_position = 0
            
            # 第一个位置的前一个事件的绝对时间为0
            prev_absolute_time = 0
            
            # 粘贴事件
            for i, event_data in enumerate(self.main_window.copied_events):
                # 计算新事件的相对时间
                relative_time = int(event_data[5]) if event_data[5] else 100
                
                # 计算新事件的绝对时间
                new_absolute_time = prev_absolute_time + relative_time
                
                # 插入新行
                insert_position = paste_position + i
                self.events_table.insertRow(insert_position)
                new_row_data = [
                    str(insert_position + 1),  # 行号
                    event_data[0],  # 事件名称
                    event_data[1],  # 事件类型
                    event_data[2],  # 键码
                    event_data[3],  # X坐标
                    event_data[4],  # Y坐标
                    str(relative_time),  # 相对偏移
                    str(new_absolute_time)  # 绝对偏移
                ]
                
                for col, data in enumerate(new_row_data):
                    item = QTableWidgetItem(str(data))
                    item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.events_table.setItem(insert_position, col, item)
                
                # 更新前一个事件的绝对时间
                prev_absolute_time = new_absolute_time
            
            # 更新行号
            self.update_row_numbers()
            
            # 根据时间修改选项调整后续事件
            if time_option == "修改后重新计算后续事件时间":
                # 重新计算后续所有事件的绝对时间
                self.recalculate_time_from_row(len(self.main_window.copied_events))
            elif time_option == "仅修改当前事件时间":
                # 仅重新计算粘贴位置后一个事件的相对时间
                next_row_index = len(self.main_window.copied_events)
                if next_row_index < self.events_table.rowCount():
                    # 获取粘贴位置后一个事件的绝对时间
                    next_item = self.events_table.item(next_row_index, 7)  # 绝对偏移列
                    if next_item and next_item.text().isdigit():
                        next_absolute_time = int(next_item.text())
                        # 获取粘贴的最后一个事件的绝对时间
                        last_paste_item = self.events_table.item(next_row_index - 1, 7)  # 绝对偏移列
                        if last_paste_item and last_paste_item.text().isdigit():
                            last_paste_absolute_time = int(last_paste_item.text())
                            # 计算新的相对时间
                            new_relative_time = next_absolute_time - last_paste_absolute_time
                            # 更新相对时间
                            rel_time_item = self.events_table.item(next_row_index, 6)  # 相对偏移列
                            if rel_time_item:
                                rel_time_item.setText(str(new_relative_time))
            
            self.update_stats()
            
            self.main_window.status_bar.showMessage(f"✅ 已粘贴 {len(self.main_window.copied_events)} 个事件到第一个位置")
            self.debug_logger.log_info(f"已粘贴 {len(self.main_window.copied_events)} 个事件到第一个位置，使用逻辑: {time_option}")
            
            # 立即更新预计总时间
            self.main_window.settings_panel.on_calculate_total_time()
        finally:
            # 结束批量操作
            self.main_window._batch_operation = False
    
    def on_add_to_first_position(self):
        """添加事件到第一个位置
        
        在事件列表的第一个位置（位置0）添加新事件。
        此功能通常由表头右键菜单触发。
        """
        try:
            # 插入位置固定为0（第一个位置）
            insert_position = 0
            insert_after_item = None  # 在最前面插入
            
            # 保存当前状态到撤销栈
            self.main_window.state_manager.save_state_to_undo_stack()
            
            # 开始批量操作
            self.main_window._batch_operation = True
            
            try:
                # 第一个位置的前一个事件的绝对时间为0
                prev_absolute_time = 0
                
                # 创建事件编辑对话框，传入插入位置信息
                dialog = EventEditDialog(
                    self.main_window, 
                    is_edit_mode=False, 
                    insert_position=insert_position,
                    insert_after_item=insert_after_item,
                    prev_absolute_time=prev_absolute_time,
                    edit_logic=self.main_window.get_edit_logic(),
                    default_time_unit=self.main_window.menu_manager.get_time_unit()
                )
                
                # 更新插入位置信息
                dialog.update_insert_position_info(insert_position, insert_after_item)
                
                if dialog.exec() == QDialog.DialogCode.Accepted:
                    event_data = dialog.get_event_data()
                    time_option = dialog.get_time_option()
                    
                    # 获取新事件的相对时间
                    relative_time = int(event_data[5]) if event_data[5] else 100
                    
                    # 计算新事件的绝对时间（第一个位置，前一个绝对时间为0）
                    new_absolute_time = prev_absolute_time + relative_time
                    
                    # 插入新行到第一个位置
                    self.events_table.insertRow(insert_position)
                    new_row_data = [
                        str(insert_position + 1),  # 行号
                        event_data[0],  # 事件名称
                        event_data[1],  # 事件类型
                        event_data[2],  # 键码
                        event_data[3],  # X坐标
                        event_data[4],  # Y坐标
                        str(relative_time),  # 相对偏移
                        str(new_absolute_time)  # 绝对偏移
                    ]
                    
                    for col, data in enumerate(new_row_data):
                        item = QTableWidgetItem(str(data))
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        self.events_table.setItem(insert_position, col, item)
                    
                    # 更新行号
                    self.update_row_numbers()
                    
                    # 根据时间修改选项调整后续事件
                    if time_option == "仅修改当前事件时间":
                        self.adjust_next_event_relative_time(insert_position, new_absolute_time)
                    else:  # 修改后重新计算后续事件时间
                        self.recalculate_time_from_row(insert_position + 1)
                    
                    # 更新应用状态
                    self.update_app_state()
                    
                    self.main_window.status_bar.showMessage("✅ 已添加新事件到第一个位置")
                    self.debug_logger.log_info(f"已添加新事件到第一个位置: {event_data[0]}")
            finally:
                # 结束批量操作
                self.main_window._batch_operation = False
        except Exception as e:
            self.main_window._batch_operation = False
            error_msg = f"添加事件到第一个位置错误: {e}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", f"添加事件到第一个位置失败: {str(e)}")
    
    def on_select_all_events(self):
        """全选事件
        
        选中表格中的所有事件。
        """
        self.events_table.selectAll()
        self.main_window.status_bar.showMessage("✅ 已全选所有事件")
        self.debug_logger.log_info("已全选所有事件")
    
    def on_clear_events(self):
        """清空所有事件
        
        显示确认对话框，用户确认后清空表格并更新统计信息。
        """
        if self.events_table.rowCount() == 0:
            ChineseMessageBox.show_info(self.main_window, "提示", "事件列表已经为空")
            return
        
        # 确认清空操作
        reply = ChineseMessageBox.show_question(self.main_window, "确认清空", "确定要清空所有事件吗？")
        if reply:
            # 保存当前状态到撤销栈
            self.main_window.state_manager.save_state_to_undo_stack()
            
            # 开始批量操作
            self.main_window._batch_operation = True
            
            try:
                # 清空表格
                self.events_table.setRowCount(0)
                
                # 更新统计信息
                self.update_stats()
                
                self.main_window.status_bar.showMessage("✅ 已清空所有事件")
                self.debug_logger.log_info("已清空所有事件")
            finally:
                # 结束批量操作
                self.main_window._batch_operation = False
