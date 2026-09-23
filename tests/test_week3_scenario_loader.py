from src.scenario_loader import load_scenario
from src.process import ProcessState


def test_hafta2_senaryosu_dogru_calisir():
    result = load_scenario("scenarios/hafta2_temel_akis.json")

    p1 = result["processes"]["P1"]
    p2 = result["processes"]["P2"]
    r1 = result["resources"]["R1"]

    assert p1.state == ProcessState.READY
    assert p2.state == ProcessState.READY
    assert "R1" not in p1.held_resources
    assert p2.held_resources["R1"] == 1
    assert r1.allocation[p2] == 1


def test_hafta2_senaryosu_olay_kaydi_dogru_sirada():
    result = load_scenario("scenarios/hafta2_temel_akis.json")
    types = [e["type"] for e in result["event_log"].events]

    assert types == ["ACQUIRED", "WAITING", "RELEASED", "ACQUIRED"]


def test_cok_ornekli_senaryo_bekleyen_istegi_karsilar():
    result = load_scenario("scenarios/hafta3_cok_ornekli.json")

    p1 = result["processes"]["P1"]
    p2 = result["processes"]["P2"]
    r1 = result["resources"]["R1"]

    assert p1.held_resources["R1"] == 1
    assert p2.held_resources["R1"] == 2
    assert p2.state == ProcessState.READY
    assert r1.waiting_queue == []
