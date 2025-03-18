import streamlit as st
import pandas as pd
import qrcode
import io
import yagmail
import os
from datetime import datetime

# --- SETUP ---
DEFAULT_ADMIN = "Admin"
DEFAULT_PASSWORD = "123"
ATTENDEES_FILE = "attendees.csv"

def authenticate():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    if 'username' not in st.session_state:
        st.session_state['username'] = ""

    st.session_state['username'] = st.text_input("Username", value=st.session_state['username'])
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if st.session_state['username'] == DEFAULT_ADMIN and password == DEFAULT_PASSWORD:
            st.session_state['authenticated'] = True
        else:
            st.error("Invalid Credentials")

def load_attendees():
    if os.path.exists(ATTENDEES_FILE):
        return pd.read_csv(ATTENDEES_FILE)
    return pd.DataFrame(columns=["Name", "ID", "Phone", "Email", "QR Code", "Attended", "Time Entered"])

def save_attendees(df):
    df.to_csv(ATTENDEES_FILE, index=False)

def generate_qr_code(text):
    qr = qrcode.make(text)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    return buffer.getvalue()

def send_email(email, qr_code):
    yag = yagmail.SMTP("your-email@gmail.com", "your-password")
    yag.send(to=email, subject="Your Event QR Code", contents="Scan this QR code at the event.", attachments=qr_code)

def main():
    if 'authenticated' not in st.session_state:
        authenticate()
    if not st.session_state['authenticated']:
        return
    
    st.title("Admin Dashboard")
    attendees = load_attendees()
    
    uploaded_file = st.file_uploader("Upload Attendees CSV", type=["csv"])
    if uploaded_file:
        attendees = pd.read_csv(uploaded_file)
        attendees["QR Code"] = attendees["ID"].apply(lambda x: generate_qr_code(str(x)))
        save_attendees(attendees)
        st.success("Attendees uploaded & QR Codes generated!")
    
    st.write("### Attendee Records")
    st.dataframe(attendees)
    
    search_id = st.text_input("Search Attendee by ID")
    if search_id:
        result = attendees[attendees["ID"].astype(str) == search_id]
        st.write(result)
        
        if not result.empty:
            if st.button("Mark as Attended"):
                attendees.loc[attendees["ID"].astype(str) == search_id, "Attended"] = "Yes"
                attendees.loc[attendees["ID"].astype(str) == search_id, "Time Entered"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_attendees(attendees)
                st.success("Attendee marked as attended!")
    
    if st.button("Download Report"):
        attendees.to_csv("attendance_report.csv", index=False)
        st.download_button(label="Download Report", data=open("attendance_report.csv", "rb").read(), file_name="attendance_report.csv", mime="text/csv")
    
if __name__ == "__main__":
    main()
