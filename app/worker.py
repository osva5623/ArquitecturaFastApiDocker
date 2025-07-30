import asyncio, json, aio_pika
from aio_pika import connect_robust
import logging
import base64
import json
import uuid
import requests
from google.oauth2 import service_account
from google.auth.transport.requests import Request


from core.rbm.rbm_service import RBMService
from core.rbm.rbm_repository import RBMRepository

from rcs_business_messaging import rbm_service
from rcs_business_messaging import messages
from rcs_business_messaging import agent_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AGENT_ID = "prueba_ujyndkxw_agent"
RABBITMQ_URL = "amqp://user:pass@rabbitmq/"
MAX_RETRIES = 10
RETRY_SECONDS = 3

SERVICE_ACCOUNT_FILE = "resource/rbm-agent-service-account-credentials.json"
REGION = "us"  # o "europe-west1", según tu configuración



"""
nombre 
apellido p
apellido m
fecha de nacimiento
email
"""


async def connect_with_retry():
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"🔄 Conectando a RabbitMQ (intento {attempt})...")
            connection = await aio_pika.connect_robust(RABBITMQ_URL)
            print("✅ ¡Conectado a RabbitMQ!")
            return connection
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(RETRY_SECONDS)
    raise RuntimeError(
        "🚫 No se pudo conectar a RabbitMQ después de varios intentos  s"
    )


async def handle_message(body: bytes):

    repository = RBMRepository(AGENT_ID)

    rbm_service_udp = RBMService(repository)
    # decoded_json = base64.b64decode(data_encoded).decode("utf-8")
    rbm_service.init(AGENT_ID)
    payload = json.loads(body.decode("utf-8"))
    logger.info(f"🔔 Procesando mensaje: {payload}")

    data_decoded = json.loads(
        base64.b64decode(payload["message"].get("data")).decode("utf-8")
    )
    logger.info(f"🔔 Procesando data_mensaje: {data_decoded}")

    attributos = payload["message"].get("attributes")
    logger.info(f"🔔 atributos: {attributos}")

    tipo_mensaje = attributos.get("message_type")
    logger.info(f"🔔 tipo mensaje: {tipo_mensaje}")

    msisdn = data_decoded["senderPhoneNumber"]
    formId=msisdn+'_sep_'+AGENT_ID


    logger.info(f"mensaje dn: {msisdn}")

    if "SUGGESTION_RESPONSE" == tipo_mensaje:
        postback = data_decoded["suggestionResponse"].get("postbackData", "").lower()
        if postback == "acepto":
            mensaje = """ 📌Tu cambio de línea prepago a un plan de renta mensual con TikTok, WhatsApp, Instagram y más se aplicará en las siguientes 24 horas después de tu confirmación ⏰.
Para completar, es muy importante que finalices este registro.
Puedes consultar tus beneficios en la imagen que recibiste al inicio."""

            mensajeRbm = rbm_service_udp.rbm_message(mensaje)
            cluster = messages.MessageCluster().append_message(mensajeRbm)

            MESSAGE_ID = str(uuid.uuid4().int) + "a"
            cluster.send_to_msisdn(msisdn)
            SCOPES = ["https://www.googleapis.com/auth/rcsbusinessmessaging"]
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            credentials.refresh(Request())
            access_token = credentials.token


            
            logger.info(f"token {access_token}")
            payload = {
                "contentMessage": {
                    "richCard": {
                        "standaloneCard": {
                            "cardOrientation": "VERTICAL",
                            
                            "cardContent": {
                                "title": "Informacion de tu cuenta",
                                "description": "Por favor, captura los datos de tu cuenta para completar la migración.",
                                "suggestions": [
                                    {
                                        "action": {
                                            "text": "Captura de datos",
                                            "postbackData": "reply:datos_capturados",
                                            "openUrlAction": {
                                                "url": f"https://formularios-master-ackcbg.laravel.cloud/formularios/{msisdn}_sep_{AGENT_ID}",
                                                "application": "WEBVIEW",
                                                "webviewViewMode": "TALL",
                                                "description": "Accessibility description"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "suggestions": []
                }
            }

            url = f"https://rcsbusinessmessaging.googleapis.com/v1/phones/{msisdn}/agentMessages?messageId={MESSAGE_ID}&agentId={AGENT_ID}"

            # === ENVIAR MENSAJE ===
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": "curl/rcs-business-messaging"
            }
            json_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            response = requests.post(url, headers=headers, data=json_data)
            




        elif postback == "otra_ocasion":

            mensaje = """❌ Has rechazado el cambio de tu línea a un plan de renta mensual.

Tu línea continuará como prepago y no se aplicará ningún cambio.F

📞 Si cambias de opinión, puedes solicitar la oferta por llamada telefónica con uno de nuestros asesores.

⏳ Recuerda que esta promoción con TikTok, WhatsApp, Instagram y más está disponible por tiempo limitado, y podrías perder los beneficios si no confirmas pronto.
                        """
            mensajeRbm = rbm_service_udp.rbm_message(mensaje)
            cluster = messages.MessageCluster().append_message(mensajeRbm)
            cluster.send_to_msisdn(msisdn)
        elif postback == "correctos":
            mensaje = """✅ ¡Terminamos!.
                        Una vez CONFIRADO el cambio de modalidad de tu línea de recarga al plan de renta mensual seleccionado, recibirás los detalles en el correo electrónico proporcionado con la información de tus nuevos beneficios contratados.
También puedes consultar los detalles de tu cuenta en la app Mi Movistar MX: 
                        https://play.google.com/store/apps/details?id=com.movistarmx.mx.app"""
            mensajeRbm = rbm_service_udp.rbm_message(mensaje)
            cluster = messages.MessageCluster().append_message(mensajeRbm)
            cluster.send_to_msisdn(msisdn)
        elif postback == "incorrectos":
            MESSAGE_ID = str(uuid.uuid4().int) + "a"
            SCOPES = ["https://www.googleapis.com/auth/rcsbusinessmessaging"]
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES
            )
            credentials.refresh(Request())
            access_token = credentials.token


            
            logger.info(f"token {access_token}")
            payload = {
                "contentMessage": {
                    "richCard": {
                        "standaloneCard": {
                            "cardOrientation": "VERTICAL",
                            
                            "cardContent": {
                                "title": "Informacion de tu cuenta",
                                "description": "Por favor, captura los datos de tu cuenta para completar la migraci\u00f3n.",
                                "suggestions": [
                                    {
                                        "action": {
                                            "text": "Captura de datos",
                                            "postbackData": "reply:datos_capturados",
                                            "openUrlAction": {
                                                "url": f"https://formularios-master-ackcbg.laravel.cloud/formularios/{msisdn}_sep_{AGENT_ID}",
                                                "application": "WEBVIEW",
                                                "webviewViewMode": "TALL",
                                                "description": "Accessibility description"
                                            }
                                        }
                                    }
                                ]
                            }
                        }
                    },
                    "suggestions": []
                }
            }

            url = f"https://rcsbusinessmessaging.googleapis.com/v1/phones/{msisdn}/agentMessages?messageId={MESSAGE_ID}&agentId={AGENT_ID}"

            # === ENVIAR MENSAJE ===
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": "curl/rcs-business-messaging"
            }
            json_data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            response = requests.post(url, headers=headers, data=json_data)
    elif "TEXT" == tipo_mensaje:

        orientation = "VERTICAL"
        title = "Tienes 6gb esperandote 🔥🚀"
        description = """🚀 Actívala ahora y empieza a disfrutar de más velocidad, más libertad y más conexión donde quiera que estés.
    No dejes pasar esta oportunidad, los GB no van a esperar para siempre 😉

    👉 Toca aquí y aprovecha esta promo antes de que se acabe."""
        image_url = "https://content-ci360.movistar.com.mx/tngcipecvus/2/5919d7c2-ef61-495e-9321-ba6d0c33708c"
        suggestions = {"Acepto migrarme": "acepto", "En otra ocasion": "otra_ocasion"}
        size = "MEDIUM"
        """
                suggestions = [
        messages.SuggestedReply('Acepto migrarme', 'acepto'),
        messages.SuggestedReply('En otra ocasion', 'otra_ocasion'),
        ]

        """

        # Image to be displayed by the card

        rich_card = rbm_service_udp.StandaloneCard(
            orientation, title, description, suggestions, image_url, size
        )

        logger.info(f"standalone card rbm service: {rich_card}")

        cluster = messages.MessageCluster().append_message(rich_card)
        cluster.send_to_msisdn(msisdn)
        # Aquí pones tu lógica con rbm_service, etc.

        logger.info("✅ Mensaje enviado")

    # if "senderPhoneNumber" in decoded_json and "text" in decoded_json:


"""    rbm_service.init(AGENT_ID)
    msisdn = payload["senderPhoneNumber"]
    message_id = payload['messageId']

    print(f"🔔 Procesando mensaje de: {payload.get('senderPhoneNumber')}")
    logger.info(f"Mensaje recibido de {msisdn}")"""


async def handle_message_formulario(body: bytes):
    repository = RBMRepository(AGENT_ID)
    
    rbm_service_udp = RBMService(repository)
    # decoded_json = base64.b64decode(data_encoded).decode("utf-8")
    rbm_service.init(AGENT_ID)
    payload = json.loads(body.decode("utf-8"))
    logger.info(f"🔔 Procesando mensaje de formulario: {payload}")

    msisdn= payload["usuario"].split('_sep_')[0]
    if(len(msisdn) < 13):
        return 0
    nombre = payload["name"]
    email = payload["email"]
    apellido_p = payload["apellidoP"]
    apellido_m = payload["apellidoM"]
    fecha_nacimiento = payload["day"]+"/"+ payload["month"]+"/"+payload["year"]
    # Procesa mensaje de formulario

    orientation = "VERTICAL"
    size = "MEDIUM"
    mensaje = f"""
    Nombre: {nombre}
    Apellido paterno: {apellido_p}  
    Apellido materno: {apellido_m}
    Fecha de nacimiento: {fecha_nacimiento}
    Correo electronico: {email}
    """
    title = '¿Podrías confirmar los datos que capturaste son correctos?'
    suggestions = {"Sí, son correctos": "correctos", "No, son incorrectos": "incorrectos"}

    rich_card = rbm_service_udp.StandaloneCard(
            orientation, title, mensaje, suggestions, None, size
        )
    cluster = messages.MessageCluster().append_message(rich_card)
    cluster.send_to_msisdn(msisdn)



async def consume_queue(queue_name, handle_message):
    connection = await connect_with_retry()
    channel = await connection.channel()
    queue = await channel.declare_queue(queue_name, durable=True)

    logger.info(f"✅ Escuchando cola {queue_name}...")

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await handle_message(message.body)



async def main():
    await asyncio.gather(
        consume_queue("formulario_rcs", handle_message_formulario),
        consume_queue("rcs_messages", handle_message)
    )

asyncio.run(main())
