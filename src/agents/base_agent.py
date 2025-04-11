import aiohttp
import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "mistral"
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the agent-specific system prompt"""
        pass
        
    async def run(self, prompt: str) -> str:
        try:
            system_prompt = self.get_system_prompt()
            enhanced_prompt = f"""System: {system_prompt}
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
                        return result.get('response', 'I apologize, I cannot generate a response.')
                    else:
                        logger.error(f"LLM API error: {response.status}")
                        return "I encountered an error processing your request."
                        
        except Exception as e:
            logger.error(f"Error in agent {self.name}: {str(e)}")
            return f"I apologize, but I encountered an error while processing your request."