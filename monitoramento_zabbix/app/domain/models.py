from dataclasses import dataclass
from datetime import datetime

@dataclass
class Incident:
    event_id: str
    data: datetime
    host: str
    municipio: str
    descricao: str
    severidade: int
    dre: str
    status: int = 0
    data_resolucao: str = ""