
import qdarktheme
import sys
from database.database import AccountDatabase
from gui.login_window import LoginWindow
from PyQt5.QtWidgets import QApplication


if __name__ == '__main__':
    app = QApplication(sys.argv)
    qdarktheme.setup_theme(theme="dark")
    ex = LoginWindow(AccountDatabase())
    sys.exit(app.exec_())
