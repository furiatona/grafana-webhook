from dotenv import load_dotenv
import os

load_dotenv()

class Config:
    DEBUG = os.getenv("DEBUG", "INFO")
    GRAFANA_URL = os.getenv("GRAFANA_URL")
    GRAFANA_API_TOKEN = os.getenv("GRAFANA_API_TOKEN")
    SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")
    WEBHOOK_USERNAME = os.getenv("WEBHOOK_USERNAME")
    WEBHOOK_PASSWORD = os.getenv("WEBHOOK_PASSWORD")
    BYPASS_INSTANCE = os.getenv("BYPASS_INSTANCE")
    BYPASS_NODENAME = os.getenv("BYPASS_NODENAME")
    GRAFANA_DATASOURCE_UID = os.getenv("GRAFANA_DATASOURCE_UID", "1")
    
    @staticmethod
    def is_debug():
        return Config.DEBUG.lower() == "info"
    @staticmethod
    def use_bypass():
        return bool(Config.BYPASS_INSTANCE or Config.BYPASS_NODENAME)