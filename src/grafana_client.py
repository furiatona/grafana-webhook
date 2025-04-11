import requests
from config import Config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GrafanaClient:
    def __init__(self):
        self.base_url = Config.GRAFANA_URL
        self.datasource_uid = Config.GRAFANA_DATASOURCE_UID
        self.headers = {
            "Authorization": f"Bearer {Config.GRAFANA_API_TOKEN}",
            "Content-Type": "application/json"
        }

    def get_top_processes(self, instance: str):
        payload = {
            "queries": [
                {
                    "refId": "A",
                    "datasource": {
                        "type": "prometheus",
                        "uid": self.datasource_uid
                    },
                    "expr": f'top_processes{{instance="{instance}"}}',
                    "instant": True,
                    "intervalMs": 15000, # Adjust according to prometheus data scrape interval
                    "maxDataPoints": 5
                }
            ],
            "from": "now-30s",
            "to": "now"
        }
        
        try:
            url = f"{self.base_url}/api/ds/query"
            logger.info(f"Querying Grafana URL: {url} with payload: {payload}")
            response = requests.post(
                url,
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Grafana top_processes response for {instance}: {data}")
            return self._parse_processes(data)
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error querying Grafana for {instance}: {e} - Status: {e.response.status_code}")
            return []
        except Exception as e:
            logger.error(f"Error querying Grafana for {instance}: {e}")
            return []

    def _parse_processes(self, data):
        processes = []
        try:
            frames = data.get("results", {}).get("A", {}).get("frames", [])
            for frame in frames[:5]:  # Limit to top 5
                fields = frame.get("schema", {}).get("fields", [])
                labels = next((f.get("labels", {}) for f in fields if f.get("name") == "Value"), {})
                values = frame.get("data", {}).get("values", [[], []])
                cpu_value = values[1][0] if values[1] else 0
                processes.append({
                    "user": labels.get("user", "unknown"),
                    "command": labels.get("command", "unknown"),
                    "cpu": float(cpu_value)
                })
        except Exception as e:
            logger.error(f"Error parsing processes: {e}")
        return processes