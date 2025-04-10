from src.agents.sales_agent import SalesAgent
from src.agents.legal_agent import LegalAgent
from src.agents.general_agent import GeneralAgent

import logging

logger = logging.getLogger(__name__)

class SlackRouter:
    def __init__(self):
        self.agents = {}
        logger.info("Router initialized")
    
    async def route_mention(self, event, say):
        try:
            logger.info(f"Route mention called with say function: {say}")
            # Test the say function directly
            await say(text="Hello from router!")
            logger.info("Message sent from router")
        except Exception as e:
            logger.error(f"Router error: {str(e)}")
            logger.exception(e)
            channel = event.get("channel")
            logger.info(f"Routing mention for channel: {channel}")
            await say(channel=channel, text="Hello Amit")
            logger.info("Message sent successfully")
        except Exception as e:
            logger.error(f"Failed to send message: {str(e)}")
            logger.exception(e)
            await say("Error occurred")
    
    async def route_message(self, event, say):
        try:
            logger.info("Received message event")
            # Hardcoded response for testing
            await say(text="Hello Amit")
        except Exception as e:
            logger.error(f"Error in route_message: {str(e)}")
            await say("Error occurred")
    
    async def _determine_agent(self, text: str):
        if 'sales' in text.lower():
            return self.agents['sales']
        elif 'legal' in text.lower():
            return self.agents['legal']
        return self.agents['general']