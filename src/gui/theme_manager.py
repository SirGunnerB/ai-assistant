from PyQt6.QtGui import QColor
from PyQt6.QtCore import QObject, pyqtSignal

class ThemeManager(QObject):
    theme_changed = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.theme = {
            "background": "#2b2b2b",
            "text": "#ffffff",
            "button": "#3c3f41",
            "button_text": "#ffffff",
            "highlight": "#4e9eff",
            "highlighted_text": "#ffffff",
            "alternate_background": "#323232",
            "tooltip_background": "#2b2b2b",
            "tooltip_text": "#ffffff",
            "disabled": "#808080"
        }
    
    def get_current_theme(self):
        """Get the theme colors dictionary."""
        return self.theme