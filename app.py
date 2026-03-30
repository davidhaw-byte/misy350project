#Doctor / Clinic Admin: Creates available time slots in the schedule, views the daily patient roster, and updates appointment statuses (e.g., "Completed" or "No-Show").
#Patient: Views the doctor's open availability, books a specific time slot, and cancels or reschedules their appointment if necessary.
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config("Patient Appointment Tracker", layout = "wide", initial_sidebar_state= "expanded")

#Session State Initialization
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    
if "user" not in st.session_state:
    st.session_state["user"] = None

if "page" not in st.session_state:
    st.session_state["page"] = "login"

if "role" not in st.session_state:
    st.session_state["role"] = None

users = [
    {
        "id" : str(uuid.uuid4()),
        "name" : "Ivonne Rivera",
        "email" : "bonny@gmail.com",
        "password" : "Il1kefl0wer$",
        "role" : "Doctor"
    },
    {
        "id" : str(uuid.uuid4()),
        "name" : "David Hawtof",
        "email" : "dgh@gmail.com",
        "password" : "dowman56!!",
        "role" : "Patient"
    }
]
appointments = [
    {
        "appointment_id" : str(uuid.uuid4()),
        "patient_id" : None,
        "doctor_id" : "1",#Change ID
        "date" : "03_20_2026",
        "status" : "available"
    }
]

json_path_users = Path("users.json")
json_path_appointments = Path("appointments.json")

if json_path_users.exists():
    with open(json_path_users, "r") as f:
        users = json.load(f)

if json_path_appointments.exists():
    with open(json_path_appointments, "r") as f:
        appointments = json.load(f)


