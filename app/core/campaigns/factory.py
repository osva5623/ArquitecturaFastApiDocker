
from campaigns.campaign_a import CampaignA

class CampaignFactory:
    @staticmethod
    def get_campaign(campaign_id, agent_id):
        if campaign_id == "A":
            return CampaignA("A", agent_id)
        else:
            raise ValueError("Campaña no reconocida")
