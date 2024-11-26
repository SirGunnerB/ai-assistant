from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QLabel, QScrollArea, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QTextCursor, QFont, QColor, QPalette

class MessageWidget(QFrame):
    """Widget for displaying a single chat message."""
    def __init__(self, text, is_user=True, parent=None):
        super().__init__(parent)
        self.setup_ui(text, is_user)
    
    def setup_ui(self, text, is_user):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Message bubble
        message = QLabel(text)
        message.setWordWrap(True)
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setOpenExternalLinks(True)
        
        # Style the message
        if is_user:
            self.setStyleSheet("""
                MessageWidget {
                    background-color: palette(highlight);
                    border-radius: 10px;
                    margin-left: 50px;
                }
                QLabel {
                    color: palette(highlighted-text);
                }
            """)
        else:
            self.setStyleSheet("""
                MessageWidget {
                    background-color: palette(button);
                    border-radius: 10px;
                    margin-right: 50px;
                }
                QLabel {
                    color: palette(text);
                }
            """)
        
        layout.addWidget(message)

class ChatTab(QWidget):
    def __init__(self, chat_manager, voice_manager, model_manager):
        super().__init__()
        self.chat_manager = chat_manager
        self.voice_manager = voice_manager
        self.model_manager = model_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the chat tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Chat history scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Container for messages
        self.message_container = QWidget()
        self.message_layout = QVBoxLayout(self.message_container)
        self.message_layout.setSpacing(10)
        self.message_layout.addStretch()
        
        scroll.setWidget(self.message_container)
        layout.addWidget(scroll)
        
        # Input area
        input_frame = QFrame()
        input_frame.setStyleSheet("""
            QFrame {
                background-color: palette(button);
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(5, 5, 5, 5)
        
        # Message input
        self.message_input = QTextEdit()
        self.message_input.setPlaceholderText("Type your message here...")
        self.message_input.setMaximumHeight(100)
        self.message_input.setStyleSheet("""
            QTextEdit {
                border: none;
                background-color: transparent;
            }
        """)
        input_layout.addWidget(self.message_input)
        
        # Button container
        button_layout = QVBoxLayout()
        button_layout.setSpacing(5)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.setDefault(True)
        self.send_button.clicked.connect(self.send_message)
        button_layout.addWidget(self.send_button)
        
        # Voice button
        self.voice_button = QPushButton("🎤")
        self.voice_button.setToolTip("Voice Input")
        self.voice_button.clicked.connect(self.toggle_voice_input)
        button_layout.addWidget(self.voice_button)
        
        input_layout.addLayout(button_layout)
        layout.addWidget(input_frame)
        
        # Set up key press event
        self.message_input.installEventFilter(self)
    
    def eventFilter(self, obj, event):
        """Handle key press events."""
        if obj == self.message_input and event.type() == event.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.NoModifier:
                self.send_message()
                return True
            elif event.key() == Qt.Key.Key_Return and event.modifiers() == Qt.KeyboardModifier.ShiftModifier:
                cursor = self.message_input.textCursor()
                cursor.insertText("\\n")
                return True
        return super().eventFilter(obj, event)
    
    def add_message(self, text, is_user=True):
        """Add a message to the chat history."""
        message = MessageWidget(text, is_user)
        self.message_layout.insertWidget(self.message_layout.count() - 1, message)
        
        # Scroll to bottom
        scroll = self.message_container.parent()
        if isinstance(scroll, QScrollArea):
            scroll.verticalScrollBar().setValue(scroll.verticalScrollBar().maximum())
    
    @pyqtSlot()
    def send_message(self):
        """Send a message to the AI."""
        message = self.message_input.toPlainText().strip()
        if message:
            # Add user message
            self.add_message(message, True)
            self.message_input.clear()
            
            try:
                # Get AI response
                response = self.chat_manager.get_response(message)
                self.add_message(response, False)
            except Exception as e:
                self.add_message(f"Error: {str(e)}", False)
    
    @pyqtSlot()
    def toggle_voice_input(self):
        """Toggle voice input."""
        try:
            text = self.voice_manager.listen()
            if text:
                self.message_input.setPlainText(text)
                self.message_input.moveCursor(QTextCursor.MoveOperation.End)
        except Exception as e:
            self.add_message(f"Voice Input Error: {str(e)}", False)