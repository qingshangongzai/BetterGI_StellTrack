# event_timeline.py - 事件可视化时间轴工具
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QWidget, QScrollArea, QMessageBox, QFileDialog, QGroupBox)
from PyQt6.QtCore import Qt, QPoint, QRect, QSize
from PyQt6.QtGui import (QPainter, QPen, QBrush, QColor, QFont, QPixmap, 
                        QPainterPath, QMouseEvent, QWheelEvent)
from styles import StyleHelper, StyledDialog, ModernGroupBox
from utils import convert_event_type_num_to_str_with_button, generate_key_event_name

class EventTimelineDialog(StyledDialog):
    """事件可视化时间轴对话框"""
    
    def __init__(self, parent=None, events_table=None):
        super().__init__(parent, title="事件可视化时间轴", size=(1000, 600))
        self.events_table = events_table
        self.events = []
        
        # 时间轴配置
        self.min_time = 0
        self.max_time = 1000
        self.zoom_level = 1.0
        self.offset = 0
        self.selected_event = None
        
        # 鼠标状态
        self.is_dragging = False
        self.last_mouse_pos = QPoint()
        
        # 颜色配置
        self.colors = {
            'background': '#ffffff',
            'line': StyleHelper.COLORS['border'],
            'text': StyleHelper.COLORS['text'],
            'text_secondary': StyleHelper.COLORS['text_secondary'],
            'event_point': StyleHelper.COLORS['primary'],
            'event_line': StyleHelper.COLORS['primary_hover'],
            'selected': StyleHelper.COLORS['primary_pressed'],
            'grid': StyleHelper.COLORS['grid']
        }
        
        # 先创建UI，再加载事件，确保timeline_widget已存在
        self.setup_ui()
        self.load_events()
    
    def load_events(self):
        """从事件表格加载事件数据，使用绝对偏移时间"""
        if not self.events_table:
            return
        
        self.events = []
        row_count = self.events_table.rowCount()
        
        for row in range(row_count):
            try:
                # 检查单元格是否存在
                if (self.events_table.item(row, 1) is None or
                    self.events_table.item(row, 2) is None or
                    self.events_table.item(row, 3) is None or
                    self.events_table.item(row, 4) is None or
                    self.events_table.item(row, 5) is None or
                    self.events_table.item(row, 6) is None or
                    self.events_table.item(row, 7) is None):
                    continue
                
                # 获取事件数据
                event_name = self.events_table.item(row, 1).text()
                event_type = self.events_table.item(row, 2).text()
                key_code = self.events_table.item(row, 3).text()
                x_coord = self.events_table.item(row, 4).text()
                y_coord = self.events_table.item(row, 5).text()
                relative_time = int(self.events_table.item(row, 6).text())
                absolute_time = int(self.events_table.item(row, 7).text())
                
                # 创建事件对象
                event = {
                    'name': event_name,
                    'type': event_type,
                    'key_code': key_code,
                    'x': x_coord,
                    'y': y_coord,
                    'relative_time': relative_time,
                    'absolute_time': absolute_time,
                    'row': row
                }
                
                self.events.append(event)
            except Exception as e:
                # 静默处理错误，避免影响用户体验
                continue
        
        # 按绝对时间排序事件
        self.events.sort(key=lambda x: x['absolute_time'])
        
        # 计算时间范围（使用绝对时间）
        if self.events:
            # 获取所有事件的绝对时间
            absolute_times = [event['absolute_time'] for event in self.events]
            self.min_time = min(absolute_times)
            self.max_time = max(absolute_times)
            
            # 确保时间范围覆盖所有事件，不添加额外边距
            time_range = self.max_time - self.min_time
            if time_range == 0:
                # 如果所有事件都在同一时间点，设置合理的时间范围
                self.min_time -= 100
                self.max_time += 100
            
            print(f"[DEBUG] 事件时间范围: {self.min_time}ms - {self.max_time}ms")
            
            # 确保timeline_widget也使用这个时间范围
            self.timeline_widget.min_time = self.min_time
            self.timeline_widget.max_time = self.max_time
        else:
            # 设置默认时间范围
            self.min_time = 0
            self.max_time = 1000
            
            # 确保timeline_widget也使用这个时间范围
            self.timeline_widget.min_time = self.min_time
            self.timeline_widget.max_time = self.max_time
        
        # 计算同一时间点的事件数量，用于绘制时避免重叠
        self.event_overlap = {}
        
        if self.events:
            # 按绝对时间分组事件
            time_groups = {}
            for event in self.events:
                time_key = event['absolute_time']
                if time_key not in time_groups:
                    time_groups[time_key] = []
                time_groups[time_key].append(event)
            
            # 计算每个时间点的事件数量
            for time_key, events in time_groups.items():
                self.event_overlap[time_key] = len(events)
                
                # 为每个事件添加偏移信息，用于绘制时避免重叠
                for i, event in enumerate(events):
                    event['overlap_index'] = i
                    event['overlap_count'] = len(events)
    
    def setup_ui(self):
        """设置对话框UI"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(12)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建标题
        title_label = QLabel("📊 事件可视化时间轴")
        StyleHelper.set_smiley_font(title_label, 16, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {StyleHelper.COLORS['primary']};")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建时间轴显示区域
        timeline_group = ModernGroupBox("时间轴视图")
        timeline_layout = QVBoxLayout(timeline_group)
        
        # 创建时间轴控件
        self.timeline_widget = TimelineWidget(self)
        self.timeline_widget.setMinimumHeight(400)
        # 设置更大的最小宽度，确保可以滚动查看所有事件
        self.timeline_widget.setMinimumWidth(2000)  # 增大最小宽度，确保可以显示更多事件
        self.timeline_widget.setStyleSheet("background-color: white; border: 1px solid #d0d0d0; border-radius: 6px;")
        
        # 使用水平和垂直滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(False)  # 关闭自动调整大小，允许水平滚动
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setWidget(self.timeline_widget)
        
        timeline_layout.addWidget(scroll_area)
        main_layout.addWidget(timeline_group)
        
        # 创建控制按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 缩放按钮
        zoom_in_btn = QPushButton("🔍 放大")
        zoom_in_btn.setFixedHeight(32)
        zoom_in_btn.setStyleSheet(StyleHelper.get_button_style())
        zoom_in_btn.clicked.connect(self.zoom_in)
        
        zoom_out_btn = QPushButton("🔍 缩小")
        zoom_out_btn.setFixedHeight(32)
        zoom_out_btn.setStyleSheet(StyleHelper.get_button_style())
        zoom_out_btn.clicked.connect(self.zoom_out)
        
        reset_btn = QPushButton("🔄 重置视图")
        reset_btn.setFixedHeight(32)
        reset_btn.setStyleSheet(StyleHelper.get_button_style())
        reset_btn.clicked.connect(self.reset_view)
        
        # 导出按钮
        export_btn = QPushButton("📸 导出图片")
        export_btn.setFixedHeight(32)
        export_btn.setStyleSheet(StyleHelper.get_button_style(accent=True))
        export_btn.clicked.connect(self.export_as_image)
        
        # 添加按钮到布局
        button_layout.addWidget(zoom_in_btn)
        button_layout.addWidget(zoom_out_btn)
        button_layout.addWidget(reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(export_btn)
        
        main_layout.addLayout(button_layout)
    
    def zoom_in(self):
        """放大时间轴"""
        self.zoom_level *= 1.2
        self.timeline_widget.update()
    
    def zoom_out(self):
        """缩小时间轴"""
        self.zoom_level /= 1.2
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
        self.timeline_widget.update()
    
    def reset_view(self):
        """重置时间轴视图"""
        self.zoom_level = 1.0
        self.offset = 0
        self.selected_event = None
        self.timeline_widget.update()
    
    def export_as_image(self):
        """导出时间轴为图片"""
        # 创建保存文件对话框
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出时间轴图片",
            "event_timeline.png",
            "PNG图片 (*.png);;JPEG图片 (*.jpg);;BMP图片 (*.bmp)"
        )
        
        if not file_path:
            return
        
        try:
            # 创建QPixmap并绘制时间轴
            pixmap = QPixmap(self.timeline_widget.size())
            pixmap.fill(Qt.GlobalColor.white)
            painter = QPainter(pixmap)
            self.timeline_widget.paintEvent(None, painter)
            painter.end()
            
            # 保存图片
            if pixmap.save(file_path):
                from styles import ChineseMessageBox
                ChineseMessageBox.show_info(self, "成功", f"时间轴已成功导出到: {file_path}")
            else:
                from styles import ChineseMessageBox
                ChineseMessageBox.show_error(self, "错误", "导出图片失败")
        except Exception as e:
            from styles import ChineseMessageBox
            ChineseMessageBox.show_error(self, "错误", f"导出图片时发生错误: {str(e)}")

class TimelineWidget(QWidget):
    """时间轴绘制控件"""
    
    def __init__(self, dialog):
        super().__init__()
        self.dialog = dialog
        self.setMinimumSize(800, 400)
        self.setMouseTracking(True)
        
        # 配置参数
        self.margin_left = 80
        self.margin_right = 20
        self.margin_top = 60
        self.margin_bottom = 80
        self.event_height = 60
        self.event_spacing = 30
        
        # 鼠标状态
        self.is_dragging = False
        self.last_mouse_pos = QPoint()
    
    def paintEvent(self, event, painter=None):
        """绘制时间轴"""
        custom_painter = painter is None
        if custom_painter:
            painter = QPainter(self)
        
        # 设置抗锯齿
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 获取绘制区域
        rect = self.rect()
        
        # 绘制背景
        painter.fillRect(rect, QColor(self.dialog.colors['background']))
        
        # 绘制时间轴区域
        timeline_rect = QRect(
            self.margin_left,
            self.margin_top,
            rect.width() - self.margin_left - self.margin_right,
            rect.height() - self.margin_top - self.margin_bottom
        )
        
        # 绘制网格线
        self.draw_grid(painter, timeline_rect)
        
        # 绘制时间刻度
        self.draw_time_ticks(painter, timeline_rect)
        
        # 绘制事件
        self.draw_events(painter, timeline_rect)
        
        # 绘制选中事件信息
        if self.dialog.selected_event:
            self.draw_selected_event_info(painter, timeline_rect)
        
        if custom_painter:
            painter.end()
    
    def draw_grid(self, painter, rect):
        """绘制网格线（优化密度，避免重叠）"""
        pen = QPen(QColor(self.dialog.colors['grid']), 0.5)
        painter.setPen(pen)
        
        # 绘制垂直线
        time_range = self.dialog.max_time - self.dialog.min_time
        if time_range <= 0:
            return
        
        # 根据时间范围动态调整网格线数量，避免重叠
        # 计算合适的网格线数量（每50ms一个网格）
        grid_interval_ms = 50
        grid_count = max(2, int(time_range / grid_interval_ms))
        # 限制最大网格线数量，避免过多导致重叠
        grid_count = min(grid_count, 20)
        
        for i in range(grid_count + 1):
            time = self.dialog.min_time + (time_range * i / grid_count)
            x = self.time_to_x(time, rect)
            painter.drawLine(x, rect.top(), x, rect.bottom())
        
        # 绘制水平线（减少数量，避免重叠）
        line_count = max(2, (self.height() - self.margin_top - self.margin_bottom) // 80)
        line_count = min(line_count, 5)
        for i in range(line_count + 1):
            y = self.margin_top + i * (rect.height() // line_count)
            painter.drawLine(self.margin_left, y, rect.right(), y)
    
    def draw_time_ticks(self, painter, rect):
        """绘制时间刻度（根据实际时间范围绘制，而不是固定的0-1000ms）"""
        pen = QPen(QColor(self.dialog.colors['text_secondary']), 0.5)
        painter.setPen(pen)
        
        font = QFont()
        font.setPointSize(8)
        painter.setFont(font)
        
        # 使用直接设置的min_time和max_time
        min_time = self.dialog.min_time
        max_time = self.dialog.max_time
        time_range = max_time - min_time
        if time_range <= 0:
            return
        
        # 计算刻度数量
        min_tick_spacing = 50  # 最小刻度间距（像素）
        tick_count = max(2, int(rect.width() / min_tick_spacing))
        tick_count = min(tick_count, 20)  # 限制最大刻度数量
        
        # 打印调试信息，查看时间范围
        print(f"[DEBUG] 绘制时间刻度，范围: {min_time}ms - {max_time}ms, 刻度数量: {tick_count}")
        
        # 根据时间范围和宽度动态调整刻度数量，避免重叠
        min_tick_spacing = 50  # 最小刻度间距（像素）
        tick_count = max(2, int(rect.width() / min_tick_spacing))
        tick_count = min(tick_count, 20)  # 限制最大刻度数量
        
        # 绘制主要刻度
        for i in range(tick_count + 1):
            # 计算当前刻度的时间值
            time = min_time + (time_range * i / tick_count)
            x = self.time_to_x(time, rect)
            
            # 绘制刻度线
            painter.drawLine(x, rect.bottom(), x, rect.bottom() + 5)
            
            # 绘制时间文本，避免与事件文本重叠
            time_text = f"{int(time)}ms"
            text_rect = painter.boundingRect(0, 0, 100, 20, Qt.AlignmentFlag.AlignCenter, time_text)
            
            # 确保文本不会超出窗口边界
            text_x = x - text_rect.width() // 2
            if text_x < self.margin_left:
                text_x = self.margin_left
            elif text_x + text_rect.width() > rect.right():
                text_x = rect.right() - text_rect.width()
            
            painter.drawText(
                text_x,
                rect.bottom() + 15,
                time_text
            )
    

    
    def draw_events(self, painter, rect):
        """绘制事件（处理同一时间点的多个事件）"""
        if not self.dialog.events:
            # 绘制提示信息
            font = QFont()
            font.setPointSize(12)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(QColor(self.dialog.colors['text_secondary'])))
            
            hint_text = "未加载到事件数据"
            text_rect = painter.boundingRect(rect, Qt.AlignmentFlag.AlignCenter, hint_text)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, hint_text)
            return
        
        # 计算事件垂直位置
        base_y = rect.top() + rect.height() // 2
        
        # 绘制时间轴线
        pen = QPen(QColor(self.dialog.colors['line']), 2)
        painter.setPen(pen)
        painter.drawLine(rect.left(), base_y, rect.right(), base_y)
        
        # 先收集所有事件点的位置信息
        event_positions = []
        for event in self.dialog.events:
            x = self.time_to_x(event['absolute_time'], rect)
            
            # 计算垂直偏移，处理同一时间点的多个事件
            overlap_index = event.get('overlap_index', 0)
            overlap_count = event.get('overlap_count', 1)
            
            overlap_offset = 0
            if overlap_count > 1:
                # 计算垂直偏移，将同一时间点的事件上下排列
                spacing = 120  # 增大垂直间距到120px，确保文本不会重叠
                total_height = (overlap_count - 1) * spacing
                # 居中排列同一时间点的事件
                overlap_offset = -total_height / 2 + overlap_index * spacing
                
                # 确保事件不会超出窗口边界
                max_offset = rect.height() / 3  # 限制最大偏移量为窗口高度的1/3
                if overlap_offset < -max_offset:
                    overlap_offset = -max_offset
                elif overlap_offset > max_offset:
                    overlap_offset = max_offset
            
            # 计算y坐标并转换为整数
            y = int(base_y + overlap_offset)
            event_positions.append((x, y))
        
        # 绘制事件连接线（虚线）
        pen = QPen(QColor(self.dialog.colors['event_line']), 1, Qt.PenStyle.DashLine)
        painter.setPen(pen)
        
        # 只连接相邻但不同时间点的事件
        prev_time = None
        for i, event in enumerate(self.dialog.events):
            curr_time = event['absolute_time']
            if i > 0 and curr_time != prev_time:
                # 只连接不同时间点的事件
                x1, y1 = event_positions[i-1]
                x2, y2 = event_positions[i]
                # 绘制水平线连接两个相邻时间点的基础位置
                painter.drawLine(x1, base_y, x2, base_y)
            prev_time = curr_time
        
        # 绘制事件点、垂直线和详细信息
        for i, (event, (x, y)) in enumerate(zip(self.dialog.events, event_positions)):
            # 选择颜色
            if event == self.dialog.selected_event:
                point_color = QColor(self.dialog.colors['selected'])
                line_color = QColor(self.dialog.colors['selected'])
                text_color = QColor(self.dialog.colors['selected'])
                point_size = 14
            else:
                point_color = QColor(self.dialog.colors['event_point'])
                line_color = QColor(self.dialog.colors['event_line'])
                text_color = QColor(self.dialog.colors['text'])
                point_size = 10
            
            # 绘制垂直线连接事件点和基础时间轴
            pen = QPen(line_color, 1)
            painter.setPen(pen)
            painter.drawLine(x, base_y, x, y)
            
            # 绘制事件点
            painter.setBrush(QBrush(point_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawEllipse(x - point_size // 2, y - point_size // 2, point_size, point_size)
            
            # 绘制事件索引
            font = QFont()
            font.setPointSize(7)
            font.setBold(True)
            painter.setFont(font)
            painter.setPen(QPen(Qt.GlobalColor.white))
            index_text = str(event['row'] + 1)
            text_rect = painter.boundingRect(0, 0, 20, 20, Qt.AlignmentFlag.AlignCenter, index_text)
            painter.drawText(
                x - text_rect.width() // 2,
                y - text_rect.height() // 2,
                text_rect.width(),
                text_rect.height(),
                Qt.AlignmentFlag.AlignCenter,
                index_text
            )
            
            # 绘制事件详细信息（调整垂直位置以避免重叠）
            self.draw_event_details(painter, event, x, y, text_color, rect)
    
    def draw_event_details(self, painter, event, x, y, text_color, rect):
        """绘制事件详细信息（移除相对时间显示）"""
        from utils import VK_MAPPING, KEY_NAME_MAPPING
        
        # 转换按键键码为按键名称
        def get_key_name(key_code_str):
            """将键码字符串转换为按键名称"""
            try:
                key_code = int(key_code_str)
                # 使用虚拟键码映射获取按键名称
                key_name = VK_MAPPING.get(key_code, f"键码:{key_code_str}")
                # 转换为中文名称
                key_name_cn = KEY_NAME_MAPPING.get(key_name, key_name)
                return key_name_cn
            except (ValueError, TypeError):
                return key_code_str
        
        # 根据事件类型准备显示文本
        if '鼠标' in event['type']:
            # 鼠标事件：显示类型、坐标
            event_text = f"{event['type']}\n({event['x']}, {event['y']})"
        elif '按键' in event['type']:
            # 按键事件：直接显示事件列表中的事件名称
            event_text = event['name']
        else:
            # 其他事件：显示类型
            event_text = event['type']
        
        # 设置字体
        # 事件文本
        event_font = QFont()
        event_font.setPointSize(9)
        event_font.setBold(True)
        
        # 绘制事件文本（根据事件点位置决定文本在上方或下方，避免被水平线穿过）
        painter.setFont(event_font)
        painter.setPen(QPen(text_color))
        
        # 分行绘制事件文本
        event_lines = event_text.split('\n')
        line_height = 18
        total_text_height = len(event_lines) * line_height
        
        # 计算文本起始位置，确保不被水平线穿过
        # 计算基础时间轴位置
        base_y = rect.top() + rect.height() // 2
        
        # 计算文本与水平线的最小距离
        min_distance = 10
        
        # 根据事件点相对于水平线的位置，决定文本在上方还是下方
        if y < base_y - min_distance:
            # 事件点在水平线上方，文本绘制在事件点下方
            start_y = y + 15
        elif y > base_y + min_distance:
            # 事件点在水平线下方，文本绘制在事件点上方
            start_y = y - total_text_height - 15
        else:
            # 事件点接近水平线，文本绘制在事件点上方
            start_y = y - total_text_height - 15
        
        for i, line in enumerate(event_lines):
            line_rect = painter.boundingRect(0, 0, 200, line_height, Qt.AlignmentFlag.AlignCenter, line)
            # 计算文本位置，确保不会超出左边界
            text_x = x - line_rect.width() // 2
            if text_x < self.margin_left:
                text_x = self.margin_left
            elif text_x + line_rect.width() > rect.right():
                text_x = rect.right() - line_rect.width()
            
            # 确保文本不会超出窗口边界
            current_y = start_y + i * line_height
            if current_y < 0:
                current_y = 0
            elif current_y > rect.bottom():
                current_y = rect.bottom()
            
            painter.drawText(
                text_x,
                current_y,
                line
            )
    
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        # 确保时间轴覆盖整个事件列表，根据事件数量调整控件宽度
        if self.dialog.events:
            # 计算需要的最小宽度，确保覆盖所有事件
            min_width = 1200  # 基础最小宽度
            self.setMinimumWidth(min_width)
            # 确保时间轴控件宽度足够
            self.timeline_widget.setMinimumWidth(min_width)
        self.update()
    
    def draw_selected_event_info(self, painter, rect):
        """绘制选中事件的详细信息"""
        event = self.dialog.selected_event
        if not event:
            return
        
        # 计算信息框位置（使用绝对时间）
        x = self.time_to_x(event['absolute_time'], rect)
        
        # 计算垂直位置，考虑同一时间点的多个事件
        base_y = rect.top() - 100
        y = base_y
        
        # 如果是同一时间点的多个事件之一，调整信息框位置
        if hasattr(event, 'overlap_index') and hasattr(event, 'overlap_count'):
            # 根据事件在同一时间点的索引调整信息框位置
            spacing = 30
            y += -spacing + event['overlap_index'] * spacing
        
        # 创建信息文本
        info_text = [
            f"事件: {event['name']}",
            f"类型: {event['type']}",
            f"键码: {event['key_code']}",
            f"坐标: ({event['x']}, {event['y']})",
            f"相对时间: {event['relative_time']}ms",
            f"绝对时间: {event['absolute_time']}ms"
        ]
        
        # 绘制信息框
        font = QFont()
        font.setPointSize(9)
        painter.setFont(font)
        
        # 计算文本区域大小
        max_width = 0
        total_height = 0
        for line in info_text:
            text_rect = painter.boundingRect(0, 0, 250, 20, Qt.AlignmentFlag.AlignLeft, line)
            max_width = max(max_width, text_rect.width())
            total_height += text_rect.height()
        
        # 添加内边距
        padding = 12
        box_width = max_width + 2 * padding
        box_height = total_height + 2 * padding
        
        # 调整位置，避免超出窗口
        box_x = x - box_width // 2
        if box_x < 0:
            box_x = 0
        elif box_x + box_width > self.width():
            box_x = self.width() - box_width
        
        # 调整垂直位置，避免超出窗口顶部
        if y < 0:
            y = 10
        
        # 绘制背景
        painter.setBrush(QBrush(QColor(255, 255, 255)))
        painter.setPen(QPen(QColor(self.dialog.colors['border']), 1))
        painter.drawRoundedRect(box_x, y, box_width, box_height, 6, 6)
        
        # 绘制文本
        painter.setPen(QPen(QColor(self.dialog.colors['text'])))
        text_y = y + padding + 10
        for line in info_text:
            painter.drawText(box_x + padding, text_y, line)
            text_rect = painter.boundingRect(0, 0, 250, 20, Qt.AlignmentFlag.AlignLeft, line)
            text_y += text_rect.height() + 2
    
    def time_to_x(self, time, rect):
        """将时间值转换为x坐标（应用缩放，禁用鼠标滚轮缩放）"""
        min_time = self.dialog.min_time
        max_time = self.dialog.max_time
        time_range = max_time - min_time
        if time_range <= 0:
            return rect.left()
        
        # 应用缩放和偏移（修正放大缩小逻辑）
        relative_pos = (time - min_time) / time_range
        scaled_pos = (relative_pos - self.dialog.offset) * self.dialog.zoom_level
        x = rect.left() + scaled_pos * rect.width()
        
        # 返回整数坐标
        return int(x)
    
    def x_to_time(self, x, rect):
        """将x坐标转换为时间值（应用缩放，禁用鼠标滚轮缩放）"""
        min_time = self.dialog.min_time
        max_time = self.dialog.max_time
        time_range = max_time - min_time
        if time_range <= 0:
            return min_time
        
        # 应用缩放和偏移（与time_to_x保持一致）
        relative_pos = (x - rect.left()) / rect.width()
        scaled_pos = relative_pos / self.dialog.zoom_level + self.dialog.offset
        time = min_time + scaled_pos * time_range
        
        return time
    
    def mousePressEvent(self, event):
        """处理鼠标按下事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击了事件点
            rect = QRect(
                self.margin_left,
                self.margin_top,
                self.width() - self.margin_left - self.margin_right,
                self.height() - self.margin_top - self.margin_bottom
            )
            
            event_y = rect.top() + rect.height() // 2
            clicked_event = None
            
            for event_item in self.dialog.events:
                x = self.time_to_x(event_item['absolute_time'], rect)
                # 考虑垂直偏移，计算实际事件点位置
                overlap_index = event_item.get('overlap_index', 0)
                overlap_count = event_item.get('overlap_count', 1)
                spacing = 70
                total_height = (overlap_count - 1) * spacing
                overlap_offset = -total_height / 2 + overlap_index * spacing
                actual_y = event_y + overlap_offset
                distance = ((x - event.position().x()) ** 2 + (actual_y - event.position().y()) ** 2) ** 0.5
                if distance <= 15:  # 点击半径
                    clicked_event = event_item
                    break
            
            if clicked_event:
                self.dialog.selected_event = clicked_event
                self.update()
            else:
                # 开始拖拽
                self.is_dragging = True
                self.last_mouse_pos = event.position().toPoint()
    
    def mouseMoveEvent(self, event):
        """处理鼠标移动事件"""
        if self.is_dragging:
            # 计算拖拽距离
            delta = event.position().toPoint() - self.last_mouse_pos
            self.last_mouse_pos = event.position().toPoint()
            
            # 更新偏移量
            rect = QRect(
                self.margin_left,
                self.margin_top,
                self.width() - self.margin_left - self.margin_right,
                self.height() - self.margin_top - self.margin_bottom
            )
            
            # 将像素偏移转换为时间偏移比例
            time_range = self.dialog.max_time - self.dialog.min_time
            if time_range > 0:
                self.dialog.offset -= delta.x() / rect.width() / self.dialog.zoom_level
            
            self.update()
    
    def mouseReleaseEvent(self, event):
        """处理鼠标释放事件"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
    
    def wheelEvent(self, event):
        """处理鼠标滚轮事件（禁用缩放）"""
        # 禁用鼠标滚轮缩放，不做任何处理
        pass
    
    def resizeEvent(self, event):
        """处理窗口大小变化事件"""
        super().resizeEvent(event)
        self.update()
