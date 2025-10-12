# utils/mnotify_sms.py
import requests
from django.conf import settings

def send_sms_via_mnotify(recipients, message, sms_type=None):
    """
    Send SMS using mNotify API.
    recipients: list of phone numbers as strings
    message: message text
    sms_type: optional, e.g. 'otp' if sending OTP messages
    """
    api_key = settings.MNOTIFY_API_KEY
    url = f"{settings.MNOTIFY_URL}?key={api_key}"

    data = {
        "recipient": recipients,
        "sender": settings.MNOTIFY_SENDER_ID,
        "message": message,
        "is_schedule": False,
        "schedule_date": "",
    }

    # Only include sms_type if it's specified (per mNotify docs)
    if sms_type:
        data["sms_type"] = sms_type

    try:
        response = requests.post(url, json=data)
        result = response.json()
        print("mNotify response:", result)
        return result
    except Exception as e:
        print("Error sending SMS:", e)
        return None
