from cryptography.fernet import Fernet

def create_encryption_key():
    print(Fernet.generate_key().decode())


