from src.process import Process, ProcessState
from src.resource import Resource
from src.detection import detect_deadlock
from src.bankers import system_state
from src.recovery import option_cost, recovery_options, apply_option, recover, terminate, preempt
from src.run_scenario import run_scenario_step_by_step
from src.risk import RiskLevel


def _klasik_deadlock(p1_priority=1, p2_priority=1):
    p1 = Process("P1", priority=p1_priority)
    p2 = Process("P2", priority=p2_priority)
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)
    return [p1, p2], [r1, r2]


def test_process_varsayilanlari():
    p = Process("P1")
    assert p.priority == 1
    assert p.victim_count == 0


def test_maliyet_formulu():
    p = Process("P1", priority=2)
    p.victim_count = 1
    # öncelik×10 − serbest bırakılan×2 + kurban sayısı×5 = 20 − 4 + 5
    assert option_cost(p, freed_units=2) == 21


def test_deadlock_yoksa_secenek_yok():
    p1 = Process("P1")
    r1 = Resource("R1")
    r1.acquire(p1)
    assert recovery_options([p1], [r1]) == []


def test_klasik_deadlockta_dort_secenek_ve_en_ucuzu_once():
    processes, resources = _klasik_deadlock()
    options = recovery_options(processes, resources)
    kinds = sorted((o.kind, o.process.name, o.resource.name if o.resource else "") for o in options)
    assert kinds == [
        ("preempt", "P1", "R1"),
        ("preempt", "P2", "R2"),
        ("terminate", "P1", ""),
        ("terminate", "P2", ""),
    ]
    best = options[0]
    assert best.cost == 8  # 1×10 − 1×2 + 0
    assert best.kind == "preempt"  # eşit maliyette geri alma tercih edilir (process yaşamaya devam eder)


def test_oncelik_yuksek_process_korunur():
    processes, resources = _klasik_deadlock(p1_priority=5)
    assert recovery_options(processes, resources)[0].process.name == "P2"


def test_sonlandirma_kaynaklari_birakir_ve_kuyruklardan_cikarir():
    (p1, p2), (r1, r2) = _klasik_deadlock()
    terminate(p1, [r1, r2])

    assert p1.state == ProcessState.TERMINATED
    assert p1.held_resources == {}
    assert all(p is not p1 for p, _ in r2.waiting_queue)
    assert r1.allocation == {p2: 1}  # R1, bekleyen P2'ye geçti
    assert p2.state == ProcessState.READY
    assert detect_deadlock([r1, r2]) == []


def test_geri_alma_kaynagi_bekleyene_verir_ve_kurban_sayisini_artirir():
    (p1, p2), (r1, r2) = _klasik_deadlock()
    preempt(p1, r1, [r1, r2])

    assert "R1" not in p1.held_resources
    assert r1.allocation == {p2: 1}
    assert p1.victim_count == 1
    assert p1.state == ProcessState.WAITING  # hâlâ R2'yi bekliyor
    assert detect_deadlock([r1, r2]) == []


def test_kurban_sayisi_maliyeti_artirir_starvation_onlenir():
    processes, resources = _klasik_deadlock()
    processes[0].victim_count = 3  # P1 daha önce 3 kez kurban seçilmiş
    assert recovery_options(processes, resources)[0].process.name == "P2"


def test_recover_deadlocku_cozer_ve_uygulananlari_doner():
    processes, resources = _klasik_deadlock()
    applied = recover(processes, resources)
    assert len(applied) == 1
    assert detect_deadlock(resources) == []


def test_uc_processli_dongu_recover_ile_cozulur():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1, r2, r3 = Resource("R1"), Resource("R2"), Resource("R3")
    r1.acquire(p1)
    r2.acquire(p2)
    r3.acquire(p3)
    r2.acquire(p1)
    r3.acquire(p2)
    r1.acquire(p3)

    recover([p1, p2, p3], [r1, r2, r3])
    assert detect_deadlock([r1, r2, r3]) == []


def test_sonlandirilan_process_bankers_hesabina_katilmaz():
    p1 = Process("P1", max_claim={"R1": 1})
    p2 = Process("P2", max_claim={"R1": 1})
    r1 = Resource("R1")
    r1.acquire(p1)
    terminate(p1, [r1])

    available, maximum, allocation = system_state([p1, p2], [r1])
    assert "P1" not in maximum
    assert available == {"R1": 1}


def test_apply_option_secenegi_uygular():
    processes, resources = _klasik_deadlock()
    option = recovery_options(processes, resources)[0]
    apply_option(option, resources)
    assert detect_deadlock(resources) == []


def test_senaryoda_recover_sonrasi_risk_duser():
    result = run_scenario_step_by_step("scenarios/hafta8_recovery.json")
    levels = [risk.level for risk in result["risk_timeline"]]
    assert RiskLevel.CRITICAL in levels
    assert levels[-1] < RiskLevel.HIGH  # kurtarmadan sonra sistem tekrar güvenli
    assert result["report"].has_deadlock is False


def _senaryo_yaz(tmp_path, recovery_event):
    import json
    scenario = {
        "resources": [{"name": "R1"}, {"name": "R2"}],
        "events": [
            {"action": "acquire", "process": "P1", "resource": "R1"},
            {"action": "acquire", "process": "P2", "resource": "R2"},
            {"action": "acquire", "process": "P1", "resource": "R2"},
            {"action": "acquire", "process": "P2", "resource": "R1"},
            recovery_event,
        ],
    }
    path = tmp_path / "s.json"
    path.write_text(json.dumps(scenario), encoding="utf-8")
    return str(path)


def test_senaryoda_elle_sonlandirma(tmp_path):
    result = run_scenario_step_by_step(_senaryo_yaz(tmp_path, {"action": "terminate", "process": "P2"}))
    assert result["processes"]["P2"].state == ProcessState.TERMINATED
    assert result["report"].has_deadlock is False
    assert any(e["type"] == "RECOVERY" for e in result["event_log"].events)


def test_sonlandirilan_process_yeni_olay_alamaz(tmp_path):
    import json, pytest
    path = _senaryo_yaz(tmp_path, {"action": "terminate", "process": "P2"})
    data = json.loads(open(path, encoding="utf-8").read())
    data["events"].append({"action": "acquire", "process": "P2", "resource": "R1"})
    open(path, "w", encoding="utf-8").write(json.dumps(data))
    with pytest.raises(ValueError):
        run_scenario_step_by_step(path)
