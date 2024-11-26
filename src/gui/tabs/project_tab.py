from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTreeView,
                               QPushButton, QLabel, QDialog, QFrame,
                               QLineEdit, QFileDialog, QMessageBox,
                               QFormLayout, QTextEdit, QSplitter)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QStandardItemModel, QStandardItem, QIcon
from pathlib import Path
import json

class ProjectDialog(QDialog):
    """Dialog for creating or editing projects."""
    def __init__(self, title="New Project", project_data=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.project_data = project_data or {}
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Form layout for project details
        form = QFormLayout()
        form.setSpacing(10)
        
        # Project name
        self.name_input = QLineEdit(self.project_data.get("name", ""))
        self.name_input.setPlaceholderText("Enter project name")
        form.addRow("Project Name:", self.name_input)
        
        # Project location
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit(self.project_data.get("path", ""))
        self.path_input.setPlaceholderText("Select project location")
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        form.addRow("Location:", path_layout)
        
        # Project description
        self.description = QTextEdit(self.project_data.get("description", ""))
        self.description.setPlaceholderText("Enter project description")
        self.description.setMaximumHeight(100)
        form.addRow("Description:", self.description)
        
        layout.addLayout(form)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        create_btn = QPushButton("Create" if not self.project_data else "Save")
        create_btn.clicked.connect(self.accept)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        # Set dialog style
        self.setStyleSheet("""
            QDialog {
                background-color: palette(window);
                min-width: 400px;
            }
            QLineEdit, QTextEdit {
                padding: 8px;
                border: 1px solid palette(mid);
                border-radius: 5px;
                background-color: palette(base);
            }
            QLabel {
                font-weight: bold;
            }
        """)
    
    def browse_path(self):
        """Browse for project location."""
        path = QFileDialog.getExistingDirectory(
            self, "Select Project Location",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            self.path_input.setText(path)
    
    def get_project_data(self):
        """Get the project data from the dialog."""
        return {
            "name": self.name_input.text().strip(),
            "path": self.path_input.text().strip(),
            "description": self.description.toPlainText().strip()
        }

class ProjectTab(QWidget):
    """Modern project management tab."""
    def __init__(self, project_manager):
        super().__init__()
        self.project_manager = project_manager
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the project tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background-color: palette(alternate-base);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        header_layout = QHBoxLayout(header)
        
        # Title and description
        title_layout = QVBoxLayout()
        title = QLabel("Project Manager")
        title.setStyleSheet("font-size: 24px; font-weight: bold;")
        title_layout.addWidget(title)
        
        description = QLabel("Create and manage your AI projects")
        description.setStyleSheet("color: palette(mid);")
        title_layout.addWidget(description)
        header_layout.addLayout(title_layout)
        
        # Project actions
        action_layout = QHBoxLayout()
        
        self.new_project_btn = QPushButton("New Project")
        self.new_project_btn.setStyleSheet("""
            QPushButton {
                background-color: palette(highlight);
                color: palette(highlighted-text);
                padding: 8px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        action_layout.addWidget(self.new_project_btn)
        
        self.open_project_btn = QPushButton("Open Project")
        action_layout.addWidget(self.open_project_btn)
        
        header_layout.addLayout(action_layout)
        layout.addWidget(header)
        
        # Main content area
        content = QSplitter(Qt.Orientation.Horizontal)
        content.setStyleSheet("""
            QSplitter::handle {
                background-color: palette(mid);
                width: 1px;
            }
        """)
        
        # Project list
        project_frame = QFrame()
        project_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        project_layout = QVBoxLayout(project_frame)
        project_layout.setContentsMargins(10, 10, 10, 10)
        
        # Project tree
        self.project_tree = QTreeView()
        self.project_tree.setHeaderHidden(True)
        self.project_tree.setAnimated(True)
        self.project_tree.setIndentation(20)
        self.project_model = QStandardItemModel()
        self.project_tree.setModel(self.project_model)
        project_layout.addWidget(self.project_tree)
        
        # Project details
        details_frame = QFrame()
        details_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        details_layout = QVBoxLayout(details_frame)
        details_layout.setContentsMargins(20, 20, 20, 20)
        
        self.details_title = QLabel("Project Details")
        self.details_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        details_layout.addWidget(self.details_title)
        
        self.details_content = QTextEdit()
        self.details_content.setReadOnly(True)
        details_layout.addWidget(self.details_content)
        
        # Project actions
        actions_layout = QHBoxLayout()
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setEnabled(False)
        actions_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("Delete")
        self.delete_btn.setEnabled(False)
        actions_layout.addWidget(self.delete_btn)
        
        details_layout.addLayout(actions_layout)
        
        # Add frames to splitter
        content.addWidget(project_frame)
        content.addWidget(details_frame)
        content.setSizes([200, 400])  # Set initial sizes
        
        layout.addWidget(content)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.new_project_btn.clicked.connect(self.create_new_project)
        self.open_project_btn.clicked.connect(self.open_project)
        self.edit_btn.clicked.connect(self.edit_project)
        self.delete_btn.clicked.connect(self.delete_project)
        self.project_tree.clicked.connect(self.show_project_details)
        
        # Connect project manager signals
        self.project_manager.project_opened.connect(self.update_project_list)
        self.project_manager.project_closed.connect(self.update_project_list)
        self.project_manager.project_saved.connect(self.update_project_list)
    
    def create_new_project(self):
        """Create a new project."""
        dialog = ProjectDialog(parent=self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()
            try:
                self.project_manager.create_project(
                    data["name"],
                    data["description"]
                )
                self.update_project_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create project: {str(e)}")
    
    def open_project(self):
        """Open an existing project."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Open Project",
            str(Path.home()),
            QFileDialog.Option.ShowDirsOnly
        )
        if path:
            try:
                self.project_manager.open_project(path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open project: {str(e)}")
    
    def edit_project(self):
        """Edit the selected project."""
        project = self.project_manager.current_project
        if not project:
            return
        
        dialog = ProjectDialog(
            title="Edit Project",
            project_data={
                "name": project.name,
                "path": str(project.path),
                "description": project.description
            },
            parent=self
        )
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_project_data()
            try:
                project.name = data["name"]
                project.description = data["description"]
                self.project_manager.save_project()
                self.update_project_list()
                self.show_project_details()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update project: {str(e)}")
    
    def delete_project(self):
        """Delete the selected project."""
        project = self.project_manager.current_project
        if not project:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete project '{project.name}'?\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.project_manager.close_project()
                # TODO: Implement actual project deletion
                self.update_project_list()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete project: {str(e)}")
    
    def update_project_list(self):
        """Update the project tree view."""
        self.project_model.clear()
        self.project_model.setHorizontalHeaderLabels(["Projects"])
        
        # Add recent projects
        recent = QStandardItem("Recent Projects")
        recent.setEditable(False)
        self.project_model.appendRow(recent)
        
        for path in self.project_manager.recent_projects:
            try:
                with open(Path(path) / "project.json", 'r') as f:
                    project_data = json.load(f)
                    item = QStandardItem(project_data["name"])
                    item.setEditable(False)
                    item.setData(path)
                    recent.appendRow(item)
            except Exception:
                continue
        
        self.project_tree.expandAll()
    
    def show_project_details(self, index=None):
        """Show details of the selected project."""
        if index and index.isValid():
            item = self.project_model.itemFromIndex(index)
            path = item.data()
            if path:
                try:
                    with open(Path(path) / "project.json", 'r') as f:
                        project_data = json.load(f)
                        self.details_title.setText(project_data["name"])
                        self.details_content.setHtml(f"""
                            <h3>Project Details</h3>
                            <p><b>Name:</b> {project_data["name"]}</p>
                            <p><b>Location:</b> {project_data["path"]}</p>
                            <p><b>Description:</b></p>
                            <p>{project_data["description"] or "No description available."}</p>
                        """)
                        
                        # Enable action buttons
                        self.edit_btn.setEnabled(True)
                        self.delete_btn.setEnabled(True)
                        return
                except Exception:
                    pass
        
        # Clear details if no valid project selected
        self.details_title.setText("Project Details")
        self.details_content.clear()
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)
