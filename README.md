<div align="center">
  <img src="https://github.com/user-attachments/assets/1382fa43-056d-420a-93f5-902eec7ca826">
</div>

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


