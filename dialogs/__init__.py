# 对话框模块

# 统一导出所有对话框类

from .batch_dialog import BatchEditDialog
from .debug_dialog import CustomInputDialog
from .event_dialogs import EventEditDialog, PasteOptionsDialog, SimpleCoordinateCapture, DeleteOptionsDialog

__all__ = [
    'BatchEditDialog',
    'CustomInputDialog',
    'EventEditDialog',
    'PasteOptionsDialog',
    'SimpleCoordinateCapture',
    'DeleteOptionsDialog',
]
