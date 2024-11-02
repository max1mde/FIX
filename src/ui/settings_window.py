import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QKeySequence, QIcon
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QLineEdit, QLabel, QPushButton,
                             QDialog,
                             QGroupBox, QKeySequenceEdit, QTableWidget, QTableWidgetItem)


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
        self.setWindowTitle("Autocorrect Settings")
        self.setWindowIcon(QIcon("assets/icon.ico"))
        self.settings_modified = False

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        features_group = QGroupBox("Features")
        features_layout = QVBoxLayout()

        self.auto_cap = QCheckBox("Auto-capitalize")
        self.auto_cap.stateChanged.connect(self.mark_modified)
        self.auto_punct = QCheckBox("Auto-punctuate")
        self.auto_punct.stateChanged.connect(self.mark_modified)
        self.ai_rephrase = QCheckBox("AI Rephrase")
        self.ai_rephrase.stateChanged.connect(self.mark_modified)
        self.german_noun_capitalization = QCheckBox("German Noun Capitalization")
        self.german_noun_capitalization.stateChanged.connect(self.mark_modified)

        features_layout.addWidget(self.auto_cap)
        features_layout.addWidget(self.auto_punct)
        features_layout.addWidget(self.ai_rephrase)
        features_layout.addWidget(self.german_noun_capitalization)
        features_group.setLayout(features_layout)
        layout.addWidget(features_group)

        prompt_group = QGroupBox("AI Prompts")
        prompt_layout = QVBoxLayout()

        self.ai_rephrase_prompt = QLineEdit()
        self.ai_rephrase_prompt.setPlaceholderText("Enter AI rephrase prompt...")
        self.ai_rephrase_prompt.textChanged.connect(self.mark_modified)
        prompt_layout.addWidget(self.ai_rephrase_prompt)

        self.ai_translation_prompt = QLineEdit()
        self.ai_translation_prompt.setPlaceholderText("Enter AI translation prompt...")
        self.ai_translation_prompt.textChanged.connect(self.mark_modified)
        prompt_layout.addWidget(self.ai_translation_prompt)

        prompt_group.setLayout(prompt_layout)
        layout.addWidget(prompt_group)

        translation_group = QGroupBox("Translation Settings")
        translation_layout = QVBoxLayout()

        self.translation_hotkey_input = QKeySequenceEdit()
        translation_hotkey = self.settings.get_setting('translation_hotkey', 'Alt+4')
        self.translation_hotkey_input.setKeySequence(QKeySequence(translation_hotkey))
        self.translation_hotkey_input.editingFinished.connect(self.mark_modified)

        self.language_input = QLineEdit()
        self.language_input.setPlaceholderText("Enter language (e.g., 'german')")
        self.language_input.setText(self.settings.get_setting('alternative_language', 'german'))
        self.language_input.textChanged.connect(self.mark_modified)

        translation_layout.addWidget(QLabel("Translation Hotkey:"))
        translation_layout.addWidget(self.translation_hotkey_input)
        translation_layout.addWidget(QLabel("Alternative Language:"))
        translation_layout.addWidget(self.language_input)

        translation_group.setLayout(translation_layout)
        layout.addWidget(translation_group)

        hotkey_group = QGroupBox("Hotkeys")
        hotkey_layout = QVBoxLayout()

        self.rephrase_hotkey_input = QKeySequenceEdit()
        current_rephrase_hotkey = self.settings.get_setting('rephrase_hotkey', 'Alt+2')
        self.rephrase_hotkey_input.setKeySequence(QKeySequence(current_rephrase_hotkey))
        self.rephrase_hotkey_input.editingFinished.connect(self.mark_modified)

        self.switch_phrasings_hotkey_input = QKeySequenceEdit()
        current_switch_hotkey = self.settings.get_setting('switch_phrasings', 'Alt+3')
        self.switch_phrasings_hotkey_input.setKeySequence(QKeySequence(current_switch_hotkey))
        self.switch_phrasings_hotkey_input.editingFinished.connect(self.mark_modified)

        self.fix_hotkey_input = QKeySequenceEdit()
        current_fix_hotkey = self.settings.get_setting('fix_hotkey', 'Alt+1')
        self.fix_hotkey_input.setKeySequence(QKeySequence(current_fix_hotkey))
        self.fix_hotkey_input.editingFinished.connect(self.mark_modified)

        self.custom_prompt_hotkey_input = QKeySequenceEdit()
        current_prompt_hotkey = self.settings.get_setting('custom_prompt_hotkey', 'Alt+5')
        self.custom_prompt_hotkey_input.setKeySequence(QKeySequence(current_prompt_hotkey))
        self.custom_prompt_hotkey_input.editingFinished.connect(self.mark_modified)

        hotkey_layout.addWidget(QLabel("Rephrase Hotkey:"))
        hotkey_layout.addWidget(self.rephrase_hotkey_input)
        hotkey_layout.addWidget(QLabel("Switch Phrasings Hotkey:"))
        hotkey_layout.addWidget(self.switch_phrasings_hotkey_input)
        hotkey_layout.addWidget(QLabel("Fix Hotkey:"))
        hotkey_layout.addWidget(self.fix_hotkey_input)
        hotkey_layout.addWidget(QLabel("Custom Prompt Hotkey:"))
        hotkey_layout.addWidget(self.custom_prompt_hotkey_input)

        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)

        self.token = QLineEdit()
        self.token.setFixedWidth(100)
        self.token.setPlaceholderText("Enter open router key")
        self.token.textChanged.connect(self.mark_modified)

        layout.addWidget(self.token)

        replacements_btn = QPushButton("Manage Replacements")
        replacements_btn.clicked.connect(self.show_replacements)
        layout.addWidget(replacements_btn)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)
        layout.addWidget(save_btn)

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

        github_link = QLabel("<a href='https://github.com/max1mde/AutocorrectApp'>GitHub</a>")
        github_link.setStyleSheet("color: blue;")
        github_link.setOpenExternalLinks(True)  #

        bottom_layout.addWidget(copyright_label)
        bottom_layout.addStretch()
        bottom_layout.addWidget(github_link)

        layout.addLayout(bottom_layout)

        self.setFixedSize(650, 750)
        self.load_settings()

    def load_settings(self):
        self.auto_cap.setChecked(self.settings.get_setting('auto_capitalize', True))
        self.auto_punct.setChecked(self.settings.get_setting('auto_punctuate', True))
        self.ai_rephrase.setChecked(self.settings.get_setting('ai_rephrase', True))
        self.german_noun_capitalization.setChecked(self.settings.get_setting('german_noun_capitalization', True))
        self.ai_rephrase_prompt.setText(self.settings.get_setting(
            'ai_rephrase_prompt', 'Provide 3 different concise rephrasing of the text, separated by | characters.'
        ))
        self.ai_translation_prompt.setText(self.settings.get_setting(
            'ai_translation_prompt', 'You are a basic translater. Add punctuation and use correct spelling. '
                                     'Translate the following text to English if it is in any other language than '
                                     'English, else translate it to %alternative_language% and ONLY answer with the '
                                     'translated message:'
        ))
        self.token.setText(self.settings.get_setting(
            'open_router_key', 'none'
        ))

        self.rephrase_hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('rephrase_hotkey', 'Alt+2')))
        self.switch_phrasings_hotkey_input.setKeySequence(
            QKeySequence(self.settings.get_setting('switch_phrasings', 'Alt+3')))
        self.custom_prompt_hotkey_input.setKeySequence(
            QKeySequence(self.settings.get_setting('custom_prompt_hotkey', 'Alt+5')))
        self.fix_hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('fix_hotkey', 'Alt+1')))
        self.translation_hotkey_input.setKeySequence(QKeySequence(self.settings.get_setting('translation_hotkey', 'Alt+4')))
        self.language_input.setText(self.settings.get_setting('alternative_language', 'german'))

        self.settings_modified = False

    def show_replacements(self):
        replacements = self.settings.get_replacements()
        dialog = ReplacementsDialog(replacements, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.set_setting('replacements', dialog.replacements)
            self.settings_modified = True

    def reset_settings(self):
        dialog = ConfirmationDialog(
            'Are you sure you want to reset all settings?<br>'
            'This action cannot be undone.', self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.settings.reset_settings()
            self.load_settings()

    def save_settings(self):
        self.settings.set_setting('auto_capitalize', self.auto_cap.isChecked())
        self.settings.set_setting('auto_punctuate', self.auto_punct.isChecked())
        self.settings.set_setting('ai_rephrase', self.ai_rephrase.isChecked())
        self.settings.set_setting('german_noun_capitalization', self.german_noun_capitalization.isChecked())
        self.settings.set_setting('ai_rephrase_prompt', self.ai_rephrase_prompt.text())
        self.settings.set_setting('ai_translation_prompt', self.ai_translation_prompt.text())
        self.settings.set_setting('open_router_key', self.token.text())
        self.settings.set_setting('rephrase_hotkey', self.rephrase_hotkey_input.keySequence().toString())
        self.settings.set_setting('switch_phrasings', self.switch_phrasings_hotkey_input.keySequence().toString())
        self.settings.set_setting('custom_prompt_hotkey',
                                  self.custom_prompt_hotkey_input.keySequence().toString())
        self.settings.set_setting('fix_hotkey', self.fix_hotkey_input.keySequence().toString())
        self.settings.set_setting('translation_hotkey', self.translation_hotkey_input.keySequence().toString())
        self.settings.set_setting('alternative_language', self.language_input.text())
        self.settings_modified = False

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
