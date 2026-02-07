import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import settings
from twilio.rest import Client

def send_crisis_email(user_name: str, content: str):
    if not settings.leader_emails:
        return

    subject = "🔴 JoyBucket Alert: Urgent Entry Detected"
    body = f"""
    Urgent entry logged by {user_name}.
    
    Content:
    "{content}"
    
    Please check the Admin Dashboard immediately.
    """
    
    message = MIMEMultipart()
    message["From"] = settings.smtp_login
    message["To"] = settings.leader_emails
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))
    
    try:
        with smtplib.SMTP("smtp-relay.brevo.com", 587) as server:
            server.starttls()
            server.login(settings.smtp_login, settings.smtp_password)
            server.send_message(message)
    except Exception as e:
        print(f"Email Error: {e}")

def send_crisis_sms(user_name: str):
    if not settings.enable_sms or not settings.leader_phones:
        return

    # Assuming TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are in environment/settings
    # For now, placeholder for Twilio integration
    # client = Client(settings.twilio_sid, settings.twilio_token)
    # try:
    #     client.messages.create(
    #         body=f"URGENT JoyBucket: Crisis entry from {user_name}. Check dashboard.",
    #         from_=settings.twilio_number,
    #         to=settings.leader_phones
    #     )
    # except Exception as e:
    #     print(f"SMS Error: {e}")
    print(f"SMS Alert Triggered for {user_name}") # Placeholder
