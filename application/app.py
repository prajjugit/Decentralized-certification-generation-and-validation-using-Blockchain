import streamlit as st
from PIL import Image
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
from streamlit_extras.switch_page_button import switch_page
import base64

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()


def load_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

background_image_path = "../assets/blockchain.png" #
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

    header{{
    visibility:hidden;
    }}
     
</style>
"""

# Apply the CSS
st.markdown(background_image_css, unsafe_allow_html=True)

st.title("Decentralised Certificate Generation and Validation System Through Blockchain")

st.subheader("Select Your Role")

col1, col2 = st.columns(2)
institite_logo = Image.open("../assets/institute_logo1.png")
with col1:
    st.image(institite_logo, output_format="jpg", width=230)


    clicked_institute = st.button("Institute")

company_logo = Image.open("../assets/company_logo1.jpg")
with col2:
    st.image(company_logo, output_format="jpg", width=220)
    clicked_verifier = st.button("Verifier")

if clicked_institute:
    st.session_state.profile = "Institute"
    switch_page('login')
elif clicked_verifier:
    st.session_state.profile = "Verifier"
    switch_page('login')
