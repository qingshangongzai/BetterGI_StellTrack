"""样式模块，统一导出所有样式相关的类和函数

本模块提供了应用程序的样式管理功能，包括字体管理、主题管理、控件样式和对话框样式。
"""

# 导入字体管理模块
from .fonts import GlobalFontManager, get_global_font_manager

# 导入主题管理模块
from .themes import (
    UnifiedStyleHelper,
    DarkStyleHelper,
    LIGHT_COLORS,
    DARK_COLORS,
    COLORS,
    SHADOWS
)

# 导入控件样式模块
from .widgets import (
    StyledWidget,
    StyledDialog,
    StyledMainWindow,
    StyleManager,
    TitleBarThemeMixin,
    FadeInWindowMixin,
    WindowIconMixin,
    ModernMenu,
    ModernMenuBar,
    ModernGroupBox,
    ModernLineEdit,
    ModernComboBox,
    ModernSpinBox,
    ModernDoubleSpinBox,
    CenteredComboBox,
    CenteredLineEdit,
    TimeOffsetSpinBox,
    AnimatedButton,
    ModernButton,
    EventEditButton
)

# 导入对话框样式模块
from .dialogs import (
    DialogFactory,
    AnimatedDialog,
    ChineseMessageBox
)

__version__ = "2.0.0"
