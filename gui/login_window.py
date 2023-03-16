from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QVBoxLayout)
from utils.cryptography import hash_str
from gui.helpers import WINDOW_TITLE, get_gui_font, get_gui_icon
from gui.main_window import MainWindow


class LoginWindow(QMainWindow):
    """
    The main window of the application, where the user logs in with their master password.
    """

    def __init__(self, account_database):
        """
        Initializes the main window.
        """
        super().__init__()
        self.account_database = account_database
        self.set_window_properties()

        # Create a central widget and a vertical layout for it
        self.central_layout = QVBoxLayout()

        self.central_widget = QWidget(self)
        self.central_widget.setLayout(self.central_layout)
        self.setCentralWidget(self.central_widget)

        self.central_layout.addWidget(self.create_centered_label())
        self.central_layout.addLayout(self.create_input_layout())
        self.central_layout.addStretch()
        self.show()

    def set_window_properties(self) -> None:
        """Sets the properties for the window, including the title, icon,
        and geometry.
        """
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(get_gui_icon())
        self.setGeometry(800, 400, 300, 150)

    def create_centered_label(self) -> QLabel:
        """Creates and returns a QLabel object that displays a centered
        message.
        """
        label = QLabel('Enter master password', self.central_widget)
        label.setFont(get_gui_font())
        label.setAlignment(Qt.AlignCenter)
        return label

    def create_input_layout(self) -> QVBoxLayout:
        """Creates and returns a QVBoxLayout object that contains a
        QLineEdit and a QPushButton for user input.
        """
        input_layout = QVBoxLayout()

        # Create the password field and add it to the input layout
        self.password_field = QLineEdit(self.central_widget)
        self.password_field.setEchoMode(QLineEdit.Password)
        input_layout.addWidget(self.password_field)

        # Create the login button and add it to the input layout
        self.login_button = QPushButton('Login', self.central_widget)
        self.login_button.clicked.connect(self.login)
        input_layout.addWidget(self.login_button)

        return input_layout

    def login(self):
        """
        Authenticate the user by checking the master password entered against the hashed password stored in the database.
        If the master password is correct, open the main window. Otherwise, display an error message.
        """

        password = self.password_field.text()

        try:
            master_password = self.account_database.fetch_master_password()
            if master_password is None:
                self.account_database.set_master_password(
                    hash_str(password.encode()))
                QMessageBox.information(
                    self, 'Success', 'Master password set successfully.')
                self.close_and_show_next_window()
            else:
                if hash_str(password.encode()) == master_password:
                    self.close_and_show_next_window()
                else:
                    QMessageBox.warning(
                        self, 'Error', 'Incorrect master password.')
        except Exception as err:
            QMessageBox.critical(
                self, 'Error', str(err)
            )

    def close_and_show_next_window(self) -> None:
        """Closes the current window, and opens the next window.
        """
        self.close()

        # Create and show the next window
        self.main_window = MainWindow(self.account_database)
        self.main_window.show()
