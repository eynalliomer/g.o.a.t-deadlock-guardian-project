from src.process import Process, ProcessState
from src.resource import Resource


def test_yeni_process_ready_ve_bos_kaynak_listesiyle_baslar():
    p = Process("P1")
    assert p.state == ProcessState.READY
    assert p.held_resources == {}


def test_bos_kaynak_dogrudan_verilir():
    p = Process("P1")
    r = Resource("R1")

    sonuc = r.acquire(p)

    assert sonuc is True
    assert r.allocation[p] == 1
    assert p.state == ProcessState.READY
    assert p.held_resources["R1"] == 1


def test_mesgul_kaynak_isteyen_process_waiting_olur():
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1")

    r.acquire(p1)
    sonuc = r.acquire(p2)

    assert sonuc is False
    assert p2.state == ProcessState.WAITING
    assert any(p is p2 for p, _ in r.waiting_queue)


def test_release_kaynagi_bekleyen_processe_devreder():
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1")

    r.acquire(p1)
    r.acquire(p2)

    r.release(p1)

    assert p2 in r.allocation
    assert r.allocation[p2] == 1
    assert p2.state == ProcessState.READY
    assert p2.held_resources["R1"] == 1
    assert p1 not in r.allocation
    assert r.waiting_queue == []


def test_sahibi_olmayan_process_kaynagi_birakamaz():
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1")

    r.acquire(p1)

    try:
        r.release(p2)
        assert False, "ValueError bekleniyordu"
    except ValueError:
        pass
