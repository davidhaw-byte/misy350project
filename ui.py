import streamlit as st
from datetime import datetime
from typing import List, Optional

from data.models import Appointment, User
from services.appointment_service import AppointmentService
from services.auth_service import AuthService
from services.chat_service import AIChatService


def init_session_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "page" not in st.session_state:
        st.session_state["page"] = "login"
    if "role" not in st.session_state:
        st.session_state["role"] = None
    if "userid" not in st.session_state:
        st.session_state["userid"] = None
    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant", "content": "Hi! How can I help you?"}
        ]


def render_sidebar(auth_service: AuthService, appointment_service: AppointmentService) -> None:
    with st.sidebar:
        if st.session_state.get("logged_in"):
            user = st.session_state.get("user")
            st.markdown(f"### Welcome, {user.name}")
            if user.is_patient():
                if st.button("Patient Dashboard", type="primary", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Patient"
                    st.experimental_rerun()
                if st.button("Schedule Appointment", type="primary", use_container_width=True):
                    st.session_state["page"] = "patient_schedule"
                    st.experimental_rerun()
            if user.is_doctor():
                if st.button("Doctor Dashboard", type="primary", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Doctor"
                    st.experimental_rerun()
            if st.button("Log Out", type="primary", use_container_width=True):
                st.session_state["page"] = "login"
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["userid"] = None
                st.experimental_rerun()
        else:
            st.markdown("### Patient Appointment Tracker")
            if st.button("Log In", type="primary", use_container_width=True):
                st.session_state["page"] = "login"
                st.experimental_rerun()
            if st.button("Register", type="secondary", use_container_width=True):
                st.session_state["page"] = "register"
                st.experimental_rerun()


def render_login_page(auth_service: AuthService) -> None:
    st.set_page_config("Patient Appointment Tracker", layout="centered", initial_sidebar_state="expanded")
    st.header("Log In")
    with st.form("login_form"):
        email = st.text_input("Email Address", key="email_address_login")
        password = st.text_input("Password", type="password", key="password_login")
        submitted = st.form_submit_button("Log In")
        if submitted:
            user, error = auth_service.login(email, password)
            if error:
                st.error(error)
            else:
                st.success(f"Welcome back, {user.name}!")
                st.session_state["logged_in"] = True
                st.session_state["user"] = user
                st.session_state["role"] = user.role
                st.session_state["userid"] = user.id
                st.session_state["page"] = "home"
                st.experimental_rerun()

    st.markdown("---")
    st.markdown("**Test Accounts**")
    st.markdown("- Doctor: bonny@gmail.com / Il1kefl0wer$")
    st.markdown("- Patient: dgh@gmail.com / dowman56!!")


def render_register_page(auth_service: AuthService) -> None:
    st.set_page_config("Patient Appointment Tracker", layout="centered", initial_sidebar_state="expanded")
    st.header("Register")
    with st.form("register_form"):
        name = st.text_input("Full Name", key="name_register")
        email = st.text_input("Email Address", key="email_address_register")
        password = st.text_input("Password", type="password", key="password_register")
        role = st.selectbox("Account Type", ["Doctor", "Patient"])
        submitted = st.form_submit_button("Register")
        if submitted:
            user, error = auth_service.register(name, email, password, role)
            if error:
                st.error(error)
            else:
                st.success(f"Registered {user.name}! You may now log in.")
                st.session_state["page"] = "login"
                st.experimental_rerun()


def render_patient_dashboard(
    appointment_service: AppointmentService,
    chat_service: AIChatService,
) -> None:
    st.set_page_config("Patient Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("Patient Dashboard")
    st.divider()
    available = appointment_service.get_available()
    your_appointments = appointment_service.get_patient_appointments(st.session_state["userid"])

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("Available Appointments")
        if available:
            st.dataframe([appt.to_dict() for appt in available], use_container_width=True)
        else:
            st.info("No available appointments currently.")

        if st.button("Go to Scheduler", type="primary", use_container_width=True):
            st.session_state["page"] = "patient_schedule"
            st.experimental_rerun()

    with col2:
        st.subheader("Appointment Chat Assistant")
        if st.button("Clear Chat", key="clear_chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": "Hi! How can I help you?"}]
            st.experimental_rerun()

        for message in st.session_state["messages"]:
            with st.chat_message(message["role"]):
                st.write(message["content"])

        user_input = st.chat_input("Ask a question about your schedule...")
        if user_input:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            response = chat_service.generate_response(user_input, st.session_state["user"], your_appointments)
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.experimental_rerun()

    st.divider()
    st.subheader("Your Appointments")
    if your_appointments:
        st.dataframe([appt.to_dict() for appt in your_appointments], use_container_width=True)
    else:
        st.info("You have no scheduled appointments.")


def render_patient_schedule(appointment_service: AppointmentService) -> None:
    st.set_page_config("Schedule Appointments", layout="wide", initial_sidebar_state="expanded")
    st.title("Schedule Appointments")
    st.divider()

    available = appointment_service.get_available()
    your_appointments = appointment_service.get_patient_appointments(st.session_state["userid"])

    with st.container():
        st.subheader("Available Appointments")
        if available:
            options = {f"{appt.date} | {appt.length} | Dr: {appt.doctor_id}": appt.appointment_id for appt in available}
            selected = st.selectbox("Choose an appointment", [*options.keys()])
            if st.button("Book Appointment", type="primary"):
                appointment_id = options[selected]
                _, error = appointment_service.book_appointment(appointment_id, st.session_state["userid"])
                if error:
                    st.error(error)
                else:
                    st.success("Appointment booked successfully.")
                    st.experimental_rerun()
        else:
            st.info("No available appointments to book.")

    st.divider()
    st.subheader("Your Scheduled Appointments")
    if your_appointments:
        options = {f"{appt.date} | {appt.length} | Dr: {appt.doctor_id}": appt.appointment_id for appt in your_appointments}
        selected = st.selectbox("Select your appointment", [*options.keys()], key="your_appointments")
        selected_id = options[selected]
        selected_appointment = appointment_service.get_appointment_by_id(selected_id)

        reschedule_time = st.datetime_input("New date and time", value=datetime.now())
        if st.button("Reschedule Appointment", type="secondary"):
            _, error = appointment_service.reschedule_appointment(selected_id, st.session_state["userid"], reschedule_time)
            if error:
                st.error(error)
            else:
                st.success("Appointment rescheduled.")
                st.experimental_rerun()

        if st.button("Cancel Appointment", type="primary"):
            _, error = appointment_service.cancel_appointment(selected_id, st.session_state["userid"])
            if error:
                st.error(error)
            else:
                st.success("Appointment canceled.")
                st.experimental_rerun()
    else:
        st.info("You do not have any scheduled appointments.")


def render_doctor_dashboard(appointment_service: AppointmentService) -> None:
    st.set_page_config("Doctor Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("Doctor Dashboard")
    st.divider()

    with st.container():
        st.subheader("Create Availability")
        date_time = st.datetime_input("Date and Time Available")
        length = st.selectbox("Appointment Length", ["15 minutes", "30 minutes", "45 minutes", "60 minutes"])
        if st.button("Create Appointment", type="primary"):
            appointment, error = appointment_service.create_availability(
                st.session_state["userid"], date_time, length
            )
            if error:
                st.error(error)
            else:
                st.success(f"Created availability for {appointment.date}.")
                st.experimental_rerun()

    st.divider()
    st.subheader("Manage Appointments")
    doctor_appointments = appointment_service.get_doctor_appointments(st.session_state["userid"])
    if doctor_appointments:
        options = {f"{appt.date} | {appt.status} | Patient: {appt.patient_id or 'Open'}": appt.appointment_id for appt in doctor_appointments}
        selected = st.selectbox("Select an appointment", [*options.keys()], key="doctor_appointments")
        appointment_id = options[selected]
        appointment = appointment_service.get_appointment_by_id(appointment_id)

        if appointment:
            st.markdown(f"**Status:** {appointment.status}")
            st.markdown(f"**Appointment Time:** {appointment.date}")
            st.markdown(f"**Length:** {appointment.length}")
            st.markdown(f"**Patient:** {appointment.patient_id or 'Available'}")

            new_status = st.selectbox("Update Status", ["scheduled", "completed", "no show", "cancel"], index=0)
            if st.button("Save Status", type="primary"):
                _, error = appointment_service.update_status(appointment_id, new_status)
                if error:
                    st.error(error)
                else:
                    st.success("Appointment status updated.")
                    st.experimental_rerun()

            if st.button("Delete Appointment", type="secondary"):
                appointment_service.database.appointments.remove(appointment)
                appointment_service.database.save_appointments()
                st.success("Appointment deleted.")
                st.experimental_rerun()
    else:
        st.info("No appointment records found for this doctor.")
