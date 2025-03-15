import logging
import coloredlogs

# Definir o formato com espaçamento alinhado
log_format = (
    "%(asctime)s | %(levelname)-8s | %(filename)s:%(funcName)s:%(lineno)d | %(message)s"
)

# Definir as cores para cada nível de log
level_styles = {
    'debug': {'color': 'blue'},
    'info': {'color': 'green'},
    'warning': {'color': 'yellow'},
    'error': {'color': 'red'},
    'critical': {'color': 'magenta'}
}

# Instalar coloredlogs com as configurações personalizadas
coloredlogs.install(
    level='INFO',
    fmt=log_format,
    level_styles=level_styles,
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)