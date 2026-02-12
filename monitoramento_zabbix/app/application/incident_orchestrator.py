from datetime import datetime
from app.infrastructure.zabbix_service import ZabbixService
from app.infrastructure.google_sheets_service import GoogleSheetsService
from app.config.settings import Settings
from app.utils.logger import logger
from app.domain.incident_processor import IncidentProcessor
from app.utils.timer import log_tempo

class IncidentOrchestrator:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.zabbix = ZabbixService(settings=self.settings)
        self.sheets = GoogleSheetsService(settings=self.settings)
        self.processor = IncidentProcessor(
            allowed_groups=self.settings.allowed_groups,
            allowed_prefixes=self.settings.allowed_prefixes,
            dre_map=self.settings.dre_map,
            min_severity=self.settings.min_severity
        )

    # ----------------------------------

    def run(self) -> None:
        with log_tempo("Processamento total"):
            logger.info("🚀 Iniciando processamento de incidentes...")

        # 1️⃣ Coleta de incidentes do Zabbix
        with log_tempo("Busca no Zabbix"):
            problems = self.zabbix.get_active_problems()
            if not problems:
                logger.info("⚠ Nenhum incidente encontrado.")
                return

        logger.info(f"🔎 Incidentes encontrados: {len(problems)}")

        # 2️⃣ Mapeia eventos → hostid
        event_ids = [p["eventid"] for p in problems]
        events = self.zabbix.get_events(event_ids)
        event_host_map = {
            ev["eventid"]: ev["hosts"][0]["hostid"]
            for ev in events if ev.get("hosts")
        }

        # 3️⃣ Mapeia hosts → nome + grupos
        hostids = list(set(event_host_map.values()))
        hosts = self.zabbix.get_hosts(hostids)
        hosts_map = {
            h["hostid"]: {
                "name": h["name"],
                "groups": [g["name"] for g in h["groups"]]
            }
            for h in hosts
        }

        # 4️⃣ Busca incidentes existentes no Google Sheets
        existing_event_ids = self.sheets.get_all_event_ids()

        # 5️⃣ Processa e filtra incidentes
        
        with log_tempo("Processamento dos incidentes"):
            incidents_by_dre = self.processor.process(
                problems=problems,
                event_host_map=event_host_map,
                hosts_map=hosts_map,
                existing_event_ids=existing_event_ids
            )

        # 6️⃣ Envia para Google Sheets
        with log_tempo("Envio ao Google Sheets"):
            self.sheets.append_incidents(incidents_by_dre)

        logger.info("✅ Incidentes enviados com sucesso para o Google Sheets!")