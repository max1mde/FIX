from pynput.keyboard import Key, Controller
import time
import requests
import json
import pyperclip
import logging
import keyboard
import re
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QThread
from PyQt6.QtGui import QPainter, QColor, QCursor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QApplication

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        # logging.FileHandler('app.log')
                    ])

logger = logging.getLogger(__name__)
controller = Controller()


class Worker(QObject):
    show_dialog = pyqtSignal(str)

    def handle_custom_prompt(self, selected_text):
        try:
            self.show_dialog.emit(selected_text)
        except Exception as e:
            logger.error(f"Error in handle_custom_prompt: {str(e)}")


class CustomPromptDialog(QDialog):
    def __init__(self, parent=None, last_prompt=None, show_suggestions=None):
        super().__init__(parent)
        try:
            self.setup_ui(last_prompt, show_suggestions)
        except Exception as e:
            logger.error(f"Error initializing CustomPromptDialog: {str(e)}")
            self.close()

    def setup_ui(self, last_prompt, show_suggestions):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.selected_prompt = None

        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        top_layout = QHBoxLayout()
        top_layout.addStretch()

        self.is_dragging = False
        self.drag_position = QPoint()

        self.close_button = QPushButton("X")
        self.close_button.setFixedSize(20, 20)
        self.close_button.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(30, 30, 30, 0.9);
                        color: white;
                        border-radius: 10px;
                        font-size: 16px;
                        font-weight: bold;
                        padding: 0;
                        margin: 0;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 0, 0, 0.8);
                    }
                """)
        top_layout.addWidget(self.close_button)

        cursor_position = QCursor.pos()
        screen_geometry = QApplication.primaryScreen().geometry()

        if cursor_position.y() < screen_geometry.height() // 2:
            x_position = cursor_position.x() - (self.width() // 5) + 5
            y_position = cursor_position.y() + 80
        else:
            x_position = cursor_position.x() - (self.width() // 5) + 5
            y_position = cursor_position.y() - 190

        self.move(x_position, y_position)

        layout.addLayout(top_layout)

        self.prompt_input = QLineEdit()
        self.prompt_input.setPlaceholderText("Enter prompt...")
        self.prompt_input.setStyleSheet("""
                    QLineEdit {
                        background-color: rgba(20, 20, 20, 0.85);
                        border-radius: 15px;
                        padding: 10px;
                        font-size: 14px;
                        border: 1px solid #ccc;
                        color: white;
                    }
                """)
        layout.addWidget(self.prompt_input)

        if show_suggestions is not None:
            buttons_layout_top = QHBoxLayout()
            buttons_layout_bottom = QHBoxLayout()

            quick_actions = {
                "Fix": "Correct all spelling, capitalization, grammar, and punctuation errors without changing wording.",
                "Shorter": "Make the text shorter and more concise while maintaining the key message. Correct spelling, grammar, punctuation, and capitalization.",
                "Longer": "Expand the text with more detail while maintaining the same tone. Correct spelling, grammar, punctuation, and capitalization.",
                "Like Email": "Rewrite the text as a professional email",
                "Add Emoticons": "Add emoticons at the end of sentences which fit to the text. You can choose from "
                                 "this list: ._., :), :D, T-T, :(, <3, :3, 3:, xD, xd, XD. Correct spelling, grammar, punctuation, and capitalization.",
                "More Formal": "Make the text more formal and professional",
                "More Casual": "Make the text more casual and friendly",
                "Fix code": "Fix any mistakes (syntax or logic) in this code",
                "Improve code": "Improve the code in the in terms of readability, performance & conventions. Do not "
                                "include ```'s in the answer just the modified raw code. Also don't ",
                "Add Emojis": "Add (gen z) fitting emojis like 💀😭👌🫵😂🏢✈️🧨😏🥶💦💅🗣️ to the text (they should "
                              "NOT be random and fit to th text). Correct spelling, grammar, punctuation, "
                              "and capitalization. (Use max 1 emoji in a row)",
                "Add many Emojis (old people)": "Add to the text some (boomer) emojis (they should NOT be randomly "
                                                "choosen"
                                                "and fit into to the text) here is a good list from often used emojis:"
                                                "😊😇🤣🤗☘️🙈👼😀🤩🫢🙏👍😎😍🙃😻😹. Sometimes just add an emoji after "
                                                "some activity mentioned or thing like for example after: we went to "
                                                "the"
                                                "beach ☀️🏖️. Correct spelling, grammar, punctuation, "
                                                "and capitalization.",
                "Translate": "Translate English to German or vice versa. Correct spelling, grammar, punctuation, "
                             "and capitalization."
            }

            first_half = list(quick_actions.items())[:len(quick_actions) // 2]
            for action_name, action_prompt in first_half:
                btn = QPushButton(action_name)
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(30, 30, 30, 0.9);
                                color: white;
                                border-radius: 10px;
                                padding: 5px 10px;
                                margin: 2px;
                            }
                            QPushButton:hover {
                                background-color: rgba(70, 70, 70, 1);
                            }
                        """)
                buttons_layout_top.addWidget(btn)
                btn.clicked.connect(lambda checked, p=action_prompt: self.handle_quick_action(p))

            second_half = list(quick_actions.items())[len(quick_actions) // 2:]
            for action_name, action_prompt in second_half:
                btn = QPushButton(action_name)
                btn.setStyleSheet("""
                            QPushButton {
                                background-color: rgba(30, 30, 30, 0.9);
                                color: white;
                                border-radius: 10px;
                                padding: 5px 10px;
                                margin: 2px;
                            }
                            QPushButton:hover {
                                background-color: rgba(70, 70, 70, 1);
                            }
                        """)
                buttons_layout_bottom.addWidget(btn)
                btn.clicked.connect(lambda checked, p=action_prompt: self.handle_quick_action(p))

            layout.addLayout(buttons_layout_top)
            layout.addLayout(buttons_layout_bottom)

        self.prompt_input.returnPressed.connect(self.handle_return_pressed)
        self.close_button.clicked.connect(self.reject)

    def handle_quick_action(self, prompt):
        try:
            self.selected_prompt = prompt
            self.accept()
        except Exception as e:
            logger.error(f"Error in handle_quick_action: {str(e)}")

    def handle_return_pressed(self):
        self.selected_prompt = self.prompt_input.text()
        self.accept()

    def get_result(self):
        return self.selected_prompt

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(1, 1, 1, 170))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.is_dragging and event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            event.accept()


class AutocorrectService:
    def __init__(self, settings_manager):
        try:
            self.settings = settings_manager
            self.enabled = True
            self.phrase_index = 0
            self.phrases = []
            self.last_prompt = None
            self.worker = Worker()
            self.worker_thread = QThread()
            self.worker.moveToThread(self.worker_thread)
            self.worker.show_dialog.connect(self.get_custom_prompt)
            self.worker_thread.start()
        except Exception as e:
            logger.error(f"Error initializing AutocorrectService: {str(e)}")

    def make_api_request(self, prompt, retry_count=3):
        for attempt in range(retry_count):
            try:
                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.get_setting('open_router_key')}",
                    },
                    data=json.dumps({
                        "model": "openai/gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}]
                    }),
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                logger.error(f"API request attempt {attempt + 1} failed: {str(e)}")
                if attempt == retry_count - 1:
                    raise
                time.sleep(1)

    def get_selected_text(self):
        try:
            pyperclip.copy('')
            time.sleep(0.1)
            if self.settings.get_setting('auto_select_text'):
                with controller.pressed(Key.ctrl.value):
                    controller.press('a')
                    controller.release('a')
                time.sleep(0.1)
            with controller.pressed(Key.ctrl.value):
                controller.press('c')
                controller.release('c')
            time.sleep(0.4)
            selected_text = pyperclip.paste()
            return selected_text.strip()
        except Exception as e:
            logger.error(f"Error getting selected text: {str(e)}")
            return ""

    def replace_selected_text(self, new_text):
        if not new_text:
            logger.warning("Attempted to replace with empty text")
            return

        try:
            pyperclip.copy(new_text)
            time.sleep(0.1)
            if self.settings.get_setting('auto_select_text'):
                with controller.pressed(Key.ctrl.value):
                    controller.press('a')
                    controller.release('a')
                time.sleep(0.1)
            with controller.pressed(Key.ctrl.value):
                controller.press('v')
                controller.release('v')
        except Exception as e:
            logger.error(f"Error replacing text: {str(e)}")

    def handle_rephrase_hotkey(self):
        try:
            selected_text = self.get_selected_text()
            if not selected_text:
                return

            if self.settings.get_setting('fix.use_replacements'):
                for old, new in self.settings.get_setting('replacements').items():
                    selected_text = re.sub(rf'\b{re.escape(old)}\b', new, selected_text)

            prompt = self.settings.get_setting('rephrase.prompt') + selected_text

            try:
                response_data = self.make_api_request(prompt)
                response_text = response_data['choices'][0]['message']['content']
                suggestions = [s.strip() for s in response_text.split('|')]

                if suggestions:
                    self.replace_selected_text(suggestions[0])
                    self.phrases = suggestions
                else:
                    logger.warning("No suggestions received from API")
            except Exception as e:
                logger.error(f"Error in API communication: {str(e)}")

        except Exception as e:
            logger.error(f"Error in handle_rephrase_hotkey: {str(e)}")

    def fix_text(self):
        try:
            selected_text = self.get_selected_text()
            if not selected_text:
                return

            if self.settings.get_setting('fix.use_replacements'):
                for old, new in self.settings.get_setting('replacements').items():
                    selected_text = re.sub(rf'\b{re.escape(old)}\b', new, selected_text)

            if self.settings.get_setting('fix.german_noun_capitalization'):
                words = selected_text.split()
                selected_text = ' '.join([self.noun_capitalization(w) for w in words])

            if self.settings.get_setting('fix.name_capitalization'):
                words = selected_text.split()
                selected_text = ' '.join([self.name_capitalization(w) for w in words])

            if self.settings.get_setting('fix.punctuate'):
                selected_text = self.auto_punctuate(selected_text)

            if self.settings.get_setting('fix.capitalization'):
                selected_text = selected_text[:1].upper() + selected_text[1:]

            self.replace_selected_text(selected_text)
        except Exception as e:
            logger.error(f"Error in fix_text: {str(e)}")

    def get_custom_prompt(self, selected_text):
        try:
            show_suggestions = selected_text is not None and selected_text.strip() != ""
            dialog = CustomPromptDialog(last_prompt=self.last_prompt, show_suggestions=show_suggestions)

            if not show_suggestions:
                for child in dialog.findChildren(QPushButton):
                    child.hide()

            if dialog.exec() == QDialog.DialogCode.Accepted:
                extracted = dialog.get_result()
                if extracted:
                    self.last_prompt = extracted
                    prompt = extracted if not selected_text else f"{extracted}. This is the text, which should be modified (Only answer with the modified text nothing else.): {selected_text}"

                    try:
                        response_data = self.make_api_request(prompt)
                        translated_text = response_data['choices'][0]['message']['content']
                        if translated_text:
                            self.replace_selected_text(translated_text)
                    except Exception as e:
                        logger.error(f"Error in API communication: {str(e)}")
        except Exception as e:
            logger.error(f"Error in get_custom_prompt: {str(e)}")

    def switch_phrasings(self):
        try:
            if not self.phrases:
                logger.warning("No phrases available to switch between")
                return

            self.phrase_index = (self.phrase_index + 1) % len(self.phrases)
            current_phrase = self.phrases[self.phrase_index]

            if current_phrase:
                self.replace_selected_text(current_phrase)
            else:
                logger.warning("Current phrase is empty")
        except Exception as e:
            logger.error(f"Error in switch_phrasings: {str(e)}")

    def handle_translation_hotkey(self):
        try:
            if not self.enabled:
                return

            selected_text = self.get_selected_text()
            if not selected_text:
                return

            if self.settings.get_setting('fix.use_replacements'):
                for old, new in self.settings.get_setting('replacements').items():
                    selected_text = re.sub(rf'\b{re.escape(old)}\b', new, selected_text)

            prompt = self.settings.get_setting('translate.prompt').replace(
                "%alternative_language%",
                self.settings.get_setting('translate.alternative_language')
            ) + selected_text

            try:
                response_data = self.make_api_request(prompt)
                translated_text = response_data['choices'][0]['message']['content']
                if translated_text:
                    self.replace_selected_text(translated_text)
                else:
                    logger.warning("Received empty translation from API")
            except Exception as e:
                logger.error(f"Error in translation API request: {str(e)}")

        except Exception as e:
            logger.error(f"Error in handle_translation_hotkey: {str(e)}")

    def handle_custom_prompt_hotkey(self):
        try:
            if not self.enabled:
                return

            time.sleep(0.1)
            selected_text = self.get_selected_text()

            if not selected_text:
                selected_text = ""

            if self.settings.get_setting('fix.use_replacements'):
                for old, new in self.settings.get_setting('replacements').items():
                    selected_text = re.sub(rf'\b{re.escape(old)}\b', new, selected_text)

            self.worker.handle_custom_prompt(selected_text)

        except Exception as e:
            logger.error(f"Error in handle_custom_prompt_hotkey: {str(e)}")

    def safe_file_read(self, filename):
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                return set(file.read().splitlines())
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            return set()

    def noun_capitalization(self, word):
        try:
            return word.capitalize() if self.is_german_noun(word) else word
        except Exception as e:
            logger.error(f"Error in noun_capitalization for word '{word}': {str(e)}")
            return word

    def name_capitalization(self, word):
        try:
            return word.capitalize() if self.is_name(word) else word
        except Exception as e:
            logger.error(f"Error in name_capitalization for word '{word}': {str(e)}")
            return word

    def auto_punctuate(self, text):
        try:
            if not text:
                return text

            text = text.strip()
            if text and text[-1] not in '.!?':
                return text + '.'
            return text
        except Exception as e:
            logger.error(f"Error in auto_punctuate: {str(e)}")
            return text

    def is_german_noun(self, word):
        german_nouns = self.safe_file_read('./assets/lists/german_nouns.txt')
        return word.lower() in (noun.lower() for noun in german_nouns)

    def is_name(self, word):
        names = self.safe_file_read('./assets/lists/names.txt')
        return word.lower() in (name.lower() for name in names)

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(self.settings.get_setting('fix.hotkey'), self.fix_text)
            keyboard.add_hotkey(self.settings.get_setting('rephrase.hotkey'), self.handle_rephrase_hotkey)
            keyboard.add_hotkey(self.settings.get_setting('rephrase.switch_phrasings_hotkey'), self.switch_phrasings)
            keyboard.add_hotkey(self.settings.get_setting('translate.hotkey'), self.handle_translation_hotkey)
            keyboard.add_hotkey(self.settings.get_setting('custom_prompt.hotkey'), self.handle_custom_prompt_hotkey)
            logger.info("Hotkeys successfully set up")
        except Exception as e:
            logger.error(f"Error setting up hotkeys: {str(e)}")

    def cleanup(self):
        try:
            self.worker_thread.quit()
            self.worker_thread.wait()
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")

    def run(self):
        try:
            keyboard.wait()
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
