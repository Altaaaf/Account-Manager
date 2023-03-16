from sqlalchemy import (
    create_engine,
    event,
    Column,
    Integer,
    String)
from sqlalchemy.orm import sessionmaker, declarative_base
from utils.cryptography import (
    is_empty_or_whitespace,
    save_key_to_file,
    encrypt,
    hash_str,
    generate_key,
    encrypt,
    read_key_from_file,
    delete_key_file)
import os
import shutil
from datetime import date
Base = declarative_base()


class Account(Base):
    __tablename__ = 'accounts'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    key_file = Column(String(256), unique=True, nullable=True)
    website = Column(String(256), nullable=True)
    notes = Column(String(256), nullable=True)
    email = Column(String(256), nullable=True)
    username = Column(String(256), nullable=True)
    password = Column(String(256), nullable=False)


class AccountDatabase:
    """A class to interact with the account database.

    Attributes:
    -----------
    engine : sqlalchemy.engine.base.Engine
        The SQLAlchemy engine to connect to the database.
    session : sqlalchemy.orm.session.Session
        The SQLAlchemy session to execute database operations.
    master_pass : str
        The master password to encrypt and decrypt account data.
    """

    def __init__(self):
        """Initializes the AccountDatabase object.
        """
        self.engine = create_engine('sqlite:///Accounts.db')
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)
        os.makedirs("backup", exist_ok=True)
        os.makedirs("keys", exist_ok=True)

        @event.listens_for(self.engine, "commit")
        def backup_database(*args):
            backup_file_path = os.path.join(
                "backup",
                f"accounts_backup_{date.today()}.db")
            if not os.path.exists(backup_file_path):
                shutil.copy("Accounts.db", backup_file_path)
                print(f"Backup file {backup_file_path} created.")

    def fetch_master_password(self):
        """Fetches the hashed master password from the database.

        Returns:
            str or None: The hashed master password, or None if it doesn't exist.
        """
        with self.session() as session:
            account = session.query(Account).filter_by(
                username='master').first()
            if account:
                return account.password
            return None

    def set_master_password(self, hashed_password):
        """Saves the hashed master password to the database.

        Args:
            hashed_password (str): The hashed master password.
        """
        with self.session() as session:
            account = Account(username='master', password=str(hashed_password))
            session.add(account)
            session.commit()

    def is_key_exists(self, key):
        """Checks if the specified key exists in the database.

        Args:
            key (str): The key to check.

        Returns:
        Account or None: The Account object that matches the specified key, or None if it doesn't exist.
        """
        with self.session() as session:
            return session.query(Account).filter_by(key_file=key).first()

    def load_accounts(self):
        """Loads all accounts from the database.

        Returns:
            list: A list of all Account objects in the database.
        """
        with self.session() as session:
            return session.query(Account).all()

    def save_account(self, website, notes, email, username, password):
        """Saves a new account to the database.

        Args:
            website (str): The website associated with the account.
            notes (str): Any additional notes for the account.
            email (str): The email address associated with the account.
            username (str): The username for the account.
            password (str): The password for the account.
        """
        try:
            with self.session() as session:
                key = generate_key()
                hashed_key = hash_str(key)[:15]
                account = Account(id=None,
                                  key_file=hashed_key,
                                  website=encrypt(key, website),
                                  notes=encrypt(key, notes),
                                  email=encrypt(key, email),
                                  username=encrypt(key, username),
                                  password=encrypt(key, password))
                session.add(account)
                session.commit()

                save_key_to_file(hashed_key, key)
        except Exception as err:
            print(f"Error saving account to database: {err}")
            raise

    def update_account(self, uid: int, column_updated: str, new_value: str) -> None:
        """
        Updates the value of a specific column in the account table for the account with the given UID.

        Args:
            uid (int): The UID of the account to update.
            column_updated (str): The name of the column to update.
            new_value (str): The new value to set for the column.

        Raises:
            ValueError: If the column name is invalid.
        """
        with self.session() as session:
            row = session.query(Account).filter_by(id=uid).first()

            if not row:
                raise ValueError(f"Account with UID {uid} not found.")

            if not is_empty_or_whitespace(new_value):
                key = read_key_from_file(row.key_file)

                new_value = encrypt(key, new_value)

            if column_updated == "Website":
                row.website = new_value
            elif column_updated == "Notes":
                row.notes = new_value
            elif column_updated == "Email":
                row.email = new_value
            elif column_updated == "Username":
                row.username = new_value
            elif column_updated == "Password":
                row.password = new_value
            else:
                raise ValueError(f"Invalid column name: {column_updated}")
            session.commit()

    def delete_account(self, uid: int) -> None:
        """
        Deletes the account with the specified UID from the database and deletes its associated key file.

        Parameters:
        uid (int): The UID of the account to delete.

        Returns:
        None

        Raises:
        TypeError: If the uid argument is not an integer.
        """
        with self.session() as session:
            account_to_delete = session.query(
                Account).filter_by(id=uid).first()
            if account_to_delete:
                session.delete(account_to_delete)
                delete_key_file(account_to_delete.key_file)
                session.commit()
