import streamlit as st
import os
import hashlib
from utils.cert_utils import extract_certificate
from utils.streamlit_utils import view_certificate
from connection import contract
from utils.streamlit_utils import displayPDF, hide_icons, hide_sidebar, remove_whitespaces
import base64

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

def load_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

background_image_path = "../assets/veri.jpg" #
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


st.title("Verifier Page")
options = ("Verify Certificate using PDF", "View/Verify Certificate using Certificate ID")
selected = st.selectbox("hi", options, label_visibility="hidden")

if selected == options[0]:
    uploaded_file = st.file_uploader("Upload the PDF version of the certificate")
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        with open("certificate.pdf", "wb") as file:
            file.write(bytes_data)
        
        # Status container for validation
        with st.status("Validating the certificate...", expanded=True) as status:
            try:
                (uid, candidate_name, course_name, org_name) = extract_certificate("certificate.pdf")
                displayPDF("certificate.pdf")
                os.remove("certificate.pdf")

                # Calculating hash
                data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
                certificate_id = hashlib.sha256(data_to_hash).hexdigest()

                # Smart Contract Call
                result = contract.functions.isVerified(certificate_id).call()
                if result:
                    st.success("Certificate validated successfully!")
                    status.update(label="Certificate validation successful!", state="complete")
                else:
                    st.error("Invalid Certificate! Certificate might be tampered.")
                    status.update(label="Validation failed: Invalid certificate.", state="error")
            except Exception as e:
                st.error("Error: Invalid Certificate! Certificate might be tampered.")
                status.update(label="An error occurred during validation.", state="error")

elif selected == options[1]:
    form = st.form("Validate-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Validate")
    if submit:
        # Status container for ID validation
        with st.status("Validating the Certificate ID...", expanded=True) as status:
            try:
                view_certificate(certificate_id)
                # Smart Contract Call
                result = contract.functions.isVerified(certificate_id).call()
                if result:
                    st.success("Certificate validated successfully!")
                    status.update(label="Certificate ID validation successful!", state="complete")
                else:
                    st.error("Invalid Certificate ID!")
                    status.update(label="Validation failed: Invalid Certificate ID.", state="error")
            except Exception as e:
                st.error("Error: Invalid Certificate ID!")
                status.update(label="An error occurred during validation.", state="error")
