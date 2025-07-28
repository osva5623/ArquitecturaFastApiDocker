import asyncio, json, aio_pika
from aio_pika import connect_robust
import logging
import base64

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
            mensaje = """Tu solicitud fue recibida correctamente y estamos trabajando en activarla.
        📦 Detalles del plan:

        6 GB extra para navegar, ver videos y usar tus apps favoritas

        Vigencia: [X días/semanas] a partir del momento de activación

        Compatible con tu plan actual, sin cambios en tu número ni configuraciones

        🕒 ¿Cuándo se activará?
        La activación se hará en un plazo máximo de [15 minutos / 1 hora]. Te enviaremos una confirmación cuando esté lista para que empieces a usar tus nuevos datos.

        🚀 ¡Gracias por seguir con nosotros! Si tienes dudas, aquí estamos para ayudarte."""

            mensajeRbm = rbm_service_udp.rbm_message(mensaje)
            cluster = messages.MessageCluster().append_message(mensajeRbm)


            cluster.send_to_msisdn(msisdn)

            url=f"https://formularios-master-ackcbg.laravel.cloud/formularios/{formId}"
            suggestions = [messages.OpenUrlAction(
            'Captura de datos',
            'reply:datos_capturados',
            url)]
            title = 'Informacion de tu cuenta'
            description = 'Por favor, captura los datos de tu cuenta para completar la migración.'

            rich_card = messages.StandaloneCard('VERTICAL',
                                        title,
                                        description,
                                        suggestions,
                                        None,
                                        None,
                                        None,
                                        'MEDIUM')
            cluster = messages.MessageCluster().append_message(rich_card)
            cluster.send_to_msisdn(msisdn)
        elif postback == "otra_ocasion":
            pass
        elif postback == "correctos":
            mensaje = """ 🎉 ¡Gracias por completar el formulario!
                        ✅ Hemos recibido tus datos correctamente y están siendo validados.
                        🕒 En breve recibirás una confirmación con los siguientes pasos.
                        📲 Si tienes dudas, no dudes en responder este mensaje. """
            mensajeRbm = rbm_service_udp.rbm_message(mensaje)
            cluster = messages.MessageCluster().append_message(mensajeRbm)
            cluster.send_to_msisdn(msisdn)

    elif "TEXT" == tipo_mensaje:
        orientation = "VERTICAL"
        title = "Tienes 6gb esperandote 🔥🚀"
        description = """🚀 Actívala ahora y empieza a disfrutar de más velocidad, más libertad y más conexión donde quiera que estés.
    No dejes pasar esta oportunidad, los GB no van a esperar para siempre 😉

    👉 Toca aquí y aprovecha esta promo antes de que se acabe."""
        image_url = "https://tienda.movistar.com.mx/media/wysiwyg/Home2025/rotativofijo1/1.Banner_Rotativo_FIJO_MIGRA.jpg"
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
    nombre = payload["name"]
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
    Fecha de nacimiento: {fecha_nacimiento}.
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
