import sys
from unittest.mock import MagicMock
import pytest

# Bloqueia imports externos do Google Sheets
sys.modules["oauth2client"] = MagicMock()
sys.modules["oauth2client.service_account"] = MagicMock()

from app.infrastructure.zabbix_service import ZabbixService
from app.infrastructure.google_sheets_service import GoogleSheetsService
from app.application.incident_orchestrator import IncidentOrchestrator
from app.config.settings import Settings
from app.domain.models import Incident


@pytest.fixture
def fake_settings(monkeypatch):
    # Define variáveis de ambiente necessárias
    monkeypatch.setenv("ZABBIX_URL", "fake_url")
    monkeypatch.setenv("ZABBIX_TOKEN", "fake_token")
    monkeypatch.setenv("SPREADSHEET_NAME", "fake_sheet")
    monkeypatch.setenv("GOOGLE_CREDS", "fake.json")
    return Settings()


@pytest.fixture
def mock_zabbix(monkeypatch):
    mock_service = MagicMock(spec=ZabbixService)

    mock_service.get_active_problems.return_value = [
        {"eventid": "1", "name": "CPU", "severity": 3, "clock": "1", "value": "0"},
        {"eventid": "2", "name": "MEM", "severity": 4, "clock": "2", "value": "1", "r_clock": "2"}
    ]

    mock_service.get_events.return_value = [
        {"eventid": "1", "hosts": [{"hostid": "h1"}]},
        {"eventid": "2", "hosts": [{"hostid": "h2"}]},
    ]

    mock_service.get_hosts.return_value = [
        {"hostid": "h1", "name": "HOST-A-MUNI1", "groups": [{"name": "GRUPO_A"}]},
        {"hostid": "h2", "name": "HOST-B-MUNI2", "groups": [{"name": "GRUPO_A"}]},
    ]

    monkeypatch.setattr(
        "app.infrastructure.zabbix_service.ZabbixService",
        lambda settings: mock_service
    )
    return mock_service


@pytest.fixture
def mock_sheets(monkeypatch):
    mock_service = MagicMock(spec=GoogleSheetsService)
    mock_service.get_all_event_ids.return_value = {}

    monkeypatch.setattr(
        "app.infrastructure.google_sheets_service.GoogleSheetsService",
        lambda settings: mock_service
    )
    return mock_service


def test_orchestrator_end_to_end(mock_zabbix, mock_sheets, fake_settings):
    orchestrator = IncidentOrchestrator(settings=fake_settings)
    orchestrator.run()

    mock_zabbix.get_active_problems.assert_called_once()
    mock_zabbix.get_events.assert_called_once()
    mock_zabbix.get_hosts.assert_called_once()

    assert mock_sheets.append_incidents.called
    incidents_by_dre = mock_sheets.append_incidents.call_args[0][0]

    # evento deve estar no dicionário
    assert any(isinstance(i, Incident) for dre in incidents_by_dre.values() for i in dre)
