from .client import SlackClient
from .router import SlackRouter
from slack_bolt.adapter.fastapi import SlackRequestHandler
import logging

logger = logging.getLogger(__name__)

class SlackEventListener:
    def __init__(self, client: SlackClient):
        self.client = client
        self.router = SlackRouter()
        self.handler = SlackRequestHandler(self.client.app)
        self._register_handlers()
    
    def _register_handlers(self):
        @self.client.app.event("message")
        def handle_message(body, say):
            try:
                event = body["event"]
                if "bot_id" in event:
                    logger.info("Skipping bot message")
                    return
                
                logger.info(f"Processing user message: {event}")
                user = event.get("user", "there")
                if "@Dasham" in event.get("text", ""):
                    say(text=f"Hi <@{user}>! How can I help you today?")
                    logger.info(f"Response sent to user {user}")
            except Exception as e:
                logger.error(f"Message handler error: {str(e)}")

        @self.client.app.event("app_mention")
        def handle_mention(body, say):
            try:
                event = body["event"]
                if "bot_id" in event:
                    logger.info("Skipping bot mention")
                    return
                
                logger.info(f"Processing user mention: {event}")
                user = event.get("user", "there")
                text = event.get("text", "").lower()
                
                # Handle different types of queries
                if any(word in text for word in ["how are you", "hello", "hi", "hey"]):
                    say(text=f"Hi <@{user}>! I'm doing great, thanks for asking! I'm here to help with sales information, legal queries, or general assistance. What would you like to know?")
                elif "sales" in text:
                    say(text=f"I'd be happy to help you with sales information, <@{user}>! What specific details are you looking for?")
                elif "legal" in text:
                    say(text=f"I can assist you with legal queries, <@{user}>! What information do you need?")
                else:
                    say(text=f"Hi <@{user}>! I'm here to help. You can ask me about sales, legal matters, or general information.")
                    
                logger.info(f"Response sent to user {user}")
            except Exception as e:
                logger.error(f"Mention handler error: {str(e)}")