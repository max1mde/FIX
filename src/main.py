import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from settings_manager import SettingsManager
from autocorrect_service import AutocorrectService
from ui.settings_window import SettingsWindow


class AutocorrectApp:
    def __init__(self):
        self.tray = None
        self.app = QApplication(sys.argv)
        self.settings = SettingsManager()
        self.service = AutocorrectService(self.settings)
        self.settings_window = SettingsWindow(self.settings)
        self.service.setup_hotkeys()
        self.setup_tray()

    def setup_tray(self):
        from PyQt6.QtWidgets import QSystemTrayIcon, QMenu
        self.tray = QSystemTrayIcon(QIcon("assets/icon.ico"))
        self.tray.setToolTip("Autocorrect App")
        menu = QMenu()
        menu.addAction("Settings", self.settings_window.show)
        menu.addAction("Exit", self.quit_app)
        self.tray.setContextMenu(menu)
        self.tray.show()

    def quit_app(self):
        self.service.cleanup()
        self.app.quit()

    def run(self):
        self.settings_window.show()
        return self.app.exec()


if __name__ == "__main__":
    app = AutocorrectApp()
    sys.exit(app.run())

