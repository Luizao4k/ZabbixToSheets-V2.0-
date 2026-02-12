import time
from contextlib import contextmanager
from app.utils.logger import logger


@contextmanager
def log_tempo(nome_operacao: str):
    inicio = time.perf_counter()

    yield  # roda o código dentro do bloco

    fim = time.perf_counter()
    logger.info(f"⏱ {nome_operacao} levou {fim - inicio:.2f}s")