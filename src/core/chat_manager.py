from PyQt6.QtCore import QObject, pyqtSignal

class ChatManager(QObject):
    """Manages chat interactions with the AI model."""
    
    message_received = pyqtSignal(str, str)  # role, content
    
    def __init__(self, model_manager):
        super().__init__()
        self.model_manager = model_manager
        self.history = []
    
    def get_response(self, message):
        """Get a response from the AI model."""
        try:
            response = self.model_manager.get_response(message)
            self.history.append(("user", message))
            self.history.append(("assistant", response))
            self.message_received.emit("assistant", response)
            return response
        except Exception as e:
            print(f"Error getting response: {e}")
            return f"Error: {str(e)}"
    
    def clear_history(self):
        """Clear chat history."""
        self.history.clear()