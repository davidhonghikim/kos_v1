from src.core.agents.base_agent import BaseAgent

class Chef(BaseAgent):
    def act(self, ingredients):
        return f"Recipe for {self.name} using {ingredients}"
