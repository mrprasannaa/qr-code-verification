import streamlit as st
import pandas as pd
import qrcode
import os
from io import BytesIO
from PIL import Image
import base64
import smtplib
import requests
from datetime import datetime

data_file = "attendees.csv"
qr_folder = "qrcodes"

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    return buffered.getvalue()

def save_attendees(file):
    df = pd.read_csv(file)
    df["QR_Code"] = ""
    df.to_csv(data_file, index=False)
    return df

def generate_qr_for_attendees(df):
    for index, row in df.iterrows():
        qr_data = f"{row['ID']}|{row['Name']}|{row['Phone']}"
        qr_code = generate_qr_code(qr_data)
        file_path = os.path.join(qr_folder, f"{row['ID']}.png")
        with open(file_path, "wb") as f:
            f.write(qr_code)
        df.at[index, "QR_Code"] = file_path
    df.to_csv(data_file, index=False)

def send_email(receiver_email, subject, body, qr_path):
    sender_email = "your-email@example.com"
    sender_password = "your-password"
    with open(qr_path, "rb") as f:
        qr_data = f.read()
    msg = f"Subject: {subject}\n\n{body}"
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg)

def send_whatsapp(phone, message, qr_path):
    url = "https://api.twilio.com/YOUR_TWILIO_API_URL"
    files = {"media": open(qr_path, "rb")}
    data = {"To": phone, "From": "YOUR_TWILIO_NUMBER", "Body": message}
    requests.post(url, data=data, files=files)

def verify_attendee(qr_data):
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        for index, row in df.iterrows():
            stored_qr = f"{row['ID']}|{row['Name']}|{row['Phone']}"
            if stored_qr == qr_data:
                df.at[index, "Verified_Time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                df.to_csv(data_file, index=False)
                return True, row["Name"]
    return False, None

st.title("QR Code Event Verification")
menu = ["Upload Attendees", "Generate QR Codes & Send", "Scan & Verify"]
choice = st.sidebar.selectbox("Select Option", menu)

if choice == "Upload Attendees":
    uploaded_file = st.file_uplo
