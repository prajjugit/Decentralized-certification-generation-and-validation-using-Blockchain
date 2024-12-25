import streamlit as st
import hashlib
import os
import requests
import json
import smtplib
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.cert_utils import generate_certificate
from utils.streamlit_utils import view_certificate
from connection import contract, w3
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
import base64

st.set_page_config(
    layout="centered", 
    initial_sidebar_state="collapsed",
    page_title="Institute",
    page_icon="💰",
)

hide_icons()
hide_sidebar()
remove_whitespaces()

def load_image_as_base64(file_path):
    with open(file_path, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
    return encoded_image

background_image_path = "../assets/cert.png" #
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

api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")

def upload_to_pinata(file_path, api_key, api_secret):
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": api_key,
        "pinata_secret_api_key": api_secret,
    }
    with open(file_path, "rb") as file:
        files = {"file": (file.name, file)}
        response = requests.post(pinata_api_url, headers=headers, files=files)
        result = json.loads(response.text)
        if "IpfsHash" in result:
            ipfs_hash = result["IpfsHash"]
            print(f"File uploaded to Pinata. IPFS Hash: {ipfs_hash}")
            return ipfs_hash
        else:
            print(f"Error uploading to Pinata: {result.get('error', 'Unknown error')}")
            return None

def send_email(certificate_id, uid, candidate_name, course_name, ipfs_hash):
    sender_email = "prajwalb0624@gmail.com"
    receiver_email = email
    password = "kkskjfduixmyvbkh"  # Consider using an app password

    # Construct the IPFS link
    certificate_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Certificate Generation Confirmation"

    body =f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <div style="text-align: center; padding: 10px; background-color: #4CAF50; color: white;">
        <h1>Certificate Generation Confirmation</h1>
    </div>
    <div style="padding: 20px; margin: auto; max-width: 600px;">
        <h2>Hello,</h2>
        <p>Congratulations! Here are the details of the generated certificate:</p>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <th style="text-align: left; padding: 8px; background-color: #f2f2f2;">Detail</th>
                <th style="text-align: left; padding: 8px; background-color: #f2f2f2;">Information</th>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">UID</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{uid}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Name</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{candidate_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Course Name</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{course_name}</td>
            </tr>
            <tr>
                <td style="padding: 8px; border: 1px solid #ddd;">Certificate ID</td>
                <td style="padding: 8px; border: 1px solid #ddd;">{certificate_id}</td>
            </tr>
        </table>
        <p style="text-align: center;">
            <a href="{certificate_url}" style="display: inline-block; padding: 10px 20px; margin-top: 20px; font-size: 18px; color: white; background-color: #4CAF50; text-decoration: none; border-radius: 5px;">
                Download Certificate :)
            </a>
        </p>
        <p style="font-size: 14px; color: #777;">Thank you for using our service!</p>
    </div>
</body>
</html>
"""

    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print(f"Email sent successfully to {email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

st.title("Certificate Section")

options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("select", options, label_visibility="hidden")

if selected == options[0]:
    form = st.form("Generate-Certificate")
    uid = form.text_input(label="UID")
    candidate_name = form.text_input(label="Name")
    course_name = form.text_input(label="Course Name")
    org_name = form.text_input(label="Org Name")
    email=form.text_input(label="Email")

    submit = form.form_submit_button("Submit")

    if submit:
        progress_bar = st.progress(0)  # Initialize progress bar
        status_text = st.empty()       # Empty text for task updates
        
        with st.spinner("Processing..."):
            with st.container():
                # Step 3: Generate Certificate ID
                status_text.text("Generating certificate ID...")
                progress_bar.progress(10)
                data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
                certificate_id = hashlib.sha256(data_to_hash).hexdigest()

                # Step 1: Generate Certificate
                status_text.text("Generating the certificate...")
                progress_bar.progress(30)
                pdf_file_path = f"{uid}'s certificate.pdf"
                institute_logo_path = "../assets/institute_logo1.png"
                generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_path)

                # Step 2: Upload to IPFS
                status_text.text("Uploading certificate to IPFS...")
                progress_bar.progress(50)
                ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
                os.remove(pdf_file_path)

                # Step 4: Save on Blockchain
                status_text.text("Recording certificate on the blockchain...")
                progress_bar.progress(70)
                contract.functions.generateCertificate(certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash).transact({'from': w3.eth.accounts[0]})

                # Step 5: Send Email Confirmation
                status_text.text(f"Sending email with certificate details to {email}")
                progress_bar.progress(90)
                send_email(certificate_id, uid, candidate_name, course_name, ipfs_hash)

        progress_bar.progress(100)
        status_text.text("Certificate generation process completed successfully!")
        st.success(f"Certificate successfully generated with Certificate ID: {certificate_id}")

else:
    form = st.form("View-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Submit")
    if submit:
        try:
            view_certificate(certificate_id)
        except Exception as e:
            st.error("Invalid Certificate ID!")
