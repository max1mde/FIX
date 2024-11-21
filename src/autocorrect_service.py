from pynput.keyboard import Key, Controller
import time
import requests
import json
import pyperclip
import logging
import keyboard
import re
import tiktoken
from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QObject, QThread, QTimer
from PyQt6.QtGui import QPainter, QColor, QCursor
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QApplication, QMessageBox, \
    QLabel, QWidget

import speech_recognition as sr
import pyttsx3
import threading
import queue
import datetime
from rapidfuzz import fuzz

from command_executer import CommandExecutor

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),
                        # logging.FileHandler('app.log')
                    ])

logger = logging.getLogger(__name__)
controller = Controller()


class VoiceControl:
    def __init__(self, autocorrect_service, settings, handle_translation_hotkey, fix_text, execute_command, handle_custom_prompt_hotkey, make_api_request):
        self.service = autocorrect_service
        self.settings = settings
        self.handle_translation_hotkey = handle_translation_hotkey
        self.fix_text = fix_text
        self.make_api_request = make_api_request
        self.execute_command = execute_command
        self.handle_custom_prompt_hotkey = handle_custom_prompt_hotkey
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.language = self.settings.get_setting('voice_control.language', 'en-US')
        self.microphone_device = self.settings.get_setting('voice_control.microphone', None)
        self.text_queue = queue.Queue()
        self.stop_listening = False
        self.engine = pyttsx3.init()

        self.notification_worker = VoiceNotificationWorker()
        self.notification_thread = QThread()
        self.notification_worker.moveToThread(self.notification_thread)

        self.notification_popup = VoiceNotificationPopup()

        self.notification_worker.show_notification.connect(
            self.notification_popup.show_notification
        )

        self.notification_thread.start()

    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def recognize_speech(self):
        MAX_COMMAND_TIME = 20
        pause_time = self.settings.get_setting('voice_control.pause_settings', 3)
        trigger = self.service.settings.get_setting('voice_control.trigger_name', 'fix').lower()

        similarity_threshold = 85
        trigger_words = trigger.split()

        with sr.Microphone(device_index=self.microphone_device) as source:

            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while not self.stop_listening and self.settings.get_setting("voice_control.enabled", False):
                try:
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=None)

                    try:
                        text = self.recognizer.recognize_google(audio, language=self.language)
                        print(f"Heard: {text}")

                        if text.lower() == "stop" or text.lower() == "stopp":
                            self.speak("Ok cancelled")
                            break

                        text_lower = text.lower()

                        words = text_lower.split()

                        #approximate trigger match
                        trigger_index = -1
                        for i in range(len(words) - len(trigger_words) + 1):
                            segment = " ".join(words[i:i + len(trigger_words)])
                            if fuzz.ratio(segment, trigger) >= similarity_threshold:
                                trigger_index = i
                                break

                        if trigger_index != -1:
                            print(f"Trigger word '{trigger}' detected. Processing command...")
                            self.notification_worker.show_notification.emit(text, 3000)


                            command_text = text_lower[trigger_index + len(trigger):].strip()
                            print(f"Initial command: {command_text}")
                            self.notification_worker.show_notification.emit("Understanding...", 1000)

                            full_command = [command_text]
                            start_time = time.time()
                            last_successful_recognition = time.time()

                            while True:
                                if time.time() - start_time > MAX_COMMAND_TIME:
                                    print("Maximum command time reached, processing command")
                                    break
                                try:

                                    additional_audio = self.recognizer.listen(
                                        source,
                                        timeout=1,
                                        phrase_time_limit=None
                                    )

                                    try:
                                        additional_text = self.recognizer.recognize_google(
                                            additional_audio,
                                            language=self.language
                                        )


                                        if trigger in additional_text.lower():
                                            print("New trigger detected, resetting command")
                                            break

                                        full_command.append(additional_text.lower())
                                        print(f"Added to command: {additional_text}")
                                        last_successful_recognition = time.time()

                                    except sr.UnknownValueError:

                                        if time.time() - last_successful_recognition > pause_time:
                                            break
                                        continue

                                except sr.WaitTimeoutError:

                                    if time.time() - last_successful_recognition > pause_time:
                                        break
                                    continue

                            final_command = " ".join(full_command).strip()
                            if len(final_command.split()) < 2:
                                print("Command too short, ignoring")
                                continue
                            print(f"Full Command: {final_command}")
                            if final_command:
                                self.process_voice_command(final_command)

                    except sr.UnknownValueError:
                        pass
                    except sr.RequestError as e:
                        print(f"Could not request results; {e}")

                except Exception as e:
                    print(f"Unexpected error in speech recognition: {str(e)}")
                    import traceback
                    traceback.print_exc()

    def process_voice_command(self, command):

        action_type = self.detect_voice_command_type(command)
        print(f"Detected Action Type: {action_type}")

        if action_type == 'translate' and self.settings.get_setting('voice_control.translate_module'):
            self.notification_worker.show_notification.emit("Translating...", 3000)
            self.handle_translation_hotkey()

        elif action_type == 'mark' and self.settings.get_setting('voice_control.fix_module'):
            controller = Controller()
            with controller.pressed(Key.ctrl):
                controller.press('a')
                controller.release('a')

        elif action_type == 'command' and self.settings.get_setting('voice_control.command_execution_module'):
            self.notification_worker.show_notification.emit("Understanding task...", 1000)
            time.sleep(1)
            self.notification_worker.show_notification.emit("Thinking about the steps needed...", 1000)
            time.sleep(1)
            self.notification_worker.show_notification.emit("Executing task...", 4000)
            self.execute_command(command)

        elif action_type == 'fix' and self.settings.get_setting('voice_control.fix_module'):
            self.notification_worker.show_notification.emit("Fixing text...", 3000)
            self.fix_text()

        elif action_type == 'question' and self.settings.get_setting('voice_control.question_module'):
            self.notification_worker.show_notification.emit("Thinking...", 1500)
            jetzt = datetime.datetime.now()
            response_data = self.make_api_request("(Additional info: Date:"+str(jetzt.date())+" Time: "+str(jetzt.time())+") " + command + " (very short answer and no markdown)")
            response = response_data['choices'][0]['message']['content'].strip().lower()
            self.notification_worker.show_notification.emit(response, 7000)
            print(response)
            self.speak(response)

        return True


    def start(self):
        self.stop_listening = False
        threading.Thread(target=self.recognize_speech, daemon=True).start()

    def stop(self):
        self.stop_listening = True

    def detect_voice_command_type(self, command_text):
        prompt = (
            "Analyze the voice command (language doesn't matter). Return ONE action type (what the user wants to do): "
            "'translate', 'mark', 'command', 'fix', 'question', 'none'. "
            "Use 'command' for PC actions like opening apps/browsers or system interactions (or pressing hotkeys). "
            "Use 'translate', or 'fix', for text modification actions (like: translate the marked text). "
            "Use 'question', if user wants to know something"
            f"(Answer only with type) Users command: {command_text}"
        )

        try:
            response_data = self.make_api_request(prompt)
            action_type = response_data['choices'][0]['message']['content'].strip().lower()
            return action_type
        except Exception as e:
            logger.error(f"Error detecting command type: {str(e)}")
            return 'none'


class VoiceNotificationPopup(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.label = QLabel(self)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        screen = QApplication.primaryScreen().geometry()
        self.label.setFixedSize(320, 80)
        self.label.setWordWrap(True)


        self.setGeometry(
            screen.width() - 400,
            screen.height() - 150,
            350,
            100
        )

        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.hide)

    def show_notification(self, text, duration=3000):
        self.label.setText(text)
        self.show()
        self.hide_timer.start(duration)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(30, 30, 30, 180))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 15, 15)

class VoiceNotificationWorker(QObject):
    show_notification = pyqtSignal(str, int)

class Worker(QObject):
    show_dialog = pyqtSignal(str)
    show_command_dialog = pyqtSignal(str)
    show_notification = pyqtSignal(str, int)
    def handle_custom_prompt(self, selected_text):
        try:
            self.show_dialog.emit(selected_text)
        except Exception as e:
            logger.error(f"Error in handle_custom_prompt: {str(e)}")

    def handle_command_execution(self):
        try:
            self.show_command_dialog.emit("")
        except Exception as e:
            logger.error(f"Error in handle_command_execution: {str(e)}")

class CommandExecutionDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setup_ui()
        except Exception as e:
            logger.error(f"Error initializing CommandExecutionDialog: {str(e)}")
            self.close()

    def setup_ui(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup | Qt.WindowType.NoDropShadowWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setModal(True)
        self.selected_command = None

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
        x_position = cursor_position.x() - (self.width() // 5) + 5
        y_position = cursor_position.y() + 80
        self.move(x_position, y_position)

        layout.addLayout(top_layout)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Enter command (e.g., 'open browser', 'shutdown pc in 20 minutes'...)")
        self.command_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(20, 20, 20, 0.85);
                border-radius: 15px;
                padding: 10px;
                font-size: 14px;
                border: 1px solid #ccc;
                color: white;
            }
        """)
        layout.addWidget(self.command_input)
        self.command_input.setFocus()
        quick_actions = {
            "Open Recycle Bin": "open recycle bin",
            "Minimize windows": "minimize all windows",
            "Create and open file on desktop": "create a file on desktop called test.txt and open it",
            "Skip song and open yt": "open spotify, wait and skip song, wait and open rick roll on youtube",
            "Open device manager": "open the windows device manager app",
        }

        buttons_layout = QHBoxLayout()
        for action_name, action_command in quick_actions.items():
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
            buttons_layout.addWidget(btn)
            btn.clicked.connect(lambda checked, c=action_command: self.handle_quick_action(c))

        layout.addLayout(buttons_layout)

        self.command_input.returnPressed.connect(self.handle_return_pressed)
        self.close_button.clicked.connect(self.reject)

    def handle_quick_action(self, command):
        try:
            self.selected_command = command
            self.accept()
        except Exception as e:
            logger.error(f"Error in handle_quick_action: {str(e)}")

    def handle_return_pressed(self):
        self.selected_command = self.command_input.text()
        self.accept()

    def get_result(self):
        return self.selected_command

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

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.command_input.setFocus()
        QApplication.processEvents()


class CustomPromptDialog(QDialog):
    def __init__(self, parent=None, last_prompt=None, show_suggestions=None):
        super().__init__(parent)
        self.last_prompt = last_prompt
        try:
            self.setup_ui(show_suggestions)
        except Exception as e:
            logger.error(f"Error initializing CustomPromptDialog: {str(e)}")
            self.close()

    def setup_ui(self, show_suggestions):
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
        self.prompt_input.setFocus()

        if show_suggestions is not None:

            quick_actions = {
                "Fix": "Correct all spelling, grammar, capitalization, and punctuation errors without changing wording.",

                "Shorter": "Shorten the text while maintaining meaning and correcting spelling, grammar, punctuation, "
                           "and capitalization.",

                "Longer": "Expand the text with more detail while preserving tone and correcting spelling, grammar, "
                          "punctuation, and capitalization.",

                "Like Email": "Rewrite the text as a professional or casual email, depending on context.",

                "Add Emoticons": "Add fitting emoticons at the end of sentences (choose from ._., :), :D, T-T, :(, "
                                 "<3, :3, 3:, xD, xd, XD). Correct spelling, grammar, punctuation, and capitalization.",

                "More Formal": "Make the text more formal and professional, with corrections to spelling, grammar, "
                               "punctuation, and capitalization.",

                "More Casual": "Make the text more casual and friendly, with corrections to spelling, grammar, "
                               "punctuation, and capitalization.",

                "Fix Code": "Correct any syntax or logical errors in the code. Keep the same formatting as in the "
                            "provided code.",

                "Improve Code": "Improve code readability, performance, and conventions. Keep the same formatting as "
                                "in the provided code.",

                "Add Emojis": "Add relevant Gen Z emojis (e.g., 💀, 😂, 🫵, 😭, 🗣️, 👌) that match the tone of the "
                              "text. Correct"
                              "spelling, grammar, punctuation, and capitalization.",

                "Add Emojis (Boomer)": "Add fitting 'boomer' emojis (e.g., 😊, 👍, 😇, 😎, 🤣, 🤗, 🙈, 🤩,) where "
                                       "appropriate. Correct"
                                       "spelling, grammar, punctuation, and capitalization.",

                "Translate": "Translate between English and German, preserving meaning rather than a literal "
                             "translation. Correct spelling, grammar, punctuation, and capitalization.",

                "Paraphrase": "Rephrase the text to convey the same meaning in different words while maintaining "
                              "clarity and tone.",

                "Bullet Points": "Transform the text into concise bullet points for easier reading.",
            }

            buttons_layout_top = QHBoxLayout()
            buttons_layout_bottom = QHBoxLayout()

            if self.last_prompt:
                last_prompt_btn = QPushButton("Last Prompt")
                last_prompt_btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(30, 40, 90, 0.9); 
                        color: white;
                        border-radius: 10px;
                        padding: 5px 10px;
                        margin: 2px;
                    }
                    QPushButton:hover {
                        background-color: rgba(70, 80, 120, 1); 
                    }
                """)
                buttons_layout_top.addWidget(last_prompt_btn)
                last_prompt_btn.clicked.connect(self.handle_last_prompt)

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

    def handle_last_prompt(self):
        if self.last_prompt:
            self.handle_quick_action(self.last_prompt)

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

    def showEvent(self, event):
        super().showEvent(event)
        self.activateWindow()
        self.prompt_input.setFocus()
        QApplication.processEvents()
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
            self.tokenizer = tiktoken.encoding_for_model("gpt-4o")
        except Exception as e:
            logger.error(f"Error initializing Tiktoken tokenizer: {str(e)}")
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
            self.worker.show_command_dialog.connect(self.get_command_execution)
            self.worker_thread.start()
            self.setup_hotkeys()
            self.voice_control = VoiceControl(self, self.settings, self.handle_translation_hotkey, self.fix_text, self.execute_command, self.handle_custom_prompt_hotkey, self.make_api_request)
            self.voice_control.start()
        except Exception as e:
            logger.error(f"Error initializing AutocorrectService: {str(e)}")

    def count_tokens(self, text: str) -> int:
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            return 0

    def make_api_request(self, prompt, retry_count=3):
        for attempt in range(retry_count):
            try:
                input_tokens = self.count_tokens(prompt)
                response = requests.post(
                    url=f"{self.settings.get_setting('api_endpoint', 'https://openrouter.ai/api/v1/chat/completions')}",
                    headers={
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {self.settings.get_setting('provider_api_key')}",
                    },
                    data=json.dumps({
                        "model": f"{self.settings.get_setting('api_model', 'openai/gpt-4o-mini')}",
                        "messages": [{"role": "user", "content": prompt}]
                    }),
                    timeout=10
                )
                response.raise_for_status()

                response_data = response.json()

                response.raise_for_status()

                completion_text = response_data['choices'][0]['message']['content']
                completion_tokens = self.count_tokens(completion_text)

                default_endpoint = self.settings.get_default_setting('api_endpoint')
                default_model = self.settings.get_default_setting('api_model')

                if (self.settings.get_setting('api_endpoint') == default_endpoint and
                        self.settings.get_setting('api_model') == default_model):
                    self.settings.update_usage(input_tokens, completion_tokens)

                return response_data
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
                    prompt = extracted if not selected_text else f"{extracted}. Modify this text (Only reply with the " \
                                                                 f"modified text, nothing else): {selected_text}"

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

    def handle_command_execution_hotkey(self):
        try:
            if not self.enabled:
                return

            self.worker.handle_command_execution()

        except Exception as e:
            logger.error(f"Error in handle_command_execution_hotkey: {str(e)}")

    def get_command_execution(self, _):
        try:
            dialog = CommandExecutionDialog()

            if dialog.exec() == QDialog.DialogCode.Accepted:
                command = dialog.get_result()
                if command:
                    self.execute_command(command)

        except Exception as e:
            logger.error(f"Error in get_command_execution: {str(e)}")

    def execute_command(self, command_text):
        try:

            executor = CommandExecutor(make_api_request=self.make_api_request,
                                       settings=self.settings,
                                       logger=logger)

            executor.execute_command(command_text)
        except Exception as e:
            logger.error(f"Error in execute_command: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"An unexpected error occurred: {str(e)}")

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
            keyboard.add_hotkey(self.settings.get_setting('command_execution.hotkey'),
                                self.handle_command_execution_hotkey)
            logger.info("Hotkeys successfully set up")
        except Exception as e:
            logger.error(f"Error setting up hotkeys: {str(e)}")

    def cleanup(self):
        try:
            if self.worker_thread:
                self.worker_thread.quit()
                self.worker_thread.wait()
            if hasattr(self, 'voice_control'):
                self.voice_control.stop()
        except Exception as e:
            logger.error(f"Error in cleanup: {str(e)}")

    def run(self):
        try:
            keyboard.wait()
        except Exception as e:
            logger.error(f"Error in run: {str(e)}")
