import streamlit as st

from data.database import DatabaseManager
from services.auth_service import AuthService
from services.appointment_service import AppointmentService
from services.chat_service import AIChatService
import ui

st.set_page_config("Patient Appointment Tracker", layout="wide", initial_sidebar_state="expanded")

# Initialize data and service layers
database = DatabaseManager()
auth_service = AuthService(database)
appointment_service = AppointmentService(database)
chat_service = AIChatService()

ui.init_session_state()
ui.render_sidebar(auth_service, appointment_service)

page = st.session_state.get("page", "login")
role = st.session_state.get("role")

if page == "login":
    ui.render_login_page(auth_service)
elif page == "register":
    ui.render_register_page(auth_service)
elif page == "home" and role == "Patient":
    ui.render_patient_dashboard(appointment_service, chat_service)
elif page == "patient_schedule" and role == "Patient":
    ui.render_patient_schedule(appointment_service)
elif page == "home" and role == "Doctor":
    ui.render_doctor_dashboard(appointment_service, chat_service)
else:
    st.info("Please use the sidebar to navigate to a page.")
