import os
import json
from datetime import datetime

class AgentMemoryManager:
    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        safe_name = agent_name.lower().replace(" ", "_")  # ← FIX HERE
        self.memory_file_path = f"src/agents/{safe_name}/memory.json"
        self._initialize_memory_file()

    def _initialize_memory_file(self):
        directory = os.path.dirname(self.memory_file_path)
        os.makedirs(directory, exist_ok=True)  # ← Ensure folder exists
        if not os.path.exists(self.memory_file_path):
            with open(self.memory_file_path, 'w') as f:
                json.dump([], f)

    def save_entry(self, entry: dict):
        entry['timestamp'] = datetime.now().isoformat()
        with open(self.memory_file_path, 'r+') as f:
            memory = json.load(f)
            memory.append(entry)
            f.seek(0)
            json.dump(memory, f, indent=4)

    def get_recent(self, limit: int = 5):
        with open(self.memory_file_path, 'r') as f:
            memory = json.load(f)
            return memory[-limit:] if len(memory) >= limit else memory
