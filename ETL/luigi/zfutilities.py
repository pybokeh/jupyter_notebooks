import os.path as op
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email import encoders
from win10toast import ToastNotifier

def sendEmail(sender: str, pwd: str, to, subject: str, message: str, files: list):
    recipient = to if type(to) is list else [to]
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(recipient)
    msg.attach(MIMEText(message))
    
    for path in files:
        part = MIMEBase('application', "octet-stream")
        with open(path, 'rb') as file:
            part.set_payload(file.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(op.basename(path)))
        msg.attach(part)
    
    server = smtplib.SMTP('smtp.office365.com:587')
    server.ehlo()
    server.starttls()

    try:
        server.login(sender, pwd)
        print('Successfully authenticated...')
    except smtplib.SMTPAuthenticationError:               # Check for authentication error
        return " Authentication ERROR"

    try:
        server.sendmail(sender, recipient, msg.as_string())
        print('Email sent!')
    except smtplib.SMTPRecipientsRefused:                # Check if recipient's email was accepted by the server
        return "ERROR"
    server.quit()

def sendWin10Notification(message: str):
    toaster = ToastNotifier()
    toaster.show_toast("ZF Vouchering Process Status:", message, icon_path=None, duration=10)