import os
from hashlib import sha256
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
KEYS_DIRECTORY = os.path.join(os.getcwd(), "keys")
KEY_FILE_EXTENSION = ".bin"


def hash_str(key) -> str:
    """
    Hashes key input using SHA-256 and returns the output as a string

    Args:
        key (str or bytes): The string or bytes to be hashed.

    Returns:
        str: The SHA-256 hash of the key.
    """
    if isinstance(key, str):
        key = key.encode()
    return sha256(key).hexdigest()


def generate_key() -> bytes:
    """
    Generates a random 256-bit key.

    Returns:
        bytes: The generated key.
    """
    return secrets.token_bytes(32)


def encrypt(key: bytes, plaintext: str) -> bytes:
    """
    Encrypts a string using AES-GCM authenticated encryption.

    Args:
        key (bytes): The encryption key.
        plaintext (str): The plaintext to encrypt.

    Returns:
        bytes: The encrypted ciphertext, including the nonce and tag.
    """
    if is_empty_or_whitespace(plaintext):
        return plaintext
    aesgcm = AESGCM(key)
    nonce = secrets.token_bytes(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode('utf-8'), None)
    return nonce + ciphertext


def decrypt(key: bytes, ciphertext: bytes) -> str:
    """
    Decrypts a string using AES-GCM authenticated encryption.

    Args:
        key (bytes): The decryption key.
        ciphertext (bytes): The ciphertext to decrypt, including the nonce and tag.

    Returns:
        str: The decrypted plaintext.
    """
    if is_empty_or_whitespace(ciphertext):
        return ciphertext
    aesgcm = AESGCM(key)
    nonce = ciphertext[:12]
    ciphertext = ciphertext[12:]

    plaintext = aesgcm.decrypt(nonce, ciphertext, None)
    return plaintext.decode('utf-8')


def save_key_to_file(file_name: str, key: bytes) -> None:
    """
    Saves encryption/decryption keys to a file

    Args:
        file_name (str): The name to use for the key file.
        key (bytes): The encryption/decryptio key to save.

    Returns:
        None.
    """
    with open(build_key_file_path(file_name), 'wb') as key_file:
        key_file.write(key)


def read_key_from_file(file_name: str) -> bytes:
    """
    Reads a encryption/decryption keys from a file

    Args:
        file_name (str): The name of the key file to load.

    Returns:
        bytes: The Saves encryption/decryption key loaded from the file.
    """
    with open(build_key_file_path(file_name), 'rb') as key_file:
        key = key_file.read()
        return key


def delete_key_file(file_name: str) -> bool:
    """
    Deletes a file with the specified file name from the KEYS_DIRECTORY.

    Parameters:
    file_name (str): The name of the file to delete (without the file extension).

    Returns:
    bool: True if the file was deleted successfully, False if the file does not exist or could not be deleted.
    """
    file_path = build_key_file_path(file_name)
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
    except Exception as err:
        print(f"Error deleting file {file_path}: {err}")
    return False


def build_key_file_path(file_name: str) -> str:
    """Builds the full file path for a key file given the file name.

    Args:
        file_name (str): The name of the key file.

    Returns:
        str: The full file path for the key file, including the keys directory
            and file extension.
    """
    return os.path.join(KEYS_DIRECTORY, file_name + KEY_FILE_EXTENSION)


def is_empty_or_whitespace(strng: str) -> bool:
    """Checks if a string is empty or consists only of whitespace.

    Args:
        strng (str): The string to check.

    Returns:
        bool: True if the string is empty or consists only of whitespace, False otherwise.
    """
    return strng is None or not strng.strip()
