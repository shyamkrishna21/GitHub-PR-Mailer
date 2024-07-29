import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

class EmailService:
    def __init__(self, sender, to, email_username, password, server, email_use_tls, port, cc=None, bcc=None) -> None:
        self.sender = sender
        self.to = to if isinstance(to, list) else [to]
        self.cc = cc if cc else []
        self.bcc = bcc if bcc else []
        self.email_username = email_username
        self.password = password
        self.server = server
        self.email_use_tls = email_use_tls
        self.port = port

    def send_email(self, report):
        msg = MIMEMultipart()
        msg['From'] = self.sender
        msg['To'] = ", ".join(self.to)
        if self.cc:
            msg['Cc'] = ", ".join(self.cc)
        msg['Subject'] = 'Weekly GitHub Pull Request Summary'

        msg.attach(MIMEText(report, 'html'))

        # Attach Excel files
        for filename in os.listdir('.'):
            if filename.startswith('pull_requests_summary_') and filename.endswith('.xlsx'):
                try:
                    with open(filename, 'rb') as attachment:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(attachment.read())
                        encoders.encode_base64(part)
                        part.add_header('Content-Disposition', f'attachment; filename={filename}')
                        msg.attach(part)
                except Exception as e:
                    print(f"Failed to attach file {filename}: {e}")

        recipients = self.to + self.cc + self.bcc

        try:
            server = smtplib.SMTP(self.server, self.port)
            if self.email_use_tls:
                server.starttls()
            server.login(self.email_username, self.password)
            server.sendmail(self.sender, recipients, msg.as_string())
            server.close()
            print(f"FROM: {msg['From']}")
            print(f"To: {msg['To']}")
            if self.cc:
                print(f"Cc: {msg['Cc']}")
            if self.bcc:
                print(f"Bcc: {', '.join(self.bcc)}")
            print(f"Subject: {msg['Subject']}")
            print("Email sent successfully.")
        except Exception as e:
            print(f"Failed to send email: {e}")
