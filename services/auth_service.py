import uuid
from typing import Optional, Tuple

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

    def login(self, email: str, password: str) -> Tuple[Optional[User], Optional[str]]:
        if not email or not password:
            return None, "Email and password are required."

        user = self.database.get_user_by_email(email)
        if not user:
            return None, "Invalid email or password."

        if not self.check_password(password, user.password):
            return None, "Invalid email or password."

        return user, None

    def register(self, name: str, email: str, password: str, role: str) -> Tuple[Optional[User], Optional[str]]:
        normalized_email = email.strip().lower()
        if not name or not email or not password or not role:
            return None, "All fields are required."

        if "@" not in normalized_email:
            return None, "Please enter a valid email address."

        if len(password) < 6:
            return None, "Password must be at least 6 characters long."

        if role not in ["Patient", "Doctor"]:
            return None, "Role must be Patient or Doctor."

        if self.database.get_user_by_email(normalized_email):
            return None, "Email already registered."

        user = User(
            id=str(uuid.uuid4()),
            name=name.strip(),
            email=normalized_email,
            password=self.hash_password(password),
            role=role.strip(),
        )

        self.database.users.append(user)
        self.database.save_users()
        return user, None
