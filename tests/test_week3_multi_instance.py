from src.process import Process, ProcessState
from src.resource import Resource


def test_varsayilan_total_instances_bir():
    r = Resource("R1")
    assert r.total_instances == 1
    assert r.available_instances == 1


def test_cok_ornekli_kaynaktan_birden_fazla_birim_alinabilir():
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1", total_instances=3)

    assert r.acquire(p1, amount=2) is True
    assert r.available_instances == 1

    assert r.acquire(p2, amount=1) is True
    assert r.available_instances == 0
    assert p1.held_resources["R1"] == 2
    assert p2.held_resources["R1"] == 1


def test_yetersiz_miktar_tum_ya_da_hic_reddedilir():
    p1 = Process("P1")
    p2 = Process("P2")
    r = Resource("R1", total_instances=3)

    r.acquire(p1, amount=2)  # 1 birim kaldı

    sonuc = r.acquire(p2, amount=2)  # 2 istiyor ama sadece 1 boşta

    assert sonuc is False
    assert p2.state == ProcessState.WAITING
    assert "R1" not in p2.held_resources  # hiç verilmedi (tüm-ya-da-hiç)
    assert r.available_instances == 1  # p1'in payı dokunulmadı


def test_kuyrukta_karsilanabilen_istek_atlanarak_servis_edilir():
    p1 = Process("P1")
    p2 = Process("P2")
    p3 = Process("P3")
    r = Resource("R1", total_instances=2)

    r.acquire(p1, amount=2)  # kaynak tamamen dolu
    r.acquire(p2, amount=2)  # WAITING, kuyrukta (P2, 2)
    r.acquire(p3, amount=1)  # WAITING, kuyrukta (P3, 1)

    r.release(p1, amount=1)  # şimdi 1 birim boşta: P2'nin isteği (2) hâlâ karşılanamaz, P3'ünki (1) karşılanabilir

    assert p3.state == ProcessState.READY
    assert p3.held_resources["R1"] == 1
    assert p2.state == ProcessState.WAITING
    assert any(p is p2 for p, _ in r.waiting_queue)
    assert not any(p is p3 for p, _ in r.waiting_queue)


def test_elindekinden_fazla_birakma_hata_verir():
    p1 = Process("P1")
    r = Resource("R1", total_instances=3)
    r.acquire(p1, amount=1)

    try:
        r.release(p1, amount=2)
        assert False, "ValueError bekleniyordu"
    except ValueError:
        pass
