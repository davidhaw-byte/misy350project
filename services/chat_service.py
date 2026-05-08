import os
from datetime import datetime
from typing import List, Optional

try:
    import openai
except ImportError:
    openai = None

from data.models import Appointment, User


class AIChatService:
    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.model = model
        self.api_key = os.getenv("OPENAI_API_KEY")
        if openai and self.api_key:
            openai.api_key = self.api_key

    def generate_response(self, message: str, user: User, appointments: List[Appointment]) -> str:
        if openai and self.api_key:
            try:
                response = openai.ChatCompletion.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are an appointment assistant for a clinic scheduling app."},
                        {"role": "user", "content": self._build_prompt(message, user, appointments)},
                    ],
                    max_tokens=250,
                )
                return response.choices[0].message.content.strip()
            except Exception:
                return self.fallback_response(message, user, appointments)

        return self.fallback_response(message, user, appointments)

    def _build_prompt(self, message: str, user: User, appointments: List[Appointment]) -> str:
        upcoming = [appt for appt in appointments if appt.patient_id == user.id and appt.is_scheduled()]
        if upcoming:
            appointment = upcoming[0]
            details = f"Next appointment is on {appointment.date} for {appointment.length}."
        else:
            details = "There are no scheduled appointments."

        return f"User: {message}\n\nPatient name: {user.name}. {details}"

    def fallback_response(self, message: str, user: User, appointments: List[Appointment]) -> str:
        normalized = message.strip().lower()
        upcoming = [appt for appt in appointments if appt.patient_id == user.id and appt.is_scheduled()]
        if "next" in normalized and "appointment" in normalized:
            if upcoming:
                appointment = upcoming[0]
                return f"Your next appointment is on {appointment.date} for {appointment.length}."
            return "You have no scheduled appointments."
        if "who" in normalized and "next" in normalized and "appointment" in normalized:
            if upcoming:
                return f"Your next appointment is with Dr. {upcoming[0].doctor_id}."
            return "You have no scheduled appointments."
        if "how" in normalized and "schedule" in normalized:
            return "Use the appointment scheduler page to choose an available slot and click Book Appointment."
        return "I couldn't find a good answer. Try asking about your next appointment or how to book a slot."
