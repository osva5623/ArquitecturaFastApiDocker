
from .base import MessageStrategy

class WelcomeStrategy(MessageStrategy):
    def get_data(self):
        return {
            "text": "¡Hola! ¿Te interesa duplicar tus datos gratis?"
        }

    def send(self, phone, data, client):
        client.send_text(phone, data["text"])
