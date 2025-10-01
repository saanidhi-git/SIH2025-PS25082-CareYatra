import streamlit as st
import app
import cloud_app
# import app3

PAGES = {
    "Insurance Predictor": app,
    "Patient Manager": cloud_app,
    # "Mini Cloud Storage": app3,
}

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", list(PAGES.keys()))

page = PAGES[choice]
page.app()   # each app file must have an `app()` function
