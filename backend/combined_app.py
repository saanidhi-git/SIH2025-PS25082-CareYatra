# app.py
import streamlit as st
import os
import shutil
from combined import signup, login, init_files, patient_home, doctor_homepage, upload_new_document, view_new_documents, notification,insurance

# Initialize required files/folders
init_files()

# ----------------------------
# Streamlit UI
# ----------------------------
st.set_page_config(page_title="🏥 Healthcare System", layout="centered")
st.title("🏥 Healthcare System")

# Session State
if "user" not in st.session_state:
    st.session_state.user = None
if "user_type" not in st.session_state:
    st.session_state.user_type = None

menu = ["Signup (Patient)", "Signup (Doctor)", "Login (Patient)", "Login (Doctor)", "Exit"]
choice = st.sidebar.selectbox("📌 Menu", menu)

# ----------------------------
# Signup as Patient
# ----------------------------
if choice == "Signup (Patient)":
    st.subheader("🧑‍⚕️ Patient Signup")
    with st.form("patient_signup"):
        uname = st.text_input("ABHA ID")
        pw = st.text_input("Password", type="password")
        name = st.text_input("Name")
        age = st.text_input("Age")
        doctor = st.text_input("Assigned Doctor Username")
        family = st.text_input("Family Contact")
        submitted = st.form_submit_button("Register Patient")
        if submitted:
            msg = signup("patient", uname, pw, name=name, age=age, doctor_assigned=doctor, family_contact=family)
            st.success(msg)

# ----------------------------
# Signup as Doctor
# ----------------------------
elif choice == "Signup (Doctor)":
    st.subheader("👨‍⚕️ Doctor Signup")
    with st.form("doctor_signup"):
        uname = st.text_input("ABHA ID")
        pw = st.text_input("Password", type="password")
        name = st.text_input("Name")
        spec = st.text_input("Specialization")
        submitted = st.form_submit_button("Register Doctor")
        if submitted:
            msg = signup("doctor", uname, pw, name=name, specialization=spec)
            st.success(msg)

# ----------------------------
# Login as Patient
# ----------------------------
elif choice == "Login (Patient)":
    st.subheader("🔑 Patient Login")
    uname = st.text_input("ABHA ID", key="plogin")
    pw = st.text_input("Password", type="password", key="ppass")
    if st.button("Login Patient"):
        user = login("patient", uname, pw)
        if user:
            st.session_state.user = user
            st.session_state.user_type = "patient"
            st.success(f"Welcome {user['name']} 👋")
        else:
            st.error("Invalid login")

# ----------------------------
# Login as Doctor
# ----------------------------
elif choice == "Login (Doctor)":
    st.subheader("🔑 Doctor Login")
    uname = st.text_input("ABHA ID", key="dlogin")
    pw = st.text_input("Password", type="password", key="dpass")
    if st.button("Login Doctor"):
        user = login("doctor", uname, pw)
        if user:
            st.session_state.user = user
            st.session_state.user_type = "doctor"
            st.success(f"Welcome Dr. {user['name']} 👋")
        else:
            st.error("Invalid login")

# ----------------------------
# After Login - Patient Dashboard
# ----------------------------
if st.session_state.user and st.session_state.user_type == "patient":
    st.sidebar.markdown("---")
    st.sidebar.header("🏠 Patient Dashboard")

    action = st.sidebar.radio("Choose Action", [
        "Emergency notify doctor/family",
        "View documents (from doctor)",
        "Upload new document",
        "Insurance Section",
        "Family Account",
        "Notifications",
        "ABHA AI",
        "Logout"
    ])

    if action == "Emergency notify doctor/family":
        st.warning(f"🚨 Notifying Doctor: {st.session_state.user['doctor_assigned']} and Family: {st.session_state.user['family_contact']}")

    elif action == "View documents (from doctor)":
        st.info("📑 Checking doctor-uploaded documents...")
        view_new_documents(st.session_state.user["username"])

    elif action == "Upload new document":
        uploaded = st.file_uploader("Upload PDF/Image", type=["pdf", "jpg", "jpeg", "png"])
        if uploaded:
            save_path = f"documents/patient_uploads/{st.session_state.user['username']}/{uploaded.name}"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded.read())
            st.success(f"✅ File saved as {save_path}")

    elif action == "Insurance Section":
        st.info("Insurance Module Placeholder")

    elif action == "Family Account":
        st.info("Family Account Section Placeholder")

    elif action == "Notifications":
        st.info("Notification Section Placeholder")

    elif action == "ABHA AI":
        st.info("AI Assistant Placeholder")

    elif action == "Logout":
        st.session_state.user = None
        st.session_state.user_type = None
        st.success("👋 Logged out")

# ----------------------------
# Doctor Dashboard
# ----------------------------
if st.session_state.user and st.session_state.user_type == "doctor":
    st.sidebar.markdown("---")
    st.sidebar.header("👨‍⚕️ Doctor Dashboard")

    action = st.sidebar.radio("Choose Action", [
        "View Emergency notify",
        "View patient documents",
        "Upload new document for patient",
        "Insurance Section",
        "Family Account",
        "Notifications",
        "ABHA AI",
        "Logout"
    ])

    if action == "View Emergency notify":
        st.warning("🚨 Emergency Notifications (simulated)")

    elif action == "View patient documents":
        st.info("📑 Viewing uploaded patient documents...")

    elif action == "Upload new document for patient":
        patient_username = st.text_input("Enter Patient Username")
        uploaded = st.file_uploader("Upload PDF/Image for Patient", type=["pdf", "jpg", "jpeg", "png"])
        if uploaded and patient_username:
            save_path = f"documents/doctor_uploads/{patient_username}/{uploaded.name}"
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(uploaded.read())
            st.success(f"✅ File saved as {save_path}")

    elif action == "Insurance Section":
        st.info("Insurance Module Placeholder")

    elif action == "Family Account":
        st.info("Family Account Section Placeholder")

    elif action == "Notifications":
        st.info("Notification Section Placeholder")

    elif action == "ABHA AI":
        st.info("AI Assistant Placeholder")

    elif action == "Logout":
        st.session_state.user = None
        st.session_state.user_type = None
        st.success("👋 Logged out")
