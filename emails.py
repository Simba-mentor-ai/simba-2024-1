import smtplib
import streamlit as st
from email.message import EmailMessage

pwd = st.secrets["EMAILAPPPWD"]

def send_email_gmail(subject, message, destination):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    #This is where you would replace your password with the app password
    server.login('simba.mentor.recovery@gmail.com', pwd)

    msg = EmailMessage()

    message = f'{message}\n'
    msg.set_content(message)
    msg['Subject'] = subject
    msg['From'] = 'simba.mentor.recovery@gmail.com'
    msg['To'] = destination
    server.send_message(msg)
