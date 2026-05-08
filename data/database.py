import json
from pathlib import Path
from typing import List, Optional

from .models import Appointment, User


class DatabaseManager:
    def __init__(self, users_file: str = "users.json", appointments_file: str = "appointments.json"):
        self.users_file = Path(users_file)
        self.appointments_file = Path(appointments_file)
        self.users: List[User] = self.load_users()
        self.appointments: List[Appointment] = self.load_appointments()

    def load_json(self, file_path: Path, default):
        if not file_path.exists():
            return default
        try:
            with file_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default

    def save_json(self, file_path: Path, data):
        with file_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def load_users(self) -> List[User]:
        raw_users = self.load_json(self.users_file, [])
        return [User.from_dict(item) for item in raw_users]

    def save_users(self) -> None:
        self.save_json(self.users_file, [user.to_dict() for user in self.users])

    def load_appointments(self) -> List[Appointment]:
        raw_appointments = self.load_json(self.appointments_file, [])
        return [Appointment.from_dict(item) for item in raw_appointments]

    def save_appointments(self) -> None:
        self.save_json(self.appointments_file, [appointment.to_dict() for appointment in self.appointments])

    def get_user_by_email(self, email: str) -> Optional[User]:
        normalized = email.strip().lower()
        return next((user for user in self.users if user.email.strip().lower() == normalized), None)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return next((user for user in self.users if user.id == user_id), None)

    def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        return next((appt for appt in self.appointments if appt.appointment_id == appointment_id), None)
