class BaseAgent:
    def __init__(self, name):
        self.name = name

    def act(self, input_data):
        raise NotImplementedError
