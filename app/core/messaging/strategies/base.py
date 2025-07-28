
class MessageStrategy:
    def get_data(self):
        raise NotImplementedError()

    def send(self, phone, data, client):
        raise NotImplementedError()
