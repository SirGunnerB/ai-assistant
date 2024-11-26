from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QLabel, QGroupBox, QFormLayout, QProgressBar,
                           QFrame, QStackedWidget)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from pathlib import Path

class SettingsSidebar(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_sidebar")
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create navigation buttons
        self.buttons = {}
        for section in ["Model", "API", "Voice", "Settings"]:
            btn = QPushButton(section)
            btn.setCheckable(True)
            self.buttons[section.lower()] = btn
            layout.addWidget(btn)
        
        layout.addStretch()

class SettingsTab(QWidget):
    def __init__(self, model_manager, theme_manager):
        super().__init__()
        self.model_manager = model_manager
        self.theme_manager = theme_manager
        
        # Connect model manager signals
        self.model_manager.model_download_progress.connect(self.update_download_progress)
        self.model_manager.download_started.connect(self.on_download_started)
        self.model_manager.download_completed.connect(self.on_download_completed)
        self.model_manager.download_failed.connect(self.on_download_failed)
        self.model_manager.model_loaded.connect(self.on_model_loaded)
        self.model_manager.model_error.connect(self.on_model_error)
        
        self.setup_ui()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create sidebar
        self.sidebar = SettingsSidebar()
        layout.addWidget(self.sidebar)
        
        # Create stacked widget for content
        self.content = QStackedWidget()
        
        # Create pages
        self.setup_model_page()
        self.setup_api_page()
        self.setup_voice_page()
        self.setup_settings_page()
        
        # Connect sidebar buttons
        for section, btn in self.sidebar.buttons.items():
            btn.clicked.connect(lambda checked, s=section: self.show_section(s))
        
        # Show initial section
        self.sidebar.buttons["model"].setChecked(True)
        self.show_section("model")
        
        layout.addWidget(self.content)
    
    def setup_model_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Model Info Group
        model_group = QGroupBox("Model Information")
        model_layout = QFormLayout()
        
        # Model Status
        self.model_status_label = QLabel("Not loaded")
        model_layout.addRow("Status:", self.model_status_label)
        
        # Model Name
        self.model_name_label = QLabel("No model selected")
        model_layout.addRow("Model:", self.model_name_label)
        
        # Model Size
        self.model_size_label = QLabel("-")
        model_layout.addRow("Size:", self.model_size_label)
        
        # Download Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        model_layout.addRow("Progress:", self.progress_bar)
        
        # Download Button
        self.download_button = QPushButton("Download Model")
        self.download_button.clicked.connect(self.download_model)
        model_layout.addRow("", self.download_button)
        
        model_group.setLayout(model_layout)
        layout.addWidget(model_group)
        
        # Add stretch to push everything to the top
        layout.addStretch()
        
        self.content.addWidget(page)
        self.update_model_status()
    
    def setup_api_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("API Settings"))
        self.content.addWidget(page)
    
    def setup_voice_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("Voice Settings"))
        self.content.addWidget(page)
    
    def setup_settings_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.addWidget(QLabel("General Settings"))
        self.content.addWidget(page)
    
    def show_section(self, section):
        self.content.setCurrentIndex(list(self.sidebar.buttons.keys()).index(section))
        
        # Update button states
        for btn_section, btn in self.sidebar.buttons.items():
            btn.setChecked(btn_section == section)
    
    def update_model_status(self):
        """Update the model status display."""
        model_config = next(iter(self.model_manager.DEFAULT_MODEL_CONFIG.values()))
        model_path = Path("models") / model_config["file"]
        
        if self.model_manager.is_model_loaded():
            self.model_status_label.setText("Model is loaded and ready")
            self.model_status_label.setStyleSheet("color: #4CAF50;")  # Green
            self.model_name_label.setText(model_config["name"])
            size_gb = model_config["size"] / 1_000_000_000
            self.model_size_label.setText(f"{size_gb:.1f} GB")
            self.download_button.setEnabled(False)
            self.download_button.setText("Model Loaded")
        elif self.model_manager.is_model_available():
            self.model_status_label.setText("Model downloaded but not loaded")
            self.model_status_label.setStyleSheet("color: #FFA500;")  # Orange
            self.model_name_label.setText(model_config["name"])
            size_gb = model_config["size"] / 1_000_000_000
            self.model_size_label.setText(f"{size_gb:.1f} GB")
            self.download_button.setEnabled(True)
            self.download_button.setText("Reload Model")
        else:
            self.model_status_label.setText("Model not downloaded")
            self.model_status_label.setStyleSheet("color: #F44336;")  # Red
            self.model_name_label.setText(model_config["name"])
            size_gb = model_config["size"] / 1_000_000_000
            self.model_size_label.setText(f"{size_gb:.1f} GB")
            self.download_button.setEnabled(True)
            self.download_button.setText("Download Model")
    
    def on_model_loaded(self):
        """Handle successful model loading."""
        self.update_model_status()
    
    def on_model_error(self, error):
        """Handle model loading error."""
        self.model_status_label.setText(f"Error: {error}")
        self.model_status_label.setStyleSheet("color: #F44336;")  # Red
        self.download_button.setEnabled(True)
        self.download_button.setText("Retry Download")
        
    def download_model(self):
        """Start model download."""
        self.model_manager.download_model()
    
    def update_download_progress(self, progress):
        """Update download progress bar."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(progress)
        self.download_button.setEnabled(False)
        self.download_button.setText("Downloading...")
    
    def on_download_started(self):
        """Handle download start."""
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.model_status_label.setText("Downloading model...")
        self.model_status_label.setStyleSheet("color: #2196F3;")  # Blue
        self.download_button.setEnabled(False)
        self.download_button.setText("Downloading...")
    
    def on_download_completed(self):
        """Handle download completion."""
        self.progress_bar.setVisible(False)
        self.update_model_status()
    
    def on_download_failed(self, error):
        """Handle download failure."""
        self.progress_bar.setVisible(False)
        self.model_status_label.setText(f"Download failed: {error}")
        self.model_status_label.setStyleSheet("color: #F44336;")  # Red
        self.download_button.setEnabled(True)
        self.download_button.setText("Retry Download")