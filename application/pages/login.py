import streamlit as st
from db.firebase_app import login
from dotenv import load_dotenv
import os
from streamlit_extras.switch_page_button import switch_page
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
import base64

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

def load_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

background_image_path = "../assets/glass.jpg" #
base64_image = load_image_as_base64(background_image_path)

background_image_css = f"""
<style>
    /* Apply to entire Streamlit App, including header */
    .stApp {{
        background-image: url("data:image/jpg;base64,{base64_image}");
        background-size: cover;
        background-repeat: no-repeat;
        background-position: center;
        background-attachment: fixed;
    }}
    /* Hide Streamlit's default header and menu bar */
    header {{
        visibility: hidden;
    }}
</style>
"""
# Apply the CSS
st.markdown(background_image_css, unsafe_allow_html=True)


load_dotenv()
st.title("Login")
form = st.form("login")
email = form.text_input("Enter your email")
password = form.text_input("Enter your password", type="password")

if st.session_state.profile != "Institute":
    clicked_register = st.button("New user? Click here to register!")

    if clicked_register:
        switch_page("register")

submit = form.form_submit_button("Login")
if submit:
    if st.session_state.profile == "Institute":
        valid_email = os.getenv("institute_email")
        valid_pass = os.getenv("institute_password")
        
        if email == valid_email and password == valid_pass:
            switch_page("institute")
        else:
            print(valid_email)
            print(valid_pass)
            st.error("Invalid credentials!")
    else:
        result = login(email, password)
        if result == "success":
            st.success("Login successful!")
            switch_page("verifier")
        else:
            st.error("Invalid credentials!")
        