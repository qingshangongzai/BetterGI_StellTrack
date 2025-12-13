# user_agreement.py
import sys
import os
import ctypes
import hashlib
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QDialog, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QComboBox, QPushButton, QTableWidget, 
                            QTableWidgetItem, QTextEdit, QFrame, QGroupBox, QGridLayout,
                            QHeaderView, QScrollArea, QSizePolicy, QSplitter,
                            QMessageBox, QStatusBar, QFileDialog, QTextBrowser,
                            QListView, QDialogButtonBox, QCheckBox, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import (QFont, QPalette, QColor, QIcon, QPixmap, QPainter, QPen, QCursor, 
                        QKeyEvent, QStandardItemModel, QStandardItem, QDesktopServices, QFontDatabase)

# 导入版本管理器
from main import version_manager

# 导入共享模块
from styles import DialogFactory, UnifiedStyleHelper

# =============================================================================
# 从styles模块导入样式和字体管理相关组件
# =============================================================================
from styles import (UnifiedStyleHelper, StyledDialog, StyledMainWindow, get_global_font_manager, 
                   ModernGroupBox, ModernLineEdit, ModernComboBox, ModernSpinBox, 
                   ModernDoubleSpinBox, ChineseMessageBox)
# 从utils模块导入通用功能
from utils import (VK_MAPPING, KEY_NAME_MAPPING, EVENT_TYPE_MAP,
                  convert_event_type_num_to_str_with_button, generate_key_event_name,
                  set_app_user_model_id, fix_windows_taskbar_icon_for_window, load_icon_universal, load_logo,
                  get_base_path, find_resource_file, get_resource_path, get_current_version, get_current_app_info)

# 导入窗口图标混入类
from styles import WindowIconMixin

# =============================================================================
# 单文件 EXE 图标加载修复
# =============================================================================

def load_icon_exe_safe():
    """兼容性函数，指向统一的图标加载函数"""
    return load_icon_universal()

# =============================================================================
# Windows 11 任务栏图标修复方案 - 简化版
# =============================================================================

# 任务栏图标修复函数已迁移到utils.py

# =============================================================================
# 全局常量和映射 - 保持不变
# =============================================================================

# COLORS 已从 styles 模块导入

# 以下全局常量已迁移到utils.py
# VK_MAPPING、KEY_NAME_MAPPING、EVENT_TYPE_MAP

# 以下内容已迁移到utils.py
# - KEY_NAME_MAPPING
# - EVENT_TYPE_MAP
# - 事件处理函数

# 事件处理函数已迁移到utils.py
# - convert_event_type_num_to_str_with_button
# - generate_key_event_name

# =============================================================================
# 样式工具类 - 保持不变
# =============================================================================

# UnifiedStyleHelper 已从 styles 模块导入

# =============================================================================
# 现代化控件类 - 保持不变
# =============================================================================

# 现代化控件类已迁移到styles.py

# 自定义消息框类已迁移到utils.py

# =============================================================================
# 用户协议HTML文件加载函数 - 保持不变
# =============================================================================

def load_user_agreement_html():
    """加载用户协议HTML文件内容"""
    try:
        # 查找用户协议HTML文件
        html_files = [
            "UserAgreement.html",
            "assets/UserAgreement.html",
            "docs/UserAgreement.html"
        ]
        
        for html_file in html_files:
            html_path = find_resource_file(html_file)
            if html_path and os.path.exists(html_path):
                with open(html_path, 'r', encoding='utf-8') as f:
                    return f.read()
        
        # 如果找不到HTML文件，返回错误信息
        error_html = """
        <div style="font-family: SourceHanSerifCN; font-size: 12px; line-height: 1.5; padding: 20px; text-align: center;">
            <h2 style="color: #d13438;">用户协议显示错误</h2>
            <p>无法加载用户协议文件，请更新软件到最新版本。</p>
            <p>如果您已经是最新版本，请联系开发者获取帮助。</p>
        </div>
        """
        return error_html
        
    except Exception as e:
        error_msg = f"加载用户协议HTML文件失败: {e}"
        print(f"[DEBUG] {error_msg}")
        
        error_html = f"""
        <div style="font-family: SourceHanSerifCN; font-size: 12px; line-height: 1.5; padding: 20px; text-align: center;">
            <h2 style="color: #d13438;">用户协议显示错误</h2>
            <p>无法加载用户协议文件：{str(e)}</p>
            <p>请更新软件到最新版本或联系开发者获取帮助。</p>
        </div>
        """
        return error_html

# =============================================================================
# 用户协议确认对话框 - 保持不变
# =============================================================================

class UserAgreementDialog(StyledDialog, WindowIconMixin):
    """用户协议确认对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("[DEBUG] 初始化用户协议对话框")
        # 直接设置对话框背景为纯白色
        self.setStyleSheet(f"QDialog {{ background-color: #ffffff; }}")
        self.setup_ui()
        # 设置图标修复 - 在窗口显示后调用
        self.setup_icon_fixing()
        

    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("用户协议与免责声明")
        self.setFixedSize(800, 600)
        
        # 设置窗口标志，删除最小化和最大化按钮
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 设置窗口图标
        self.setWindowIcon(load_icon_universal())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 创建头部区域
        self.create_header(layout)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        layout.addWidget(separator)
        
        # 创建协议内容区域
        self.create_agreement_content(layout)
        
        # 创建确认区域
        self.create_confirmation_area(layout)
        
        # 创建按钮区域
        self.create_buttons(layout)
        
        print("[DEBUG] 用户协议对话框UI设置完成")
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)  # 使用UnifiedStyleHelper统一设置字体
        header_layout.addWidget(logo_label)
        
        # 标题区域
        title_layout = QVBoxLayout()
        
        # 使用版本管理器获取应用信息
        app_info = get_current_app_info()
        
        # 中文标题 - 使用得意黑字体
        title_label = QLabel("用户服务协议与免责声明")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 14, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_layout.addWidget(title_label)
        
        # 副标题 - 使用SourceHanSerifCN字体
        subtitle_label = QLabel(f"首次使用请仔细阅读并同意用户服务协议与免责声明")
        font_manager = get_global_font_manager()
        subtitle_label.setFont(font_manager.get_source_han_font(11))
        subtitle_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_agreement_content(self, parent_layout):
        """创建协议内容区域"""
        # 创建文本浏览器（自带滚动条）
        self.agreement_browser = QTextBrowser()
        self.agreement_browser.setOpenExternalLinks(True)
        self.agreement_browser.setStyleSheet(UnifiedStyleHelper.get_instance().get_agreement_browser_style())
        
        # 设置协议内容
        self.set_agreement_content()
        
        parent_layout.addWidget(self.agreement_browser)
    
    def create_confirmation_area(self, parent_layout):
        """创建确认区域"""
        confirmation_layout = QHBoxLayout()
        
        # 确认复选框
        self.agree_checkbox = QCheckBox("我已仔细阅读并同意以上用户服务协议与免责声明")
        font_manager = get_global_font_manager()
        self.agree_checkbox.setFont(font_manager.get_source_han_font(10))
        self.agree_checkbox.stateChanged.connect(self.on_agreement_changed)
        confirmation_layout.addWidget(self.agree_checkbox)
        
        parent_layout.addLayout(confirmation_layout)
    
    def create_buttons(self, parent_layout):
        """创建按钮区域"""
        # 获取字体管理器
        font_manager = get_global_font_manager()
        
        # 使用DialogFactory创建按钮布局
        button_layout = DialogFactory.create_ok_cancel_buttons(
            parent=self,
            on_ok=self.accept,
            on_cancel=self.reject,
            ok_text="同意并继续",
            cancel_text="不同意"
        )
        
        # 获取按钮并设置字体
        ok_btn = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        cancel_btn = button_layout.itemAt(2).widget()
        
        ok_btn.setFont(font_manager.get_source_han_font(10))
        cancel_btn.setFont(font_manager.get_source_han_font(10))
        
        self.agree_button = ok_btn
        self.disagree_button = cancel_btn
        
        self.agree_button.setEnabled(False)  # 初始禁用
        
        parent_layout.addLayout(button_layout)
    
    def set_agreement_content(self):
        """设置协议内容 - 从HTML文件加载"""
        html_content = load_user_agreement_html()
        self.agreement_browser.setHtml(html_content)
    
    def on_agreement_changed(self, state):
        """协议复选框状态改变"""
        self.agree_button.setEnabled(state == Qt.CheckState.Checked.value)
        print(f"[DEBUG] 用户协议复选框状态: {'同意' if state == Qt.CheckState.Checked.value else '未同意'}")
    

    


# =============================================================================
# 用户协议窗口 - 保持不变
# =============================================================================

class UserAgreementWindow(StyledMainWindow, WindowIconMixin):
    """用户协议窗口"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        # 直接设置窗口背景为纯白色
        self.setStyleSheet(f"QMainWindow {{ background-color: #ffffff; }}")
        self.setup_ui()
        # 设置图标修复 - 在窗口显示后调用
        self.setup_icon_fixing()
        

    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("用户服务协议与免责声明")
        self.setFixedSize(800, 600)
        
        # 设置窗口标志，删除最小化和最大化按钮
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | 
                           Qt.WindowType.WindowTitleHint | Qt.WindowType.WindowCloseButtonHint)
        
        # 设置窗口图标
        self.setWindowIcon(load_icon_universal())
        
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # 创建头部区域
        self.create_header(main_layout)
        
        # 创建分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['border']};")
        main_layout.addWidget(separator)
        
        # 创建协议内容区域
        self.create_agreement_content(main_layout)
        
        # 创建按钮区域
        self.create_buttons(main_layout)
        
    def create_header(self, parent_layout):
        """创建头部区域"""
        header_layout = QHBoxLayout()
        
        # Logo
        logo_label = QLabel()
        logo_pixmap = load_logo()
        if logo_pixmap:
            logo_label.setPixmap(logo_pixmap)
        else:
            logo_label.setText("⚙️")
            UnifiedStyleHelper.get_instance().set_smiley_font(logo_label, 20)  # 使用UnifiedStyleHelper统一设置字体
        header_layout.addWidget(logo_label)
        
        # 标题区域
        title_layout = QVBoxLayout()
        
        # 使用版本管理器获取应用信息
        app_info = version_manager.get_app_info()
        
        # 中文标题 - 使用得意黑字体
        title_label = QLabel("用户服务协议与免责声明")
        UnifiedStyleHelper.get_instance().set_smiley_font(title_label, 14, QFont.Weight.Bold)  # 使用UnifiedStyleHelper统一设置字体
        title_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['primary']};")
        title_layout.addWidget(title_label)
        
        # 副标题 - 使用SourceHanSerifCN字体
        subtitle_label = QLabel(f"请仔细阅读{app_info['name']}的用户服务协议与免责声明")
        font_manager = get_global_font_manager()
        subtitle_label.setFont(font_manager.get_source_han_font(11))
        subtitle_label.setStyleSheet(f"color: {UnifiedStyleHelper.get_instance().COLORS['text']};")
        title_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        parent_layout.addLayout(header_layout)
    
    def create_agreement_content(self, parent_layout):
        """创建协议内容区域"""
        # 创建文本浏览器（自带滚动条）
        self.agreement_browser = QTextBrowser()
        self.agreement_browser.setOpenExternalLinks(True)
        self.agreement_browser.setStyleSheet(UnifiedStyleHelper.get_instance().get_agreement_browser_style())
        
        # 设置协议内容
        self.set_agreement_content()
        
        parent_layout.addWidget(self.agreement_browser)
    
    def create_buttons(self, parent_layout):
        """创建按钮区域"""
        # 获取字体管理器
        font_manager = get_global_font_manager()
        
        # 使用DialogFactory创建关闭按钮布局
        button_layout = DialogFactory.create_close_button(
            parent=self,
            on_close=self.close,
            text="关闭"
        )
        
        # 获取按钮并设置字体
        close_button = button_layout.itemAt(1).widget()  # itemAt(0)是stretch
        close_button.setFont(font_manager.get_source_han_font(10))
        
        parent_layout.addLayout(button_layout)
    
    def set_agreement_content(self):
        """设置协议内容 - 从HTML文件加载"""
        html_content = load_user_agreement_html()
        self.agreement_browser.setHtml(html_content)
    


def check_user_agreement():
    """检查用户协议，如果用户不同意则退出程序"""
    try:
        print("[DEBUG] 开始检查用户协议")
    except:
        print("[DEBUG] 开始检查用户协议")
    
    # 检查是否已经同意过协议
    try:
        # 获取程序所在目录（对于打包环境，是exe所在目录；开发环境，是脚本所在目录）
        if getattr(sys, 'frozen', False):
            # 打包后的环境，状态文件保存在exe所在目录
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = get_base_path()

        # 使用版本管理器获取应用信息
        app_info = version_manager.get_app_info()

        # 同意状态文件路径
        agreement_file = os.path.join(base_path, f"{app_info['name_en']}_agreement_accepted.txt")
        
        print(f"[DEBUG] 检查协议文件: {agreement_file}")
        print(f"[DEBUG] 协议文件存在: {os.path.exists(agreement_file)}")
        
        # 获取当前用户协议文件的哈希值（使用SHA256）
        current_agreement_hash = ""
        agreement_html_file = find_resource_file("UserAgreement.html")
        
        if agreement_html_file and os.path.exists(agreement_html_file):
            # 计算当前协议文件的SHA256哈希值
            with open(agreement_html_file, 'rb') as f:
                current_agreement_hash = hashlib.sha256(f.read()).hexdigest()
            print(f"[DEBUG] 当前协议文件哈希: {current_agreement_hash}")
        else:
            print("[DEBUG] 未找到用户协议HTML文件")
        
        # 计算应用程序目录路径的SHA256哈希值
        current_path_hash = hashlib.sha256(base_path.encode('utf-8')).hexdigest()
        print(f"[DEBUG] 当前应用目录哈希: {current_path_hash}")
        
        # 检查是否需要重新确认协议
        need_reconfirm = False
        
        if os.path.exists(agreement_file):
            # 读取已保存的协议信息
            try:
                with open(agreement_file, 'r', encoding='utf-8') as f:
                    saved_content = f.read()
                
                # 检查协议内容是否有变化
                if current_agreement_hash and "协议哈希:" in saved_content:
                    # 提取保存的协议哈希
                    saved_hash = saved_content.split("协议哈希:")[1].split("\n")[0].strip()
                    
                    # 检查是否有路径哈希
                    if "目录路径哈希:" in saved_content:
                        saved_path_hash = saved_content.split("目录路径哈希:")[1].split("\n")[0].strip()
                        
                        # 同时检查协议哈希和路径哈希
                        if saved_hash != current_agreement_hash or saved_path_hash != current_path_hash:
                            need_reconfirm = True
                            print(f"[DEBUG] 协议内容或目录路径已更新，需要重新确认")
                            print(f"[DEBUG] 保存的协议哈希: {saved_hash}")
                            print(f"[DEBUG] 当前协议哈希: {current_agreement_hash}")
                            print(f"[DEBUG] 保存的路径哈希: {saved_path_hash}")
                            print(f"[DEBUG] 当前路径哈希: {current_path_hash}")
                        else:
                            print("[DEBUG] 协议内容和目录路径未变化，无需重新确认")
                    else:
                        # 兼容旧版本：没有路径哈希记录，需要重新确认
                        need_reconfirm = True
                        print("[DEBUG] 旧版本协议文件，需要重新确认以记录路径哈希")
                else:
                    # 兼容旧版本：没有哈希值记录，需要重新确认
                    need_reconfirm = True
                    print("[DEBUG] 旧版本协议文件，需要重新确认以记录哈希值")
                        
            except Exception as e:
                print(f"[DEBUG] 读取协议文件失败: {e}")
                need_reconfirm = True
        else:
            # 首次运行
            need_reconfirm = True
            print("[DEBUG] 首次运行，需要确认协议")
        
        if not need_reconfirm:
            print("[DEBUG] 用户已同意过当前版本的协议，直接返回")
            return True
        
        # 需要重新确认协议
        print("[DEBUG] 需要用户重新确认协议")
        
        # 在创建对话框之前设置AppUserModelID
        if os.name == 'nt':
            set_app_user_model_id()
        
        # 显示用户协议对话框
        print("[DEBUG] 显示用户协议对话框")
        agreement_dialog = UserAgreementDialog()
        
        # 修复：确保对话框可以正常关闭
        agreement_dialog.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        result = agreement_dialog.exec()
        print(f"[DEBUG] 用户协议对话框返回结果: {result}")
        
        if result == QDialog.DialogCode.Accepted:
            # 用户同意协议，创建标记文件
            print("[DEBUG] 用户同意协议，创建标记文件")
            try:
                # 确保目录存在
                os.makedirs(base_path, exist_ok=True)
                
                # 写入协议信息，包含协议哈希和目录路径哈希
                with open(agreement_file, 'w', encoding='utf-8') as f:
                    content = f"{app_info['name']} 用户协议同意时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    if current_agreement_hash:
                        content += f"协议哈希: {current_agreement_hash}\n"
                        content += f"目录路径哈希: {current_path_hash}\n"
                    f.write(content)
                print(f"[DEBUG] 协议文件已创建: {agreement_file}")
                return True
            except Exception as e:
                print(f"[DEBUG] 创建协议同意文件失败: {e}")
                # 即使文件创建失败，也允许继续使用
                return True
        else:
            # 用户不同意协议
            print("[DEBUG] 用户不同意协议")
            ChineseMessageBox.show_info(None, "提示", f"您需要同意用户协议才能使用本软件。")
            return False
            
    except Exception as e:
        print(f"[DEBUG] 检查用户协议时出错: {e}")
        import traceback
        traceback.print_exc()
        # 出错时默认允许继续使用
        return True
