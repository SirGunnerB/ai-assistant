from pathlib import Path
import json
import shutil
from PyQt6.QtCore import QObject, pyqtSignal

class Project:
    def __init__(self, name, path, description=""):
        self.name = name
        self.path = Path(path)
        self.description = description
        self.files = []
        self.settings = {}
        
    def to_dict(self):
        return {
            "name": self.name,
            "path": str(self.path),
            "description": self.description,
            "settings": self.settings
        }
    
    @classmethod
    def from_dict(cls, data):
        project = cls(data["name"], data["path"], data["description"])
        project.settings = data.get("settings", {})
        return project

class ProjectManager(QObject):
    project_opened = pyqtSignal(object)  # Emits Project object
    project_closed = pyqtSignal()
    project_saved = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.workspace_dir = Path("workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        self.current_project = None
        self.recent_projects = self.load_recent_projects()
        
    def load_recent_projects(self):
        config_file = Path("config/recent_projects.json")
        if not config_file.exists():
            return []
        with open(config_file, 'r') as f:
            return json.load(f)
            
    def save_recent_projects(self):
        config_file = Path("config/recent_projects.json")
        config_file.parent.mkdir(exist_ok=True)
        with open(config_file, 'w') as f:
            json.dump(self.recent_projects, f)
            
    def create_project(self, name, description=""):
        project_path = self.workspace_dir / name
        if project_path.exists():
            raise ValueError(f"Project {name} already exists")
            
        project_path.mkdir(parents=True)
        project = Project(name, project_path, description)
        
        # Create project structure
        (project_path / "src").mkdir()
        (project_path / "resources").mkdir()
        (project_path / "output").mkdir()
        
        # Create project config
        with open(project_path / "project.json", 'w') as f:
            json.dump(project.to_dict(), f, indent=4)
            
        self.current_project = project
        self.add_to_recent_projects(str(project_path))
        self.project_opened.emit(project)
        return project
        
    def open_project(self, path):
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Project path {path} does not exist")
            
        config_file = path / "project.json"
        if not config_file.exists():
            raise ValueError(f"Not a valid project directory: {path}")
            
        with open(config_file, 'r') as f:
            project_data = json.load(f)
            
        project = Project.from_dict(project_data)
        self.current_project = project
        self.add_to_recent_projects(str(path))
        self.project_opened.emit(project)
        return project
        
    def close_project(self):
        if self.current_project:
            self.save_project()
            self.current_project = None
            self.project_closed.emit()
            
    def save_project(self):
        if not self.current_project:
            return
            
        config_file = self.current_project.path / "project.json"
        with open(config_file, 'w') as f:
            json.dump(self.current_project.to_dict(), f, indent=4)
        self.project_saved.emit()
        
    def add_to_recent_projects(self, path):
        if path in self.recent_projects:
            self.recent_projects.remove(path)
        self.recent_projects.insert(0, path)
        self.recent_projects = self.recent_projects[:10]  # Keep only 10 most recent
        self.save_recent_projects() 