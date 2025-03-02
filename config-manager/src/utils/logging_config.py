import logging

def setup_logging():
    # Configurar o logging no nível raiz
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Criar um logger específico para nossa aplicação
    logger = logging.getLogger('config_manager')
    logger.setLevel(logging.DEBUG)

    # Criar um handler para console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    # Definir o formato
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)

    # Adicionar o handler ao logger
    logger.addHandler(console_handler)

    return logger