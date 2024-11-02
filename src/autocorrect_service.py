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
                        logging.StreamHandler()
                    ])

controller = Controller()

class Worker(QObject):
    show_dialog = pyqtSignal(str)

    def handle_custom_prompt(self, selected_text):
        self.show_dialog.emit(selected_text)


class CustomPromptDialog(QDialog):
    def __init__(self, parent=None, last_prompt=None, show_suggestions=None):
        super().__init__(parent)
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
                "Add Emojis": "Add (gen z) fitting emojis like 🫥💀😭👌🫵😂🏢✈️🧨😏🥶💦💅🗣️ to the text (they should "
                              "NOT be random and fit to th text). Correct spelling, grammar, punctuation, and capitalization.",
                "Add Emojis (old people)": "Add to the text some (boomer) emojis (they should NOT be randomly choosen "
                                           "and fit into to the text) here is a good list from often used emojis:"
                                           "😊😇🤣🤗☘️🙈👼😀🤩🫢🙏👍😎😍🙃😻😹. Sometimes just add an emoji after "
                                           "some activity mentioned or thing like for example after: we went to the "
                                           "beach ☀️🏖️. Correct spelling, grammar, punctuation, and capitalization.",
                "Translate": "Translate English to German or vice versa. Correct spelling, grammar, punctuation, and capitalization."
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
        self.selected_prompt = prompt
        self.accept()

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

    def get_selected_text(self):
        try:
            controller.release(Key.alt)
            pyperclip.copy('')
            time.sleep(0.1)
            with controller.pressed(Key.ctrl.value):
                controller.press('c')
                controller.release('c')
            controller.press(Key.alt)
            time.sleep(0.4)
            selected_text = pyperclip.paste()
            logging.info(f"Selected text: {selected_text}")
            return selected_text
        except Exception as e:
            logging.error(f"Error getting selected text: {e}")
            return ""

    def replace_selected_text(self, new_text):
        try:
            pyperclip.copy(new_text)

            controller.release(Key.alt)
            time.sleep(0.1)
            with controller.pressed(Key.ctrl.value):
                controller.press('v')
                controller.release('v')

            logging.info(f"Replaced text with: {new_text}")
        except Exception as e:
            logging.error(f"Error replacing text: {e}")

    def handle_rephrase_hotkey(self):
        if not self.enabled or not self.settings.get_setting('ai_rephrase'):
            return

        selected_text = self.get_selected_text()
        if not selected_text:
            return

        prompt = self.settings.get_setting('ai_rephrase_prompt') + selected_text

        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.get_setting('open_router_key')}",
            },
            data=json.dumps({
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

            })
        )

        if response.status_code == 200:
            response_data = response.json()
            response_text = response_data['choices'][0]['message']['content']
            suggestions = response_text.split('|')
            suggestions = [s.strip() for s in suggestions]

            logging.info(f"AI Suggestions: {suggestions}")
            self.replace_selected_text(suggestions[0])
            self.phrases = suggestions
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def fix_text(self):
        selected_text = self.get_selected_text()

        if not selected_text or selected_text.strip() == "":
            return

        for old, new in self.settings.get_setting('replacements').items():
            selected_text = re.sub(rf'\b{re.escape(old)}\b', new, selected_text)

        if self.settings.get_setting('german_noun_capitalization'):
            words = selected_text.split()
            selected_text = ' '.join([self.noun_capitalization(w) for w in words])

        if self.settings.get_setting('auto_punctuate'):
            selected_text = self.auto_punctuate(selected_text)

        if self.settings.get_setting('auto_capitalize'):
            selected_text = selected_text[:1].upper() + selected_text[1:]

        self.replace_selected_text(selected_text)

    def get_custom_prompt(self, selected_text):
        controller.release(Key.alt)
        show_suggestions = selected_text is not None and selected_text.strip() != ""
        dialog = CustomPromptDialog(last_prompt=self.last_prompt, show_suggestions=show_suggestions)

        if not show_suggestions:
            for child in dialog.findChildren(QPushButton):
                child.hide()

        dialog.exec()

        if dialog.result() == QDialog.DialogCode.Accepted:
            extracted = dialog.get_result()
            if extracted:
                self.last_prompt = extracted

                if not extracted:
                    return

                if not selected_text and selected_text.strip() != "":
                    prompt = extracted
                else:
                    prompt = f"{extracted}. This is the text, which should be modified (Only answer with the modified text " \
                             f"nothing else.): {selected_text}"

                response = requests.post(
                    url="https://openrouter.ai/api/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.get_setting('open_router_key')}",
                    },
                    data=json.dumps({
                        "model": "openai/gpt-4o-mini",
                        "messages": [
                            {
                                "role": "user",
                                "content": prompt
                            }
                        ]

                    })
                )

                if response.status_code == 200:
                    response_data = response.json()
                    translated_text = response_data['choices'][0]['message']['content']
                    self.replace_selected_text(translated_text)
                else:
                    print(f"Error: {response.status_code} - {response.text}")
                return
        return

    def switch_phrasings(self):
        if not self.phrases:
            return

        self.phrase_index += 1
        if self.phrase_index >= len(self.phrases):
            self.phrase_index = 0

        current_phrase = self.phrases[self.phrase_index]
        self.replace_selected_text(current_phrase)

    def handle_custom_prompt_hotkey(self):
        if not self.enabled:
            return
        controller.release(Key.alt)
        time.sleep(0.1)
        selected_text = self.get_selected_text()
        if not selected_text:
            selected_text = ""
        self.worker.handle_custom_prompt(selected_text)

    def handle_translation_hotkey(self):
        if not self.enabled:
            return

        selected_text = self.get_selected_text()
        if not selected_text or selected_text.strip() == "":
            return
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.settings.get_setting('open_router_key')}",
            },
            data=json.dumps({
                "model": "openai/gpt-4o-mini",
                "messages": [
                    {
                        "role": "user",
                        "content": self.settings.get_setting('ai_translation_prompt').replace("%alternative_language%",
                                                                                              self.settings.get_setting(
                                                                                                  'alternative_language')) + selected_text
                    }
                ]

            })
        )

        if response.status_code == 200:
            response_data = response.json()
            translated_text = response_data['choices'][0]['message']['content']
            self.replace_selected_text(translated_text)
        else:
            print(f"Error: {response.status_code} - {response.text}")

    def noun_capitalization(self, word):
        return word.capitalize() if self.is_german_noun(word) else word

    def auto_punctuate(self, text):
        if text.strip() and text.strip()[-1] not in '.!?':
            return text.rstrip() + '.'
        return text

    def is_german_noun(self, word):
        return False

    def is_proper_name(self, word):
        # TODO
        return False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def cleanup(self):
        self.listener.stop()
        self.worker_thread.quit()

    def setup_hotkeys(self):
        try:
            keyboard.add_hotkey(self.settings.get_setting('fix_hotkey'), self.fix_text)
            keyboard.add_hotkey(self.settings.get_setting('rephrase_hotkey'), self.handle_rephrase_hotkey)
            keyboard.add_hotkey(self.settings.get_setting('switch_phrasings'), self.switch_phrasings)
            keyboard.add_hotkey(self.settings.get_setting('translation_hotkey'), self.handle_translation_hotkey)
            keyboard.add_hotkey(self.settings.get_setting('custom_prompt_hotkey'), self.handle_custom_prompt_hotkey)
            logging.info("Hotkeys successfully set up")
        except Exception as e:
            logging.error(f"Error setting up hotkeys: {e}")

    def run(self):
        keyboard.wait()
