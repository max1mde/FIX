import sys
from pathlib import Path
from typing import Optional
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QMessageBox
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QCoreApplication

from settings_manager import SettingsManager
from autocorrect_service import AutocorrectService
from ui.settings_window import SettingsWindow


class AutocorrectApp:

    APP_NAME = "Autocorrect App"
    ICON_PATH = Path("assets/icon.ico")

    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.app.setApplicationName(self.APP_NAME)
        self.app.setQuitOnLastWindowClosed(False)

        self.tray: Optional[QSystemTrayIcon] = None
        self._initialize_components()

    def _initialize_components(self) -> None:
        try:
            self.settings = SettingsManager()
            self.service = AutocorrectService(self.settings)
            self.settings_window = SettingsWindow(self.settings)
            self._setup_tray()
        except Exception as e:
            self._show_error_and_exit(f"Failed to initialize application: {str(e)}")

    def _setup_tray(self) -> None:
        if not self.ICON_PATH.exists():
            self._show_error_and_exit("Icon file not found!")
            return

        try:
            self.tray = QSystemTrayIcon(QIcon(str(self.ICON_PATH)))
            self.tray.setToolTip(self.APP_NAME)

            menu = QMenu()
            settings_action = menu.addAction("Settings")
            settings_action.triggered.connect(self.settings_window.show)

            exit_action = menu.addAction("Exit")
            exit_action.triggered.connect(self.quit_app)

            self.tray.setContextMenu(menu)
            self.tray.show()

            self.tray.activated.connect(self._handle_tray_activation)

        except Exception as e:
            self._show_error_and_exit(f"Failed to setup system tray: {str(e)}")

    def _handle_tray_activation(self, reason: QSystemTrayIcon.ActivationReason) -> None:
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.settings_window.show()

    def _show_error_and_exit(self, message: str) -> None:
        QMessageBox.critical(None, "Error", message)
        print(message)
        self.quit_app()

    def quit_app(self) -> None:
        try:
            if self.service:
                self.service.cleanup()

            if self.tray:
                self.tray.hide()

            QCoreApplication.quit()
        except Exception as e:
            print(f"Error during shutdown: {e}", file=sys.stderr)
            sys.exit(1)

    def run(self) -> int:
        try:
            self.settings_window.show()

            if not QSystemTrayIcon.isSystemTrayAvailable():
                self._show_error_and_exit("System tray is not available on this system!")
                return 1

            return self.app.exec()

        except Exception as e:
            self._show_error_and_exit(f"Application error: {str(e)}")
            return 1


def main() -> int:
    try:
        app = AutocorrectApp()
        return app.run()
    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())