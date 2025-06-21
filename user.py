import uuid
import hashlib

class User:
    def __init__(self, username, password):
        self.id = str(uuid.uuid4())
        self.username = username
        self.password = self.hash_password(password)

    @staticmethod
    def hash_password(password):
        return hashlib.sha256(password.encode()).hexdigest()
