from fastapi import APIRouter, HTTPException,Request
from fastapi.responses import JSONResponse
import argparse
import datetime
import time
import base64
import json
import logging

# app/main.py
import base64, json, asyncio
from aio_pika import connect_robust, Message

from rcs_business_messaging import rbm_service
from rcs_business_messaging import messages
from rcs_business_messaging import agent_config
router = APIRouter()

# === Configuración ===
AGENT_ID = "prueba_ujyndkxw_agent"
RABBIT_URL = "amqp://user:pass@rabbitmq/"


logger = logging.getLogger("uvicorn")


def envio_mensaje(msisdn):


    message_text = messages.TextMessage('What is your favorite color?')

        # Send user an opening message to start the conversation
    messages.MessageCluster().append_message(message_text).send_to_msisdn(msisdn)

        # Send a message with a 10 second expiry
        # messages.MessageCluster().append_message(message_text).send_to_msisdn(msisdn, '10s')

        # Send a message with a specified expiry time of 20 seconds from now
        # d = datetime.datetime.utcnow() + datetime.timedelta(0, 20)
        # timeToStop = d.strftime('%Y-%m-%dT%H:%M:%SZ')
        # messages.MessageCluster().append_message(message_text).send_to_msisdn(msisdn, expireTime=timeToStop)



@router.get("/")
async def hello_world():
    return {"mensaje": "Hola Mundo desde FastAPI"}




@router.post("/webhook")
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
        logger.info("⚠️payload: %s", decoded_json)

        if "senderPhoneNumber" in decoded_json and "text" in decoded_json:

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
        # Ignorar otros eventos del sistema
        logger.info("⚠️ Evento ignorado (no es mensaje de texto de usuario): %s", decoded_json)
    
    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.post("/antiguowebhook")
async def callback(request: Request):
    try:
        payload = await request.json()
        logger.info("Webhook recibido")
        
        # 🔐 Verificación inicial del webhook (evento de configuración)
        if "clientToken" in payload:
            print(payload)

            return JSONResponse(content={"secret": payload.get("secret")}, status_code=200)

        if "message" not in payload:
            logger.warning("⚠️ No se encontró 'data' en el mensaje.")
            return JSONResponse(content={"status": "no_data"}, status_code=200)

        pubsub_message = payload["message"]
        data_encoded = pubsub_message.get("data")


        if not data_encoded:
            logger.warning("⚠️ Falta campo 'data' en el mensaje.")
            return JSONResponse(content={"status": "no_data"}, status_code=200)

        decoded_json = base64.b64decode(data_encoded).decode("utf-8")
        request_body = json.loads(decoded_json)
        # ✉️ Evento de mensaje entrante
        if "senderPhoneNumber" in request_body:
            JSONResponse(status_code=200, content={"status": "ok"})
            rbm_service.init(AGENT_ID)
            # Extract the text from userEvent
            msisdn = request_body["senderPhoneNumber"]
            logger.info(f"Mensaje recibido de {msisdn}")
            message_text = messages.TextMessage('Hello, world!')

            messages.MessageCluster().append_message(message_text).send_to_msisdn(msisdn)

            logger.info(f"Mensaje enviado a {msisdn}")
        return 

    except Exception as e:
        logger.error(f"Webhook handling failed: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
