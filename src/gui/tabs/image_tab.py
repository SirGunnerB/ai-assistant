from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
                               QPushButton, QLabel, QSpinBox, QComboBox,
                               QFrame, QScrollArea, QGridLayout, QSizePolicy)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import QPixmap, QPainter, QColor, QPalette

class ImagePreview(QLabel):
    """Custom image preview widget with placeholder and loading states."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(512, 512)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                background-color: palette(base);
                border: 2px dashed palette(mid);
                border-radius: 10px;
            }
        """)
        self.show_placeholder()
    
    def show_placeholder(self):
        """Show the placeholder message."""
        self.setText("Generated image will appear here")
    
    def show_loading(self):
        """Show the loading message."""
        self.setText("Generating image...")
    
    def set_image(self, pixmap):
        """Set the image to display."""
        scaled_pixmap = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled_pixmap)

class StyleButton(QPushButton):
    """Custom button for style selection."""
    def __init__(self, text, description="", parent=None):
        super().__init__(text, parent)
        self.description = description
        self.setCheckable(True)
        self.setMinimumWidth(120)
        self.setStyleSheet("""
            QPushButton {
                padding: 10px;
                text-align: left;
                border-radius: 6px;
            }
            QPushButton:checked {
                background-color: palette(highlight);
                color: palette(highlighted-text);
            }
        """)

class ImageTab(QWidget):
    def __init__(self, image_manager, model_manager):
        super().__init__()
        self.image_manager = image_manager
        self.model_manager = model_manager
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Set up the image tab UI."""
        layout = QHBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Left side - Controls
        controls = QFrame()
        controls.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        controls.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)
        
        controls_layout = QVBoxLayout(controls)
        controls_layout.setSpacing(15)
        controls_layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Image Generation")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        controls_layout.addWidget(title)
        
        # Prompt input
        prompt_label = QLabel("Prompt")
        prompt_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(prompt_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setPlaceholderText("Describe the image you want to generate...")
        self.prompt_input.setMaximumHeight(100)
        controls_layout.addWidget(self.prompt_input)
        
        # Style selection
        style_label = QLabel("Style")
        style_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(style_label)
        
        style_grid = QGridLayout()
        style_grid.setSpacing(10)
        
        styles = [
            ("Realistic", "Photorealistic style"),
            ("Artistic", "Digital art style"),
            ("Anime", "Anime/Manga style"),
            ("3D", "3D rendered style"),
            ("Sketch", "Hand-drawn sketch"),
            ("Pixel", "Pixel art style")
        ]
        
        self.style_buttons = []
        for i, (style, desc) in enumerate(styles):
            btn = StyleButton(style, desc)
            self.style_buttons.append(btn)
            style_grid.addWidget(btn, i // 2, i % 2)
        
        controls_layout.addLayout(style_grid)
        
        # Settings
        settings_label = QLabel("Settings")
        settings_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(settings_label)
        
        # Size selector
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Size:"))
        self.size_selector = QComboBox()
        self.size_selector.addItems(["256x256", "512x512", "1024x1024"])
        self.size_selector.setCurrentText("512x512")
        size_layout.addWidget(self.size_selector)
        controls_layout.addLayout(size_layout)
        
        # Number of images
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("Count:"))
        self.count_spinner = QSpinBox()
        self.count_spinner.setRange(1, 4)
        self.count_spinner.setValue(1)
        count_layout.addWidget(self.count_spinner)
        controls_layout.addLayout(count_layout)
        
        # Generate button
        self.generate_button = QPushButton("Generate Image")
        self.generate_button.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-weight: bold;
                background-color: palette(highlight);
                color: palette(highlighted-text);
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: palette(dark);
            }
            QPushButton:disabled {
                background-color: palette(mid);
            }
        """)
        controls_layout.addWidget(self.generate_button)
        
        controls_layout.addStretch()
        
        # Right side - Image preview
        preview_frame = QFrame()
        preview_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 10px;
            }
        """)
        
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setContentsMargins(15, 15, 15, 15)
        
        # Preview title
        preview_title = QLabel("Preview")
        preview_title.setStyleSheet("font-size: 18px; font-weight: bold;")
        preview_layout.addWidget(preview_title)
        
        # Image display
        self.image_preview = ImagePreview()
        preview_layout.addWidget(self.image_preview)
        
        # Add main sections to layout
        layout.addWidget(controls)
        layout.addWidget(preview_frame, stretch=1)
    
    def setup_connections(self):
        """Set up signal connections."""
        self.generate_button.clicked.connect(self.generate_image)
        self.image_manager.generation_started.connect(self.on_generation_started)
        self.image_manager.generation_completed.connect(self.on_generation_completed)
        self.image_manager.generation_failed.connect(self.on_generation_failed)
    
    @pyqtSlot()
    def generate_image(self):
        """Generate an image based on the prompt and settings."""
        prompt = self.prompt_input.toPlainText().strip()
        if prompt:
            try:
                # Get selected style
                style = next((btn.text() for btn in self.style_buttons if btn.isChecked()), None)
                if style:
                    prompt = f"{style} style: {prompt}"
                
                size = tuple(map(int, self.size_selector.currentText().split('x')))
                count = self.count_spinner.value()
                
                self.image_manager.generate_image(prompt, size, count)
            except Exception as e:
                self.on_generation_failed(str(e))
    
    @pyqtSlot()
    def on_generation_started(self):
        """Handle generation start."""
        self.generate_button.setEnabled(False)
        self.image_preview.show_loading()
    
    @pyqtSlot(str)
    def on_generation_completed(self, image_path):
        """Handle generation completion."""
        self.generate_button.setEnabled(True)
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            self.image_preview.set_image(pixmap)
        else:
            self.on_generation_failed("Failed to load generated image")
    
    @pyqtSlot(str)
    def on_generation_failed(self, error_message):
        """Handle generation failure."""
        self.generate_button.setEnabled(True)
        self.image_preview.setText(f"Error: {error_message}")