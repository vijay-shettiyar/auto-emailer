# 🔐 Gmail SMTP Access Fixes
# ✅ Option 1: Use App Passwords (Recommended)
# Enable 2-Step Verification on the sender's Gmail account:
# https://myaccount.google.com/security

# Create an App Password:
# Go to: https://myaccount.google.com/apppasswords
# Choose: App = Mail, Device = Windows Computer (or anything).
# It will generate a 16-character password.


import smtplib
import json
import os
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Load configuration
with open('config.json', 'r') as f:
    config = json.load(f)

# Extract fields
sender = config['sender_email']
password = config['sender_password']
to = config.get('recipient_email', [])
cc = config.get('cc_email', [])
bcc = config.get('bcc_email', [])
subject = config['subject']
body = config['body']
file_location = config['file_location']
file_names = config['file_name']
log_file = config.get('log')

# Format date as dd-mmm-yy (e.g., 18-May-25)
today = datetime.now().strftime('%d-%b-%y')
subject = config['subject'].replace("{date}", today)
resolved_files = [name.replace("{date}", today) for name in file_names]
all_recipients = to + cc + bcc

# Build email message
msg = MIMEMultipart()
msg['From'] = sender
msg['To'] = ', '.join(to)
msg['Cc'] = ', '.join(cc)
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))

# Attach files
for file_name in resolved_files:
    file_path = os.path.join(file_location, file_name)
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=file_name)
            part['Content-Disposition'] = f'attachment; filename="{file_name}"'
            msg.attach(part)
    else:
        print(f"Warning: File not found - {file_path}")

# Log to file
def log_status(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    entry = f"[{timestamp}] {message}\n"
    print(entry.strip())
    if log_file:
        with open(log_file, 'a') as log:
            log.write(entry)

# Send the email
try:
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, all_recipients, msg.as_string())
        log_status(f"Email sent successfully to: {', '.join(all_recipients)}")
except Exception as e:
    log_status(f"Failed to send email: {str(e)}")
