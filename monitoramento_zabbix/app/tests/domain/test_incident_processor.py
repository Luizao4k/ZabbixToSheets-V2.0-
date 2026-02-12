import pytest
from datetime import datetime
from app.domain.incident_processor import IncidentProcessor
from app.domain.models import Incident


@pytest.fixture
def processor():
    allowed_groups = ["GRUPO_A", "GRUPO_B"]
    allowed_prefixes = ["HOST1", "SRV"]
    dre_map = {"MUNICIPIO1": "DRE1", "MUNICIPIO2": "DRE2"}
    min_severity = 2

    return IncidentProcessor(
        allowed_groups=allowed_groups,
        allowed_prefixes=allowed_prefixes,
        dre_map=dre_map,
        min_severity=min_severity
    )


@pytest.fixture
def base_data():
    now_ts = int(datetime.now().timestamp())
    problems = [
        {"eventid": "1", "name": "CPU alta", "severity": 3, "clock": now_ts},
        {"eventid": "2", "name": "Memória baixa", "severity": 1, "clock": now_ts},
        {"eventid": "3", "name": "Disco cheio", "severity": 4, "clock": now_ts},
        {"eventid": "4", "name": "Rede lenta", "severity": 3, "clock": now_ts},
    ]

    event_host_map = {
        "1": "host1_id",
        "2": "host2_id",
        "3": "host3_id",
        "4": "host4_id"
    }

    hosts_map = {
        "host1_id": {"name": "HOST1-MUNICIPIO1", "groups": ["GRUPO_A"]},
        "host2_id": {"name": "HOST2-MUNICIPIO2", "groups": ["GRUPO_B"]},
        "host3_id": {"name": "SRV-MUNICIPIO2", "groups": ["GRUPO_X"]},
        "host4_id": {"name": "SRV-MUNICIPIO3", "groups": ["GRUPO_B"]},
    }

    existing_event_ids = {}

    return problems, event_host_map, hosts_map, existing_event_ids


def test_incident_processor_basic(processor, base_data):
    problems, event_host_map, hosts_map, existing_event_ids = base_data

    incidents_by_dre = processor.process(
        problems,
        event_host_map,
        hosts_map,
        existing_event_ids
    )

    assert "DRE1" in incidents_by_dre
    assert "DRE - OUTROS" in incidents_by_dre
    assert len(incidents_by_dre["DRE1"]) == 1
    assert len(incidents_by_dre["DRE - OUTROS"]) == 1

    incident1 = incidents_by_dre["DRE1"][0]
    incident2 = incidents_by_dre["DRE - OUTROS"][0]

    assert isinstance(incident1, Incident)
    assert incident1.event_id == "1"
    assert incident1.host == "HOST1-MUNICIPIO1"
    assert incident1.dre == "DRE1"

    assert incident2.event_id == "4"
    assert incident2.dre == "DRE - OUTROS"


def test_min_severity_filter(processor, base_data):
    problems, event_host_map, hosts_map, existing_event_ids = base_data

    incidents_by_dre = processor.process(
        [problems[1]], event_host_map, hosts_map, existing_event_ids
    )
    assert incidents_by_dre == {}


def test_group_filter(processor, base_data):
    problems, event_host_map, hosts_map, existing_event_ids = base_data

    incidents_by_dre = processor.process(
        [problems[2]], event_host_map, hosts_map, existing_event_ids
    )
    assert incidents_by_dre == {}


def test_prefix_filter(processor, base_data):
    problems, event_host_map, hosts_map, existing_event_ids = base_data

    incidents_by_dre = processor.process(
        [problems[1]], event_host_map, hosts_map, existing_event_ids
    )
    assert incidents_by_dre == {}


def test_duplicate_event(processor, base_data):
    problems, event_host_map, hosts_map, existing_event_ids = base_data

    # Processa evento 1 pela primeira vez
    processor.process([problems[0]], event_host_map, hosts_map, existing_event_ids)
    # Processa novamente -> deve ser ignorado
    incidents_by_dre = processor.process([problems[0]], event_host_map, hosts_map, existing_event_ids)
    assert incidents_by_dre == {}
