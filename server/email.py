from email import encoders
from email.mime.base import MIMEBase
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .manager import EMAIL_SENDER, EMAIL_PASSWORD, log, LogType

# Gmail SMTP Server
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587  # Use 465 for SSL

def send_email_with_attachment(to_email, subject, body, file):
    try:
        # Convert DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        file.to_csv(csv_buffer, index=False)
        csv_buffer.seek(0)

        # Create Email
        msg = MIMEMultipart()
        msg["From"] = EMAIL_SENDER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Attach CSV file
        part = MIMEBase("application", "octet-stream")
        part.set_payload(csv_buffer.getvalue().encode())  # Encode CSV to bytes
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=data_report.csv")
        msg.attach(part)

        # Send Email
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure connection
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_SENDER, to_email, msg.as_string())
        server.quit()

        log(LogType.SUCCESS, f"✅ Email with DataFrame CSV sent to {to_email}")

    except Exception as e:
        log(LogType.ERROR, f"❌ Error sending email: {e}")

# Example Usage
# send_email_with_attachment("recipient@gmail.com", "Test Subject", "Hello, this is a test email!")
