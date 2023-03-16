
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QMessageBox
import os
from typing import Optional

WINDOW_ICON = os.getcwd() + "/static/lock.png"
WINDOW_TITLE = "Account Manager"


def get_gui_font() -> QFont:
    """Returns a QFont object for GUI purposes.

    Returns:
        QFont: A QFont object with a family of "Segoe UI" and point size of 10.
    """
    font = QFont()
    font.setFamily('Segoe UI')
    font.setPointSize(10)
    return font


def get_gui_icon() -> Optional[QIcon]:
    """Returns a QIcon object for the main window icon.

    Returns:
        QIcon: A QIcon object with the image specified in the WINDOW_ICON path.
            Returns None if the image file cannot be found or loaded.
    """
    try:
        icon = QIcon(WINDOW_ICON)
        return icon
    except (FileNotFoundError, OSError) as e:
        print(f"Error loading window icon: {e}")
        return None


def show_confirmation_message_box(text: str) -> Optional[bool]:
    """Displays a confirmation message box with the specified text.

    Args:
        text (str): The text to display in the message box.

    Returns:
        bool: True if the user clicked "Ok", False if the user clicked "Cancel",
            or None if there was an error displaying the message box.
    """
    try:
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(WINDOW_TITLE)
        msg_box.setWindowIcon(get_gui_icon())
        msg_box.setText(text)
        msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        response = msg_box.exec()
        return response == QMessageBox.Ok
    except Exception as e:
        print(f"Error displaying message box: {e}")
        return None
