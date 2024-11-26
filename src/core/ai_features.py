from PyQt6.QtCore import QObject, pyqtSignal
import re
import ast
import json
from pathlib import Path

class AIFeatures(QObject):
    analysis_complete = pyqtSignal(str, dict)  # file_path, results
    suggestion_ready = pyqtSignal(str, list)   # context, suggestions
    
    def __init__(self, chat_manager):
        super().__init__()
        self.chat_manager = chat_manager
        
    def analyze_code_structure(self, code, language):
        """Analyze code structure and complexity"""
        prompt = f"""Analyze this {language} code and provide detailed information about:
1. Code structure (classes, functions, etc.)
2. Complexity metrics
3. Potential issues
4. Best practices compliance

Code:
{code}

Provide the analysis in JSON format with these sections."""
        
        response = self.chat_manager.process_message(prompt)
        try:
            return json.loads(response)
        except:
            return {"error": "Failed to parse analysis"}
            
    def suggest_improvements(self, code, language):
        """Suggest code improvements"""
        prompt = f"""Review this {language} code and suggest improvements for:
1. Performance optimization
2. Code readability
3. Error handling
4. Security considerations

Code:
{code}

Provide specific suggestions with example code."""
        
        return self.chat_manager.process_message(prompt)
        
    def generate_documentation(self, code, language):
        """Generate documentation for code"""
        prompt = f"""Generate comprehensive documentation for this {language} code including:
1. Overview
2. Function/class documentation
3. Parameters and return values
4. Usage examples

Code:
{code}

Provide the documentation in markdown format."""
        
        return self.chat_manager.process_message(prompt)
        
    def explain_code(self, code, language, level="intermediate"):
        """Explain code with specified detail level"""
        prompt = f"""Explain this {language} code at a {level} level. Include:
1. Overall purpose
2. How it works
3. Key concepts used
4. Step-by-step explanation

Code:
{code}"""
        
        return self.chat_manager.process_message(prompt)
        
    def suggest_tests(self, code, language):
        """Suggest unit tests for code"""
        prompt = f"""Generate unit tests for this {language} code. Include:
1. Test cases
2. Edge cases
3. Input/output examples
4. Testing best practices

Code:
{code}

Provide complete test code examples."""
        
        return self.chat_manager.process_message(prompt)
        
    def refactor_code(self, code, language):
        """Suggest code refactoring"""
        prompt = f"""Suggest refactoring for this {language} code to improve:
1. Design patterns usage
2. Code organization
3. Maintainability
4. Reusability

Code:
{code}

Provide the refactored code with explanations."""
        
        return self.chat_manager.process_message(prompt)
        
    def generate_similar_code(self, code, language):
        """Generate similar code with variations"""
        prompt = f"""Generate 3 variations of this {language} code with:
1. Different approaches
2. Alternative implementations
3. Various design patterns

Original code:
{code}

Provide complete code examples with explanations."""
        
        return self.chat_manager.process_message(prompt)
        
    def debug_code(self, code, error_message, language):
        """Help debug code with error"""
        prompt = f"""Debug this {language} code that produces the following error:
Error: {error_message}

Code:
{code}

Provide:
1. Error analysis
2. Potential causes
3. Solutions
4. Fixed code example"""
        
        return self.chat_manager.process_message(prompt)
        
    def optimize_code(self, code, language):
        """Suggest performance optimizations"""
        prompt = f"""Analyze and optimize this {language} code for:
1. Time complexity
2. Space complexity
3. Resource usage
4. Algorithm efficiency

Code:
{code}

Provide optimized code with performance impact explanations."""
        
        return self.chat_manager.process_message(prompt) 