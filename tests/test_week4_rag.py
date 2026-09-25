from src.process import Process
from src.resource import Resource
from src.detection import build_rag, find_cycle


def test_atama_ve_istek_kenarlari_dogru_kurulur():
    p1 = Process("P1")
    p2 = Process("P2")
    r1 = Resource("R1")

    r1.acquire(p1)  # atama kenarı: R1 → P1
    r1.acquire(p2)  # istek kenarı: P2 → R1

    graph = build_rag([r1])
    assert graph["R1"] == ["P1"]
    assert graph["P2"] == ["R1"]


def test_bos_sistemde_dongu_yok():
    assert find_cycle(build_rag([Resource("R1"), Resource("R2")])) is None


def test_bekleme_var_ama_dongu_yoksa_deadlock_yok():
    p1 = Process("P1")
    p2 = Process("P2")
    r1 = Resource("R1")

    r1.acquire(p1)
    r1.acquire(p2)  # P2 bekliyor ama P1 kimseyi beklemiyor → zincir P2 → R1 → P1'de biter

    assert find_cycle(build_rag([r1])) is None


def test_klasik_iki_processli_deadlock_dongusu_bulunur():
    p1 = Process("P1")
    p2 = Process("P2")
    r1 = Resource("R1")
    r2 = Resource("R2")

    r1.acquire(p1)  # P1, R1'i tutuyor
    r2.acquire(p2)  # P2, R2'yi tutuyor
    r2.acquire(p1)  # P1, R2'yi bekliyor
    r1.acquire(p2)  # P2, R1'i bekliyor → döngü

    cycle = find_cycle(build_rag([r1, r2]))
    assert cycle is not None
    assert set(cycle) == {"P1", "P2", "R1", "R2"}


def test_dongu_disindaki_process_donguye_dahil_edilmez():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1, r2 = Resource("R1"), Resource("R2")

    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)
    r1.acquire(p3)  # P3 de R1'i bekliyor ama döngünün parçası değil

    cycle = find_cycle(build_rag([r1, r2]))
    assert "P3" not in cycle
