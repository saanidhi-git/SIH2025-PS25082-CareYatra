import streamlit as st
import os

def app():
    # Folder to store uploaded files
    UPLOAD_FOLDER = "uploads"
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    st.title("☁️ Mini Cloud Storage")

    # --- Upload Section ---
    st.header("📤 Upload a File")
    uploaded_file = st.file_uploader("Choose a file", type=None)

    if uploaded_file is not None:
        filepath = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
        with open(filepath, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File uploaded and saved at: {filepath}")

    # --- Download Section ---
    st.header("📥 Download Files")

    files = os.listdir(UPLOAD_FOLDER)
    if files:
        for file in files:
            filepath = os.path.join(UPLOAD_FOLDER, file)
            with open(filepath, "rb") as f:
                st.download_button(
                    label=f"⬇️ Download {file}",
                    data=f,
                    file_name=file
                )
    else:
        st.info("No files available for download yet.")
