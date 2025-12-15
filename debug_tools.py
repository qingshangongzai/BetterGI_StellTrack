# debug_tools.py
import sys
import os
import json
import traceback
import logging
import threading
import time
import queue
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTextEdit, QGroupBox, 
                            QGridLayout, QFileDialog, QMessageBox, QTextBrowser,
                            QProgressBar, QTabWidget, QTreeWidget, QTreeWidgetItem,
                            QSplitter, QCheckBox)
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSignal, QThread
from PyQt6.QtGui import QDesktopServices, QTextCursor, QFont, QColor, QFontDatabase

# 导入共享模块
from styles import UnifiedStyleHelper, get_global_font_manager, StyledDialog, DialogFactory
from styles import ChineseMessageBox
# 导入资源管理器（已从resource_manager合并到styles）
from utils import get_base_path, find_resource_file, get_current_version, get_current_app_info
# 导入版本管理器
from version import version_manager

# =============================================================================
# 输出捕获类 - 简化版
# =============================================================================

class SafeOutputCapture:
    """安全的输出捕获类，避免递归问题
    
    用于捕获标准输出和标准错误，并将其重定向到日志文件，同时避免递归调用问题。
    提供线程安全的缓冲区管理和写入机制。
    
    参数：
    - original_stream: 原始流对象（stdout或stderr）
    - logger: 日志记录器实例
    - stream_name: 流名称（"STDOUT"或"STDERR"）
    """
    
    def __init__(self, original_stream, logger, stream_name):
        self.original_stream = original_stream
        self.logger = logger
        self.stream_name = stream_name
        self.buffer = []
        self.buffer_lock = threading.Lock()
        self._is_recursing = False

    def write(self, text):
        """写入文本到原始流和日志"""
        if self.original_stream is None:
            return
            
        if self._is_recursing:
            try:
                self.original_stream.write(text)
                self.original_stream.flush()
            except:
                pass
            return
            
        self._is_recursing = True
        try:
            if text.strip():
                timestamp = datetime.now().strftime("%H:%M:%S")
                formatted_text = f"[{timestamp}] [{self.stream_name}] {text}"
                
                with self.buffer_lock:
                    self.buffer.append(formatted_text)
                    if len(self.buffer) > 1000:
                        self.buffer = self.buffer[-500:]
                
                try:
                    if hasattr(self, 'logger') and self.logger:
                        if self.stream_name == "STDOUT":
                            self.logger.info(text.strip())
                        else:
                            self.logger.error(text.strip())
                except:
                    pass
            
            try:
                self.original_stream.write(text)
                self.original_stream.flush()
            except:
                pass
        finally:
            self._is_recursing = False
    
    def flush(self):
        """刷新原始流"""
        try:
            if self.original_stream is not None:
                self.original_stream.flush()
        except:
            pass
    
    def get_buffer(self):
        """获取缓冲区内容"""
        with self.buffer_lock:
            return self.buffer.copy()
    
    def clear_buffer(self):
        """清空缓冲区"""
        with self.buffer_lock:
            self.buffer.clear()

# =============================================================================
# 调试日志记录器 - 简化版
# =============================================================================

class SafeDebugLogger:
    """安全的调试日志记录器，避免递归问题"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SafeDebugLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if SafeDebugLogger._initialized:
            return
            
        SafeDebugLogger._initialized = True
        
        self.performance_data = {
            'start_time': time.time(),
            'error_count': 0,
            'warning_count': 0,
            'info_count': 0
        }
        
        self.log_file = self.get_log_file_path()
        self.console_buffer = []
        self.buffer_lock = threading.Lock()
        
        self.setup_logging()
        self.setup_output_capture()
    
    def get_log_file_path(self):
        """获取日志文件路径"""
        try:
            base_path = get_base_path()
            
            if getattr(sys, 'frozen', False):
                logs_dir = os.path.join(os.path.dirname(sys.executable), "logs")
            else:
                logs_dir = os.path.join(base_path, "logs")
            
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)
            
            # 直接使用version_manager获取应用信息
            app_info = version_manager.get_app_info()
            version = version_manager.get_version()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            return os.path.join(logs_dir, f"{app_info['name_en']}_v{version}_{timestamp}.log")
        except Exception as e:
            print(f"获取日志文件路径失败: {e}")
            return "debug.log"
    
    def setup_logging(self):
        """设置日志记录"""
        try:
            # 直接使用version_manager获取应用信息
            app_info = version_manager.get_app_info()
            version = version_manager.get_version()
            
            # 创建日志记录器
            self.logger = logging.getLogger(f'{app_info["name_en"]}_Debug')
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False
            
            # 移除现有处理器
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)
            
            # 添加文件处理器
            file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            
            self.log_info("安全调试日志系统初始化完成")
            self.log_info(f"应用名称: {app_info['name']} v{version}")
            self.log_info(f"日志文件路径: {self.log_file}")
            
        except Exception as e:
            print(f"设置日志记录失败: {e}")
    
    def setup_output_capture(self):
        """设置输出捕获"""
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        try:
            self.stdout_capture = SafeOutputCapture(
                self.original_stdout, 
                self.logger, 
                "STDOUT"
            )
            sys.stdout = self.stdout_capture
            
            self.stderr_capture = SafeOutputCapture(
                self.original_stderr, 
                self.logger, 
                "STDERR"
            )
            sys.stderr = self.stderr_capture
            
            self.logger.info("安全输出捕获系统已启动")
            
        except Exception as e:
            sys.stdout = self.original_stdout
            sys.stderr = self.original_stderr
            print(f"设置输出捕获失败: {e}")
    
    def restore_output(self):
        """恢复原始输出流"""
        try:
            if hasattr(self, 'original_stdout'):
                sys.stdout = self.original_stdout
            if hasattr(self, 'original_stderr'):
                sys.stderr = self.original_stderr
            self.log_info("输出流已恢复")
        except Exception as e:
            print(f"恢复输出流失败: {e}")
    
    def log_info(self, message):
        """记录信息日志"""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.info(message)
            self.performance_data['info_count'] += 1
        except Exception as e:
            print(f"记录信息日志失败: {e}")
    
    def log_error(self, message, exc_info=None):
        """记录错误日志"""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.error(message, exc_info=exc_info)
            self.performance_data['error_count'] += 1
        except Exception as e:
            print(f"记录错误日志失败: {e}")
    
    def log_warning(self, message):
        """记录警告日志"""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.warning(message)
            self.performance_data['warning_count'] += 1
        except Exception as e:
            print(f"记录警告日志失败: {e}")
    
    def log_debug(self, message):
        """记录调试日志"""
        try:
            if hasattr(self, 'logger') and self.logger:
                self.logger.debug(message)
        except Exception as e:
            print(f"记录调试日志失败: {e}")
    
    def log_system_info(self):
        """记录系统信息"""
        try:
            import platform
            
            # 直接使用version_manager获取应用信息
            app_info = version_manager.get_app_info()
            version = version_manager.get_version()
            version_info = version_manager.get_version_info()
            
            system_info = [
                "=== 系统信息 ===",
                f"应用程序: {app_info['name']} v{version}",
                f"版本详情: {version_info['major']}.{version_info['minor']}.{version_info['patch']}.{version_info['build']}",
                f"操作系统: {platform.system()} {platform.release()}",
                f"系统版本: {platform.version()}",
                f"处理器: {platform.processor()}",
                f"架构: {platform.architecture()[0]}",
                f"Python版本: {platform.python_version()}"
            ]
            
            try:
                import psutil
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                system_info.extend([
                    f"总内存: {memory.total // (1024**3)} GB",
                    f"可用内存: {memory.available // (1024**3)} GB",
                    f"内存使用率: {memory.percent}%",
                    f"总磁盘空间: {disk.total // (1024**3)} GB",
                    f"可用磁盘空间: {disk.free // (1024**3)} GB",
                    f"磁盘使用率: {disk.percent}%"
                ])
            except ImportError:
                system_info.append("内存信息: 需要psutil库")
            
            system_info_text = "\n".join(system_info)
            self.log_info(f"系统信息:\n{system_info_text}")
            
        except Exception as e:
            self.log_error(f"记录系统信息失败: {e}")
    
    def get_log_content(self):
        """获取日志文件内容"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                return "日志文件不存在"
        except Exception as e:
            return f"读取日志文件失败: {str(e)}"
    
    def get_console_output(self):
        """获取控制台输出"""
        try:
            stdout_buffer = self.stdout_capture.get_buffer() if hasattr(self, 'stdout_capture') else []
            stderr_buffer = self.stderr_capture.get_buffer() if hasattr(self, 'stderr_capture') else []
            return stdout_buffer + stderr_buffer
        except Exception as e:
            return [f"获取控制台输出失败: {str(e)}"]
    
    def clear_log(self):
        """清空日志文件"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'w', encoding='utf-8') as f:
                    f.write("")
                return True
            return False
        except Exception as e:
            self.log_error(f"清空日志文件失败: {e}")
            return False
    
    def clear_console_buffer(self):
        """清空控制台缓冲区"""
        try:
            if hasattr(self, 'stdout_capture'):
                self.stdout_capture.clear_buffer()
            if hasattr(self, 'stderr_capture'):
                self.stderr_capture.clear_buffer()
            return True
        except Exception as e:
            self.log_error(f"清空控制台缓冲区失败: {e}")
            return False
    
    def get_log_file_info(self):
        """获取日志文件信息"""
        try:
            if os.path.exists(self.log_file):
                file_size = os.path.getsize(self.log_file)
                file_time = datetime.fromtimestamp(os.path.getmtime(self.log_file))
                return {
                    'path': self.log_file,
                    'size': file_size,
                    'modified': file_time.strftime("%Y-%m-%d %H:%M:%S"),
                    'exists': True
                }
            else:
                return {
                    'path': self.log_file,
                    'size': 0,
                    'modified': '文件不存在',
                    'exists': False
                }
        except Exception as e:
            return {
                'path': self.log_file,
                'size': 0,
                'modified': f'获取失败: {str(e)}',
                'exists': False
            }
    
    def get_performance_stats(self):
        """获取性能统计"""
        try:
            uptime = time.time() - self.performance_data['start_time']
            hours, remainder = divmod(uptime, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # 使用版本管理器获取应用信息
            app_info = get_current_app_info()
            version = get_current_version()
            
            stats = {
                'app_name': app_info['name'],
                'app_version': version,
                'uptime': f"{int(hours)}小时{int(minutes)}分钟{int(seconds)}秒",
                'error_count': self.performance_data['error_count'],
                'warning_count': self.performance_data['warning_count'],
                'info_count': self.performance_data['info_count'],
                'log_file': self.log_file
            }
            
            return stats
        except Exception as e:
            self.log_error(f"获取性能统计失败: {e}")
            return {}

# =============================================================================
# 后台日志监控线程
# =============================================================================

class SafeLogMonitorThread(QThread):
    """安全的日志监控线程，用于实时监控日志文件和控制台输出变化
    
    信号:
        log_updated (str): 当日志文件内容更新时发出
    """
    
    log_updated = pyqtSignal(str)
    
    def __init__(self, debug_logger):
        """初始化监控线程
        
        参数:
            debug_logger: SafeDebugLogger实例，用于获取日志信息
        """
        super().__init__()
        self.debug_logger = debug_logger
        self.running = True
        self.last_size = 0
    
    def run(self):
        """运行监控线程，定期检查日志文件变化"""
        while self.running:
            try:
                # 检查日志文件是否存在并读取更新
                if os.path.exists(self.debug_logger.log_file):
                    current_size = os.path.getsize(self.debug_logger.log_file)
                    if current_size != self.last_size:
                        self.last_size = current_size
                        try:
                            with open(self.debug_logger.log_file, 'r', encoding='utf-8') as f:
                                content = f.read()
                                self.log_updated.emit(content)
                        except Exception as e:
                            print(f"读取日志文件失败: {e}")
                
                # 短暂休眠，避免资源占用过高
                time.sleep(2)
                
            except Exception as e:
                print(f"日志监控错误: {e}")
                # 错误发生时延长休眠时间，避免频繁报错
                time.sleep(5)
    
    def stop(self):
        """安全停止监控线程"""
        self.running = False

# =============================================================================
# 密码验证对话框
# =============================================================================

class PasswordDialog(QDialog):
    """安全调试工具的密码验证对话框
    
    该对话框用于保护调试工具的访问权限，只有输入正确密码的用户才能使用调试功能。
    密码验证成功后，对话框返回QDialog.DialogCode.Accepted，否则继续显示供用户重试。
    """
    
    # 调试工具的访问密码
    DEBUG_PASSWORD = "39782877"
    
    def __init__(self, parent=None):
        """初始化密码验证对话框
        
        参数:
            parent: 父窗口组件
        """
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """设置密码验证对话框的UI界面
        
        配置对话框的标题、大小、窗口标志、布局和样式，确保密码输入体验良好。
        设置OK按钮为默认按钮，并将回车键连接到密码验证功能。
        """
        try:
            self.setWindowTitle("调试工具 - 密码验证")
            self.setFixedSize(350, 150)
            
            # 设置窗口标志，确保对话框样式一致
            self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                               Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
            
            # 创建主布局
            layout = QVBoxLayout(self)
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)
            
            # 标题标签
            title_label = QLabel("请输入调试工具访问密码")
            title_label.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
            layout.addWidget(title_label)
            
            # 密码输入框
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.password_input.setPlaceholderText("输入密码...")
            self.password_input.setStyleSheet(UnifiedStyleHelper.get_instance().get_line_edit_style())
            self.password_input.returnPressed.connect(self.verify_password)
            layout.addWidget(self.password_input)
            
            # 使用DialogFactory创建确定和取消按钮布局
            button_layout = DialogFactory.create_ok_cancel_buttons(
                parent=self,
                on_ok=self.verify_password,
                on_cancel=self.reject,
                ok_text="确定",
                cancel_text="取消"
            )
            
            layout.addLayout(button_layout)
            
            # 获取按钮引用
            self.ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
            self.cancel_btn = button_layout.itemAt(2).widget()
            
            # 设置确定按钮为默认按钮
            self.ok_btn.setDefault(True)
            
            # 自动聚焦到密码输入框
            self.password_input.setFocus()
        except Exception as e:
            print(f"设置密码对话框UI失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
    
    def verify_password(self):
        """验证用户输入的密码
        
        获取用户输入的密码并与预设密码进行比较。如果密码正确，则接受对话框；
        如果密码错误，则显示错误消息并清空输入框，让用户重新输入。
        """
        try:
            password = self.password_input.text().strip()
            if password == self.DEBUG_PASSWORD:
                self.accept()
            else:
                # 显示错误消息
                ChineseMessageBox.show_error(self, "错误", "密码错误，请重新输入！")
                # 清空输入框并重新聚焦
                self.password_input.clear()
                self.password_input.setFocus()
        except Exception as e:
            print(f"验证密码失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
            # 显示通用错误消息
            ChineseMessageBox.show_error(self, "错误", "验证过程中发生错误，请重试。")
            # 确保输入框可用
            if hasattr(self, 'password_input'):
                self.password_input.setFocus()

# =============================================================================
# 调试窗口
# =============================================================================

class SafeDebugWindow(StyledDialog):
    """安全的调试窗口，用于显示和管理应用程序的日志和调试信息
    
    该窗口提供了实时日志监控、系统信息展示、日志文件管理等功能，
    同时采用了防止递归日志记录的安全机制，确保调试过程不会影响主程序运行。
    """
    
    def __init__(self, parent=None):
        """初始化调试窗口
        
        参数:
            parent: 父窗口组件
        """
        try:
            # 使用版本管理器获取应用信息
            app_info = get_current_app_info()
            version = get_current_version()
            
            # 使用基类初始化方法设置窗口属性
            super().__init__(parent,
                           title=f"安全调试工具 - {app_info['name']} v{version}",
                           window_flags=Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                                      Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
            
            # 设置最小尺寸
            self.setMinimumSize(900, 700)
            
            # 初始化调试日志记录器
            self.debug_logger = SafeDebugLogger()
            # 监控线程
            self.monitor_thread = None
            # 初始化状态标志
            self._is_initialized = False
            
            # 设置UI界面
            self.setup_ui()
            # 设置信号连接
            self.setup_connections()
            
            # 延迟启动监控和刷新显示，确保UI完全初始化
            QTimer.singleShot(100, self.start_monitoring)
            QTimer.singleShot(200, self.refresh_all_displays)
        except Exception as e:
            print(f"初始化调试窗口失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
        
    def setup_ui(self):
        """设置调试窗口的UI界面
        
        配置窗口标题、大小、窗口标志，并创建各个功能区域：
        - 标题区域
        - 应用信息显示区域
        - 文件信息区域
        - 日志显示区域
        - 操作按钮区域
        - 测试功能区域
        
        设置完成后，将初始化状态标志设置为True。
        """
        try:
            # 创建主布局
            layout = QVBoxLayout(self)
            layout.setSpacing(12)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # 创建标题
            title_label = QLabel("安全调试工具")
            # 使用UnifiedStyleHelper统一设置字体
            UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 18, QFont.Weight.Bold)
            title_label.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {UnifiedStyleHelper.get_instance().COLORS['primary']}; margin: 5px;")
            layout.addWidget(title_label)
            
            # 创建各个功能区域
            self.create_app_info_section(layout)
            self.create_file_info_section(layout)
            self.create_log_display_section(layout)
            self.create_operation_buttons(layout)
            self.create_test_functions(layout)
            
            # 标记UI初始化完成
            self._is_initialized = True
        except Exception as e:
            print(f"设置调试窗口UI失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
            # 确保状态标志设置为False
            self._is_initialized = False
    
    def create_app_info_section(self, parent_layout):
        """创建应用信息显示区域
        
        在调试窗口中创建显示应用程序基本信息的区域，包括：
        - 应用名称（中英文）
        - 当前版本号
        - 详细版本号（主版本.次版本.修订版本.构建版本）
        - 开发公司信息
        
        参数:
            parent_layout: 父布局组件，信息区域将被添加到此布局中
        """
        try:
            # 创建应用信息分组框
            info_group = QGroupBox("应用信息")
            # 使用网格布局排列信息项
            info_layout = QGridLayout(info_group)
            info_layout.setSpacing(8)
            info_layout.setContentsMargins(12, 15, 12, 12)
            
            try:
                # 使用版本管理器获取应用信息
                app_info = get_current_app_info()
                version = get_current_version()
                version_info = version_manager.get_version_info()
            except Exception as e:
                print(f"获取应用信息失败: {e}")
                # 使用默认值
                app_info = {'name': '未知应用', 'name_en': 'Unknown App', 'company': '未知公司'}
                version = 'v0.0.0'
                version_info = {'major': 0, 'minor': 0, 'patch': 0, 'build': 0}
            
            # 添加应用名称信息行
            info_layout.addWidget(QLabel("应用名称:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
            app_name_label = QLabel(f"{app_info.get('name', '未知应用')} ({app_info.get('name_en', 'Unknown App')})")
            app_name_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(app_name_label, 0, 1)
            
            # 添加当前版本信息行
            info_layout.addWidget(QLabel("当前版本:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
            version_label = QLabel(version)
            version_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(version_label, 1, 1)
            
            # 添加版本详情信息行
            info_layout.addWidget(QLabel("版本详情:"), 2, 0, Qt.AlignmentFlag.AlignLeft)
            version_detail_label = QLabel(f"{version_info.get('major', 0)}.{version_info.get('minor', 0)}.{version_info.get('patch', 0)}.{version_info.get('build', 0)}")
            version_detail_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(version_detail_label, 2, 1)
            
            # 添加开发公司信息行
            info_layout.addWidget(QLabel("开发公司:"), 3, 0, Qt.AlignmentFlag.AlignLeft)
            company_label = QLabel(app_info.get("company", "未知公司"))
            company_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(company_label, 3, 1)
            
            # 将信息分组框添加到父布局
            parent_layout.addWidget(info_group)
        except Exception as e:
            print(f"创建应用信息区域失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
    
    def create_file_info_section(self, parent_layout):
        """创建日志文件信息显示区域
        
        在调试窗口中创建显示日志文件相关信息的区域，包括：
        - 日志文件完整路径（支持鼠标选中复制）
        - 日志文件大小
        - 日志文件最后修改时间
        
        参数:
            parent_layout: 父布局组件，信息区域将被添加到此布局中
        """
        try:
            # 创建日志文件信息分组框
            info_group = QGroupBox("日志文件信息")
            # 使用网格布局排列信息项
            info_layout = QGridLayout(info_group)
            info_layout.setSpacing(8)
            info_layout.setContentsMargins(12, 15, 12, 12)
            
            try:
                # 获取日志文件信息
                file_info = self.debug_logger.get_log_file_info()
            except Exception as e:
                print(f"获取日志文件信息失败: {e}")
                # 使用默认值
                file_info = {
                    'path': '获取失败',
                    'size': 0,
                    'modified': '获取失败',
                    'exists': False
                }
            
            # 添加文件路径信息行
            info_layout.addWidget(QLabel("文件路径:"), 0, 0, Qt.AlignmentFlag.AlignLeft)
            self.path_label = QLabel(file_info['path'])
            self.path_label.setStyleSheet(f"color: #0066CC; font-size: 10px;")
            self.path_label.setWordWrap(True)
            # 设置文本可被鼠标选中
            self.path_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            info_layout.addWidget(self.path_label, 0, 1)
            
            # 添加文件大小信息行
            info_layout.addWidget(QLabel("文件大小:"), 1, 0, Qt.AlignmentFlag.AlignLeft)
            size_text = f"{file_info['size']} 字节" if file_info['exists'] else "文件不存在"
            self.size_label = QLabel(size_text)
            self.size_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(self.size_label, 1, 1)
            
            # 添加修改时间信息行
            info_layout.addWidget(QLabel("修改时间:"), 2, 0, Qt.AlignmentFlag.AlignLeft)
            self.modified_label = QLabel(file_info['modified'])
            self.modified_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS.get('text_secondary', '#666666')}; font-size: 10px;")
            info_layout.addWidget(self.modified_label, 2, 1)
            
            # 将信息分组框添加到父布局
            parent_layout.addWidget(info_group)
        except Exception as e:
            print(f"创建日志文件信息区域失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
    
    def create_log_display_section(self, parent_layout):
        """创建日志内容显示区域
        
        在调试窗口中创建用于显示和管理日志内容的区域，包括：
        - 只读的日志文本编辑区域（使用等宽字体提高可读性）
        - 暗色主题样式配置，确保长时间查看日志不会视觉疲劳
        
        参数:
            parent_layout: 父布局组件，日志显示区域将被添加到此布局中
        """
        try:
            # 创建日志显示分组框
            log_group = QGroupBox("日志内容")
            # 使用垂直布局排列日志显示区域
            log_layout = QVBoxLayout(log_group)
            log_layout.setSpacing(8)
            log_layout.setContentsMargins(12, 15, 12, 12)
            
            # 创建日志文本显示区域
            self.log_display = QTextEdit()
            self.log_display.setReadOnly(True)  # 设置为只读模式
            # 配置暗色主题样式，提高长时间阅读的舒适度
            self.log_display.setStyleSheet(UnifiedStyleHelper.get_instance().get_log_display_style())
            log_layout.addWidget(self.log_display)
            
            # 将日志显示区域添加到父布局
            parent_layout.addWidget(log_group)
        except Exception as e:
            print(f"创建日志显示区域失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
    
    def create_operation_buttons(self, parent_layout):
        """创建操作按钮区域
        
        在调试窗口中创建包含多种日志操作功能的按钮区域，包括：
        - 刷新日志按钮：手动触发日志内容更新
        - 清空日志按钮：清除当前日志文件内容
        - 导出日志按钮：将日志保存为本地文件
        - 打开日志目录按钮：在文件管理器中打开日志目录
        
        参数:
            parent_layout: 父布局组件，操作按钮区域将被添加到此布局中
        
        说明:
            - 按钮采用垂直布局包含水平布局的方式，确保整体布局美观
            - 按钮之间设置了适当间距，保持一致的外观和交互风格
            - 导出日志按钮使用强调样式，作为主要操作突出显示
        """
        try:
            # 创建操作按钮分组框
            button_group = QGroupBox("操作")
            # 使用垂直布局作为外层容器
            button_layout = QVBoxLayout(button_group)
            button_layout.setContentsMargins(12, 15, 12, 12)
            
            # 创建按钮水平布局容器
            buttons_container = QWidget()
            buttons_h_layout = QHBoxLayout(buttons_container)
            buttons_h_layout.setSpacing(10)
            buttons_h_layout.setContentsMargins(0, 0, 0, 0)
            
            # 创建刷新日志按钮
            self.refresh_btn = QPushButton("刷新日志")
            self.refresh_btn.setFixedWidth(100)
            self.refresh_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
            self.refresh_btn.clicked.connect(self.refresh_log_display)
            
            # 创建清空日志按钮
            self.clear_btn = QPushButton("清空日志")
            self.clear_btn.setFixedWidth(100)
            self.clear_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
            self.clear_btn.clicked.connect(self.clear_log)
            
            # 创建导出日志按钮，使用强调样式
            self.export_btn = QPushButton("导出日志")
            self.export_btn.setFixedWidth(100)
            self.export_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
            self.export_btn.clicked.connect(self.export_log)
            
            # 创建打开日志目录按钮
            self.open_logs_dir_btn = QPushButton("打开日志目录")
            self.open_logs_dir_btn.setFixedWidth(120)
            self.open_logs_dir_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
            self.open_logs_dir_btn.clicked.connect(self.open_logs_directory)
            
            # 按钮布局，两边添加伸缩项确保按钮居中
            buttons_h_layout.addStretch()
            buttons_h_layout.addWidget(self.refresh_btn)
            buttons_h_layout.addWidget(self.clear_btn)
            buttons_h_layout.addWidget(self.export_btn)
            buttons_h_layout.addWidget(self.open_logs_dir_btn)
            buttons_h_layout.addStretch()
            
            # 将按钮容器添加到垂直布局
            button_layout.addWidget(buttons_container)
            # 将操作按钮区域添加到父布局
            parent_layout.addWidget(button_group)
        except Exception as e:
            print(f"创建操作按钮区域失败: {e}")
            # 记录异常详情
            import traceback
            traceback.print_exc()
    
    def create_test_functions(self, parent_layout):
        """创建测试功能区域"""
        test_group = QGroupBox("测试功能")
        test_layout = QVBoxLayout(test_group)
        test_layout.setSpacing(8)
        test_layout.setContentsMargins(12, 15, 12, 12)
        
        test_container = QWidget()
        test_h_layout = QHBoxLayout(test_container)
        test_h_layout.setSpacing(10)
        test_h_layout.setContentsMargins(0, 0, 0, 0)
        
        self.test_log_btn = QPushButton("测试日志记录")
        self.test_log_btn.setFixedWidth(120)
        self.test_log_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.test_log_btn.clicked.connect(self.test_logging)
        
        self.test_exception_btn = QPushButton("测试异常捕获")
        self.test_exception_btn.setFixedWidth(120)
        self.test_exception_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.test_exception_btn.clicked.connect(self.test_exception)
        
        self.system_info_btn = QPushButton("系统信息")
        self.system_info_btn.setFixedWidth(100)
        self.system_info_btn.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        self.system_info_btn.clicked.connect(self.show_system_info)
        
        test_h_layout.addStretch()
        test_h_layout.addWidget(self.test_log_btn)
        test_h_layout.addWidget(self.test_exception_btn)
        test_h_layout.addWidget(self.system_info_btn)
        test_h_layout.addStretch()
        
        test_layout.addWidget(test_container)
        
        test_explanation = QLabel("测试功能用于验证调试系统的正常运行，不会影响程序主功能")
        test_explanation.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text_secondary']}; font-size: 10px; font-style: italic; margin-top: 5px;")
        test_explanation.setAlignment(Qt.AlignmentFlag.AlignCenter)
        test_layout.addWidget(test_explanation)
        
        parent_layout.addWidget(test_group)
    
    def setup_connections(self):
        """设置信号连接"""
        pass
    
    def start_monitoring(self):
        """开始监控"""
        if not self._is_initialized:
            return
            
        try:
            self.monitor_thread = SafeLogMonitorThread(self.debug_logger)
            self.monitor_thread.log_updated.connect(self.append_log_content)
            self.monitor_thread.start()
        except Exception as e:
            print(f"启动监控线程失败: {e}")
    
    def stop_monitoring(self):
        """停止监控"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            if self.monitor_thread.isRunning():
                self.monitor_thread.wait(2000)
    
    def refresh_all_displays(self):
        """刷新所有显示"""
        if not self._is_initialized:
            return
            
        self.refresh_log_display()
    
    def refresh_log_display(self):
        """刷新日志显示"""
        try:
            log_content = self.debug_logger.get_log_content()
            self.log_display.setPlainText(log_content)
            
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()
            
            file_info = self.debug_logger.get_log_file_info()
            self.path_label.setText(file_info['path'])
            size_text = f"{file_info['size']} 字节" if file_info['exists'] else "文件不存在"
            self.size_label.setText(size_text)
            self.modified_label.setText(file_info['modified'])
            
        except Exception as e:
            error_msg = f"刷新日志显示失败: {str(e)}"
            self.log_display.setPlainText(error_msg)
    
    def append_log_content(self, new_content):
        """追加日志内容"""
        if not new_content or not self._is_initialized:
            return
            
        try:
            cursor = self.log_display.textCursor()
            cursor.movePosition(QTextCursor.MoveOperation.End)
            cursor.insertText(new_content)
            self.log_display.setTextCursor(cursor)
            self.log_display.ensureCursorVisible()
        except Exception as e:
            print(f"追加日志内容失败: {e}")
    

    
    def clear_log(self):
        """清空日志"""
        try:
            if self.debug_logger.clear_log():
                self.refresh_log_display()
                self.debug_logger.log_info("日志文件已清空")
                ChineseMessageBox.show_info(self, "成功", "日志文件已清空")
            else:
                ChineseMessageBox.show_error(self, "错误", "清空日志文件失败")
        except Exception as e:
            error_msg = f"清空日志失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def export_log(self):
        """导出日志"""
        try:
            # 使用版本管理器获取应用信息
            app_info = get_current_app_info()
            version = get_current_version()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{app_info['name_en']}_v{version}_Debug_Log_{timestamp}.txt"
            
            filename, _ = QFileDialog.getSaveFileName(
                self,
                "导出调试日志",
                default_filename,
                "文本文件 (*.txt);;所有文件 (*.*)"
            )
            
            if filename:
                log_content = self.debug_logger.get_log_content()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(log_content)
                
                self.debug_logger.log_info(f"日志已导出到: {filename}")
                ChineseMessageBox.show_info(self, "成功", f"日志已导出到:\n{filename}")
                
        except Exception as e:
            error_msg = f"导出日志失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def open_logs_directory(self):
        """打开日志目录"""
        try:
            log_file_path = self.debug_logger.log_file
            logs_directory = os.path.dirname(log_file_path)
            
            if os.path.exists(logs_directory):
                QDesktopServices.openUrl(QUrl.fromLocalFile(logs_directory))
                self.debug_logger.log_info(f"已打开日志目录: {logs_directory}")
            else:
                ChineseMessageBox.show_warning(self, "警告", "日志目录不存在")
                
        except Exception as e:
            error_msg = f"打开日志目录失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def test_logging(self):
        """测试日志记录功能"""
        try:
            # 使用版本管理器获取应用信息
            app_info = get_current_app_info()
            version = get_current_version()
            
            self.debug_logger.log_info("这是一条测试信息日志")
            self.debug_logger.log_warning("这是一条测试警告日志")
            self.debug_logger.log_debug("这是一条测试调试日志")
            
            self.debug_logger.log_info("测试数据示例:")
            self.debug_logger.log_info(f"应用名称: {app_info['name']} v{version}")
            self.debug_logger.log_info(f"当前时间: {datetime.now()}")
            self.debug_logger.log_info(f"Python版本: {sys.version}")
            self.debug_logger.log_info(f"程序路径: {os.path.abspath(__file__)}")
            
            self.refresh_log_display()
            ChineseMessageBox.show_info(self, "测试完成", "测试日志记录已完成，请查看日志内容")
            
        except Exception as e:
            error_msg = f"测试日志记录失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def test_exception(self):
        """测试异常捕获功能"""
        try:
            self.debug_logger.log_info("开始测试异常捕获...")
            
            try:
                result = 10 / 0
            except Exception as e:
                self.debug_logger.log_error("测试异常捕获: 除零错误", exc_info=True)
            
            try:
                nonexistent_obj = None
                nonexistent_obj.some_method()
            except Exception as e:
                self.debug_logger.log_error("测试异常捕获: 空对象方法调用", exc_info=True)
            
            self.refresh_log_display()
            ChineseMessageBox.show_info(self, "测试完成", "异常捕获测试已完成，请查看日志中的异常信息")
            
        except Exception as e:
            error_msg = f"测试异常捕获失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def show_system_info(self):
        """显示系统信息"""
        try:
            self.debug_logger.log_system_info()
            self.refresh_log_display()
            ChineseMessageBox.show_info(self, "系统信息", "系统信息已记录到日志文件")
            
        except Exception as e:
            error_msg = f"获取系统信息失败: {str(e)}"
            ChineseMessageBox.show_error(self, "错误", error_msg)
    
    def closeEvent(self, event):
        """关闭事件 - 优化关闭响应速度"""
        # 立即接受关闭事件，避免延迟
        event.accept()
        
        # 异步执行清理操作，不阻塞关闭
        QTimer.singleShot(0, self._async_cleanup)
    
    def _async_cleanup(self):
        """异步清理资源"""
        try:
            self.stop_monitoring()
        except Exception as e:
            print(f"清理资源时出错: {e}")

# 保持向后兼容性
DebugWindow = SafeDebugWindow

# =============================================================================
# 全局异常处理 - 保持不变
# =============================================================================

def setup_global_exception_handler():
    """设置全局异常处理器"""
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """全局异常处理函数"""
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        
        try:
            debug_logger = SafeDebugLogger()
            debug_logger.log_error("未处理的异常", exc_info=(exc_type, exc_value, exc_traceback))
        except:
            print("全局异常处理错误:", file=sys.stderr)
            print(error_msg, file=sys.stderr)
        
        try:
            from PyQt6.QtWidgets import QApplication
            app = QApplication.instance()
            if app and hasattr(app, 'activeWindow'):
                ChineseMessageBox.show_error(
                    app.activeWindow(), 
                    "程序异常", 
                    f"程序发生未处理的异常:\n\n{exc_type.__name__}: {exc_value}\n\n详细信息已记录到日志文件。"
                )
        except:
            pass
    
    sys.excepthook = global_exception_handler

# 初始化全局调试记录器
_global_debug_logger = None

def get_global_debug_logger():
    """获取全局调试记录器"""
    global _global_debug_logger
    if _global_debug_logger is None:
        _global_debug_logger = SafeDebugLogger()
    return _global_debug_logger

def initialize_global_logging():
    """初始化全局日志记录"""
    global _global_debug_logger
    _global_debug_logger = SafeDebugLogger()
    return _global_debug_logger
