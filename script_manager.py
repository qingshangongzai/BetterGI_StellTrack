# script_manager.py
import os
import json
from datetime import datetime
from PyQt6.QtWidgets import QFileDialog, QMessageBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar, QPushButton
from PyQt6.QtGui import QDesktopServices, QFont
from PyQt6.QtCore import QThread, pyqtSignal, Qt

# 导入共享模块
from styles import ChineseMessageBox, UnifiedStyleHelper, FadeInWindowMixin, StyledDialog, get_global_font_manager, DialogFactory
from utils import VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP, convert_event_type_str_to_num, convert_event_type_num_to_str, get_key_chinese_name, get_event_data_from_table, check_event_pairing, load_icon_universal
from debug_tools import get_global_debug_logger

# =============================================================================
# 脚本生成进度对话框
# =============================================================================

class ScriptGenerationProgressDialog(FadeInWindowMixin, StyledDialog):
    """脚本生成进度对话框,显示脚本生成过程的进度"""
    
    # 定义信号
    cancel_requested = pyqtSignal()  # 取消请求信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_cancelled = False
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("生成脚本")
        self.setFixedSize(500, 220)
        
        # 设置窗口标志,保留关闭按钮
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 设置窗口图标
        self.setWindowIcon(load_icon_universal())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # 标题区域
        title_label = QLabel("正在生成脚本...")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 14, QFont.Weight.Bold)
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin-bottom: 5px;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # 状态标签
        self.status_label = QLabel("准备开始...")
        UnifiedStyleHelper.get_instance().set_source_han_font(self.status_label, 10)
        self.status_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']};")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(UnifiedStyleHelper.get_instance().get_progress_bar_style())
        self.progress_bar.setFixedHeight(20)
        layout.addWidget(self.progress_bar)
        
        # 添加弹性空间
        layout.addStretch()
        
        # 取消按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        UnifiedStyleHelper.get_instance().set_source_han_font(self.cancel_button, 9)
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self.on_cancel_clicked)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def update_progress(self, value, status_text):
        """更新进度条和状态文本
        
        Args:
            value: 进度值 (0-100)
            status_text: 状态文本
        """
        self.progress_bar.setValue(value)
        self.status_label.setText(status_text)
    
    def on_cancel_clicked(self):
        """取消按钮点击事件"""
        if not self.is_cancelled:
            self.is_cancelled = True
            self.cancel_requested.emit()
            self.status_label.setText("正在取消...")
            self.cancel_button.setEnabled(False)
    
    def closeEvent(self, event):
        """重写关闭事件,直接取消操作"""
        # 如果已经取消或已经完成,直接关闭
        if self.is_cancelled or self.progress_bar.value() == 100:
            event.accept()
            return
        
        # 直接取消,不弹出确认对话框
        self.is_cancelled = True
        self.cancel_requested.emit()
        event.accept()

# =============================================================================
# 脚本管理类
# =============================================================================

class GenerateScriptThread(QThread):
    """脚本生成线程类，负责在后台生成脚本"""
    
    # 信号定义
    script_generated = pyqtSignal(dict, str)  # 脚本生成成功信号
    script_generation_failed = pyqtSignal(str)  # 脚本生成失败信号
    pairing_check_failed = pyqtSignal(list)  # 事件成对性检查失败信号
    pairing_check_passed = pyqtSignal()  # 事件成对性检查通过信号
    progress_updated = pyqtSignal(int, str)  # 进度更新信号 (进度值, 状态文本)
    
    def __init__(self, main_window, events_table):
        super().__init__()
        self.main_window = main_window
        self.events_table = events_table
        self.debug_logger = get_global_debug_logger()
        self.is_cancelled = False  # 取消标志
    
    def cancel(self):
        """请求取消线程执行"""
        self.is_cancelled = True
        self.debug_logger.log_info("用户请求取消脚本生成")
    
    def run(self):
        """线程运行方法，执行脚本生成逻辑"""
        try:
            self.debug_logger.log_info("开始生成脚本...")
            
            # 收集事件数据
            events = []
            total_rows = self.events_table.rowCount()
            
            # 报告开始收集事件
            self.progress_updated.emit(0, "正在收集事件数据...")
            
            for row in range(total_rows):
                # 检查是否被取消
                if self.is_cancelled:
                    self.script_generation_failed.emit("脚本生成已取消")
                    return
                
                event_data = get_event_data_from_table(self.events_table, row)
                
                if event_data[0]:  # 如果事件名称不为空
                    # 转换为脚本格式
                    event_type_num = convert_event_type_str_to_num(event_data[1])
                    script_event = {
                        "type": event_type_num,
                        "mouseX": int(event_data[3]) if event_data[3] else 0,
                        "mouseY": int(event_data[4]) if event_data[4] else 0,
                        "time": int(event_data[6]) if event_data[6] else 0  # 使用绝对偏移时间
                    }
                    
                    # 如果是键盘事件，添加keyCode
                    if event_data[1] in ["按键按下", "按键释放"] and event_data[2]:
                        script_event["keyCode"] = int(event_data[2])
                    
                    # 如果是鼠标点击事件，添加mouseButton
                    if event_data[1] in ["左键按下", "左键释放"]:
                        script_event["mouseButton"] = "Left"
                    elif event_data[1] in ["右键按下", "右键释放"]:
                        script_event["mouseButton"] = "Right"
                    elif event_data[1] in ["中键按下", "中键释放"]:
                        script_event["mouseButton"] = "Middle"
                    
                    events.append(script_event)
                
                # 更新进度（收集事件阶段占20%）
                if total_rows > 0:
                    progress = int((row + 1) / total_rows * 20)
                    self.progress_updated.emit(progress, f"正在收集事件数据... ({row + 1}/{total_rows})")
            
            if not events:
                self.script_generation_failed.emit("没有事件可生成脚本")
                return
            
            # 检查是否被取消
            if self.is_cancelled:
                self.script_generation_failed.emit("脚本生成已取消")
                return
            
            # 获取循环次数
            loop_count = self.main_window.settings_panel.get_safe_loop_count()
            
            # 获取间隔时间
            interval = self.main_window.settings_panel.interval_input.value()
            
            # 转换时间单位为毫秒
            time_unit = self.main_window.settings_panel.time_unit_combo.currentText()
            if time_unit == "s":
                interval_ms = int(interval * 1000)
            elif time_unit == "min":
                interval_ms = int(interval * 60000)
            else:  # ms
                interval_ms = int(interval)
            
            # 报告开始生成循环事件
            self.progress_updated.emit(20, "正在生成循环事件...")
            
            # 生成完整的事件序列（考虑循环）
            full_events = []
            last_event_time = 0
            total_events_count = len(events) * loop_count
            processed_count = 0
            
            for loop in range(loop_count):
                # 在每个循环开始时检查取消
                if self.is_cancelled:
                    self.script_generation_failed.emit("脚本生成已取消")
                    return
                
                for i, event in enumerate(events):
                    # 复制事件
                    new_event = event.copy()
                    
                    # 确保时间值为整数
                    event_time = int(event["time"])
                    
                    # 如果是第一个循环，使用原始时间
                    if loop == 0:
                        new_event["time"] = event_time
                    else:
                        # 后续循环：时间 = 原始时间 + (循环索引 * (最后一个事件时间 + 间隔时间))
                        new_event["time"] = event_time + loop * (last_event_time + interval_ms)
                    
                    full_events.append(new_event)
                    processed_count += 1
                    
                    # 每处理50个事件检查一次取消状态（提高响应速度）
                    if processed_count % 50 == 0:
                        if self.is_cancelled:
                            self.script_generation_failed.emit("脚本生成已取消")
                            return
                    
                    # 更新进度（生成循环事件阶段占60%，从20%到80%）
                    if total_events_count > 0:
                        progress = 20 + int((processed_count / total_events_count) * 60)
                        self.progress_updated.emit(progress, f"正在生成循环事件... ({processed_count}/{total_events_count})")
                
                # 更新最后一个事件的时间
                if events:
                    last_event_time = int(events[-1]["time"])
            
            # 报告生成脚本结构
            self.progress_updated.emit(80, "正在生成脚本结构...")
            
            # 检查是否被取消
            if self.is_cancelled:
                self.script_generation_failed.emit("脚本生成已取消")
                return
            
            # 获取缩放比例并转换为小数
            scale_str = self.main_window.settings_panel.scale_combo.currentText()
            try:
                record_dpi = float(scale_str.strip('%')) / 100.0
            except ValueError:
                record_dpi = 1.0  # 如果转换失败，使用默认值1.0
            
            # 获取应用信息用于脚本描述
            from utils import get_current_app_info
            app_info = get_current_app_info()
            
            # 脚本结构
            script = {
                "macroEvents": full_events,
                "info": {
                    "description": "由BetterGI StellTrack创建",
                    "x": 0,
                    "y": 0,
                    "width": int(self.main_window.settings_panel.width_input.text()),
                    "height": int(self.main_window.settings_panel.height_input.text()),
                    "recordDpi": record_dpi
                }
            }
            
            # 报告完成
            self.progress_updated.emit(100, "脚本生成完成！")
            
            # 发送成功信号前再次检查取消状态
            if self.is_cancelled:
                self.script_generation_failed.emit("脚本生成已取消")
                return
            
            # 生成默认文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            default_filename = f"BetterGI_GCM_{timestamp}.json"
            
            # 发送脚本生成成功信号
            self.script_generated.emit(script, default_filename)
            
        except Exception as e:
            error_msg = f"生成脚本失败: {str(e)}"
            self.script_generation_failed.emit(error_msg)


class CheckEventPairingThread(QThread):
    """事件成对性检查线程类，负责在后台检查事件成对性"""
    
    # 信号定义
    pairing_check_complete = pyqtSignal(bool, list)  # 检查完成信号
    
    def __init__(self, events_table):
        super().__init__()
        self.events_table = events_table
        self.debug_logger = get_global_debug_logger()
    
    def run(self):
        """线程运行方法，执行事件成对性检查逻辑"""
        issues = check_event_pairing(self.events_table)
        
        # 发送检查完成信号
        self.pairing_check_complete.emit(len(issues) == 0, issues)


class ImportScriptThread(QThread):
    """脚本导入线程类，负责在后台导入脚本"""
    
    # 信号定义
    import_complete = pyqtSignal(list)  # 导入完成信号
    import_failed = pyqtSignal(str)  # 导入失败信号
    
    def __init__(self, filename, event_manager):
        super().__init__()
        self.filename = filename
        self.event_manager = event_manager
        self.debug_logger = get_global_debug_logger()
    
    def run(self):
        """线程运行方法，执行脚本导入逻辑"""
        try:
            # 读取并解析脚本文件
            with open(self.filename, 'r', encoding='utf-8') as f:
                script_data = json.load(f)
            
            # 检查脚本格式是否正确
            if "macroEvents" not in script_data:
                self.import_failed.emit("无效的脚本格式: 缺少macroEvents字段")
                return
            
            # 导入事件
            imported_events = []
            for i, event in enumerate(script_data["macroEvents"]):
                # 转换事件类型
                event_type = convert_event_type_num_to_str(event["type"])
                
                # 获取事件数据
                keycode = str(event.get("keyCode", "")) if event_type in ["按键按下", "按键释放"] else ""
                mouse_x = str(event.get("mouseX", 0))
                mouse_y = str(event.get("mouseY", 0))
                time = str(event.get("time", 0))
                
                # 生成事件名称
                from utils import generate_key_event_name
                event_name = generate_key_event_name(event_type, keycode)
                
                # 添加到导入事件列表
                imported_events.append([
                    str(i + 1),  # 行号
                    event_name,  # 事件名称
                    event_type,  # 事件类型
                    keycode,  # 键码
                    mouse_x,  # X坐标
                    mouse_y,  # Y坐标
                    "0",  # 相对偏移（将在后续重新计算）
                    time  # 绝对偏移
                ])
            
            # 发送导入完成信号
            self.import_complete.emit(imported_events)
            
        except json.JSONDecodeError:
            self.import_failed.emit("无效的JSON文件格式")
        except Exception as e:
            self.import_failed.emit(f"导入脚本失败: {str(e)}")


class ScriptManager:
    """脚本管理类，负责所有与脚本生成、导入和管理相关的操作
    
    核心功能包括：
    - 脚本生成：将事件表格数据转换为BetterGI可执行的脚本
    - 脚本验证：检查事件成对性和完整性
    - 脚本导出：保存生成的脚本到文件
    - 脚本导入：从文件加载脚本并转换为事件表格数据
    - 多线程处理：使用线程在后台执行耗时操作，确保UI响应流畅
    """
    
    def __init__(self, main_window):
        """初始化脚本管理器
        
        Args:
            main_window: 主窗口实例，用于访问事件管理器和其他组件
        """
        self.main_window = main_window
        self.debug_logger = get_global_debug_logger()
        self.script = None  # 存储生成的脚本
        
        # 线程实例，用于处理耗时操作
        self.generate_script_thread = None
        self.check_pairing_thread = None
        self.import_script_thread = None
        
        # 进度对话框
        self.progress_dialog = None
    
    def on_generate_script(self):
        """启动脚本生成流程
        
        首先检查事件成对性，然后启动脚本生成线程。
        处理脚本生成过程中的异常并显示错误信息。
        """
        try:
            self.debug_logger.log_info("开始生成脚本...")
            
            # 检查事件成对性
            event_manager = self.main_window.event_manager
            
            # 创建并启动事件成对性检查线程
            self.check_pairing_thread = CheckEventPairingThread(event_manager.events_table)
            self.check_pairing_thread.pairing_check_complete.connect(self.on_pairing_check_complete)
            self.check_pairing_thread.start()
            
        except Exception as e:
            error_msg = f"生成脚本失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_pairing_check_complete(self, is_passed, issues):
        """事件成对性检查完成回调
        
        根据检查结果决定是否继续生成脚本，如果有问题则询问用户是否继续。
        
        Args:
            is_passed: 布尔值，表示检查是否通过
            issues: 字符串列表，包含检查出的问题
        """
        if not is_passed:
            # 显示详细的问题信息，并询问是否继续
            message = "检测到以下事件成对性问题：\n\n" + "\n".join(issues) + "\n\n是否继续生成脚本？"
            self.debug_logger.log_warning(f"事件成对性问题: {issues}")
            
            if not ChineseMessageBox.show_question(self.main_window, "事件成对性检查", message):
                self.debug_logger.log_warning("事件成对性检查失败，脚本生成取消")
                return
        
        self.debug_logger.log_info("事件成对性检查通过")
        
        # 成对性检查通过，开始生成脚本
        self.start_generate_script_thread()
    
    def start_generate_script_thread(self):
        """启动脚本生成线程
        
        创建并启动脚本生成线程，连接相关信号处理程序。
        如果事件数量较多，显示进度对话框。
        """
        event_manager = self.main_window.event_manager
        
        # 检查事件数量，如果超过阈值则显示进度条
        event_count = event_manager.events_table.rowCount()
        loop_count = self.main_window.settings_panel.get_safe_loop_count()
        total_events = event_count * loop_count
        
        # 设置阈值：总事件数超过1000时显示进度条
        PROGRESS_THRESHOLD = 1000
        
        # 如果事件数量过多，先弹出确认对话框
        if total_events > PROGRESS_THRESHOLD:
            reply = ChineseMessageBox.show_question(
                self.main_window,
                "确认生成",
                "生成的事件数量过多，\n可能会对程序的运行造成卡顿，\n\n请确认生成脚本"
            )
            
            if not reply:
                # 用户选择取消
                self.debug_logger.log_info("用户取消生成大量事件脚本")
                return
            
            # 用户确认，创建并显示进度对话框
            self.progress_dialog = ScriptGenerationProgressDialog(self.main_window)
            # 连接取消信号
            self.progress_dialog.cancel_requested.connect(self.on_cancel_requested)
            
        # 创建并启动脚本生成线程
        self.generate_script_thread = GenerateScriptThread(self.main_window, event_manager.events_table)
        self.generate_script_thread.script_generated.connect(self.on_script_generated)
        self.generate_script_thread.script_generation_failed.connect(self.on_script_generation_failed)
        
        # 连接进度更新信号
        if self.progress_dialog:
            self.generate_script_thread.progress_updated.connect(self.on_progress_updated)
            self.progress_dialog.show()
        
        self.generate_script_thread.start()
    
    def on_cancel_requested(self):
        """处理取消请求"""
        if self.generate_script_thread and self.generate_script_thread.isRunning():
            self.debug_logger.log_info("用户请求取消脚本生成")
            self.generate_script_thread.cancel()
    
    def on_progress_updated(self, value, status_text):
        """进度更新回调
        
        Args:
            value: 进度值 (0-100)
            status_text: 状态文本
        """
        if self.progress_dialog:
            self.progress_dialog.update_progress(value, status_text)
    
    def on_script_generated(self, script, default_filename):
        """脚本生成成功回调"""
        try:
            # 关闭进度对话框
            if self.progress_dialog:
                self.progress_dialog.accept()
                self.progress_dialog = None
            
            # 存储生成的脚本
            self.script = script
            
            # 同时存储到主窗口，以便预览功能使用
            self.main_window.script = self.script
            
            # 更新统计信息
            self.main_window.stats_panel.update_stats()
            
            # 获取循环次数
            loop_count = self.main_window.settings_panel.get_safe_loop_count()
            
            self.main_window.status_bar.showMessage("✅ 脚本生成成功")
            self.debug_logger.log_info(f"脚本生成成功: {len(script['macroEvents'])} 个事件, {loop_count} 次循环")
            ChineseMessageBox.show_info(self.main_window, "成功", f"脚本已成功生成！\n包含 {len(script['macroEvents'])} 个事件 ({loop_count} 次循环)\n文件名: {default_filename}")
        except Exception as e:
            error_msg = f"处理生成的脚本时失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_script_generation_failed(self, error_msg):
        """脚本生成失败回调"""
        # 关闭进度对话框
        if self.progress_dialog:
            self.progress_dialog.reject()
            self.progress_dialog = None
        
        self.debug_logger.log_warning(error_msg)
        ChineseMessageBox.show_warning(self.main_window, "警告", error_msg)
    
    def check_event_pairing(self):
        """检查事件成对性"""
        event_manager = self.main_window.event_manager
        issues = check_event_pairing(event_manager.events_table)
        
        if issues:
            # 显示详细的问题信息，并询问是否继续
            message = "检测到以下事件成对性问题：\n\n" + "\n".join(issues) + "\n\n是否继续生成脚本？"
            self.debug_logger.log_warning(f"事件成对性问题: {issues}")
            return ChineseMessageBox.show_question(self.main_window, "事件成对性检查", message)
        
        self.debug_logger.log_info("事件成对性检查通过")
        return True
    

    
    def on_save_script(self):
        """保存脚本"""
        try:
            if not self.script:
                self.debug_logger.log_warning("尝试保存但未生成脚本")
                ChineseMessageBox.show_warning(self.main_window, "警告", "请先生成脚本")
                return
            
            # 生成默认文件名
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")[:-3]
            default_filename = f"BetterGI_GCM_{timestamp}.json"
            
            filename, _ = QFileDialog.getSaveFileName(
                self.main_window,
                "保存脚本",
                default_filename,
                "JSON文件 (*.json);;所有文件 (*.*)"
            )
            
            if not filename:
                self.debug_logger.log_info("用户取消保存脚本")
                return
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.script, f, ensure_ascii=False, separators=(',', ':'))
            
            self.main_window.status_bar.showMessage(f"✅ 脚本已保存到: {filename}")
            self.debug_logger.log_info(f"脚本已保存到: {filename}")
            ChineseMessageBox.show_info(self.main_window, "成功", f"脚本已保存到:\n{filename}")
            
        except Exception as e:
            error_msg = f"保存脚本失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_import_script(self):
        """导入脚本"""
        try:
            # 显示警告弹窗
            reply = ChineseMessageBox.show_question(
                self.main_window,
                "导入脚本警告",
                "导入脚本会清空现有事件列表！\n请确保已保存当前事件列表后再导入。\n\n是否继续导入？"
            )
            
            if not reply:
                self.debug_logger.log_info("用户取消导入脚本")
                return
            
            # 打开文件对话框选择要导入的脚本文件
            filename, _ = QFileDialog.getOpenFileName(
                self.main_window,
                "导入脚本",
                "",
                "JSON文件 (*.json);;所有文件 (*.*)"
            )
            
            if not filename:
                self.debug_logger.log_info("用户取消导入脚本")
                return
            
            event_manager = self.main_window.event_manager
            
            # 创建并启动脚本导入线程
            self.import_script_thread = ImportScriptThread(filename, event_manager)
            self.import_script_thread.import_complete.connect(self.on_import_complete)
            self.import_script_thread.import_failed.connect(self.on_import_failed)
            self.import_script_thread.start()
            
        except Exception as e:
            error_msg = f"导入脚本失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_import_complete(self, imported_events):
        """脚本导入完成回调"""
        try:
            event_manager = self.main_window.event_manager
            
            # 清空当前事件
            event_manager.events_table.setRowCount(0)
            
            # 重置搜索筛选条件，确保导入的事件都能显示出来
            event_manager.on_reset_search_filter()
            
            # 保存当前状态到撤销栈
            self.main_window.save_state_to_undo_stack()
            
            # 开始批量操作
            self.main_window._batch_operation = True
            
            try:
                # 导入事件
                event_manager.add_table_rows(imported_events)
                
                # 重新计算相对时间
                event_manager.recalculate_relative_times()
                
                # 更新行号
                event_manager.update_row_numbers()
                
                # 更新统计信息
                event_manager.update_stats()
                
                # 标记状态变更
                self.main_window.mark_state_dirty()
                
                self.main_window.status_bar.showMessage("✅ 脚本导入成功")
                self.debug_logger.log_info(f"脚本导入成功: {len(imported_events)} 个事件")
                ChineseMessageBox.show_info(self.main_window, "成功", f"脚本导入成功！\n包含 {len(imported_events)} 个事件")
                
                # 立即更新预计总时间
                self.main_window.on_calculate_total_time()
            finally:
                # 结束批量操作
                self.main_window._batch_operation = False
                
        except Exception as e:
            error_msg = f"处理导入的脚本时失败: {str(e)}"
            self.debug_logger.log_error(error_msg, exc_info=True)
            ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    
    def on_import_failed(self, error_msg):
        """脚本导入失败回调"""
        self.debug_logger.log_error(f"导入脚本失败: {error_msg}")
        ChineseMessageBox.show_error(self.main_window, "错误", error_msg)
    

