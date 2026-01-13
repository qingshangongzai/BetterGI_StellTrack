# batch_edit_dialog.py

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, 
    QTableWidget, QTableWidgetItem, QFrame, QGroupBox, QGridLayout,
    QHeaderView, QScrollArea, QSizePolicy, QSplitter,
    QMessageBox, QStatusBar, QFileDialog, QDialog, QMenu, QMenuBar,
    QCheckBox
)

from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor

# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager, ChineseMessageBox, ModernGroupBox, ModernLineEdit, ModernComboBox, ModernDoubleSpinBox, StyledDialog, DialogFactory
from styles.widgets import FadeInWindowMixin


class BatchEditDialog(FadeInWindowMixin, StyledDialog):
    """批量编辑对话框"""
    
    def __init__(self, parent=None, selected_rows=None, events_table=None):
        super().__init__(parent)
        self.selected_rows = selected_rows or []
        self.events_table = events_table

        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("批量编辑事件")
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题区域
        title_label = QLabel("批量编辑事件")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 16, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
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
        self.offset_input = ModernDoubleSpinBox(width=input_width)
        self.offset_input.setMinimum(-999999)
        self.offset_input.setMaximum(999999)
        self.offset_input.setValue(0)
        self.offset_input.setDecimals(0)
        self.offset_input.setSingleStep(100)

        offset_label_unit = QLabel("ms")
        offset_label_unit.setFixedWidth(20)
        offset_label_unit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        operation_layout.addWidget(offset_label, 0, 0)
        operation_layout.addWidget(self.offset_input, 0, 1)
        operation_layout.addWidget(offset_label_unit, 0, 2)

        # 2. 统一相对时间
        rel_time_label = QLabel("统一相对时间:")
        rel_time_label.setFixedWidth(120)
        self.rel_time_input = ModernDoubleSpinBox(width=input_width)
        self.rel_time_input.setMinimum(0)
        self.rel_time_input.setMaximum(999999)
        self.rel_time_input.setValue(0)
        self.rel_time_input.setDecimals(0)
        self.rel_time_input.setSingleStep(100)

        rel_time_label_unit = QLabel("ms")
        rel_time_label_unit.setFixedWidth(20)
        rel_time_label_unit.setAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignCenter)

        operation_layout.addWidget(rel_time_label, 1, 0)
        operation_layout.addWidget(self.rel_time_input, 1, 1)
        operation_layout.addWidget(rel_time_label_unit, 1, 2)

        
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
                    if event_type in ["按键按下", "按键释放"] and keycode:
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
                        elif event_type in ["按键按下", "按键释放"] and event_name_item:
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
        """获取偏移调整值"""
        return int(self.offset_input.value())
    
    def get_unified_rel_time(self):
        """获取统一相对时间值"""
        return int(self.rel_time_input.value())
    
    def get_type_replacement(self):
        """获取类型替换信息"""
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
        """获取统一坐标值和应用标志"""
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