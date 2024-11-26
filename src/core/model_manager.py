from PyQt6.QtCore import QObject, pyqtSignal
from pathlib import Path
import requests
from gpt4all import GPT4All
import time
from datetime import datetime, timedelta
import threading
from queue import Queue
import hashlib
import json
from tqdm import tqdm
import os

class DownloadStatus:
    def __init__(self):
        self.start_time = time.time()
        self.downloaded = 0
        self.total_size = 0
        self.speed = 0
        self.last_update = time.time()
        self.last_downloaded = 0
        self.is_paused = False
        self.pause_event = threading.Event()
        self.retry_count = 0
        self.max_retries = 3

class ModelManager(QObject):
    model_download_progress = pyqtSignal(int)
    download_started = pyqtSignal()
    download_completed = pyqtSignal()
    download_failed = pyqtSignal(str)
    model_loaded = pyqtSignal()
    model_error = pyqtSignal(str)
    
    DEFAULT_MODEL_CONFIG = {
        "mistral-7b-instruct": {
            "name": "Mistral 7B Instruct",
            "description": "A powerful instruction-following language model",
            "file": "mistral-7b-instruct-v0.1.Q4_0.gguf",
            "url": "https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/mistral-7b-instruct-v0.1.Q4_0.gguf",
            "size": 4_100_000_000,  # ~4.1GB
            "type": "mistral",
            "context_length": 8192,
            "parameters": "7B",
            "requires_auth": True,
            "auth_token": "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"
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model = None
        self.model_path = Path("models")
        self.model_path.mkdir(exist_ok=True)
        self.current_model_name = None
        self._is_downloading = False
        self.download_status = None
        
        # Load model if it exists
        self.load_model()
    
    def is_model_loaded(self):
        return self.model is not None and self.current_model_name is not None
    
    def is_model_downloading(self):
        return self._is_downloading
    
    def is_model_available(self, model_name=None):
        model_path = self.get_model_path(model_name)
        if not model_path.exists():
            return False
        # Verify file size
        expected_size = self.DEFAULT_MODEL_CONFIG[model_name or next(iter(self.DEFAULT_MODEL_CONFIG))]["size"]
        actual_size = os.path.getsize(model_path)
        return abs(actual_size - expected_size) <= 1024 * 1024  # Allow 1MB difference
    
    def get_model_path(self, model_name=None):
        if model_name is None:
            model_name = next(iter(self.DEFAULT_MODEL_CONFIG))
        model_file = self.DEFAULT_MODEL_CONFIG[model_name]["file"]
        return self.model_path / str(model_file)
    
    def load_model(self, model_name=None):
        """Load the specified model or the default model."""
        if model_name is None:
            model_name = next(iter(self.DEFAULT_MODEL_CONFIG))
        
        model_path = self.get_model_path(model_name)
        if not model_path.exists():
            self.model_error.emit(f"Model file not found: {model_path}")
            return False
        
        # Verify file size
        if not self.is_model_available(model_name):
            self.model_error.emit("Model file is incomplete or corrupted")
            return False
        
        try:
            # Get model config
            model_config = self.DEFAULT_MODEL_CONFIG[model_name]
            
            # Initialize model with specific parameters
            self.model = GPT4All(
                model_path=str(model_path),
                model_type=model_config["type"],
                allow_download=False,
                n_ctx=model_config["context_length"]
            )
            
            # Test the model with a simple prompt
            try:
                self.model.generate("Test.", max_tokens=1)
                self.current_model_name = model_name
                self.model_loaded.emit()
                print(f"Model loaded successfully: {model_name}")
                return True
            except Exception as e:
                raise RuntimeError(f"Model verification failed: {str(e)}")
            
        except Exception as e:
            error_msg = f"Error loading model: {str(e)}"
            print(error_msg)
            self.model = None
            self.current_model_name = None
            self.model_error.emit(error_msg)
            
            # If file seems corrupted, delete it
            if "corrupted" in str(e).lower() or "invalid" in str(e).lower():
                try:
                    model_path.unlink()
                    print(f"Deleted corrupted model file: {model_path}")
                except Exception as del_e:
                    print(f"Error deleting corrupted model: {del_e}")
            
            return False
    
    def download_model(self, model_name=None):
        """Download the specified model or the default model."""
        if model_name is None:
            model_name = next(iter(self.DEFAULT_MODEL_CONFIG))
        
        if self._is_downloading:
            return
        
        if model_name not in self.DEFAULT_MODEL_CONFIG:
            self.download_failed.emit(f"Model '{model_name}' not found")
            return
        
        model_config = self.DEFAULT_MODEL_CONFIG[model_name]
        model_path = self.get_model_path(model_name)
        
        if model_path.exists():
            self.load_model(model_name)
            return
        
        self._is_downloading = True
        self.download_status = DownloadStatus()
        self.download_started.emit()
        
        # Start download in a separate thread
        thread = threading.Thread(target=self._download_model_thread, args=(model_name,))
        thread.daemon = True
        thread.start()
    
    def _download_model_thread(self, model_name):
        """Download thread implementation."""
        try:
            model_config = self.DEFAULT_MODEL_CONFIG[model_name]
            url = model_config["url"]
            model_path = self.get_model_path(model_name)
            
            # Create a session with headers
            session = requests.Session()
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
            
            # Add authorization if required
            if model_config.get("requires_auth"):
                headers["Authorization"] = f"Bearer {model_config['auth_token']}"
            
            session.headers.update(headers)
            
            # Make the request
            response = session.get(url, stream=True)
            response.raise_for_status()
            
            # Get total size
            total_size = int(response.headers.get("content-length", 0))
            if total_size == 0:
                total_size = model_config["size"]  # Use predefined size if not provided
            
            self.download_status.total_size = total_size
            
            # Download with progress
            with open(model_path, "wb") as f:
                downloaded = 0
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        downloaded += len(chunk)
                        f.write(chunk)
                        
                        # Update progress
                        progress = int((downloaded / total_size) * 100)
                        self.model_download_progress.emit(progress)
            
            # Verify file size
            actual_size = model_path.stat().st_size
            if abs(actual_size - total_size) > 1024 * 1024:  # Allow 1MB difference
                raise ValueError(f"Downloaded file size ({actual_size}) does not match expected size ({total_size})")
            
            # Load the model
            if self.load_model(model_name):
                self.download_completed.emit()
            else:
                raise ValueError("Failed to load downloaded model")
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            if model_path.exists():
                model_path.unlink()  # Delete partial download
            self.download_failed.emit(str(e))
        
        finally:
            self._is_downloading = False
    
    def get_response(self, prompt):
        """Get a response from the model."""
        if not self.is_model_loaded():
            raise RuntimeError("No model is currently loaded")
        
        try:
            response = self.model.generate(prompt)
            return response
        except Exception as e:
            print(f"Error getting response: {e}")
            return None
    
    def get_available_models(self):
        """Get list of available models."""
        return self.available_models
    
    def get_current_model(self):
        """Get the currently loaded model."""
        return self.current_model
    
    def add_model(self, name, info):
        """Add a new model configuration."""
        if name in self.available_models:
            raise ValueError(f"Model '{name}' already exists")
        
        required_fields = ["name", "description", "file", "url", "size", "type"]
        missing_fields = [field for field in required_fields if field not in info]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")
        
        self.available_models[name] = info
        self.save_models()
    
    def remove_model(self, name):
        """Remove a model configuration."""
        if name in self.DEFAULT_MODEL_CONFIG:
            raise ValueError("Cannot remove default models")
        
        if name in self.available_models:
            model_path = self.models_dir / self.available_models[name]["file"]
            if model_path.exists():
                model_path.unlink()
            
            del self.available_models[name]
            self.save_models()
    
    def get_model_info(self, model_name=None):
        """Get detailed information about a model."""
        model_name = model_name or self.default_model
        if model_name not in self.available_models:
            raise ValueError(f"Model '{model_name}' not found")
        
        info = self.available_models[model_name].copy()
        info["downloaded"] = self.is_model_available(model_name)
        info["current"] = model_name == self.current_model
        return info