from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QListWidget,
                               QListWidgetItem, QFrame, QScrollArea,
                               QFileDialog, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QIcon, QColor

class PluginListItem(QFrame):
    """Custom widget for displaying plugin information."""
    def __init__(self, plugin_name, plugin_info, parent=None):
        super().__init__(parent)
        self.setup_ui(plugin_name, plugin_info)
    
    def setup_ui(self, plugin_name, plugin_info):
        """Set up the plugin item UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Plugin info
        info_layout = QVBoxLayout()
        
        # Plugin name
        name_label = QLabel(plugin_name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(name_label)
        
        # Plugin description
        if plugin_info.get('description'):
            desc_label = QLabel(plugin_info['description'])
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: palette(text);")
            info_layout.addWidget(desc_label)
        
        # Plugin metadata
        meta_layout = QHBoxLayout()
        
        if plugin_info.get('version'):
            version_label = QLabel(f"v{plugin_info['version']}")
            version_label.setStyleSheet("color: palette(mid); font-size: 12px;")
            meta_layout.addWidget(version_label)
        
        if plugin_info.get('author'):
            author_label = QLabel(f"by {plugin_info['author']}")
            author_label.setStyleSheet("color: palette(mid); font-size: 12px;")
            meta_layout.addWidget(author_label)
        
        meta_layout.addStretch()
        info_layout.addLayout(meta_layout)
        
        layout.addLayout(info_layout)
        
        # Plugin status/actions
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        
        # Status indicator
        status = plugin_info.get('status', 'inactive')
        status_label = QLabel(status.title())
        status_label.setStyleSheet(f"""
            color: {'#4CAF50' if status == 'active' else '#9E9E9E'};
            font-size: 12px;
        """)
        status_layout.addWidget(status_label, alignment=Qt.AlignmentFlag.AlignRight)
        
        # Action button
        action_btn = QPushButton("Disable" if status == 'active' else "Enable")
        action_btn.setMaximumWidth(80)
        status_layout.addWidget(action_btn, alignment=Qt.AlignmentFlag.AlignRight)
        
        layout.addLayout(status_layout)
        
        # Set frame style
        self.setStyleSheet("""
            PluginListItem {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
            PluginListItem:hover {
                background-color: palette(alternate-base);
            }
        """)

class PluginTab(QWidget):
    def __init__(self, plugin_manager):
        super().__init__()
        self.plugin_manager = plugin_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the plugin tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title and description
        title_layout = QVBoxLayout()
        
        title = QLabel("Plugin Manager")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title_layout.addWidget(title)
        
        description = QLabel("Manage and configure your AI Assistant plugins")
        description.setStyleSheet("color: palette(mid);")
        title_layout.addWidget(description)
        
        header_layout.addLayout(title_layout)
        
        # Action buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.install_button = QPushButton("Install Plugin")
        self.install_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-radius: 6px;
                font-weight: bold;
            }
        """)
        button_layout.addWidget(self.install_button)
        
        self.refresh_button = QPushButton("Refresh")
        button_layout.addWidget(self.refresh_button)
        
        header_layout.addLayout(button_layout)
        
        layout.addWidget(header)
        
        # Plugin list
        list_frame = QFrame()
        list_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        
        list_layout = QVBoxLayout(list_frame)
        list_layout.setContentsMargins(15, 15, 15, 15)
        
        # Plugin list scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        # Plugin list container
        self.plugin_container = QWidget()
        self.plugin_layout = QVBoxLayout(self.plugin_container)
        self.plugin_layout.setSpacing(10)
        self.plugin_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll.setWidget(self.plugin_container)
        list_layout.addWidget(scroll)
        
        layout.addWidget(list_frame)
        
        # Connect signals
        self.install_button.clicked.connect(self.install_plugin)
        self.refresh_button.clicked.connect(self.update_plugin_list)
        
        # Initial plugin list update
        self.update_plugin_list()
    
    def update_plugin_list(self):
        """Update the list of plugins."""
        # Clear existing items
        for i in reversed(range(self.plugin_layout.count())):
            widget = self.plugin_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Add plugins
        plugins = self.plugin_manager.get_available_plugins()
        if not plugins:
            no_plugins = QLabel("No plugins installed")
            no_plugins.setStyleSheet("color: palette(mid); padding: 20px;")
            no_plugins.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.plugin_layout.addWidget(no_plugins)
        else:
            for plugin_name, plugin_info in plugins.items():
                item = PluginListItem(plugin_name, plugin_info)
                self.plugin_layout.addWidget(item)
        
        # Add stretch at the end
        self.plugin_layout.addStretch()
    
    def install_plugin(self):
        """Install a new plugin."""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Install Plugin",
            "",
            "Python Files (*.py);;All Files (*.*)"
        )
        
        if file_name:
            try:
                self.plugin_manager.install_plugin(file_name)
                self.update_plugin_list()
                QMessageBox.information(
                    self,
                    "Success",
                    "Plugin installed successfully!"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to install plugin: {str(e)}"
                )
    
    def remove_plugin(self):
        """Remove selected plugin (placeholder)."""
        selected = self.plugin_list.currentItem()
        if selected:
            plugin_name = selected.text()
            print(f"Would remove plugin: {plugin_name}") 