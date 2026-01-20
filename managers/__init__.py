"""管理器模块

提供应用程序的核心管理功能，包括：
- 菜单管理器：负责菜单栏创建和菜单状态管理
- 状态管理器：负责状态保存、加载、撤销和重做功能
- 事件管理器：处理事件的添加、编辑、删除等操作
- 脚本管理器：负责脚本的生成和保存
"""

# 统一导出所有管理器类
# 项目模块导入
from .menu_manager import MenuManager
from .state_manager import StateManager
from .event_manager import EventManager
from .script_manager import ScriptManager

__all__ = [
    'MenuManager',
    'StateManager',
    'EventManager',
    'ScriptManager',
]
