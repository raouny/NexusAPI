from hashlib import pbkdf2_hmac
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import configparser
import os


key = "qK3uLe8GIr6Frue2mGqr3dfkWWiwcXFbmtU780JbrwU="


def encrypt(message):
    message.encode()
    f = Fernet(key)
    encrypted = f.encrypt(message)
    return encrypted

def decrypt(encrypted):
    f = Fernet(key)
    decrypted = f.decrypt(str(encrypted))
    return decrypted



