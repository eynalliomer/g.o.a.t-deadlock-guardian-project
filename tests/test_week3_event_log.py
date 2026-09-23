from src.process import Process
from src.resource import Resource
from src.event_log import EventLog


def test_event_log_bos_baslar():
    log = EventLog()
    assert log.events == []


def test_acquire_ve_release_olaylari_kaydedilir():
    log = EventLog()
    p1 = Process("P1")
    r = Resource("R1", event_log=log)

    r.acquire(p1)
    r.release(p1)

    assert len(log.events) == 2
    assert log.events[0]["type"] == "ACQUIRED"
    assert log.events[0]["process"] == "P1"
    assert log.events[0]["resource"] == "R1"
    assert log.events[1]["type"] == "RELEASED"


def test_waiting_olayi_kaydedilir():
    log = EventLog()
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1", event_log=log)

    r.acquire(p1)
    r.acquire(p2)  # meşgul -> WAITING

    types = [e["type"] for e in log.events]
    assert types == ["ACQUIRED", "WAITING"]


def test_log_verilmezse_hata_vermez():
    p1 = Process("P1")
    r = Resource("R1")  # event_log yok

    assert r.acquire(p1) is True
    r.release(p1)
