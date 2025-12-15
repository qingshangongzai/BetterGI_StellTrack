# main.py
# 导入必要的标准库模块
import sys
import os
import time
import threading
import json
import re

# PyQt6 核心组件导入
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QFont


# 导入版本管理器
from version import version_manager


# Windows平台特定功能
if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes

    class VS_FIXEDFILEINFO(ctypes.Structure):
        """Windows版本信息结构
        
        用于获取和处理Windows可执行文件的版本信息。
        对应Windows API中的VS_FIXEDFILEINFO结构。
        """
        _fields_ = [
            ('dwSignature', wintypes.DWORD),
            ('dwStrucVersion', wintypes.DWORD),
            ('dwFileVersionMS', wintypes.DWORD),
            ('dwFileVersionLS', wintypes.DWORD),
            ('dwProductVersionMS', wintypes.DWORD),
            ('dwProductVersionLS', wintypes.DWORD),
            ('dwFileFlagsMask', wintypes.DWORD),
            ('dwFileFlags', wintypes.DWORD),
            ('dwFileOS', wintypes.DWORD),
            ('dwFileType', wintypes.DWORD),
            ('dwFileSubtype', wintypes.DWORD),
            ('dwFileDateMS', wintypes.DWORD),
            ('dwFileDateLS', wintypes.DWORD),
        ]

    def set_version_info():
        """
        设置Windows EXE文件的版本信息
        
        从版本管理器获取信息并构建版本信息结构，
        为Windows平台上的应用程序提供完整的版本元数据。
        """
        try:
            # 从版本管理器获取信息
            app_info = version_manager.get_app_info()
            version_info = version_manager.get_version_info()
            file_version_info = version_manager.get_file_version_info()
            
            # 构建版本信息结构
            version_info_struct = VS_FIXEDFILEINFO()
            version_info_struct.dwSignature = 0xFEEF04BD
            version_info_struct.dwStrucVersion = 0x00010000
            version_info_struct.dwFileVersionMS = file_version_info["file_version_ms"]
            version_info_struct.dwFileVersionLS = file_version_info["file_version_ls"]
            version_info_struct.dwProductVersionMS = file_version_info["product_version_ms"]
            version_info_struct.dwProductVersionLS = file_version_info["product_version_ls"]
            version_info_struct.dwFileFlagsMask = 0x3F
            version_info_struct.dwFileFlags = 0x0
            version_info_struct.dwFileOS = 0x00040004  # NT平台
            version_info_struct.dwFileType = 0x00000001  # 应用程序类型
            version_info_struct.dwFileSubtype = 0x00000000
            version_info_struct.dwFileDateMS = 0
            version_info_struct.dwFileDateLS = 0
            
            # 定义字符串资源信息
            string_info = {
                'CompanyName': app_info["company"],
                'FileDescription': app_info["description"],
                'FileVersion': version_info["full"],
                'InternalName': app_info["internal_name"],
                'LegalCopyright': app_info["copyright"],
                'OriginalFilename': app_info["original_filename"],
                'ProductName': app_info["name"],
                'ProductVersion': version_info["full"],
                'Comments': '基于Python语言开发的专用软件，主要为BetterGI提供键鼠脚本生成功能',
                'LegalTrademarks': 'BetterGI 是 HXiaoStudio 的商标',
                'PrivateBuild': '正式版本',
                'SpecialBuild': '包含调试功能的版本'
            }
            
            # 语言代码设置
            language_id = 0x0804  # 中文（简体）
            charset_id = 0x04B0  # Unicode UTF-16
            
            print(f"[DEBUG] 版本信息已设置（中文简体）: {string_info['FileDescription']}")
            print(f"[DEBUG] 语言代码: {language_id:#x}, 字符集代码: {charset_id:#x}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 设置版本信息失败: {e}")
            return False


def setup_exe_environment():
    """
    配置执行环境路径
    
    处理不同执行环境下的路径问题，特别是PyInstaller单文件模式，
    确保应用程序能够正确找到资源文件和模块，支持在各种环境中一致运行。
    
    Returns:
        str: 应用程序的基础路径
    """
    # 导入utils模块，获取基础路径
    from utils import get_base_path
    
    # 确定基础路径 - 使用utils.py中的get_base_path()函数
    base_path = get_base_path()
    
    # 确保基础路径在sys.path中
    if base_path not in sys.path:
        sys.path.insert(0, base_path)
    
    # Windows平台特定初始化
    if sys.platform == 'win32':
        print("[DEBUG] 设置Windows版本信息")
        set_version_info()
    
    # 设置工作目录为基础路径，确保相对路径引用正确
    try:
        os.chdir(base_path)
        print(f"[DEBUG] 已切换工作目录到: {base_path}")
    except Exception as e:
        print(f"[DEBUG] 切换工作目录时出错: {e}")
    
    return base_path


# 初始化环境 - 在导入其他模块前执行
base_path = setup_exe_environment()

class ApplicationMonitor(QObject):
    """
    应用程序状态监控器
    
    负责定期监控应用程序的运行状态，收集系统资源使用情况，并通过信号通知UI更新。
    主要功能包括监控内存使用、CPU使用率、运行时间等关键指标。
    
    Signals:
        status_updated (dict): 当应用程序状态更新时发出，包含完整的状态信息
    """
    
    status_updated = pyqtSignal(dict)
    
    def __init__(self):
        """
        初始化应用程序监控器
        
        设置监控初始状态、计数器和启动时间
        """
        super().__init__()
        
        # 监控控制标志
        self.monitoring = False
        
        # 状态计数器
        self.start_time = time.time()
        self.error_count = 0
        self.warning_count = 0
        self.info_count = 0
        
        # 资源使用情况
        self.memory_usage = 0
        self.cpu_usage = 0
        
        # 监控线程
        self.monitor_thread = None
    
    def start_monitoring(self):
        """
        启动监控线程，开始定期收集应用程序状态信息
        
        如果监控线程不存在或未运行，则创建并启动新的监控线程
        """
        if not self.monitor_thread or not self.monitor_thread.is_alive():
            self.monitoring = True
            self.monitor_thread = threading.Thread(
                target=self._monitor_loop,
                daemon=True,
                name="ApplicationMonitorThread"
            )
            self.monitor_thread.start()
            print("[DEBUG] 应用程序监控已启动")
    
    def stop_monitoring(self):
        """
        停止监控线程，不再收集状态信息
        
        设置监控标志为False并等待线程结束（最多等待2秒）
        """
        self.monitoring = False
        if self.monitor_thread and self.monitor_thread.is_alive():
            print("[DEBUG] 正在停止应用程序监控...")
            # 等待线程结束（最多等待2秒）
            self.monitor_thread.join(timeout=2.0)
            print("[DEBUG] 应用程序监控已停止")
    
    def _monitor_loop(self):
        """
        监控主循环，定期收集并发送状态信息
        
        在循环中获取应用程序状态并通过信号发送，
        捕获并处理可能出现的异常，避免监控线程意外终止
        """
        while self.monitoring:
            try:
                status = self.get_application_status()
                self.status_updated.emit(status)
                time.sleep(5)  # 每5秒更新一次
            except Exception as e:
                print(f"[DEBUG] 监控循环错误: {e}")
                time.sleep(10)  # 出错时增加等待时间以避免过度消耗资源
    
    def get_application_status(self):
        """
        获取应用程序当前状态信息
        
        计算运行时间，尝试获取系统资源使用情况，并整合为完整的状态信息
        
        Returns:
            dict: 包含应用程序状态信息的字典
        """
        # 计算运行时间
        uptime = time.time() - self.start_time
        hours, remainder = divmod(uptime, 3600)
        minutes, seconds = divmod(remainder, 60)
        uptime_str = f"{int(hours)}h {int(minutes)}m {int(seconds)}s"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # 基础状态信息（无论psutil是否可用）
        base_status = {
            'uptime': uptime_str,
            'memory_usage': 'N/A',
            'cpu_usage': 'N/A',
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'timestamp': timestamp
        }
        
        # 尝试使用psutil获取详细系统信息
        try:
            import psutil
            import platform
            
            # 获取进程资源使用情况
            process = psutil.Process()
            memory_info = process.memory_info()
            self.memory_usage = memory_info.rss / 1024 / 1024  # 转换为MB
            self.cpu_usage = process.cpu_percent()
            
            # 收集系统信息
            system_info = {
                'platform': f"{platform.system()} {platform.release()}",
                'python_version': platform.python_version(),
                'processor': platform.processor()
            }
            
            # 更新状态信息
            base_status.update({
                'memory_usage': f"{self.memory_usage:.1f} MB",
                'cpu_usage': f"{self.cpu_usage:.1f}%",
                'system_info': system_info
            })
            
        except ImportError:
            # psutil不可用时，设置基本系统信息
            base_status['system_info'] = {
                'platform': 'Unknown',
                'python_version': 'Unknown',
                'processor': 'Unknown'
            }
            
        return base_status
    
    def increment_error_count(self):
        """
        增加错误计数器，用于追踪应用程序错误数量
        """
        self.error_count += 1
    
    def increment_warning_count(self):
        """
        增加警告计数器，用于追踪应用程序警告数量
        """
        self.warning_count += 1
    
    def increment_info_count(self):
        """
        增加信息计数器，用于追踪应用程序信息日志数量
        """
        self.info_count += 1

# =============================================================================
# 增强的应用程序类 - 使用版本管理器
# =============================================================================

class BetterGIApplication:
    """
    BetterGI 应用程序主类
    
    负责管理应用程序的完整生命周期，包括初始化、配置加载、主窗口创建和资源管理。
    作为应用程序的核心控制器，协调各组件间的交互并提供统一的错误处理机制。
    
    主要职责：
    1. 初始化应用程序环境和配置
    2. 设置Qt应用程序和全局样式
    3. 配置平台特定功能
    4. 初始化日志系统
    5. 检查用户协议
    6. 创建和显示主窗口
    7. 运行应用程序主循环
    8. 管理应用程序资源的清理
    
    应用程序启动流程：
    - 初始化应用程序环境
    - 设置Qt应用程序
    - 配置平台特定功能
    - 设置全局样式
    - 初始化日志系统
    - 检查用户协议
    - 创建主窗口
    - 显示主窗口
    - 进入应用程序主循环
    
    应用程序退出流程：
    - 退出主循环
    - 清理应用程序资源
    - 停止监控器
    - 恢复输出流
    """
    
    def __init__(self):
        """
        初始化应用程序实例
        
        创建应用程序所需的核心组件引用和初始状态变量
        记录应用程序启动时间点，用于后续计算启动耗时
        """
        # 应用程序核心组件
        self.app = None             # PyQt应用程序实例
        self.main_window = None     # 主窗口实例
        self.debug_logger = None    # 调试日志记录器
        self.monitor = None         # 应用程序监控器
        
        # 启动计时
        self.startup_time = time.time()
        
    def initialize(self):
        """
        初始化应用程序环境和核心组件
        
        按照预定顺序初始化应用程序的各个组件，包括：
        - 配置高DPI显示支持
        - 创建和配置QApplication实例
        - 设置应用程序样式和字体
        - 初始化日志系统和异常处理器
        - 设置平台特定功能
        - 初始化应用监控器
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            print("[DEBUG] 开始初始化应用程序")
            
            # 配置Qt应用程序基础设置
            if not self._initialize_qt_application():
                return False
            
            # 设置应用程序样式
            self._setup_global_style()
            
            # 平台特定设置
            self._setup_platform_specific_features()
            
            # 初始化日志系统
            if not self._initialize_logging():
                return False
            
            # 设置异常处理器
            if not self._setup_exception_handler():
                return False
            
            # 初始化应用监控器
            self._initialize_monitor()
            
            # 记录启动信息
            version = version_manager.get_version()
            self._log_startup_info(version)
            
            print("[DEBUG] 应用程序初始化完成")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 应用程序初始化失败: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def _initialize_qt_application(self):
        """
        初始化Qt应用程序实例和基本配置
        
        设置高DPI支持、创建QApplication实例、配置应用程序信息和字体
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        try:
            # 配置高DPI显示支持
            QApplication.setHighDpiScaleFactorRoundingPolicy(
                Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
            )
            
            # 创建QApplication实例
            self.app = QApplication(sys.argv)
            
            # 设置应用程序字体 - 使用SourceHanSerifCN确保中文显示正常
            from styles import get_global_font_manager
            font_manager = get_global_font_manager()
            font = font_manager.get_source_han_font(9)
            self.app.setFont(font)
            
            # 使用版本管理器获取并设置应用程序信息
            app_info = version_manager.get_app_info()
            version = version_manager.get_version()
            
            self.app.setApplicationName(app_info["name"])
            self.app.setApplicationVersion(version)
            self.app.setOrganizationName(app_info["company"])
            
            print(f"[DEBUG] 应用程序信息已设置: {app_info['name']} v{version}")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 初始化Qt应用程序失败: {e}")
            return False
            
    def _setup_platform_specific_features(self):
        """
        设置平台特定功能
        
        根据不同操作系统平台设置相应的功能，如Windows的AppUserModelID等
        """
        if os.name == 'nt':
            self._setup_windows_specific_features()
    
    def _setup_global_style(self):
        """
        设置应用程序全局样式表和样式属性
        
        使用styles模块中的UnifiedStyleHelper来统一管理应用程序样式
        """
        try:
            # 使用全局样式管理器的setup_global_style方法
            from styles import UnifiedStyleHelper
            UnifiedStyleHelper.get_instance().setup_global_style(self)
            print("[DEBUG] 全局样式已应用")
            
        except Exception as e:
            print(f"[DEBUG] 设置全局样式失败: {e}")
            import traceback
            traceback.print_exc()
    
    def _setup_windows_specific_features(self):
        """
        设置Windows平台特定功能
        
        包括AppUserModelID设置等Windows专属功能
        """
        if os.name == 'nt':
            print("[DEBUG] 设置AppUserModelID")
            try:
                from utils import set_app_user_model_id
                set_app_user_model_id()
                print("[DEBUG] AppUserModelID设置成功")
            except Exception as e:
                print(f"[DEBUG] AppUserModelID设置失败: {e}")
    
    def _initialize_logging(self):
        """
        初始化应用程序全局日志记录系统
        
        导入debug_tools模块并调用initialize_global_logging函数设置日志系统，
        确保应用程序能够记录运行时信息、警告和错误，方便调试和问题排查。
        
        Returns:
            bool: 初始化成功返回True，失败返回False
        """
        print("[DEBUG] 初始化全局日志记录")
        try:
            from debug_tools import initialize_global_logging
            self.debug_logger = initialize_global_logging()
            print("[DEBUG] 全局日志记录初始化成功")
            return True
        except ImportError as e:
            print(f"[DEBUG] 导入debug_tools模块失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"[DEBUG] 初始化全局日志系统失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _setup_exception_handler(self):
        """
        设置全局异常处理器
        
        捕获未处理的异常并记录到日志中，防止应用程序因未捕获异常而意外崩溃
        提供详细的错误信息记录，便于问题排查
        
        Returns:
            bool: 设置成功返回True，失败返回False
        """
        print("[DEBUG] 设置全局异常处理器")
        try:
            def handle_exception(exc_type, exc_value, exc_traceback):
                """处理未捕获的异常的回调函数"""
                # 忽略KeyboardInterrupt，让程序正常退出
                if issubclass(exc_type, KeyboardInterrupt):
                    sys.__excepthook__(exc_type, exc_value, exc_traceback)
                    return
                    
                # 构建异常错误信息
                error_msg = "未捕获的异常: {0}: {1}".format(
                    exc_type.__name__, str(exc_value)
                )
                
                # 使用日志记录器记录异常信息
                if self.debug_logger:
                    self.debug_logger.log_error(error_msg, exc_info=(exc_type, exc_value, exc_traceback))
                else:
                    print(f"[ERROR] {error_msg}")
                    import traceback
                    traceback.print_tb(exc_traceback)
                    
            # 设置全局异常钩子
            sys.excepthook = handle_exception
            print("[DEBUG] 全局异常处理器已设置")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 设置全局异常处理器失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _initialize_monitor(self):
        """
        初始化应用程序监控器
        
        创建并启动应用程序性能和状态监控器，用于收集和跟踪应用程序运行状态
        监控器将在独立线程中运行，定期收集应用程序性能和使用情况数据
        连接监控器的状态更新信号到应用程序的状态更新处理函数
        """
        print("[DEBUG] 初始化应用程序监控器")
        try:
            # 创建并启动监控器实例
            self.monitor = ApplicationMonitor()
            self.monitor.status_updated.connect(self.on_status_updated)
            self.monitor.start_monitoring()
            print("[DEBUG] 应用程序监控器已启动")
        except Exception as e:
            print(f"[DEBUG] 初始化应用监控器失败: {e}")
            import traceback
            traceback.print_exc()
            # 监控器初始化失败不影响主程序运行
    
    def _log_startup_info(self, version):
        """
        记录应用程序启动信息到日志系统
        
        Args:
            version (str): 应用程序版本号
        """
        if self.debug_logger:
            self.debug_logger.log_info("BetterGI 星轨应用程序启动")
            self.debug_logger.log_info(f"版本: {version}")
            self.debug_logger.log_system_info()
    
    def check_user_agreement(self):
        """
        检查用户是否已同意软件使用协议
        
        验证用户是否已经接受了应用程序的许可协议，
        调用外部模块检查用户协议状态，优化异常处理和日志记录
        
        Returns:
            bool: 用户同意协议返回True，拒绝或取消返回False；出现异常时默认返回True
        """
        try:
            print("[DEBUG] 开始检查用户协议")
            
            # 导入协议检查模块
            from user_agreement import check_user_agreement
            
            # 执行协议检查
            if not check_user_agreement():
                print("[DEBUG] 用户不同意协议，退出程序")
                return False
            
            print("[DEBUG] 用户协议检查通过")
            return True
            
        except ImportError as e:
            print(f"[DEBUG] 导入用户协议模块失败: {e}")
            import traceback
            traceback.print_exc()
            # 导入失败时默认允许继续使用
            return True
            
        except Exception as e:
            print(f"[DEBUG] 检查用户协议时发生错误: {e}")
            import traceback
            traceback.print_exc()
            # 其他异常时默认允许继续使用
            return True
    
    def create_main_window(self):
        """
        创建应用程序主窗口
        
        导入MainWindow类并创建其实例，这是应用程序用户界面的核心组件
        确保在创建主窗口前所有必要的资源和配置都已准备就绪
        
        Returns:
            bool: 创建成功返回True，失败返回False
        """
        try:
            print("[DEBUG] 创建主窗口")
            from main_window import MainWindow
            self.main_window = MainWindow()
            
            # 连接主窗口信号到监控器
            if hasattr(self.main_window, 'status_bar'):
                # 可以在这里添加状态栏更新等连接
                pass
                
            print("[DEBUG] 主窗口创建完成")
            return True
            
        except ImportError as e:
            print(f"[DEBUG] 导入主窗口模块失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        except Exception as e:
            print(f"[DEBUG] 创建主窗口失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def show_main_window(self):
        """
        显示应用程序主窗口
        
        调用主窗口的show方法，将用户界面呈现给用户
        计算并显示应用程序启动总耗时，用于性能监控和调试
        修复任务栏图标问题并完善异常处理机制
        
        Returns:
            bool: 显示成功返回True，失败返回False
        """
        try:
            print("[DEBUG] 显示主窗口")
            if self.main_window:
                self.main_window.show()
                
                # 修复任务栏图标问题
                QTimer.singleShot(100, self.main_window.fix_taskbar_icon)
                
                # 计算并显示启动耗时
                startup_time = time.time() - self.startup_time
                print(f"[DEBUG] 应用程序启动耗时: {startup_time:.2f} 秒")
                
                # 记录窗口显示事件和启动耗时
                if self.debug_logger:
                    self.debug_logger.log_info("主窗口已显示")
                    self.debug_logger.log_info(f"应用程序启动完成，总耗时: {startup_time:.2f} 秒")
            
            print("[DEBUG] 主窗口显示完成")
            return True
            
        except Exception as e:
            print(f"[DEBUG] 显示主窗口失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 记录错误到日志
            if self.debug_logger:
                self.debug_logger.log_error(f"显示主窗口失败: {e}", exc_info=True)
            
            return False
    
    def run(self):
        """
        运行应用程序主流程
        
        按照预定顺序执行应用程序的各个阶段：
        1. 初始化应用程序环境
        2. 检查用户协议
        3. 创建主窗口
        4. 显示主窗口
        5. 运行应用程序事件循环
        6. 清理资源
        
        Returns:
            int: 应用程序退出代码，0表示正常退出，非0表示异常退出
        """
        try:
            print("[DEBUG] 开始运行应用程序主流程")
            
            # 初始化应用程序
            if not self.initialize():
                print("[DEBUG] 应用程序初始化失败，退出")
                return 1
            
            # 检查用户协议
            if not self.check_user_agreement():
                print("[DEBUG] 用户协议检查失败，退出")
                return 0
            
            # 创建主窗口
            if not self.create_main_window():
                print("[DEBUG] 主窗口创建失败，退出")
                return 1
            
            # 显示主窗口
            if not self.show_main_window():
                print("[DEBUG] 主窗口显示失败，退出")
                return 1
            
            # 记录启动完成并计算启动时间
            startup_time = time.time() - self.startup_time
            if self.debug_logger:
                self.debug_logger.log_info(f"应用程序启动完成，耗时 {startup_time:.2f} 秒")
            
            # 运行应用程序主循环
            print("[DEBUG] 进入应用程序主循环")
            return_code = self.app.exec()
            
            # 记录退出信息
            if self.debug_logger:
                self.debug_logger.log_info(f"应用程序退出，返回码: {return_code}")
            
            return return_code
            
        except Exception as e:
            print(f"[DEBUG] 运行应用程序时出错: {e}")
            import traceback
            traceback.print_exc()
            
            # 记录错误信息
            if self.debug_logger:
                self.debug_logger.log_error("应用程序运行失败", exc_info=True)
            
            # 发生异常时也尝试清理资源
            self.cleanup()
            return 1
    
    def on_status_updated(self, status):
        """
        处理应用程序状态更新事件
        
        接收监控器发送的状态信息，可用于更新UI或执行其他操作
        
        Args:
            status (dict): 包含应用程序状态信息的字典
        """
        try:
            # 更新UI元素（如状态栏）
            if self.main_window and hasattr(self.main_window, 'status_bar'):
                # 示例：在状态栏显示内存使用情况
                memory_text = f"内存: {status['memory_usage']}" if status['memory_usage'] != 'N/A' else "内存: N/A"
                # 这里可以添加状态栏更新逻辑
                pass
                
            # 可以添加定时记录状态信息的逻辑（避免过于频繁）
            # if int(time.time()) % 30 == 0:  # 每30秒记录一次
            #     self.debug_logger.log_debug(f"应用程序状态: {status}")
                
        except Exception as e:
            print(f"处理状态更新时出错: {e}")
    
    def cleanup(self):
        """
        清理应用程序资源
        
        释放应用程序运行过程中使用的所有资源，确保正确关闭：
        1. 停止应用程序监控器
        2. 恢复输出流并记录清理信息
        3. 确保所有资源正确释放
        
        即使在发生异常的情况下也尝试进行资源清理，防止资源泄漏
        """
        try:
            print("[DEBUG] 开始清理应用程序资源")
            
            # 停止监控器
            if self.monitor:
                self.monitor.stop_monitoring()
                print("[DEBUG] 监控器已停止")
            
            # 恢复输出流
            if self.debug_logger:
                self.debug_logger.restore_output()
                self.debug_logger.log_info("应用程序资源清理完成")
            
            print("[DEBUG] 应用程序资源清理完成")
            
        except Exception as e:
            print(f"[DEBUG] 清理应用程序资源时发生错误: {e}")
            import traceback
            traceback.print_exc()

# =============================================================================
# 导入版本获取工具函数
# =============================================================================
from utils import get_current_version

# =============================================================================
# 主函数
# =============================================================================

def main():
    """
    应用程序入口函数
    
    初始化并运行BetterGI应用程序，处理整个应用程序的生命周期。
    """
    print("[DEBUG] 开始启动 BetterGI 星轨")
    print(f"[DEBUG] 当前版本: {get_current_version()}")
    
    # 创建并运行应用程序
    app = BetterGIApplication()
    
    try:
        return_code = app.run()
    finally:
        # 确保无论是否发生异常都会执行清理操作
        app.cleanup()
    
    return return_code

# 应用程序入口点
if __name__ == "__main__":
    sys.exit(main())
