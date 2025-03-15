import asyncio
from .services import PubSubClient
from .utils import logger
from .services import ProcessHandler


async def start_pubsub_listener():
    pubsub_client = PubSubClient(ProcessHandler())
    await asyncio.to_thread(pubsub_client.subscribe_messages)



async def startup_event():
    """
    Função de inicialização que será registrada como evento no FastAPI.
    Esta função é responsável por iniciar o listener do Pub/Sub.
    """
    logger.info("Iniciando o servidor FastAPI e Pub/Sub listener...")
    asyncio.create_task(start_pubsub_listener())

