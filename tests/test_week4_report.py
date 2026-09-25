from src.process import Process
from src.resource import Resource
from src.detection import analyze


def _klasik_deadlock():
    p1, p2 = Process("P1"), Process("P2")
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)
    return [r1, r2]


def test_deadlock_yoksa_rapor_temiz():
    report = analyze([Resource("R1")])
    assert report.has_deadlock is False
    assert report.deadlocked == []
    assert report.cycle is None
    assert "yok" in report.summary()


def test_deadlock_raporu_processleri_ve_donguyu_icerir():
    report = analyze(_klasik_deadlock())
    assert report.has_deadlock is True
    assert report.deadlocked == ["P1", "P2"]
    assert set(report.cycle) == {"P1", "P2", "R1", "R2"}


def test_dongu_yolu_basladigi_dugumle_kapanir():
    report = analyze(_klasik_deadlock())
    path = report.cycle_path()
    parts = path.split(" → ")
    assert parts[0] == parts[-1]
    assert len(parts) == 5  # 4 düğüm + başa dönüş


def test_dongu_var_deadlock_yok_durumu_ayri_raporlanir():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1 = Resource("R1", total_instances=2)
    r2 = Resource("R2")
    r1.acquire(p1)
    r1.acquire(p3)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)

    report = analyze([r1, r2])
    assert report.has_deadlock is False
    assert report.cycle is not None
    assert "döngü" in report.summary().lower()
