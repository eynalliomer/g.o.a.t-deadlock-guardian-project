from src.process import Process
from src.resource import Resource
from src.detection import analyze
from src.graph_view import render_rag_svg


def _klasik_deadlock():
    p1, p2 = Process("P1"), Process("P2")
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)
    return [p1, p2], [r1, r2]


def test_her_process_ve_kaynak_icin_dugum_cizilir():
    processes, resources = _klasik_deadlock()
    svg = render_rag_svg(processes, resources)
    assert svg.startswith("<svg")
    assert svg.count('class="node process') == 2
    assert svg.count('class="node resource') == 2


def test_atama_ve_istek_kenarlari_ayri_cizilir():
    processes, resources = _klasik_deadlock()
    svg = render_rag_svg(processes, resources)
    assert svg.count('class="edge assign') == 2  # R1 → P1, R2 → P2
    assert svg.count('class="edge request') == 2  # P1 → R2, P2 → R1


def test_kaynak_icinde_her_ornek_icin_nokta_vardir():
    p1 = Process("P1")
    r1 = Resource("R1", total_instances=3)
    r1.acquire(p1, amount=2)
    svg = render_rag_svg([p1], [r1])
    assert svg.count('class="instance used"') == 2
    assert svg.count('class="instance free"') == 1


def test_rapor_yoksa_dongu_vurgulanmaz():
    processes, resources = _klasik_deadlock()
    svg = render_rag_svg(processes, resources)
    assert "cycle" not in svg


def test_deadlockta_dongu_kenarlari_ve_processler_vurgulanir():
    processes, resources = _klasik_deadlock()
    report = analyze(resources)
    svg = render_rag_svg(processes, resources, report)
    assert svg.count('class="edge assign cycle') == 2
    assert svg.count('class="edge request cycle') == 2
    assert svg.count('class="node process deadlocked') == 2


def test_dongu_disindaki_kenar_vurgulanmaz():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)
    r1.acquire(p3)  # P3 → R1 döngünün parçası değil

    report = analyze([r1, r2])
    svg = render_rag_svg([p1, p2, p3], [r1, r2], report)
    assert svg.count('class="edge request cycle') == 2  # P1 → R2, P2 → R1
    assert svg.count('class="edge request"') == 1  # P3 → R1 normal çizilir


def test_bos_sistem_cizilebilir():
    svg = render_rag_svg([], [Resource("R1")])
    assert svg.count('class="node resource') == 1
    assert "edge" not in svg


def test_deadlocksuz_dongu_turuncu_deadlocklu_dongu_kirmizi_cizilir():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1 = Resource("R1", total_instances=2)
    r2 = Resource("R2")
    r1.acquire(p1)
    r1.acquire(p3)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)

    svg = render_rag_svg([p1, p2, p3], [r1, r2], analyze([r1, r2]))
    assert "#e67e22" in svg and "url(#arrow-orange)" in svg
    assert "url(#arrow-red)" not in svg

    processes, resources = _klasik_deadlock()
    svg = render_rag_svg(processes, resources, analyze(resources))
    assert "url(#arrow-red)" in svg
    assert "url(#arrow-orange)" not in svg
