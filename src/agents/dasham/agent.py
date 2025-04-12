from src.core.summary_relay import SummaryRelay
from src.agents.base_agent import BaseAgent

class DashamAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Dasham",
            role="Chief Executive Officer"
        )
        self.summary_relay = SummaryRelay()

    def get_system_prompt(self) -> str:
        with open("src/agents/dasham/system_prompt.txt", "r") as f:
            return f.read()

    def get_config(self) -> dict:
        return self.load_config("src/agents/dasham/agent_config.yaml")