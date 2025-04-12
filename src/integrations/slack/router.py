from src.agents import PranavAgent, NevithaAgent, DashamAgent

import logging
import re

logger = logging.getLogger(__name__)

# [TODO: Refactor into platform-agnostic MessageRouter base class]
class SlackRouter:
    def __init__(self):
        self.agents = {
            'cfo': PranavAgent(),
            'cto': NevithaAgent(),
            'Pranav': PranavAgent(),
            'Nevitha': NevithaAgent(),
            'dasham': DashamAgent(),
            'Dasham': DashamAgent()
        }
        self.conversation_history = {}
        logger.info("Router initialized with CEO, CFO and CTO agents")

    def _get_conversation_key(self, channel: str, user: str) -> str:
        return f"{channel}:{user}"
    
    # [TODO: Temporary Slack-specific routing – to be replaced with platform-agnostic message router]
    async def route_mention(self, event, say):
        try:
            channel = event.get("channel")
            user = event.get("user")
            text = event.get("text", "")
            thread_ts = event.get("thread_ts")
            
            logger.info(f"Processing mention from user {user} in channel {channel}")
            
            # Extract hashtag mentions
            mentioned_agents = [agent_name for agent_name in self._extract_mentions(text)]
            
            # Get conversation history key
            conv_key = self._get_conversation_key(channel, user)
            
            # Initialize conversation history if needed
            if conv_key not in self.conversation_history:
                self.conversation_history[conv_key] = []
            
            # Add user message to history
            self.conversation_history[conv_key].append({"role": "user", "content": text})
            
            # Get Dasham agent - always responds as the unified voice
            dasham_agent = self.agents.get('dasham')
            response = ""
            
            # If a specific agent is tagged
            if mentioned_agents:
                for agent_name in mentioned_agents:
                    agent_key = agent_name.lower()
                    if agent_key in self.agents and agent_key != 'dasham':
                        # Get the specific agent
                        agent = self.agents[agent_key]
                        
                        # Get response from the agent
                        agent_response = await agent.run(text, user, thread_ts)
                        
                        if agent_response:
                            # Format response with attribution
                            attribution = f"According to {agent.name}"
                            response = f"{attribution}... {agent_response}"
                            
                            # Update agent's memory
                            agent.memory.save_entry({
                                "thread_id": thread_ts,
                                "message": text,
                                "response": agent_response,
                                "tags": ["delegated", "via_dasham"],
                                "summary": "Agent response delivered through Dasham",
                                "from": user if user else "Unknown"
                            })
                            break
            
            # If no specific agent is tagged or no valid agent found, use Dasham's own logic
            if not response:
                dasham_response = await dasham_agent.run(text, user, thread_ts)
                if dasham_response:
                    response = dasham_response
            
            # Send response if we have one
            if response:
                # Add signature to Dasham's direct responses (not when attributing to other agents)
                if not mentioned_agents or all(agent_name.lower() == 'dasham' for agent_name in mentioned_agents):
                    response += f"\n\n— {dasham_agent.name}, {dasham_agent.role}"
                
                # Add response to history
                self.conversation_history[conv_key].append({"role": "assistant", "content": response})
                await say(text=response)
                
                # Record the response in thread memory
                from ..core.thread_memory import thread_memory
                thread_memory.record_response(dasham_agent.name, thread_ts)
            
            # Keep only last 10 messages in history
            self.conversation_history[conv_key] = self.conversation_history[conv_key][-10:]
            
            logger.info(f"Successfully processed mention and sent responses")
            
        except Exception as e:
            logger.error(f"Error in route_mention: {str(e)}")
            logger.exception(e)
            await say(text="I apologize, but I encountered an error while processing your request.")
    
    # [TODO: Temporary Slack-specific routing – to be replaced with platform-agnostic message router]
    def _extract_mentions(self, text: str) -> list:
        """Extract agent mentions (e.g. #Pranav) from text."""
        return [word[1:] for word in text.split() if word.startswith('#')]

    async def route_message(self, event, say):
        try:
            channel = event.get("channel")
            user = event.get("user")
            text = event.get("text", "")
            thread_ts = event.get("thread_ts") or event.get("ts")
            
            logger.info(f"Processing message from user {user} in channel {channel}")
            
            # Get conversation history key
            conv_key = self._get_conversation_key(channel, user)
            
            # Initialize conversation history if needed
            if conv_key not in self.conversation_history:
                self.conversation_history[conv_key] = []
            
            # Add user message to history
            self.conversation_history[conv_key].append({"role": "user", "content": text})
            
            # Get Dasham agent - always responds as the unified voice
            dasham_agent = self.agents.get('dasham')
            response = ""
            
            # Extract mentions to check if specific agents are tagged
            mentioned_agents = self._extract_mentions(text)
            
            # If a specific agent is tagged (other than Dasham)
            if mentioned_agents:
                for agent_name in mentioned_agents:
                    agent_key = agent_name.lower()
                    if agent_key in self.agents and agent_key != 'dasham':
                        # Get the specific agent
                        agent = self.agents[agent_key]
                        
                        # Get response from the agent
                        agent_response = await agent.run(text, sender_id=user, thread_ts=thread_ts)
                        
                        if agent_response:
                            # Format response with attribution
                            attribution = f"{agent.name}'s view on this is"
                            response = f"{attribution}... {agent_response}"
                            
                            # Update agent's memory
                            agent.memory.save_entry({
                                "thread_id": thread_ts,
                                "message": text,
                                "response": agent_response,
                                "tags": ["delegated", "via_dasham"],
                                "summary": "Agent response delivered through Dasham",
                                "from": user if user else "Unknown"
                            })
                            break
            
            # If no specific agent is tagged or no valid agent found
            if not response:
                # If no specific agent mentioned, determine if we should use a specific agent based on content
                if not mentioned_agents:
                    content_specific_agent = await self._determine_agent(text)
                    if content_specific_agent and content_specific_agent.name.lower() != 'dasham':
                        # Get response from the content-specific agent
                        agent_response = await content_specific_agent.run(text, sender_id=user, thread_ts=thread_ts)
                        
                        if agent_response:
                            # Format response with attribution
                            attribution = f"Based on {content_specific_agent.name}'s expertise"
                            response = f"{attribution}... {agent_response}"
                            
                            # Update agent's memory
                            content_specific_agent.memory.save_entry({
                                "thread_id": thread_ts,
                                "message": text,
                                "response": agent_response,
                                "tags": ["inferred", "via_dasham"],
                                "summary": "Agent response delivered through Dasham based on content",
                                "from": user if user else "Unknown"
                            })
                
                # If still no response, use Dasham's own logic
                if not response:
                    dasham_response = await dasham_agent.run(text, sender_id=user, thread_ts=thread_ts)
                    if dasham_response:
                        response = dasham_response
            
            # Send response if we have one
            if response:
                # Add signature to Dasham's direct responses (not when attributing to other agents)
                if not mentioned_agents or all(agent_name.lower() == 'dasham' for agent_name in mentioned_agents):
                    response += f"\n\n— {dasham_agent.name}, {dasham_agent.role}"
                
                # Add response to history
                self.conversation_history[conv_key].append({"role": "assistant", "content": response})
                
                # Record the response in thread memory
                from ..core.thread_memory import thread_memory
                thread_memory.record_response(dasham_agent.name, thread_ts)
                
                # Keep only last 10 messages in history
                self.conversation_history[conv_key] = self.conversation_history[conv_key][-10:]
                
                await say(text=response)
                logger.info(f"Successfully processed message and sent response")
            else:
                logger.info(f"No response generated based on thread policy or content")
            
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
        
        # Default to Dasham if no specific patterns match
        return self.agents['dasham']