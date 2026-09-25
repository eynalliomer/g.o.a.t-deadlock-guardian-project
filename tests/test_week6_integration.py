import json

from src.process import Process
from src.resource import Resource
from src.bankers import system_state, safety_of, evaluate_acquire
from src.scenario_loader import load_scenario
from src.run_scenario import run_scenario_step_by_step


def _iki_process_iki_kaynak():
    p1 = Process("P1", max_claim={"R1": 1, "R2": 1})
    p2 = Process("P2", max_claim={"R1": 1, "R2": 1})
    return [p1, p2], [Resource("R1"), Resource("R2")]


def test_max_claim_varsayilan_olarak_yok():
    assert Process("P1").max_claim is None


def test_max_bildirmeyen_process_varsa_bankers_calismaz():
    processes = [Process("P1", max_claim={"R1": 1}), Process("P2")]
    assert system_state(processes, [Resource("R1")]) is None
    assert safety_of(processes, [Resource("R1")]) is None


def test_sistem_durumu_process_ve_kaynaklardan_kurulur():
    (p1, p2), (r1, r2) = _iki_process_iki_kaynak()
    r1.acquire(p1)
    available, maximum, allocation = system_state([p1, p2], [r1, r2])
    assert available == {"R1": 0, "R2": 1}
    assert maximum["P1"] == {"R1": 1, "R2": 1}
    assert allocation["P1"] == {"R1": 1}
    assert allocation["P2"] == {}


def test_klasik_senaryoda_ikinci_adimda_sistem_guvensiz_olur():
    (p1, p2), (r1, r2) = _iki_process_iki_kaynak()

    assert safety_of([p1, p2], [r1, r2]) == (True, ["P1", "P2"])
    r1.acquire(p1)
    assert safety_of([p1, p2], [r1, r2])[0] is True

    # P2, R2'yi almadan ÖNCE değerlendirme: bu istek sistemi güvensiz yapar.
    assert evaluate_acquire(p2, r2, 1, [p1, p2], [r1, r2]).status == "UNSAFE"
    r2.acquire(p2)
    assert safety_of([p1, p2], [r1, r2]) == (False, [])


def test_senaryodaki_processes_bolumu_max_bildirir(tmp_path):
    scenario = {
        "resources": [{"name": "R1", "total_instances": 2}],
        "processes": [
            {"name": "P1", "max": {"R1": 2}},
            {"name": "P2", "max": {"R1": 1}},
        ],
        "events": [{"action": "acquire", "process": "P1", "resource": "R1"}],
    }
    path = tmp_path / "s.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")

    result = load_scenario(str(path))
    assert result["processes"]["P1"].max_claim == {"R1": 2}
    assert "P2" in result["processes"]  # olaylarda geçmese de baştan sistemde


def test_adim_adim_calistirmada_guvensiz_istek_uyarisi_uretilir():
    result = run_scenario_step_by_step("scenarios/hafta6_guvensiz_durum.json")
    html = "".join(result["steps_html"])
    assert "GÜVENSİZ" in html
    assert "Bu istek sistemi güvensiz duruma soktu" in html
    assert result["safety"] == (False, [])


def test_processes_bolumu_olmayan_eski_senaryolar_calismaya_devam_eder():
    result = run_scenario_step_by_step("scenarios/hafta4_deadlock.json")
    assert result["safety"] is None
    assert result["report"].has_deadlock
