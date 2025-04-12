import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class ThreadMemoryManager:
    def __init__(self):
        self.thread_memory: Dict[str, Dict[str, Dict]] = {}
        
    def _get_memory_key(self, agent_name: str, thread_ts: str) -> str:
        return f"{agent_name}:{thread_ts}"
        
    def can_respond(self, agent_name: str, thread_ts: str, mentioned: bool = False) -> bool:
        """Check if an agent can respond in a thread based on previous responses and mentions.
        
        Args:
            agent_name: Name of the agent
            thread_ts: Slack thread timestamp
            mentioned: Whether the agent was explicitly mentioned with #AgentName
            
        Returns:
            bool: True if agent can respond, False otherwise
        """
        memory_key = self._get_memory_key(agent_name, thread_ts)
        
        # Agent can always respond if explicitly mentioned with #AgentName
        if mentioned:
            logger.info(f"Agent {agent_name} was explicitly mentioned in thread {thread_ts}")
            return True
            
        # Check if agent has already responded in this thread
        thread_data = self.thread_memory.get(memory_key)
        if thread_data:
            logger.info(f"Agent {agent_name} has already responded in thread {thread_ts}")
            return False
            
        # Check if any other agent has responded in this thread
        for key in self.thread_memory:
            if key.endswith(f":{thread_ts}") and key != memory_key:
                logger.info(f"Another agent has already responded in thread {thread_ts}")
                return False
                
        logger.info(f"Agent {agent_name} can respond in thread {thread_ts} (first response)")
        return True
        
    def record_response(self, agent_name: str, thread_ts: str) -> None:
        """Record that an agent has responded in a thread.
        
        Args:
            agent_name: Name of the agent
            thread_ts: Slack thread timestamp
        """
        memory_key = self._get_memory_key(agent_name, thread_ts)
        self.thread_memory[memory_key] = {
            'last_response': datetime.now().isoformat(),
            'response_count': self.thread_memory.get(memory_key, {}).get('response_count', 0) + 1
        }
        
    def get_last_response_time(self, agent_name: str, thread_ts: str) -> Optional[str]:
        """Get the timestamp of agent's last response in a thread.
        
        Args:
            agent_name: Name of the agent
            thread_ts: Slack thread timestamp
            
        Returns:
            Optional[str]: ISO format timestamp of last response if exists, None otherwise
        """
        memory_key = self._get_memory_key(agent_name, thread_ts)
        thread_data = self.thread_memory.get(memory_key)
        return thread_data.get('last_response') if thread_data else None

# Global instance for use across the application
thread_memory = ThreadMemoryManager()