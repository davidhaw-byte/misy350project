#Doctor / Clinic Admin: Creates available time slots in the schedule, views the daily patient roster, and updates appointment statuses (e.g., "Completed" or "No-Show").
#Patient: Views the doctor's open availability, books a specific time slot, and cancels or reschedules their appointment if necessary.
import streamlit as st
import json
from pathlib import Path
from datetime import datetime
import uuid
import time

st.set_page_config("Patient Appointment Tracker", layout = "centered", initial_sidebar_state= "expanded")

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

with st.sidebar:
    st.markdown("Patient Appointment Sidebar")
    if "logged_in" in st.session_state and st.session_state["logged_in"] != False:
        user = st.session_state["user"]
        st.markdown(f"Welcome {user['email']}")
    else:
        st.markdown("Welcome! - Login")


if st.session_state["page"] == "login":
    st.subheader("Log In")
    with st.container(border=True):
        email_input = st.text_input("Email Address", key = "email_address_login")
        password_input = st.text_input("Password", type="password", key = "password_login")

        
        if st.button("Log In", type="primary",use_container_width=True):
            with st.spinner("Logging in..."):
                time.sleep(2) # Fake backend delay
                
                # Find user
                found_user = None
                for user in users:
                    if user["email"].strip().lower() == email_input.strip().lower() and user["password"] == password_input:
                        found_user = user
                        break
                
                if found_user:
                    st.success(f"Welcome back, {found_user['email']}!")
                    st.session_state["logged_in"]= True
                    st.session_state["user"] = found_user
                    st.session_state["role"] = found_user['role']
                    st.session_state['page'] = "home"
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    url = st.session_state["page"] = "register"
    link_text = "Create Account"
    st.markdown(f"Don't have an account? [{link_text}]({url})")
        

if st.session_state["page"] == "register":
    st.subheader("Register")
    with st.container(border=True):
        namereg_input = st.text_input("Full Name", key = "name_register")
        emailreg_input = st.text_input("Email Address", key = "email_address_register")
        passwordreg_input = st.text_input("Password", type="password", key = "password_register")
        account_typereg_input = st.selectbox("Account Type", ["Doctor", "Patient"])
        if st.button("Register", type="primary",use_container_width=True):
            with st.spinner("Registering..."):
                time.sleep(2) # Fake backend delay
                
                user_exists = False
                for user in users:
                    if user["email"].strip().lower() == emailreg_input.strip().lower():
                        st.error("Email already in use")
                        user_exists =True
                        break
                if not user_exists:
                    users.append(
                            {
                                "id" : str(uuid.uuid4()),
                                "name" : namereg_input,
                                "email" : emailreg_input,
                                "password" : passwordreg_input,
                                "role" : account_typereg_input
                            }
                        )
                    with json_path_users.open("w",encoding = "utf-8") as f:
                            json.dump(users, f, indent = 4)
                    st.success(f"Registered {namereg_input}!")
                    st.session_state["logged_in"]= False
                    st.session_state["user"] = None
                    st.session_state["role"] = None
                    st.session_state['page'] = "login"
                    time.sleep(2)
                    st.rerun()
if st.session_state["page"] == "home":
    st.markdown("home")
