import json
import os
from pathlib import Path

class SettingsManager:
    def __init__(self):
        self.settings = None
        self.app_data = Path(os.getenv('APPDATA')) / 'Autocorrect'
        self.app_data.mkdir(exist_ok=True)
        self.settings_file = self.app_data / 'settings.json'
        self.load_settings()

    def load_settings(self):
        if self.settings_file.exists():
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.reset_settings()

    def save_settings(self):
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get_setting(self, key, default=None):
        return self.settings.get(key, default)

    def set_setting(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def get_replacements(self):
        return self.settings.get('replacements', {})

    def reset_settings(self):
        self.settings = {
            'fix.capitalization': True,
            'fix.punctuate': True,
            'fix.german_noun_capitalization': True,
            'fix.use_replacements': True,
            'fix.hotkey': 'Ctrl+F8',
            'fix.auto_fix_on_send': True,
            'rephrase.hotkey': 'Ctrl+F9',
            'rephrase.switch_phrasings_hotkey': 'Ctrl+F10',
            'rephrase.use_replacements': True,
            'rephrase.prompt': 'You are a helpful writing assistant. Provide 3 different concise rephrasing of '
                             'the given text, separated by | characters. Please provide 3 alternative '
                             'phrasings for the following text (The first one just spelling and punctuation '
                             'fixes no different words, only the next phrases should contain alternative words) '
                             '(if the text is longer than 20 words only one alternative phrasing):',

            'translate.hotkey': 'Ctrl+F11',
            'translate.use_replacements': True,
            'translate.alternative_language': 'german',
            'translate.prompt': 'You are a basic translater. Add punctuation and use correct spelling. '
                              'Translate the following text to English if it is in any other language than '
                              'English, else translate it to %alternative_language% and ONLY answer with the '
                              'translated message:',

            'custom_prompt.hotkey': 'Ctrl+F12',
            'custom_prompt.use_replacements': True,
            'custom_prompt.auto_custom_prompt': True,
            'custom_prompt.auto_select_text': True,

            'open_router_key': '',
            'replacements': {
                'i': 'I',
                'jz': 'jetzt',
                'ig': 'I guess',
                'u': 'you',
                'ur': 'your',
                'r': 'are',
                'b4': 'before',
                'btw': 'by the way',
                'tbh': 'to be honest',
                'idc': 'I don’t care',
                'idk': 'I have no idea',
                'imho': 'in my humble opinion',
                'np': 'no problem',
                'nvm': 'never mind',
                'omg': 'oh my god',
                'pls': 'please',
                'tho': 'though',
                'thx': 'thanks',
                'ty': 'thank you',
                'wanna': 'want to',
                'gonna': 'going to',
                'gotta': 'got to',
                'k': 'okay',
                'ok': 'okay',
                'alr': 'alright',
                'lmk': 'let me know',
                'bc': 'because',
                'atm': 'at the moment',
                'ppl': 'people',
                'asap': 'as soon as possible',
                'brb': 'be right back',
                'ftw': 'for the win',
                'imo': 'in my opinion',
                'irl': 'in real life',
                'jk': 'just kidding',
                'fyi': 'for your information',
                'omw': 'on my way',
                'sry': 'sorry',
                'ily': 'I love you',
                'wyd': 'what are you doing',
                'ttyl': 'talk to you later',
                'fr': 'for real',
                'hbu': 'how about you',
                'rn': 'right now',
                'afaik': 'as far as I know',
                'smth': 'something',
                'bcuz': 'because',
                'cuz': 'because',
                'ttys': 'talk to you soon',
                'sup': 'what’s up',
                'imma': 'I am going to',
                'ive': 'I have',
                'ofc': 'of course',
                'rlly': 'really',
                'yt': 'YouTube',
                'tt': 'TikTok',
                'dc': 'Discord',
                'insta': 'Instagram',
                'bb': 'Bye',
            }
        }
        self.save_settings()