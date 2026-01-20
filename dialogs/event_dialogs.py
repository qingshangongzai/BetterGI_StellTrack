# event_dialogs.py
# 标准库模块导入
import os
import re

# 第三方模块导入
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QComboBox, QPushButton, QTableWidgetItem, QFrame, QGroupBox,
    QGridLayout, QScrollArea, QFileDialog, QSpinBox, QSizePolicy,
    QTextEdit
)

# 项目模块导入
from styles import (
    UnifiedStyleHelper,
    CenteredComboBox,
    CenteredLineEdit,
    TimeOffsetSpinBox,
    EventEditButton,
    StyledDialog,
    FadeInWindowMixin,
    AnimatedDialog,
    ModernGroupBox,
    ChineseMessageBox,
    DialogFactory
)
from utils import VK_MAPPING, KEY_NAME_MAPPING, KEY_PRESS_EVENTS, find_resource_file, convert_time_to_ms

# =============================================================================
# 事件编辑对话框相关组件
# =============================================================================

class SimpleCoordinateCapture(StyledDialog):
    """简化版坐标捕获对话框，用于从图片中选择坐标
    
    提供图片显示和鼠标交互功能，允许用户通过点击图片选择坐标点。
    支持图片缩放显示，自动计算原始图片坐标。
    
    功能特性：
    - 加载并显示图片
    - 鼠标移动时实时显示坐标
    - 点击确认选择坐标
    - 支持ESC键取消
    
    Args:
        image_path (str): 图片文件路径
    """
    
    def __init__(self, image_path):
        """初始化坐标捕获对话框
        
        Args:
            image_path (str): 图片文件路径
        """
        super().__init__()
        self.image_path = image_path
        self.pixmap = None
        self.selected_x = 0
        self.selected_y = 0
        self.init_ui()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("坐标捕获 - 点击图片选择坐标 (ESC取消)")
        self.setMinimumSize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 创建图片显示标签
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_coordinate_capture_label_style())
        layout.addWidget(self.image_label)
        
        # 加载图片
        if os.path.exists(self.image_path):
            self.pixmap = QPixmap(self.image_path)
            if not self.pixmap.isNull():
                # 调整图片大小以适应窗口
                scaled_pixmap = self.pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
                self.image_label.setPixmap(scaled_pixmap)
                self.original_size = self.pixmap.size()
                self.scaled_size = scaled_pixmap.size()
            else:
                ChineseMessageBox.show_error(self, "错误", "无法加载图片文件")
                self.close()
                return
        else:
            ChineseMessageBox.show_error(self, "错误", "图片文件不存在")
            self.close()
            return
            
        # 坐标显示标签
        self.coord_label = QLabel("移动鼠标选择坐标，点击左键确认，右键或ESC取消")
        self.coord_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 12px; padding: 10px;")
        self.coord_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.coord_label)
        
        # 按钮区域
        # 使用DialogFactory创建确定和取消按钮布局
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text="确认选择",
            cancel_text="取消"
        )
        layout.addLayout(button_layout)
        
        # 设置鼠标跟踪
        self.image_label.setMouseTracking(True)
        self.image_label.mouseMoveEvent = self.on_mouse_move
        self.image_label.mousePressEvent = self.on_mouse_press
        
    def on_mouse_move(self, event):
        """鼠标移动事件处理
        
        实时计算并显示鼠标在图片上的坐标位置。
        
        Args:
            event: 鼠标移动事件对象
        """
        if self.pixmap is None or self.pixmap.isNull():
            return
            
        # 计算在原始图片上的坐标
        pos = event.pos()
        label_size = self.image_label.size()
        
        # 计算图片在标签中的位置（居中显示）
        x_offset = (label_size.width() - self.scaled_size.width()) // 2
        y_offset = (label_size.height() - self.scaled_size.height()) // 2
        
        # 计算相对于图片的坐标
        x_in_image = pos.x() - x_offset
        y_in_image = pos.y() - y_offset
        
        # 转换为原始图片坐标
        if (0 <= x_in_image < self.scaled_size.width() and 
            0 <= y_in_image < self.scaled_size.height()):
            self.selected_x = int(x_in_image * self.original_size.width() / self.scaled_size.width())
            self.selected_y = int(y_in_image * self.original_size.height() / self.scaled_size.height())
            self.coord_label.setText(f"坐标: ({self.selected_x}, {self.selected_y}) - 点击左键确认，右键或ESC取消")
        else:
            self.coord_label.setText("移动鼠标选择坐标，点击左键确认，右键或ESC取消")
            
    def on_mouse_press(self, event):
        """鼠标点击事件处理
        
        左键点击确认坐标选择，右键点击取消选择。
        
        Args:
            event: 鼠标点击事件对象
        """
        if self.pixmap is None or self.pixmap.isNull():
            return
            
        if event.button() == Qt.MouseButton.LeftButton:
            # 计算在原始图片上的坐标
            pos = event.pos()
            label_size = self.image_label.size()
            
            # 计算图片在标签中的位置（居中显示）
            x_offset = (label_size.width() - self.scaled_size.width()) // 2
            y_offset = (label_size.height() - self.scaled_size.height()) // 2
            
            # 计算相对于图片的坐标
            x_in_image = pos.x() - x_offset
            y_in_image = pos.y() - y_offset
            
            # 转换为原始图片坐标
            if (0 <= x_in_image < self.scaled_size.width() and 
                0 <= y_in_image < self.scaled_size.height()):
                self.selected_x = int(x_in_image * self.original_size.width() / self.scaled_size.width())
                self.selected_y = int(y_in_image * self.original_size.height() / self.scaled_size.height())
                self.confirm_selection()
        elif event.button() == Qt.MouseButton.RightButton:
            self.reject()
            
    def confirm_selection(self):
        """确认选择坐标并关闭对话框"""
        self.accept()
            
    def keyPressEvent(self, event):
        """按键事件处理
        
        按ESC键取消选择，其他按键传递给父类处理。
        
        Args:
            event: 按键事件对象
        """
        if event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)



class EventEditDialog(FadeInWindowMixin, StyledDialog):
    """事件编辑对话框，用于添加和编辑各种类型的键鼠事件
    
    支持的事件类型包括：按键按下/释放、指针移动、平行移动、鼠标按键按下/释放、鼠标滚轮。
    提供直观的UI界面，允许用户设置事件名称、类型、键码、坐标和时间等参数。
    
    Args:
        parent: 父窗口实例
        event_data: 事件数据字典，用于编辑模式
        is_edit_mode: 是否为编辑模式
        insert_position: 插入位置（用于插入模式）
        insert_after_item: 插入后项目（用于插入模式）
        prev_absolute_time: 前一个事件的绝对时间
        current_row: 当前行号
        edit_logic: 编辑事件逻辑（'current' 或 'recalculate'），默认为 'current'
        default_time_unit: 默认时间单位（'auto', 'ms', 's', 'min'），默认为 'auto'
    """
    
    def __init__(self, parent=None, event_data=None, is_edit_mode=False, insert_position=None, insert_after_item=None, prev_absolute_time=0, current_row=None, edit_logic='current', default_time_unit='auto'):
        """初始化事件编辑对话框
        
        Args:
            parent: 父窗口实例
            event_data: 事件数据字典，用于编辑模式
            is_edit_mode: 是否为编辑模式
            insert_position: 插入位置（用于插入模式）
            insert_after_item: 插入后项目（用于插入模式）
            prev_absolute_time: 前一个事件的绝对时间
            current_row: 当前行号
            edit_logic: 编辑事件逻辑（'current' 或 'recalculate'），默认为 'current'
            default_time_unit: 默认时间单位（'auto', 'ms', 's', 'min'），默认为 'auto'
        """
        # 使用基类初始化方法设置窗口属性
        super().__init__(parent,
                       title="编辑事件" if is_edit_mode else "添加事件",
                       window_flags=Qt.WindowType.Dialog)
        
        self.event_data = event_data
        self.is_edit_mode = is_edit_mode
        self.insert_position = insert_position
        self.insert_after_item = insert_after_item
        self.prev_absolute_time = prev_absolute_time
        self.current_row = current_row
        self.edit_logic = edit_logic
        self.default_time_unit = default_time_unit
        self.key_capture_active = False
        
        try:
            # 设置最小尺寸和大小策略
            self.setMinimumSize(605, 415)  # 最小高度为原来的1/2
            self.setMaximumSize(605, 830)  # 最大高度为当前的默认高度
            self.resize(605, 830)  # 默认高度维持原来的最小高度大小
            self.setFixedWidth(605)  # 固定宽度为605px
            self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
            
            # 应用对话框背景样式
            self.setStyleSheet(UnifiedStyleHelper.get_instance().get_dialog_bg_style())
            
            self.setup_ui()
            self.setup_connections()
            
            if event_data:
                self.load_event_data(event_data)
            
        except (OSError, ValueError) as e:
            pass

    def setup_ui(self):
        """设置UI界面
        
        创建事件编辑对话框的所有UI组件，包括：
        - 事件基本信息组（事件名称、事件类型）
        - 键码设置组（键码输入、按键捕获、常用按键）
        - 坐标设置组（X/Y坐标、坐标捕获）
        - 时间设置组（相对时间、绝对时间、快速时间、时间修改选项）
        - 插入/编辑位置信息组
        - 确定和取消按钮
        """
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # 创建内容部件
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setSpacing(12)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # 事件基本信息组
        basic_info_group = ModernGroupBox("📋 事件基本信息")
        basic_layout = QGridLayout(basic_info_group)
        basic_layout.setVerticalSpacing(8)
        basic_layout.setHorizontalSpacing(15)
        
        # 事件名称
        basic_layout.addWidget(QLabel("事件名称:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.name_edit = CenteredLineEdit()
        self.name_edit.setFixedHeight(20)
        self.name_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        basic_layout.addWidget(self.name_edit, 0, 1)
        
        # 事件类型
        basic_layout.addWidget(QLabel("事件类型:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.type_combo = CenteredComboBox()
        self.type_combo.addItems(["按键按下", "按键释放", "指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"])
        self.type_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        basic_layout.addWidget(self.type_combo, 1, 1)
        
        layout.addWidget(basic_info_group)
        
        # 键码设置组
        keycode_group = ModernGroupBox("⌨️ 键码设置")
        keycode_layout = QVBoxLayout(keycode_group)
        keycode_layout.setSpacing(8)
        
        # 键码输入行
        keycode_row = QHBoxLayout()
        keycode_row.addWidget(QLabel("键码:"))
        self.keycode_edit = CenteredLineEdit()
        self.keycode_edit.setMaximumWidth(100)
        self.keycode_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        keycode_row.addWidget(self.keycode_edit)
        
        # 按键捕获按钮 - 合并为一个按钮
        self.capture_btn = EventEditButton("按键捕获")
        keycode_row.addWidget(self.capture_btn)
        
        # 捕获状态
        self.capture_status = QLabel("就绪")
        self.capture_status.setStyleSheet(UnifiedStyleHelper.get_instance().get_capture_status_style())
        keycode_row.addWidget(self.capture_status)
        
        keycode_row.addStretch()
        keycode_layout.addLayout(keycode_row)
        
        # 常用按键快速选择
        quick_keys_label = QLabel("常用按键:")
        quick_keys_label.setStyleSheet(UnifiedStyleHelper.get_instance().get_quick_keys_label_style())
        keycode_layout.addWidget(quick_keys_label)
        
        # 常用按键 - 分两行显示，统一宽度
        quick_keys_container = QWidget()
        quick_keys_layout = QVBoxLayout(quick_keys_container)
        quick_keys_layout.setSpacing(5)
        quick_keys_layout.setContentsMargins(0, 0, 0, 0)
        
        # 计算统一宽度（以最长的按钮文本为准）
        max_width = 70
        
        # 第一行：数字键和主要功能按键
        row1_layout = QHBoxLayout()
        common_keys_row1 = [
            ("1", "49"), ("2", "50"), ("3", "51"), ("4", "52"), ("5", "53"),
            ("回车", "13"), ("空格", "32")
        ]
        
        for key_name, key_code in common_keys_row1:
            btn = EventEditButton(key_name, fixed_width=max_width)
            btn.setProperty("key_code", key_code)
            btn.setProperty("key_name", key_name)
            btn.clicked.connect(self.on_common_key_clicked)
            row1_layout.addWidget(btn)
        
        row1_layout.addStretch()
        quick_keys_layout.addLayout(row1_layout)
        
        # 第二行：剩余功能键和修饰键
        row2_layout = QHBoxLayout()
        common_keys_row2 = [
            ("ESC", "27"), ("Tab", "9"), ("Shift", "16"), ("Ctrl", "17"), ("Alt", "18"),
            ("F1", "112"), ("F2", "113")
        ]
        
        for key_name, key_code in common_keys_row2:
            btn = EventEditButton(key_name, fixed_width=max_width)
            btn.setProperty("key_code", key_code)
            btn.setProperty("key_name", key_name)
            btn.clicked.connect(self.on_common_key_clicked)
            row2_layout.addWidget(btn)
        
        row2_layout.addStretch()
        quick_keys_layout.addLayout(row2_layout)
        
        keycode_layout.addWidget(quick_keys_container)
        
        layout.addWidget(keycode_group)
        
        # 坐标设置组
        coord_group = ModernGroupBox("📍 坐标设置")
        coord_layout = QVBoxLayout(coord_group)
        coord_layout.setSpacing(8)
        
        # 坐标输入行 - 使用水平布局居中
        coord_row = QHBoxLayout()
        coord_row.addStretch()
        
        # X坐标
        x_label = QLabel("X坐标:")
        x_label.setMinimumWidth(60)
        coord_row.addWidget(x_label)
        self.x_edit = CenteredLineEdit()
        self.x_edit.setText("0")
        self.x_edit.setMinimumWidth(120)
        self.x_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        coord_row.addWidget(self.x_edit)
        
        # 添加间距
        coord_row.addSpacing(20)
        
        # Y坐标
        y_label = QLabel("Y坐标:")
        y_label.setMinimumWidth(60)
        coord_row.addWidget(y_label)
        self.y_edit = CenteredLineEdit()
        self.y_edit.setText("0")
        self.y_edit.setMinimumWidth(120)
        self.y_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        coord_row.addWidget(self.y_edit)
        
        coord_row.addStretch()
        coord_layout.addLayout(coord_row)
        
        # 坐标捕获按钮
        self.coord_capture_btn = EventEditButton("通过截图定位获取坐标")
        coord_layout.addWidget(self.coord_capture_btn)
        
        layout.addWidget(coord_group)
        
        # 时间设置组
        time_group = ModernGroupBox("⏱️ 时间设置")
        time_layout = QGridLayout(time_group)
        time_layout.setVerticalSpacing(8)
        time_layout.setHorizontalSpacing(15)
        
        # 相对时间偏移
        time_layout.addWidget(QLabel("相对时间偏移:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
        time_input_layout = QHBoxLayout()
        time_input_layout.setSpacing(5)
        
        # 使用TimeOffsetSpinBox控件，支持上下调节按钮，根据时间单位动态调整步长
        self.time_edit = TimeOffsetSpinBox()
        self.time_edit.setMaximumWidth(100)
        self.time_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        # 初始设置为ms单位，步长为100
        self.time_edit.update_step_based_on_unit("ms")
        time_input_layout.addWidget(self.time_edit)
        
        self.time_unit_combo = CenteredComboBox()
        self.time_unit_combo.addItems(["ms", "s", "min"])
        self.time_unit_combo.setMinimumWidth(80)
        self.time_unit_combo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        time_input_layout.addWidget(self.time_unit_combo)
        
        # 应用默认时间单位设置（如果不是系统自动匹配）
        if self.default_time_unit != 'auto':
            self.time_unit_combo.setCurrentText(self.default_time_unit)
            # 根据默认时间单位更新步长
            self.time_edit.update_step_based_on_unit(self.default_time_unit)
        
        # 添加伸缩空间，将绝对偏移时间组件推到右侧
        time_input_layout.addStretch()
        
        # 绝对偏移时间显示
        abs_time_label = QLabel("绝对偏移时间:")
        abs_time_label.setMinimumWidth(100)
        time_input_layout.addWidget(abs_time_label)
        self.absolute_time_edit = CenteredLineEdit()
        self.absolute_time_edit.setMaximumWidth(120)
        self.absolute_time_edit.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.absolute_time_edit.setReadOnly(True)
        self.absolute_time_edit.setStyleSheet(UnifiedStyleHelper.get_instance().get_absolute_time_edit_style())
        time_input_layout.addWidget(self.absolute_time_edit)
        
        time_layout.addLayout(time_input_layout, 0, 1)
        
        # 快速时间按钮 - 分两行显示
        time_layout.addWidget(QLabel("快速时间:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
        quick_time_container = QWidget()
        quick_time_layout = QVBoxLayout(quick_time_container)
        quick_time_layout.setSpacing(5)
        quick_time_layout.setContentsMargins(0, 0, 0, 0)
        
        # 第一行按钮
        row1_layout = QHBoxLayout()
        time_presets_row1 = [
            ("100", "100"), ("200", "200"), ("300", "300"), 
            ("400", "400"), ("500", "500"), ("600", "600")
        ]
        
        # 第二行按钮 - 新增选项
        row2_layout = QHBoxLayout()
        time_presets_row2 = [
            ("1", "1"), ("2", "2"), ("3", "3"), 
            ("4", "4"), ("5", "5"), ("10", "10")
        ]
        
        # 使用相同的固定宽度
        time_btn_width = 70
        
        # 添加第一行按钮
        for time_name, time_value in time_presets_row1:
            btn = EventEditButton(time_name, fixed_width=time_btn_width)
            btn.setProperty("time_value", time_value)
            btn.clicked.connect(self.on_quick_time_clicked)
            row1_layout.addWidget(btn)
        row1_layout.addStretch()
        
        # 添加第二行按钮
        for time_name, time_value in time_presets_row2:
            btn = EventEditButton(time_name, fixed_width=time_btn_width)
            btn.setProperty("time_value", time_value)
            btn.clicked.connect(self.on_quick_time_clicked)
            row2_layout.addWidget(btn)
        row2_layout.addStretch()
        
        quick_time_layout.addLayout(row1_layout)
        quick_time_layout.addLayout(row2_layout)
        
        time_layout.addWidget(quick_time_container, 1, 1)
        
        # 时间修改选项
        time_layout.addWidget(QLabel("时间修改选项:"), 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.time_option_combo = CenteredComboBox()
        self.time_option_combo.addItems(["仅修改当前事件时间", "修改后重新计算后续事件时间"])
        self.time_option_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # 根据edit_logic设置默认选项
        if self.edit_logic == 'current':
            self.time_option_combo.setCurrentText("仅修改当前事件时间")
        elif self.edit_logic == 'recalculate':
            self.time_option_combo.setCurrentText("修改后重新计算后续事件时间")
        
        time_layout.addWidget(self.time_option_combo, 2, 1)
        
        # 绝对偏移时间信息
        absolute_time_info = QLabel("绝对偏移时间将根据相对偏移自动计算")
        absolute_time_info.setStyleSheet(UnifiedStyleHelper.get_instance().get_absolute_time_info_style())
        time_layout.addWidget(absolute_time_info, 3, 0, 1, 2)
        
        layout.addWidget(time_group)
        
        # 位置信息 - 新增
        group_title = "📌 插入位置信息" if not self.is_edit_mode else "📌 编辑位置信息"
        insert_info_group = ModernGroupBox(group_title)
        insert_info_layout = QVBoxLayout(insert_info_group)
        insert_info_layout.setSpacing(8)
        
        # 位置显示
        if not self.is_edit_mode:
            self.insert_position_label = QLabel("将在最后添加事件")
        else:
            current_event_number = self.current_row + 1 if self.current_row is not None else ""
            self.insert_position_label = QLabel(f"正在编辑事件 {current_event_number}")
        
        # 设置样式：居中显示，使用primary颜色（与事件后插入新事件的颜色一致）
        self.insert_position_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.insert_position_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-size: 10px;")
        insert_info_layout.addWidget(self.insert_position_label)
        
        layout.addWidget(insert_info_group)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 设置滚动区域的内容
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
        # 使用DialogFactory创建确定和取消按钮布局，直接使用EventEditButton类
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.on_save,
            on_cancel=self.reject,
            ok_text="保存",
            cancel_text="取消",
            button_class=EventEditButton
        )
        
        # 获取按钮引用，以便后续使用
        self.save_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        self.cancel_btn = button_layout.itemAt(2).widget()
        
        main_layout.addLayout(button_layout)

    def setup_connections(self):
        """设置信号连接
        
        连接所有UI组件的信号到对应的槽函数：
        - 按键捕获按钮
        - 坐标捕获按钮
        - 事件类型变化
        - 键码变化
        - 时间相关变化（相对时间、时间单位）
        """
        # 按钮连接 - save_btn和cancel_btn的信号已在DialogFactory中连接
        self.capture_btn.clicked.connect(self.toggle_key_capture)
        self.coord_capture_btn.clicked.connect(self.on_coordinate_capture)
        
        # 事件类型变化
        self.type_combo.currentTextChanged.connect(self.on_event_type_changed)
        
        # 键码变化
        self.keycode_edit.textChanged.connect(self.on_keycode_changed)
        
        # 时间相关变化 - 新增
        self.time_edit.valueChanged.connect(self.update_absolute_time)
        self.time_unit_combo.currentTextChanged.connect(self.update_absolute_time)
        # 当时间单位改变时，更新步长
        self.time_unit_combo.currentTextChanged.connect(self.time_edit.update_step_based_on_unit)

    def toggle_key_capture(self):
        """切换按键捕获状态
        
        在按键捕获和非捕获状态之间切换。
        """
        if self.key_capture_active:
            self.on_key_capture_cancel()
        else:
            self.on_key_capture_start()

    def on_coordinate_capture(self):
        """坐标捕获按钮点击事件处理
        
        打开文件对话框选择截图文件，然后显示坐标捕获对话框。
        用户可以在图片上点击选择坐标。
        """
        # 打开文件对话框选择图片
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "选择截图文件", 
            "", 
            "图片文件 (*.png *.jpg *.jpeg *.bmp *.gif);;所有文件 (*.*)"
        )
        
        if file_path:
            try:
                capture_dialog = SimpleCoordinateCapture(file_path)
                if capture_dialog.exec() == QDialog.DialogCode.Accepted:
                    # 获取选择的坐标并填充
                    self.x_edit.setText(str(capture_dialog.selected_x))
                    self.y_edit.setText(str(capture_dialog.selected_y))
            except Exception as e:
                ChineseMessageBox.show_error(self, "错误", f"坐标捕获失败: {str(e)}")

    def load_event_data(self, event_data):
        """加载事件数据到对话框
        
        将事件数据填充到对话框的各个输入框中。
        根据时间值自动选择合适的时间单位（ms/s/min）。
        
        Args:
            event_data (tuple): 事件数据元组，包含（事件名称、事件类型、键码、X坐标、Y坐标、相对时间）
        """
        if len(event_data) >= 7:
            # 设置加载数据标志，防止on_event_type_changed覆盖自定义名称
            self._loading_data = True
            
            try:
                # 先保存事件数据
                saved_name = event_data[0]
                event_type = event_data[1]
                keycode = event_data[2]
                x = event_data[3]
                y = event_data[4]
                
                # 关键修复：正确处理相对时间
                relative_time = event_data[5]  # 这应该是毫秒值
                
                # 先加载除事件类型外的所有数据
                self.keycode_edit.setText(keycode)
                self.x_edit.setText(x)
                self.y_edit.setText(y)
                
                # 处理时间数据
                try:
                    relative_time_ms = int(relative_time)
                    
                    # 如果不是系统自动匹配，使用默认时间单位
                    if self.default_time_unit != 'auto':
                        if self.default_time_unit == 'min':
                            # 显示为分钟
                            self.time_edit.setValue(relative_time_ms // 60000)
                            self.time_unit_combo.setCurrentText("min")
                        elif self.default_time_unit == 's':
                            # 显示为秒
                            self.time_edit.setValue(relative_time_ms // 1000)
                            self.time_unit_combo.setCurrentText("s")
                        else:  # 'ms'
                            # 显示为毫秒
                            self.time_edit.setValue(relative_time_ms)
                            self.time_unit_combo.setCurrentText("ms")
                    else:
                        # 系统自动匹配（原有逻辑）
                        if relative_time_ms >= 60000:
                            # 大于1分钟，显示为分钟
                            self.time_edit.setValue(relative_time_ms // 60000)
                            self.time_unit_combo.setCurrentText("min")
                        elif relative_time_ms >= 1000:
                            # 大于1秒，显示为秒
                            self.time_edit.setValue(relative_time_ms // 1000)
                            self.time_unit_combo.setCurrentText("s")
                        else:
                            # 小于1秒，显示为毫秒
                            self.time_edit.setValue(relative_time_ms)
                            self.time_unit_combo.setCurrentText("ms")
                except ValueError:
                    # 如果转换失败，默认显示100ms
                    self.time_edit.setValue(100)
                    self.time_unit_combo.setCurrentText("ms")
                
                # 更新绝对偏移时间显示 - 新增
                self.update_absolute_time()
                
                # 最后加载事件名称和事件类型
                self.name_edit.setText(saved_name)
                self.type_combo.setCurrentText(event_type)
            finally:
                # 清除加载数据标志
                self._loading_data = False

    def get_event_data(self):
        """获取对话框中的事件数据
        
        将用户输入的数据转换为事件数据元组。
        时间值会根据选择的单位自动转换为毫秒。
        
        Returns:
            tuple: 事件数据元组，包含（事件名称、事件类型、键码、X坐标、Y坐标、相对时间ms）
        """
        try:
            # 获取相对时间并转换为毫秒
            relative_time = self.time_edit.value()
            time_unit = self.time_unit_combo.currentText()
            relative_time_ms = convert_time_to_ms(relative_time, time_unit)
            
            return (
                self.name_edit.text(),
                self.type_combo.currentText(),
                self.keycode_edit.text(),
                self.x_edit.text(),
                self.y_edit.text(),
                str(relative_time_ms)  # 确保返回的是毫秒
            )
        except ValueError:
            # 如果转换失败，返回默认值
            return (
                self.name_edit.text(),
                self.type_combo.currentText(),
                self.keycode_edit.text(),
                self.x_edit.text(),
                self.y_edit.text(),
                "100"  # 默认100ms
            )

    def get_time_option(self):
        """获取时间修改选项
        
        Returns:
            str: 时间修改选项文本
        """
        return self.time_option_combo.currentText()

    def on_save(self):
        """保存事件
        
        验证必填字段和数字字段，如果验证通过则接受对话框。
        """
        # 验证必填字段
        if not self.name_edit.text().strip():
            ChineseMessageBox.show_warning(self, "警告", "请填写事件名称")
            return
        
        # 验证数字字段
        try:
            # 坐标可以为空，默认为0
            x_text = self.x_edit.text().strip()
            y_text = self.y_edit.text().strip()
            
            # 验证坐标格式
            int(x_text) if x_text else 0
            int(y_text) if y_text else 0
            
            # 如果是键盘事件，验证键码
            if self.keycode_edit.text().strip() and self.type_combo.currentText() in KEY_PRESS_EVENTS:
                int(self.keycode_edit.text())
        except ValueError:
            ChineseMessageBox.show_warning(self, "警告", "坐标和键码必须为数字")
            return
        
        self.accept()

    def on_key_capture_start(self):
        """开始按键捕获
        
        设置对话框焦点，等待用户按下键盘按键。
        """
        self.key_capture_active = True
        self.capture_btn.setText("取消捕获")
        self.capture_status.setText("等待按键...")
        self.capture_status.setStyleSheet(UnifiedStyleHelper.get_instance().get_capture_status_style("active"))
        
        # 设置焦点以便捕获按键
        self.setFocus()

    def on_key_capture_cancel(self):
        """取消按键捕获
        
        恢复到非捕获状态。
        """
        self.key_capture_active = False
        self.capture_btn.setText("按键捕获")
        self.capture_status.setText("已取消")
        self.capture_status.setStyleSheet(UnifiedStyleHelper.get_instance().get_capture_status_style("inactive"))

    def on_common_key_clicked(self):
        """常用按键点击事件处理
        
        将选中的常用按键的键码填入键码输入框。
        如果是按键事件，自动生成事件名称。
        """
        sender = self.sender()
        key_code = sender.property("key_code")
        key_name = sender.property("key_name")
        
        self.keycode_edit.setText(key_code)
        
        # 自动生成事件名称
        event_type = self.type_combo.currentText()
        if event_type in KEY_PRESS_EVENTS:
            action = "按下" if event_type == "按键按下" else "释放"
            self.name_edit.setText(f"{action}{key_name}")

    def on_quick_time_clicked(self):
        """快速时间按钮点击事件处理
        
        将选中的快速时间值填入时间输入框。
        """
        sender = self.sender()
        time_value = sender.property("time_value")
        
        # 直接使用不带单位的数值
        try:
            self.time_edit.setValue(int(time_value))
        except (ValueError, TypeError):
            pass

    def on_event_type_changed(self, event_type):
        """事件类型变化处理
        
        根据选择的事件类型自动更新事件名称和键码。
        如果是加载事件数据时触发，则不自动更新事件名称。
        
        Args:
            event_type (str): 新的事件类型
        """
        # 获取当前事件名称
        current_name = self.name_edit.text().strip()
        
        # 判断是否为加载事件数据时触发
        # 如果是，不自动更新事件名称
        if hasattr(self, '_loading_data') and self._loading_data:
            return
        
        # 定义鼠标事件类型列表
        mouse_event_types = ["指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
        
        # 判断是否为自定义名称的辅助函数
        def is_custom_name(name):
            """判断是否为自定义名称（非系统自动生成）"""
            import re
            # 1. 空名称不是自定义
            if not name:
                return False
            # 2. 包含数字后缀的是自定义（如 "按下回车-1", "鼠标滚轮-2"）
            if re.search(r'-\d+$', name):
                return True
            # 3. 精确匹配系统生成的鼠标事件名称
            if name in mouse_event_types:
                return False
            # 4. 精确匹配系统生成的按键事件名称格式："按下XXX" 或 "释放XXX"
            # 系统格式：动作在前，按键名称在后，且前面没有其他内容
            if re.match(r'^(按下|释放).+$', name):
                # 检查是否严格匹配系统格式（动作必须在开头，且后面是按键名称）
                if re.match(r'^(按下|释放)[^按下释放]+$', name):
                    # 这可能是系统生成的，但如果不在常见按键名称中，则是自定义
                    # 为安全起见，只有完全匹配已知格式才认为是系统生成
                    return False
            # 5. 其他所有情况都是自定义（如 "a按下回车", "自定义操作" 等）
            return True
        
        if event_type in mouse_event_types:
            # 选择鼠标事件
            # 只有非自定义名称才自动填充
            if not is_custom_name(current_name):
                # 更新为鼠标事件名称
                self.name_edit.setText(event_type)
            # 清空键码（鼠标事件不需要键码）
            self.keycode_edit.clear()
        elif event_type in KEY_PRESS_EVENTS:
            # 选择按键事件
            # 检查是否需要自动填充
            should_auto_fill = False
            
            # 情况1：名称为空
            if not current_name:
                should_auto_fill = True
            # 情况2：当前是鼠标事件名称
            elif current_name in mouse_event_types:
                should_auto_fill = True
            # 情况3：当前是系统生成的按键事件，但动作不匹配
            elif not is_custom_name(current_name):
                expected_action = "按下" if event_type == "按键按下" else "释放"
                if expected_action not in current_name:
                    should_auto_fill = True
                else:
                    # 动作匹配的系统生成名称也需要更新
                    should_auto_fill = True
            
            if should_auto_fill:
                # 如果有键码，更新事件名称
                keycode = self.keycode_edit.text().strip()
                if keycode:
                    try:
                        keycode_int = int(keycode)
                        # 使用虚拟键码映射
                        key_name = VK_MAPPING.get(keycode_int, f"键码:{keycode}")
                        # 转换为中文名称
                        key_name_cn = KEY_NAME_MAPPING.get(key_name, key_name)
                        action = "按下" if event_type == "按键按下" else "释放"
                        auto_name = f"{action}{key_name_cn}"
                        self.name_edit.setText(auto_name)
                    except ValueError:
                        # 如果键码不是数字，忽略
                        pass
                else:
                    # 如果没有键码，清空事件名称
                    self.name_edit.clear()

    def on_keycode_changed(self, keycode):
        """键码变化处理
        
        根据输入的键码自动生成事件名称。
        如果是鼠标事件且输入了键码，提示冲突并清空键码。
        
        Args:
            keycode (str): 新的键码值
        """
        if self.type_combo.currentText() in KEY_PRESS_EVENTS and keycode.strip():
            try:
                keycode_int = int(keycode)
                # 使用虚拟键码映射
                key_name = VK_MAPPING.get(keycode_int, f"键码:{keycode}")
                # 转换为中文名称
                key_name_cn = KEY_NAME_MAPPING.get(key_name, key_name)
                event_type = self.type_combo.currentText()
                action = "按下" if event_type == "按键按下" else "释放"
                auto_name = f"{action}{key_name_cn}"
                
                # 获取当前事件名称
                current_name = self.name_edit.text().strip()
                
                # 判断是否为自定义名称
                def is_custom_name(name):
                    """判断是否为自定义名称（非系统自动生成）"""
                    if not name:
                        return False
                    # 包含数字后缀的是自定义
                    if re.search(r'-\d+$', name):
                        return True
                    # 精确匹配系统生成的鼠标事件名称
                    mouse_event_types = ["指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"]
                    if name in mouse_event_types:
                        return False
                    # 精确匹配系统生成的按键事件名称格式
                    if re.match(r'^(按下|释放).+$', name):
                        if re.match(r'^(按下|释放)[^按下释放]+$', name):
                            return False
                    # 其他情况都是自定义
                    return True
                
                # 只有非自定义名称才自动填充
                if not is_custom_name(current_name):
                    self.name_edit.setText(auto_name)
            except ValueError:
                # 如果键码不是数字，忽略
                pass
        elif self.type_combo.currentText() in ["指针移动", "平行移动", "左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "鼠标滚轮"] and keycode.strip():
            # 鼠标事件时输入了键码，提示冲突
            ChineseMessageBox.show_warning(self, "事件类型冲突", "鼠标事件不需要键码")
            self.keycode_edit.clear()

    def calculate_absolute_offset(self):
        """计算绝对偏移时间
        
        绝对偏移时间 = 前面所有事件的累计相对时间 + 当前事件的相对时间
        
        Returns:
            int: 绝对偏移时间（毫秒）
        """
        try:
            # 获取当前事件的相对时间（转换为ms）
            relative_time = self.time_edit.value()
            time_unit = self.time_unit_combo.currentText()
            relative_time_ms = convert_time_to_ms(relative_time, time_unit)
            
            # 计算绝对偏移时间：前面事件累计时间 + 当前事件相对时间
            absolute_offset = self.prev_absolute_time + relative_time_ms
            
            return absolute_offset
        except Exception:
            return 0
    
    def update_absolute_time(self):
        """更新绝对偏移时间显示"""
        absolute_offset = self.calculate_absolute_offset()
        self.absolute_time_edit.setText(f"{absolute_offset}")
    
    def keyPressEvent(self, event):
        """按键事件处理 - 用于捕获按键
        
        如果处于按键捕获状态，捕获按下的键并填入键码输入框。
        否则将事件传递给父类处理。
        
        Args:
            event: 按键事件对象
        """
        if self.key_capture_active:
            # 获取虚拟键码
            key_code = event.nativeVirtualKey()
            
            # 使用虚拟键码映射
            key_name = VK_MAPPING.get(key_code, f"键码:{key_code}")
            # 转换为中文名称
            key_name_cn = KEY_NAME_MAPPING.get(key_name, key_name)
            
            # 设置键码和名称
            self.keycode_edit.setText(str(key_code))
            
            # 自动生成事件名称
            event_type = self.type_combo.currentText()
            if event_type in KEY_PRESS_EVENTS:
                action = "按下" if event_type == "按键按下" else "释放"
                self.name_edit.setText(f"{action}{key_name_cn}")
            
            # 更新状态
            self.capture_status.setText(f"已捕获: {key_name_cn}")
            self.capture_status.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['success']};")
            
            # 结束捕获状态
            self.key_capture_active = False
            self.capture_btn.setText("按键捕获")
            
            # 阻止事件继续传播
            event.accept()
        else:
            super().keyPressEvent(event)

    def update_insert_position_info(self, insert_position, insert_after_item=None):
        """更新插入位置信息显示
        
        根据插入位置和插入后项目更新位置信息标签。
        
        Args:
            insert_position: 插入位置
            insert_after_item: 插入后项目（可选）
        """
        if hasattr(self, 'insert_position_label'):
            if insert_after_item is not None:
                # 在指定事件后插入
                self.insert_position_label.setText(f"将在事件 {insert_after_item + 1} 后插入新事件")
            elif insert_position == 0:
                # 在第一个事件前插入
                self.insert_position_label.setText("将在第一个事件前插入新事件")
            else:
                # 在指定位置插入
                self.insert_position_label.setText(f"将在事件 {insert_position} 处插入新事件")
            self.insert_position_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-size: 10px;")

# =============================================================================
# 粘贴选项对话框
# =============================================================================

class PasteOptionsDialog(AnimatedDialog):
    """粘贴选项对话框，用于设置事件粘贴时的选项
    
    允许用户选择粘贴事件时的时间处理方式，以适应不同的场景需求。
    
    提供的时间修改选项包括：
    - 仅修改当前事件时间：根据复制事件原有的相对时间，调整绝对时间
    - 修改后重新计算后续事件时间：在粘贴位置之后的事件的时间都要重新计算
    
    Args:
        parent: 父窗口实例
    """
    
    def __init__(self, parent=None):
        """初始化粘贴选项对话框
        
        Args:
            parent: 父窗口实例
        """
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面
        
        创建粘贴选项对话框的所有UI组件，包括：
        - 标题标签
        - 时间修改选项下拉框
        - 选项说明文本框
        - 确定和取消按钮
        """
        self.setWindowTitle("粘贴选项")
        self.setMinimumWidth(400)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_event_dialog_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("请选择粘贴选项")
        title_label.setStyleSheet(f"font-weight: bold; color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 时间修改选项
        time_option_label = QLabel("时间修改选项:")
        time_option_label.setStyleSheet(f"font-weight: bold;")
        layout.addWidget(time_option_label)
        
        self.time_option_combo = CenteredComboBox()
        self.time_option_combo.addItems(["仅修改当前事件时间", "修改后重新计算后续事件时间"])
        layout.addWidget(self.time_option_combo)
        
        # 说明文本
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        explanation.setPlainText("""选项说明：

• 仅修改当前事件时间：
  根据复制事件原有的相对时间，调整绝对时间
  粘贴后原先下一个事件的绝对时间不变，计算相对时间

• 修改后重新计算后续事件时间：
  在粘贴位置之后的事件的时间都要重新计算
  例如：第1s和第3s之间插入事件，第3s的事件延后执行""")
        explanation.setMaximumHeight(180)
        explanation.setStyleSheet(UnifiedStyleHelper.get_instance().get_explanation_text_edit_style())
        layout.addWidget(explanation)
        
        # 使用DialogFactory创建确定和取消按钮布局
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text="确定",
            cancel_text="取消"
        )
        
        # 获取按钮并保存引用
        self.ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        self.cancel_btn = button_layout.itemAt(2).widget()
        
        layout.addLayout(button_layout)
    
    def get_time_option(self):
        """获取时间修改选项"""
        return self.time_option_combo.currentText()

    # =============================================================================
# 删除选项对话框
# =============================================================================

class DeleteOptionsDialog(AnimatedDialog):
    """删除选项对话框，用于设置事件删除时的选项
    
    允许用户选择删除事件后如何处理后续事件的时间。
    
    提供的删除选项包括：
    - 仅修改当前事件时间：删除事件后，后续事件的绝对时间不变
    - 修改后重新计算后续事件时间：删除事件后，重新计算后续所有事件的绝对时间
    
    Args:
        parent: 父窗口实例
    """
    
    def __init__(self, parent=None):
        """初始化删除选项对话框
        
        Args:
            parent: 父窗口实例
        """
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面
        
        创建删除选项对话框的所有UI组件，包括：
        - 标题标签
        - 时间修改选项下拉框
        - 选项说明文本框
        - 确定和取消按钮
        """
        self.setWindowTitle("删除选项")
        self.setMinimumWidth(400)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_event_dialog_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("请选择删除选项")
        title_label.setStyleSheet(f"font-weight: bold; color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-size: 14px;")
        layout.addWidget(title_label)
        
        # 时间修改选项
        time_option_label = QLabel("时间修改选项:")
        time_option_label.setStyleSheet(f"font-weight: bold;")
        layout.addWidget(time_option_label)
        
        self.time_option_combo = CenteredComboBox()
        self.time_option_combo.addItems(["仅修改当前事件时间", "修改后重新计算后续事件时间"])
        layout.addWidget(self.time_option_combo)
        
        # 说明文本
        explanation = QTextEdit()
        explanation.setReadOnly(True)
        explanation.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        explanation.setPlainText("""选项说明：

• 仅修改当前事件时间：
  删除事件后，后续事件的绝对时间不变
  仅重新计算删除位置后一个事件的相对时间

• 修改后重新计算后续事件时间：
  删除事件后，重新计算后续所有事件的绝对时间
  保持每个事件的相对时间不变，确保时间连续性""")
        explanation.setMaximumHeight(180)
        explanation.setStyleSheet(UnifiedStyleHelper.get_instance().get_explanation_text_edit_style())
        layout.addWidget(explanation)
        
        # 使用DialogFactory创建确定和取消按钮布局
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text="确定",
            cancel_text="取消"
        )
        
        # 获取按钮并保存引用
        self.ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        self.cancel_btn = button_layout.itemAt(2).widget()
        
        layout.addLayout(button_layout)
    
    def get_time_option(self):
        """获取时间修改选项"""
        return self.time_option_combo.currentText()

