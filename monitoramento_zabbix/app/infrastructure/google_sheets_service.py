import gspread
from gspread import Spreadsheet
from oauth2client.service_account import ServiceAccountCredentials
from app.domain.models import Incident
from app.config.settings import Settings
from app.utils.logger import logger
import sys



class GoogleSheetsService:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "service_account.json",
            scope
        )

        client: gspread.Client = gspread.authorize(creds)

        try:
            self.spreadsheet: Spreadsheet = client.open(settings.spreadsheet_name)
            logger.info("✅ Conectado ao Google Sheets")
        except Exception as e:
            logger.error(f"❌ Falha ao abrir a planilha: {e}")
            sys.exit(1)
    # ----------------------------------

     # ----------------------------------
    def get_all_event_ids(self) -> dict[str, set[str]]:
        """
        Retorna um dicionário {dre: set(event_ids)}
        para evitar duplicações na planilha.
        """
        eventids_por_dre: dict[str, set[str]] = {}

        for ws in self.spreadsheet.worksheets():
            dre = ws.title
            try:
                col_eventids = ws.col_values(1)[1:]  # ignora cabeçalho
                eventids_por_dre[dre] = set(col_eventids)
            except Exception:
                eventids_por_dre[dre] = set()

        return eventids_por_dre

    # ----------------------------------
    def append_incidents(
        self,
        incidents_by_dre: dict[str, list[Incident]]
    ) -> None:
        """
        Recebe {dre: [Incident, Incident, ...]} e adiciona em lote na planilha
        """
        for dre, incidents in incidents_by_dre.items():
            if not incidents:
                continue

            try:
                worksheet = self.spreadsheet.worksheet(dre)
            except gspread.exceptions.WorksheetNotFound:
                worksheet = self.spreadsheet.add_worksheet(
                    title=dre,
                    rows="1000",
                    cols="10"
                )
                worksheet.append_row([
                    "EVENT_ID",
                    "DATA",
                    "HOST",
                    "MUNICIPIO",
                    "DESCRICAO",
                    "SEVERIDADE",
                    "STATUS",          # nova coluna
                    "DATA_RESOLUCAO"   # nova coluna
                ])

            # converte Incident para lista de valores
            rows = []
            for incident in incidents:
                rows.append([
                    incident.event_id,
                    incident.data,
                    incident.host,
                    incident.municipio,
                    incident.descricao,
                    incident.severidade,
                    incident.status,
                    incident.data_resolucao
                ])

            worksheet.append_rows(rows, value_input_option="USER_ENTERED")

        logger.info(f"📄 Incidentes escritos no Google Sheets por DRE: {', '.join(incidents_by_dre.keys())}")