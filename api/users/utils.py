import binascii
import os


def generate_token(length: int = 20):
    """Генерация токена по заданной длине `length`."""
    return binascii.hexlify(os.urandom(length)).decode()
