# panels.py
import os
import ctypes
import json
from datetime import datetime
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                            QLineEdit, QComboBox, QPushButton, QGroupBox, 
                            QTextEdit, QGridLayout, QDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator

from styles import StyleHelper
from styles import ModernGroupBox, ModernLineEdit, ModernComboBox, ModernSpinBox, ModernDoubleSpinBox, ChineseMessageBox, DialogFactory
from debug_tools import get_global_debug_logger

# =============================================================================
# 设置面板 - 循环设置和窗口设置
# =============================================================================

class SettingsPanel(QWidget):
    """设置面板 - 包含循环设置和屏幕设置"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存主窗口引用
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 循环设置
        self.create_loop_settings(layout)
        
        # 窗口设置
        self.create_screen_settings(layout)
    
    def create_loop_settings(self, parent_layout):
        """创建循环设置组"""
        group = ModernGroupBox("🔄 循环设置")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setColumnMinimumWidth(0, 70)  # 设置第0列最小宽度
        layout.setColumnStretch(0, 0)  # 第0列不拉伸
        layout.setColumnStretch(1, 1)  # 第1列拉伸以填充剩余空间
        
        # 循环次数 - 使用SpinBox
        label1 = QLabel("循环次数")
        label1.setFixedWidth(70)
        layout.addWidget(label1, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.loop_count_input = ModernSpinBox()
        self.loop_count_input.setMinimum(1)  # 最小值为1
        self.loop_count_input.setMaximum(999999)  # 最大值
        self.loop_count_input.setValue(1)  # 默认值为1
        self.loop_count_input.setSingleStep(1)  # 步长为1
        
        layout.addWidget(self.loop_count_input, 0, 1)
        
        # 间隔时间 - 使用DoubleSpinBox
        label2 = QLabel("间隔时间")
        label2.setFixedWidth(70)
        layout.addWidget(label2, 1, 0, Qt.AlignmentFlag.AlignLeft)
        time_layout = QHBoxLayout()
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(8)
        self.interval_input = ModernDoubleSpinBox()
        self.interval_input.setMinimum(0)  # 最小值为0
        self.interval_input.setMaximum(999999)  # 最大值
        self.interval_input.setValue(3)  # 默认值为3
        self.interval_input.setDecimals(2)  # 支持2位小数
        self.interval_input.setSingleStep(1)  # 步长为1
        self.time_unit_combo = ModernComboBox()
        self.time_unit_combo.addItems(["ms", "s", "min"])
        self.time_unit_combo.setCurrentText("s")
        self.time_unit_combo.setFixedWidth(50)  # 设置固定宽度为50px
        # 使用统一的居中组合框样式
        self.time_unit_combo.setStyleSheet(StyleHelper.get_centered_combo_box_style())
        time_layout.addWidget(self.interval_input)
        time_layout.addWidget(self.time_unit_combo)
        layout.addLayout(time_layout, 1, 1)
        
        # 预计总时间
        label3 = QLabel("预计总时间")
        label3.setFixedWidth(70)
        layout.addWidget(label3, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.total_time_label = QLabel("0.0 s")
        self.total_time_label.setStyleSheet(StyleHelper.get_total_time_label_style())
        layout.addWidget(self.total_time_label, 2, 1, Qt.AlignmentFlag.AlignLeft)
        
        parent_layout.addWidget(group)
    
    def get_safe_loop_count(self):
        """安全获取循环次数，确保总是返回有效值"""
        # SpinBox已经自动限制了最小值为1，直接返回值即可
        return self.loop_count_input.value()
    
    def create_screen_settings(self, parent_layout):
        """创建窗口设置组"""
        group = ModernGroupBox("🖥️ 窗口设置")
        layout = QGridLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        layout.setColumnMinimumWidth(0, 70)  # 设置第0列最小宽度与循环设置一致
        layout.setColumnStretch(0, 0)  # 第0列不拉伸
        layout.setColumnStretch(1, 1)  # 第1列拉伸以填充剩余空间
        
        # 窗口宽度
        label1 = QLabel("窗口宽度")
        label1.setFixedWidth(70)
        layout.addWidget(label1, 0, 0, Qt.AlignmentFlag.AlignLeft)
        self.width_input = ModernLineEdit("1920")
        layout.addWidget(self.width_input, 0, 1)
        
        # 窗口高度
        label2 = QLabel("窗口高度")
        label2.setFixedWidth(70)
        layout.addWidget(label2, 1, 0, Qt.AlignmentFlag.AlignLeft)
        self.height_input = ModernLineEdit("1080")
        layout.addWidget(self.height_input, 1, 1)
        
        # 缩放比例
        label3 = QLabel("缩放比例")
        label3.setFixedWidth(70)
        layout.addWidget(label3, 2, 0, Qt.AlignmentFlag.AlignLeft)
        self.scale_combo = ModernComboBox()
        self.scale_combo.addItems(["100%", "125%", "150%", "175%", "200%", "225%", "250%"])
        self.scale_combo.setCurrentText("100%")
        # 使用统一的居中组合框样式
        self.scale_combo.setStyleSheet(StyleHelper.get_centered_combo_box_style())
        layout.addWidget(self.scale_combo, 2, 1)
        
        # 获取分辨率和缩放比例按钮
        self.detect_screen_btn = QPushButton("📏 获取屏幕分辨率和缩放")
        self.detect_screen_btn.setFixedHeight(32)
        self.detect_screen_btn.setStyleSheet(StyleHelper.get_button_style())
        layout.addWidget(self.detect_screen_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)
    
    def update_total_time_display(self, total_ms):
        """更新总时间显示"""
        # 修复：当值大于60s后就显示min值，小于60s就显示s值
        if total_ms < 1000:
            # 小于1秒，显示毫秒
            self.total_time_label.setText(f"{total_ms} ms")
        elif total_ms < 60000:
            # 小于60秒，显示秒
            seconds = total_ms / 1000
            self.total_time_label.setText(f"{seconds:.1f} s")
        else:
            # 大于60秒，显示分钟
            minutes = total_ms / 60000
            self.total_time_label.setText(f"{minutes:.1f} min")
    
    def update_screen_settings(self, width, height, scale):
        """更新屏幕设置"""
        self.width_input.setText(str(width))
        self.height_input.setText(str(height))
        self.scale_combo.setCurrentText(scale)
    
    def reset_settings(self):
        """重置设置"""
        self.loop_count_input.setValue(1)
        self.interval_input.setValue(3)
        self.time_unit_combo.setCurrentText("s")
        self.width_input.setText("1920")
        self.height_input.setText("1080")
        self.scale_combo.setCurrentText("100%")
        self.total_time_label.setText("0.0 s")
    
    def restore_settings(self, state):
        """从状态恢复设置"""
        try:
            loop_count = int(state.get('loop_count', '1'))
            self.loop_count_input.setValue(loop_count)
        except (ValueError, TypeError):
            self.loop_count_input.setValue(1)
        
        try:
            interval = float(state.get('interval', '3'))
            self.interval_input.setValue(interval)
        except (ValueError, TypeError):
            self.interval_input.setValue(3)
        
        self.time_unit_combo.setCurrentText(state.get('time_unit', 's'))
        self.width_input.setText(state.get('width', '1920'))
        self.height_input.setText(state.get('height', '1080'))
        self.scale_combo.setCurrentText(state.get('scale', '100%'))

# =============================================================================
# 操作面板 - 包含操作按钮和预览功能
# =============================================================================

class OperationsPanel(QWidget):
    """操作面板 - 包含操作按钮"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存主窗口引用
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = ModernGroupBox("⚡ 操作")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        # 按钮布局
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.generate_btn = QPushButton("🚀 生成脚本")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet(StyleHelper.get_button_style(accent=True))
        
        self.save_btn = QPushButton("💾 保存脚本")
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet(StyleHelper.get_button_style())
        
        self.preview_btn = QPushButton("👁️ 预览脚本")
        self.preview_btn.setFixedHeight(35)
        self.preview_btn.setStyleSheet(StyleHelper.get_button_style())
        
        # 导入脚本按钮 - 移动到操作模块
        self.import_script_btn = QPushButton("📥 导入脚本")
        self.import_script_btn.setFixedHeight(35)
        self.import_script_btn.setStyleSheet(StyleHelper.get_button_style())
        
        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addWidget(self.import_script_btn)
        
        group_layout.addLayout(buttons_layout)
        layout.addWidget(group)
    
    def on_preview_script(self):
        """预览脚本 - 从主窗口转移过来的功能"""
        try:
            if not self.main_window or not self.main_window.script:
                self.debug_logger.log_warning("尝试预览但未生成脚本")
                ChineseMessageBox.show_warning(self, "警告", "请先生成脚本")
                return
            
            # 创建预览对话框
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("脚本预览")
            preview_dialog.resize(500, 700)  # 修改宽度为500px
            
            layout = QVBoxLayout(preview_dialog)
            
            # 脚本内容显示
            script_text = QTextEdit()
            script_text.setReadOnly(True)
            script_text.setStyleSheet(StyleHelper.get_script_text_style())
            script_text.setPlainText(json.dumps(self.main_window.script, ensure_ascii=False, indent=2))
            layout.addWidget(script_text)
            
            # 使用DialogFactory创建关闭按钮布局
            button_layout = DialogFactory.create_close_button(
                parent=preview_dialog,
                on_close=preview_dialog.close,
                text="关闭"
            )
            layout.addLayout(button_layout)
            
            self.debug_logger.log_info("打开脚本预览对话框")
            preview_dialog.exec()
            
        except Exception as e:
            error_msg = f"预览脚本失败: {str(e)}"
            self.debug_logger.log_error(error_msg)
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def on_generate_script(self):
        """生成脚本 - 调用主窗口的方法"""
        if self.main_window:
            self.main_window.on_generate_script()
    
    def on_save_script(self):
        """保存脚本 - 调用主窗口的方法"""
        if self.main_window:
            self.main_window.on_save_script()
    
    def on_import_script(self):
        """导入脚本 - 调用主窗口的方法"""
        if self.main_window:
            self.main_window.on_import_script()

# =============================================================================
# 统计信息面板 - 集成计算逻辑
# =============================================================================

class StatsPanel(QWidget):
    """统计信息面板"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent  # 保存主窗口引用
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = ModernGroupBox("📊 统计信息")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(15, 20, 15, 15)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet(StyleHelper.get_explanation_text_edit_style())
        self.stats_text.setPlainText(f"""脚本信息将在此显示...

• 总事件数: 0
• 按键事件: 0
• 鼠标事件: 0  
• 总执行时间: 0ms
• 循环次数: 1
• 循环间隔: 0ms

窗口设置:
• 分辨率: 1920x1080
• 缩放比例: 100%""")
        
        group_layout.addWidget(self.stats_text)
        layout.addWidget(group)
    
    def update_stats(self):
        """更新统计信息 - 从主窗口转移过来的计算逻辑"""
        try:
            if not self.main_window:
                return
                
            row_count = self.main_window.events_table.rowCount()
            
            # 计算单次循环总时间
            single_loop_time_ms = self.calculate_single_loop_time_ms()
            
            # 获取循环次数 - 使用安全获取方法
            loop_count = self.main_window.settings_panel.get_safe_loop_count()
            
            # 获取间隔时间
            interval = self.main_window.settings_panel.interval_input.value()
            
            time_unit = self.main_window.settings_panel.time_unit_combo.currentText()
            if time_unit == "s":
                interval_ms = interval * 1000
            elif time_unit == "min":
                interval_ms = interval * 60000
            else:  # ms
                interval_ms = interval
            
            # 计算总执行时间
            total_time_ms = self.calculate_total_time_ms()
            
            # 统计各类事件数量
            key_press_count = 0
            key_release_count = 0
            mouse_move_count = 0
            mouse_click_count = 0
            
            for row in range(self.main_window.events_table.rowCount()):
                type_item = self.main_window.events_table.item(row, 2)  # 事件类型列
                if type_item:
                    event_type = type_item.text()
                    if event_type == "按键按下":
                        key_press_count += 1
                    elif event_type == "按键释放":
                        key_release_count += 1
                    elif event_type == "鼠标移动":
                        mouse_move_count += 1
                    elif event_type in ["左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放"]:
                        mouse_click_count += 1
                    elif event_type == "鼠标滚轮":
                        mouse_move_count += 1
            
            # 获取窗口设置
            width = self.main_window.settings_panel.width_input.text() or "1920"
            height = self.main_window.settings_panel.height_input.text() or "1080"
            scale = self.main_window.settings_panel.scale_combo.currentText()
            
            # 计算时间分布
            avg_interval = 0
            if row_count > 1:
                avg_interval = single_loop_time_ms / (row_count - 1)
            
            # 生成统计信息文本
            stats_text = f"""═══════════════════════════════════════
📊 脚本统计信息
═══════════════════════════════════════

🔢 事件统计:
• 总事件数: {row_count}
  ├─ 按键按下: {key_press_count}
  ├─ 按键释放: {key_release_count}
  ├─ 鼠标移动: {mouse_move_count}
  └─ 鼠标点击: {mouse_click_count}

⏱️ 时间统计:
• 单次循环时间: {self.format_time_display(single_loop_time_ms)}
• 总执行时间: {self.format_time_display(total_time_ms)}
• 平均事件间隔: {self.format_time_display(avg_interval)}
• 循环次数: {loop_count}
• 循环间隔: {interval} {time_unit}

🖥️ 窗口设置:
• 分辨率: {width}×{height}
• 缩放比例: {scale}
• 像素总数: {int(width) * int(height):,}

💾 脚本信息:
• 预计文件大小: ~{row_count * 50} bytes
• 事件密度: {row_count / (single_loop_time_ms / 1000) if single_loop_time_ms > 0 else 0:.1f} 事件/秒
• 脚本复杂度: {'简单' if row_count < 10 else '中等' if row_count < 50 else '复杂'}

📝 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""  # 移除了版本信息
            
            self.stats_text.setPlainText(stats_text)
            
            # 同时更新预计总时间标签
            if self.main_window:
                self.main_window.on_calculate_total_time()
            
        except Exception as e:
            error_msg = f"更新统计信息时出错: {e}"
            self.debug_logger.log_error(error_msg)
            self.stats_text.setPlainText(f"统计信息更新失败: {error_msg}")
    
    def format_time_display(self, time_ms):
        """格式化时间显示"""
        if time_ms < 1000:
            return f"{time_ms:.0f} ms"
        elif time_ms < 60000:
            seconds = time_ms / 1000
            return f"{time_ms:.0f} ms ({seconds:.1f} s)"
        else:
            minutes = time_ms / 60000
            return f"{time_ms:.0f} ms ({minutes:.1f} min)"
    
    def calculate_single_loop_time_ms(self):
        """计算单次循环的总时间（毫秒）"""
        try:
            # 获取单次循环时间（最后一个事件的绝对时间）
            if not self.main_window or self.main_window.events_table.rowCount() == 0:
                return 0
            last_row = self.main_window.events_table.rowCount() - 1
            time_item = self.main_window.events_table.item(last_row, 7)  # 绝对偏移列
            if time_item and time_item.text().isdigit():
                return int(time_item.text())
            else:
                return 0
        except Exception as e:
            self.debug_logger.log_error(f"计算单次循环时间失败: {e}")
            return 0
    
    def calculate_total_time_ms(self):
        """计算整个脚本的总时间（毫秒）"""
        try:
            if not self.main_window:
                return 0
                
            # 获取单次循环时间
            single_loop_time = self.calculate_single_loop_time_ms()
            
            # 获取循环次数 - 使用安全获取方法
            loop_count = self.main_window.settings_panel.get_safe_loop_count()
            
            # 获取间隔时间（毫秒）
            interval = self.main_window.settings_panel.interval_input.value()
            
            # 转换时间单位为毫秒
            time_unit = self.main_window.settings_panel.time_unit_combo.currentText()
            if time_unit == "s":
                interval_ms = interval * 1000
            elif time_unit == "min":
                interval_ms = interval * 60000
            else:  # ms
                interval_ms = interval
            
            # 总时间 = 单次循环时间 * 循环次数 + 间隔时间 * (循环次数 - 1)
            total_time = single_loop_time * loop_count + interval_ms * (loop_count - 1)
            return total_time
        except Exception as e:
            self.debug_logger.log_error(f"计算总时间失败: {e}")
            return 0
    
    def update_stats_display(self, stats_text):
        """更新统计信息显示 - 保持向后兼容"""
        self.stats_text.setPlainText(stats_text)
