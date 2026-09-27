"""Risk seviyesi sistemi (projeye özgü heuristic, hafta 7).

Seviye, tetiklenen kuralların en yükseğidir; her kural kendi nedenini ekler:
  CRITICAL : tespit algoritması deadlock buldu
  HIGH     : Banker's güvenli sıra bulamıyor (güvensiz durum)
  MEDIUM   : bekleyen process var, boştaki kaynak eşiğin altında
             ya da RAG'de döngü var ama deadlock yok
  LOW      : hiçbiri
Eşikler ekip kararıdır (bkz. hafta 7 notu); kesin garanti değil, sezgisel kuraldır.
"""
from dataclasses import dataclass
from enum import IntEnum

from src.bankers import safety_of
from src.detection import analyze

FREE_RATIO_THRESHOLD = 0.20  # boştaki kaynak toplamın %20'sinin altındaysa "az"


class RiskLevel(IntEnum):  # IntEnum: seviyeler karşılaştırılabilir (LOW < CRITICAL), max() alınabilir
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class RiskAssessment:
    level: RiskLevel
    reasons: list


def assess_risk(processes, resources) -> RiskAssessment:
    report = analyze(resources)
    safety = safety_of(processes, resources)
    findings = []  # [(seviye, neden), ...]

    if report.has_deadlock:
        findings.append((RiskLevel.CRITICAL,
                         f"DEADLOCK: {', '.join(report.deadlocked)} takılı. {report.cycles_text()}"))

    if safety is not None and not safety[0]:
        findings.append((RiskLevel.HIGH, "Sistem güvensiz: Banker's güvenli sıra bulamıyor."))

    if report.cycle and not report.has_deadlock:
        findings.append((RiskLevel.MEDIUM,
                         f"RAG'de döngü var ({report.cycle_path()}) ama şimdilik deadlock yok."))

    for r in resources:
        holders = ", ".join(p.name for p in r.allocation) or "kimse"
        for p, amount in r.waiting_queue:
            findings.append((RiskLevel.MEDIUM,
                             f"{p.name} bekliyor: {r.name} ({amount} birim) şu an {holders} elinde."))

    total = sum(r.total_instances for r in resources)
    free = sum(r.available_instances for r in resources)
    if total and free / total < FREE_RATIO_THRESHOLD:
        findings.append((RiskLevel.MEDIUM,
                         f"Boştaki kaynak az: {free}/{total} birim (%{round(100 * free / total)})."))

    if not findings:
        return RiskAssessment(RiskLevel.LOW, ["Sistem normal çalışıyor."])
    findings.sort(key=lambda f: f[0], reverse=True)  # en ciddi neden en üstte
    return RiskAssessment(findings[0][0], [reason for _, reason in findings])
