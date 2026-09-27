"""Hafta 10: sistem testleri (el kitabı 10.2). Her senaryo baştan sona motorla oynatılır.

Her test üç parçalı: hazırlık (senaryo dosyası) → eylem (oynatma) → beklenen sonuç.
"""
from src.detection import analyze, build_rag, find_cycles
from src.engine import Simulation
from src.process import Process
from src.resource import Resource
from src.risk import RiskLevel


def _play(name, stop_before=None):
    """Senaryoyu oynatır; stop_before verilirse o türden ilk olaydan önce durur."""
    sim = Simulation.from_file(f"scenarios/{name}")
    while (event := sim.next_event()) is not None and event["action"] != stop_before:
        sim.step()
    return sim


def _levels(sim):
    return [sim.initial_risk.level] + [s.risk.level for s in sim.history]


def test_1_normal_calisma_deadlock_yok_risk_hep_low():
    sim = _play("hafta10_normal_calisma.json")
    assert set(_levels(sim)) == {RiskLevel.LOW}
    assert all(s.decision is None or s.decision.status == "SAFE" for s in sim.history)
    assert sim.analysis().report.has_deadlock is False


def test_2_tek_deadlock_p1_p2_critical():
    analysis = _play("hafta4_deadlock.json").analysis()
    assert analysis.report.deadlocked == ["P1", "P2"]
    assert analysis.risk.level == RiskLevel.CRITICAL


def test_3_coklu_deadlock_iki_dongu_ayri_raporlanir():
    analysis = _play("hafta10_coklu_deadlock.json", stop_before="recover").analysis()
    assert analysis.report.deadlocked == ["P1", "P2", "P3", "P4"]
    cycles = [set(c) for c in analysis.report.cycles]
    assert len(cycles) == 2
    assert {"P1", "P2", "R1", "R2"} in cycles
    assert {"P3", "P4", "R3", "R4"} in cycles
    assert "Döngü 2" in analysis.report.summary()


def test_3b_coklu_deadlockta_recovery_iki_dongüyu_de_cozer():
    sim = _play("hafta10_coklu_deadlock.json")
    assert len(sim.history[-1].applied) == 2  # her döngü için bir kurtarma
    assert sim.analysis().report.has_deadlock is False


def test_4_recovery_sonrasi_deadlock_kalmaz_sistem_safe():
    sim = _play("hafta8_recovery.json")
    analysis = sim.analysis()
    assert RiskLevel.CRITICAL in _levels(sim)
    assert analysis.report.has_deadlock is False
    assert analysis.safety[0] is True


def test_5_dongu_var_ama_deadlock_yok():
    sim = _play("hafta4_dongu_deadlock_yok.json")
    levels = _levels(sim)
    assert RiskLevel.CRITICAL not in levels  # en sık yapılan hata: döngüyü deadlock sanmak
    assert RiskLevel.MEDIUM in levels


def test_donguye_takilan_process_ayri_dongu_sayilmaz():
    # Tek döngü (P1 → R2 → P2 → R1 → P1); P3 yalnızca döngüdeki R2yi bekliyor: ikinci döngü yok ama P3 de takılı.
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1, r2, r3 = Resource("R1"), Resource("R2"), Resource("R3")
    r1.acquire(p1)
    r2.acquire(p2)
    r3.acquire(p3)
    r2.acquire(p1)
    r1.acquire(p2)
    r2.acquire(p3)
    assert len(find_cycles(build_rag([r1, r2, r3]))) == 1
    assert analyze([r1, r2, r3]).deadlocked == ["P1", "P2", "P3"]
