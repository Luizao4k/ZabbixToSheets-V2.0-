    from datetime import datetime
    from typing import List, Dict, Set
    from app.domain.models import Incident
    from app.utils.logger import logger
    import unicodedata


    def normalizar(texto: str) -> str:
        """
        Normaliza um texto para comparação:
        - Maiúsculas
        - Remove acentos
        - Remove espaços extras
        """
        if not texto:
            return ""
        texto = texto.upper().strip()
        texto = "".join(c for c in unicodedata.normalize("NFD", texto)
                        if unicodedata.category(c) != "Mn")
        return texto


    class IncidentProcessor:
        def __init__(
            self,
            allowed_groups: List[str],
            allowed_prefixes: List[str],
            dre_map: Dict[str, str],
            min_severity: int
        ):
            self.allowed_groups = [normalizar(g) for g in allowed_groups]
            self.allowed_prefixes = [normalizar(p) for p in allowed_prefixes]
            self.dre_map = {normalizar(k): v for k, v in dre_map.items()}
            self.min_severity = min_severity

        def process(
            self,
            problems: List[dict],
            event_host_map: Dict[str, str],
            hosts_map: Dict[str, dict],
            existing_event_ids: Dict[str, Set[str]],
        ) -> Dict[str, List[Incident]]:

            incidents_by_dre: Dict[str, List[Incident]] = {}
            novos_incidentes = 0

            for p in problems:
                eventid = str(p["eventid"])
                severity = int(p["severity"])

                # filtro severidade
                if severity < self.min_severity:
                    logger.debug(f"Ignorado {eventid}: severidade {severity} < {self.min_severity}")
                    continue

                hostid = event_host_map.get(eventid)
                if not hostid or hostid not in hosts_map:
                    logger.debug(f"Ignorado {eventid}: host não encontrado")
                    continue

                host_info = hosts_map[hostid]
                host = host_info["name"]
                grupos = [normalizar(g) for g in host_info["groups"]]

                # filtro grupo
                if not any(g in self.allowed_groups for g in grupos):
                    logger.debug(f"Ignorado {eventid}: grupo(s) {grupos} não permitido(s)")
                    continue

                # filtro prefixo
                host_upper = normalizar(host)
                if not any(host_upper.startswith(prefix) for prefix in self.allowed_prefixes):
                    logger.debug(f"Ignorado {eventid}: prefixo {host_upper} não permitido")
                    continue

                municipio = normalizar(host.split("-")[-1].strip())
                dre = self.dre_map.get(municipio, "DRE - OUTROS")

                # evita duplicação
                event_ids = existing_event_ids.setdefault(dre, set())
                if eventid in event_ids:
                    logger.debug(f"Ignorado {eventid}: já existe na DRE {dre}")
                    continue
                event_ids.add(eventid)
                novos_incidentes += 1

                # Datas
                data = datetime.fromtimestamp(int(p["clock"])).strftime("%d/%m/%Y")
                status = int(p.get("value", 0))  # 0 pendente, 1 resolvido
                data_resolucao = ""

                if status == 1:
                    data_resolucao = datetime.fromtimestamp(
                        int(p.get("r_clock", p["clock"]))
                    ).strftime("%d/%m/%Y")
                    logger.info(f"Evento {eventid} resolvido em {data_resolucao}")

                incident = Incident(
                    event_id=eventid,
                    data=data,
                    host=host,
                    municipio=municipio,
                    descricao=p["name"],
                    severidade=severity,
                    dre=dre,
                    status=status,
                    data_resolucao=data_resolucao
                )

                incidents_by_dre.setdefault(dre, []).append(incident)

            total_incidentes = sum(len(v) for v in incidents_by_dre.values())
            logger.info(f"📈 Total de incidentes processados: {total_incidentes}")
            logger.info(f"📈 Novos incidentes adicionados: {novos_incidentes}")
            return incidents_by_dre
