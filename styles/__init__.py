from .fonts import GlobalFontManager, get_global_font_manager

from .themes import (
    UnifiedStyleHelper,
    DarkStyleHelper,
    LIGHT_COLORS,
    DARK_COLORS,
    COLORS,
    SHADOWS
)

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

from .dialogs import (
    DialogFactory,
    AnimatedDialog,
    ChineseMessageBox
)

__version__ = "2.0.0"
