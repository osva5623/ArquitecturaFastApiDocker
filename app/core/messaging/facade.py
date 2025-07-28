
class RCSClientFacade:
    def __init__(self, helper):
        self.helper = helper

    def send_text(self, phone, text):
        return self.helper.send_message(phone, {"text": text})

    def send_card(self, phone, title, suggestions):
        return self.helper.send_card(phone, title, suggestions)
