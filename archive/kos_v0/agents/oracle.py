from src.core.agents.base_agent import BaseAgent

class Oracle(BaseAgent):
    def act(self, question):
        return f"Oracle says: The answer to '{question}' is 42."
