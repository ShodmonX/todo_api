from dns import resolver
import requests
from typing import Any

from app.config import settings


def check_domain(email: str) -> bool:
    try:
        domain = email.split("@")[1]

        try:
            resolver.resolve(domain, 'MX')
            return True
        except:
            resolver.resolve(domain, 'A')
            return True
        
    except:
        return False


def _send_email(subject: str, text: str, html: str, email_to: str, name_from: str, email_from: str = "noreplay@mail.exchange-rates-api.uz"):
    API_KEY = settings.MAILTRAP_API_TOKEN

    url = "https://send.api.mailtrap.io/api/send"

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload: dict[str, Any] = {
        "from": { "email": email_from, "name": name_from },
        "to": [
            { "email": email_to }
        ],
        "subject": subject,
        "text": text,
        "html": html
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 200:
        return response.json()
    
    return None

def send_verification_email(email: str, verification_url: str):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial; background:#f5f5f5; padding:30px;">
    <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:8px;">
        <h2>Email Verification</h2>
        <p>Iltimos quyidagi tugmani bosib email manzilingizni tasdiqlang.</p>
        <p>
            <a href="{verification_url}" 
            style="padding:10px 20px; background:#2b8cff; color:white; text-decoration:none; border-radius:6px;">
            Verify Email
            </a>
        </p>
    </div>
    </body>
    </html>
    """
    _send_email("Emailni tasdiqlash", "Iltimos quyidagi tugmani bosib email manzilingizni tasdiqlang.", html, email, "ToDo Application")  

def send_reset_password_email(email: str, password_reset_url: str):
    html = f"""
    <!DOCTYPE html>
    <html>
    <body style="font-family: Arial; background:#f5f5f5; padding:30px;">
    <div style="max-width:600px; margin:auto; background:white; padding:20px; border-radius:8px;">
        <h2>Password Reset</h2>
        <p>Parolni qayta tiklash uchun quyidagi tugmadan foydalanishingiz mumkin.</p>
        <p>
            <a href="{password_reset_url}" 
            style="padding:10px 20px; background:#2b8cff; color:white; text-decoration:none; border-radius:6px;">
            Password Reset
            </a>
        </p>
    </div>
    </body>
    </html>
    """
    _send_email("Parolni qayta tiklash", "Parolni qayta tiklash uchun quyidagi tugmadan foydalanishingiz mumkin.", html, email, "ToDo Application")  