from typing import List, Dict, Any
from grafana_client import GrafanaClient
from slack_client import SlackClient
from config import Config
import logging
from time import time

logger = logging.getLogger(__name__)

class WebhookHandler:
    def __init__(self):
        self.grafana = GrafanaClient()
        self.slack = SlackClient()
        self.last_sent = {}  # Track last notification time per fingerprint

    def process_webhook(self, payload: Dict[str, Any]) -> str:
        logger.info(f"Received webhook payload: {payload}")

        # Handle test notifications
        if not payload.get("alerts") and "receiver" in payload:
            logger.info("Detected test notification")
            return "Webhook connection test successful"

        # Extract alert data and rate-limit
        alert_data = self._extract_alert_data(payload)
        current_time = time()
        filtered_data = []
        for instance, nodename, load in alert_data:
            fingerprint = next(
                (a.get("fingerprint") for a in payload.get("alerts", [])
                 if a.get("labels", {}).get("instance") == instance), ""
            )
            if fingerprint and (fingerprint not in self.last_sent or
                              current_time - self.last_sent[fingerprint] > 600):
                filtered_data.append((instance, nodename, load))
                self.last_sent[fingerprint] = current_time

        if not filtered_data:
            logger.info("No new alerts to process (rate-limited or no valid data)")
            return ""

        # Apply bypass if enabled
        if Config.use_bypass():
            instances = [Config.BYPASS_INSTANCE] if Config.BYPASS_INSTANCE else []
            nodename = Config.BYPASS_NODENAME or Config.BYPASS_INSTANCE
            logger.info(f"Bypass enabled, querying instance: {instances}, display as: {nodename}")
            filtered_data = [(instances[0], nodename, "N/A")] if instances else filtered_data

        message_parts = []
        message_parts.append(f"High Load Notification - {len(filtered_data)} Server(s)")
        for instance, nodename, load in filtered_data:
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
        seen_fingerprints = set()
        for alert in payload.get("alerts", []):
            if not isinstance(alert, dict):
                logger.warning(f"Invalid alert format: {alert}")
                continue
            fingerprint = alert.get("fingerprint")
            if fingerprint in seen_fingerprints:
                continue  # Deduplicate within payload
            seen_fingerprints.add(fingerprint)
            labels = alert.get("labels") or {}
            instance = labels.get("instance")
            nodename = labels.get("nodename")
            load = alert.get("values", {}).get("B", "N/A")
            if instance and nodename:
                alert_data.append((instance, nodename, load))
            else:
                logger.warning(f"Missing instance or nodename in alert labels: {labels}")
        logger.info(f"Extracted alert data: {[(i, n) for i, n, _ in alert_data]}")
        return alert_data