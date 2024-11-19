import re
import subprocess
import time
import pyperclip
from pynput.keyboard import Key, Controller
from PyQt6.QtWidgets import QMessageBox

controller = Controller()


class CommandExecutor:
    def __init__(self, make_api_request, settings, logger):
        self.make_api_request = make_api_request
        self.settings = settings
        self.logger = logger
        self.max_tasks = 30 # TODO implement

    def execute_command(self, command_text):
        try:
            print("\nA task was requested: " + command_text)
            steps = self.generate_steps(command_text)
            if not steps:
                return

            for step in steps:
                if not self.execute_step(step):
                    break

        except Exception as e:
            self.logger.error(f"Error in execute_command: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"Failed to execute command: {str(e)}")

    def generate_steps(self, task_description):

        steps = []
        prompt = self.settings.get_setting("command_execution.prompt") + task_description

        try:
            response_data = self.make_api_request(prompt)
            response_content = response_data['choices'][0]['message']['content'].strip()
            response_content = re.sub(r'\(.*?\)', '', response_content)
            steps = response_content.split('\n')
            steps = [re.sub(r'^\d+\.\s*', '', step).strip() for step in steps]
        except Exception as e:
            self.logger.error(f"Error generating steps: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"Failed to generate steps: {str(e)}")
        return steps

    def execute_step(self, step):
        print("Executing step: " + step)
        try:
            if step.startswith("PowerShell:"):
                command = step.replace("PowerShell:", "").strip()
                self.run_powershell(command)
            elif step.startswith("Hotkey:"):
                hotkey_command = step.replace("Hotkey:", "").strip()
                self.run_hotkey(hotkey_command)
            elif step.startswith("Wait:"):
                wait_time = float(step.replace("Wait:", "").strip())
                self.wait(wait_time)
            elif step.startswith("Clipboard:"):
                clipboard_command = step.replace("Clipboard:", "").strip()
                self.run_clipboard(clipboard_command)
            else:
                self.logger.error(f"Unknown step type: {step}")
                return False
            return True
        except Exception as e:
            self.logger.error(f"Error executing step: {step}, Error: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"Failed to execute step: {step}")
            return False

    def run_powershell(self, command):
        dangerous_patterns = [
            (r'(rm|remove-item|del)\s+-r(?:ecurse)?\s+.*(system32|windows\\system)',
             'Critical system directory deletion'),
            (r'format\s+[a-zA-Z]:', 'Drive formatting'),
            (r'reg\s+delete\s+HKLM\\SOFTWARE\\Microsoft', 'Critical registry deletion'),
            (r'rmdir\s+/s\s+.*windows', 'Windows directory deletion')
        ]

        for pattern, description in dangerous_patterns:
            if re.search(pattern, command.lower()):
                QMessageBox.warning(None, "Command Execution",
                                    f"Blocked dangerous operation: {description}")
                return

        si = subprocess.STARTUPINFO()
        si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        si.wShowWindow = 0

        subprocess.Popen(['powershell.exe', '-Command', command],
                         startupinfo=si, creationflags=subprocess.CREATE_NEW_CONSOLE)

    def run_hotkey(self, hotkey_command):
        try:
            keys = hotkey_command.split('+')


            special_keys = {
                'RIGHT': Key.right,
                'LEFT': Key.left,
                'UP': Key.up,
                'DOWN': Key.down,
                'ENTER': Key.enter,
                'WIN': Key.cmd_l,
                'ESC': Key.esc,
                'TAB': Key.tab,
                'BACKSPACE': Key.backspace,
                'SHIFT': Key.shift,
                'CTRL': Key.ctrl,
                'ALT': Key.alt,
                'CAPSLOCK': Key.caps_lock,
                'SPACE': Key.space,
                'F1': Key.f1,
                'F2': Key.f2,
                'F3': Key.f3,
                'F4': Key.f4,
                'F5': Key.f5,
                'F6': Key.f6,
                'F7': Key.f7,
                'F8': Key.f8,
                'F9': Key.f9,
                'F10': Key.f10,
                'F11': Key.f11,
                'F12': Key.f12,
                'PAGEUP': Key.page_up,
                'PAGEDOWN': Key.page_down,
                'HOME': Key.home,
                'END': Key.end,
                'INSERT': Key.insert,
                'DELETE': Key.delete,
                'NUMLOCK': Key.num_lock,
            }


            keys = [key.strip().upper() for key in keys]

            modifiers = {
                'CTRL': Key.ctrl,
                'ALT': Key.alt,
                'SHIFT': Key.shift,
                'WIN': Key.cmd_l
            }
            pressed_keys = []


            for key in keys:
                if key in modifiers:
                    pressed_keys.append(modifiers[key])

            with controller.pressed(*pressed_keys):
                for key in keys:
                    if key not in modifiers:
                        if key in special_keys:
                            controller.press(special_keys[key])
                            controller.release(special_keys[key])
                        else:
                            controller.press(key.lower())
                            controller.release(key.lower())

        except Exception as e:
            self.logger.error(f"Error executing hotkey: {hotkey_command}, Error: {str(e)}")
            QMessageBox.critical(None, "Error", f"Failed to execute hotkey: {hotkey_command}")

    def wait(self, seconds):
        try:
            time.sleep(seconds)
        except Exception as e:
            self.logger.error(f"Error during wait: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"Failed to wait: {str(e)}")

    def run_clipboard(self, clipboard_command):
        try:
            if clipboard_command.startswith("Copy"):
                text_to_copy = clipboard_command.replace("Copy", "").strip().strip("'")
                pyperclip.copy(text_to_copy)
            elif clipboard_command == "Paste":
                time.sleep(0.1)
                with controller.pressed(Key.ctrl):
                    controller.press('v')
                    controller.release('v')
        except Exception as e:
            self.logger.error(f"Error executing clipboard command: {clipboard_command}, Error: {str(e)}")
            QMessageBox.critical(None, "Error",
                                 f"Failed to execute clipboard command: {clipboard_command}")
