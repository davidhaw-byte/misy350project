from datetime import datetime
from typing import List, Optional, Tuple
from uuid import uuid4

from data.database import DatabaseManager
from data.models import Appointment


class AppointmentService:
    def __init__(self, database: DatabaseManager):
        self.database = database

    def get_available(self) -> List[Appointment]:
        return [appt for appt in self.database.appointments if appt.is_available()]

    def get_patient_appointments(self, patient_id: str) -> List[Appointment]:
        return [appt for appt in self.database.appointments if appt.patient_id == patient_id]

    def get_doctor_appointments(self, doctor_id: str) -> List[Appointment]:
        return [appt for appt in self.database.appointments if appt.doctor_id == doctor_id]

    def get_appointment_by_id(self, appointment_id: str) -> Optional[Appointment]:
        return self.database.get_appointment_by_id(appointment_id)

    def create_availability(self, doctor_id: str, date_time: datetime, length: str) -> Tuple[Optional[Appointment], Optional[str]]:
        if not doctor_id or not date_time or not length:
            return None, "All fields are required."

        new_date = date_time.strftime("%Y-%m-%d %H:%M:%S")
        for appointment in self.get_doctor_appointments(doctor_id):
            if appointment.date == new_date:
                return None, "An availability already exists at that time."

        appointment = Appointment(
            appointment_id=str(uuid4()),
            patient_id=None,
            doctor_id=doctor_id,
            date=new_date,
            length=length,
            status="available",
        )
        self.database.appointments.append(appointment)
        self.database.save_appointments()
        return appointment, None

    def book_appointment(self, appointment_id: str, patient_id: str) -> Tuple[Optional[Appointment], Optional[str]]:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            return None, "Selected appointment was not found."
        if not appointment.is_available():
            return None, "The appointment is no longer available."

        appointment.book(patient_id)
        self.database.save_appointments()
        return appointment, None

    def cancel_appointment(self, appointment_id: str, patient_id: str) -> Tuple[Optional[Appointment], Optional[str]]:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment or appointment.patient_id != patient_id:
            return None, "You can only cancel your own scheduled appointment."

        appointment.cancel()
        self.database.save_appointments()
        return appointment, None

    def reschedule_appointment(self, appointment_id: str, patient_id: str, new_date_time: datetime) -> Tuple[Optional[Appointment], Optional[str]]:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment or appointment.patient_id != patient_id:
            return None, "You can only reschedule your own appointment."

        appointment.reschedule(new_date_time.strftime("%Y-%m-%d %H:%M:%S"))
        self.database.save_appointments()
        return appointment, None

    def update_status(self, appointment_id: str, new_status: str) -> Tuple[Optional[Appointment], Optional[str]]:
        appointment = self.get_appointment_by_id(appointment_id)
        if not appointment:
            return None, "Appointment not found."

        valid_statuses = ["available", "scheduled", "completed", "no show", "cancel"]
        if new_status not in valid_statuses:
            return None, f"Invalid status: {new_status}."

        appointment.update_status(new_status)
        self.database.save_appointments()
        return appointment, None

    def find_appointments_by_date(self, search_date: datetime) -> List[Appointment]:
        return [
            appt
            for appt in self.database.appointments
            if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == search_date.date()
        ]
