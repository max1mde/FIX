import json
from pathlib import Path
from typing import Dict, Any
import json


class SettingsManager:
    DEFAULT_SETTINGS = {
        'fix.capitalization': True,
        'fix.punctuate': False,
        'fix.german_noun_capitalization': True,
        'fix.name_capitalization': True,
        'fix.use_replacements': True,
        'fix.hotkey': 'Ctrl+F8',
        'fix.auto_fix_on_send': True,
        'rephrase.hotkey': 'Ctrl+F9',
        'rephrase.switch_phrasings_hotkey': 'Ctrl+F10',
        'rephrase.use_replacements': True,
        'rephrase.prompt': (
            'Provide 3 different concise rephrasing of '
            'the given text, separated by | characters. '
            'The first rephrasing should not be rephrased just correct all spelling, capitalization, grammar, '
            'and punctuation errors without changing wording.'
            '(If the text is longer than 30 words, only fix the text. Also keep the same language in all '
            'rephrasings). Here is the text:'
        ),
        'usage_stats': {
            'input_tokens': 0,
            'completion_tokens': 0,
            'total_cost': 0.0
        },
        'translate.hotkey': 'Ctrl+F11',
        'translate.use_replacements': True,
        'translate.alternative_language': 'german',
        'translate.prompt': (
            'You are a basic translater. (also additionally add punctuation and use correct spelling.) '
            'Translate the following text to English if it is in any other language than '
            'English, else translate it to %alternative_language% and ONLY answer with the '
            'translated message:'
        ),
        'custom_prompt.hotkey': 'Ctrl+F12',
        'custom_prompt.use_replacements': True,
        'custom_prompt.auto_custom_prompt': True,
        'command_execution.hotkey': 'Ctrl+F7',
        'command_execution.prompt': (
            'Convert this command to a PowerShell script. If impossible or really dangerous / destructive, respond with "This action is impossible". '
            'Output only the command. Do not include explanations, notes, or instructions. Examples:\n'
            '- "open discord" → Start-Process "C:\\Users\\$env:USERNAME\\AppData\\Local\\Discord\\Update.exe" --processStart Discord.exe\n'
            '- "shutdown in 30 minutes" → shutdown.exe /s /t 1800\n'
            'Convert this:'
        ),
        'auto_select_text': False,
        'provider_api_key': '',
        'api_endpoint': 'https://openrouter.ai/api/v1/chat/completions',
        'api_model': 'openai/gpt-4o-mini',
        'replacements': {}
    }

    def __init__(self) -> None:
        self.settings: Dict[str, Any] = {}
        self.app_data = Path.home() / 'AppData' / 'Roaming' / 'Autocorrect'
        self.settings_file = self.app_data / 'settings.json'
        self.replacements_file = './assets/lists/replacements.json'
        self._initialize_settings()

    def _initialize_settings(self) -> None:
        self.app_data.mkdir(parents=True, exist_ok=True)
        self.load_settings()

    def load_settings(self) -> None:
        try:
            if self.settings_file.exists():
                with self.settings_file.open('r', encoding='utf-8') as f:
                    self.settings = json.load(f)
            else:
                self.reset_settings()
        except (json.JSONDecodeError, PermissionError) as e:
            print(f"Error loading settings: {e}")
            self.reset_settings()

    def save_settings(self) -> None:
        try:
            with self.settings_file.open('w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=4, ensure_ascii=False)
        except (PermissionError, IOError) as e:
            print(f"Error saving settings: {e}")

    def get_setting(self, key: str, default: Any = None) -> Any:
        return self.settings.get(key, default)

    def get_default_setting(self, key: str, default: Any = None) -> Any:
        return self.DEFAULT_SETTINGS.get(key, default)

    def set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
        self.save_settings()

    def get_replacements(self) -> Dict[str, str]:
        return self.settings.get('replacements', {})

    def reset_settings(self) -> None:
        usage_stats = self.settings.get('usage_stats', self.DEFAULT_SETTINGS['usage_stats']).copy()
        provider_api_key = self.settings.get('provider_api_key', self.DEFAULT_SETTINGS['provider_api_key'])

        replacements = self.safe_file_read_json(self.replacements_file)

        if replacements:
            replacements_dict = dict(replacements)
        else:
            replacements_dict = self.DEFAULT_SETTINGS['replacements']

        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings['usage_stats'] = usage_stats
        self.settings['provider_api_key'] = provider_api_key
        self.settings['replacements'] = replacements_dict
        self.save_settings()

    def update_usage(self, input_tokens: int, completion_tokens: int) -> None:
        current_input = self.settings.get('usage_stats', {}).get('input_tokens', 0)
        current_completion = self.settings.get('usage_stats', {}).get('completion_tokens', 0)

        new_input = current_input + input_tokens
        new_completion = current_completion + completion_tokens

        # $0.15 per million input tokens
        # $0.60 per million completion tokens
        input_cost = (new_input / 1_000_000) * 0.15
        completion_cost = (new_completion / 1_000_000) * 0.60
        total_cost = input_cost + completion_cost
        self.settings['usage_stats'] = {
            'input_tokens': new_input,
            'completion_tokens': new_completion,
            'total_cost': total_cost
        }
        self.save_settings()

    def safe_file_read_json(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error reading file {filename}: {str(e)}")
            return {}
