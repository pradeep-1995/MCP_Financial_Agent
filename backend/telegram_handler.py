import requests
from config import BASE_TELEGRAM_URL

def send_msg(chat_id: int, text: str, parse_mode="Markdown"):
    """Send a message to a Telegram chat"""
    url = f"{BASE_TELEGRAM_URL}/sendMessage"
    payload = {
        "chat_id": chat_id, 
        "text": text, 
        "parse_mode": parse_mode
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Telegram send error: {e}")
        return None

def set_webhook(webhook_url: str):
    """Set the Telegram webhook"""
    url = f"{BASE_TELEGRAM_URL}/setWebhook"
    payload = {"url": webhook_url}
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Webhook setup error: {e}")
        return None

def get_webhook_info():
    """Get current webhook information"""
    url = f"{BASE_TELEGRAM_URL}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        return response.json()
    except Exception as e:
        print(f"Get webhook info error: {e}")
        return None
