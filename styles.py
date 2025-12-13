# styles.py - 全局样式和字体管理模块
import os
import sys
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QPainter, QColor, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtWidgets import QGroupBox, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QListView, QPushButton, QWidget, QDialog, QMainWindow, QHBoxLayout

# 导入资源管理器函数
from utils import get_base_path, find_resource_file, get_resource_path, load_icon_universal, create_fallback_icon, fix_windows_taskbar_icon_for_window

# =============================================================================
# 字体管理器 - 修改为全局字体管理器
# =============================================================================

class GlobalFontManager:
    """全局字体管理器 - 专门负责字体的加载和管理"""
    
    _instance = None
    _smiley_font_loaded = False
    _smiley_font_id = -1
    _source_han_loaded = False
    _source_han_id = -1
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = GlobalFontManager()
        return cls._instance
    
    def __init__(self):
        """初始化字体管理器"""
        # 延迟加载机制：仅在需要时才加载字体
        pass
    
    def _load_smiley_font(self):
        """加载得意黑字体"""
        try:
            font_files = ["SmileySans-Oblique.ttf"]
            for font_file in font_files:
                font_path = find_resource_file(font_file)
                if font_path and os.path.exists(font_path):
                    self._smiley_font_id = QFontDatabase.addApplicationFont(font_path)
                    if self._smiley_font_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(self._smiley_font_id)
                        if font_families:
                            self._smiley_font_loaded = True
                            print(f"全局字体管理器：成功加载得意黑字体: {font_families[0]} from {font_path}")
                            return True
                        else:
                            print(f"全局字体管理器：加载得意黑字体失败: 无法获取字体家族 from {font_path}")
                    else:
                        print(f"全局字体管理器：加载得意黑字体失败: QFontDatabase.addApplicationFont返回-1 for {font_path}")
            
            print("全局字体管理器：未找到得意黑字体文件，将使用备用字体")
            return False
            
        except Exception as e:
            print(f"全局字体管理器：加载得意黑字体时出错: {e}")
            return False
    
    def get_smiley_font(self, size=12, weight=QFont.Weight.Normal):
        """获取得意黑字体"""
        if not self._smiley_font_loaded:
            self._load_smiley_font()
        
        if self._smiley_font_loaded:
            font_families = QFontDatabase.applicationFontFamilies(self._smiley_font_id)
            if font_families:
                font = QFont(font_families[0], size, weight)
                return font
        
        # 备用字体：使用系统默认的无衬线字体
        font = QFont("sans-serif", size, weight)
        return font
    
    def _load_source_han_font(self):
        """加载SourceHanSerifCN-Regular-1.otf字体"""
        try:
            font_files = ["SourceHanSerifCN-Regular-1.otf"]
            for font_file in font_files:
                font_path = find_resource_file(font_file)
                if font_path and os.path.exists(font_path):
                    self._source_han_id = QFontDatabase.addApplicationFont(font_path)
                    if self._source_han_id != -1:
                        font_families = QFontDatabase.applicationFontFamilies(self._source_han_id)
                        if font_families:
                            self._source_han_loaded = True
                            print(f"全局字体管理器：成功加载思源宋体: {font_families[0]} from {font_path}")
                            return True
                        else:
                            print(f"全局字体管理器：加载思源宋体失败: 无法获取字体家族 from {font_path}")
                    else:
                        print(f"全局字体管理器：加载思源宋体失败: QFontDatabase.addApplicationFont返回-1 for {font_path}")
            
            print("全局字体管理器：未找到思源宋体字体文件，将使用备用字体")
            return False
            
        except Exception as e:
            print(f"全局字体管理器：加载思源宋体字体时出错: {e}")
            return False
    
    def get_source_han_font(self, size=12, weight=QFont.Weight.Normal):
        """获取思源宋体字体"""
        if not self._source_han_loaded:
            self._load_source_han_font()
        
        if self._source_han_loaded:
            font_families = QFontDatabase.applicationFontFamilies(self._source_han_id)
            if font_families:
                font = QFont(font_families[0], size, weight)
                return font
        
        # 备用字体：使用系统默认的衬线字体
        font = QFont("serif", size, weight)
        return font
    
    def is_source_han_font_available(self):
        """检查思源宋体字体是否可用"""
        if not self._source_han_loaded:
            self._load_source_han_font()
        return self._source_han_loaded
    
    def is_smiley_font_available(self):
        """检查得意黑字体是否可用"""
        if not self._smiley_font_loaded:
            self._load_smiley_font()
        return self._smiley_font_loaded

# 保持兼容性的StyleManager类
class StyleManager:
    """样式管理器 - 管理应用程序的样式"""
    
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = StyleManager()
        return cls._instance
    
    def __init__(self):
        """初始化样式管理器"""
        # 样式管理器的初始化代码
        pass

# 添加全局获取函数
def get_global_font_manager():
    """获取全局字体管理器实例"""
    return GlobalFontManager.get_instance()


class StyledWidget(QWidget):
    """基础样式控件类，自动初始化字体管理器"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 自动初始化字体管理器
        self.font_manager = get_global_font_manager()


class StyledDialog(QDialog):
    """基础样式对话框类，自动初始化字体管理器和窗口基本设置"""
    
    def __init__(self, parent=None, title="", size=None, window_flags=None, icon=None):
        super().__init__(parent)
        # 自动初始化字体管理器
        self.font_manager = get_global_font_manager()
        
        # 设置窗口基本属性
        if title:
            self.setWindowTitle(title)
        
        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width > 0 and height > 0:
                    self.setFixedSize(width, height)
        
        if window_flags:
            self.setWindowFlags(window_flags)
        
        if icon:
            self.setWindowIcon(icon)
        elif hasattr(self, 'load_icon'):
            try:
                icon = self.load_icon()
                if icon:
                    self.setWindowIcon(icon)
            except Exception:
                pass
        
        # 应用对话框背景样式
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_dialog_bg_style())


class StyledMainWindow(QMainWindow):
    """基础样式主窗口类，自动初始化字体管理器和窗口基本设置"""
    
    def __init__(self, parent=None, title="", size=None, window_flags=None, icon=None):
        super().__init__(parent)
        # 自动初始化字体管理器
        self.font_manager = get_global_font_manager()
        
        # 设置窗口基本属性
        if title:
            self.setWindowTitle(title)
        
        if size:
            if isinstance(size, tuple) and len(size) == 2:
                width, height = size
                if width > 0 and height > 0:
                    self.setFixedSize(width, height)
        
        if window_flags:
            self.setWindowFlags(window_flags)
        
        if icon:
            self.setWindowIcon(icon)
        elif hasattr(self, 'load_icon'):
            try:
                icon = self.load_icon()
                if icon:
                    self.setWindowIcon(icon)
            except Exception:
                pass


class WindowIconMixin:
    """窗口图标修复混入类，提供统一的任务栏图标修复功能"""
    
    # 信号：图标修复完成
    icon_fixed = pyqtSignal(bool)
    
    def __init__(self):
        """初始化混入类"""
        self._icon_fixed = False  # 防止重复修复的标志
        self._fix_timer = None  # 定时器引用
    
    def setup_icon_fixing(self, delay_ms=100):
        """
        设置图标修复，在窗口显示后调用
        
        Args:
            delay_ms: 延迟时间（毫秒），默认100ms
        """
        if self._icon_fixed:
            return
            
        if os.name == 'nt':
            # 使用定时器延迟调用，确保窗口已经完全显示
            self._fix_timer = QTimer()
            self._fix_timer.setSingleShot(True)
            self._fix_timer.timeout.connect(self._fix_icon_safe)
            self._fix_timer.start(delay_ms)
            self._icon_fixed = True
    
    def _fix_icon_safe(self):
        """安全修复任务栏图标"""
        try:
            # 检查是否已经修复过，避免重复执行
            if hasattr(self, '_icon_fixed') and self._icon_fixed:
                return True
            
            success = fix_windows_taskbar_icon_for_window(self)
            # 修复完成后设置标志，防止重复修复
            if hasattr(self, '_icon_fixed'):
                self._icon_fixed = True
            
            if hasattr(self, 'debug_logger') and hasattr(self.debug_logger, 'log_info'):
                self.debug_logger.log_info("任务栏图标修复完成")
            self.icon_fixed.emit(success)
            return success
        except Exception as e:
            error_msg = f"任务栏图标修复失败: {e}"
            if hasattr(self, 'debug_logger') and hasattr(self.debug_logger, 'log_error'):
                self.debug_logger.log_error(error_msg)
            else:
                print(f"[ERROR] {error_msg}")
            self.icon_fixed.emit(False)
            return False
    
    def fix_taskbar_icon(self):
        """
        修复任务栏图标 - 兼容旧接口
        
        为了保持向后兼容性，提供此方法
        """
        return self._fix_icon_safe()
    
    def _fix_taskbar_icon_safe(self):
        """
        安全修复任务栏图标 - 兼容旧接口
        
        为了保持向后兼容性，提供此方法
        """
        return self._fix_icon_safe()
    
    def cleanup_icon_fixing(self):
        """清理图标修复相关的资源"""
        if self._fix_timer and self._fix_timer.isActive():
            self._fix_timer.stop()
            self._fix_timer = None

# =============================================================================
# 全局常量和映射 - 保持不变
# =============================================================================

# 颜色主题 - 修改背景色为纯白色
COLORS = {
    'bg': "#ffffff",  # 改为纯白色
    'card_bg': "#ffffff",
    'primary': "#66ccff",
    'primary_hover': "#66ccff",
    'primary_pressed': "#3399ff",
    'secondary': "#ffffff",  # 普通按钮改为纯白色
    'secondary_hover': "#f5f5f5",  # 悬停时略微变灰
    'secondary_pressed': "#e5e5e5",
    'text': "#323130",
    'text_secondary': "#666666",
    'success': "#107c10",
    'error': "#d13438",
    'warning': "#ff8c00",
    'border': "#d0d0d0",
    'border_light': "#e0e0e0",
    'grid': "#e8e8e8"
}

# WinUI3阴影效果 - 根据控件层级定义不同深度的阴影（注释掉不支持的box-shadow）
SHADOWS = {
    'small': '',  # 小型控件 - 移除box-shadow
    'medium': '',  # 中型控件 - 移除box-shadow
    'large': ''  # 大型控件 - 移除box-shadow
}

# =============================================================================
# 样式工具类 - 统一样式系统
# =============================================================================

class UnifiedStyleHelper:
    """统一样式助手类，使用单例模式管理所有控件样式"""
    _instance = None
    
    @classmethod
    def get_instance(cls):
        if not cls._instance:
            cls._instance = UnifiedStyleHelper()
        return cls._instance
    
    def __init__(self):
        """初始化样式助手"""
        # 颜色主题常量
        self.COLORS = COLORS
        self.SHADOWS = SHADOWS
    
    def get_button_style(self, accent=False, disabled=False):
        """获取按钮样式"""
        if disabled:
            return f"""
                QPushButton {{
                    background-color: #f5f5f5;
                    color: #999999;
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 11px;
                    {self.SHADOWS['small']}

                }}
            """
        
        if accent:
            return f"""
                QPushButton {{
                    background-color: {self.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-weight: bold;
                    font-size: 11px;
                    {self.SHADOWS['small']}
                }}
                QPushButton:hover {{
                    background-color: {self.COLORS['primary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.COLORS['primary_pressed']};
                }}
            """
        else:
            return f"""
                QPushButton {{
                    background-color: {self.COLORS['secondary']};
                    color: {self.COLORS['text']};
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 11px;
                    {self.SHADOWS['small']}
                }}
                QPushButton:hover {{
                    background-color: {self.COLORS['secondary_hover']};
                }}
                QPushButton:pressed {{
                    background-color: {self.COLORS['secondary_pressed']};
                }}
            """
    
    def get_line_edit_style(self):
        """获取输入框样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QLineEdit {{ 
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
            }}
            QLineEdit:focus {{ 
                border-color: {self.COLORS['primary']};
                background-color: #fafafa;
            }}
            QLineEdit:hover {{ 
                border-color: #a0a0a0;
            }}
        """
    
    def get_combo_box_style(self):
        """获取下拉框样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QComboBox {{ 
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
                min-width: 80px;
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
            }}
            QComboBox::drop-down {{ 
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{ 
                width: 12px;
                height: 12px;
                border: none;
            }}
            QComboBox QAbstractItemView {{ 
                border: 1px solid {self.COLORS['border']}; 
                border-radius: 6px; 
                background-color: white; 
                selection-background-color: {self.COLORS['primary']}; 
                selection-color: white; 
                font-size: 11px; 
                padding: 4px;
                {self.SHADOWS['small']} 
            }}
            QComboBox:hover {{ 
                border-color: #a0a0a0;
            }}
            QComboBox:focus {{ 
                border-color: {self.COLORS['primary']};
            }}
        """
    
    def get_table_style(self):
        """获取表格样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QTableWidget {{ 
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                background-color: white;
                gridline-color: #f0f0f0;
                font-size: 11px;
                outline: none;
                {self.SHADOWS['medium']}
            }}
            QTableWidget::item {{ 
                padding: 6px 8px;
                border: none;
                text-align: center;
            }}
            QTableWidget::item:selected {{ 
                background-color: {self.COLORS['primary']};
                color: white;
            }}
            QTableWidget::item:hover {{ 
                background-color: #f0f8ff;
            }}
            QHeaderView::section {{ 
                background-color: #ffffff;
                padding: 4px 10px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 10px;
                color: #333333;
                text-align: center;
                min-height: 20px;
            }}
            QHeaderView::section:last {{ 
                border-right: none;
            }}
            QTableCornerButton::section {{ 
                background-color: #ffffff;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
            }}
        """
    
    def get_group_box_style(self):
        """获取分组框样式 - 已去掉灰色底纹"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QGroupBox {{ 
                font-size: 12px;
                font-weight: bold;
                color: {self.COLORS['primary']};
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 12px;
                /* background-color: #fafafa;  已去掉灰色底纹 */
                {self.SHADOWS['medium']}
            }}
            QGroupBox::title {{ 
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 8px 0 8px;
                /* background-color: #fafafa;  已去掉灰色底纹 */
            }}
        """
    
    def get_header_widget_style(self):
        """获取标题栏样式"""
        return f"""
            HeaderWidget {{
                background-color: #ffffff;
                border-bottom: 1px solid {self.COLORS['border']};
                
            }}
        """
    
    def get_slogan_label_style(self):
        """获取标语标签样式"""
        return f"""
            QLabel {{
                font-family: "SourceHanSerifCN";
                font-size: 12px;
                color: {self.COLORS['text_secondary']};
                font-style: italic;
                margin-right: 15px;
                background-color: transparent;
            }}
        """
    
    def get_dialog_bg_style(self):
        """获取对话框背景样式"""
        return f"""
            QDialog {{
                background-color: {self.COLORS['bg']};
            }}
        """
    
    def get_logo_label_style(self):
        """获取Logo标签样式"""
        return "font-size: 28px; background-color: transparent;"
    
    def get_container_bg_style(self):
        """获取容器背景样式"""
        return "background-color: #ffffff;"
    
    
    
    def get_quick_keys_label_style(self):
        """获取快速按键标签样式"""
        return "font-size: 10px;"
    
    def get_total_time_label_style(self):
        """获取总时间标签样式"""
        return f"""
            QLabel {{
                font-weight: bold; 
                color: {self.COLORS['primary']};
                font-size: 12px;
                background-color: transparent;
            }}
        """
    
    def get_script_text_style(self):
        """获取脚本文本样式"""
        return f"""
            QTextEdit {{ 
                font-family: "Consolas, SourceHanSerifCN";
                font-size: 12px;
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_log_display_style(self):
        """获取日志显示样式"""
        return f"""
            QTextEdit {{ 
                font-family: "Consolas, SourceHanSerifCN";
                font-size: 10px;
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px;
            }}
        """
    
    def get_agreement_browser_style(self):
        """获取协议浏览器样式"""
        return f"""
            QTextBrowser {{ 
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 4px;
                padding: 6px;
                font-family: SourceHanSerifCN;
                font-size: 10px;
                line-height: 1.3;
            }}
            QTextBrowser a {{ 
                color: {self.COLORS['primary']};
                text-decoration: none;
            }}
            QTextBrowser a:hover {{ 
                color: {self.COLORS['primary_hover']};
                text-decoration: underline;
            }}
        """
    
    def get_info_edit_style(self):
        """获取信息编辑框样式"""
        return f"""
            QPlainTextEdit {{ 
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 4px;
                padding: 10px;
                font-family: SourceHanSerifCN;
                font-size: 10px;
                line-height: 1.3;
            }}
        """
    
    def get_status_bar_style(self):
        """获取状态栏样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QStatusBar {{ 
                background-color: #ffffff;
                color: {self.COLORS['text']};
                border-top: 1px solid {self.COLORS['border']};
                font-size: 10px;
            }}
        """
    
    def get_text_browser_style(self):
        """获取文本浏览器样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QTextBrowser {{
                background-color: #f8f9fa;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 6px;
                padding: 10px;
                font-size: 10px;
                line-height: 1.3;
                {self.SHADOWS['small']}
            }}
            QTextBrowser a {{
                color: {self.COLORS['primary']};
                text-decoration: none;
            }}
            QTextBrowser a:hover {{
                color: {self.COLORS['primary_hover']};
                text-decoration: underline;
            }}
        """
    
    def get_spin_box_style(self):
        """获取整数和浮点数输入框样式"""
        # 使用系统默认字体，避免硬编码字体名称
        return f"""
            QSpinBox, QDoubleSpinBox {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px 4px 6px 4px;
                background-color: white;
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                text-align: center;
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
            }}
            QSpinBox:focus, QDoubleSpinBox:focus {{
                border-color: {self.COLORS['primary']};
                background-color: #fafafa;
                border-width: 1.5px;
            }}
            QSpinBox:hover, QDoubleSpinBox:hover {{
                border-color: #a0a0a0;
                background-color: #fafafa;
            }}
            QSpinBox::up-button, QDoubleSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                height: 15px;
                border: none;
                border-top-right-radius: 5px;
                background-color: transparent;
                margin: 1px 1px 0px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::up-button:hover, QDoubleSpinBox::up-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::up-button:pressed, QDoubleSpinBox::up-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
            QSpinBox::down-button, QDoubleSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                height: 15px;
                border: none;
                border-bottom-right-radius: 5px;
                background-color: transparent;
                margin: 0px 1px 1px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::down-button:hover, QDoubleSpinBox::down-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::down-button:pressed, QDoubleSpinBox::down-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
        """
    
    def get_coordinate_capture_label_style(self):
        """获取坐标捕获标签样式"""
        return f"""
            QLabel {{
                border: 2px solid {self.COLORS['border']};
                background-color: #ffffff;
            }}
        """
    
    def get_centered_combo_box_style(self):
        """获取居中组合框样式"""
        return f"""
            QComboBox {{
                background-color: {self.COLORS['card_bg']};
                color: {self.COLORS['text']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px 8px;
                font-size: 11px;
                text-align: center;
            }}
            QComboBox::drop-down {{
                border: none;
                width: 0px;
            }}
            QComboBox::down-arrow {{
                image: none;
            }}
        """
    
    def get_splitter_style(self):
        """获取分割器样式"""
        return """
            QSplitter::handle {
                background-color: transparent;
                width: 6px;
                height: 6px;
                border-radius: 3px;
            }
            QSplitter::handle:hover {
                background-color: transparent;
            }
        """
    
    def get_search_container_style(self):
        """获取搜索容器样式"""
        return """
            QWidget {
                background-color: #ffffff;
                border: none;
                border-radius: 8px;
                %s
            }
        """ % (self.SHADOWS['small'])
    
    def get_search_input_style(self):
        """获取搜索输入框样式"""
        return """
            QLineEdit {{ 
                border: 1px solid %s;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
                selection-background-color: %s;
                %s
                min-height: 30px;
                max-height: 30px;
            }}
            QLineEdit:focus {{ 
                border-color: %s;
                background-color: #fafafa;
            }}
            QLineEdit:hover {{ 
                border-color: #a0a0a0;
            }}
        """ % (self.COLORS['border'], self.COLORS['primary'], self.SHADOWS['small'], self.COLORS['primary'])
    
    def get_filter_combo_style(self):
        """获取过滤组合框样式"""
        return """
            QComboBox {{ 
                border: 1px solid %s;
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                font-size: 11px;
                min-width: 80px;
                %s
                min-height: 30px;
                max-height: 30px;
            }}
            QComboBox::drop-down {{ 
                border: none;
                width: 20px;
            }}
            QComboBox::down-arrow {{ 
                width: 12px;
                height: 12px;
                border: none;
            }}
            QComboBox QAbstractItemView {{ 
                border: 1px solid %s; 
                border-radius: 6px; 
                background-color: white; 
                selection-background-color: %s; 
                selection-color: white; 
                font-size: 11px; 
                padding: 4px;
                %s 
            }}
            QComboBox:hover {{ 
                border-color: #a0a0a0;
            }}
            QComboBox:focus {{ 
                border-color: %s;
            }}
        """ % (self.COLORS['border'], self.SHADOWS['small'], self.COLORS['border'], self.COLORS['primary'], self.SHADOWS['small'], self.COLORS['primary'])
    
    def get_scroll_bar_style(self):
        """获取滚动条样式"""
        return """
            /* 垂直滚动条 */
            QScrollBar:vertical {
                background-color: %s;
                width: 8px;
                margin: 0px;
            }
            
            QScrollBar::groove:vertical {
                background-color: %s;
                border-radius: 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: %s;
                border-radius: 4px;
                min-height: 20px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: %s;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: %s;
            }
            
            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }
            
            QScrollBar::add-page:vertical,
            QScrollBar::sub-page:vertical {
                background-color: transparent;
            }
            
            /* 水平滚动条 */
            QScrollBar:horizontal {
                background-color: %s;
                height: 8px;
                margin: 0px;
            }
            
            QScrollBar::groove:horizontal {
                background-color: %s;
                border-radius: 4px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: %s;
                border-radius: 4px;
                min-width: 20px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: %s;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: %s;
            }
            
            QScrollBar::add-line:horizontal,
            QScrollBar::sub-line:horizontal {
                background-color: transparent;
                border: none;
                height: 0px;
                width: 0px;
            }
            
            QScrollBar::add-page:horizontal,
            QScrollBar::sub-page:horizontal {
                background-color: transparent;
            }
        """ % (
            self.COLORS['bg'],
            self.COLORS['bg'],  # 将槽的背景色改为纯白色
            self.COLORS['border'],
            self.COLORS['primary_hover'],
            self.COLORS['primary_pressed'],
            self.COLORS['bg'],
            self.COLORS['bg'],  # 将槽的背景色改为纯白色
            self.COLORS['border'],
            self.COLORS['primary_hover'],
            self.COLORS['primary_pressed']
        )
    
    def get_centered_combobox_listview_style(self):
        """获取居中组合框列表视图样式"""
        return f"""
            QListView {{ 
                background-color: {self.COLORS['card_bg']}; 
                color: {self.COLORS['text']}; 
                font-family: "SourceHanSerifCN";
                font-size: 11px;
                outline: none;
                show-decoration-selected: 0;
            }}
            QListView::item {{ 
                padding: 8px;
                text-align: center;
                border: none;
            }}
            QListView::item:selected {{ 
                background-color: {self.COLORS['primary']}; 
                color: white;
            }}
        """
    
    def set_smiley_font(self, widget, size=12, weight=QFont.Weight.Normal):
        """为组件设置得意黑字体"""
        font_manager = get_global_font_manager()
        if font_manager.is_smiley_font_available():
            widget.setFont(font_manager.get_smiley_font(size, weight))
        else:
            widget.setFont(QFont("sans-serif", size, weight))
    
    def set_source_han_font(self, widget, size=12, weight=QFont.Weight.Normal):
        """为组件设置思源宋体字体"""
        font_manager = get_global_font_manager()
        widget.setFont(font_manager.get_source_han_font(size, weight))
    
    def get_time_offset_spin_box_style(self):
        """获取时间偏移输入框样式"""
        return f"""
            QSpinBox {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 6px;
                padding: 6px 8px;
                background-color: white;
                font-family: "SourceHanSerifCN";
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                text-align: center;
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
            }}
            QSpinBox:focus {{
                border-color: {self.COLORS['primary']};
                background-color: #fafafa;
                border-width: 1.5px;
            }}
            QSpinBox:hover {{
                border-color: #a0a0a0;
                background-color: #fafafa;
            }}
            QSpinBox::up-button {{
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 24px;
                height: 15px;
                border: none;
                border-top-right-radius: 5px;
                background-color: transparent;
                margin: 1px 1px 0px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::up-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::up-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
            QSpinBox::down-button {{
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 24px;
                height: 15px;
                border: none;
                border-bottom-right-radius: 5px;
                background-color: transparent;
                margin: 0px 1px 1px 0px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }}
            QSpinBox::down-button:hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QSpinBox::down-button:pressed {{
                background-color: {self.COLORS['primary_pressed']};
            }}
        """
    
    def get_explanation_text_edit_style(self):
        """获取说明文本编辑器样式"""
        return f"""
            QTextEdit {{
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 6px;
                padding: 6px;
                font-family: "SourceHanSerifCN";
                font-size: 10px;
                {self.SHADOWS['small']}
            }}
        """
    
    def get_event_dialog_style(self):
        """获取事件对话框样式"""
        return f"""
            QDialog {{ 
                background-color: {self.COLORS['bg']}; 
            }}
        """
    
    def get_absolute_time_info_style(self):
        """获取绝对时间信息标签样式"""
        return f"color: {self.COLORS['text_secondary']}; font-size: 9px;"
    
    def get_capture_status_style(self, status="inactive"):
        """获取捕获状态样式
        
        Args:
            status: 状态类型，可选值："active"、"inactive"、"bold"
        
        Returns:
            对应的样式字符串
        """
        if status == "active":
            return f"color: {self.COLORS['primary']};"
        elif status == "inactive":
            return f"color: {self.COLORS['text_secondary']};"
        elif status == "bold":
            return f"color: {self.COLORS['primary']}; font-weight: bold;"
        return f"color: {self.COLORS['text_secondary']};"
    
    def setup_global_style(self, app):
        """设置全局样式"""
        from PyQt6.QtWidgets import QApplication
        
        # 设置全局字体 - 使用SourceHanSerifCN字体
        font_manager = get_global_font_manager()
        q_app = QApplication.instance()
        if q_app:
            # 使用SourceHanSerifCN字体作为全局默认字体
            q_app.setFont(font_manager.get_source_han_font(9))
        
        # 获取滚动条样式
        scroll_bar_style = self.get_scroll_bar_style()
        
        # 设置应用程序样式表
        # 尝试直接在QApplication实例上设置样式表
        if hasattr(q_app, 'setStyleSheet'):
            q_app.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {self.COLORS['bg']};
                }}
                QDialog {{
                    background-color: {self.COLORS['bg']};
                }}
                QWidget {{
                    background-color: {self.COLORS['bg']};
                }}
                QGroupBox {{
                    background-color: {self.COLORS['bg']};
                }}
                QMenuBar {{
                    background-color: {self.COLORS['bg']};
                    border: none;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    padding: 4px 8px;
                    border-radius: 4px;
                }}
                QMenuBar::item:selected {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                QMenu {{ 
                    background-color: {self.COLORS['bg']};
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 4px;
                    padding: 4px;
                    {self.SHADOWS['small']}
                }}
                QMenu::item {{
                    padding: 4px 16px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                QAction::hover {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                
                /* 滚动条样式 */
                {scroll_bar_style}
            """)
        # 如果QApplication实例不可用，尝试在传入的app对象上设置
        elif hasattr(app, 'setStyleSheet'):
            app.setStyleSheet(f"""
                QMainWindow {{
                    background-color: {self.COLORS['bg']};
                }}
                QDialog {{
                    background-color: {self.COLORS['bg']};
                }}
                QWidget {{
                    background-color: {self.COLORS['bg']};
                }}
                QGroupBox {{
                    background-color: {self.COLORS['bg']};
                }}
                QMenuBar {{
                    background-color: {self.COLORS['bg']};
                    border: none;
                    padding: 4px;
                }}
                QMenuBar::item {{
                    padding: 4px 8px;
                    border-radius: 4px;
                }}
                QMenuBar::item:selected {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                QMenu {{ 
                    background-color: {self.COLORS['bg']};
                    border: 1px solid {self.COLORS['border']};
                    border-radius: 4px;
                    padding: 4px;
                    {self.SHADOWS['small']}
                }}
                QMenu::item {{
                    padding: 4px 16px;
                    border-radius: 4px;
                }}
                QMenu::item:selected {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                QAction::hover {{
                    background-color: {self.COLORS['primary_hover']};
                    color: white;
                }}
                
                /* 滚动条样式 */
                {scroll_bar_style}
            """)

# =============================================================================
# 现代化控件类
# =============================================================================

class ModernGroupBox(QGroupBox):
    """现代化的分组框"""
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_group_box_style())

class ModernLineEdit(QLineEdit):
    """现代化的输入框，内容居中显示"""
    def __init__(self, text="", parent=None, width=None):
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if width:
            self.setFixedWidth(width)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_line_edit_style())

class ModernComboBox(QComboBox):
    """现代化的下拉框，内容居中显示"""
    def __init__(self, parent=None, width=None):
        super().__init__(parent)
        if width:
            self.setFixedWidth(width)
        
        # 结合原有样式表并添加文本居中样式
        combo_style = UnifiedStyleHelper.get_instance().get_combo_box_style() + "\n"
        combo_style += "QComboBox {\n"
        combo_style += "    text-align: center;\n"
        combo_style += "    padding-left: 15px; /* 调整文本位置使其居中 */\n"
        combo_style += "}\n"
        self.setStyleSheet(combo_style)
        
        # 获取下拉列表视图并设置样式
        view = self.view()
        if view:
            # 增加下拉列表项的高度并设置居中
            view.setStyleSheet("""
                 QListView::item {
                     padding: 6px 8px;
                     min-height: 20px;
                     text-align: center;
                 }
             """)
        
    def addItem(self, text):
        super().addItem(text)
        # 设置该项居中
        self.setItemData(self.count() - 1, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
    
    def addItems(self, texts):
        super().addItems(texts)
        # 设置所有项居中
        for i in range(self.count()):
            self.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
    
    def wheelEvent(self, event):
        """屏蔽鼠标滚轮事件，防止误触"""
        event.ignore()

class ModernSpinBox(QSpinBox):
    """现代化的整数输入框，带上下按钮，内容居中显示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_spin_box_style())

class ModernDoubleSpinBox(QDoubleSpinBox):
    """现代化的浮点数输入框，带上下按钮，内容居中显示"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_spin_box_style())


class CenteredComboBox(QComboBox):
    """完全居中的组合框"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # 设置组合框样式 - 移除下拉箭头
        base_style = UnifiedStyleHelper.get_instance().get_centered_combo_box_style()
        # 添加高度限制样式
        enhanced_style = base_style + """
            QComboBox {
                min-height: 20px;
                max-height: 20px;
            }
        """
        self.setStyleSheet(enhanced_style)
        
        # 移除下拉箭头
        self.setEditable(False)
        
        # 获取下拉列表视图并设置样式
        view = self.view()
        if view:
            # 增加下拉列表项的高度
            view.setStyleSheet("""
                QListView::item {
                    padding: 6px 8px;
                    min-height: 20px;
                }
            """)
    
    def addItems(self, items):
        """添加项目并确保居中"""
        super().addItems(items)
        # 设置所有项居中
        for i in range(self.count()):
            self.setItemData(i, Qt.AlignmentFlag.AlignCenter, Qt.ItemDataRole.TextAlignmentRole)
    
    def wheelEvent(self, event):
        """屏蔽鼠标滚轮事件，防止误触"""
        event.ignore()

class CenteredLineEdit(QLineEdit):
    """居中对齐的单行文本编辑器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置文本居中对齐
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # 获取基础样式并添加居中对齐样式
        base_style = UnifiedStyleHelper.get_instance().get_line_edit_style()
        # 在样式表中添加高度限制，覆盖原有设置
        enhanced_style = base_style + """
            QLineEdit {
                min-height: 20px;
                max-height: 20px;
            }
        """
        self.setStyleSheet(enhanced_style)

class TimeOffsetSpinBox(QSpinBox):
    """时间偏移输入框，带上下调节按钮，步长为100ms"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QSpinBox.ButtonSymbols.PlusMinus)
        self.setMinimum(0)
        self.setMaximum(999999)
        self.setSingleStep(100)
        self.setValue(0)
        
        # 设置样式表，保持与界面风格统一
        base_style = UnifiedStyleHelper.get_instance().get_time_offset_spin_box_style()
        # 添加高度限制样式
        enhanced_style = base_style + """
            QSpinBox {
                min-height: 20px;
                max-height: 20px;
            }
        """
        self.setStyleSheet(enhanced_style)

class DialogFactory:
    """对话框UI组件工厂，封装重复的UI创建模式"""
    
    @staticmethod
    def create_ok_cancel_buttons(parent, on_ok, on_cancel, ok_text="确定", cancel_text="取消", button_class=None):
        """创建确定和取消按钮布局
        
        参数:
            parent: 父窗口组件
            on_ok: 确定按钮点击事件处理函数
            on_cancel: 取消按钮点击事件处理函数
            ok_text: 确定按钮文本，默认为"确定"
            cancel_text: 取消按钮文本，默认为"取消"
            button_class: 自定义按钮类，默认为None（使用ModernButton）
        
        返回:
            QHBoxLayout: 包含确定和取消按钮的水平布局
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # 使用指定的按钮类或默认使用ModernButton
        if button_class is None:
            button_class = ModernButton
        
        ok_btn = button_class(ok_text, parent=parent, accent=True)
        cancel_btn = button_class(cancel_text, parent=parent)
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(on_cancel)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        
        return button_layout
    
    @staticmethod
    def create_close_button(parent, on_close, text="关闭"):
        """创建关闭按钮布局
        
        参数:
            parent: 父窗口组件
            on_close: 关闭按钮点击事件处理函数
            text: 关闭按钮文本，默认为"关闭"
            
        返回:
            QHBoxLayout: 包含关闭按钮的水平布局
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = ModernButton(text, parent=parent)
        close_btn.clicked.connect(on_close)
        
        button_layout.addWidget(close_btn)
        
        return button_layout

# =============================================================================
# 自定义消息框类
# =============================================================================

class ChineseMessageBox:
    """自定义消息框，确保按钮显示中文"""
    
    @staticmethod
    def show_warning(parent, title, message):
        """显示警告消息"""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Warning)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(load_icon_universal())
        
        # 清除所有标准按钮
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        
        # 添加自定义中文按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        
        # 使用UnifiedStyleHelper设置样式
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        # 不在Windows平台下调用任务栏图标修复，避免循环
        msg_box.exec()
    
    @staticmethod
    def show_error(parent, title, message):
        """显示错误消息"""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(load_icon_universal())
        
        # 清除所有标准按钮
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        
        # 添加自定义中文按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        
        # 使用UnifiedStyleHelper设置样式
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        # 不在Windows平台下调用任务栏图标修复，避免循环
        msg_box.exec()
    
    @staticmethod
    def show_info(parent, title, message):
        """显示信息消息"""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(load_icon_universal())
        
        # 清除所有标准按钮
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        
        # 添加自定义中文按钮
        ok_button = msg_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
        
        # 使用UnifiedStyleHelper设置样式
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        # 不在Windows平台下调用任务栏图标修复，避免循环
        msg_box.exec()
    
    @staticmethod
    def show_question(parent, title, message):
        """显示询问消息"""
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Icon.Question)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setWindowIcon(load_icon_universal())
        
        # 清除所有标准按钮
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton)
        
        # 添加自定义中文按钮
        yes_button = msg_box.addButton("是", QMessageBox.ButtonRole.YesRole)
        yes_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        
        no_button = msg_box.addButton("否", QMessageBox.ButtonRole.NoRole)
        no_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        
        msg_box.setDefaultButton(no_button)
        
        # 不在Windows平台下调用任务栏图标修复，避免循环
        result = msg_box.exec()
        
        # 修复：检查点击的按钮而不是对话框结果
        user_choice = "是" if msg_box.clickedButton() == yes_button else "否"
        print(f"[DEBUG] 用户选择: {user_choice}")
        
        return msg_box.clickedButton() == yes_button


# =============================================================================
# 带动画效果的按钮控件
# =============================================================================

class AnimatedButton(QPushButton):
    """带动画效果的按钮控件"""
    
    def __init__(self, text="", parent=None, accent=False, disabled=False):
        super().__init__(text, parent)
        self.accent = accent
        self.disabled = disabled
        self.pressed_color = None  # 按下时的颜色
        self.animation_duration = 100  # 动画持续时间(ms)
        
        # 设置基础样式
        self.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent, disabled))
        
        # 保存原始样式用于恢复
        self.original_style = UnifiedStyleHelper.get_instance().get_button_style(accent, disabled)
        
        # 连接鼠标事件
        self.pressed.connect(self._on_pressed)
        self.released.connect(self._on_released)
    
    def _on_pressed(self):
        """按钮按下时的处理"""
        if not self.disabled:
            # 根据按钮类型应用不同的按下效果
            if self.accent:
                # 主要按钮使用更深的颜色
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['primary_pressed']};
                        color: white;
                        border: none;
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-weight: bold;
                        font-size: 11px;
                        {SHADOWS['small']}
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['primary_pressed']};
                    }}
                """
            else:
                # 普通按钮使用 slightly darker 颜色
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['secondary_pressed']};
                        color: {COLORS['text']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 11px;
                        {SHADOWS['small']}
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['secondary_pressed']};
                    }}
                """
            self.setStyleSheet(pressed_style)
    
    def _on_released(self):
        """按钮释放时的处理"""
        # 恢复原始样式
        self.setStyleSheet(self.original_style)


# =============================================================================
# 更新现有控件以使用动画效果
# =============================================================================

# 更新ModernButton以继承自AnimatedButton
class ModernButton(AnimatedButton):
    """现代化的按钮，带有动画效果"""
    def __init__(self, text="", parent=None, accent=False, disabled=False):
        super().__init__(text, parent, accent, disabled)


# 更新EventEditButton以继承自AnimatedButton
class EventEditButton(AnimatedButton):
    """事件编辑对话框专用按钮，带有动画效果"""
    def __init__(self, text, accent=False, parent=None, fixed_width=None):
        super().__init__(text, parent, accent, False)  # disabled参数设为False
        
        # 设置固定高度
        self.setFixedHeight(20)
        
        # 设置固定宽度（如果提供）
        if fixed_width:
            self.setFixedWidth(fixed_width)
        
        # 获取基础按钮样式并添加显式的高度控制
        base_style = UnifiedStyleHelper.get_instance().get_button_style(accent)
        # 添加显式的高度控制样式，确保与其他UI元素高度一致
        enhanced_style = base_style + "\n"
        enhanced_style += "QPushButton {\n"
        enhanced_style += "    min-height: 20px;\n"
        enhanced_style += "    max-height: 20px;\n"
        enhanced_style += "}"
        self.setStyleSheet(enhanced_style)
        
        # 更新原始样式以包含高度控制
        self.original_style = enhanced_style
