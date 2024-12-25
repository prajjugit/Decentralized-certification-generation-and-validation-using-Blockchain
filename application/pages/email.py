from plistlib import UID
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from institute import certificate_id,uid,candidate_name,course_name

def send_email():
    sender_email = "prajwalb0624@gmail.com"
    receiver_email = "prajwalfreelance@gmail.com"
    password = "kkskjfduixmyvbkh"  # Consider using an app password

    # Message setup
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "Test Email"

    # Message content
    body = f"Hello, this is the certificate of student with /n UID : {uid} \n and name: {candidate_name}\n course name:{course_name} \n and \n This is your certificate ID : {certificate_id} sent from Python!"
    message.attach(MIMEText(body, "plain"))

    # Sending email
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
        

