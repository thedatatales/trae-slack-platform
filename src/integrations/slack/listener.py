from .client import SlackClient
from .router import SlackRouter
from slack_bolt.adapter.fastapi import SlackRequestHandler
from ...llm.ollama_client import OllamaClient
import requests
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
                print("=== Starting message handler ===")
                event = body["event"]
                
                # Skip bot messages
                if event.get("subtype") == "bot_message" or "bot_id" in event:
                    return
                
                # Skip messages without text
                if "text" not in event:
                    return
                
                user = event.get("user", "there")
                text = event.get("text", "").strip()
                
                # Process message
                say(text=f"<@{user}> I'm processing your request, please wait...")
                
                # Enhanced prompt with context
                enhanced_prompt = f"""You are Dasham, a helpful AI assistant. 
                Keep your responses concise and direct.
                User question: {text}"""
                
                # Send request to Ollama
                response = requests.post(
                    "http://127.0.0.1:11434/api/generate",
                    json={
                        "model": "mistral",
                        "prompt": enhanced_prompt,
                        "stream": False,
                        "temperature": 0.7,
                        "top_k": 40,
                        "top_p": 0.9
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    ai_response = response.json().get('response', 'Sorry, I could not generate a response.')
                    say(text=f"<@{user}> {ai_response}")
                    print("Response sent successfully")
                else:
                    print(f"Ollama error status: {response.status_code}")
                    say(text=f"<@{user}> I encountered an error generating a response.")
                    
            except requests.Timeout:
                print("Request timed out")
                say(text=f"<@{user}> Sorry, the response is taking too long. Please try a shorter question.")
            except Exception as e:
                print(f"Error in message handler: {str(e)}")
                try:
                    say(f"<@{event.get('user', 'there')}> Sorry, I encountered an error.")
                except:
                    print("Could not send error message")