from src.process import Process
from src.resource import Resource
from src.detection import build_rag, find_cycle, detect_deadlock


def test_bos_sistemde_deadlock_yok():
    assert detect_deadlock([Resource("R1", total_instances=3)]) == []


def test_tek_ornekli_klasik_deadlock_tespit_edilir():
    p1, p2 = Process("P1"), Process("P2")
    r1, r2 = Resource("R1"), Resource("R2")

    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)

    assert detect_deadlock([r1, r2]) == ["P1", "P2"]


def test_dongu_var_ama_cok_ornekli_kaynak_sayesinde_deadlock_yok():
    # Silberschatz Şekil 8.9'un benzeri: R1'in 2 birimi var, biri kimseyi beklemeyen P3'te.
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1 = Resource("R1", total_instances=2)
    r2 = Resource("R2")

    r1.acquire(p1)
    r1.acquire(p3)  # R1'in ikinci birimi P3'te, P3 hiçbir şey beklemiyor
    r2.acquire(p2)
    r2.acquire(p1)  # P1, R2'yi bekliyor
    r1.acquire(p2)  # P2, R1'i bekliyor

    assert find_cycle(build_rag([r1, r2])) is not None  # grafta döngü görünüyor...
    assert detect_deadlock([r1, r2]) == []  # ...ama P3 bitince zincir çözülüyor


def test_cok_ornekli_gercek_deadlock_tespit_edilir():
    p1, p2 = Process("P1"), Process("P2")
    r1 = Resource("R1", total_instances=2)
    r2 = Resource("R2", total_instances=2)

    r1.acquire(p1, amount=2)
    r2.acquire(p2, amount=2)
    r2.acquire(p1)  # R2'de boş birim yok
    r1.acquire(p2)  # R1'de boş birim yok

    assert detect_deadlock([r1, r2]) == ["P1", "P2"]


def test_donguye_takili_process_de_deadlock_listesinde_yer_alir():
    # P3 döngünün parçası değil ama R3'ü tutarken döngüdeki R1'i bekliyor → o da asla bitemez.
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1, r2, r3 = Resource("R1"), Resource("R2"), Resource("R3")

    r1.acquire(p1)
    r2.acquire(p2)
    r3.acquire(p3)
    r2.acquire(p1)
    r1.acquire(p2)
    r1.acquire(p3)

    assert "P3" not in find_cycle(build_rag([r1, r2, r3]))
    assert detect_deadlock([r1, r2, r3]) == ["P1", "P2", "P3"]
