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

if "messages" not in st.session_state:
    st.session_state["messages"] = [
        {
            "role": "assistant",
            "content": "Hi! How can I help you?"
        }
    ]

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
        if st.session_state["role"] == 'Patient':
            if st.button("Patient Dashboard", type="primary", use_container_width=True):
                st.session_state["page"] = "home"
                st.rerun()
            if st.button("View Appointments", type="primary", use_container_width=True):
                st.session_state["page"] = "patient_appt_view"
                st.rerun()
            if st.button("Schedule Appointment", type="primary", use_container_width=True):
                st.session_state["page"] = "patient_schedule"
                st.rerun()
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
    st.markdown(f"Don't have an account?") #[{link_text}]({url})")
    if st.button("Create Account", type="primary", use_container_width=False):
        st.session_state["page"] = "register"
        st.rerun()
        

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
        colpat1, colpat2 = st.columns([4,2])
        with colpat1:
            st.subheader("Available Appointments", text_alignment='center')
            available_appts = []
            for appointment in appointments:
                if appointment['status'] == 'available':
                    available_appts.append(appointment)
            st.dataframe(available_appts[:5], column_order=['status', 'doctor_id', 'date', 'length'])
            if st.button("View All", type = "primary", use_container_width=True):
                st.session_state["page"] = "patient_appt_view"
                st.rerun()
        with colpat2:
            st.subheader("Patient Chat Assistant", text_alignment="center")
            st.caption("Try Asking: When's my next Appointment")
            if st.button("Clear", key= "clear_chat_btn"):
                    st.session_state["messages"] = [
                        {
                            "role" : "assistant", 
                            "content" : "Hi! How can I help you?"
                        }
                    ]

            with st.container(border=True, height = 150):
                for message in st.session_state["messages"]:
                    with st.chat_message(message["role"]):
                        st.write(message["content"])
            
            user_input = st.chat_input("Ask a question ... ")
            if user_input == "How long is my next appointment":
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {
                            "role" : "user",
                            "content" : user_input
                        }
                    )
                    next_length = None
                    for appointment in appointments:
                        if st.session_state["userid"] == appointment["patient_id"]:
                            next_length = appointment['length']
                            break
                    if next_length:
                        ai_response = f"Your next appointment is {next_length} long"
                    else:
                        ai_response = "You have no appointments scheduled"
                    st.session_state["messages"].append(
                        {
                            "role" : "assistant",
                            "content" : ai_response
                        }
                    )
                    time.sleep(2)
                    st.rerun()
            elif user_input == "When is my next appointment":
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {
                            "role" : "user",
                            "content" : user_input
                        }
                    )
                    next_date = None
                    for appointment in appointments:
                        if st.session_state["userid"] == appointment["patient_id"]:
                            next_date = appointment['date']
                            break
                    if next_date:
                        ai_response = f"Your next appointment is {next_date}"
                    else:
                        ai_response = "You have no appointments scheduled"
                    st.session_state["messages"].append(
                        {
                            "role" : "assistant",
                            "content" : ai_response
                        }
                    )
                    time.sleep(2)
                    st.rerun()
            elif user_input == "Who is my next appointment with":
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {
                            "role" : "user",
                            "content" : user_input
                        }
                    )
                    next_doctor = None
                    for appointment in appointments:
                        if st.session_state["userid"] == appointment["patient_id"]:
                            next_doctor = appointment['doctor_id']
                            break
                    if next_doctor:
                        ai_response = f"Your next appointment is with {next_doctor}"
                    else:
                        ai_response = "You have no appointments scheduled"
                    st.session_state["messages"].append(
                        {
                            "role" : "assistant",
                            "content" : ai_response
                        }
                    )
                    time.sleep(2)
                    st.rerun()
            elif user_input == "How do I schedule an appointment":
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {
                            "role" : "user",
                            "content" : user_input
                        }
                    )

                    ai_response = "Look to the sidebar on the left side and select the schedule appointment button. Then select the appointment time you like and Book the appointment!"
                    st.session_state["messages"].append(
                        {
                            "role" : "assistant",
                            "content" : ai_response
                        }
                    )
                    time.sleep(2)
                    st.rerun()
            elif user_input:
                with st.spinner("Thinking..."):
                    st.session_state["messages"].append(
                        {
                            "role" : "user",
                            "content" : user_input
                        }
                    )

                    ai_response = "I couldn't find an answer for it, try again"
                    st.session_state["messages"].append(
                        {
                            "role" : "assistant",
                            "content" : ai_response
                        }
                    )
                    time.sleep(2)
                    st.rerun()


    elif st.session_state['page'] == "patient_appt_view":
        st.set_page_config("Patient Appointment Tracker", layout = "wide", initial_sidebar_state= "expanded")
        st.header("Available Appointments")
        st.divider()
        full_av_appts = []
        for appointment in appointments:
            if appointment['status'] == 'available':
                full_av_appts.append(appointment)
        st.dataframe(full_av_appts, column_order=['status', 'doctor_id', 'date', 'length'])
        if st.button("Schedule Appointment", type="primary", use_container_width=True):
            st.session_state["page"] = "patient_schedule"
            st.rerun()
    elif st.session_state["page"] == "patient_schedule":
        st.set_page_config("Patient Appointment Tracker", layout = "wide", initial_sidebar_state= "expanded")
        st.header("Schedule Appointments")
        st.divider()
        colpat3, colpat4 = st.columns([4,2])
        with colpat3:
            tabpat1, tabpat2 = st.tabs(["Available Appointments", "Your Appointments"])
            with tabpat1:
                with st.container(border=True):
                    #date_search = st.datetime_input("Search by Date and time")
                    full_av_appts = []
                    #time_specific_appts = []
                    #search_appts = None
                    all_appts = None
                    selected_all_appts=None
                    #selected_search_appt= None
                    for appointment in appointments:
                        if appointment['status'] == 'available':
                            full_av_appts.append(appointment)
                            #if appointment['date'] == str(date_search):
                                #time_specific_appts.append(appointment)
                    #if st.button("Search by Date", type="primary", use_container_width= True):
                        #search_appts = st.dataframe(time_specific_appts, column_order=['status', 'doctor_id', 'date', 'length'], on_select="rerun", selection_mode="single-row")
                    else:
                        all_appts = st.dataframe(full_av_appts, column_order=['status', 'doctor_id', 'date', 'length'], on_select="rerun", selection_mode="single-row")
                    if all_appts:
                        if all_appts.selection.rows:
                            all_appts_index = all_appts.selection.rows[0]
                            #Use the index to grab the original dictionary from your list
                            selected_all_appts = full_av_appts[all_appts_index]
                    #elif search_appts:
                        #if search_appts.selection.rows:
                            #search_appt_index = search_appts.selection.rows[0]
                            #selected_search_appt = time_specific_appts[search_appt_index]
            with tabpat2:
                with st.container(border=True):
                    your_appt_df=None
                    selected_your_appt = None
                    your_appts = []
                    for appointment in appointments:
                        if appointment["patient_id"] == st.session_state["userid"]:
                            your_appts.append(appointment)
                    if your_appts == []: 
                        st.error("No Appointments Scheduled")
                    else:
                        your_appt_df = st.dataframe(your_appts, on_select="rerun", column_order=["doctor_id", "status", "date", "length"])
                    if your_appt_df:
                        if your_appt_df.selection.rows:
                            your_appt_index = your_appt_df.selection.rows[0]
                            selected_your_appt = your_appts[your_appt_index]
        with colpat4:
            with st.container(border= True):
                st.markdown("### Appointment Details")
                if selected_all_appts: #or selected_search_appt:
                    with st.container(border= True):
                        st.markdown(f"**Status:** {selected_all_appts['status']}")
                        st.markdown(f"**Date and Time:** {selected_all_appts['date']}")
                        st.markdown(f"**Length:** {selected_all_appts['length']}")
                        st.markdown(f"**Doctor ID:** {selected_all_appts['doctor_id']}")
                        #st.markdown(f"**Excuse Type:** {selected_all_appts['excuse_type']}")
                        #st.markdown(f"**Explanation:** {selected_all_appts['explanation']}")
                        if st.button("Book Appointment", key = "book_appt_btn", type="primary",use_container_width=True):
                            with st.spinner("Booking Appointment..."):
                                for appointment in appointments:
                                    if appointment["appointment_id"] == selected_all_appts["appointment_id"]:
                                        appointment["status"] = "scheduled"
                                        appointment["patient_id"] = st.session_state['userid']
                                        break
                                
                                with open(json_path_appointments,"w") as f :
                                    json.dump(appointments,f)
                            
                            st.success("Appointment Booked.")
                            time.sleep(3)
                            st.rerun()
                elif selected_your_appt:
                    with st.container(border= True):
                        st.markdown(f"**Status:** {selected_your_appt['status']}")
                        st.markdown(f"**Date and Time:** {selected_your_appt['date']}")
                        st.markdown(f"**Length:** {selected_your_appt['length']}")
                        st.markdown(f"**Doctor ID:** {selected_your_appt['doctor_id']}")
                        #st.markdown(f"**Excuse Type:** {selected_all_appts['excuse_type']}")
                        #st.markdown(f"**Explanation:** {selected_all_appts['explanation']}")
                        tabpat3, tabpat4 = st.tabs(["Cancel Appointment","Reschedule Appointment"])
                        with tabpat3:
                            if st.button("Cancel Appointment", key = "cancel_appt_btn", type="primary",use_container_width=True):
                                with st.spinner("Canceling Appointment..."):
                                    for appointment in appointments:
                                        if appointment["appointment_id"] == selected_all_appts["appointment_id"]:
                                            appointment["status"] = "available"
                                            appointment["patient_id"] = None
                                            break
                                    
                                    with open(json_path_appointments,"w") as f :
                                        json.dump(appointments,f)
                                
                                st.success("Appointment Canceled.")
                                time.sleep(3)
                                st.rerun()
                        with tabpat4:
                            reschedule_date = st.datetime_input("Reschedule Appointment")
                            if st.button("Reschedule Appointment", key = "reschedule_appt_btn", type="primary",use_container_width=True):
                                with st.spinner("Rescheduling Appointment..."):
                                    for appointment in appointments:
                                        if appointment["appointment_id"] == selected_all_appts["appointment_id"]:
                                            appointment["status"] = "rescheduled"
                                            appointment["date"] = str(reschedule_date)
                                            break
                                    
                                    with open(json_path_appointments,"w") as f :
                                        json.dump(appointments,f)
                                
                                st.success("Appointment Rescheduled.")
                                time.sleep(3)
                                st.rerun()
                        
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
                    appt_by_date = st.dataframe(found_appointments, column_order=['date', 'length', 'status']) #Remove ID Columns with names and sort by time

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