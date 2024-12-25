import streamlit as st
import requests
import json
import os
import smtplib
import hashlib
import mysql.connector
from dotenv import load_dotenv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from utils.cert_utils import generate_certificate
from utils.streamlit_utils import view_certificate
from connection import contract, w3
from utils.streamlit_utils import hide_icons, hide_sidebar, remove_whitespaces

st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
hide_icons()
hide_sidebar()
remove_whitespaces()

load_dotenv()

api_key = os.getenv("PINATA_API_KEY")
api_secret = os.getenv("PINATA_API_SECRET")
db_host = os.getenv("DB_HOST")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")
db_name = os.getenv("DB_NAME")

def connect_db():
    return mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )

def get_student_details(uid):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE uid = %s", (uid,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student

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

def send_email(receiver_email, certificate_id, uid, candidate_name, course_name, ipfs_hash):
    sender_email = "prajwalb0624@gmail.com"
    password = "kkskjfduixmyvbkh"  # Consider using an app password

    certificate_url = f"https://gateway.pinata.cloud/ipfs/{ipfs_hash}"
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Certificate Generation Confirmation"

    body =f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <h1>Certificate Generation Confirmation</h1>
        <p>Congratulations! Here are the details of the generated certificate:</p>
        <p>UID: {uid}</p>
        <p>Name: {candidate_name}</p>
        <p>Course Name: {course_name}</p>
        <p>Certificate ID: {certificate_id}</p>
        <a href="{certificate_url}">View Certificate</a>
    </body>
    </html>
    """
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")

options = ("Generate Certificate", "View Certificates")
selected = st.selectbox("select", options, label_visibility="hidden")

if selected == options[0]:
    form = st.form("Generate-Certificate")
    uid = form.text_input(label="UID")
    submit = form.form_submit_button("Submit")
    
    if submit:
        student = get_student_details(uid)
        
        if student:
            candidate_name = student['name']
            course_name = student['course_name']
            org_name = student['org_name']
            receiver_email = student['email']

            pdf_file_path = f"{uid}'s certificate.pdf"
            institute_logo_path = "../assets/logo.jpg"
            generate_certificate(pdf_file_path, uid, candidate_name, course_name, org_name, institute_logo_path)

            ipfs_hash = upload_to_pinata(pdf_file_path, api_key, api_secret)
            os.remove(pdf_file_path)

            data_to_hash = f"{uid}{candidate_name}{course_name}{org_name}".encode('utf-8')
            certificate_id = hashlib.sha256(data_to_hash).hexdigest()

            contract.functions.generateCertificate(certificate_id, uid, candidate_name, course_name, org_name, ipfs_hash).transact({'from': w3.eth.accounts[0]})
            st.success(f"Certificate successfully generated with Certificate ID: {certificate_id}")
            
            send_email(receiver_email, certificate_id, uid, candidate_name, course_name, ipfs_hash)
        else:
            st.error("Student not found in the database!")

else:
    form = st.form("View-Certificate")
    certificate_id = form.text_input("Enter the Certificate ID")
    submit = form.form_submit_button("Submit")
    if submit:
        try:
            view_certificate(certificate_id)
        except Exception as e:
            st.error("Invalid Certificate ID!")
