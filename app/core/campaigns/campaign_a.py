
from messaging.strategies.welcome import WelcomeStrategy
from messaging.strategies.upsell import UpsellStrategy
from campaigns.base import Campaign

class CampaignA(Campaign):
    def get_strategy(self, trigger: str):
        if "hola" in trigger:
            return WelcomeStrategy()
        elif "sí" in trigger or "quiero" in trigger:
            return UpsellStrategy()
        else:
            return WelcomeStrategy()
