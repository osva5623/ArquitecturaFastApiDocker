from fastapi import APIRouter, HTTPException
import httpx
import os

router = APIRouter()

RCS_API_URL = os.getenv("RCS_API_BASE_URL")
API_KEY = os.getenv("RCS_API_KEY")

@router.post("/send-rcs")
async def send_rcs_message(to: str, message: str):
    try:
        payload = {
            "to": to,
            "message": message,
            "apiKey": API_KEY
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{RCS_API_URL}/send", json=payload)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))

@router.get("/")
async def hello_world():
    return {"mensaje": "Hola Mundo desde FastAPI"}
    