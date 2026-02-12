from pyzabbix.api import ZabbixAPI
from app.config.settings import Settings
import sys
from pyzabbix.api import ZabbixAPIException
from app.utils.logger import logger


class ZabbixService:

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

        try:
            self.zapi: ZabbixAPI = ZabbixAPI(settings.zabbix_url)
            self.zapi.login(api_token=settings.zabbix_token)
            logger.info(f"✅ Conectado ao Zabbix: {settings.zabbix_url}")

        except ZabbixAPIException as e:
            logger.error(f"❌ Erro de autenticação/API no Zabbix: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"❌ Erro de conexão (Rede/Proxy): {e}")
            sys.exit(1)
    # -----------------------------

    def get_active_problems(self) -> list[dict]:
        problems = self.zapi.problem.get(
            recent=True,
            output=["eventid", "name", "severity", "clock", "value"],
            sortfield="eventid",
            sortorder="DESC"
        )

        return problems

    # -----------------------------

    def get_events(self, event_ids: list[str]) -> list[dict]:

        if not event_ids:
            return []

        return self.zapi.event.get(
            eventids=event_ids,
            output=["eventid"],
            selectHosts="extend"
        )

    # -----------------------------

    def get_hosts(self, hostids: list[str]) -> list[dict]:

        if not hostids:
            return []

        return self.zapi.host.get(
            hostids=hostids,
            output=["name"],
            selectGroups=["name"]
        )
