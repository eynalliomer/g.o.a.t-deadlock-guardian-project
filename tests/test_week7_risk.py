from src.process import Process
from src.resource import Resource
from src.risk import RiskLevel, assess_risk
from src.run_scenario import run_scenario_step_by_step


def test_seviyeler_siralidir():
    assert RiskLevel.LOW < RiskLevel.MEDIUM < RiskLevel.HIGH < RiskLevel.CRITICAL


def test_bos_sistem_low():
    risk = assess_risk([], [Resource("R1")])
    assert risk.level == RiskLevel.LOW
    assert risk.reasons == ["Sistem normal çalışıyor."]


def test_bekleyen_process_medium_ve_nedeni_aciklanir():
    p1, p2 = Process("P1"), Process("P2")
    r1 = Resource("R1")
    r2 = Resource("R2", total_instances=9)  # boş kaynak oranı yüksek kalsın, sadece bekleme tetiklensin
    r1.acquire(p1)
    r1.acquire(p2)

    risk = assess_risk([p1, p2], [r1, r2])
    assert risk.level == RiskLevel.MEDIUM
    assert any("P2" in r and "R1" in r and "P1" in r for r in risk.reasons)


def test_bos_kaynak_esigin_altinda_medium():
    p1 = Process("P1")
    r1 = Resource("R1", total_instances=10)
    r1.acquire(p1, amount=9)  # %10 boş

    risk = assess_risk([p1], [r1])
    assert risk.level == RiskLevel.MEDIUM
    assert any("1/10" in r for r in risk.reasons)


def test_bos_kaynak_tam_esikte_low():
    p1 = Process("P1")
    r1 = Resource("R1", total_instances=5)
    r1.acquire(p1, amount=4)  # %20 boş: eşik "altı" olduğu için tetiklenmez

    assert assess_risk([p1], [r1]).level == RiskLevel.LOW


def test_dongu_var_deadlock_yok_medium():
    p1, p2, p3 = Process("P1"), Process("P2"), Process("P3")
    r1 = Resource("R1", total_instances=2)
    r2 = Resource("R2")
    r1.acquire(p1)
    r1.acquire(p3)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)

    risk = assess_risk([p1, p2, p3], [r1, r2])
    assert risk.level == RiskLevel.MEDIUM
    assert any("döngü" in r.lower() for r in risk.reasons)


def test_guvensiz_durum_high():
    p1 = Process("P1", max_claim={"R1": 1, "R2": 1})
    p2 = Process("P2", max_claim={"R1": 1, "R2": 1})
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)

    risk = assess_risk([p1, p2], [r1, r2])
    assert risk.level == RiskLevel.HIGH
    assert any("güvensiz" in r.lower() for r in risk.reasons)


def test_deadlock_critical_ve_dongu_nedeni():
    p1, p2 = Process("P1"), Process("P2")
    r1, r2 = Resource("R1"), Resource("R2")
    r1.acquire(p1)
    r2.acquire(p2)
    r2.acquire(p1)
    r1.acquire(p2)

    risk = assess_risk([p1, p2], [r1, r2])
    assert risk.level == RiskLevel.CRITICAL
    assert any("P1 → R2 → P2 → R1 → P1" in r for r in risk.reasons)


def test_senaryoda_risk_seyri_kaydedilir():
    result = run_scenario_step_by_step("scenarios/hafta6_guvensiz_durum.json")
    levels = [risk.level for risk in result["risk_timeline"]]
    L, H, C = RiskLevel.LOW, RiskLevel.HIGH, RiskLevel.CRITICAL
    assert levels == [L, L, H, H, C]
