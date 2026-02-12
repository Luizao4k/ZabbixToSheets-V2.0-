import os
import json
import unicodedata
from datetime import datetime
from dotenv import load_dotenv

import gspread
from pyzabbix import ZabbixAPI
from oauth2client.service_account import ServiceAccountCredentials

# =====================
# LOAD ENV
# =====================
load_dotenv()

ZABBIX_URL = os.getenv("ZABBIX_URL")
ZABBIX_TOKEN = os.getenv("ZABBIX_TOKEN")
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")
MIN_SEVERITY = int(os.getenv("MIN_SEVERITY", 0))


# =====================
# NORMALIZA TEXTO
# =====================
def normalizar(texto):
    if not texto:
        return ""
    texto = texto.upper().strip()
    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return texto

# =====================
# LOAD GRUPOS 
# =====================
with open("config_groups.json", "r", encoding="utf-8") as f:
    config = json.load(f)

ALLOWED_GROUPS = config.get("allowed_groups", [])
ALLOWED_GROUPS = [normalizar(g) for g in ALLOWED_GROUPS]

if not ALLOWED_GROUPS:
    raise SystemExit("❌ Nenhum grupo configurado")

# =====================
# LOAD HOST PREFIX
# =====================
with open("config_groups.json", "r", encoding="utf-8") as f:
    config_groups = json.load(f)

ALLOWED_PREFIXES = [normalizar(p) for p in config_groups.get("allowed_prefixes", [])]

if not ALLOWED_PREFIXES:
    raise SystemExit("❌ Nenhum prefixo configurado")

def host_permitido(hostname):
    nome = normalizar(hostname)
    return any(nome.startswith(p) for p in ALLOWED_PREFIXES)

# =====================
# LOAD DRE MAP
# =====================
with open("dre_map.json", "r", encoding="utf-8") as f:
    DRE_MAP = {normalizar(k): v for k, v in json.load(f).items()}

def detectar_dre(municipio):
    return DRE_MAP.get(normalizar(municipio), "DRE - OUTROS")

# =====================
# LOAD SEVERITY FILTER
# =====================
with open("config_severity.json", "r", encoding="utf-8") as f:
    config_severity = json.load(f)

MIN_SEVERITY = config_severity.get("min_severity", 0)

# =====================
# GOOGLE SHEETS
# =====================
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json", scope
)

gc = gspread.authorize(creds)
spreadsheet = gc.open(SPREADSHEET_NAME)

# =====================
# ZABBIX
# =====================
zapi = ZabbixAPI(ZABBIX_URL)
zapi.login(api_token=ZABBIX_TOKEN)

print("✅ Conectado ao Zabbix")

# =====================
# BUSCA INCIDENTES ATIVOS
# =====================
problems = zapi.problem.get(
    recent=True,
    output=["eventid", "name", "severity", "clock"],
    sortfield="eventid",
    sortorder="DESC"
)

print(f"🔎 Incidentes ativos encontrados: {len(problems)}")

event_ids = [p["eventid"] for p in problems]

if not event_ids:
    raise SystemExit("⚠ Nenhum incidente")

# =====================
# EVENT → HOSTID
# =====================
events = zapi.event.get(
    eventids=event_ids,
    output=["eventid"],
    selectHosts="extend"
)

event_hostid = {}

for ev in events:
    if not ev.get("hosts"):
        continue

    host = ev["hosts"][0]  # Zabbix sempre retorna lista
    event_hostid[ev["eventid"]] = host["hostid"]

hostids = list(set(event_hostid.values()))

# =====================
# HOST → NAME + GROUPS
# =====================
hosts = zapi.host.get(
    hostids=hostids,
    output=["name"],
    selectGroups=["name"]
)

hosts_map = {
    h["hostid"]: {
        "name": h["name"],
        "groups": [normalizar(g["name"]) for g in h["groups"]]
    }
    for h in hosts
}

# =====================
# CARREGA EVENT_IDS EXISTENTES DAS ABAS
# =====================
eventids_por_dre = {}

for ws in spreadsheet.worksheets():
    dre = ws.title

    try:
        col_eventids = ws.col_values(1)[1:]  # ignora cabeçalho
        eventids_por_dre[dre] = set(col_eventids)
    except Exception:
        eventids_por_dre[dre] = set()

# =====================
# PROCESSA INCIDENTES
# =====================
# cache local para evitar reler a aba várias vezes
linhas_por_dre = {}

for p in problems:
    eventid = str(p["eventid"])
    severidade = int(p["severity"])

    if severidade < MIN_SEVERITY:
        continue

    hostid = event_hostid.get(eventid)
    if not hostid or hostid not in hosts_map:
        continue

    host_info = hosts_map[hostid]
    host = host_info["name"]
    grupos = host_info["groups"]

    # filtro grupo
    if not any(g in ALLOWED_GROUPS for g in grupos):
        continue

    # filtro host
    if not host_permitido(host):
        continue

    municipio = host.split("-")[-1].strip()
    dre = detectar_dre(municipio)

    novos_incidentes = 0

    #  garante que a DRE exista no cache
    eventids_por_dre.setdefault(dre, set())
    if eventid in eventids_por_dre[dre]:
        continue
    #evita a duplicação dentro do google sheets
    eventids_por_dre[dre].add(eventid)
    novos_incidentes += 1

    data = datetime.fromtimestamp(int(p["clock"])).strftime("%d/%m/%Y %H:%M")

    linha = [
        eventid,
        data,
        host,
        municipio,
        p["name"],
        severidade
    ]

    linhas_por_dre.setdefault(dre, []).append(linha)
    eventids_por_dre[dre].add(eventid)

# =====================
# ESCRITA EM LOTE
# =====================
for dre, linhas in linhas_por_dre.items():
    if not linhas:
        continue

    try:
        worksheet = spreadsheet.worksheet(dre)
    except gspread.exceptions.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
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
            "SEVERIDADE"
        ])

    worksheet.append_rows(
        linhas,
        value_input_option="USER_ENTERED"
    )

print("🚀 Incidentes enviados com sucesso (escrita em lote por DRE)")
print("=" * 50)
print("📈 RESUMO DA EXECUÇÃO")
print(f"Total coletado do Zabbix: {len(problems)}")
print(f"Novos adicionados: {novos_incidentes}")
print(f"Ignorados: {len(problems) - novos_incidentes}")
print("=" * 50)