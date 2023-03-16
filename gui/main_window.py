
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QMainWindow,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QAbstractItemView,
    QHBoxLayout,
    QVBoxLayout,
    QCheckBox,
    QSpinBox,
    QMenu,
    QAction)
import random
import string
from utils.cryptography import decrypt, read_key_from_file
from gui.helpers import WINDOW_TITLE, get_gui_icon, get_gui_font, show_confirmation_message_box


class MainWindow(QMainWindow):
    """
    Main window of the application.
    """

    def __init__(self, account_database) -> None:
        """Initializes the main window of the application."""
        super().__init__()
        self.account_database = account_database
        self.context_menu = QMenu(self)
        # Set window properties
        self.set_window_properties()

        # Create the left and right layouts and add them to the central widget
        hbox = QHBoxLayout(self.central_widget)
        hbox.addLayout(self.create_left_layout())
        hbox.addWidget(self.create_right_layout())

        # Populate the table with account data
        self.refresh_table()

        # Show the window
        self.show()

    def set_window_properties(self) -> None:
        """Sets the properties of the main window."""
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(get_gui_icon())
        self.setGeometry(400, 250, 1300, 350)

        # Set the central widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)

    def create_right_layout(self) -> QGroupBox:
        """Creates the right-hand layout of the main window."""
        vbox = QVBoxLayout()

        # Create a group box to contain the table and the refresh button
        self.table_panel = QGroupBox('Account List', self.central_widget)
        self.table_panel.setLayout(vbox)

        # Create the password table and add it to the group box
        self.password_table = QTableWidget(self.table_panel)
        self.password_table.setColumnCount(6)
        self.password_table.setHorizontalHeaderLabels(
            ['UID', 'Website', 'Notes', 'Email', 'Username', 'Password'])
        self.password_table.setEditTriggers(QAbstractItemView.DoubleClicked)
        self.password_table.cellChanged.connect(self.handle_cell_changed)
        self.password_table.setContextMenuPolicy(Qt.CustomContextMenu)

        self.setup_context_menu()

        # Connect the context menu to the table's customContextMenuRequested signal
        self.password_table.customContextMenuRequested.connect(
            self.show_context_menu)

        vbox.addWidget(self.password_table)

        # Create the refresh button and add it to the group box
        refresh_button = QPushButton('Refresh', self.table_panel)
        refresh_button.clicked.connect(self.refresh_table)
        vbox.addWidget(refresh_button)

        return self.table_panel

    def setup_context_menu(self):
        """
        Sets up the context menu for the table.

        The context menu allows the user to delete rows or refresh the table.

        Returns:
            None
        """
        # Add an action to delete the selected row
        delete_action = QAction("Delete selected accounts", self)
        delete_action.triggered.connect(self.delete_rows)

        # Add an action to refresh the table
        refresh_action = QAction("Refresh accounts", self)
        refresh_action.triggered.connect(self.refresh_table)

        # Add actions to the context menu
        self.context_menu.addAction(delete_action)
        self.context_menu.addSeparator()
        self.context_menu.addAction(refresh_action)

    def show_context_menu(self, position):
        """
        Displays the context menu at the given position on the password table.

        Args:
            position (QPoint): The position on the password table where the context menu should be displayed.
        """
        self.context_menu.exec_(
            self.password_table.viewport().mapToGlobal(position))

    def delete_rows(self):
        """
        Deletes the selected row(s) from the password table and the account database.

        Returns:
        None
        """

        # Use try-except block to handle errors gracefully
        try:
            # Get the selected row(s) and delete them
            rows = set([index.row()
                        for index in self.password_table.selectedIndexes()])

            # Check if rows were selected
            if len(rows) > 0:
                # Confirm deletion with the user
                confirmation = show_confirmation_message_box(
                    "Are you sure you want to delete the selected row(s)?")

                if confirmation:
                    # Loop through selected rows in reverse order to avoid changing row numbers
                    for row in sorted(rows, reverse=True):
                        # Get the UID of the selected row and delete it from the account database
                        selected_row_uid = self.password_table.item(
                            row, 0).text()
                        self.account_database.delete_account(selected_row_uid)

                        # Remove the selected row from the password table
                        self.password_table.removeRow(row)
                else:
                    # User cancelled deletion
                    return
            else:
                # No rows were selected
                QMessageBox.warning(
                    self, "Error", "Please select a row to delete")
                return
        except Exception as e:
            # Catch all exceptions to prevent crashes and log the error message
            print(f"An error occurred: {e}")
            QMessageBox.critical(self, "Error", f"An error occurred: {e}")
            return

    def create_left_layout(self):
        """
        Creates and returns the left panel layout that contains the 'Save Account' and 'Generate Password' group boxes.

        Returns:
        QVBoxLayout: The left panel layout.
        """
        # Left panel - Account group box

        self.save_account_panel = QGroupBox(
            'Save Account',
            self.central_widget)
        save_account_layout = QFormLayout(self.save_account_panel)

        website_label = QLabel('Website:')
        notes_label = QLabel('Notes:')
        email_label = QLabel('Email:')
        username_label = QLabel('Username:')
        password_label = QLabel('Password:')

        website_label.setFont(get_gui_font())
        notes_label.setFont(get_gui_font())
        email_label.setFont(get_gui_font())
        username_label.setFont(get_gui_font())
        password_label.setFont(get_gui_font())

        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save_password)
        self.website_field = QLineEdit()
        self.notes_field = QLineEdit()
        self.email_field = QLineEdit()
        self.username_field = QLineEdit()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)

        save_account_layout.addRow(website_label, self.website_field)
        save_account_layout.addRow(notes_label, self.notes_field)
        save_account_layout.addRow(email_label, self.email_field)
        save_account_layout.addRow(username_label, self.username_field)
        save_account_layout.addRow(password_label, self.password_field)
        save_account_layout.addWidget(save_button)

        # Left panel - Password Generator

        self.generate_password_panel = QGroupBox(
            'Generate Password',
            self.central_widget)
        generate_password_layout = QFormLayout(self.generate_password_panel)

        generate_button = QPushButton('Generate')
        generate_button.clicked.connect(self.generate_password)

        length_label = QLabel('Length:')
        output_label = QLabel('Output:')
        length_label.setFont(get_gui_font())
        output_label.setFont(get_gui_font())

        self.options_a_z = QCheckBox('All lowercase letters (a-z)')
        self.options_A_Z = QCheckBox('All uppercase letters (A-Z)')
        self.options_0_9 = QCheckBox('All numbers (0-9)')
        self.options_symbols = QCheckBox('All special characters (!@#$%^&*)')
        self.output_field = QLineEdit()
        self.length_spin_box = QSpinBox(self.generate_password_panel)
        self.length_spin_box.setMinimum(1)

        generate_password_layout.addRow(self.options_a_z)
        generate_password_layout.addRow(self.options_A_Z)
        generate_password_layout.addRow(self.options_0_9)
        generate_password_layout.addRow(self.options_symbols)
        generate_password_layout.addRow(length_label, self.length_spin_box)
        generate_password_layout.addRow(output_label, self.output_field)
        generate_password_layout.addWidget(generate_button)

        left_layout = QVBoxLayout()
        left_layout.addWidget(self.save_account_panel)
        left_layout.addWidget(self.generate_password_panel)
        return left_layout

    def handle_cell_changed(self, row: int, col: int) -> None:
        """
        This function is called when the user edits a cell. It updates the
        corresponding account data in the database.

        Args:
            row (int): The row index of the cell that was edited.
            col (int): The column index of the cell that was edited.

        Returns:
            None
        """
        if self.populating_table:
            return
        try:
            # Get the edited text and the UID of the account being edited
            item = self.password_table.item(row, col)
            if item is not None:
                edited_text = item.text()
                uid = self.password_table.item(row, 0).text()

                # Update the account data in the database
                self.account_database.update_account(
                    uid,
                    self.password_table.horizontalHeaderItem(col).text(),
                    str(edited_text)
                )
        except Exception as err:
            QMessageBox.critical(
                self, 'Error', str(err)
            )

    def generate_password(self) -> None:
        """Generate a random password based on the selected options and length.

        Raises:
            Exception: If there is an error generating the password.
        """
        try:
            # Get the options and length
            options = ''
            length = self.length_spin_box.value()
            if self.options_a_z.isChecked():
                options += string.ascii_lowercase
            if self.options_A_Z.isChecked():
                options += string.ascii_uppercase
            if self.options_0_9.isChecked():
                options += string.digits
            if self.options_symbols.isChecked():
                options += '!@#$%^&*'

            # Generate password using selected options
            if options:
                password = ''.join(random.choice(options)
                                   for i in range(length))
                self.output_field.setText(password)
            else:
                # Show a warning message if no options are selected
                QMessageBox.warning(
                    self, 'Error', "Select at least one option"
                )
        except Exception as err:
            # Display an error message if it occurs
            QMessageBox.critical(
                self, 'Error', str(err)
            )

    def save_password(self) -> None:
        """
        Saves the current account data to the database and displays a message
        indicating success or failure.

        Returns:
            None
        """
        self.account_database.save_account(
            self.website_field.text(),
            self.notes_field.text(),
            self.email_field.text(),
            self.username_field.text(),
            self.password_field.text()
        )

        # Display a success message
        QMessageBox.information(
            self, 'Success', 'Account saved successfully.'
        )

    def refresh_table(self) -> None:
        """
        Refreshes the password table with the latest account data from the
        database.

        Returns:
            None
        """
        try:
            self.populating_table = True
            accounts = self.account_database.load_accounts()

            # Clear the existing rows from the table
            self.password_table.setRowCount(0)

            # Iterate through the accounts and add each one to the table
            for account in accounts:
                if str(account.username) == "master":
                    continue
                # Decrypt the account data, if key file available
                try:
                    key = read_key_from_file(account.key_file)
                    website = decrypt(
                        key=key,
                        ciphertext=account.website)
                    notes = decrypt(
                        key=key,
                        ciphertext=account.notes)
                    email = decrypt(
                        key=key,
                        ciphertext=account.email)
                    username = decrypt(
                        key=key,
                        ciphertext=account.username)
                    password = decrypt(
                        key=key,
                        ciphertext=account.password)
                except Exception as err:
                    print(err)
                    website, notes, email, username, password = str(account.website), str(
                        account.notes), str(account.email), str(account.username), str(account.password)

                # Add the account data to the table
                item = QTableWidgetItem(str(account.id))
                item.setFlags(Qt.ItemIsEnabled)
                self.password_table.insertRow(
                    self.password_table.rowCount())
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 0, item)
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 1, QTableWidgetItem(website))
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 2, QTableWidgetItem(notes))
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 3, QTableWidgetItem(email))
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 4, QTableWidgetItem(username))
                self.password_table.setItem(
                    self.password_table.rowCount() - 1, 5, QTableWidgetItem(password))
        except Exception as err:
            # Display an error message if an exception occurs
            QMessageBox.critical(
                self, 'Error', str(err)
            )
        finally:
            # Set populating_table to False after the table has been updated
            self.populating_table = False
