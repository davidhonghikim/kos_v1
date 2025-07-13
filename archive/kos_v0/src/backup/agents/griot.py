from src.core.agents.base_agent import BaseAgent

class Griot(BaseAgent):
    def act(self, story_request):
        return f"Once upon a time in the land of {self.name}..."
