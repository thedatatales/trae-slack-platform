from src.core.summary_relay import SummaryRelay
from src.agents.base_agent import BaseAgent

class NevithaAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Nevitha",
            role="Chief Technology Officer"
        )
        self.summary_relay = SummaryRelay()

    def get_system_prompt(self) -> str:
        with open("src/agents/nevitha/system_prompt.txt", "r") as f:
            return f.read()

    def get_config(self) -> dict:
        return self.load_config("src/agents/nevitha/agent_config.yaml")