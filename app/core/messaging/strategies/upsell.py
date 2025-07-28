
from .base import MessageStrategy

class UpsellStrategy(MessageStrategy):
    def get_data(self):
        return {
            "title": "Oferta especial: duplica tus datos por solo $50 más.",
            "suggestions": ["¡Claro!", "No, gracias"]
        }

    def send(self, phone, data, client):
        client.send_card(phone, data["title"], data["suggestions"])
