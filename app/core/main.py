
from fastapi import FastAPI, Request
from rcs_helper import RCSHelper
from messaging.facade import RCSClientFacade
from campaigns.factory import CampaignFactory

app = FastAPI()
rcs_helper = RCSHelper()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()

    phone = body.get("senderPhoneNumber")
    text = body.get("text", "").lower()
    postback = body.get("suggestionResponse", {}).get("postbackData", "").lower()
    trigger = postback or text

    campaign_id = body.get("campaignId", "A")
    agent_id = body.get("agentId", "default")

    campaign = CampaignFactory.get_campaign(campaign_id, agent_id)
    strategy = campaign.get_strategy(trigger)

    client = RCSClientFacade(rcs_helper)
    data = strategy.get_data()
    strategy.send(phone, data, client)

    return {"status": "ok"}
