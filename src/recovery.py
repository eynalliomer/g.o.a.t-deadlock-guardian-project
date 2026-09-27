"""Deadlock'tan kurtarma (Silberschatz 8.8): process sonlandırma ve kaynak geri alma.

Kurban seçimi maliyete göre yapılır (ekip kararı, hafta 8):
    maliyet = öncelik × 10 − serbest bırakılan birim × 2 + kurban seçilme sayısı × 5
  - yüksek öncelikli process pahalıdır (korunur)
  - çok kaynak serbest bırakan seçenek ucuzdur (deadlock'u çözme ihtimali yüksek)
  - sık kurban seçilen process pahalılaşır (starvation önlenir)
Eşit maliyette kaynak geri alma, sonlandırmadan önce gelir: process yaşamaya devam eder.
"""
from dataclasses import dataclass

from src.detection import detect_deadlock
from src.process import ProcessState

PRIORITY_WEIGHT = 10
FREED_UNIT_WEIGHT = 2
VICTIM_COUNT_WEIGHT = 5


def option_cost(process, freed_units: int) -> int:
    return (process.priority * PRIORITY_WEIGHT
            - freed_units * FREED_UNIT_WEIGHT
            + process.victim_count * VICTIM_COUNT_WEIGHT)


@dataclass
class RecoveryOption:
    kind: str  # "preempt" | "terminate"
    process: object
    resource: object | None  # geri almada hangi kaynak; sonlandırmada None
    cost: int
    freed_units: int  # bu seçenek uygulanınca serbest kalacak birim sayısı

    def label(self) -> str:
        if self.kind == "terminate":
            return f"Sonlandır: {self.process.name}"
        return f"Geri al: {self.resource.name}, sahibi {self.process.name}"


def make_option(kind, process, resource=None) -> RecoveryOption:
    if kind == "terminate":
        freed = sum(process.held_resources.values())
    else:
        freed = resource.allocation.get(process, 0)
    return RecoveryOption(kind, process, resource, option_cost(process, freed), freed)


def recovery_options(processes, resources) -> list:
    """Deadlock'taki processler için bütün kurtarma seçenekleri, en ucuzu başta. Deadlock yoksa boş."""
    deadlocked = set(detect_deadlock(resources))
    by_name = {r.name: r for r in resources}
    options = []
    for p in processes:
        if p.name not in deadlocked:
            continue
        options.append(make_option("terminate", p))
        for r_name in p.held_resources:
            if by_name[r_name].waiting_queue:  # yalnızca birinin beklediği kaynağı geri almak işe yarar
                options.append(make_option("preempt", p, by_name[r_name]))

    kind_order = {"preempt": 0, "terminate": 1}
    options.sort(key=lambda o: (o.cost, kind_order[o.kind], o.process.name, o.resource.name if o.resource else ""))
    return options


def terminate(process, resources):
    """Process'i sonlandırır: bekleyen isteklerini iptal eder, elindeki bütün kaynakları bırakır."""
    for r in resources:
        r.cancel_wait(process)  # önce kuyruktan çık ki bırakılan kaynak ona geri verilmesin
    for r in resources:
        held = r.allocation.get(process, 0)
        if held:
            r.release(process, held)  # release bekleyenlere dağıtır
    process.state = ProcessState.TERMINATED
    process.victim_count += 1


def preempt(process, resource, resources):
    """Kaynağı process'ten geri alır (rollback: o kaynağı almadan önceki noktaya döner)."""
    resource.release(process, resource.allocation[process])
    process.victim_count += 1
    still_waiting = any(p is process for r in resources for p, _ in r.waiting_queue)
    process.state = ProcessState.WAITING if still_waiting else ProcessState.READY


def apply_option(option, resources):
    if option.kind == "terminate":
        terminate(option.process, resources)
    else:
        preempt(option.process, option.resource, resources)


def recover(processes, resources, on_apply=None) -> list:
    """Birer birer kurtarma: en ucuz seçeneği uygula, tespiti tekrar çalıştır, deadlock bitene kadar sür.

    on_apply: her seçenek uygulanmadan hemen önce çağrılır (ör. olay kaydına yazmak için).
    """
    applied = []
    while True:
        options = recovery_options(processes, resources)
        if not options:
            return applied
        if on_apply is not None:
            on_apply(options[0])
        apply_option(options[0], resources)
        applied.append(options[0])
