# app/main.py
import base64, json, asyncio
from fastapi import FastAPI, Request
from aio_pika import connect_robust, Message
from fastapi.responses import JSONResponse

app = FastAPI()

RABBIT_URL = "amqp://user:pass@rabbitmq/"

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()

        if "clientToken" in payload:
            return JSONResponse(content={"secret": payload.get("secret")}, status_code=200)

        if "message" not in payload:
            return JSONResponse(content={"status": "no_data"}, status_code=200)

        data_encoded = payload["message"].get("data")
        if not data_encoded:
            return JSONResponse(content={"status": "no_data"}, status_code=200)

        decoded_json = base64.b64decode(data_encoded).decode("utf-8")

        # Enviar a la cola
        connection = await connect_robust(RABBIT_URL)
        channel = await connection.channel()
        queue = await channel.declare_queue("rcs_messages", durable=True)
        await channel.default_exchange.publish(
            Message(body=decoded_json.encode()),
            routing_key=queue.name
        )
        await connection.close()

        return JSONResponse(status_code=200, content={"status": "queued"})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

