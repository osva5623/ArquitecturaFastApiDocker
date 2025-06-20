import asyncio, json,aio_pika
from aio_pika import connect_robust
import logging

from rcs_business_messaging import rbm_service
from rcs_business_messaging import messages
from rcs_business_messaging import agent_config

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

AGENT_ID = "prueba_ujyndkxw_agent"
RABBITMQ_URL = "amqp://user:pass@rabbitmq/"
MAX_RETRIES = 10
RETRY_SECONDS = 3

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
    raise RuntimeError("🚫 No se pudo conectar a RabbitMQ después de varios intentos  s")

async def handle_message(body: bytes):
    payload = json.loads(body.decode())
    logger.info(f"payload {payload}")
    
    rbm_service.init(AGENT_ID)
    msisdn = payload["senderPhoneNumber"]
    message_id = payload['messageId']

    print(f"🔔 Procesando mensaje de: {payload.get('senderPhoneNumber')}")
    logger.info(f"Mensaje recibido de {msisdn}")

    if "suggestionResponse" in payload:
        postback = payload["suggestionResponse"].get("postbackData", "").lower()

        if postback == "acepto":
                message = messages.TextMessage("""Tu solicitud fue recibida correctamente y estamos trabajando en activarla.
📦 Detalles del plan:

6 GB extra para navegar, ver videos y usar tus apps favoritas

Vigencia: [X días/semanas] a partir del momento de activación

Compatible con tu plan actual, sin cambios en tu número ni configuraciones

🕒 ¿Cuándo se activará?
La activación se hará en un plazo máximo de [15 minutos / 1 hora]. Te enviaremos una confirmación cuando esté lista para que empieces a usar tus nuevos datos.

🚀 ¡Gracias por seguir con nosotros! Si tienes dudas, aquí estamos para ayudarte.""")
        elif postback == "otra_ocasion":
                message = messages.TextMessage("""¡Entendido! Aunque esta vez dijiste que no, tus 8 GB seguirán esperándote por un tiempo limitado.
🎯 Si cambias de opinión, solo tienes que regresar y activarlos.
Queremos que tengas siempre la mejor experiencia… ¡y con más datos, es mucho mejor!""")
        else:
                message = messages.TextMessage("No entendí tu respuesta. ¿Podrías intentarlo de nuevo?")

        messages.MessageCluster().append_message(message).send_to_msisdn(msisdn)
        logger.info(f"✅ Respuesta enviada para postbackData '{postback}' a {msisdn}")
    else:
        suggestions = [
        messages.SuggestedReply('Acepto migrarme', 'acepto'),
        messages.SuggestedReply('En otra ocacion', 'otra_ocasion'),
        ]

        # Image to be displayed by the card
        image_url = 'https://tienda.movistar.com.mx/media/wysiwyg/Home2025/rotativofijo1/1.Banner_Rotativo_FIJO_MIGRA.jpg';
        rich_card = messages.StandaloneCard('VERTICAL',
                                        'Tienes 6gb esperandote 🔥🚀',
                                        """🚀 Actívala ahora y empieza a disfrutar de más velocidad, más libertad y más conexión donde quiera que estés.
    No dejes pasar esta oportunidad, los GB no van a esperar para siempre 😉

    👉 Toca aquí y aprovecha esta promo antes de que se acabe.
                                        """,
                                        suggestions,
                                        image_url,
                                        None,
                                        None,
                                        'MEDIUM')

        cluster = messages.MessageCluster().append_message(rich_card)
        cluster.send_to_msisdn(msisdn)
        # Aquí pones tu lógica con rbm_service, etc.

        logger.info("✅ Mensaje enviado")
        logger.info(f"📦 Recibido mensaje RabbitMQ con tag {message_id}")



async def main():
    logger.info("✅ Iniciando worker de RabbitMQ...")

    connection = await connect_with_retry()
    channel = await connection.channel()
    queue = await channel.declare_queue("rcs_messages", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await handle_message(message.body)


asyncio.run(main())
