import streamlit as st
import requests
import json
import os
import smtplib
from dotenv import load_dotenv
import hashlib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.cert_utils import generate_certificate
from utils.streamlit_utils import view_certificate
from connection import contract, w3
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces
import mysql.connector

# Load environment variables
load_dotenv()
api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

# Streamlit settings
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

# Database connection
def connect_db():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )

def get_student_email(uid):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email FROM students WHERE uid=%s", (uid,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result[0] if result else None

# Pinata Upload Function
def upload_to_pinata(file_path, api_key, api_secret):
    pinata_api_url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {"pinata_api_key": api_key, "pinata_secret_api_key": api_secret}
    try:
        with open(file_path, "rb") as file:
            files = {"file": (file.name, file)}
            response = requests.post(pinata_api_url, headers=headers, files=files)
            result = response.json()
            return result.get("IpfsHash", None)
    except Exception as e:
        print(f"Error uploading to Pinata: {e}")
        return None

# Email Sending
def send_email(certificate_id, uid, candidate_name, course_name, ipfs_hash, receiver_email):
    certificate_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = receiver_email
    message["Subject"] = "Certificate Generation Confirmation"

    body = f"""
    <html>
        <body>
            <p>Dear {candidate_name},</p>
            <p>Your certificate for the <strong>{course_name}</strong> course has been successfully generated.</p>
            <p>Certificate ID: <strong>{certificate_id}</strong></p>
            <p><a href="{certificate_url}">Download Certificate Here</a></p>
            <p>Thank you!</p>
        </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, receiver_email, message.as_string())
        print(f"Email sent successfully to {receiver_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# Streamlit UI
st.title("Certificate Management System")
options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("Choose an option", options)

if selected == options[0]:  # Generate Certificate
    form = st.form("Generate-Certificate")
    uid = form.text_input("UID")
    candidate_name = form.text_input("Name")
    course_name = form.text_input("Course Name")
    org_name = form.text_input("Org Name")
    submit = form.form_submit_button("Generate")

    if submit:
        # Generate Certificate
        pdf_file_path = f"{uid}_certificate.pdf"
        generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name)

        # Upload to Pinata
        ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
        if not ipfs_hash:
            st.error("Failed to upload certificate to IPFS.")
        else:
            os.remove(pdf_file_path)
            certificate_id = hashlib.sha256(f"{uid}{candidate_name}{course_name}{org_name}".encode()).hexdigest()

            # Save to blockchain
            contract.functions.generateCertificate(
                certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash
            ).transact({"from": w3.eth.accounts[0]})

            # Send email
            receiver_email = get_student_email(uid)
            if receiver_email:
                send_email(certificate_id, uid, candidate_name, course_name, ipfs_hash, receiver_email)
                st.success(f"Certificate generated and sent successfully to {receiver_email}")
            else:
                st.error("Email not found for the provided UID.")

elif selected == options[1]:  # View Certificate
    form = st.form("View-Certificate")
    certificate_id = form.text_input("Certificate ID")
    submit = form.form_submit_button("View")

    if submit:
        try:
            view_certificate(certificate_id)
        except Exception as e:
            st.error("Certificate ID not found.")
