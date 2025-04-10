import aiohttp
import logging
import asyncio

logger = logging.getLogger(__name__)

class OllamaClient:
    def __init__(self):
        self.base_url = "http://localhost:11434/api/generate"
        self.model = "mistral"
        self.timeout = aiohttp.ClientTimeout(total=30)  # 30 seconds timeout
    
    async def generate_response(self, prompt: str) -> str:
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                payload = {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False  # Disable streaming for faster response
                }
                
                async with session.post(self.base_url, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get('response', 'I apologize, I cannot generate a response at the moment.')
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        raise Exception(f"API error: {response.status}")
                        
        except asyncio.TimeoutError:
            logger.error("Request timed out")
            return "I'm sorry, the response took too long. Please try again."
        except Exception as e:
            logger.error(f"Error: {str(e)}")
            return "I encountered an error processing your request."