import streamlit as st
from db.firebase_app import register
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

background_image_path = "../assets/regi.jpg" 
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

st.title("Register")

form = st.form("login")
email = form.text_input("Enter your email")
password = form.text_input("Enter your password", type="password")
clicked_login = st.button("Already registered? Click here to login!")

if clicked_login:
    switch_page("login")
    
submit = form.form_submit_button("Register")
if submit:
    result = register(email, password)
    if result == "success":
        st.success("Registration successful!")
        if st.session_state.profile == "Institute":
            switch_page("institute")
        else:
            switch_page("verifier")
    else:
        st.error("Registration unsuccessful!")