import uuid
from typing import Optional

import bcrypt

from data.database import DatabaseManager
from data.models import User


class AuthService:
    def __init__(self, database: DatabaseManager):
        self.database = database

    def hash_password(self, password: str) -> str:
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def check_password(self, raw_password: str, stored_password: str) -> bool:
        if stored_password.startswith("$2b$") or stored_password.startswith("$2a$"):
            try:
                return bcrypt.checkpw(raw_password.encode("utf-8"), stored_password.encode("utf-8"))
            except ValueError:
                return False
        return raw_password == stored_password

    def login(self, email: str, password: str) -> tuple[Optional[User], Optional[str]]:
        user = self.database.get_user_by_email(email)
        if not user:
            return None, "Invalid email or password"

        if not self.check_password(password, user.password):
            return None, "Invalid email or password"

        if not user.password.startswith("$2"):
            user.password = self.hash_password(password)
            self.database.save_users()

        return user, None

    def register(self, name: str, email: str, password: str, role: str) -> tuple[Optional[User], Optional[str]]:
        normalized_email = email.strip().lower()
        if self.database.get_user_by_email(normalized_email):
            return None, "Email already in use"

        hashed_password = self.hash_password(password)
        user = User(
            id=str(uuid.uuid4()),
            name=name.strip(),
            email=normalized_email,
            password=hashed_password,
            role=role.strip(),
        )
        self.database.users.append(user)
        self.database.save_users()
        return user, None

    def logout(self) -> None:
        pass
