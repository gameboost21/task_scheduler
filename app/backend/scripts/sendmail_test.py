from email import message
from email.message import EmailMessage
import smtplib

msg = EmailMessage()
msg["Subject"] = "Test"
msg["From"] = "admin@tuschkoreit.de"
msg["To"] = "tom@tuschkoreit.de"
msg.set_content("Hello from Python")

with smtplib.SMTP("my.tuschkoreit.de", 587) as server:
    server.starttls()
    server.login("admin@tuschkoreit.de", "your-password")
    server.send_message(msg)
