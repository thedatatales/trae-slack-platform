from .client import SlackClient
from .router import SlackRouter
from slack_bolt.adapter.fastapi import SlackRequestHandler
from ...llm.ollama_client import OllamaClient
import requests
from ...agents import PranavAgent, NivethaAgent
import logging

logger = logging.getLogger(__name__)

class SlackEventListener:
    def __init__(self, client: SlackClient):
        self.client = client
        self.router = SlackRouter()
        self.handler = SlackRequestHandler(self.client.app)
        self.pranav = PranavAgent()
        self.nivetha = NivethaAgent()
        self._register_handlers()
    
    def _register_handlers(self):
        @self.client.app.event("app_mention")
        async def handle_mention(body, say):
            try:
                event = body["event"]
                await self.router.route_mention(event, say)
            except Exception as e:
                logger.error(f"Error in app_mention handler: {str(e)}")
                logger.exception(e)
                await say(text=f"<@{event.get('user', 'there')}> Sorry, I encountered an error.")

        @self.client.app.event("message")
        def handle_message(body, say):
            try:
                print("=== Starting message handler ===")
                event = body["event"]
                
                if event.get("subtype") == "bot_message" or "bot_id" in event:
                    return
                
                user = event.get("user", "there")
                text = event.get("text", "").strip()
                
                # Send acknowledgment
                say(text=f"<@{user}> I'm processing your request, please wait...")
                
                # Route to appropriate agent based on content
                if any(word in text.lower() for word in ["finance", "budget", "cost", "investment", "risk"]):
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "mistral",
                            "prompt": f"As a CFO named Pranav: {text}",
                            "stream": False
                        },
                        timeout=60
                    ).json().get('response')
                elif any(word in text.lower() for word in ["tech", "infrastructure", "cloud", "devops", "ai", "machine learning", "tech stack", "framework", "architecture"]):
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "mistral",
                            "prompt": f"As a CTO named Nivetha with expertise in AI and technology stacks: {text}",
                            "stream": False
                        },
                        timeout=60
                    ).json().get('response')
                else:
                    response = "I'm not sure how to help with that. Try asking about finance or technology."
                
                say(text=f"<@{user}> {response}")
                print("Response sent successfully")
                    
            except Exception as e:
                print(f"Error in message handler: {str(e)}")
                try:
                    say(f"<@{event.get('user', 'there')}> Sorry, I encountered an error.")
                except:
                    print("Could not send error message")
    
    async def generate_default_response(self, text: str) -> str:
        # Your existing Ollama code here
        pass