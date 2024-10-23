import bcrypt


class HashPassword:
    def create_hash(self, password: str):
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify_hash(self, plain_password: str, hashed_password: str):
        return bcrypt.checkpw(plain_password.encode(),
                              hashed_password.encode())
