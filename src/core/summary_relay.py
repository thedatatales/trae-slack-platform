from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Summary:
    text: str
    tags: List[str]
    source_agent: str
    thread_id: Optional[str] = None

class SummaryRelay:
    def __init__(self, delivery_method: str = "slack"):
        self.delivery_method = delivery_method
        
    def format_message(self, summary: Summary) -> str:
        """Format the summary into a structured message."""
        formatted_msg = f"*Update from {summary.source_agent}*\n\n"
        formatted_msg += f"{summary.text}\n\n"
        if summary.tags:
            formatted_msg += f"*Tags:* {', '.join(['#' + tag for tag in summary.tags])}"
        return formatted_msg
    
    def deliver_summary(self, summary: Summary) -> bool:
        """Deliver the summary to Dasham.
        
        Returns:
            bool: True if delivery was successful, False otherwise
        """
        message = self.format_message(summary)
        
        if self.delivery_method == "slack":
            # TODO: Implement Slack delivery using the Slack integration
            # This will be implemented once Slack integration is set up
            return self._deliver_to_slack(message, summary.thread_id)
        else:
            # Default to logging the message
            return self._log_message(message)
    
    def _deliver_to_slack(self, message: str, thread_id: Optional[str] = None) -> bool:
        """Deliver the message to Slack.
        
        Args:
            message: The formatted message to send
            thread_id: Optional thread ID for threading messages
            
        Returns:
            bool: True if delivery was successful, False otherwise
        """
        # TODO: Implement actual Slack delivery
        # For now, just log the message
        print(f"[SLACK] {message}")
        return True
    
    def _log_message(self, message: str) -> bool:
        """Log the message for storage/debugging.
        
        Args:
            message: The formatted message to log
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            print(f"[LOG] {message}")
            return True
        except Exception as e:
            print(f"Error logging message: {e}")
            return False