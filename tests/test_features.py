import sys
import os
import json
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.model_manager import ModelManager
from src.core.chat_manager import ChatManager
from src.core.ai_features import AIFeatures
from src.core.file_manager import FileManager

def wait_for_download(model_manager, model_name):
    """Wait for model download to complete"""
    download_complete = False
    
    def on_download_complete(completed_model):
        nonlocal download_complete
        if completed_model == model_name:
            download_complete = True
    
    model_manager.download_completed.connect(on_download_complete)
    
    while not download_complete:
        time.sleep(1)
        print("Waiting for download to complete...")

def test_code_analysis():
    # Initialize managers
    model_manager = ModelManager()
    chat_manager = ChatManager(model_manager)
    ai_features = AIFeatures(chat_manager)
    file_manager = FileManager()

    # Test code to analyze
    test_code = """
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def main():
    # Calculate first 10 Fibonacci numbers
    for i in range(10):
        print(fibonacci(i))

if __name__ == "__main__":
    main()
"""

    # Create a test file
    test_file = "workspace/test_code.py"
    file_manager.create_file(test_file, test_code)

    print("Testing Code Analysis Features:")
    print("-" * 50)

    # Test structure analysis
    print("\n1. Code Structure Analysis:")
    analysis = ai_features.analyze_code_structure(test_code, "Python")
    print(json.dumps(analysis, indent=2))

    # Test improvements suggestion
    print("\n2. Code Improvements:")
    improvements = ai_features.suggest_improvements(test_code, "Python")
    print(improvements)

    # Test documentation generation
    print("\n3. Documentation Generation:")
    docs = ai_features.generate_documentation(test_code, "Python")
    print(docs)

    # Test code explanation
    print("\n4. Code Explanation:")
    explanation = ai_features.explain_code(test_code, "Python")
    print(explanation)

    # Test optimization suggestions
    print("\n5. Optimization Suggestions:")
    optimization = ai_features.optimize_code(test_code, "Python")
    print(optimization)

def test_file_management():
    file_manager = FileManager()

    print("\nTesting File Management:")
    print("-" * 50)

    # Test file creation
    test_file = "workspace/test.py"
    content = "print('Hello, World!')"
    file_manager.create_file(test_file, content)
    print(f"\nCreated file: {test_file}")

    # Test file reading
    read_content = file_manager.read_file(test_file)
    print(f"Read content: {read_content}")

    # Test file type detection
    file_type = file_manager.get_file_type(test_file)
    print(f"Detected file type: {file_type}")

    # Test file history
    file_manager.write_file(test_file, content + "\nprint('Updated!')")
    print(f"File history: {file_manager.file_history[test_file]}")

if __name__ == "__main__":
    print("Starting Feature Tests\n")
    
    # Initialize model manager
    model_manager = ModelManager()
    print("Checking for default model...")
    
    # Ensure model is downloaded and loaded
    model_manager.ensure_model_available(model_manager.default_model)
    
    print("Loading model...")
    model_manager.load_model(model_manager.default_model)
    
    # Run tests
    test_code_analysis()
    test_file_management() 