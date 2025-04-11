# Grafana Webhook Processor

Python application that processes Grafana webhooks, queries Grafana for top processes data, and sends formatted messages to a Slack channel. It can be run locally using a virtual environment or deployed as a Docker container.

## Features
- Receives webhooks from Grafana at `/api/v1/webhook/grafana`
- Extracts instance/hostnames from webhook payloads
- Queries Grafana for top 5 processes per instance
- Sends formatted messages to Slack
- Supports debug mode to view raw webhook payloads
- Containerized with Docker Compose
- Local development with virtual environment

## Prerequisites
- Python 3.9+
- Docker and Docker Compose (for containerized deployment)
- Grafana instance with API access
- Slack webhook URL

## Project Structure
```
grafana-webhook/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
├── .env
├── .gitignore
├── setup_venv.sh
├── src/
│   ├── config.py
│   ├── main.py
│   ├── webhook_handler.py
│   ├── grafana_client.py
│   ├── slack_client.py
└── README.md
```
## Setup

### 1. Configure Environment Variables
Create a `.env` file in the root directory with the following:
```
DEBUG=INFO
GRAFANA_URL=https://example-grafana.com
GRAFANA_DATASOURCE_UID=xxyyyzzz
GRAFANA_API_TOKEN="xxxzzz"
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/yyy/zzz
WEBHOOK_USERNAME=xxx
WEBHOOK_PASSWORD=yyy
# BYPASS_INSTANCE=103.244.115.122:9100 # For testing
# BYPASS_NODENAME=sg1000dnsiaas.com # For testing
```
Replace values with your actual Grafana URL, API token, and Slack webhook URL.

### 2. Local Development (Virtual Environment)
1. **Setup Virtual Environment:**
   ```bash
   chmod +x setup_venv.sh
   ./setup_venv.sh
   source venv/bin/activate
   ```
2. **Run the Application:**
   ```bash
   python src/main.py
   Access the webhook endpoint at http://localhost:5100/api/v1/webhook/grafana
   Deactivate:
   bash
   deactivate
   ```
### 3. Containerized Deployment (Docker)
Build and Run:
```bash
docker-compose up --build
The application runs on port 5100 (e.g., http://<docker-host>:5100/api/v1/webhook/grafana)
```
Stop:
```bash
docker-compose down
```

## 4. Grafana Configuration
1. In Grafana: Alerting > Contact Points
2. Create a Webhook contact point
3. Set URL to: http://<host>:5100/api/v1/webhook/grafana, fill basic username and password
4. Test and save
5. Output on Slack
   ```
   High Load Processes Notification
   server1.example.com top 5 processes
   user=xxx, command=xxx, cpu=xx%
   user=yyy, command=yyy, cpu=zz%
   ```

## Contributing
Feel free to submit issues or pull requests for improvements!

## License
MIT License