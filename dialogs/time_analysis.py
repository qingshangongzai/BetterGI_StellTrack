# time_analysis.py - 事件时间分析插件
import sys
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                            QGroupBox, QGridLayout, QComboBox, QFrame, QMessageBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

# 导入共享模块
from styles import UnifiedStyleHelper, ChineseMessageBox, ModernGroupBox, CenteredComboBox, StyledDialog, get_global_font_manager, FadeInWindowMixin


class EventTimeAnalyzerDialog(FadeInWindowMixin, StyledDialog):
    """事件时间分析对话框"""
    
    def __init__(self, parent=None, events_table=None):
        super().__init__(parent)
        self.events_table = events_table
        self.setWindowTitle("事件时间分析")
        self.setFixedSize(500, 480)  # 大幅增加窗口大小以确保内容完全显示
        
        # 设置窗口标志，删除最小化和最大化按钮
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(25, 20, 25, 20)
        
        # 标题区域
        title_label = QLabel("事件时间分析")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 16, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 8px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 事件选择区域
        event_selection_group = ModernGroupBox("📋 事件选择")
        event_selection_layout = QVBoxLayout(event_selection_group)
        event_selection_layout.setSpacing(10)
        event_selection_layout.setContentsMargins(15, 20, 15, 15)
        event_selection_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 起始事件行布局
        start_event_layout = QHBoxLayout()
        start_event_layout.setSpacing(2)  # 极小的间距
        start_event_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 起始事件标签
        start_event_label = QLabel("起始事件：")
        UnifiedStyleHelper.get_instance().set_source_han_font(start_event_label, 10)
        start_event_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        start_event_layout.addWidget(start_event_label)
        
        # 起始事件下拉框
        self.start_event_combo = CenteredComboBox()
        self.start_event_combo.setMinimumWidth(150)
        self.start_event_combo.setMinimumHeight(30)
        start_event_layout.addWidget(self.start_event_combo)
        
        # 结束事件行布局
        end_event_layout = QHBoxLayout()
        end_event_layout.setSpacing(2)  # 极小的间距
        end_event_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 结束事件标签
        end_event_label = QLabel("结束事件：")
        UnifiedStyleHelper.get_instance().set_source_han_font(end_event_label, 10)
        end_event_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        end_event_layout.addWidget(end_event_label)
        
        # 结束事件下拉框
        self.end_event_combo = CenteredComboBox()
        self.end_event_combo.setMinimumWidth(150)
        self.end_event_combo.setMinimumHeight(30)
        end_event_layout.addWidget(self.end_event_combo)
        
        # 将行布局添加到主布局
        event_selection_layout.addLayout(start_event_layout)
        event_selection_layout.addLayout(end_event_layout)
        
        # 填充事件列表
        self.populate_event_combos()
        
        main_layout.addWidget(event_selection_group)
        
        # 分析按钮
        analyze_btn = QPushButton("🔍 开始分析")
        analyze_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        analyze_btn.setMinimumHeight(32)
        analyze_btn.clicked.connect(self.on_analyze)
        # 创建按钮容器并设置居中布局
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        btn_layout.addWidget(analyze_btn)
        main_layout.addLayout(btn_layout)
        
        # 结果显示区域
        self.result_group = ModernGroupBox("📊 分析结果")
        result_layout = QVBoxLayout(self.result_group)
        result_layout.setSpacing(5)  # 减小布局间距
        result_layout.setContentsMargins(15, 15, 15, 10)  # 减小边距
        
        # 结果网格布局
        result_grid = QGridLayout()
        result_grid.setSpacing(3)  # 大幅减小间距
        
        # 总时间
        self.total_time_label = QLabel("0 ms")
        self.total_time_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-weight: bold; font-size: 12px;")
        self.total_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 左对齐以更靠近标签
        result_grid.addWidget(QLabel("总时间："), 0, 0, Qt.AlignmentFlag.AlignRight)
        result_grid.addWidget(self.total_time_label, 0, 1)
        
        # 平均时间
        self.avg_time_label = QLabel("0 ms")
        self.avg_time_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-weight: bold; font-size: 12px;")
        self.avg_time_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 左对齐以更靠近标签
        result_grid.addWidget(QLabel("平均时间："), 1, 0, Qt.AlignmentFlag.AlignRight)
        result_grid.addWidget(self.avg_time_label, 1, 1)
        
        # 重复次数
        self.repeat_count_label = QLabel("0")
        self.repeat_count_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; font-weight: bold; font-size: 12px;")
        self.repeat_count_label.setAlignment(Qt.AlignmentFlag.AlignLeft)  # 左对齐以更靠近标签
        result_grid.addWidget(QLabel("重复次数："), 2, 0, Qt.AlignmentFlag.AlignRight)
        result_grid.addWidget(self.repeat_count_label, 2, 1)
        
        result_layout.addLayout(result_grid)
        main_layout.addWidget(self.result_group)
        
        # 重置按钮
        reset_btn = QPushButton("🔄 重置")
        reset_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        reset_btn.setMinimumHeight(30)
        reset_btn.clicked.connect(self.reset_results)
        # 创建按钮容器并设置居中布局
        reset_layout = QHBoxLayout()
        reset_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        reset_layout.addWidget(reset_btn)
        main_layout.addLayout(reset_layout)
    
    def populate_event_combos(self):
        """从事件表格中填充事件列表到下拉框，只严格排除指针移动和平行移动事件"""
        if not self.events_table:
            return
        
        # 获取所有唯一事件名称，只严格排除指针移动和平行移动事件
        event_names = set()
        for row in range(self.events_table.rowCount()):
            item = self.events_table.item(row, 1)  # 事件名称在第2列（索引1）
            event_type_item = self.events_table.item(row, 2)  # 事件类型在第3列（索引2）
            
            # 确保项目存在且有文本内容
            if item and item.text():
                # 只排除明确标识为指针移动或平行移动的事件
                skip_event = False
                
                # 通过事件类型判断是否为指针移动或平行移动事件
                if event_type_item and (event_type_item.text() == "指针移动" or event_type_item.text() == "平行移动"):
                    skip_event = True
                # 只在事件名称完全匹配"指针移动"或"平行移动"时才排除
                elif item.text().strip() == "指针移动" or item.text().strip() == "平行移动":
                    skip_event = True
                    
                # 添加非指针移动和平行移动事件
                if not skip_event:
                    event_names.add(item.text())
        
        # 转换为列表并排序
        sorted_event_names = sorted(event_names)
        
        # 填充下拉框
        self.start_event_combo.addItems(sorted_event_names)
        self.end_event_combo.addItems(sorted_event_names)
    
    def format_time_display(self, total_ms):
        """格式化时间显示，与循环设置的显示逻辑保持一致
        
        Args:
            total_ms: 总时间（毫秒）
            
        Returns:
            str: 格式化后的时间字符串
        """
        if total_ms < 1000:
            return f"{int(total_ms)} ms"
        elif total_ms < 60000:
            seconds = total_ms / 1000
            return f"{seconds:.1f} s"
        else:
            minutes = total_ms / 60000
            return f"{minutes:.1f} min"
    
    def on_analyze(self):
        """开始分析事件时间"""
        if not self.events_table:
            ChineseMessageBox.show_error(self, "错误", "未找到事件表格数据")
            return
        
        # 获取选中的事件
        start_event = self.start_event_combo.currentText()
        end_event = self.end_event_combo.currentText()
        
        if not start_event or not end_event:
            ChineseMessageBox.show_warning(self, "提示", "请选择起始事件和结束事件")
            return
        
        # 分析事件时间
        time_pairs = []
        start_events = []
        
        for row in range(self.events_table.rowCount()):
            event_name_item = self.events_table.item(row, 1)
            event_time_item = self.events_table.item(row, 7)  # 绝对偏移时间在第8列（索引7）
            
            if event_name_item and event_time_item:
                event_name = event_name_item.text()
                try:
                    event_time = int(event_time_item.text())
                    
                    if event_name == start_event:
                        # 记录起始事件
                        start_events.append(event_time)
                    elif event_name == end_event and start_events:
                        # 找到结束事件，匹配最后一个未匹配的起始事件
                        last_start_time = start_events[-1]
                        duration = event_time - last_start_time
                        if duration >= 0:  # 只记录正的时间差
                            time_pairs.append(duration)
                            start_events.pop()  # 移除已匹配的起始事件
                except ValueError:
                    continue
        
        # 计算结果
        if time_pairs:
            total_time = sum(time_pairs)
            avg_time = total_time / len(time_pairs)
            repeat_count = len(time_pairs)
            
            # 更新结果显示
            self.total_time_label.setText(self.format_time_display(total_time))
            self.avg_time_label.setText(f"{int(avg_time)} ms")
            self.repeat_count_label.setText(f"{repeat_count}")
            
            ChineseMessageBox.show_info(self, "分析完成", f"已找到 {repeat_count} 个时间对")
        else:
            # 重置结果
            self.reset_results()
            ChineseMessageBox.show_info(self, "分析结果", "未找到匹配的事件时间对")
    
    def reset_results(self):
        """重置分析结果"""
        self.total_time_label.setText("0 ms")
        self.avg_time_label.setText("0 ms")
        self.repeat_count_label.setText("0")
    
    def get_results(self):
        """获取分析结果"""
        return {
            "total_time": int(self.total_time_label.text().replace(" ms", "")),
            "avg_time": int(self.avg_time_label.text().replace(" ms", "")),
            "repeat_count": int(self.repeat_count_label.text())
        }