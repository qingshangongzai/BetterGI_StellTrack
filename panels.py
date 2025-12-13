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

from styles import UnifiedStyleHelper
from styles import ModernGroupBox, ModernLineEdit, ModernComboBox, ModernSpinBox, ModernDoubleSpinBox, ChineseMessageBox, DialogFactory
from debug_tools import get_global_debug_logger

# =============================================================================
# 设置面板 - 循环设置和窗口设置
# =============================================================================

class SettingsPanel(QWidget):
    """应用程序设置面板
    
    管理应用程序的核心设置，包括：
    - 循环设置：控制脚本执行的循环次数和间隔时间
    - 屏幕设置：管理目标屏幕分辨率和缩放比例
    
    提供UI界面用于设置调整和显示，以及相关的辅助方法。
    """
    
    def __init__(self, parent=None):
        """初始化设置面板
        
        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent  # 重命名为更通用的parent_window
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置面板的UI布局和组件
        
        创建并布局面板的主要组件，包括：
        - 循环设置区域
        - 屏幕设置区域
        
        使用垂直布局组织所有设置组。
        """
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
        loop_count_label = QLabel("循环次数")
        loop_count_label.setFixedWidth(70)
        layout.addWidget(loop_count_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.loop_count_input = ModernSpinBox()
        self.loop_count_input.setMinimum(1)  # 最小值为1
        self.loop_count_input.setMaximum(999999)  # 最大值
        self.loop_count_input.setValue(1)  # 默认值为1
        self.loop_count_input.setSingleStep(1)  # 步长为1
        
        layout.addWidget(self.loop_count_input, 0, 1)
        
        # 间隔时间 - 使用DoubleSpinBox
        interval_label = QLabel("间隔时间")
        interval_label.setFixedWidth(70)
        layout.addWidget(interval_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        
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
        self.time_unit_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        
        time_layout.addWidget(self.interval_input)
        time_layout.addWidget(self.time_unit_combo)
        layout.addLayout(time_layout, 1, 1)
        
        # 预计总时间
        total_time_label = QLabel("预计总时间")
        total_time_label.setFixedWidth(70)
        layout.addWidget(total_time_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.total_time_display = QLabel("0.0 s")
        self.total_time_display.setStyleSheet(UnifiedStyleHelper.get_instance().get_total_time_label_style())
        layout.addWidget(self.total_time_display, 2, 1, Qt.AlignmentFlag.AlignLeft)
        
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
        width_label = QLabel("窗口宽度")
        width_label.setFixedWidth(70)
        layout.addWidget(width_label, 0, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.width_input = ModernLineEdit("1920")
        layout.addWidget(self.width_input, 0, 1)
        
        # 窗口高度
        height_label = QLabel("窗口高度")
        height_label.setFixedWidth(70)
        layout.addWidget(height_label, 1, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.height_input = ModernLineEdit("1080")
        layout.addWidget(self.height_input, 1, 1)
        
        # 缩放比例
        scale_label = QLabel("缩放比例")
        scale_label.setFixedWidth(70)
        layout.addWidget(scale_label, 2, 0, Qt.AlignmentFlag.AlignLeft)
        
        self.scale_combo = ModernComboBox()
        self.scale_combo.addItems(["100%", "125%", "150%", "175%", "200%", "225%", "250%"])
        self.scale_combo.setCurrentText("100%")
        # 使用统一的居中组合框样式
        self.scale_combo.setStyleSheet(UnifiedStyleHelper.get_instance().get_centered_combo_box_style())
        layout.addWidget(self.scale_combo, 2, 1)
        
        # 获取分辨率和缩放比例按钮
        self.detect_screen_btn = QPushButton("📏 获取屏幕分辨率和缩放")
        self.detect_screen_btn.setFixedHeight(32)
        self.detect_screen_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        layout.addWidget(self.detect_screen_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)
    
    def update_total_time_display(self, total_ms):
        """更新总时间显示"""
        # 修复：当值大于60s后就显示min值，小于60s就显示s值
        if total_ms < 1000:
            # 小于1秒，显示毫秒
            self.total_time_display.setText(f"{int(total_ms)} ms")
        elif total_ms < 60000:
            # 小于60秒，显示秒
            seconds = total_ms / 1000
            self.total_time_display.setText(f"{seconds:.1f} s")
        else:
            # 大于60秒，显示分钟
            minutes = total_ms / 60000
            self.total_time_display.setText(f"{minutes:.1f} min")
    
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
        self.total_time_display.setText("0.0 s")
    
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
    """应用程序操作面板
    
    提供应用程序的核心操作按钮，包括：
    - 生成脚本：创建BetterGI可执行的脚本
    - 保存脚本：将生成的脚本保存到文件
    - 预览脚本：查看生成的脚本内容
    - 导入脚本：从文件导入现有脚本
    
    所有操作按钮都与父窗口的对应方法绑定。
    """
    
    def __init__(self, parent=None):
        """初始化操作面板
        
        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent  # 保存父窗口引用，避免使用main_window命名
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置操作面板的UI布局和组件
        
        创建并布局操作面板的主要组件，包括：
        - 生成脚本按钮
        - 保存脚本按钮
        - 预览脚本按钮
        - 导入脚本按钮
        
        使用垂直布局组织所有操作按钮，强调主要操作。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = ModernGroupBox("⚡ 操作")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(10)
        group_layout.setContentsMargins(10, 15, 10, 10)
        
        # 按钮布局
        buttons_layout = QVBoxLayout()
        buttons_layout.setSpacing(8)
        
        self.generate_btn = QPushButton("🚀 生成脚本")
        self.generate_btn.setFixedHeight(40)
        self.generate_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        self.save_btn = QPushButton("💾 保存脚本")
        self.save_btn.setFixedHeight(35)
        self.save_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        
        self.preview_btn = QPushButton("👁️ 预览脚本")
        self.preview_btn.setFixedHeight(35)
        self.preview_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        
        # 导入脚本按钮 - 移动到操作模块
        self.import_script_btn = QPushButton("📥 导入脚本")
        self.import_script_btn.setFixedHeight(35)
        self.import_script_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        
        buttons_layout.addWidget(self.generate_btn)
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.preview_btn)
        buttons_layout.addWidget(self.import_script_btn)
        
        group_layout.addLayout(buttons_layout)
        layout.addWidget(group)
    
    def on_preview_script(self):
        """预览脚本 - 从主窗口转移过来的功能"""
        try:
            if not self.parent_window or not self.parent_window.script:
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
            script_text.setStyleSheet(UnifiedStyleHelper.get_instance().get_script_text_style())
            script_text.setPlainText(json.dumps(self.parent_window.script, ensure_ascii=False, indent=2))
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
        """生成脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_generate_script()
    
    def on_save_script(self):
        """保存脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_save_script()
    
    def on_import_script(self):
        """导入脚本 - 调用父窗口的方法"""
        if self.parent_window:
            self.parent_window.on_import_script()

# =============================================================================
# 统计信息面板 - 集成计算逻辑
# =============================================================================

class StatsPanel(QWidget):
    """应用程序统计信息面板
    
    显示脚本和事件的统计信息，包括：
    - 事件数量统计
    - 执行时间计算
    - 循环设置信息
    - 屏幕设置信息
    
    实时更新以反映当前的脚本配置和事件数据。
    """
    
    def __init__(self, parent=None):
        """初始化统计信息面板
        
        Args:
            parent: 父窗口或部件实例
        """
        super().__init__(parent)
        self.parent_window = parent  # 保存父窗口引用，避免使用main_window命名
        self.debug_logger = get_global_debug_logger()
        self.setup_ui()
    
    def setup_ui(self):
        """设置统计信息面板的UI布局和组件
        
        创建并布局统计信息面板的主要组件，包括：
        - 统计信息显示区域
        - 预设的统计信息文本格式
        
        使用文本编辑控件展示格式化的统计数据。
        """
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(0, 0, 0, 0)
        
        group = ModernGroupBox("📊 统计信息")
        group_layout = QVBoxLayout(group)
        group_layout.setContentsMargins(10, 15, 10, 10)
        
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)
        self.stats_text.setStyleSheet(UnifiedStyleHelper.get_instance().get_explanation_text_edit_style())
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
        """更新统计信息"""
        try:
            if not self.parent_window:
                return
                
            # 获取事件管理器
            event_manager = getattr(self.parent_window, 'event_manager', None)
            settings_panel = getattr(self.parent_window, 'settings_panel', None)
            
            if not event_manager or not settings_panel:
                self.debug_logger.log_warning("无法获取事件管理器或设置面板")
                return
            
            row_count = event_manager.events_table.rowCount()
            
            # 计算单次循环总时间
            single_loop_time_ms = self.calculate_single_loop_time_ms(event_manager)
            
            # 获取循环次数 - 使用安全获取方法
            loop_count = settings_panel.get_safe_loop_count()
            
            # 获取间隔时间
            interval = settings_panel.interval_input.value()
            
            time_unit = settings_panel.time_unit_combo.currentText()
            if time_unit == "s":
                interval_ms = interval * 1000
            elif time_unit == "min":
                interval_ms = interval * 60000
            else:  # ms
                interval_ms = interval
            
            # 计算总执行时间
            total_time_ms = self.calculate_total_time_ms(single_loop_time_ms, loop_count, interval_ms)
            
            # 统计各类事件数量
            key_press_count, key_release_count, mouse_move_count, mouse_click_count = self.count_events(event_manager)
            
            # 获取窗口设置
            width = settings_panel.width_input.text() or "1920"
            height = settings_panel.height_input.text() or "1080"
            scale = settings_panel.scale_combo.currentText()
            
            # 计算时间分布
            avg_interval = 0
            if row_count > 1:
                avg_interval = single_loop_time_ms / (row_count - 1)
            
            # 生成统计信息文本
            stats_text = self.generate_stats_text(
                row_count,
                key_press_count,
                key_release_count,
                mouse_move_count,
                mouse_click_count,
                single_loop_time_ms,
                total_time_ms,
                avg_interval,
                loop_count,
                interval,
                time_unit,
                width,
                height,
                scale
            )
            
            self.stats_text.setPlainText(stats_text)
            
            # 同时更新预计总时间标签
            if hasattr(self.parent_window, 'on_calculate_total_time'):
                self.parent_window.on_calculate_total_time()
            
        except Exception as e:
            error_msg = f"更新统计信息时出错: {e}"
            self.debug_logger.log_error(error_msg)
            self.stats_text.setPlainText(f"统计信息更新失败: {error_msg}")
    
    def count_events(self, event_manager):
        """统计各类事件数量"""
        key_press_count = 0
        key_release_count = 0
        mouse_move_count = 0
        mouse_click_count = 0
        
        for row in range(event_manager.events_table.rowCount()):
            type_item = event_manager.events_table.item(row, 2)  # 事件类型列
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
        
        return key_press_count, key_release_count, mouse_move_count, mouse_click_count
    
    def generate_stats_text(self, row_count, key_press_count, key_release_count, mouse_move_count, 
                          mouse_click_count, single_loop_time_ms, total_time_ms, avg_interval, 
                          loop_count, interval, time_unit, width, height, scale):
        """生成统计信息文本"""
        return f"""═════════════════
📊 脚本统计信息
═════════════════

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

📝 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"""
    
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
    
    def calculate_single_loop_time_ms(self, event_manager):
        """计算单次循环的总时间（毫秒）"""
        try:
            # 获取单次循环时间（最后一个事件的绝对时间）
            if event_manager.events_table.rowCount() == 0:
                return 0
            last_row = event_manager.events_table.rowCount() - 1
            time_item = event_manager.events_table.item(last_row, 7)  # 绝对偏移列
            if time_item and time_item.text().isdigit():
                return int(time_item.text())
            else:
                return 0
        except Exception as e:
            self.debug_logger.log_error(f"计算单次循环时间失败: {e}")
            return 0
    
    def calculate_total_time_ms(self, single_loop_time, loop_count, interval_ms):
        """计算整个脚本的总时间（毫秒）"""
        try:
            # 总时间 = 单次循环时间 * 循环次数 + 间隔时间 * (循环次数 - 1)
            total_time = single_loop_time * loop_count + interval_ms * (loop_count - 1)
            return total_time
        except Exception as e:
            self.debug_logger.log_error(f"计算总时间失败: {e}")
            return 0
    
    def update_stats_display(self, stats_text):
        """更新统计信息显示 - 保持向后兼容"""
        self.stats_text.setPlainText(stats_text)
