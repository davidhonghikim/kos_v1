from src.core.agents.base_agent import BaseAgent

class Ronin(BaseAgent):
    def act(self, mission):
        return f"Ronin completes the mission: {mission}"
