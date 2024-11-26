from pathlib import Path
import shutil
import json
from PyQt6.QtCore import QObject, pyqtSignal
import hashlib
import mimetypes

class FileManager(QObject):
    file_created = pyqtSignal(str)  # path
    file_deleted = pyqtSignal(str)  # path
    file_modified = pyqtSignal(str)  # path
    
    def __init__(self):
        super().__init__()
        self.workspace_dir = Path("workspace")
        self.workspace_dir.mkdir(exist_ok=True)
        self.file_history = {}  # path: [versions]
        self.load_history()
        
    def load_history(self):
        history_file = self.workspace_dir / "file_history.json"
        if history_file.exists():
            with open(history_file, 'r') as f:
                self.file_history = json.load(f)
                
    def save_history(self):
        history_file = self.workspace_dir / "file_history.json"
        with open(history_file, 'w') as f:
            json.dump(self.file_history, f, indent=4)
            
    def create_file(self, path, content=""):
        """Create a new file with optional content"""
        full_path = Path(path)
        if full_path.exists():
            raise FileExistsError(f"File already exists: {path}")
            
        full_path.parent.mkdir(parents=True, exist_ok=True)
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
            
        self.add_to_history(str(full_path))
        self.file_created.emit(str(full_path))
        
    def read_file(self, path):
        """Read file content"""
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
            
    def write_file(self, path, content):
        """Write content to file"""
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        self.add_to_history(path)
        self.file_modified.emit(path)
        
    def delete_file(self, path):
        """Delete file"""
        Path(path).unlink()
        if str(path) in self.file_history:
            del self.file_history[str(path)]
        self.save_history()
        self.file_deleted.emit(str(path))
        
    def add_to_history(self, path):
        """Add file version to history"""
        if str(path) not in self.file_history:
            self.file_history[str(path)] = []
            
        with open(path, 'rb') as f:
            content = f.read()
            hash = hashlib.md5(content).hexdigest()
            
        self.file_history[str(path)].append({
            'hash': hash,
            'timestamp': str(Path(path).stat().st_mtime)
        })
        
        # Keep only last 10 versions
        self.file_history[str(path)] = self.file_history[str(path)][-10:]
        self.save_history()
        
    def get_file_type(self, path):
        """Get file type/language"""
        mime_type, _ = mimetypes.guess_type(path)
        if mime_type:
            return mime_type
        
        # Check extensions for common programming languages
        ext = Path(path).suffix.lower()
        language_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.html': 'HTML',
            '.css': 'CSS',
            '.java': 'Java',
            '.cpp': 'C++',
            '.h': 'C++',
            '.cs': 'C#',
            '.php': 'PHP',
            '.rb': 'Ruby',
            '.go': 'Go',
            '.rs': 'Rust',
            '.swift': 'Swift',
            '.kt': 'Kotlin'
        }
        return language_map.get(ext, 'Plain Text') 