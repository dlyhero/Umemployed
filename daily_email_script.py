import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'billleynyuy@gmail.com'
EMAIL_PASSWORD = 'hlvr rkdd irly osnl'

# List of recipient email addresses
recipients = [
    'nyuydinecedric@gmail.com',
    'billleynyuy@gmail.com',
    'brandipearl123@gmail.com'
]

def send_daily_report():
    for recipient in recipients:
        # Create the email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = recipient
        msg['Subject'] = 'Daily Report - ' + datetime.now().strftime('%Y-%m-%d')

        # Email body
        body = f'Hello from UmEmployed, this is your daily report, sent to {recipient}.'
        msg.attach(MIMEText(body, 'plain'))

        # Send the email
        try:
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(EMAIL_ADDRESS, recipient, text)
            server.quit()
            print(f'Email sent successfully to {recipient}')
        except Exception as e:
            print(f'Failed to send email to {recipient}: {e}')

if __name__ == '__main__':
    send_daily_report()

# added crontab email automation
