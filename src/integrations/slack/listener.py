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
        
        # Enhanced interaction patterns
        self.interaction_patterns = {
            'greetings': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'gratitude': ['thank', 'thanks', 'appreciate', 'grateful'],
            'guidance': ['what next', 'what should', 'help me', 'advice', 'suggest'],
            'team_query': ['pranav', 'nivetha', 'nivitha', 'cfo', 'cto', 'team']
        }
        
        # Updated CEO prompt for more concise responses
        self.ceo_prompt = """You are Dasham, CEO. Your style:
- Direct and warm
- Strategic yet approachable
- Concise but personable

Key points:
- You lead a team including Pranav (CFO, finance expert) and Nivetha (CTO, tech leader)
- You value clarity and purposeful communication
- You aim to guide and connect people with the right resources

Keep responses brief but impactful."""

    def _create_enhanced_prompt(self, text: str, interaction_type: str) -> str:
        base_prompt = f"{self.ceo_prompt}\n\nUser message: {text}\n\nResponse as Dasham:"
        
        if interaction_type == 'team_query':
            return f"{base_prompt}\nMention your team members' roles briefly and offer to involve them if relevant."
        elif interaction_type == 'greetings':
            return f"{base_prompt}\nKeep the greeting warm but brief."
        elif interaction_type == 'gratitude':
            return f"{base_prompt}\nAcknowledge briefly and offer forward-looking support."
        elif interaction_type == 'guidance':
            return f"{base_prompt}\nProvide clear, actionable guidance."
        else:
            return f"{base_prompt}\nRespond concisely while being helpful."
    
    def _register_handlers(self):
        @self.client.app.event("app_mention")
        async def handle_app_mention(body, say):
            try:
                print("=== Starting app_mention handler ===")
                event = body["event"]
                
                # Route the mention through the router
                await self.router.route_mention(event, say)
                    
            except Exception as e:
                print(f"Error in app_mention handler: {str(e)}")
                try:
                    say(f"<@{event.get('user', 'there')}> Sorry, I encountered an error.")
                except:
                    print("Could not send error message")

        @self.client.app.event("message")
        def handle_message(body, say):
            try:
                print("=== Starting message handler ===")
                event = body["event"]
                
                if event.get("subtype") == "bot_message" or "bot_id" in event:
                    return
                
                user = event.get("user", "there")
                text = event.get("text", "").strip().lower()
                
                # Handle different interaction types
                prompt_type = self._get_interaction_type(text)
                enhanced_prompt = self._create_enhanced_prompt(text, prompt_type)
                
                # Send acknowledgment for longer queries
                if len(text.split()) > 3 and prompt_type not in ['greetings', 'gratitude']:
                    say(text=f"<@{user}> I'm processing your request, please wait...")
                
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={
                        "model": "mistral",
                        "prompt": enhanced_prompt,
                        "stream": False,
                        "temperature": 0.7
                    },
                    timeout=60
                ).json().get('response')
                
                say(text=f"<@{user}> {response}")
                print("Response sent successfully")
                    
            except Exception as e:
                print(f"Error in message handler: {str(e)}")
                try:
                    say(f"<@{event.get('user', 'there')}> Sorry, I encountered an error.")
                except:
                    print("Could not send error message")
    
    def _get_interaction_type(self, text: str) -> str:
        for interaction_type, patterns in self.interaction_patterns.items():
            if any(pattern in text for pattern in patterns):
                return interaction_type
        return 'general'
    
    async def generate_default_response(self, text: str) -> str:
        # Your existing Ollama code here
        pass