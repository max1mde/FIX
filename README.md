<div align="center">
  <h1>Autocorrect</h1>
</div>

![New Project - 2024-11-03T000755 649](https://github.com/user-attachments/assets/791142ed-fb65-4b33-b9df-5d44495e0192)


A Python-based autocorrect tool that enhances text input across Windows applications with:
- Automatic capitalization & punctuation
- AI-powered rephrasing with customizable hotkey
- System tray integration (Runs in background when closing)

## Requirements
- Python 3.10+
- Windows 10/11

## Installation

1. Clone the repository:
```bash
git clone https://github.com/max1mde/AutocorrectApp.git
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/Scripts/activate
```

3. Install requirements:
```bash
pip install -r requirements.txt
```

4. Create an API key on https://openrouter.ai/:


## Usage

1. Run the application:
```bash
python src/main.py
```

2. Configure settings in the popup window (Add the OpenRouter API key to the input field and save)
3. The app will minimize to system tray
4. Access settings anytime by right-clicking the tray icon

## Building Executable

To create a standalone executable:

```bash
pip install pyinstaller
pyinstaller main.spec
```

The executable will be created in the `dist` folder.

## Configuration

Settings are stored in `%APPDATA%/Autocorrect/settings.json`


