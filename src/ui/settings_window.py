import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QIcon
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QLineEdit, QLabel, QPushButton, QDialog,
                             QGroupBox, QKeySequenceEdit, QTableWidget, QTableWidgetItem, QComboBox)


window_height = 710
window_width = 360

class ConfirmationDialog(QDialog):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Confirm")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setFixedSize(300, 150)

        layout = QVBoxLayout(self)
        label = QLabel(message)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)

        buttons_layout = QHBoxLayout()
        yes_btn = QPushButton("Yes")
        yes_btn.clicked.connect(self.accept)
        no_btn = QPushButton("No")
        no_btn.clicked.connect(self.reject)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        buttons_layout.addWidget(yes_btn)
        buttons_layout.addWidget(no_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)


class FixModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Fix Module Settings")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.capitalization = QCheckBox("Capitalization")
        self.punctuate = QCheckBox("Punctuation")
        self.german_noun_capitalization = QCheckBox("German Noun Capitalization")
        self.name_capitalization = QCheckBox("Name Capitalization")
        self.use_replacements = QCheckBox("Use Replacements")

        self.hotkey_input = QKeySequenceEdit()
        hotkey_label = QLabel("Fix Hotkey:")

        for widget in [self.capitalization, self.punctuate, self.german_noun_capitalization, self.name_capitalization,
                       self.use_replacements]:
            widget.stateChanged.connect(self.mark_modified)
            layout.addWidget(widget)

        layout.addWidget(hotkey_label)
        layout.addWidget(self.hotkey_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.capitalization.setChecked(self.settings.get_setting('fix.capitalization', True))
        self.punctuate.setChecked(self.settings.get_setting('fix.punctuate', True))
        self.german_noun_capitalization.setChecked(self.settings.get_setting('fix.german_noun_capitalization', True))
        self.name_capitalization.setChecked(self.settings.get_setting('fix.name_capitalization', True))
        self.use_replacements.setChecked(self.settings.get_setting('fix.use_replacements', True))
        self.hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('fix.hotkey', 'Ctrl+F8')))

    def save_settings(self):
        self.settings.set_setting('fix.capitalization', self.capitalization.isChecked())
        self.settings.set_setting('fix.punctuate', self.punctuate.isChecked())
        self.settings.set_setting('fix.german_noun_capitalization', self.german_noun_capitalization.isChecked())
        self.settings.set_setting('fix.name_capitalization', self.name_capitalization.isChecked())
        self.settings.set_setting('fix.use_replacements', self.use_replacements.isChecked())
        self.settings.set_setting('fix.hotkey', self.hotkey_input.keySequence().toString())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True


class RephaseModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Rephrase Module Settings (AI)")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.use_replacements = QCheckBox("Use Replacements")
        self.use_replacements.stateChanged.connect(self.mark_modified)

        self.prompt = QLineEdit()
        self.prompt.textChanged.connect(self.mark_modified)
        prompt_label = QLabel("Rephrase Prompt:")

        self.hotkey_input = QKeySequenceEdit()
        hotkey_label = QLabel("Rephrase Hotkey:")

        self.switch_hotkey_input = QKeySequenceEdit()
        switch_label = QLabel("Switch Phrasings Hotkey:")

        layout.addWidget(self.use_replacements)
        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt)
        layout.addWidget(hotkey_label)
        layout.addWidget(self.hotkey_input)
        layout.addWidget(switch_label)
        layout.addWidget(self.switch_hotkey_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.use_replacements.setChecked(self.settings.get_setting('rephrase.use_replacements', True))
        self.prompt.setText(self.settings.get_setting('rephrase.prompt', ''))
        self.hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('rephrase.hotkey', 'Ctrl+F9')))
        self.switch_hotkey_input.setKeySequence(
            QKeySequence(self.settings.get_setting('rephrase.switch_phrasings_hotkey', 'Ctrl+F10')))

    def save_settings(self):
        self.settings.set_setting('rephrase.use_replacements', self.use_replacements.isChecked())
        self.settings.set_setting('rephrase.prompt', self.prompt.text())
        self.settings.set_setting('rephrase.hotkey', self.hotkey_input.keySequence().toString())
        self.settings.set_setting('rephrase.switch_phrasings_hotkey', self.switch_hotkey_input.keySequence().toString())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True


class TranslateModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Translate Module Settings (AI)")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.use_replacements = QCheckBox("Use Replacements")
        self.use_replacements.stateChanged.connect(self.mark_modified)

        self.prompt = QLineEdit()
        self.prompt.textChanged.connect(self.mark_modified)
        prompt_label = QLabel("Translation Prompt:")

        self.alternative_language = QLineEdit()
        self.alternative_language.textChanged.connect(self.mark_modified)
        lang_label = QLabel("Alternative Language:")

        self.hotkey_input = QKeySequenceEdit()
        hotkey_label = QLabel("Translation Hotkey:")

        layout.addWidget(self.use_replacements)
        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt)
        layout.addWidget(lang_label)
        layout.addWidget(self.alternative_language)
        layout.addWidget(hotkey_label)
        layout.addWidget(self.hotkey_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.use_replacements.setChecked(self.settings.get_setting('translate.use_replacements', True))
        self.prompt.setText(self.settings.get_setting('translate.prompt', ''))
        self.alternative_language.setText(self.settings.get_setting('translate.alternative_language', 'german'))
        self.hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('translate.hotkey', 'Ctrl+F11')))

    def save_settings(self):
        self.settings.set_setting('translate.use_replacements', self.use_replacements.isChecked())
        self.settings.set_setting('translate.prompt', self.prompt.text())
        self.settings.set_setting('translate.alternative_language', self.alternative_language.text())
        self.settings.set_setting('translate.hotkey', self.hotkey_input.keySequence().toString())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True


class VoiceControlModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Voice Control Module Settings")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.voice_control_enabled = QCheckBox("Enable Voice Control")
        self.voice_control_enabled.stateChanged.connect(self.mark_modified)
        layout.addWidget(self.voice_control_enabled)

        pause_seconds_layout = QHBoxLayout()
        pause_seconds_label = QLabel("Pause seconds:")
        self.pause_seconds_input = QLineEdit()
        self.pause_seconds_input.textChanged.connect(self.mark_modified)
        pause_seconds_layout.addWidget(pause_seconds_label)
        pause_seconds_layout.addWidget(self.pause_seconds_input)
        layout.addLayout(pause_seconds_layout)

        trigger_name_layout = QHBoxLayout()
        trigger_name_label = QLabel("Voice Trigger Name:")
        self.trigger_name_input = QLineEdit()
        self.trigger_name_input.textChanged.connect(self.mark_modified)
        trigger_name_layout.addWidget(trigger_name_label)
        trigger_name_layout.addWidget(self.trigger_name_input)
        layout.addLayout(trigger_name_layout)

        language_layout = QHBoxLayout()
        language_label = QLabel("Speech Recognition Language:")
        self.language_combobox = QComboBox()
        self.language_combobox.addItems([
            'en-US', 'en-GB', 'de-DE', 'fr-FR', 'es-ES', 'it-IT',
            'zh-CN', 'ja-JP', 'ru-RU', 'ar-SA'
        ])
        self.language_combobox.currentTextChanged.connect(self.mark_modified)
        language_layout.addWidget(language_label)
        language_layout.addWidget(self.language_combobox)
        layout.addLayout(language_layout)

        microphone_layout = QHBoxLayout()
        microphone_label = QLabel("Microphone Device:")
        self.microphone_combobox = QComboBox()


        import speech_recognition as sr
        for i, mic in enumerate(sr.Microphone.list_microphone_names()):
            self.microphone_combobox.addItem(mic, i)

        self.microphone_combobox.currentIndexChanged.connect(self.mark_modified)
        microphone_layout.addWidget(microphone_label)
        microphone_layout.addWidget(self.microphone_combobox)
        layout.addLayout(microphone_layout)

        module_group = QGroupBox("Enable Voice Control for Modules")
        module_layout = QVBoxLayout()

        self.question_module = QCheckBox("Question Module")
        self.fix_module = QCheckBox("Fix Module")
        self.rephrase_module = QCheckBox("Rephrase Module")
        self.translate_module = QCheckBox("Translate Module")
        self.command_execution_module = QCheckBox("Command Execution Module")

        for widget in [self.question_module, self.fix_module, self.rephrase_module,
                       self.translate_module, self.command_execution_module]:
            widget.stateChanged.connect(self.mark_modified)
            module_layout.addWidget(widget)

        module_group.setLayout(module_layout)
        layout.addWidget(module_group)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.voice_control_enabled.setChecked(
            self.settings.get_setting('voice_control.enabled', False)
        )
        self.trigger_name_input.setText(
            self.settings.get_setting('voice_control.trigger_name', 'Jerome')
        )
        self.pause_seconds_input.setText(
            self.settings.get_setting('voice_control.pause_seconds', 3)
        )
        self.fix_module.setChecked(
            self.settings.get_setting('voice_control.fix_module', True)
        )
        self.rephrase_module.setChecked(
            self.settings.get_setting('voice_control.rephrase_module', True)
        )
        self.translate_module.setChecked(
            self.settings.get_setting('voice_control.translate_module', True)
        )
        self.command_execution_module.setChecked(
            self.settings.get_setting('voice_control.command_execution_module', True)
        )

        self.question_module.setChecked(
            self.settings.get_setting('voice_control.question_module', True)
        )

        language = self.settings.get_setting('voice_control.language', 'en-US')
        self.language_combobox.setCurrentText(language)

        microphone = self.settings.get_setting('voice_control.microphone', None)
        if microphone is not None:
            self.microphone_combobox.setCurrentIndex(microphone)

    def save_settings(self):
        self.settings.set_setting('voice_control.enabled',
                                  self.voice_control_enabled.isChecked())
        self.settings.set_setting('voice_control.trigger_name',
                                  self.trigger_name_input.text())
        self.settings.set_setting('voice_control.pause_seconds',
                                  self.pause_seconds_input.text())
        self.settings.set_setting(
            'voice_control.language',
            self.language_combobox.currentText()
        )
        self.settings.set_setting('voice_control.microphone',
            self.microphone_combobox.currentData())
        self.settings.set_setting('voice_control.fix_module',
                                  self.fix_module.isChecked())
        self.settings.set_setting('voice_control.rephrase_module',
                                  self.rephrase_module.isChecked())
        self.settings.set_setting('voice_control.translate_module',
                                  self.translate_module.isChecked())
        self.settings.set_setting('voice_control.command_execution_module',
                                  self.command_execution_module.isChecked())
        self.settings.set_setting('voice_control.question_module',
                                  self.question_module.isChecked())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True

class CommandExecutionModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Command Execution Module Settings (AI)")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.prompt = QLineEdit()
        self.prompt.textChanged.connect(self.mark_modified)
        prompt_label = QLabel("Command Execution Prompt:")

        self.hotkey_input = QKeySequenceEdit()
        hotkey_label = QLabel("Command Execution Hotkey:")

        layout.addWidget(prompt_label)
        layout.addWidget(self.prompt)
        layout.addWidget(hotkey_label)
        layout.addWidget(self.hotkey_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.prompt.setText(self.settings.get_setting('command_execution.prompt',
                                                      'Convert the following user prompt into a PowerShell command or script. If it is impossible or dangerous, '
                                                      'reply with "This action is impossible". Respond with only the command or script (It will be executed directly):'
                                                      ))
        self.hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('command_execution.hotkey', 'Ctrl+F7')))

    def save_settings(self):
        self.settings.set_setting('command_execution.prompt', self.prompt.text())
        self.settings.set_setting('command_execution.hotkey', self.hotkey_input.keySequence().toString())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True

class CustomPromptModuleWindow(QDialog):
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings = settings_manager
        self.setWindowTitle("Custom Prompt Module Settings (AI)")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setup_ui()
        self.load_settings()
        self.settings_modified = False

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.use_replacements = QCheckBox("Use Replacements")
        self.auto_custom_prompt = QCheckBox("Auto Prompt When Typing")

        for widget in [self.use_replacements, self.auto_custom_prompt]:
            widget.stateChanged.connect(self.mark_modified)
            layout.addWidget(widget)

        self.hotkey_input = QKeySequenceEdit()
        hotkey_label = QLabel("Custom Prompt Hotkey:")
        layout.addWidget(hotkey_label)
        layout.addWidget(self.hotkey_input)

        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

    def load_settings(self):
        self.use_replacements.setChecked(self.settings.get_setting('custom_prompt.use_replacements', True))
        self.auto_custom_prompt.setChecked(self.settings.get_setting('custom_prompt.auto_custom_prompt', True))
        self.hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('custom_prompt.hotkey', 'Ctrl+F12')))

    def save_settings(self):
        self.settings.set_setting('custom_prompt.use_replacements', self.use_replacements.isChecked())
        self.settings.set_setting('custom_prompt.auto_custom_prompt', self.auto_custom_prompt.isChecked())
        self.settings.set_setting('custom_prompt.hotkey', self.hotkey_input.keySequence().toString())
        self.settings_modified = False
        self.close()

    def mark_modified(self):
        self.settings_modified = True


class ReplacementsDialog(QDialog):
    def __init__(self, replacements, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Manage Replacements")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.setFixedSize(600, 500)

        self.replacements = replacements
        self.setup_ui()
        self.populate_table(replacements)

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.replacements_table = QTableWidget()
        self.replacements_table.setColumnCount(2)
        self.replacements_table.setColumnWidth(0, 210)
        self.replacements_table.setColumnWidth(1, 320)
        self.replacements_table.setHorizontalHeaderLabels(["Text", "Replacement"])
        self.replacements_table.itemSelectionChanged.connect(self.on_selection_changed)
        layout.addWidget(self.replacements_table)

        self.text_input = QLineEdit()
        self.replacement_input = QLineEdit()
        layout.addWidget(QLabel("Text:"))
        layout.addWidget(self.text_input)
        layout.addWidget(QLabel("Replacement:"))
        layout.addWidget(self.replacement_input)

        buttons_layout = QHBoxLayout()
        add_btn = QPushButton("Add Replacement")
        add_btn.clicked.connect(self.add_replacement)
        edit_btn = QPushButton("Edit Replacement")
        edit_btn.clicked.connect(self.edit_replacement)
        delete_btn = QPushButton("Delete Replacement")
        delete_btn.clicked.connect(self.delete_replacement)

        buttons_layout.addWidget(add_btn)
        buttons_layout.addWidget(edit_btn)
        buttons_layout.addWidget(delete_btn)
        layout.addLayout(buttons_layout)

        ok_btn = QPushButton("Close")
        ok_btn.clicked.connect(self.accept)
        layout.addWidget(ok_btn)

    def populate_table(self, replacements):
        self.replacements_table.setRowCount(len(replacements))
        for row, (key, value) in enumerate(replacements.items()):
            self.replacements_table.setItem(row, 0, QTableWidgetItem(key))
            self.replacements_table.setItem(row, 1, QTableWidgetItem(value))

    def on_selection_changed(self):
        selected_row = self.replacements_table.currentRow()
        if selected_row >= 0:
            text_item = self.replacements_table.item(selected_row, 0)
            replacement_item = self.replacements_table.item(selected_row, 1)
            self.text_input.setText(text_item.text())
            self.replacement_input.setText(replacement_item.text())

    def add_replacement(self):
        text = self.text_input.text().strip()
        replacement = self.replacement_input.text().strip()
        if text and replacement:
            self.replacements[text] = replacement
            self.populate_table(self.replacements)
            self.clear_inputs()

    def edit_replacement(self):
        selected_row = self.replacements_table.currentRow()
        if selected_row >= 0:
            text = self.text_input.text().strip()
            replacement = self.replacement_input.text().strip()
            if text and replacement:
                original_key = self.replacements_table.item(selected_row, 0).text()
                del self.replacements[original_key]
                self.replacements[text] = replacement
                self.populate_table(self.replacements)
                self.clear_inputs()

    def delete_replacement(self):
        selected_row = self.replacements_table.currentRow()
        if selected_row >= 0:
            original_key = self.replacements_table.item(selected_row, 0).text()
            del self.replacements[original_key]
            self.populate_table(self.replacements)
            self.clear_inputs()

    def clear_inputs(self):
        self.text_input.clear()
        self.replacement_input.clear()


class SettingsWindow(QMainWindow):
    def __init__(self, settings_manager):
        super().__init__()
        self.settings = settings_manager
        self.setup_ui()
        self.setWindowTitle("FIX - Autocorrect")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.settings_modified = False

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        general_group = QGroupBox("General")
        general_layout = QVBoxLayout()

        self.usage_group = QGroupBox("API Usage Statistics")
        usage_layout = QVBoxLayout()

        self.input_tokens_label = QLabel()
        self.completion_tokens_label = QLabel()
        self.total_tokens_label = QLabel()
        self.cost_label = QLabel()

        usage_layout.addWidget(self.input_tokens_label)
        usage_layout.addWidget(self.completion_tokens_label)
        usage_layout.addWidget(self.total_tokens_label)
        usage_layout.addWidget(self.cost_label)

        reset_stats_btn = QPushButton("Reset Statistics")
        reset_stats_btn.clicked.connect(self.reset_usage_stats)
        usage_layout.addWidget(reset_stats_btn)

        api_layout = QHBoxLayout()
        self.token = QLineEdit()
        self.token.setPlaceholderText("Enter API key")
        self.token.setEchoMode(QLineEdit.EchoMode.Password)
        self.token.textChanged.connect(self.mark_modified)

        self.show_token_btn = QPushButton("Show")
        self.show_token_btn.setFixedWidth(60)
        self.show_token_btn.clicked.connect(self.toggle_token_visibility)

        self.usage_group.setLayout(usage_layout)
        general_layout.addWidget(self.usage_group)

        api_layout.addWidget(QLabel("API Key:"))
        api_layout.addWidget(self.token)
        api_layout.addWidget(self.show_token_btn)
        general_layout.addLayout(api_layout)

        endpoint_layout = QHBoxLayout()
        self.endpoint = QLineEdit()
        self.endpoint.setPlaceholderText("Enter endpoint url")
        self.endpoint.setText(self.settings.get_setting('api_endpoint'))
        endpoint_layout.addWidget(QLabel("Endpoint:"))
        endpoint_layout.addWidget(self.endpoint)
        general_layout.addLayout(endpoint_layout)

        model_layout = QHBoxLayout()
        self.model = QLineEdit()
        self.model.setPlaceholderText("Enter model name")
        self.model.setText(self.settings.get_setting('api_model'))
        model_layout.addWidget(QLabel("Model:"))
        model_layout.addWidget(self.model)
        general_layout.addLayout(model_layout)

        self.auto_select_text = QCheckBox("Auto Select Text")
        self.auto_select_text.stateChanged.connect(self.mark_modified)
        general_layout.addWidget(self.auto_select_text)

        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        modules_group = QGroupBox("Modules")
        modules_layout = QVBoxLayout()

        fix_btn = QPushButton("Fix Module Settings")
        fix_btn.clicked.connect(self.show_fix_settings)
        modules_layout.addWidget(fix_btn)

        rephrase_btn = QPushButton("Rephrase Module Settings (AI)")
        rephrase_btn.clicked.connect(self.show_rephrase_settings)
        modules_layout.addWidget(rephrase_btn)

        translate_btn = QPushButton("Translate Module Settings (AI)")
        translate_btn.clicked.connect(self.show_translate_settings)
        modules_layout.addWidget(translate_btn)

        custom_prompt_btn = QPushButton("Custom Prompt Module Settings (AI)")
        custom_prompt_btn.clicked.connect(self.show_custom_prompt_settings)
        modules_layout.addWidget(custom_prompt_btn)

        command_execution_btn = QPushButton("Command Execution Module Settings (AI)")
        command_execution_btn.clicked.connect(self.show_command_execution_settings)
        modules_layout.addWidget(command_execution_btn)

        voice_control_btn = QPushButton("Voice Control Module Settings")
        voice_control_btn.clicked.connect(self.show_voice_control_settings)
        modules_layout.addWidget(voice_control_btn)

        modules_group.setLayout(modules_layout)
        layout.addWidget(modules_group)

        replacements_btn = QPushButton("Manage Replacements")
        replacements_btn.clicked.connect(self.show_replacements)
        layout.addWidget(replacements_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

        open_dir_button = QPushButton("Open Settings Directory")
        open_dir_button.clicked.connect(self.open_settings_directory)
        layout.addWidget(open_dir_button)

        reset_btn = QPushButton("Reset Settings")
        reset_btn.setStyleSheet("background-color: red; color: white; font-weight: bold;")
        reset_btn.clicked.connect(self.reset_settings)
        layout.addWidget(reset_btn)

        terminate_btn = QPushButton("Terminate")
        terminate_btn.setStyleSheet("background-color: orange; color: white; font-weight: bold;")
        terminate_btn.clicked.connect(self.terminate_application)
        layout.addWidget(terminate_btn)

        bottom_layout = QHBoxLayout()
        copyright_label = QLabel("© MaximDe")
        copyright_label.setStyleSheet("color: gray;")
        github_link = QLabel("<a href='https://github.com/max1mde/FIX'>GitHub</a>")
        github_link.setStyleSheet("color: blue;")
        github_link.setOpenExternalLinks(True)

        bottom_layout.addWidget(copyright_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(github_link)
        layout.addLayout(bottom_layout)

        self.setFixedSize(window_width, window_height)
        self.load_settings()

        self.update_usage_display()

    def reset_usage_stats(self):
        dialog = ConfirmationDialog(
            'Are you sure you want to reset usage statistics?', self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.settings['usage_stats'] = {
                'input_tokens': 0,
                'completion_tokens': 0,
                'total_cost': 0.0
            }
            self.settings.save_settings()
            self.update_usage_display()

    def update_usage_display(self):
        usage_stats = self.settings.get_setting('usage_stats', {
            'input_tokens': 0,
            'completion_tokens': 0,
            'total_cost': 0.0
        })

        input_tokens = usage_stats['input_tokens']
        completion_tokens = usage_stats['completion_tokens']
        total_tokens = input_tokens + completion_tokens

        self.input_tokens_label.setText(
            f"Input Tokens: {input_tokens:,} (${(input_tokens / 1_000_000) * 0.15:.4f})"
        )
        self.completion_tokens_label.setText(
            f"Completion Tokens: {completion_tokens:,} (${(completion_tokens / 1_000_000) * 0.60:.4f})"
        )
        self.total_tokens_label.setText(
            f"Total Tokens: {total_tokens:,}"
        )
        self.cost_label.setText(
            f"Total Cost: ${usage_stats['total_cost']:.4f}"
        )

    def showEvent(self, event):
        super().showEvent(event)
        self.update_usage_display()

    def toggle_token_visibility(self):
        if self.token.echoMode() == QLineEdit.EchoMode.Password:
            self.token.setEchoMode(QLineEdit.EchoMode.Normal)
            self.show_token_btn.setText("Hide")
        else:
            self.token.setEchoMode(QLineEdit.EchoMode.Password)
            self.show_token_btn.setText("Show")

    def show_fix_settings(self):
        dialog = FixModuleWindow(self.settings, self)
        dialog.exec()

    def show_rephrase_settings(self):
        dialog = RephaseModuleWindow(self.settings, self)
        dialog.exec()

    def show_translate_settings(self):
        dialog = TranslateModuleWindow(self.settings, self)
        dialog.exec()

    def show_custom_prompt_settings(self):
        dialog = CustomPromptModuleWindow(self.settings, self)
        dialog.exec()

    def show_command_execution_settings(self):
        dialog = CommandExecutionModuleWindow(self.settings, self)
        dialog.exec()

    def show_voice_control_settings(self):
        dialog = VoiceControlModuleWindow(self.settings, self)
        dialog.exec()

    def show_replacements(self):
        replacements = self.settings.get_replacements()
        dialog = ReplacementsDialog(replacements, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.set_setting('replacements', dialog.replacements)
            self.settings_modified = True

    def load_settings(self):
        self.token.setText(self.settings.get_setting('provider_api_key', ''))
        self.endpoint.setText(self.settings.get_setting('api_endpoint', ''))
        self.model.setText(self.settings.get_setting('api_model', ''))
        self.auto_select_text.setChecked(self.settings.get_setting('auto_select_text', True))
        self.settings_modified = False
        self.update_usage_group_visibility()

    def save_settings(self):
        self.settings.set_setting('provider_api_key', self.token.text())
        self.settings.set_setting('api_endpoint', self.endpoint.text())
        self.settings.set_setting('api_model', self.model.text())
        self.settings.set_setting('auto_select_text', self.auto_select_text.isChecked())
        self.settings_modified = False
        self.update_usage_group_visibility()

    def open_settings_directory(self):
        import os
        import platform
        import subprocess

        directory = self.settings.get_settings_directory()

        if platform.system() == "Windows":
            os.startfile(directory)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", directory])
        else:  # Linux
            subprocess.Popen(["xdg-open", directory])

    def reset_settings(self):
        dialog = ConfirmationDialog(
            'Are you sure you want to reset all settings?<br>'
            'This action cannot be undone.', self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.reset_settings()
            self.load_settings()

    def update_usage_group_visibility(self):
        default_endpoint = self.settings.get_default_setting('api_endpoint')
        default_model = self.settings.get_default_setting('api_model')

        if self.endpoint.text() != default_endpoint or self.model.text() != default_model:
            self.usage_group.hide()
            self.usage_group.setEnabled(False)
            self.setFixedSize(window_width, window_height - 135)
        else:
            self.usage_group.show()
            self.usage_group.setEnabled(True)
            self.setFixedSize(window_width, window_height)

    def terminate_application(self):
        if self.settings_modified:
            dialog = ConfirmationDialog(
                'You have unsaved changes.<br>Do you want to save before terminating?', self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.save_settings()
                self.close()
                sys.exit()

        self.settings_modified = False
        self.close()
        sys.exit()

    def closeEvent(self, event):
        if self.settings_modified:
            dialog = ConfirmationDialog(
                'You have unsaved changes.<br>Do you want to save before closing?', self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.save_settings()
                event.ignore()
                self.hide()
            else:
                event.ignore()
                self.hide()
        else:
            event.ignore()
            self.hide()

    def mark_modified(self):
        self.settings_modified = True
