"""UI模块

提供应用程序的UI组件和面板，包括：
- 自定义控件：现代化表格、标题栏等
- 面板组件：设置面板、操作面板、统计信息面板
"""

# 统一导出UI相关的组件和面板
from .widgets import ModernTableWidget, HeaderWidget
from .panels import SettingsPanel, OperationsPanel, StatsPanel

__all__ = [
    'ModernTableWidget',
    'HeaderWidget',
    'SettingsPanel',
    'OperationsPanel',
    'StatsPanel',
]
