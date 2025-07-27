import smtplib, os, logging, secrets
from urllib.parse import urlencode
from email.message import EmailMessage
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from jinja2 import Environment, FileSystemLoader
from core.token import create_secure_token
from models.user import Users, UserApprovalToken
from sqlmodel import Session, select

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

env = Environment(loader=FileSystemLoader("templates"))

SMTP_SERVER = os.getenv("SMTP_SERVER", "localhost")
SMTP_PORT = os.getenv("SMTP_PORT", 587)
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL")

def send_email(session: Session, user: Users):

    admin_users = session.exec(
        select(Users).where(Users.role == "admin")
    ).all()

    admin_emails = [admin.email for admin in admin_users if admin.email]

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)

    approval_token = UserApprovalToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )

    session.add(approval_token)
    session.commit()

    approval_link = f"https://dashboard.tuschkoreit.de/admin/approve/?token={token}"

    template = env.get_template("user_approval_email.html")
    html = template.render(username=user.username, approve_link=approval_link)

    msg = EmailMessage()
    msg["Subject"] = f"User {user.username} awaits approval"
    msg["From"] = FROM_EMAIL
    msg["To"] = ", ".join(admin_emails)
    msg.set_content("Your client doesnt support HTML emails")
    msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
            logger.info(f"Email sent to {ADMIN_EMAIL}")
    except Exception as e:
        logger.error(f"Error sending email to {ADMIN_EMAIL}: {e}", exc_info=True)

def send_approval_email(session: Session, user: Users):
    
    
    
    template = env.get_template("user_approved_email.html")
    html = template.render(username=user.username)

    msg = EmailMessage()
    msg["Subject"] = f"Hey {user.username}, your account has now been approved"
    msg["From"] = FROM_EMAIL
    msg["To"] = user.email
    msg.set_content("Your client doesnt support HTML emails")
    msg.add_alternative(html, subtype='html')

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.set_debuglevel(1)
            server.starttls()
            if SMTP_USERNAME and SMTP_PASSWORD:   
                server.login(SMTP_USERNAME, SMTP_PASSWORD)  
            server.send_message(msg)
            logger.info(f"Approval mail has been sent to {user.email}")
    except Exception as e:
        logger.error(f"Error sending approval email to {user.email}: {e}", exc_info=True)