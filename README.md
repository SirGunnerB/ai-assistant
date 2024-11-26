# AI Assistant

A desktop application that provides an offline-capable AI assistant with chat, code, and image generation capabilities.

## Features

- 💬 Chat Interface: Interact with AI models through a user-friendly chat interface
- 💻 Code Generation: Generate and analyze code with AI assistance
- 🖼️ Image Generation: Create images using AI models
- 🔌 Plugin System: Extend functionality through plugins
- 🎨 Theme Support: Dark theme for comfortable usage
- 📱 Modern UI: Built with PyQt6 for a responsive and modern interface

## Requirements

- Python 3.8 or higher
- PyQt6
- GPT4All
- Other dependencies listed in requirements.txt

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-assistant.git
cd ai-assistant
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On Unix or MacOS
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the application:
```bash
python src/main.py
```

On first launch, the application will prompt you to download the required AI model (approximately 4GB).

## Project Structure

```
ai-assistant/
├── src/
│   ├── core/           # Core functionality
│   ├── gui/            # User interface
│   │   └── tabs/       # Application tabs
│   └── main.py         # Application entry point
├── models/             # Downloaded AI models
├── reports/            # Bug reports and logs
└── requirements.txt    # Project dependencies
```

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 