# styles.py - 全局样式和字体管理模块
import os
import sys
from PyQt6.QtGui import QFont, QFontDatabase, QIcon, QPixmap, QPainter, QColor, QStandardItemModel, QStandardItem, QPainterPath, QPen, QRegion, QBitmap, QImage
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QEvent, QRectF, QRect, QPropertyAnimation
from PyQt6.QtWidgets import QGroupBox, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QMessageBox, QListView, QPushButton, QWidget, QDialog, QMainWindow, QHBoxLayout, QVBoxLayout, QLabel, QMenu, QMenuBar

# 导入资源管理器函数
from utils import get_base_path, find_resource_file, get_resource_path, load_icon_universal, create_fallback_icon, fix_windows_taskbar_icon_for_window

# =============================================================================
# 全局字体管理器
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


class FadeInWindowMixin:
    """窗口淡入/淡出动画混入类，用于在打开和关闭时添加简单的过渡动画"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._first_show_animation_done = False
        self._closing_via_animation = False
        # 初始设置为完全透明，避免窗口创建时的闪烁
        self.setWindowOpacity(0.0)
    
    def showEvent(self, event):
        """在窗口首次显示时播放淡入动画"""
        if not self._first_show_animation_done:
            self._first_show_animation_done = True
            try:
                self._fade_anim = QPropertyAnimation(self, b"windowOpacity", self)
                self._fade_anim.setDuration(180)
                self._fade_anim.setStartValue(0.0)
                self._fade_anim.setEndValue(1.0)
                self._fade_anim.start()
            except Exception:
                # 动画失败时不影响窗口正常显示
                self.setWindowOpacity(1.0)
        
        super().showEvent(event)
    
    def closeEvent(self, event):
        """在窗口关闭时播放淡出动画"""
        # 避免递归触发关闭动画
        if self._closing_via_animation:
            return super().closeEvent(event)
        
        # 拦截第一次关闭事件，先执行淡出动画
        event.ignore()
        self._closing_via_animation = True
        try:
            start_opacity = self.windowOpacity()
            self._fade_out_anim = QPropertyAnimation(self, b"windowOpacity", self)
            self._fade_out_anim.setDuration(180)
            self._fade_out_anim.setStartValue(start_opacity)
            self._fade_out_anim.setEndValue(0.0)
            
            def _on_fade_out_finished():
                try:
                    super(type(self), self).close()
                finally:
                    self._closing_via_animation = False
            
            self._fade_out_anim.finished.connect(_on_fade_out_finished)
            self._fade_out_anim.start()
        except Exception:
            # 动画失败时直接关闭
            self._closing_via_animation = False
            super().closeEvent(event)


class WindowIconMixin:
    """窗口图标修复混入类，提供统一的任务栏图标修复功能"""
    
    # 信号：图标修复完成
    icon_fixed = pyqtSignal(bool)
    
    def __init__(self, *args, **kwargs):
        """初始化混入类"""
        super().__init__(*args, **kwargs)
        self._icon_fixed = False  # 防止重复修复的标志
        self._fix_timer = None  # 定时器引用
    
    def setup_icon_fixing(self, delay_ms=100):
        """
        设置图标修复，在窗口显示后调用
        
        Args:
            delay_ms: 延迟时间（毫秒），默认100ms
        """
        # 确保属性已初始化
        if not hasattr(self, '_icon_fixed'):
            self._icon_fixed = False
        if not hasattr(self, '_fix_timer'):
            self._fix_timer = None
            
        if self._icon_fixed:
            return
            
        if os.name == 'nt':
            # 使用定时器延迟调用，确保窗口已经完全显示
            self._fix_timer = QTimer()
            self._fix_timer.setSingleShot(True)
            self._fix_timer.timeout.connect(self._fix_icon_safe)
            self._fix_timer.start(delay_ms)
    
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
        # 确保属性已初始化
        if not hasattr(self, '_icon_fixed'):
            self._icon_fixed = False
        if not hasattr(self, '_fix_timer'):
            self._fix_timer = None
        return self._fix_icon_safe()
    
    def _fix_taskbar_icon_safe(self):
        """
        安全修复任务栏图标 - 兼容旧接口
        
        为了保持向后兼容性，提供此方法
        """
        return self._fix_icon_safe()
    
    def cleanup_icon_fixing(self):
        """清理图标修复相关的资源"""
        if hasattr(self, '_fix_timer') and self._fix_timer and self._fix_timer.isActive():
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
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 11px;
                    min-height: 20px;
                    max-height: 20px;
                    {self.SHADOWS['small']}

                }}
            """
        
        if accent:
            return f"""
                QPushButton {{
                    background-color: {self.COLORS['primary']};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-weight: bold;
                    font-size: 11px;
                    min-height: 20px;
                    max-height: 20px;
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
                    border-radius: 8px;
                    padding: 6px 12px;
                    font-size: 11px;
                    min-height: 20px;
                    max-height: 20px;
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
                border-radius: 8px;
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
                border-radius: 8px;
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
                border-radius: 8px; 
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
                border-radius: 8px;
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
                background-color: #CAE9FF;
            }}
            QHeaderView::section {{ 
                background-color: #ffffff;
                padding: 4px 10px;
                border: none;
                border-right: 1px solid #e0e0e0;
                border-bottom: 1px solid #e0e0e0;
                font-weight: bold;
                font-size: 12px;
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
                border-radius: 8px;
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
                border-radius: 8px;
                padding: 6px;
            }}
        """
    
    def get_agreement_browser_style(self):
        """获取协议浏览器样式"""
        return f"""
            QTextBrowser {{ 
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
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
                border-radius: 8px;
                padding: 10px;
                font-family: SourceHanSerifCN;
                font-size: 12px;
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
                border-radius: 8px;
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
                border-radius: 8px;
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
                border-top-right-radius: 7px;
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
                border-bottom-right-radius: 7px;
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
    
    def get_progress_bar_style(self):
        """获取进度条样式"""
        return f"""
            QProgressBar {{
                border: 1px solid {self.COLORS['border']};
                border-radius: 4px;
                text-align: center;
                background-color: #f0f0f0;
                font-size: 10px;
            }}
            QProgressBar::chunk {{
                background-color: {self.COLORS['primary']};
                border-radius: 3px;
            }}
        """
    
    def get_text_edit_style(self):
        """获取文本编辑框样式"""
        return f"""
            QTextEdit {{
                background-color: #ffffff;
                border: 1px solid {self.COLORS['border_light']};
                border-radius: 8px;
                padding: 8px;
                font-size: 10px;
                line-height: 1.3;
                {self.SHADOWS['small']}
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
                border-radius: 8px;
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
                border-radius: 8px;
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
                border-radius: 8px;
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
                border-radius: 8px; 
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
        """获取滚动条样式 - Fluent Design风格"""
        return """
            /* 垂直滚动条 */
            QScrollBar:vertical {
                background-color: transparent;
                width: 10px;
                margin: 10px 0;
            }
            
            QScrollBar::groove:vertical {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
                margin: 0 4px;
            }
            
            QScrollBar::handle:vertical {
                background-color: %s;
                border-radius: 5px;
                min-height: 20px;
                margin: 0 4px;
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
                background-color: transparent;
                height: 10px;
                margin: 0 10px;
            }
            
            QScrollBar::groove:horizontal {
                background-color: rgba(0, 0, 0, 0.08);
                border-radius: 5px;
                margin: 4px 0;
            }
            
            QScrollBar::handle:horizontal {
                background-color: %s;
                border-radius: 5px;
                min-width: 20px;
                margin: 4px 0;
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
            
            /* 滚动区域 */
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            
            QScrollArea > QWidget > QWidget {
                background-color: transparent;
            }
            
            /* 滚动条容器 */
            QAbstractScrollArea {
                background-color: transparent;
            }
        """ % (
            self.COLORS['border'],
            self.COLORS['primary_hover'],
            self.COLORS['primary_pressed'],
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
    
    def get_absolute_time_edit_style(self):
        """获取绝对偏移时间显示框样式"""
        return f"""
            QLineEdit {{ 
                border: 1px solid {self.COLORS['border']}; 
                border-radius: 8px;
                padding: 6px 8px;
                background-color: {self.COLORS['bg']}; /* 使用纯白色背景 */
                font-size: 11px;
                selection-background-color: {self.COLORS['primary']};
                {self.SHADOWS['small']}
                min-height: 20px;
                max-height: 20px;
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
                border-radius: 8px;
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
                border-top-right-radius: 7px;
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
                border-bottom-right-radius: 7px;
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
    
    def get_checkbox_style(self):
        """获取复选框样式
        
        使用简洁的样式，让Qt使用系统默认的勾选标记
        
        Returns:
            对应的样式字符串
        """
        return f"""
            QCheckBox {{
                color: {self.COLORS['text']};
                spacing: 6px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
        """
    
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
        
        # 构建全局样式表
        global_stylesheet = f"""
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
                border-radius: 8px;
                padding: 4px;
            }}
            QMenuBar::item {{
                padding: 4px 8px;
                border-radius: 8px;
            }}
            QMenuBar::item:selected {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QMenu {{ 
                background-color: {self.COLORS['bg']};
                border: 1px solid {self.COLORS['border']};
                border-radius: 8px;
                padding: 6px;
                {self.SHADOWS['small']}
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 8px;
                margin: 2px 2px;
            }}
            QMenu::item:selected {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {self.COLORS['border_light']};
                margin: 4px 8px;
            }}
            QAction::hover {{
                background-color: {self.COLORS['primary_hover']};
                color: white;
            }}
            
            /* 复选框样式 - 使用系统默认勾选标记 */
            QCheckBox {{
                color: {self.COLORS['text']};
                spacing: 6px;
            }}
            
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
            }}
            
            /* 滚动条样式 */
            {scroll_bar_style}
        """
        
        # 尝试在QApplication实例上设置样式表
        if q_app and hasattr(q_app, 'setStyleSheet'):
            q_app.setStyleSheet(global_stylesheet)
        # 如果QApplication实例不可用，尝试在传入的app对象上设置
        elif hasattr(app, 'setStyleSheet'):
            app.setStyleSheet(global_stylesheet)

# =============================================================================
# 现代化控件类
# =============================================================================

class ModernMenu(QMenu):
    """现代化的菜单，使用 setMask 修复 Windows 系统下圆角显示问题
    
    通过设置窗口遮罩为圆角形状，直接裁剪窗口。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置窗口标志
        self.setWindowFlags(
            Qt.WindowType.Popup | 
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.NoDropShadowWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        
        # 应用菜单样式
        style_helper = UnifiedStyleHelper.get_instance()
        menu_style = f"""
            QMenu {{ 
                background-color: {style_helper.COLORS['bg']};
                border: 1px solid {style_helper.COLORS['border']};
                padding: 6px;
            }}
            QMenu::item {{
                padding: 6px 16px;
                border-radius: 8px;
                margin: 2px 2px;
            }}
            QMenu::item:selected {{
                background-color: {style_helper.COLORS['primary_hover']};
                color: white;
            }}
            QMenu::separator {{
                height: 1px;
                background-color: {style_helper.COLORS['border_light']};
                margin: 4px 8px;
            }}
        """
        self.setStyleSheet(menu_style)
    
    def showEvent(self, event):
        """菜单显示时设置圆角遮罩"""
        super().showEvent(event)
        
        # 在 Windows 上使用 Windows API 移除窗口边框
        if os.name == 'nt':
            try:
                import ctypes
                
                # 获取窗口句柄
                hwnd = int(self.winId())
                
                # Windows API 常量
                GWL_STYLE = -16
                GWL_EXSTYLE = -20
                WS_POPUP = 0x80000000
                WS_BORDER = 0x00800000
                WS_DLGFRAME = 0x00400000
                WS_THICKFRAME = 0x00040000
                WS_EX_DLGMODALFRAME = 0x00000001
                WS_EX_WINDOWEDGE = 0x00000100
                WS_EX_CLIENTEDGE = 0x00000200
                WS_EX_STATICEDGE = 0x00020000
                
                # 获取当前窗口样式
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                # 移除所有边框样式
                style &= ~(WS_BORDER | WS_DLGFRAME | WS_THICKFRAME)
                style |= WS_POPUP
                ex_style &= ~(WS_EX_DLGMODALFRAME | WS_EX_WINDOWEDGE | WS_EX_CLIENTEDGE | WS_EX_STATICEDGE)
                
                # 设置新样式
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_STYLE, style)
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex_style)
                
                # 刷新窗口
                SWP_FRAMECHANGED = 0x0020
                SWP_NOMOVE = 0x0002
                SWP_NOSIZE = 0x0001
                SWP_NOZORDER = 0x0004
                ctypes.windll.user32.SetWindowPos(
                    hwnd, 0, 0, 0, 0, 0,
                    SWP_FRAMECHANGED | SWP_NOMOVE | SWP_NOSIZE | SWP_NOZORDER
                )
            except Exception:
                pass
        
        # 设置圆角遮罩 - 使用更简单可靠的方法
        QTimer.singleShot(0, self._update_rounded_mask)
    
    def resizeEvent(self, event):
        """窗口大小改变时更新遮罩"""
        super().resizeEvent(event)
        # 延迟更新遮罩，确保窗口大小已经确定
        QTimer.singleShot(0, self._update_rounded_mask)
    
    def _update_rounded_mask(self):
        """更新圆角遮罩，使用 QBitmap 创建光滑的圆角"""
        if self.width() <= 0 or self.height() <= 0:
            return
            
        # 创建位图遮罩
        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.GlobalColor.color0)  # 透明
        
        # 创建画家绘制圆角
        painter = QPainter(bitmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setBrush(Qt.GlobalColor.color1)  # 不透明
        painter.setPen(Qt.PenStyle.NoPen)
        
        # 绘制圆角矩形
        rect = QRectF(0, 0, self.width(), self.height())
        painter.drawRoundedRect(rect, 8.0, 8.0)
        painter.end()
        
        # 设置遮罩
        self.setMask(bitmap)
    
    def addMenu(self, *args):
        """重写 addMenu 方法，确保子菜单也使用 ModernMenu
        
        支持两种调用方式：
        1. addMenu(title: str) -> QMenu
        2. addMenu(menu: QMenu) -> QAction
        """
        if len(args) == 1:
            if isinstance(args[0], str):
                # 创建新子菜单，使用 ModernMenu
                submenu = ModernMenu(self)
                submenu.setTitle(args[0])
                action = super().addMenu(submenu)
                return submenu
            elif isinstance(args[0], QMenu):
                # 添加已有菜单，设置窗口标志
                menu = args[0]
                menu.setWindowFlags(
                    Qt.WindowType.Popup | 
                    Qt.WindowType.FramelessWindowHint |
                    Qt.WindowType.NoDropShadowWindowHint
                )
                menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                return super().addMenu(menu)
        return super().addMenu(*args)

class ModernMenuBar(QMenuBar):
    """现代化的菜单栏，为其创建的菜单自动应用无边框样式
    
    重写 addMenu 方法，确保所有菜单都使用 ModernMenu 类，
    自动应用无边框和透明背景属性。
    """
    def __init__(self, parent=None):
        super().__init__(parent)
    
    def addMenu(self, *args):
        """重写 addMenu 方法，创建 ModernMenu 实例
        
        支持两种调用方式：
        1. addMenu(title: str) -> QMenu
        2. addMenu(menu: QMenu) -> QAction
        """
        if len(args) == 1:
            if isinstance(args[0], str):
                # 创建新菜单，使用 ModernMenu
                menu = ModernMenu(self)
                menu.setTitle(args[0])
                action = super().addMenu(menu)
                return menu
            elif isinstance(args[0], QMenu):
                # 添加已有菜单，设置窗口标志
                menu = args[0]
                menu.setWindowFlags(
                    Qt.WindowType.Popup | 
                    Qt.WindowType.FramelessWindowHint |
                    Qt.WindowType.NoDropShadowWindowHint
                )
                menu.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
                return super().addMenu(menu)
        return super().addMenu(*args)

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
    def __init__(self, parent=None, width=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setButtonSymbols(QDoubleSpinBox.ButtonSymbols.PlusMinus)
        if width:
            self.setFixedWidth(width)
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
        
        # 设置按钮统一宽度为100px
        ok_btn.setFixedWidth(100)
        cancel_btn.setFixedWidth(100)
        
        ok_btn.clicked.connect(on_ok)
        cancel_btn.clicked.connect(on_cancel)
        
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
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
        
        # 设置按钮统一宽度为100px
        close_btn.setFixedWidth(100)
        
        close_btn.clicked.connect(on_close)
        
        button_layout.addWidget(close_btn)
        button_layout.addStretch()
        
        return button_layout

# =============================================================================
# 自定义消息框类
# =============================================================================

class AnimatedDialog(FadeInWindowMixin, QDialog):
    """带淡入淡出动画的基础对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)


class ChineseMessageBox:
    """自定义消息框，确保按钮显示中文"""
    
    @staticmethod
    def show_warning(parent, title, message):
        """显示警告消息"""
        # 创建自定义对话框
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)
        
        # 设置对话框样式
        dialog.setStyleSheet(f"QDialog {{ background-color: white; border-radius: 8px; }}")
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加消息内容
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("QLabel { font-size: 13px; color: #323130; }")
        layout.addWidget(message_label)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建按钮
        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)  # 设置按钮统一宽度为100px
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)
        
        # 添加按钮到布局
        button_layout.addWidget(ok_button)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 显示对话框
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted
    
    @staticmethod
    def show_error(parent, title, message):
        """显示错误消息"""
        # 创建自定义对话框
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)
        
        # 设置对话框样式
        dialog.setStyleSheet(f"QDialog {{ background-color: white; border-radius: 8px; }}")
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加消息内容
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("QLabel { font-size: 13px; color: #323130; }")
        layout.addWidget(message_label)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建按钮
        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)  # 设置按钮统一宽度为100px
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)
        
        # 添加按钮到布局
        button_layout.addWidget(ok_button)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec()
    
    @staticmethod
    def show_info(parent, title, message):
        """显示信息消息"""
        # 创建自定义对话框
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)
        
        # 设置对话框样式
        dialog.setStyleSheet(f"QDialog {{ background-color: white; border-radius: 8px; }}")
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加消息内容
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("QLabel { font-size: 13px; color: #323130; }")
        layout.addWidget(message_label)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # 创建按钮
        ok_button = QPushButton("确定")
        ok_button.setFixedWidth(100)  # 设置按钮统一宽度为100px
        ok_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        ok_button.clicked.connect(dialog.accept)
        
        # 添加按钮到布局
        button_layout.addWidget(ok_button)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 显示对话框
        dialog.exec()
    
    @staticmethod
    def show_question(parent, title, message):
        """显示询问消息"""
        # 创建自定义对话框
        dialog = AnimatedDialog(parent)
        dialog.setWindowTitle(title)
        dialog.setWindowIcon(load_icon_universal())
        dialog.setMinimumWidth(200)
        dialog.setMaximumWidth(400)
        
        # 设置对话框样式
        dialog.setStyleSheet(f"QDialog {{ background-color: white; border-radius: 8px; }}")
        
        # 创建布局
        layout = QVBoxLayout(dialog)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # 添加消息内容
        message_label = QLabel(message)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        message_label.setStyleSheet("QLabel { font-size: 13px; color: #323130; }")
        layout.addWidget(message_label)
        
        # 添加按钮布局
        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        button_layout.setSpacing(10)
        
        # 创建按钮
        yes_button = QPushButton("是")
        yes_button.setFixedWidth(100)  # 设置按钮统一宽度为100px
        yes_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style(accent=True))
        yes_button.clicked.connect(dialog.accept)
        
        no_button = QPushButton("否")
        no_button.setFixedWidth(100)  # 设置按钮统一宽度为100px
        no_button.setStyleSheet(UnifiedStyleHelper.get_instance().get_button_style())
        no_button.clicked.connect(dialog.reject)
        
        # 添加按钮到布局
        button_layout.addWidget(yes_button)
        button_layout.addWidget(no_button)
        
        # 添加按钮布局到主布局
        layout.addLayout(button_layout)
        
        # 显示对话框
        result = dialog.exec()
        return result == QDialog.DialogCode.Accepted


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
                # 主要按钮使用更深的颜色，并减少padding实现缩小效果
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['primary_pressed']};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-weight: bold;
                        font-size: 11px;
                        {SHADOWS['small']}
                        min-height: 18px;
                        max-height: 18px;
                    }}
                    QPushButton:hover {{
                        background-color: {COLORS['primary_pressed']};
                    }}
                """
            else:
                # 普通按钮使用 slightly darker 颜色，并减少padding实现缩小效果
                pressed_style = f"""
                    QPushButton {{
                        background-color: {COLORS['secondary_pressed']};
                        color: {COLORS['text']};
                        border: 1px solid {COLORS['border']};
                        border-radius: 8px;
                        padding: 5px 10px;
                        font-size: 11px;
                        {SHADOWS['small']}
                        min-height: 18px;
                        max-height: 18px;
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
