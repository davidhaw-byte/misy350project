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


def _get_doctor_name(appointment: Appointment, appointment_service: AppointmentService) -> str:
    doctor = appointment_service.database.get_user_by_id(appointment.doctor_id)
    return doctor.name if doctor else appointment.doctor_id


def format_appointments_for_display(appointments: List[Appointment], appointment_service: AppointmentService) -> List[dict]:
    return [
        {
            **appt.to_dict(),
            "doctor_name": _get_doctor_name(appt, appointment_service),
        }
        for appt in appointments
    ]


def render_sidebar(auth_service: AuthService, appointment_service: AppointmentService) -> None:
    with st.sidebar:
        if st.session_state.get("logged_in"):
            user = st.session_state.get("user")
            st.markdown(f"### Welcome, {user.name}")
            if user.is_patient():
                if st.button("🏠 Patient Dashboard", type="primary", use_container_width=True, key="patient_dashboard"):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Patient"
                    st.rerun()
                if st.button("📅 Schedule Appointment", type="primary", use_container_width=True, key="patient_schedule"):
                    st.session_state["page"] = "patient_schedule"
                    st.rerun()
                if st.button("👤 My Profile", use_container_width=True, key="patient_profile"):
                    st.session_state["page"] = "profile"
                    st.rerun()
                if st.button("📆 Calendar View", use_container_width=True, key="patient_calendar"):
                    st.session_state["page"] = "calendar"
                    st.rerun()
            if user.is_doctor():
                if st.button("🏥 Doctor Dashboard", type="primary", use_container_width=True, key="doctor_dashboard"):
                    st.session_state["page"] = "home"
                    st.session_state["role"] = "Doctor"
                    st.rerun()
                if st.button("👤 My Profile", use_container_width=True, key="doctor_profile"):
                    st.session_state["page"] = "profile"
                    st.rerun()
                if st.button("📆 Calendar View", use_container_width=True, key="doctor_calendar"):
                    st.session_state["page"] = "calendar"
                    st.rerun()
            if st.button("🚪 Log Out", type="primary", use_container_width=True, key="logout"):
                st.session_state["page"] = "login"
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["userid"] = None
                st.rerun()
        else:
            st.markdown("### Patient Appointment Tracker")
            if st.button("🔐 Log In", type="primary", use_container_width=True, key="login_sidebar"):
                st.session_state["page"] = "login"
                st.rerun()
            if st.button("📝 Register", type="secondary", use_container_width=True, key="register_sidebar"):
                st.session_state["page"] = "register"
                st.rerun()


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
                st.rerun()
            else:
                user, error = auth_service.login(email, password)
                if error:
                    st.session_state["feedback"] = ("error", error)
                    st.rerun()
                else:
                    st.session_state["feedback"] = ("success", f"Welcome back, {user.name}!")
                    st.session_state["logged_in"] = True
                    st.session_state["user"] = user
                    st.session_state["role"] = user.role
                    st.session_state["userid"] = user.id
                    st.session_state["page"] = "home"
                    st.rerun()

    st.markdown("---")
    st.markdown("**Test Accounts**")
    st.markdown("- Doctor: charlie.jones@gmail.com / DYo2J")
    st.markdown("- Patient: ivy.miller@gmail.com / 3vC79")


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
                st.rerun()
            elif "@" not in email:
                st.session_state["feedback"] = ("error", "Please enter a valid email address.")
                st.rerun()
            elif len(password) < 6:
                st.session_state["feedback"] = ("warning", "Password should be at least 6 characters long.")
                st.rerun()
            else:
                user, error = auth_service.register(name, email, password, role)
                if error:
                    st.session_state["feedback"] = ("error", error)
                    st.rerun()
                else:
                    st.session_state["feedback"] = ("success", f"Registered {user.name}! You may now log in.")
                    st.session_state["page"] = "login"
                    st.rerun()


def render_profile_page(appointment_service: AppointmentService) -> None:
    st.set_page_config("My Profile", layout="wide", initial_sidebar_state="expanded")
    st.title("👤 My Profile")
    display_feedback()
    user = st.session_state.get("user")
    if not user:
        st.error("No user data found. Please log in again.")
        return

    st.subheader("Account Details")
    st.write(f"**Name:** {user.name}")
    st.write(f"**Email:** {user.email}")
    st.write(f"**Role:** {user.role}")
    st.markdown("---")

    if user.is_patient():
        appointments = appointment_service.get_patient_appointments(user.id)
        st.subheader("Your Appointments")
        if appointments:
            st.dataframe(format_appointments_for_display(appointments, appointment_service), use_container_width=True)
        else:
            st.info("You have no scheduled appointments.")
    else:
        appointments = appointment_service.get_doctor_appointments(user.id)
        st.subheader("Your Doctor Appointments")
        if appointments:
            st.dataframe(format_appointments_for_display(appointments, appointment_service), use_container_width=True)
        else:
            st.info("You have no appointment records yet.")

    st.markdown("---")
    st.info("Use the sidebar to navigate to your dashboard, calendar, schedule, or logout.")


def render_calendar_page(appointment_service: AppointmentService) -> None:
    st.set_page_config("Calendar View", layout="wide", initial_sidebar_state="expanded")
    st.title("📅 Calendar View")
    display_feedback()
    user = st.session_state.get("user")
    if not user:
        st.error("Please log in to view calendar details.")
        return

    st.subheader("Upcoming Appointments")
    filter_by_date = st.checkbox("Limit to a specific date", key="calendar_filter_enabled")
    filter_date = None
    if filter_by_date:
        filter_date = st.date_input("Show appointments on", key="calendar_date_filter")

    if user.is_patient():
        appointments = appointment_service.get_patient_appointments(user.id)
        available = appointment_service.get_available()
        if filter_date:
            appointments = [appt for appt in appointments if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == filter_date]
            available = [appt for appt in available if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == filter_date]

        with st.expander("Your Scheduled Appointments", expanded=True):
            if appointments:
                st.dataframe(format_appointments_for_display(sorted(appointments, key=lambda appt: appt.date), appointment_service), use_container_width=True)
            else:
                st.info("No scheduled appointments found for this date.")

        with st.expander("Available Slots", expanded=True):
            if available:
                st.dataframe(format_appointments_for_display(sorted(available, key=lambda appt: appt.date), appointment_service), use_container_width=True)
            else:
                st.info("No available slots found for this date.")

    else:
        appointments = appointment_service.get_doctor_appointments(user.id)
        if filter_date:
            appointments = [appt for appt in appointments if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == filter_date]

        with st.expander("Your Appointments", expanded=True):
            if appointments:
                st.dataframe(format_appointments_for_display(sorted(appointments, key=lambda appt: appt.date), appointment_service), use_container_width=True)
            else:
                st.info("No appointments found for this date.")

        st.markdown("---")
        st.subheader("Status Summary")
        status_counts = {
            "available": len([appt for appt in appointments if appt.status == "available"]),
            "scheduled": len([appt for appt in appointments if appt.status == "scheduled"]),
            "completed": len([appt for appt in appointments if appt.status == "completed"]),
            "no show": len([appt for appt in appointments if appt.status == "no show"]),
            "cancel": len([appt for appt in appointments if appt.status == "cancel"]),
        }
        st.write(status_counts)


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
            st.dataframe(format_appointments_for_display(available[:5], appointment_service), use_container_width=True)
            if len(available) > 5:
                st.info(f"Showing 5 of {len(available)} available appointments.")
        else:
            st.info("No available appointments currently.")
        st.markdown("---")
        if st.button("📅 Go to Full Scheduler", type="primary", use_container_width=True):
            st.session_state["page"] = "patient_schedule"
            st.rerun()

    with col2:
        st.subheader("💬 Appointment Chat Assistant")
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state["messages"] = [{"role": "assistant", "content": "Hi! How can I help you?"}]
            st.rerun()

        with st.container(height=300):
            for message in st.session_state["messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])

        user_input = st.chat_input("Ask a question about your schedule...")
        if user_input:
            st.session_state["messages"].append({"role": "user", "content": user_input})
            response = chat_service.generate_response(user_input, st.session_state["user"], your_appointments)
            st.session_state["messages"].append({"role": "assistant", "content": response})
            st.rerun()

    st.divider()
    st.subheader("📅 Your Appointments")
    if your_appointments:
        st.dataframe(format_appointments_for_display(your_appointments, appointment_service), use_container_width=True)
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
        filter_by_date = st.checkbox("Filter by date", key="patient_schedule_filter_enabled")
        filtered_available = available
        if filter_by_date:
            search_date = st.date_input("Choose a date", key="search_date")
            filtered_available = [appt for appt in available if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == search_date]

        if filtered_available:
            options = {f"{appt.date} | {appt.length} | Dr: {_get_doctor_name(appt, appointment_service)}": appt.appointment_id for appt in filtered_available}
            selected = st.selectbox("Choose an appointment", list(options.keys()))
            if st.button("📅 Book Appointment", type="primary"):
                appointment_id = options[selected]
                _, error = appointment_service.book_appointment(appointment_id, st.session_state["userid"])
                if error:
                    st.session_state["feedback"] = ("error", error)
                else:
                    st.session_state["feedback"] = ("success", "Appointment booked successfully.")
                st.rerun()
        else:
            st.info("No available appointments matching your criteria.")

    with tab2:
        st.subheader("Manage Your Appointments")
        if your_appointments:
            options = {f"{appt.date} | {appt.length} | Dr: {_get_doctor_name(appt, appointment_service)}": appt.appointment_id for appt in your_appointments}
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
                        st.rerun()

                with col2:
                    if st.button("❌ Cancel Appointment", type="primary"):
                        if st.checkbox("Confirm cancellation"):
                            _, error = appointment_service.cancel_appointment(selected_id, st.session_state["userid"])
                            if error:
                                st.session_state["feedback"] = ("error", error)
                            else:
                                st.session_state["feedback"] = ("success", "Appointment canceled.")
                            st.rerun()
                        else:
                            st.warning("Please confirm cancellation.")
        else:
            st.info("You do not have any scheduled appointments.")
def render_doctor_dashboard(appointment_service: AppointmentService, chat_service: AIChatService) -> None:
    st.set_page_config("Doctor Dashboard", layout="wide", initial_sidebar_state="expanded")
    st.title("🏥 Doctor Dashboard")
    display_feedback()
    st.divider()

    tab1, tab2 = st.tabs(["📅 Create Availability", "📋 Manage Appointments"])

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
            st.rerun()

    with tab2:
        st.subheader("Manage Appointments")
        search_date = st.date_input("Filter by Date", key="doctor_search_date")
        status_filter = st.selectbox("Filter by Status", ["All", "available", "scheduled", "completed", "no show", "cancel"])

        doctor_appointments = appointment_service.get_doctor_appointments(st.session_state["userid"])
        if search_date:
            doctor_appointments = [appt for appt in doctor_appointments if datetime.strptime(appt.date, "%Y-%m-%d %H:%M:%S").date() == search_date]
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

                valid_statuses = ["scheduled", "completed", "no show", "cancel"]
                status_index = valid_statuses.index(appointment.status) if appointment.status in valid_statuses else 0
                new_status = st.selectbox("Update Status", valid_statuses, index=status_index)

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("💾 Save Status", type="primary"):
                        _, error = appointment_service.update_status(appointment_id, new_status)
                        if error:
                            st.session_state["feedback"] = ("error", error)
                        else:
                            st.session_state["feedback"] = ("success", "Appointment status updated.")
                        st.rerun()

                with col2:
                    if st.button("🗑️ Delete Appointment", type="secondary"):
                        if st.checkbox("Confirm deletion", key="confirm_delete"):
                            appointment_service.database.appointments.remove(appointment)
                            appointment_service.database.save_appointments()
                            st.session_state["feedback"] = ("success", "Appointment deleted.")
                            st.rerun()
                        else:
                            st.warning("Please confirm deletion.")
            else:
                st.error("Selected appointment could not be loaded.")
        else:
            st.info("No appointment records found for this doctor.")
