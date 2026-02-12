import logging
from logging.handlers import RotatingFileHandler
import sys
from pathlib import Path

# Cria diretório de logs se não existir
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Cria logger global
logger = logging.getLogger("monitoramento_zabbix")
logger.setLevel(logging.INFO)  # INFO padrão, DEBUG para mais detalhe

formatter = logging.Formatter(
    "%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%d/%m/%Y %H:%M:%S"
)

# Handler console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)
logger.addHandler(console_handler)

# Handler arquivo rotativo
file_handler = RotatingFileHandler(
    log_dir / "monitoramento.log",
    maxBytes=5 * 1024 * 1024,
    backupCount=3,
    encoding="utf-8"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
