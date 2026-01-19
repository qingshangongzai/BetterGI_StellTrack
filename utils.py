# utils.py - 通用工具和资源管理模块
"""
通用工具和资源管理模块，包含全局常量、映射和辅助函数。
"""

# 标准库模块导入
import sys
import os
import ctypes
from datetime import datetime

# 第三方模块导入
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap, QColor, QPainter

# 项目模块导入
from version import version_manager

# =============================================================================
# 全局常量和映射
# =============================================================================

# Windows API 常量
DWMWA_USE_IMMERSIVE_DARK_MODE = 20  # Windows DWM API 沉浸式深色模式标志

# 资源相关常量
RESOURCE_DIRS = ["assets", "fonts", "file", "logo"]  # 资源目录列表
ICON_FILES = ["logo.ico", "logo.png"]  # 图标文件列表
LOGO_FILE = "logo.png"  # Logo文件名

# 应用程序信息常量
APP_NAME = "BetterGI StellTrack"  # 应用程序名称
SCRIPT_DEFAULT_DIR = r"C:\Program Files\BetterGI\User\KeyMouseScript"  # 脚本默认目录

# 虚拟键码到按键名称的映射（Windows虚拟键码）
VK_MAPPING = {
    0x08: "Backspace", 0x09: "Tab", 0x0D: "Enter", 0x10: "Shift", 0x11: "Ctrl", 0x12: "Alt",
    0x13: "Pause", 0x14: "Caps Lock", 0x1B: "Esc", 0x20: "Space", 0x21: "Page Up",
    0x22: "Page Down", 0x23: "End", 0x24: "Home", 0x25: "Left", 0x26: "Up",
    0x27: "Right", 0x28: "Down", 0x2C: "Print Screen", 0x2D: "Insert", 0x2E: "Delete",
    0x30: "0", 0x31: "1", 0x32: "2", 0x33: "3", 0x34: "4", 0x35: "5", 0x36: "6", 0x37: "7", 0x38: "8", 0x39: "9",
    0x41: "A", 0x42: "B", 0x43: "C", 0x44: "D", 0x45: "E", 0x46: "F", 0x47: "G", 0x48: "H", 0x49: "I", 0x4A: "J",
    0x4B: "K", 0x4C: "L", 0x4D: "M", 0x4E: "N", 0x4F: "O", 0x50: "P", 0x51: "Q", 0x52: "R", 0x53: "S", 0x54: "T",
    0x55: "U", 0x56: "V", 0x57: "W", 0x58: "X", 0x59: "Y", 0x5A: "Z",
    0x5B: "Left Win", 0x5C: "Right Win", 0x5D: "Menu", 0x60: "Num 0", 0x61: "Num 1", 0x62: "Num 2",
    0x63: "Num 3", 0x64: "Num 4", 0x65: "Num 5", 0x66: "Num 6", 0x67: "Num 7",
    0x68: "Num 8", 0x69: "Num 9", 0x6A: "Num *", 0x6B: "Num +", 0x6D: "Num -", 0x6E: "Num .",
    0x6F: "Num /", 0x70: "F1", 0x71: "F2", 0x72: "F3", 0x73: "F4", 0x74: "F5", 0x75: "F6", 0x76: "F7", 0x77: "F8",
    0x78: "F9", 0x79: "F10", 0x7A: "F11", 0x7B: "F12",
    0x90: "Num Lock", 0x91: "Scroll Lock", 0xBA: ";", 0xBB: "=", 0xBC: ",", 0xBD: "-", 0xBE: ".",
    0xBF: "/", 0xC0: "`", 0xDB: "[", 0xDC: "\\", 0xDD: "]", 0xDE: "'",
    0xA2: "Ctrl",  # 左Ctrl键
    0xA3: "Ctrl"   # 右Ctrl键
}

# 中文按键名称映射
KEY_NAME_MAPPING = {
    "Backspace": "退格", "Tab": "Tab", "Enter": "回车", "Shift": "Shift", "Ctrl": "Ctrl", "Alt": "Alt",
    "Pause": "暂停", "Caps Lock": "大写锁定", "Esc": "ESC", "Space": "空格", "Page Up": "Page Up",
    "Page Down": "Page Down", "End": "End", "Home": "Home", "Left": "左箭头", "Up": "上箭头",
    "Right": "右箭头", "Down": "下箭头", "Print Screen": "Print Screen", "Insert": "Insert", "Delete": "Delete",
    "0": "0", "1": "1", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9",
    "A": "A", "B": "B", "C": "C", "D": "D", "E": "E", "F": "F", "G": "G", "H": "H", "I": "I", "J": "J",
    "K": "K", "L": "L", "M": "M", "N": "N", "O": "O", "P": "P", "Q": "Q", "R": "R", "S": "S", "T": "T",
    "U": "U", "V": "V", "W": "W", "X": "X", "Y": "Y", "Z": "Z",
    "Left Win": "左Win", "Right Win": "右Win", "Menu": "菜单键", "Num 0": "小键盘0", "Num 1": "小键盘1", "Num 2": "小键盘2",
    "Num 3": "小键盘3", "Num 4": "小键盘4", "Num 5": "小键盘5", "Num 6": "小键盘6", "Num 7": "小键盘7",
    "Num 8": "小键盘8", "Num 9": "小键盘9", "Num *": "小键盘*", "Num +": "小键盘+", "Num -": "小键盘-", "Num .": "小键盘.",
    "Num /": "小键盘/", "F1": "F1", "F2": "F2", "F3": "F3", "F4": "F4", "F5": "F5", "F6": "F6", "F7": "F7", "F8": "F8",
    "F9": "F9", "F10": "F10", "F11": "F11", "F12": "F12",
    "Num Lock": "Num Lock", "Scroll Lock": "Scroll Lock", ";": ";", "=": "=", ",": ",", "-": "-", ".": ".",
    "/": "/", "`": "`", "[": "[", "\\": "\\", "]": "]", "'": "'"
}

# 合并的按键映射表: 虚拟键码 -> 中文名称
_COMBINED_KEY_MAPPING = {
    vk: KEY_NAME_MAPPING.get(name, name)
    for vk, name in VK_MAPPING.items()
}

# 事件类型映射
EVENT_TYPE_MAP = {
    "按键按下": 0,
    "按键释放": 1,
    "指针移动": 2,
    "平行移动": 3,
    "左键按下": 4,
    "左键释放": 5,
    "右键按下": 4,
    "右键释放": 5,
    "中键按下": 4,
    "中键释放": 5,
    "鼠标滚轮": 6
}

# 排序提示文本
SORT_TIP_TEXT = "💡 提示：为避免计算出现异常，若添加事件、编辑事件、粘贴事件后相对时间出现负数，请点击'事件排序'"

# =============================================================================
# 事件类型转换和按键名称生成函数
# =============================================================================

def convert_event_type_num_to_str_with_button(type_num, mouse_button=None):
    """将数字事件类型转换为字符串，考虑鼠标按钮
    
    Args:
        type_num: 事件类型数字
        mouse_button: 鼠标按钮（"Left"、"Right" 或 "Middle"）
        
    Returns:
        str: 事件类型字符串
    """
    # 处理滚轮事件
    if type_num == 6:
        return "鼠标滚轮"
    
    if mouse_button:
        if type_num == 4:  # 按下
            if mouse_button == "Right":
                return "右键按下"
            elif mouse_button == "Left":
                return "左键按下"
            elif mouse_button == "Middle":
                return "中键按下"
            else:
                return "左键按下"  # 默认左键
        elif type_num == 5:  # 释放
            if mouse_button == "Right":
                return "右键释放"
            elif mouse_button == "Left":
                return "左键释放"
            elif mouse_button == "Middle":
                return "中键释放"
            else:
                return "左键释放"  # 默认左键
    
    # 如果没有mouse_button信息，使用原有映射
    type_mapping = {
        0: "按键按下",
        1: "按键释放", 
        2: "指针移动",
        3: "平行移动",
        4: "左键按下",   # 默认左键
        5: "左键释放",   # 默认左键
        6: "鼠标滚轮"    # 滚轮事件
    }
    return type_mapping.get(type_num, "未知事件")

def convert_event_type_num_to_str(type_num):
    """将数字事件类型转换为字符串
    
    Args:
        type_num: 事件类型数字
        
    Returns:
        str: 事件类型字符串
    """
    # 直接调用现有的函数，不提供mouse_button参数
    return convert_event_type_num_to_str_with_button(type_num)

def convert_event_type_str_to_num(type_str):
    """将字符串事件类型转换为数字
    
    Args:
        type_str: 事件类型字符串
        
    Returns:
        int: 事件类型数字
    """
    return EVENT_TYPE_MAP.get(type_str, 0)

def generate_key_event_name(event_type_str, keycode):
    """根据事件类型和键码生成事件名称

    Args:
        event_type_str: 事件类型字符串
        keycode: 键码

    Returns:
        str: 生成的事件名称
    """
    if event_type_str in ["按键按下", "按键释放"] and keycode:
        try:
            keycode_int = int(keycode)
            key_name_cn = _COMBINED_KEY_MAPPING.get(keycode_int, keycode)

            action = "按下" if event_type_str == "按键按下" else "释放"
            return f"{action}{key_name_cn}"
        except (ValueError, TypeError):
            return event_type_str
    elif event_type_str in ["左键按下", "左键释放", "右键按下", "右键释放", "中键按下", "中键释放", "指针移动", "平行移动", "鼠标滚轮"]:
        return event_type_str
    else:
        return event_type_str

def get_key_chinese_name(keycode):
    """获取按键的中文名称

    Args:
        keycode: 键码

    Returns:
        str: 按键的中文名称
    """
    if not keycode:
        return "未知"

    try:
        keycode_int = int(keycode)
        return _COMBINED_KEY_MAPPING.get(keycode_int, keycode)
    except (ValueError, TypeError):
        return keycode

def get_event_data_from_table(table, row, skip_row_number=True):
    """从表格中获取事件数据
    
    Args:
        table: 事件表格对象
        row: 行索引
        skip_row_number: 是否跳过行号列（默认True）
        
    Returns:
        list: 事件数据列表
    """
    event_data = []
    start_col = 1 if skip_row_number else 0
    end_col = 8  # 共8列，包括行号列
    
    for col in range(start_col, end_col):
        item = table.item(row, col)
        if item:
            event_data.append(item.text())
        else:
            event_data.append("")
    
    return event_data

def get_multiple_event_data_from_table(table, rows, skip_row_number=True):
    """批量获取多行事件数据
    
    Args:
        table: 事件表格对象
        rows: 行索引列表
        skip_row_number: 是否跳过行号列（默认True）
        
    Returns:
        list: 多行事件数据列表
    """
    start_col = 1 if skip_row_number else 0
    end_col = 8
    
    all_data = []
    for row in rows:
        event_data = []
        for col in range(start_col, end_col):
            item = table.item(row, col)
            event_data.append(item.text() if item else "")
        all_data.append(event_data)
    
    return all_data

def handle_errors(logger=None, error_title="错误", error_message="操作失败"):
    """错误处理装饰器，用于统一处理函数中的异常

    Args:
        logger: 日志记录器对象
        error_title: 错误对话框标题
        error_message: 错误对话框默认消息

    Returns:
        decorator: 装饰器函数

    Note:
        如果未提供logger，则使用print输出
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                # 构造完整的错误消息
                full_error_message = f"{error_message}: {str(e)}"

                # 记录错误日志
                if logger:
                    logger.log_error(full_error_message, exc_info=True)
                else:
                    print(f"[ERROR] {full_error_message}")

                # 显示错误消息给用户
                # 注意：这里需要从args中获取主窗口对象，或者使用其他方式获取
                # 这里简化处理，假设第一个参数是self，且self.main_window是主窗口对象
                if args and hasattr(args[0], 'main_window'):
                    from styles import ChineseMessageBox
                    ChineseMessageBox.show_error(args[0].main_window, error_title, full_error_message)

                return None
        return wrapper
    return decorator

class BatchOperation:
    """批量操作上下文管理器，用于统一处理批量操作的开始和结束逻辑

    典型用法：
    with BatchOperation(main_window):
        # 执行批量操作
        pass
    """
    
    def __init__(self, main_window, save_to_undo_stack=True):
        """初始化批量操作上下文管理器

        Args:
            main_window: 主窗口对象
            save_to_undo_stack: 是否保存当前状态到撤销栈（默认True）
        """
        self.main_window = main_window
        self.save_to_undo_stack = save_to_undo_stack
    
    def __enter__(self):
        """进入上下文，开始批量操作
        
        Returns:
            None
        """
        # 保存当前状态到撤销栈
        if self.save_to_undo_stack:
            self.main_window.save_state_to_undo_stack()
        
        # 设置批量操作标志为True
        self.main_window._batch_operation = True
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文，结束批量操作
        
        Args:
            exc_type: 异常类型
            exc_val: 异常值
            exc_tb: 异常回溯
            
        Returns:
            bool: 是否抑制异常
        """
        # 无论操作成功或失败，将批量操作标志设置为False
        self.main_window._batch_operation = False
        
        # 不抑制异常，让异常正常传播
        return False

def update_app_state(main_window, event_manager=None):
    """更新应用状态，包括统计信息和预计总时间
    
    Args:
        main_window: 主窗口对象
        event_manager: 事件管理器对象（可选）
        
    Returns:
        None
    """
    # 更新统计信息
    if event_manager and hasattr(event_manager, 'update_stats'):
        event_manager.update_stats()
    elif hasattr(main_window, 'stats_panel') and hasattr(main_window.stats_panel, 'update_stats'):
        main_window.stats_panel.update_stats()
    
    # 立即更新预计总时间
    if hasattr(main_window, 'settings_panel'):
        main_window.settings_panel.on_calculate_total_time()

# =============================================================================
# Windows 任务栏图标修复相关函数
# =============================================================================

# 任务栏图标修复标志 - 改为字典，为每个窗口单独跟踪
_TASKBAR_ICON_FIXED_WINDOWS = {}

def set_app_user_model_id():
    """设置AppUserModelID - 使用版本管理器

    Returns:
        bool: 设置成功返回True，失败返回False
    """
    if os.name != 'nt':
        return False

    try:
        # 使用版本管理器获取信息
        app_info = version_manager.get_app_info()
        version = version_manager.get_version()

        app_id = f'{app_info["company"]}.{app_info["name_en"]}.{version}'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
        print(f"[DEBUG] AppUserModelID设置成功: {app_id}")
        return True
    except Exception as e:
        print(f"[DEBUG] 设置AppUserModelID失败: {e}")
        return False


def fix_windows_taskbar_icon_for_window(window):
    """为特定窗口修复Windows任务栏图标

    为每个窗口单独跟踪图标修复状态，避免一个窗口的修复影响其他窗口。

    Args:
        window: PyQt6 窗口对象

    Returns:
        bool: 修复成功返回True，失败返回False

    Note:
        使用窗口对象的id作为键，为每个窗口单独跟踪修复状态
    """
    if os.name != 'nt':
        return False

    # 使用窗口对象的id作为键，为每个窗口单独跟踪修复状态
    window_id = id(window)
    global _TASKBAR_ICON_FIXED_WINDOWS

    # 检查此窗口是否已经修复过
    if window_id in _TASKBAR_ICON_FIXED_WINDOWS and _TASKBAR_ICON_FIXED_WINDOWS[window_id]:
        return False

    try:
        # 确保窗口已经显示：如果已经可见，就不要重复 show，避免位置/动画抖动
        if not window.isVisible():
            window.show()
        window.raise_()
        window.activateWindow()

        # 使用Qt方法获取窗口句柄
        hwnd = int(window.winId())

        # 查找图标文件
        icon_path = find_resource_file(ICON_FILES[0])  # logo.ico
        if not icon_path:
            icon_path = find_resource_file(ICON_FILES[1])  # logo.png

        if not icon_path:
            print("[DEBUG] 未找到图标文件用于任务栏修复")
            return False

        # 使用ctypes设置图标
        user32 = ctypes.windll.user32

        # 加载图标
        if icon_path.lower().endswith('.ico'):
            h_icon = user32.LoadImageW(
                None, icon_path,
                1,  # IMAGE_ICON
                0, 0,  # 使用实际大小
                0x00000010  # LR_LOADFROMFILE
            )
        else:
            # 对于PNG等格式，需要先加载为位图
            from PyQt6.QtGui import QPixmap
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                h_icon = pixmap.toImage().bits()
            else:
                print("[DEBUG] 无法加载PNG图标文件")
                return False

        if h_icon:
            # 设置图标
            user32.SendMessageW(hwnd, 0x0080, 1, h_icon)  # WM_SETICON, ICON_BIG
            user32.SendMessageW(hwnd, 0x0080, 0, h_icon)  # WM_SETICON, ICON_SMALL

            # 强制刷新任务栏
            user32.UpdateWindow(hwnd)

            print(f"[DEBUG] 任务栏图标修复成功: {icon_path}")

            # 标记此窗口已修复，但不影响其他窗口
            _TASKBAR_ICON_FIXED_WINDOWS[window_id] = True
            return True

        print("[DEBUG] 图标句柄创建失败")
        return False

    except Exception as e:
        print(f"[DEBUG] 修复任务栏图标失败: {e}")
        return False

# =============================================================================
# 兼容性函数
# =============================================================================

def load_icon_exe_safe():
    """兼容性函数，指向统一的图标加载函数

    Returns:
        QIcon: 应用程序图标对象
    """
    return load_icon_universal()



# =============================================================================
# 资源管理器 - 从styles.py迁移
# =============================================================================

# 资源文件搜索路径缓存
_search_paths_cache = None
_base_path_cache = None

def _build_search_paths(base_path):
    """构建资源文件搜索路径列表
    
    Args:
        base_path: 基础路径
        
    Returns:
        list: 搜索路径列表
    """
    search_paths = []
    
    # 添加基础路径及其子目录
    search_paths.append(base_path)
    for resource_dir in RESOURCE_DIRS:
        search_paths.append(os.path.join(base_path, resource_dir))
    
    # 添加 _MEIPASS 路径及其子目录（如果存在）
    if hasattr(sys, '_MEIPASS'):
        meipass = sys._MEIPASS
        if meipass not in search_paths:
            search_paths.append(meipass)
            for resource_dir in RESOURCE_DIRS:
                search_paths.append(os.path.join(meipass, resource_dir))
    
    return search_paths

def get_base_path():
    """获取程序基础路径，兼容开发环境和打包环境

    Returns:
        str: 程序基础路径

    Note:
        - 打包环境：返回 PyInstaller 临时目录或可执行文件所在目录
        - 开发环境：返回当前脚本文件所在目录
    """
    if getattr(sys, 'frozen', False):
        # 打包后的环境
        if hasattr(sys, '_MEIPASS'):
            # PyInstaller 临时目录
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(sys.executable)
    else:
        # 开发环境
        base_path = os.path.dirname(os.path.abspath(__file__))
    return base_path

def get_user_data_dir():
    """获取用户数据目录，用于保存日志和配置文件

    Returns:
        str: 用户数据目录路径

    Note:
        - Windows: C:/Users/<用户名>/AppData/Local/BetterGI StellTrack
        - Linux: ~/.local/share/BetterGI StellTrack
        - macOS: ~/Library/Application Support/BetterGI StellTrack
    """
    if sys.platform == "win32":
        # Windows使用AppData\Local目录
        appdata_dir = os.getenv("LOCALAPPDATA")
        if not appdata_dir:
            appdata_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local")
        data_dir = os.path.join(appdata_dir, APP_NAME)
    elif sys.platform == "darwin":
        # macOS使用Library/Application Support目录
        data_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", APP_NAME)
    else:
        # Linux使用~/.local/share目录
        data_dir = os.path.join(os.path.expanduser("~"), ".local", "share", APP_NAME)

    # 确保目录存在
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)

    return data_dir

def get_script_default_dir():
    r"""获取脚本默认目录，用于打开和保存脚本文件

    Returns:
        str: 脚本默认目录路径 (C:\Program Files\BetterGI\User\KeyMouseScript)

    Note:
        如果目录不存在，会自动创建
    """
    script_dir = SCRIPT_DEFAULT_DIR

    # 确保目录存在
    if not os.path.exists(script_dir):
        os.makedirs(script_dir, exist_ok=True)

    return script_dir

def get_system_theme_mode():
    """获取系统主题模式

    Returns:
        str: 系统主题模式，"light" 或 "dark"

    Note:
        - Windows: 从注册表读取主题设置
        - 其他平台: 默认返回 "light"
        - 读取失败时默认返回 "light"
    """
    try:
        if sys.platform == "win32":
            try:
                import winreg
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize",
                )
                value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
                winreg.CloseKey(key)
                return "light" if value == 1 else "dark"
            except Exception:
                # 读取失败时默认使用浅色主题
                return "light"
        # 其他平台暂时统一采用浅色主题
        return "light"
    except Exception:
        return "light"

def find_resource_file(filename):
    """查找资源文件，返回找到的路径或None

    Args:
        filename: 资源文件名

    Returns:
        str: 资源文件的完整路径，未找到返回None

    Note:
        搜索顺序：
        1. 基础路径
        2. 基础路径/assets
        3. 基础路径/fonts
        4. 基础路径/file
        5. 基础路径/logo
        6. _MEIPASS（打包环境）
        7. _MEIPASS/assets
        8. _MEIPASS/fonts
        9. _MEIPASS/file
        10. _MEIPASS/logo
    """
    global _search_paths_cache, _base_path_cache
    base_path = get_base_path()
    
    # 只在基础路径变化时重新构建搜索路径
    if _base_path_cache != base_path:
        _base_path_cache = base_path
        _search_paths_cache = _build_search_paths(base_path)
    
    # 在所有路径中查找文件
    for path in _search_paths_cache:
        full_path = os.path.join(path, filename)
        if os.path.exists(full_path):
            # 调试日志：记录找到的资源文件路径
            print(f"[DEBUG] 找到资源文件: {filename} -> {full_path}")
            return full_path

    # 调试日志：记录未找到的资源文件
    print(f"[DEBUG] 未找到资源文件: {filename}")
    print(f"[DEBUG] 搜索路径列表: {_search_paths_cache}")
    return None

def get_resource_path(relative_path):
    """获取资源文件的绝对路径，是资源加载的主要接口

    Args:
        relative_path: 资源文件的相对路径

    Returns:
        str: 资源文件的绝对路径，如果找不到则返回基于基础路径的相对路径

    Note:
        此函数是资源加载的主要接口，会调用 find_resource_file 进行查找
    """
    return find_resource_file(relative_path) or os.path.join(get_base_path(), relative_path)

def load_icon_universal():
    """统一的图标加载函数，适用于所有环境

    Returns:
        QIcon: 应用程序图标对象

    Note:
        尝试加载 logo.ico 和 logo.png，如果都失败则创建后备图标
    """
    # 尝试多种图标格式和路径
    for icon_file in ICON_FILES:
        icon_path = find_resource_file(icon_file)
        if icon_path and os.path.exists(icon_path):
            return QIcon(icon_path)

    # 创建后备图标
    return create_fallback_icon()

def load_logo(logo_size=(60, 60)):
    """统一的Logo加载函数，适用于所有环境

    Args:
        logo_size: Logo的目标尺寸，默认(60, 60)

    Returns:
        QPixmap: 缩放后的Logo图片，如果加载失败则返回None

    Note:
        使用平滑变换模式进行缩放，保持宽高比
    """
    try:
        # 查找logo文件
        logo_path = find_resource_file(LOGO_FILE)
        if logo_path and os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            if not pixmap.isNull():
                return pixmap.scaled(logo_size[0], logo_size[1],
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
        return None
    except Exception as e:
        print(f"[ERROR] 加载Logo失败: {e}")
        return None

def create_fallback_icon():
    """创建后备图标

    Returns:
        QIcon: 后备图标对象，创建失败返回空图标

    Note:
        创建一个简单的蓝色图标，上面显示"BG"文字
    """
    try:
        # 创建一个简单的蓝色图标
        pixmap = QPixmap(32, 32)
        pixmap.fill(QColor("#66ccff"))

        painter = QPainter(pixmap)
        painter.setPen(QColor('white'))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "BG")
        painter.end()

        return QIcon(pixmap)
    except Exception:
        # 如果创建失败，返回默认图标
        return QIcon()


# =============================================================================
# 版本信息访问函数 - 统一入口点
# =============================================================================

def get_current_version():
    """获取当前应用程序版本号

    Returns:
        str: 应用程序版本号，格式为"X.Y.Z"

    Note:
        此函数是版本信息的统一入口点
    """
    return version_manager.get_version()


def get_current_app_info():
    """获取当前应用程序信息

    Returns:
        dict: 包含应用程序名称、英文名称、公司、版权等元数据的字典

    Note:
        此函数是应用程序信息的统一入口点
    """
    return version_manager.get_app_info()

def _get_key_display_name(keycode):
    """获取按键显示名称的辅助函数

    Args:
        keycode: 键码

    Returns:
        str: 按键的中文名称
    """
    try:
        keycode_int = int(keycode)
        return _COMBINED_KEY_MAPPING.get(keycode_int, keycode)
    except (ValueError, TypeError):
        return keycode

def check_event_pairing(events_table):
    """检查事件成对性

    Args:
        events_table: 事件表格对象

    Returns:
        list: 包含检查出的问题的列表

    Note:
        检查以下问题：
        - 按键重复按下
        - 按键未按下就释放
        - 鼠标按钮重复按下
        - 鼠标按钮未按下就释放
        - 按键被按下但未释放
        - 鼠标按钮被按下但未释放
    """
    pressed_keys = {}  # 记录按下的按键，键为键码，值为按下的行号
    pressed_mouse_buttons = {}  # 记录按下的鼠标按钮，键为按钮名称，值为按下的行号
    issues = []
    
    for row in range(events_table.rowCount()):
        type_item = events_table.item(row, 2)  # 事件类型列
        keycode_item = events_table.item(row, 3)  # 键码列
        
        if not type_item:
            continue
            
        event_type = type_item.text()
        keycode = keycode_item.text() if keycode_item else ""
        
        # 检查按键事件
        if event_type == "按键按下":
            if keycode in pressed_keys:
                key_name_cn = _get_key_display_name(keycode)
                issues.append(f"第{row+1}行: 按键{key_name_cn}重复按下")
            else:
                pressed_keys[keycode] = row + 1
        elif event_type == "按键释放":
            if keycode not in pressed_keys:
                key_name_cn = _get_key_display_name(keycode)
                issues.append(f"第{row+1}行: 按键{key_name_cn}未按下就释放")
            else:
                del pressed_keys[keycode]
        
        # 检查鼠标事件
        elif event_type == "左键按下":
            if "Left" in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 左键重复按下")
            else:
                pressed_mouse_buttons["Left"] = row + 1
        elif event_type == "左键释放":
            if "Left" not in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 左键未按下就释放")
            else:
                del pressed_mouse_buttons["Left"]

        elif event_type == "右键按下":
            if "Right" in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 右键重复按下")
            else:
                pressed_mouse_buttons["Right"] = row + 1
        elif event_type == "右键释放":
            if "Right" not in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 右键未按下就释放")
            else:
                del pressed_mouse_buttons["Right"]

        elif event_type == "中键按下":
            if "Middle" in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 中键重复按下")
            else:
                pressed_mouse_buttons["Middle"] = row + 1
        elif event_type == "中键释放":
            if "Middle" not in pressed_mouse_buttons:
                issues.append(f"第{row+1}行: 中键未按下就释放")
            else:
                del pressed_mouse_buttons["Middle"]

    # 检查未释放的按键
    for key, row_num in pressed_keys.items():
        key_name_cn = _get_key_display_name(key)
        issues.append(f"第{row_num}行: 按键{key_name_cn}被按下但未释放")
    for button, row_num in pressed_mouse_buttons.items():
        button_name = "左键" if button == "Left" else "右键" if button == "Right" else "中键"
        issues.append(f"第{row_num}行: 鼠标{button_name}按钮被按下但未释放")
    
    return issues


def set_window_title_bar_theme(window, is_dark=False):
    """为窗口设置标题栏主题（Windows 10+ 深色/浅色模式）

    使用 Windows DWM API 设置窗口标题栏的沉浸式深色模式，
    使标题栏颜色与主题保持一致。

    Args:
        window: PyQt6 窗口对象（QMainWindow 或 QDialog）
        is_dark: 是否使用深色模式，True 为深色，False 为浅色

    Returns:
        bool: 设置成功返回 True，失败返回 False

    Note:
        - 此功能仅支持 Windows 10 及以上系统
        - 非 Windows 系统会静默跳过，不影响程序运行
        - 窗口必须有效且具有 windowHandle 属性
    """
    try:
        if sys.platform != "win32":
            return False

        # 全面的窗口有效性检查
        if not window:
            return False

        # 检查窗口是否已被删除或无效
        if hasattr(window, 'isValid') and callable(window.isValid):
            if not window.isValid():
                return False

        # 检查窗口是否有windowHandle属性
        if not hasattr(window, 'windowHandle'):
            return False

        # 获取windowHandle
        window_handle = window.windowHandle()
        if not window_handle:
            return False

        # 检查windowHandle是否有效
        if hasattr(window_handle, 'isValid') and callable(window_handle.isValid):
            if not window_handle.isValid():
                return False

        # 获取窗口句柄
        hwnd = int(window_handle.winId())

        value = ctypes.c_int(1 if is_dark else 0)

        # 调用DWM API设置窗口标题栏主题
        result = ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_USE_IMMERSIVE_DARK_MODE,
            ctypes.byref(value),
            ctypes.sizeof(value)
        )

        return result == 0

    except RuntimeError as e:
        # 捕获"wrapped C/C++ object of type X has been deleted"错误
        if "wrapped C/C++ object" in str(e) and "has been deleted" in str(e):
            print("[DEBUG] 尝试设置已删除窗口的标题栏主题，跳过")
            return False
        else:
            print(f"[DEBUG] 设置窗口标题栏主题失败: {e}")
            return False
    except Exception as e:
        print(f"[DEBUG] 设置窗口标题栏主题失败: {e}")
        return False
