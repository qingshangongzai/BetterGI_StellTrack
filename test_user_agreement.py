# 测试用户协议窗口任务栏图标显示
import sys
import os

# 设置应用程序路径
from main import setup_exe_environment
setup_exe_environment()

# 导入PyQt模块
from PyQt6.QtWidgets import QApplication

# 导入用户协议对话框
from user_agreement import UserAgreementDialog

# 导入日志初始化
from debug_tools import initialize_global_logging
initialize_global_logging()

# 创建应用程序
app = QApplication(sys.argv)

# 设置应用程序信息
from main import version_manager
app_info = version_manager.get_app_info()
app.setApplicationName(app_info["name"])
app.setApplicationVersion(version_manager.get_version())
app.setOrganizationName(app_info["company"])

# 在Windows上设置AppUserModelID
if os.name == 'nt':
    from utils import set_app_user_model_id
    set_app_user_model_id()

# 直接显示用户协议对话框
dialog = UserAgreementDialog()
dialog.show()

# 运行应用程序主循环
sys.exit(app.exec())