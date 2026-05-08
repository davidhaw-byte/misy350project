from dataclasses import dataclass
from typing import Optional

@dataclass
class User:
    id: str
    name: str
    email: str
    password: str
    role: str

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            email=data.get("email", ""),
            password=data.get("password", ""),
            role=data.get("role", "Patient"),
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role,
        }

    def is_doctor(self) -> bool:
        return self.role.strip().lower() == "doctor"

    def is_patient(self) -> bool:
        return self.role.strip().lower() == "patient"


@dataclass
class Appointment:
    appointment_id: str
    patient_id: Optional[str]
    doctor_id: str
    date: str
    length: str
    status: str

    @classmethod
    def from_dict(cls, data: dict) -> "Appointment":
        return cls(
            appointment_id=data.get("appointment_id", ""),
            patient_id=data.get("patient_id"),
            doctor_id=data.get("doctor_id", ""),
            date=data.get("date", ""),
            length=data.get("length", ""),
            status=data.get("status", "available"),
        )

    def to_dict(self) -> dict:
        return {
            "appointment_id": self.appointment_id,
            "patient_id": self.patient_id,
            "doctor_id": self.doctor_id,
            "date": self.date,
            "length": self.length,
            "status": self.status,
        }

    def is_available(self) -> bool:
        return self.status.strip().lower() == "available"

    def is_scheduled(self) -> bool:
        return self.status.strip().lower() == "scheduled"

    def book(self, patient_id: str) -> None:
        self.patient_id = patient_id
        self.status = "scheduled"

    def cancel(self) -> None:
        self.patient_id = None
        self.status = "available"

    def reschedule(self, new_date: str) -> None:
        self.date = new_date
        self.status = "rescheduled"

    def update_status(self, new_status: str) -> None:
        self.status = new_status
