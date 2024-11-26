from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QPushButton, QComboBox, QSplitter, QLabel,
                           QTreeView, QFrame, QMenu, QFileDialog, QScrollArea)
from PyQt6.QtCore import Qt, pyqtSlot, QSize
from PyQt6.QtGui import (QStandardItemModel, QStandardItem, QFont, 
                        QSyntaxHighlighter, QTextCharFormat, QColor,
                        QFontMetrics)

class PythonHighlighter(QSyntaxHighlighter):
    """Syntax highlighter for Python code."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighting_rules = []
        
        # Keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#FF7043"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "and", "as", "assert", "break", "class", "continue", "def",
            "del", "elif", "else", "except", "False", "finally", "for",
            "from", "global", "if", "import", "in", "is", "lambda", "None",
            "nonlocal", "not", "or", "pass", "raise", "return", "True",
            "try", "while", "with", "yield"
        ]
        self.add_mapping(keywords, keyword_format)
        
        # Built-in functions
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#42A5F5"))
        builtins = [
            "abs", "all", "any", "bin", "bool", "chr", "dict", "dir",
            "enumerate", "eval", "exec", "filter", "float", "format",
            "frozenset", "getattr", "globals", "hasattr", "hash", "help",
            "hex", "id", "input", "int", "isinstance", "issubclass", "iter",
            "len", "list", "locals", "map", "max", "min", "next", "object",
            "oct", "open", "ord", "pow", "print", "property", "range",
            "repr", "reversed", "round", "set", "setattr", "slice",
            "sorted", "staticmethod", "str", "sum", "super", "tuple",
            "type", "vars", "zip"
        ]
        self.add_mapping(builtins, builtin_format)
        
        # Strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#66BB6A"))
        self.highlighting_rules.append((
            r'"[^"\\]*(\\.[^"\\]*)*"|\'[^\'\\]*(\\.[^\'\\]*)*\'',
            string_format
        ))
        
        # Numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#AB47BC"))
        self.highlighting_rules.append((
            r'\b[0-9]+\b',
            number_format
        ))
        
        # Comments
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#78909C"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((
            r'#[^\n]*',
            comment_format
        ))
    
    def add_mapping(self, words, format):
        """Add a list of words with their format to the highlighting rules."""
        for word in words:
            pattern = r'\b' + word + r'\b'
            self.highlighting_rules.append((pattern, format))
    
    def highlightBlock(self, text):
        """Apply syntax highlighting to the given block of text."""
        import re
        for pattern, format in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                self.setFormat(match.start(), match.end() - match.start(), format)

class CodeEditor(QTextEdit):
    """Enhanced code editor with line numbers and syntax highlighting."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_editor()
    
    def setup_editor(self):
        """Set up the code editor."""
        # Set font
        font = QFont("Consolas, 'Courier New', monospace")
        font.setPointSize(10)
        self.setFont(font)
        
        # Set tab width to 4 spaces
        metrics = QFontMetrics(font)
        self.setTabStopDistance(4 * metrics.horizontalAdvance(' '))
        
        # Enable line wrapping
        self.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
        
        # Set up syntax highlighter
        self.highlighter = PythonHighlighter(self.document())
        
        # Set up styling
        self.setStyleSheet("""
            QTextEdit {
                background-color: palette(base);
                color: palette(text);
                border: none;
                padding: 5px;
            }
        """)

class CodeTab(QWidget):
    def __init__(self, chat_manager, project_manager, model_manager):
        super().__init__()
        self.chat_manager = chat_manager
        self.project_manager = project_manager
        self.model_manager = model_manager
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the code tab UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create main splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - File browser
        file_browser = QFrame()
        file_browser.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
        """)
        file_layout = QVBoxLayout(file_browser)
        file_layout.setContentsMargins(5, 5, 5, 5)
        
        # File browser header
        header = QLabel("Project Files")
        header.setStyleSheet("font-weight: bold; padding: 5px;")
        file_layout.addWidget(header)
        
        # File tree
        self.file_tree = QTreeView()
        self.file_tree.setHeaderHidden(True)
        self.file_tree.setAnimated(True)
        self.file_tree.setIndentation(20)
        self.file_model = QStandardItemModel()
        self.file_tree.setModel(self.file_model)
        file_layout.addWidget(self.file_tree)
        
        # Right side - Code editor and chat
        editor_chat = QFrame()
        editor_layout = QVBoxLayout(editor_chat)
        editor_layout.setContentsMargins(0, 0, 0, 0)
        
        # Code editor
        editor_frame = QFrame()
        editor_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
        """)
        editor_inner_layout = QVBoxLayout(editor_frame)
        editor_inner_layout.setContentsMargins(5, 5, 5, 5)
        
        # Editor toolbar
        toolbar = QHBoxLayout()
        
        # File operations
        self.new_file_btn = QPushButton("New")
        self.open_file_btn = QPushButton("Open")
        self.save_file_btn = QPushButton("Save")
        
        for btn in [self.new_file_btn, self.open_file_btn, self.save_file_btn]:
            btn.setMaximumWidth(60)
            toolbar.addWidget(btn)
        
        toolbar.addStretch()
        
        # Language selector
        self.lang_selector = QComboBox()
        self.lang_selector.addItems(["Python", "JavaScript", "HTML", "CSS"])
        self.lang_selector.setMaximumWidth(100)
        toolbar.addWidget(self.lang_selector)
        
        editor_inner_layout.addLayout(toolbar)
        
        # Code editor
        self.code_editor = CodeEditor()
        editor_inner_layout.addWidget(self.code_editor)
        
        editor_layout.addWidget(editor_frame, stretch=7)
        
        # Chat interface
        chat_frame = QFrame()
        chat_frame.setStyleSheet("""
            QFrame {
                background-color: palette(base);
                border: 1px solid palette(mid);
                border-radius: 6px;
            }
        """)
        chat_layout = QVBoxLayout(chat_frame)
        chat_layout.setContentsMargins(5, 5, 5, 5)
        
        # Chat label
        chat_label = QLabel("AI Assistant")
        chat_label.setStyleSheet("font-weight: bold; padding: 5px;")
        chat_layout.addWidget(chat_label)
        
        # Chat input area
        chat_input_layout = QHBoxLayout()
        
        self.chat_input = QTextEdit()
        self.chat_input.setPlaceholderText("Ask about your code...")
        self.chat_input.setMaximumHeight(60)
        chat_input_layout.addWidget(self.chat_input)
        
        self.send_button = QPushButton("Ask")
        self.send_button.setMaximumWidth(60)
        self.send_button.clicked.connect(self.send_message)
        chat_input_layout.addWidget(self.send_button)
        
        chat_layout.addLayout(chat_input_layout)
        
        editor_layout.addWidget(chat_frame, stretch=3)
        
        # Add widgets to splitter
        splitter.addWidget(file_browser)
        splitter.addWidget(editor_chat)
        
        # Set initial sizes (25% - 75%)
        splitter.setSizes([250, 750])
        
        layout.addWidget(splitter)
        
        # Connect signals
        self.new_file_btn.clicked.connect(self.new_file)
        self.open_file_btn.clicked.connect(self.open_file)
        self.save_file_btn.clicked.connect(self.save_file)
        self.file_tree.clicked.connect(self.file_selected)
    
    def new_file(self):
        """Create a new file."""
        self.code_editor.clear()
    
    def open_file(self):
        """Open a file."""
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", "Python Files (*.py);;All Files (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    self.code_editor.setPlainText(f.read())
            except Exception as e:
                self.show_error(f"Error opening file: {str(e)}")
    
    def save_file(self):
        """Save the current file."""
        file_name, _ = QFileDialog.getSaveFileName(
            self, "Save File", "", "Python Files (*.py);;All Files (*.*)"
        )
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    f.write(self.code_editor.toPlainText())
            except Exception as e:
                self.show_error(f"Error saving file: {str(e)}")
    
    def file_selected(self, index):
        """Handle file selection in the tree view."""
        item = self.file_model.itemFromIndex(index)
        if item and not item.hasChildren():
            try:
                file_path = item.data()
                with open(file_path, 'r') as f:
                    self.code_editor.setPlainText(f.read())
            except Exception as e:
                self.show_error(f"Error opening file: {str(e)}")
    
    def send_message(self):
        """Send a message about the code to the AI."""
        message = self.chat_input.toPlainText().strip()
        if message:
            code = self.code_editor.toPlainText()
            try:
                response = self.chat_manager.get_code_help(message, code)
                # TODO: Display response in a better way
                self.chat_input.clear()
            except Exception as e:
                self.show_error(f"Error: {str(e)}")
    
    def show_error(self, message):
        """Show an error message."""
        # TODO: Implement proper error display
        print(f"Error: {message}")