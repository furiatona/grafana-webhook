from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from config import Config
from webhook_handler import WebhookHandler
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
handler = WebhookHandler()
security = HTTPBasic()

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    correct_username = Config.WEBHOOK_USERNAME
    correct_password = Config.WEBHOOK_PASSWORD
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication credentials not configured"
        )
    if (credentials.username != correct_username or 
        credentials.password != correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

@app.post("/api/v1/webhook/grafana")
async def receive_webhook(
    request: Request,
    username: str = Depends(verify_credentials)
):
    logger.info("Webhook request received")
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Failed to parse payload: {e}")
        return {"status": "error", "message": "Invalid payload"}
    
    if Config.is_debug():
        logger.info(f"Received webhook payload: {payload}")
    
    message = handler.process_webhook(payload)
    if message:
        success = handler.slack.send_message(message)
        if not success:
            logger.error("Failed to send to Slack")
            return {"status": "error", "message": "Failed to send to Slack"}
        logger.info("Webhook processed and sent to Slack")
        return {"status": "success", "message": "Processed webhook and sent to Slack"}
    logger.info("No new top processes to send")
    return {"status": "success", "message": "No new data to process"}

@app.get("/api/v1/health")
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5100)