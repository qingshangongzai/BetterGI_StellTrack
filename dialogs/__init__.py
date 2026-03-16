# 对话框模块

# 统一导出所有对话框类

from styles import BaseFramelessDialog
from .batch_dialog import BatchEditDialog
from .debug_dialog import CustomInputDialog
from .event_dialogs import (EventEditDialog, PasteOptionsDialog, 
                            SimpleCoordinateCapture, DeleteOptionsDialog)
from .update_dialog import UpdateDialog
from .time_analysis import EventTimeAnalyzerDialog
from .user_agreement import (UserAgreementDialog, UserAgreementWindow, 
                             check_user_agreement, load_user_agreement_html)
from .debug_tools import (PasswordDialog, SafeDebugWindow, DebugWindow, 
                         SafeDebugLogger, get_global_debug_logger, 
                         initialize_global_logging)
from .about_window import (AboutWindowQt, 
                           UserAgreementWindow as AboutUserAgreementWindow)

__all__ = [
    'BaseFramelessDialog',
    'BatchEditDialog',
    'CustomInputDialog',
    'EventEditDialog',
    'PasteOptionsDialog',
    'SimpleCoordinateCapture',
    'DeleteOptionsDialog',
    'UpdateDialog',
    'EventTimeAnalyzerDialog',
    'UserAgreementDialog',
    'UserAgreementWindow',
    'check_user_agreement',
    'load_user_agreement_html',
    'PasswordDialog',
    'SafeDebugWindow',
    'DebugWindow',
    'SafeDebugLogger',
    'get_global_debug_logger',
    'initialize_global_logging',
    'AboutWindowQt',
    'AboutUserAgreementWindow',
]
