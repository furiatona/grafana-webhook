import requests
from config import Config

class SlackClient:
    def __init__(self):
        self.webhook_url = Config.SLACK_WEBHOOK_URL

    def send_message(self, message: str):
        payload = {
            "text": message,
            "mrkdwn": True
        }
        try:
            response = requests.post(self.webhook_url, json=payload)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending to Slack: {e}")
            return False