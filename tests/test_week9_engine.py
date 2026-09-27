import pytest

from src.engine import Simulation
from src.process import ProcessState
from src.risk import RiskLevel


def _sim():
    return Simulation.from_file("scenarios/hafta8_recovery.json")


def test_baslangicta_hic_olay_uygulanmamistir():
    sim = _sim()
    assert sim.cursor == 0
    assert sim.history == []
    assert sim.next_event() == {"action": "acquire", "process": "P1", "resource": "R1"}
    assert set(sim.processes) == {"P1", "P2"}  # Max bildirenler baştan sistemde


def test_step_siradaki_olayi_uygular():
    sim = _sim()
    step = sim.step()
    assert sim.cursor == 1
    assert "P1" in step.title and "R1" in step.title
    assert sim.processes["P1"].held_resources == {"R1": 1}


def test_senaryo_bitince_step_none_doner():
    sim = _sim()
    while sim.next_event() is not None:
        sim.step()
    assert sim.step() is None
    assert sim.analysis().risk.level == RiskLevel.LOW


def test_analiz_deadlock_ve_kurtarma_seceneklerini_verir():
    sim = _sim()
    for _ in range(4):
        sim.step()
    analysis = sim.analysis()
    assert analysis.report.has_deadlock
    assert analysis.risk.level == RiskLevel.CRITICAL
    assert analysis.options[0].label() == "Geri al: R2, sahibi P2"


def test_senaryo_disi_elle_eylem_uygulanabilir():
    sim = _sim()
    sim.apply({"action": "acquire", "process": "P2", "resource": "R1"})
    assert sim.cursor == 0  # senaryodaki sıra ilerlemedi
    assert sim.processes["P2"].held_resources == {"R1": 1}


def test_kurtarma_secenegi_indeksle_uygulanir():
    sim = _sim()
    for _ in range(4):
        sim.step()
    step = sim.apply_option(0)
    assert step.applied[0].label() == "Geri al: R2, sahibi P2"
    assert not sim.analysis().report.has_deadlock


def test_undo_son_eylemi_geri_alir():
    sim = _sim()
    sim.step()
    sim.step()
    sim.undo()
    assert sim.cursor == 1
    assert len(sim.history) == 1
    assert sim.processes["P2"].held_resources == {}


def test_undo_elle_eylemde_senaryo_sirasini_bozmaz():
    sim = _sim()
    sim.step()
    sim.apply({"action": "acquire", "process": "P2", "resource": "R2"})
    sim.undo()
    assert sim.cursor == 1
    assert sim.processes["P2"].held_resources == {}


def test_undo_sonlandirmayi_da_geri_alir():
    sim = _sim()
    for _ in range(4):
        sim.step()
    sim.apply({"action": "terminate", "process": "P2"})
    assert sim.processes["P2"].state == ProcessState.TERMINATED
    sim.undo()
    assert sim.processes["P2"].state == ProcessState.WAITING
    assert sim.analysis().report.has_deadlock


def test_bos_gecmiste_undo_bir_sey_yapmaz():
    sim = _sim()
    sim.undo()
    assert sim.cursor == 0


def test_bilinmeyen_eylem_hata_verir_ve_durumu_bozmaz():
    sim = _sim()
    sim.step()
    with pytest.raises(ValueError):
        sim.apply({"action": "uc", "process": "P1"})
    assert len(sim.history) == 1
