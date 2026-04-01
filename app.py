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

if "userid" not in st.session_state:
    st.session_state["userid"] = None

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
        "date" : "2026-04-10 22:30:00",
        "length": "30 minutes",
        "status" : "scheduled"
    }
]
possible_lengths = ["15 minutes", "30 minutes", "45 minutes", "60 minutes"]

json_path_users = Path("users.json")
json_path_appointments = Path("appointments.json")

if json_path_users.exists():
    with open(json_path_users, "r") as f:
        users = json.load(f)

if json_path_appointments.exists():
    with open(json_path_appointments, "r") as f:
        appointments = json.load(f)

with st.sidebar:
    if "logged_in" in st.session_state and st.session_state["logged_in"] != False:
        user = st.session_state["user"]
        st.markdown(f"Welcome {user['name']}")
        if st.button("Log Out", type = "primary", use_container_width=True):
            with st.spinner("Logging out..."):
                time.sleep(3)
                st.session_state["page"] = "login"
                st.session_state["logged_in"] = False
                st.session_state["user"] = None
                st.session_state["role"] = None
                st.session_state["userid"] = None
                st.rerun()

    else:
        st.markdown("Welcome! - Login or Register")
        if st.button("Login", type="primary", use_container_width=True):
            st.session_state["page"]  = "login"
        if st.button("Register", type = "primary", use_container_width=True, key="registerpage"):
            st.session_state["page"]  = "register"


if st.session_state["page"] == "login":
    st.set_page_config("Patient Appointment Tracker", layout = "centered", initial_sidebar_state= "expanded")
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
                    st.session_state["userid"] = found_user['id']
                    time.sleep(2)
                    st.rerun()
                else:
                    st.error("Invalid credentials")
    url = "registerpage" # Ask about in class
    link_text = "Create Account"
    st.markdown(f"Don't have an account? [{link_text}]({url})")
        

elif st.session_state["page"] == "register":
    st.set_page_config("Patient Appointment Tracker", layout = "centered", initial_sidebar_state= "expanded")
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
                    time.sleep(2)
                    st.rerun()

if st.session_state["role"] == "Patient":
    if st.session_state["page"] == "home":
        st.set_page_config("Patient Appointment Tracker", layout = "wide", initial_sidebar_state= "expanded")
        st.header("Patient Dashboard", text_alignment= "center") 
        st.divider()
        tab11, tab22 = st.tabs(["View Available Appointments", "Schedule an Appointment"], width="stretch")
        with tab11:
            pass
        with tab22:
            pass

elif st.session_state["role"] == "Doctor":
    if st.session_state["page"] == "home":
        st.set_page_config("Patient Appointment Tracker", layout = "wide", initial_sidebar_state= "expanded")
        st.header("Doctor Dashboard", text_alignment="center")
        st.divider()
        tab1, tab2 = st.tabs(["Create Availabilty", "Update Appointments"], width= "stretch", )
        with tab1:
            col1, col2 = st.columns([3,3])
            with col1:
                appt_dateandtime = st.datetime_input("Date and Time Available")
                appt_length = st.selectbox("Appointment Length", possible_lengths)
                if st.button("Create Appointment", key = "apptcreatebtn", type="primary", use_container_width=True):
                    with st.spinner("Creating..."):
                        time.sleep(2)
                        appt_exists = False
                        for appointment in appointments:
                            if (appointment["date"] == str(appt_dateandtime)) & (appointment["doctor_id"] == st.session_state["userid"]):
                                appt_exists = True
                                st.error("Appointment Already Exists!")
                                break
                        if not appt_exists:
                            appointments.append(
                                {
                                    "appointment_id" : str(uuid.uuid4()),
                                    "patient_id" : None,
                                    "doctor_id" : st.session_state["userid"],
                                    "date" : str(appt_dateandtime),
                                    "length": appt_length,
                                    "status" : "available"
                                }
                            )
                            with json_path_appointments.open("w",encoding = "utf-8") as f:
                                json.dump(appointments, f, indent = 4)
                            st.success(f"Appointment Created {appt_dateandtime}")
            with col2:
                search_date = st.date_input("Select Date", key = "search_for_date")
                found_appointments = []
                for appointment in appointments:
                    format_pattern = "%Y-%m-%d %H:%M:%S"
                    new_date = datetime.strptime(appointment['date'], format_pattern)
                    if new_date.date() == search_date:
                        found_appointments.append(appointment)
                if found_appointments == []:
                    st.error("No Appointments on that day")      
                else:                  
                    appt_by_date = st.dataframe(found_appointments) #Remove ID Columns with names and sort by time

        with tab2:
            col1, col2 = st.columns([4,2])
            selected_appointments = None
            with col1:
                appointment_list = appointments
                if "selected_status_filter" in st.session_state:
                    appointment_list = []
                    for appointment in appointments:
                        if appointment["status"] == st.session_state["selected_status_filter"]:
                            appointment_list.append(appointment)



                event = st.dataframe(
                    appointments,
                        on_select="rerun",
                        selection_mode="single-row"
                    )

                # Check if the user actually clicked on a row
                if event.selection.rows:
                    selected_index = event.selection.rows[0]
                    
                    # Use the index to grab the original dictionary from your list
                    selected_appointments = appointment_list[selected_index]
            with col2:
                with st.container(border= True):
                    st.markdown("### Appointment Details")
                    if selected_appointments:
                        with st.container(border= True):
                            st.markdown(f"**Status:** {selected_appointments['status']}")
                            st.markdown(f"**Appointment Time:** {selected_appointments['date']}")
                            st.markdown(f"**Appointment Length:** {selected_appointments['length']}")
                            #st.markdown(f"**Submit Date:** {selected_request['submitted_timestamp']}")
                            #st.markdown(f"**Excuse Type:** {selected_request['excuse_type']}")
                            #st.markdown(f"**Explanation:** {selected_request['explanation']}")
                        tab3, tab4 = st.tabs(['Change Status', 'Delete Availability'])
                        with tab3:
                            if selected_appointments['status'].strip().lower() == "scheduled":
                                update_status = st.radio("Change Status", ["Cancel", "Completed", "No Show"], key="decision_radio")
                                    

                                if st.button("Record Change", key = "record_status_change_btn", type="primary",use_container_width=True):
                                    with st.spinner("Recording the change..."):

                                        for appointment in appointments:
                                            if appointment["appointment_id"] == selected_appointments["appointment_id"]:
                                                appointment["status"] = update_status
                                                break
                                            
                                        with open(json_path_appointments,"w") as f :
                                            json.dump(appointments,f)
                                        
                                    st.success("Information recorded.")
                                    time.sleep(4)
                                    st.rerun()
                        with tab4:
                            if st.button("Delete Selected Appointment", key = "doctor_dlt_btn", type="primary"):
                                with st.spinner("Deleting..."):
                                    time.sleep(2)
                                    appointments.remove(appointments[selected_index]) 
                                    with open(json_path_appointments, "w") as f:
                                        json.dump(appointments, f)
                                    st.success("Appointment Deleted!")
                                    time.sleep(2)     
                                    st.rerun()


