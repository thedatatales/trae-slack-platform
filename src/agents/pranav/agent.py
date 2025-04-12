from ..base_agent import BaseAgent
from ...core.summary_relay import Summary, SummaryRelay

class PranavAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Pranav Desai",
            role="Chief Financial Officer"
        )
        self.summary_relay = SummaryRelay()
        
    def send_summary(self, text: str, tags: list[str], thread_id: str = None) -> bool:
        """Send a summary using the SummaryRelay.
        
        Args:
            text: The main content of the summary
            tags: List of relevant tags
            thread_id: Optional thread ID for message threading
            
        Returns:
            bool: True if delivery was successful
        """
        summary = Summary(
            text=text,
            tags=tags,
            source_agent=self.name,
            thread_id=thread_id
        )
        return self.summary_relay.deliver_summary(summary)
    
    def get_system_prompt(self) -> str:
        with open("system_prompt.txt", "r") as f:
            return f.read()