"""Hafta 10: uç durumlar (el kitabı 10.4). Her test bir gerçek hatayı ya da bilinçli bir davranışı sabitler."""
import pytest

from src.detection import detect_deadlock
from src.engine import Simulation
from src.process import Process, ProcessState
from src.resource import Resource


def _sim(events, resources=None):
    return Simulation({"resources": resources or [{"name": "R1"}, {"name": "R2"}], "events": events})


# --- Hatalar (düzeltildi) ---

def test_toplamdan_fazla_istek_reddedilir():
    # Önceden: process sonsuza kadar bekliyordu ve tespit algoritması bunu görmüyordu.
    p = Process("P1")
    r = Resource("R1", total_instances=1)
    with pytest.raises(ValueError):
        r.acquire(p, 2)
    assert p.state == ProcessState.READY
    assert r.waiting_queue == []


@pytest.mark.parametrize("amount", [0, -3])
def test_sifir_ve_negatif_istek_reddedilir(amount):
    # Önceden: -3 istek boştaki birimi 4'e çıkarıyordu (toplam 1 iken).
    p = Process("P1")
    r = Resource("R1")
    with pytest.raises(ValueError):
        r.acquire(p, amount)
    assert r.available_instances == 1
    assert r.allocation == {}


@pytest.mark.parametrize("amount", [0, -1])
def test_sifir_ve_negatif_birakma_reddedilir(amount):
    p = Process("P1")
    r = Resource("R1")
    r.acquire(p)
    with pytest.raises(ValueError):
        r.release(p, amount)
    assert r.allocation == {p: 1}


def test_bekleyen_process_yeni_istek_yapamaz():
    # Önceden: WAITING process ikinci bir kaynağı alabiliyor, iki kuyrukta birden duruyordu.
    sim = _sim([
        {"action": "acquire", "process": "P2", "resource": "R1"},
        {"action": "acquire", "process": "P1", "resource": "R1"},
        {"action": "acquire", "process": "P1", "resource": "R2"},
    ])
    sim.step()
    sim.step()
    with pytest.raises(ValueError, match="bekliyor"):
        sim.step()
    assert sim.processes["P1"].held_resources == {}
    assert sim.cursor == 2  # hatalı olay uygulanmadı, senaryo ilerlemedi


def test_bekleyen_process_kaynak_birakamaz():
    sim = _sim([
        {"action": "acquire", "process": "P1", "resource": "R2"},
        {"action": "acquire", "process": "P2", "resource": "R1"},
        {"action": "acquire", "process": "P1", "resource": "R1"},
        {"action": "release", "process": "P1", "resource": "R2"},
    ])
    for _ in range(3):
        sim.step()
    with pytest.raises(ValueError, match="bekliyor"):
        sim.step()


def test_senaryoda_olmayan_kaynak_anlasilir_hata_verir():
    # Önceden: AttributeError → web arayüzünde sayfa çöküyordu.
    sim = _sim([{"action": "acquire", "process": "P1", "resource": "R9"}])
    with pytest.raises(ValueError, match="R9"):
        sim.step()


def test_process_adi_eksik_olay_anlasilir_hata_verir():
    sim = _sim([{"action": "acquire", "resource": "R1"}])
    with pytest.raises(ValueError):
        sim.step()


# --- Bilinçli davranışlar (hata değil) ---

def test_bos_sistem_calisir():
    sim = Simulation({"resources": [], "events": []})
    assert sim.step() is None
    assert sim.analysis().report.has_deadlock is False


def test_kendi_tuttugu_kaynagi_tekrar_isteyen_process_kendini_kilitler():
    # Tek örnekli, tekrar girilemeyen (non-reentrant) kaynak: gerçek sistemlerde de self-deadlock.
    p = Process("P1")
    r = Resource("R1")
    r.acquire(p)
    r.acquire(p)
    assert detect_deadlock([r]) == ["P1"]


def test_tutmadigi_kaynagi_birakma_hata_verir():
    with pytest.raises(ValueError):
        Resource("R1").release(Process("P1"), 1)


def test_sonlandirilmis_process_islem_yapamaz():
    sim = _sim([
        {"action": "acquire", "process": "P1", "resource": "R1"},
        {"action": "terminate", "process": "P1"},
        {"action": "acquire", "process": "P1", "resource": "R1"},
    ])
    sim.step()
    sim.step()
    with pytest.raises(ValueError, match="sonlandırıldı"):
        sim.step()
