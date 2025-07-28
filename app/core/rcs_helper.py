
class RCSHelper:
    def send_message(self, phone, payload):
        print(f"[RCS] Enviando mensaje a {phone}: {payload}")
        return {"status": "sent"}

    def send_card(self, phone, title, suggestions):
        print(f"[RCS] Enviando card a {phone}: {title} con {suggestions}")
        return {"status": "card_sent"}
