from PyQt6.QtWidgets import (QDialog, QProgressBar, QLabel, QVBoxLayout,
                           QPushButton, QHBoxLayout, QSpinBox, QGroupBox)
from PyQt6.QtCore import Qt

class DownloadProgressDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Downloading Model")
        self.setModal(True)
        self.setFixedSize(500, 300)
        
        layout = QVBoxLayout()
        
        # Queue status
        queue_group = QGroupBox("Download Queue")
        queue_layout = QVBoxLayout()
        self.queue_status = QLabel("Queue: Empty")
        queue_layout.addWidget(self.queue_status)
        queue_group.setLayout(queue_layout)
        layout.addWidget(queue_group)
        
        # Download status
        status_group = QGroupBox("Download Status")
        status_layout = QVBoxLayout()
        
        # Status labels
        self.status_label = QLabel("Preparing download...")
        status_layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        status_layout.addWidget(self.progress_bar)
        
        # Speed and ETA
        speed_eta_layout = QHBoxLayout()
        self.speed_label = QLabel("Speed: Calculating...")
        self.eta_label = QLabel("ETA: Calculating...")
        speed_eta_layout.addWidget(self.speed_label)
        speed_eta_layout.addWidget(self.eta_label)
        status_layout.addLayout(speed_eta_layout)
        
        # Size info
        self.size_label = QLabel("")
        status_layout.addWidget(self.size_label)
        
        # Retry info
        self.retry_label = QLabel("")
        self.retry_label.setStyleSheet("color: orange;")
        status_layout.addWidget(self.retry_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Bandwidth control
        bandwidth_group = QGroupBox("Bandwidth Control")
        bandwidth_layout = QHBoxLayout()
        
        bandwidth_layout.addWidget(QLabel("Limit:"))
        self.bandwidth_limit = QSpinBox()
        self.bandwidth_limit.setMinimum(0)
        self.bandwidth_limit.setMaximum(100)
        self.bandwidth_limit.setValue(0)
        self.bandwidth_limit.setSuffix(" MB/s")
        self.bandwidth_limit.valueChanged.connect(self.set_bandwidth_limit)
        bandwidth_layout.addWidget(self.bandwidth_limit)
        
        bandwidth_group.setLayout(bandwidth_layout)
        layout.addWidget(bandwidth_group)
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        self.pause_button = QPushButton("Pause")
        self.pause_button.clicked.connect(self.toggle_pause)
        button_layout.addWidget(self.pause_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_download)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        self.is_paused = False
        self.model_manager = None
    
    def set_model_manager(self, manager):
        """Set the model manager for control operations."""
        self.model_manager = manager
        
        # Connect to model manager signals
        if self.model_manager:
            self.model_manager.download_queued.connect(self.update_queue_status)
            self.model_manager.download_retry.connect(self.show_retry_status)
    
    def update_queue_status(self, model_name, position):
        """Update the queue status display."""
        if position > 1:
            self.queue_status.setText(f"Queue: {model_name} (Position: {position})")
        else:
            self.queue_status.setText(f"Queue: {model_name} (Downloading)")
    
    def show_retry_status(self, model_name, attempt, max_attempts):
        """Show retry status."""
        self.retry_label.setText(f"Download failed, retrying... (Attempt {attempt}/{max_attempts})")
    
    def set_bandwidth_limit(self, limit_mbps):
        """Set the bandwidth limit."""
        if self.model_manager:
            self.model_manager.set_bandwidth_limit(limit_mbps)
    
    def toggle_pause(self):
        """Toggle download pause/resume."""
        if not self.model_manager:
            return
            
        if self.is_paused:
            self.model_manager.resume_download()
            self.pause_button.setText("Pause")
            self.status_label.setText("Downloading...")
        else:
            self.model_manager.pause_download()
            self.pause_button.setText("Resume")
            self.status_label.setText("Paused")
        
        self.is_paused = not self.is_paused
    
    def cancel_download(self):
        """Cancel the download."""
        if self.model_manager:
            self.model_manager.cancel_download()
        self.reject()
    
    def update_progress(self, progress, speed_mbps=None, eta=None):
        """Update the progress bar and status text."""
        self.progress_bar.setValue(int(progress))
        
        if not self.is_paused:
            self.status_label.setText(f"Downloading... {progress:.1f}%")
        
        if speed_mbps is not None:
            self.speed_label.setText(f"Speed: {speed_mbps:.1f} MB/s")
        
        if eta is not None:
            self.eta_label.setText(f"ETA: {eta}")
    
    def set_total_size(self, size_mb):
        """Set the total size label."""
        self.size_label.setText(f"Total size: {size_mb:.1f} MB") 