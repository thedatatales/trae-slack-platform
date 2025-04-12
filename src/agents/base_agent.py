import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Optional
from ..core.thread_memory import thread_memory
from src.core.memory.agent_memory_manager import AgentMemoryManager

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "mistral"
        self.memory = AgentMemoryManager(agent_name=self.name)
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent-specific system prompt"""
        pass
        
    async def run(self, prompt: str, sender_id: str = None, thread_ts: Optional[str] = None) -> str:
        try:
            # Extract any agent references from the prompt (e.g. #Pranav)
            referenced_agents = [word[1:] for word in prompt.split() if word.startswith('#')]
            mentioned = self.name in referenced_agents
            
            # Check if agent can respond in this thread
            if thread_ts and not thread_memory.can_respond(self.name, thread_ts, mentioned):
                return ""
                
            system_prompt = self.get_system_prompt()
            # Build context about message sender and referenced agents
            sender_context = f"Message from user {sender_id}" if sender_id else "Message from an unknown user"
            agent_context = f" referencing {', '.join(referenced_agents)}" if referenced_agents else ""
            
            enhanced_prompt = f"""System: {system_prompt}
            Context: {sender_context}{agent_context}
            User: {prompt}
            Assistant: Let me help you with that as {self.name}, {self.role}."""
            
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": enhanced_prompt,
                    "stream": False,
                    "temperature": 0.7,
                    "top_k": 40,
                    "top_p": 0.9
                }
                
                async with session.post(self.base_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        response_text = result.get('response', 'I apologize, I cannot generate a response.').strip()
                        return f"{response_text}\n\n— {self.name}, {self.role}"
                    else:
                        logger.error(f"LLM API error: {response.status}")
                        return "I encountered an error processing your request."
                        
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request."
            
        # Save interaction to agent memory
        self.memory.save_entry({
            "thread_id": thread_ts,
            "message": prompt,
            "tags": ["inferred", "auto"],
            "summary": "Agent responded to message",
            "from": sender_id if sender_id else "Unknown"
        })