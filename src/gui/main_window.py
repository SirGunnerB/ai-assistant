from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox, QVBoxLayout, QWidget, QStatusBar, QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QColor
from gui.tabs.chat_tab import ChatTab
from gui.tabs.code_tab import CodeTab
from gui.tabs.image_tab import ImageTab
from gui.tabs.project_tab import ProjectTab
from gui.tabs.plugin_tab import PluginTab
from gui.tabs.settings_tab import SettingsTab
from gui.download_dialog import DownloadProgressDialog
from gui.theme_manager import ThemeManager
from core.model_manager import ModelManager
from core.chat_manager import ChatManager
from core.plugin_manager import PluginManager
from core.voice_manager import VoiceManager
from core.image_manager import ImageManager
from core.project_manager import ProjectManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AI Assistant")
        self.resize(1200, 800)
        
        # Initialize managers
        self.theme_manager = ThemeManager()
        self.model_manager = ModelManager(self)
        self.chat_manager = ChatManager(self.model_manager)
        self.plugin_manager = PluginManager()
        self.voice_manager = VoiceManager()
        self.image_manager = ImageManager()
        self.project_manager = ProjectManager()
        
        # Initialize UI
        self.setup_ui()
        
        # Apply theme
        self.apply_theme()
        
        # Check for model and prompt download if needed
        self.check_model()
    
    def setup_ui(self):
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.chat_tab = ChatTab(self.chat_manager, self.voice_manager, self.model_manager)
        self.code_tab = CodeTab(self.chat_manager, self.project_manager, self.model_manager)
        self.image_tab = ImageTab(self.image_manager, self.model_manager)
        self.project_tab = ProjectTab(self.project_manager)
        self.plugin_tab = PluginTab(self.plugin_manager)
        self.settings_tab = SettingsTab(self.model_manager, self.theme_manager)
        
        # Add tabs
        self.tab_widget.addTab(self.chat_tab, "Chat")
        self.tab_widget.addTab(self.code_tab, "Code")
        self.tab_widget.addTab(self.image_tab, "Image")
        self.tab_widget.addTab(self.project_tab, "Project")
        self.tab_widget.addTab(self.plugin_tab, "Plugins")
        self.tab_widget.addTab(self.settings_tab, "Settings")
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Connect theme manager signal
        self.theme_manager.theme_changed.connect(self.apply_theme)
    
    def apply_theme(self):
        theme = self.theme_manager.get_current_theme()
        
        # Create and configure palette
        palette = QPalette()
        
        # Set basic colors
        palette.setColor(QPalette.ColorRole.Window, QColor(theme["background"]))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(theme["text"]))
        palette.setColor(QPalette.ColorRole.Base, QColor(theme["background"]))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(theme["alternate_background"]))
        palette.setColor(QPalette.ColorRole.Text, QColor(theme["text"]))
        palette.setColor(QPalette.ColorRole.Button, QColor(theme["button"]))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(theme["button_text"]))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(theme["highlight"]))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(theme["highlighted_text"]))
        
        # Set disabled state colors
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, QColor(theme["disabled"]))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, QColor(theme["disabled"]))
        palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, QColor(theme["disabled"]))
        
        # Apply palette to application
        self.setPalette(palette)
        QApplication.instance().setPalette(palette)
        
        # Apply stylesheet
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {theme["background"]};
            }}
            QWidget {{
                color: {theme["text"]};
            }}
            QPushButton {{
                background-color: {theme["button"]};
                color: {theme["button_text"]};
                border: 1px solid {theme["button"]};
                border-radius: 4px;
                padding: 5px 10px;
            }}
            QPushButton:hover {{
                background-color: {theme["highlight"]};
                color: {theme["highlighted_text"]};
                border: 1px solid {theme["highlight"]};
            }}
            QLineEdit, QTextEdit {{
                background-color: {theme["background"]};
                color: {theme["text"]};
                border: 1px solid {theme["button"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox {{
                background-color: {theme["button"]};
                color: {theme["button_text"]};
                border: 1px solid {theme["button"]};
                border-radius: 4px;
                padding: 5px;
            }}
            QComboBox:hover {{
                border: 1px solid {theme["highlight"]};
            }}
            QComboBox::drop-down {{
                border: none;
            }}
            QComboBox::down-arrow {{
                image: none;
                border: none;
            }}
            QScrollBar:vertical {{
                background-color: {theme["background"]};
                width: 12px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {theme["button"]};
                min-height: 20px;
                border-radius: 6px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {theme["highlight"]};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0;
            }}
            QTabWidget::pane {{
                border: 1px solid {theme["button"]};
                border-radius: 4px;
            }}
            QTabBar::tab {{
                background-color: {theme["button"]};
                color: {theme["button_text"]};
                border: 1px solid {theme["button"]};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px 10px;
                margin-right: 2px;
            }}
            QTabBar::tab:selected {{
                background-color: {theme["highlight"]};
                color: {theme["highlighted_text"]};
            }}
            QTabBar::tab:hover:!selected {{
                background-color: {theme["alternate_background"]};
            }}
            QStatusBar {{
                background-color: {theme["background"]};
                color: {theme["text"]};
                border-top: 1px solid {theme["button"]};
            }}
        """)
    
    def check_model(self):
        """Check if the model needs to be downloaded."""
        if not self.model_manager.is_model_available():
            reply = QMessageBox.question(
                self,
                "Model Download Required",
                "The AI model needs to be downloaded before you can use the application. "
                "Would you like to download it now?\n\n"
                "Note: This may take several minutes depending on your internet connection.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.model_manager.download_model()
            else:
                QMessageBox.warning(
                    self,
                    "Limited Functionality",
                    "The application will have limited functionality without the AI model."
                )
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Save any necessary state here
        event.accept()