from cryptography.fernet import Fernet
import base64
import os
from dotenv import load_dotenv

# Load encryption key from environment
load_dotenv()

class Encryptor:
    def __init__(self):
        # Get or generate encryption key
        self.key = os.getenv('ENCRYPTION_KEY')
        if not self.key:
            self.key = Fernet.generate_key()
            with open('.env', 'a') as f:
                f.write(f'\nENCRYPTION_KEY={self.key.decode()}\n')
        
        # Initialize Fernet instance
        if isinstance(self.key, str):
            self.key = self.key.encode()
        self.fernet = Fernet(self.key)

    def encrypt(self, data):
        """Encrypt data"""
        if isinstance(data, str):
            data = data.encode()
        return self.fernet.encrypt(data)

    def decrypt(self, encrypted_data):
        """Decrypt data"""
        return self.fernet.decrypt(encrypted_data).decode()

    def encrypt_file(self, file_path):
        """Encrypt a file"""
        with open(file_path, 'rb') as file:
            data = file.read()
        
        encrypted_data = self.encrypt(data)
        
        with open(file_path + '.encrypted', 'wb') as file:
            file.write(encrypted_data)

    def decrypt_file(self, encrypted_file_path):
        """Decrypt a file"""
        with open(encrypted_file_path, 'rb') as file:
            encrypted_data = file.read()
        
        decrypted_data = self.decrypt(encrypted_data)
        
        output_path = encrypted_file_path.replace('.encrypted', '.decrypted')
        with open(output_path, 'wb') as file:
            file.write(decrypted_data.encode())
        
        return output_path
