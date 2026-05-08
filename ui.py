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
    if "feedback" not in st.session_state:
        st.session_state["feedback"] = None
    if "doctor_messages" not in st.session_state:
        st.session_state["doctor_messages"] = [
            {"role": "assistant", "content": "Hello doctor! How can I assist with appointments?"}
        ]


def display_feedback() -> None:
    if st.session_state.get("feedback"):
        feedback_type, message = st.session_state["feedback"]
        if feedback_type == "success":
            st.success(message)
        elif feedback_type == "error":
            st.error(message)
        elif feedback_type == "info":
            st.info(message)
        elif feedback_type == "warning":
            st.warning(message)
        st.session_state["feedback"] = None
    with st.sidebar:
        if st.session_state.get("logged_in"):
            user = st.session_state.get("user")
            st.markdown(f"### Welcome, {user.name}")
            if user.is_patient():
                if st.button("🏠 Patient Dashboard", type="primary", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Patient"
                    st.experimental_rerun()
                if st.button("📅 Schedule Appointment", type="primary", use_container_width=True):
                    st.session_state["page"] = "patient_schedule"
                    st.experimental_rerun()
                if st.button("👤 My Profile", use_container_width=True):
                    st.session_state["page"] = "profile"
                    st.experimental_rerun()
                if st.button("📆 Calendar View", use_container_width=True):
                    st.session_state["page"] = "calendar"
                    st.experimental_rerun()
            if user.is_doctor():
                if st.button("🏥 Doctor Dashboard", type="primary", use_container_width=True):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Doctor"
                    st.experimental_rerun()
                if st.button("👤 My Profile", use_container_width=True):
                    st.session_state["page"] = "profile"
                    st.experimental_rerun()
                if st.button("📆 Calendar View", use_container_width=True):
                    st.session_state["page"] = "calendar"
                    st.experimental_rerun()
            if st.button("🚪 Log Out", type="primary", use_container_width=True):
                st.session_state["page"] = "login"
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["userid"] = None
                st.experimental_rerun()
        else:
            st.markdown("### Patient Appointment Tracker")
            if st.button("🔐 Log In", type="primary", use_container_width=True):
                st.session_state["page"] = "login"
                st.experimental_rerun()
            if st.button("📝 Register", type="secondary", use_container_width=True):
                st.session_state["page"] = "register"
                st.experimental_rerun()


def render_login_page(auth_service: AuthService) -> None:
    st.set_page_config("Patient Appointment Tracker", layout="centered", initial_sidebar_state="expanded")
    st.header("🔐 Log In")
    display_feedback()
    with st.form("login_form"):
        email = st.text_input("Email Address", key="email_address_login")
        password = st.text_input("Password", type="password", key="password_login")
        submitted = st.form_submit_button("Log In")
        if submitted:
            if not email or not password:
                st.session_state["feedback"] = ("error", "Please fill in all fields.")
                st.experimental_rerun()
            else:
                user, error = auth_service.login(email, password)
                if error:
                    st.session_state["feedback"] = ("error", error)
                    st.experimental_rerun()
                else:
                    st.session_state["feedback"] = ("success", f"Welcome back, {user.name}!")
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
    st.header("📝 Register")
    display_feedback()
    with st.form("register_form"):
        name = st.text_input("Full Name", key="name_register")
        email = st.text_input("Email Address", key="email_address_register")
        password = st.text_input("Password", type="password", key="password_register")
        role = st.selectbox("Account Type", ["Doctor", "Patient"])
        submitted = st.form_submit_button("Register")
        if submitted:
            if not name or not email or not password:
                st.session_state["feedback"] = ("error", "Please fill in all fields.")
                st.experimental_rerun()
            elif "@" not in email:
                st.session_state["feedback"] = ("error", "Please enter a valid email address.")
                st.experimental_rerun()
            elif len(password) < 6:
                st.session_state["feedback"] = ("warning", "Password should be at least 6 characters long.")
                st.experimental_rerun()
            else:
                user, error = auth_service.register(name, email, password, role)
                if error:
                    st.session_state["feedback"] = ("error", error)
                    st.experimental_rerun()
                else:
                    st.session_state["feedback"] = ("success", f"Registered {user.name}! You may now log in.")
                    st.session_state["page"] = "login"
                    st.experimental_rerun()


def render_patient_dashboard(
    appointment_service: AppointmentService,
    chat_service: AIChatService,
) -> None:
    st.set_page_config("Patient Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("🏠 Patient Dashboard")
    display_feedback()
    st.divider()
    available = appointment_service.get_available()
    your_appointments = appointment_service.get_patient_appointments(st.session_state["userid"])

    col1, col2 = st.columns([3, 2])
    with col1:
        st.subheader("📋 Available Appointments")
        if available:
            st.dataframe([appt.to_dict() for appt in available[:5]], use_container_width=True)
            if len(available) > 5:
                st.info(f"Showing 5 of {len(available)} available appointments.")
        else:
            st.info("No available appointments currently.")
        st.markdown("---")
        if st.button("📅 Go to Full Scheduler", type="primary", use_container_width=True):
            st.session_state["page"] = "patient_schedule"
            st.experimental_rerun()

    with col2:
        st.subheader("💬 Appointment Chat Assistant")
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": "Hi! How can I help you?"}]
            st.experimental_rerun()

        with st.container(height=300):
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
    st.subheader("📅 Your Appointments")
    if your_appointments:
        st.dataframe([appt.to_dict() for appt in your_appointments], use_container_width=True)
    else:
        st.info("You have no scheduled appointments.")


def render_patient_schedule(appointment_service: AppointmentService) -> None:
    st.set_page_config("Schedule Appointments", layout="wide", initial_sidebar_state="expanded")
    st.title("📅 Schedule Appointments")
    display_feedback()
    st.divider()

    available = appointment_service.get_available()
    your_appointments = appointment_service.get_patient_appointments(st.session_state["userid"])

    tab1, tab2 = st.tabs(["📋 Available Appointments", "📅 Your Appointments"])

    with tab1:
        st.subheader("Book an Appointment")
        search_date = st.date_input("Filter by Date (optional)", key="search_date")
        filtered_available = available
        if search_date:
            filtered_available = [appt for appt in available if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == search_date]

        if filtered_available:
            options = {f"{appt.date} | {appt.length} | Dr: {appt.doctor_id}": appt.appointment_id for appt in filtered_available}
            selected = st.selectbox("Choose an appointment", list(options.keys()))
            if st.button("📅 Book Appointment", type="primary"):
                appointment_id = options[selected]
                _, error = appointment_service.book_appointment(appointment_id, st.session_state["userid"])
                if error:
                    st.session_state["feedback"] = ("error", error)
                else:
                    st.session_state["feedback"] = ("success", "Appointment booked successfully.")
                st.experimental_rerun()
        else:
            st.info("No available appointments matching your criteria.")

    with tab2:
        st.subheader("Manage Your Appointments")
        if your_appointments:
            options = {f"{appt.date} | {appt.length} | Dr: {appt.doctor_id}": appt.appointment_id for appt in your_appointments}
            selected = st.selectbox("Select your appointment", list(options.keys()), key="your_appointments")
            selected_id = options[selected]
            selected_appointment = appointment_service.get_appointment_by_id(selected_id)

            if selected_appointment:
                st.markdown(f"**Status:** {selected_appointment.status}")
                st.markdown(f"**Date and Time:** {selected_appointment.date}")
                st.markdown(f"**Length:** {selected_appointment.length}")
                st.markdown(f"**Doctor:** {selected_appointment.doctor_id}")

                reschedule_time = st.datetime_input("New date and time", value=datetime.now())
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Reschedule Appointment", type="secondary"):
                        _, error = appointment_service.reschedule_appointment(selected_id, st.session_state["userid"], reschedule_time)
                        if error:
                            st.session_state["feedback"] = ("error", error)
                        else:
                            st.session_state["feedback"] = ("success", "Appointment rescheduled.")
                        st.experimental_rerun()

                with col2:
                    if st.button("❌ Cancel Appointment", type="primary"):
                        if st.checkbox("Confirm cancellation"):
                            _, error = appointment_service.cancel_appointment(selected_id, st.session_state["userid"])
                            if error:
                                st.session_state["feedback"] = ("error", error)
                            else:
                                st.session_state["feedback"] = ("success", "Appointment canceled.")
                            st.experimental_rerun()
                        else:
                            st.warning("Please confirm cancellation.")
        else:
            st.info("You do not have any scheduled appointments.")
def render_doctor_dashboard(appointment_service: AppointmentService, chat_service: AIChatService) -> None:
    st.set_page_config("Doctor Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("🏥 Doctor Dashboard")
    display_feedback()
    st.divider()

    tab1, tab2, tab3 = st.tabs(["📅 Create Availability", "📋 Manage Appointments", "💬 Assistant"])

    with tab1:
        st.subheader("Create New Availability")
        col1, col2 = st.columns(2)
        with col1:
            date_time = st.datetime_input("Date and Time Available")
        with col2:
            length = st.selectbox("Appointment Length", ["15 minutes", "30 minutes", "45 minutes", "60 minutes"])
        if st.button("➕ Create Appointment", type="primary"):
            appointment, error = appointment_service.create_availability(
                st.session_state["userid"], date_time, length
            )
            if error:
                st.session_state["feedback"] = ("error", error)
            else:
                st.session_state["feedback"] = ("success", f"Created availability for {appointment.date}.")
            st.experimental_rerun()

    with tab2:
        st.subheader("Manage Appointments")
        search_date = st.date_input("Filter by Date", key="doctor_search_date")
        status_filter = st.selectbox("Filter by Status", ["All", "available", "scheduled", "completed", "no show", "cancel"])

        doctor_appointments = appointment_service.get_doctor_appointments(st.session_state["userid"])
        if search_date:
            doctor_appointments = appointment_service.find_appointments_by_date(search_date)
            doctor_appointments = [appt for appt in doctor_appointments if appt.doctor_id == st.session_state["userid"]]
        if status_filter != "All":
            doctor_appointments = [appt for appt in doctor_appointments if appt.status == status_filter]

        if doctor_appointments:
            options = {f"{appt.date} | {appt.status} | Patient: {appt.patient_id or 'Open'}": appt.appointment_id for appt in doctor_appointments}
            selected = st.selectbox("Select an appointment", list(options.keys()), key="doctor_appointments")
            appointment_id = options[selected]
            appointment = appointment_service.get_appointment_by_id(appointment_id)

            if appointment:
                st.markdown(f"**Status:** {appointment.status}")
                st.markdown(f"**Appointment Time:** {appointment.date}")
                st.markdown(f"**Length:** {appointment.length}")
                st.markdown(f"**Patient:** {appointment.patient_id or 'Available'}")

                new_status = st.selectbox("Update Status", ["scheduled", "completed", "no show", "cancel"], index=["scheduled", "completed", "no show", "cancel"].index(appointment.status) if appointment.status in ["scheduled", "completed", "no show", "cancel"] else 0)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Status", type="primary"):
                        _, error = appointment_service.update_status(appointment_id, new_status)
                        if error:
                            st.session_state["feedback"] = ("error", error)
                        else:
                            st.session_state["feedback"] = ("success", "Appointment status updated.")
                        st.experimental_rerun()

                with col2:
                    if st.button("🗑️ Delete Appointment", type="secondary"):
                        if st.checkbox("Confirm deletion"):
                            appointment_service.database.appointments.remove(appointment)
                            appointment_service.database.save_appointments()
                            st.session_state["feedback"] = ("success", "Appointment deleted.")
                            st.experimental_rerun()
                        else:
                            st.warning("Please confirm deletion.")
        else:
            st.info("No appointment records found for this doctor.")

    with tab3:
        st.subheader("Doctor Chat Assistant")
        if st.button("🗑️ Clear Chat", key="clear_doctor_chat"):
            st.session_state["doctor_messages"] = [{"role": "assistant", "content": "Hello doctor! How can I assist with appointments?"}]
            st.experimental_rerun()

        with st.container(height=300):
            for message in st.session_state["doctor_messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        user_input = st.chat_input("Ask about appointments or patients...")
        if user_input:
            st.session_state["doctor_messages"].append({"role": "user", "content": user_input})
            # For doctor chat, use the same service but with doctor context
            response = chat_service.generate_response(user_input, st.session_state["user"], doctor_appointments)
            st.session_state["doctor_messages"].append({"role": "assistant", "content": response})
            st.experimental_rerun()
