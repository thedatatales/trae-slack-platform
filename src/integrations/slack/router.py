from src.agents.pranav_agent import PranavAgent
from src.agents.nivetha_agent import NivethaAgent

import logging
import re

logger = logging.getLogger(__name__)

# [TODO: Refactor into platform-agnostic MessageRouter base class]
class SlackRouter:
    def __init__(self):
        self.agents = {
            'cfo': PranavAgent(),
            'cto': NivethaAgent()
        }
        self.conversation_history = {}
        logger.info("Router initialized with CFO and CTO agents")

    def _get_conversation_key(self, channel: str, user: str) -> str:
        return f"{channel}:{user}"
    
    # [TODO: Temporary Slack-specific routing – to be replaced with platform-agnostic message router]
    async def route_mention(self, event, say):
        try:
            channel = event.get("channel")
            user = event.get("user")
            text = event.get("text", "")
            
            logger.info(f"Processing mention from user {user} in channel {channel}")
            
            # Get conversation history key
            conv_key = self._get_conversation_key(channel, user)
            
            # Initialize conversation history if needed
            if conv_key not in self.conversation_history:
                self.conversation_history[conv_key] = []
            
            # Determine appropriate agent
            agent = await self._determine_agent(text)
            
            # [TODO: Move conversation history management to individual agents]
            # Add user message to history
            self.conversation_history[conv_key].append({"role": "user", "content": text})
            
            # Get response from agent
            response = await agent.run(text)
            
            # Add agent response to history
            self.conversation_history[conv_key].append({"role": "assistant", "content": response})
            
            # Keep only last 10 messages in history
            self.conversation_history[conv_key] = self.conversation_history[conv_key][-10:]
            
            # [TODO: Inline agent response formatting – move to channel adapter layer]
            await say(text=response)
            logger.info(f"Successfully processed mention and sent response")
            
        except Exception as e:
            logger.error(f"Error in route_mention: {str(e)}")
            logger.exception(e)
            await say(text="I apologize, but I encountered an error while processing your request.")
    
    # [TODO: Temporary Slack-specific routing – to be replaced with platform-agnostic message router]
    async def route_message(self, event, say):
        try:
            channel = event.get("channel")
            user = event.get("user")
            text = event.get("text", "")
            
            logger.info(f"Processing message from user {user} in channel {channel}")
            
            # Get conversation history key
            conv_key = self._get_conversation_key(channel, user)
            
            # Initialize conversation history if needed
            if conv_key not in self.conversation_history:
                self.conversation_history[conv_key] = []
            
            # Determine appropriate agent
            agent = await self._determine_agent(text)
            
            # [TODO: Move conversation history management to individual agents]
            # Add user message to history
            self.conversation_history[conv_key].append({"role": "user", "content": text})
            
            # Get response from agent
            response = await agent.run(text)
            
            # Add agent response to history
            self.conversation_history[conv_key].append({"role": "assistant", "content": response})
            
            # Keep only last 10 messages in history
            self.conversation_history[conv_key] = self.conversation_history[conv_key][-10:]
            
            # [TODO: Inline agent response formatting – move to channel adapter layer]
            await say(text=response)
            logger.info(f"Successfully processed message and sent response")
            
        except Exception as e:
            logger.error(f"Error in route_message: {str(e)}")
            logger.exception(e)
            await say(text="I apologize, but I encountered an error while processing your request.")
    
    # [TODO: Regex agent selection – to be replaced by NLP/intent-based planner]
    async def _determine_agent(self, text: str):
        text = text.lower()
        
        # Define keyword patterns for CFO and CTO agents
        patterns = {
            'cfo': r'\b(finance|budget|cost|investment|revenue|expense|financial|forecast|risk)\b',
            'cto': r'\b(tech|technology|architecture|system|infrastructure|security|development|engineering|cloud|devops)\b'
        }
        
        # Check each agent's keywords
        for agent_type, pattern in patterns.items():
            if re.search(pattern, text):
                return self.agents[agent_type]
        
        # Default to CFO agent if no specific patterns match
        return self.agents['cfo']