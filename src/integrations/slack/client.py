from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

class SlackClient:
    def __init__(self):
        load_dotenv()
        
        self.bot_token = os.environ.get("SLACK_BOT_TOKEN")
        self.signing_secret = os.environ.get("SLACK_SIGNING_SECRET")
        
        if not self.bot_token or not self.signing_secret:
            raise ValueError("Missing Slack credentials")
            
        logger.info("Initializing Slack app...")
        self.app = App(
            token=self.bot_token,
            signing_secret=self.signing_secret
        )
        
        # Test the token
        try:
            auth_test = self.app.client.auth_test()
            logger.info(f"Connected as: {auth_test['bot_id']}")
        except Exception as e:
            logger.error(f"Failed to authenticate: {str(e)}")
            raise
        logger.info("SlackClient initialized successfully")
        
    async def send_message(self, channel: str, text: str, thread_ts: str = None):
        """Send a message to a Slack channel"""
        return await self.app.client.chat_postMessage(
            channel=channel,
            text=text,
            thread_ts=thread_ts
        )
    
    async def send_to_channel(self, channel_id: str, text: str):
        """Wrapper method to send message to a channel"""
        return await self.send_message(channel=channel_id, text=text)
    
    async def send_thread_reply(self, channel_id: str, thread_ts: str, text: str):
        """Send a reply in a thread"""
        return await self.send_message(
            channel=channel_id,
            text=text,
            thread_ts=thread_ts
        )
    
    def start(self):
        """Start the Slack app in socket mode"""
        handler = SocketModeHandler(self.app, os.environ.get("SLACK_APP_TOKEN"))
        handler.start()