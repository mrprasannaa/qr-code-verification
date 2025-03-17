import streamlit as st
import pandas as pd
import qrcode
import os
from io import BytesIO
from PIL import Image
import base64

data_file = "attendees.csv"
qr_folder = "qrcodes"

# Ensure the folder exists
if not os.path.exists(qr_folder):
    os.makedirs(qr_folder)

def generate_qr_code(data):
    qr = qrcode.make(data)
    buffered = BytesIO()
    qr.save(buffered, format="PNG")
    return buffered.getvalue()

def save_attendees(file):
    df = pd.read_csv(file)
    df.to_csv(data_file, index=False)
    return df

def generate_qr_for_attendees(df):
    for _, row in df.iterrows():
        qr_data = f"{row['ID']}|{row['Name']}|{row['Phone']}"
        qr_code = generate_qr_code(qr_data)
        file_path = os.path.join(qr_folder, f"{row['ID']}.png")
        with open(file_path, "wb") as f:
            f.write(qr_code)

def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

st.title("QR Code Event Verification")

menu = ["Upload Attendees", "Generate QR Codes", "Scan & Verify"]
choice = st.sidebar.selectbox("Select Option", menu)

if choice == "Upload Attendees":
    uploaded_file = st.file_uploader("Upload CSV file with ID, Name, Phone", type=["csv"])
    if uploaded_file:
        df = save_attendees(uploaded_file)
        st.dataframe(df)
        st.success("Attendees uploaded successfully!")

elif choice == "Generate QR Codes":
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        generate_qr_for_attendees(df)
        st.success("QR Codes generated!")
        for _, row in df.iterrows():
            img_path = os.path.join(qr_folder, f"{row['ID']}.png")
            st.image(img_path, caption=f"{row['Name']}", width=150)
    else:
        st.error("Please upload attendees first.")

elif choice == "Scan & Verify":
    st.write("Use a QR scanner app to scan and verify manually.")
    if os.path.exists(data_file):
        df = pd.read_csv(data_file)
        st.dataframe(df)
    else:
        st.error("No attendee data found.")
