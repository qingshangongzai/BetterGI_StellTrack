# batch_edit_dialog.py

# 标准库模块导入
# 无标准库模块导入

# 第三方模块导入
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QCheckBox, QLabel, QGridLayout, QVBoxLayout, QHBoxLayout
)

# 项目模块导入
from styles import (
    UnifiedStyleHelper,
    get_global_font_manager,
    ModernGroupBox,
    ModernLineEdit,
    ModernComboBox,
    ModernDoubleSpinBox,
    BaseFramelessDialog,
    DialogFactory,
    ChineseMessageBox
)
from utils import KEY_PRESS_EVENTS, convert_time_to_ms


class BatchEditDialog(BaseFramelessDialog):
    """批量编辑对话框，用于批量修改事件的属性
    
    提供以下批量编辑功能：
    - 增减绝对时间
    - 统一相对时间
    - 事件类型替换
    - 统一坐标
    
    Args:
        parent: 父窗口组件
        selected_rows: 选中的行列表
        events_table: 事件表格控件
    """
    
    def __init__(self, parent=None, selected_rows=None, events_table=None):
        """初始化批量编辑对话框
        
        Args:
            parent: 父窗口组件
            selected_rows: 选中的行列表
            events_table: 事件表格控件
        """
        super().__init__(
            parent=parent,
            title="批量编辑事件",
            size=(500, 400)
        )
        self.selected_rows = selected_rows or []
        self.events_table = events_table

        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面
        
        创建批量编辑对话框的界面布局，包括：
        - 操作选项组（增减偏移时间、统一相对时间、事件类型替换、统一坐标）
        - 提示信息
        - 按钮区域
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        # 顶部边距40px为标题栏留出空间
        layout.setContentsMargins(20, 40, 20, 20)
        
        # 操作选项组
        operation_group = ModernGroupBox("⚙️ 操作选项")
        operation_layout = QGridLayout(operation_group)  # 使用GridLayout确保精确对齐
        operation_layout.setSpacing(10)
        operation_layout.setContentsMargins(15, 15, 15, 15)
        
        # 设置统一的输入框宽度
        input_width = 120
        
        # 1. 增减偏移时间
        offset_label = QLabel("增减绝对时间:")
        offset_label.setFixedWidth(120)
        
        # 创建水平布局来容纳时间输入框和单位选择框
        offset_time_layout = QHBoxLayout()
        offset_time_layout.setContentsMargins(0, 0, 0, 0)
        offset_time_layout.setSpacing(8)
        
        self.offset_input = ModernDoubleSpinBox(width=input_width)
        self.offset_input.setMinimum(-999999)
        self.offset_input.setMaximum(999999)
        self.offset_input.setValue(0)
        self.offset_input.setDecimals(0)
        # 初始设置为ms单位，步长为100
        self.offset_input.update_step_based_on_unit("ms")

        self.offset_time_unit_combo = ModernComboBox()
        self.offset_time_unit_combo.addItems(["ms", "s", "min"])
        self.offset_time_unit_combo.setCurrentText("ms")
        self.offset_time_unit_combo.setFixedWidth(60)  # 设置固定宽度为60px
        # 使用统一的居中组合框样式
        self.offset_time_unit_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        # 连接信号，当时间单位改变时更新步长
        self.offset_time_unit_combo.currentTextChanged.connect(
            lambda unit: self.offset_input.update_step_based_on_unit(unit)
        )
        
        offset_time_layout.addWidget(self.offset_input)
        offset_time_layout.addWidget(self.offset_time_unit_combo)

        operation_layout.addWidget(offset_label, 0, 0)
        operation_layout.addLayout(offset_time_layout, 0, 1, 1, 2)

        # 2. 统一相对时间
        rel_time_label = QLabel("统一相对时间:")
        rel_time_label.setFixedWidth(120)
        
        # 创建水平布局来容纳时间输入框和单位选择框
        rel_time_layout = QHBoxLayout()
        rel_time_layout.setContentsMargins(0, 0, 0, 0)
        rel_time_layout.setSpacing(8)
        
        self.rel_time_input = ModernDoubleSpinBox(width=input_width)
        self.rel_time_input.setMinimum(0)
        self.rel_time_input.setMaximum(999999)
        self.rel_time_input.setValue(0)
        self.rel_time_input.setDecimals(0)
        # 初始设置为ms单位，步长为100
        self.rel_time_input.update_step_based_on_unit("ms")

        self.rel_time_unit_combo = ModernComboBox()
        self.rel_time_unit_combo.addItems(["ms", "s", "min"])
        self.rel_time_unit_combo.setCurrentText("ms")
        self.rel_time_unit_combo.setFixedWidth(60)  # 设置固定宽度为60px
        # 使用统一的居中组合框样式
        self.rel_time_unit_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        # 连接信号，当时间单位改变时更新步长
        self.rel_time_unit_combo.currentTextChanged.connect(
            lambda unit: self.rel_time_input.update_step_based_on_unit(unit)
        )
        
        rel_time_layout.addWidget(self.rel_time_input)
        rel_time_layout.addWidget(self.rel_time_unit_combo)

        operation_layout.addWidget(rel_time_label, 1, 0)
        operation_layout.addLayout(rel_time_layout, 1, 1, 1, 2)

        
        # 3. 事件类型替换
        # 提取所有按键事件（使用字典保存，事件名称为键，(event_type, keycode)为值）
        self.key_events = {}
        if self.events_table:
            for row in range(self.events_table.rowCount()):
                event_name_item = self.events_table.item(row, 1)
                event_type_item = self.events_table.item(row, 2)
                keycode_item = self.events_table.item(row, 3)
                if event_name_item and event_type_item and keycode_item:
                    event_name = event_name_item.text()
                    event_type = event_type_item.text()
                    keycode = keycode_item.text()
                    if event_type in KEY_PRESS_EVENTS and keycode:
                        # 只保存每个事件名称对应的事件类型和键码
                        self.key_events[event_name] = (event_type, keycode)

        # 基本事件类型（移除了"按键按下"和"按键释放"）
        base_event_types = ["指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
        
        # 提取选定事件的事件类型
        selected_event_types = set()
        selected_key_events = set()
        
        if self.selected_rows and self.events_table:
            for row_index in self.selected_rows:
                row = row_index.row()
                if row < self.events_table.rowCount():
                    event_type_item = self.events_table.item(row, 2)
                    event_name_item = self.events_table.item(row, 1)
                    
                    if event_type_item:
                        event_type = event_type_item.text()
                        # 添加基本事件类型
                        if event_type in base_event_types:
                            selected_event_types.add(event_type)
                        # 添加按键事件类型
                        elif event_type in KEY_PRESS_EVENTS and event_name_item:
                            event_name = event_name_item.text()
                            selected_key_events.add(event_name)
        
        # 创建事件类型替换标签
        type_replace_label = QLabel("事件类型替换:")
        type_replace_label.setFixedWidth(120)
        
        # 创建事件类型替换的水平布局,不使用GridLayout的列,而是独立的水平布局
        type_replace_layout = QHBoxLayout()
        type_replace_layout.setSpacing(5)
        type_replace_layout.setContentsMargins(0, 0, 0, 0)
                
        # 确保old_type_combo宽度一致
        self.old_type_combo = ModernComboBox(width=input_width)
        self.old_type_combo.addItem("不替换类型")
        # 只添加选定事件中的基本事件类型
        for event_type in sorted(selected_event_types):
            self.old_type_combo.addItem(event_type)
        # 只添加选定事件中的按键事件
        for event_name in sorted(selected_key_events):
            self.old_type_combo.addItem(event_name)
        
        type_arrow_label = QLabel("→")
        type_arrow_label.setFixedWidth(30)
        type_arrow_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 确保new_type_combo宽度一致
        self.new_type_combo = ModernComboBox(width=input_width)
        self.new_type_combo.addItems(base_event_types)
        # 添加具体按键事件到new_type_combo,只显示事件名称
        for event_name in sorted(self.key_events.keys()):
            self.new_type_combo.addItem(event_name)
        
        # 将控件添加到水平布局
        type_replace_layout.addWidget(self.old_type_combo)
        type_replace_layout.addWidget(type_arrow_label)
        type_replace_layout.addWidget(self.new_type_combo)
        type_replace_layout.addStretch()
        
        # 将标签和布局添加到GridLayout
        operation_layout.addWidget(type_replace_label, 2, 0)
        operation_layout.addLayout(type_replace_layout, 2, 1, 1, 3)
        
        # 4. 统一坐标（带开关）
        # 清除之前的所有组件，重新设计布局
        
        # 创建水平布局来容纳统一坐标的所有组件
        unified_coords_layout = QHBoxLayout()
        unified_coords_layout.setContentsMargins(0, 0, 0, 0)
        unified_coords_layout.setSpacing(0)
        
        # 1. 统一坐标复选框
        self.unified_coords_checkbox = QCheckBox()
        unified_coords_layout.addWidget(self.unified_coords_checkbox)
        
        # 2. 统一坐标标签
        unified_label = QLabel("统一坐标:")
        unified_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(unified_label)
        
        # 3. 空白间距
        unified_coords_layout.addSpacing(17)
        
        # 4. x坐标标签
        x_label = QLabel("X坐标:")
        x_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(x_label)
        
        # 5. x坐标输入框
        self.x_input = ModernLineEdit()
        self.x_input.setText("0")
        self.x_input.setFixedWidth(input_width)
        unified_coords_layout.addWidget(self.x_input)
        
        # 6. 空白间距
        unified_coords_layout.addSpacing(3)
        
        # 7. y坐标标签
        y_label = QLabel("Y坐标:")
        y_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        unified_coords_layout.addWidget(y_label)
        
        # 8. y坐标输入框
        self.y_input = ModernLineEdit()
        self.y_input.setText("0")
        self.y_input.setFixedWidth(input_width)
        unified_coords_layout.addWidget(self.y_input)
        
        # 9. 拉伸空间
        unified_coords_layout.addStretch()
        
        # 将整个水平布局添加到GridLayout中
        operation_layout.addLayout(unified_coords_layout, 3, 0, 1, 5, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # 将操作选项组添加到主布局
        layout.addWidget(operation_group)

        # 添加提示信息
        hint_label = QLabel("💡 提示：按键事件替换支持将事件列表中已有的按键事件替换为另一个已有的按键事件")
        hint_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px; background-color: transparent;")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addWidget(hint_label)
        
        # 按钮区域
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text="应用",
            cancel_text="取消"
        )
        layout.addLayout(button_layout)
        
        # 设置对话框布局
        self.setLayout(layout)
    
    def get_offset_adjustment(self):
        """获取偏移调整值（转换为毫秒）
        
        根据用户选择的时间单位，将偏移时间转换为毫秒。
        
        Returns:
            int: 偏移调整值（毫秒）
        """
        offset = self.offset_input.value()
        time_unit = self.offset_time_unit_combo.currentText()
        
        return convert_time_to_ms(offset, time_unit)
    
    def get_unified_rel_time(self):
        """获取统一相对时间值（转换为毫秒）
        
        根据用户选择的时间单位，将统一相对时间转换为毫秒。
        
        Returns:
            int: 统一相对时间值（毫秒）
        """
        rel_time = self.rel_time_input.value()
        time_unit = self.rel_time_unit_combo.currentText()
        
        return convert_time_to_ms(rel_time, time_unit)
    
    def get_type_replacement(self):
        """获取类型替换信息
        
        获取用户选择的事件类型替换信息，包括旧类型和新类型。
        如果用户选择"不替换类型"，则返回None。
        
        Returns:
            tuple: ((old_type, old_keycode), (new_type, new_keycode))
                    如果选择"不替换类型"，则返回 (None, None)
        """
        old_type_text = self.old_type_combo.currentText()
        new_type_text = self.new_type_combo.currentText()
        
        if old_type_text == "不替换类型":
            return None, None
        
        # 解析旧类型
        old_type = old_type_text
        old_keycode = None
        
        # 检查是否是按键事件名称
        if old_type in self.key_events:
            # 从key_events字典中获取事件类型和键码
            old_type, old_keycode = self.key_events[old_type]
        
        # 解析新类型
        new_type = new_type_text
        new_keycode = None
        
        # 检查是否是按键事件名称
        if new_type in self.key_events:
            # 从key_events字典中获取事件类型和键码
            new_type, new_keycode = self.key_events[new_type]
        
        return (old_type, old_keycode), (new_type, new_keycode)
    
    def get_unified_coordinates(self):
        """获取统一坐标值和应用标志
        
        获取用户选择的统一坐标值和是否应用标志。
        如果坐标输入无效，则使用默认值0。
        
        Returns:
            tuple: (apply_coords, x, y)
                    apply_coords: 是否应用统一坐标（bool）
                    x: X坐标值（int）
                    y: Y坐标值（int）
        """
        apply_coords = self.unified_coords_checkbox.isChecked()
        
        try:
            x = int(self.x_input.text())
        except ValueError:
            x = 0
        try:
            y = int(self.y_input.text())
        except ValueError:
            y = 0
        
        return apply_coords, x, y
    
    def refresh_theme_styles(self):
        """刷新控件的样式，应用当前主题"""
        # 调用父类的刷新方法（更新标题栏样式）
        super().refresh_theme_styles()
        
        # 刷新所有子控件
        from PyQt6.QtWidgets import QWidget
        for child in self.findChildren(QWidget):
            if hasattr(child, 'refresh_theme_styles'):
                child.refresh_theme_styles()