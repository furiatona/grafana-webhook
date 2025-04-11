from typing import List, Dict, Any
from grafana_client import GrafanaClient
from slack_client import SlackClient
from config import Config
import logging

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.grafana = GrafanaClient()
        self.slack = SlackClient()
        self.processed_fingerprints = set()  # Track processed alerts

    def process_webhook(self, payload: Dict[str, Any]) -> str:
        should_process = False
        fingerprints = set()
        for alert in payload.get("alerts", []):
            fingerprint = alert.get("fingerprint")
            if fingerprint and fingerprint not in self.processed_fingerprints:
                fingerprints.add(fingerprint)
                should_process = True

        if not should_process and not Config.use_bypass():
            logger.info("No new alerts to process (already handled or no fingerprints)")
            return ""

        if fingerprints:
            self.processed_fingerprints.update(fingerprints)
            logger.info(f"New fingerprints processed: {fingerprints}")

        if Config.use_bypass():
            instances = [Config.BYPASS_INSTANCE] if Config.BYPASS_INSTANCE else []
            nodename = Config.BYPASS_NODENAME or Config.BYPASS_INSTANCE
            logger.info(f"Bypass enabled, querying instance: {instances}, display as: {nodename}")
            alert_data = [(instances[0], nodename, "N/A")] if instances else []
        else:
            alert_data = self._extract_alert_data(payload)
            if not alert_data:
                logger.warning("No valid alerts found in webhook payload")
                return "No instances found in webhook payload"

        message_parts = []
        message_parts.append(f"High Load Notification - {len(alert_data)} Server(s)")
        for instance, nodename, load in alert_data:
            logger.info(f"Querying top processes for instance: {instance}")
            processes = self.grafana.get_top_processes(instance)
            part = f"\n*{nodename}* -- Load: {load}"
            if processes:
                process_lines = [
                    f"user={p['user']}, command={p['command']}, cpu={p['cpu']:.1f}%"
                    for p in processes
                ]
                part += "\n```\n" + "\n".join(process_lines) + "\n```"
            else:
                logger.warning(f"No processes found for instance: {instance}")
            message_parts.append(part)

        final_message = "\n".join(message_parts)
        logger.info(f"Generated Slack message: {final_message}")
        return final_message

    def _extract_alert_data(self, payload: Dict[str, Any]) -> List[tuple[str, str, str]]:
        alert_data = []
        for alert in payload.get("alerts", []):
            labels = alert.get("labels", {})
            instance = labels.get("instance")
            nodename = labels.get("nodename")
            load = alert.get("values", {}).get("B", "N/A")
            if instance and nodename:
                alert_data.append((instance, nodename, load))
            else:
                logger.warning(f"Missing instance or nodename in alert labels: {labels}")
        logger.info(f"Extracted alert data: {[(i, n) for i, n, _ in alert_data]}")
        return alert_data