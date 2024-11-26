from PyQt6.QtCore import QObject, pyqtSignal

class VoiceManager(QObject):
    """Manages voice input and output (simplified version)."""
    
    voice_input_received = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.is_listening = False
    
    def start_listening(self):
        """Start listening for voice input (placeholder)."""
        self.is_listening = True
        print("Voice input is not available in this version.")
    
    def stop_listening(self):
        """Stop listening for voice input."""
        self.is_listening = False
    
    def speak(self, text):
        """Convert text to speech (placeholder)."""
        print(f"Text-to-speech: {text}")
    
    def is_available(self):
        """Check if voice features are available."""
        return False  # Voice features are disabled in this version 