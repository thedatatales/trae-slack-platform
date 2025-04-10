from fastapi import FastAPI, Request
from src.integrations.slack.client import SlackClient
from src.integrations.slack.listener import SlackEventListener
import logging

logger = logging.getLogger(__name__)

app = FastAPI()
client = SlackClient()
listener = SlackEventListener(client)

@app.get("/")
async def root():
    return {"message": "Trae Slack Platform API is running"}

@app.post("/slack/events")
async def slack_events(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received Slack event: {body}")
        response = await listener.handler.handle(request)
        logger.info(f"Handler response: {response}")
        return response
    except Exception as e:
        logger.error(f"Error in slack_events: {str(e)}")
        logger.exception(e)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080, reload=True)