import os
import logging
from app import app
from flask import render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get email configuration from environment
EMAIL_SERVER = os.environ.get('EMAIL_SERVER', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USERNAME = os.environ.get('EMAIL_USERNAME', '')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', 'noreply@learningplatform.com')

# Use SendGrid if available
USE_SENDGRID = os.environ.get('USE_SENDGRID', 'False').lower() == 'true'
SENDGRID_API_KEY = os.environ.get('SENDGRID_API_KEY', '')

if USE_SENDGRID and SENDGRID_API_KEY:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content

def send_email(to_email, subject, html_content, text_content=None):
    """Send an email using either SMTP or SendGrid"""
    if not text_content:
        # Simple fallback text content
        text_content = "Please view this email in an HTML compatible email client."
    
    try:
        if USE_SENDGRID and SENDGRID_API_KEY:
            return _send_with_sendgrid(to_email, subject, html_content, text_content)
        else:
            return _send_with_smtp(to_email, subject, html_content, text_content)
    except Exception as e:
        logging.error(f"Failed to send email: {str(e)}")
        return False

def _send_with_smtp(to_email, subject, html_content, text_content):
    """Send email using SMTP"""
    if not EMAIL_USERNAME or not EMAIL_PASSWORD:
        logging.warning("Email credentials not set, skipping email")
        return False
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = EMAIL_FROM
    msg['To'] = to_email
    
    # Attach parts
    part1 = MIMEText(text_content, 'plain')
    part2 = MIMEText(html_content, 'html')
    msg.attach(part1)
    msg.attach(part2)
    
    try:
        server = smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USERNAME, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        logging.error(f"SMTP Error: {str(e)}")
        return False

def _send_with_sendgrid(to_email, subject, html_content, text_content):
    """Send email using SendGrid"""
    message = Mail(
        from_email=EMAIL_FROM,
        to_emails=to_email,
        subject=subject,
        html_content=html_content)
    
    try:
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return response.status_code in [200, 201, 202]
    except Exception as e:
        logging.error(f"SendGrid Error: {str(e)}")
        return False

def get_app_url():
    """Get the application's base URL from environment or use a default"""
    base_url = os.environ.get('APP_URL', 'http://localhost:5000')
    return base_url

def send_welcome_email(user):
    """Send a welcome email to new users"""
    base_url = get_app_url()
    html_content = render_template('emails/welcome.html', 
                                username=user.username,
                                base_url=base_url)
    text_content = f"Welcome to the Learning Platform, {user.username}!\n\n" \
                  f"We're excited to have you join us on your learning journey. " \
                  f"Log in to start learning and earning rewards."
    
    return send_email(
        to_email=user.email,
        subject="Welcome to the Learning Platform!",
        html_content=html_content,
        text_content=text_content
    )

def send_streak_reminder(user):
    """Send a reminder to maintain streak"""
    base_url = get_app_url()
    html_content = render_template('emails/streak_reminder.html', 
                                 username=user.username,
                                 streak_days=user.streak_days,
                                 base_url=base_url)
    text_content = f"Hello {user.username},\n\n" \
                  f"Don't break your {user.streak_days}-day streak! " \
                  f"Log in today to continue your learning journey."
    
    return send_email(
        to_email=user.email,
        subject="Don't Break Your Learning Streak! 🔥",
        html_content=html_content,
        text_content=text_content
    )

def send_achievement_notification(user, achievement):
    """Send notification for a new achievement"""
    base_url = get_app_url()
    html_content = render_template('emails/achievement.html', 
                                 username=user.username,
                                 achievement=achievement,
                                 base_url=base_url)
    text_content = f"Congratulations {user.username}!\n\n" \
                  f"You've earned a new achievement: {achievement.name}. " \
                  f"{achievement.description}. This achievement awards you {achievement.xp_reward} XP!"
    
    return send_email(
        to_email=user.email,
        subject=f"New Achievement Unlocked: {achievement.name} 🏆",
        html_content=html_content,
        text_content=text_content
    )
