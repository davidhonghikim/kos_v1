from cryptography.fernet import Fernet

def encrypt(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode())
