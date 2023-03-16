# Account-Manager
Account Manager is a Python application that enables users to securely manage their various account details. The program uses the AES-GCM encryption method to encrypt all account details, and saves them to a SQLite database. The program generates a unique encryption/decryption key for each account and saves it as a dynamic key.bin file (/keys directory). The user interface is built with PyQt5, while SQLAlchemy handles the database management.

## Technologies used

- Python
- SQLAlchemy
- PyQt5
- AES-GCM

## Get started
To get started, follow these steps:

1. Clone the repository to your local machine.
``` {.sourceCode}
git clone https://github.com/Altaaaf/Account-Manager.git
```
2. Install the required packages by running the following command:
``` {.sourceCode}
pip install -r requirements.txt
```

3. After installing the required packages, run main.py to start the application.

## Features

- [x] Password-protected main window, set upon initial usage
- [x] AES-GCM encryption of every account, with dynamically generated keys saved in the /keys directory
- [x] Automatic daily database backups saved in the /backup directory
- [x] Easy deletion of accounts using the context menu
- [x] Database synchronization based on updates and deletes made on the account table
- [x] Customizable password generator



## Usage

When the program starts, you will be prompted to enter a password to access the main window. The entered password will be used to lock the main window, and this password can be changed at any time.

After entering the correct password, you will see a table displaying all the accounts currently stored in the database. To add new accounts, click the "Add Account" button and fill in the details. To edit an account, simply double-click the corresponding cell in the table, make your changes, and press enter.

To delete one or more accounts, select the corresponding row(s) in the table and right-click to display the context menu. Then, click "Delete selected accounts".

In addition, the application features a customizable password generator that can be accessed by clicking the "Generate Password" button in the "Add Account" window. The user can specify the length, character set, and number of passwords to generate.

![python_rJXjVPZv4K](https://user-images.githubusercontent.com/75543185/225652878-97eb1d58-043c-448e-913e-b3cab1976656.png)
![python_5IrEnGfML2](https://user-images.githubusercontent.com/75543185/225652916-7e5c60ea-bed7-4a66-99b9-cca89e1ff895.png)
