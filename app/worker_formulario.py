
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
   
   pass


async def main():
    logger.info("✅ Iniciando worker formulario de RabbitMQ...")

    connection = await connect_with_retry()
    channel = await connection.channel()
    queue = await channel.declare_queue("formulario_rcs", durable=True)

    async with queue.iterator() as queue_iter:
        async for message in queue_iter:
            async with message.process():
                await handle_message(message.body)


asyncio.run(main())