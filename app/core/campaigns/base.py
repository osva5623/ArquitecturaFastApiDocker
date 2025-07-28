
class Campaign:
    def __init__(self, name, agent_id):
        self.name = name
        self.agent_id = agent_id

    def get_strategy(self, trigger: str):
        raise NotImplementedError("Debe implementarse en campañas concretas.")
