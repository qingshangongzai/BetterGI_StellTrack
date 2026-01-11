import os
from PyQt6.QtGui import QFont, QFontDatabase
from utils import find_resource_file


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


def get_global_font_manager():
    """获取全局字体管理器实例"""
    return GlobalFontManager.get_instance()
