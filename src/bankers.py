"""Banker's Algorithm (Silberschatz 8.6.3): güvenli durum kontrolü ve istek öncesi değerlendirme.

Bütün tablolar sözlük: {process_adı: {kaynak_adı: adet}}, available ise {kaynak_adı: adet}.
"""
from dataclasses import dataclass

from src.detection import run_to_completion


def compute_need(maximum, allocation) -> dict:
    """Need = Max − Allocation: her process'in en kötü durumda daha isteyebileceği miktar."""
    return {
        p: {r: max_amount - allocation.get(p, {}).get(r, 0) for r, max_amount in claims.items()}
        for p, claims in maximum.items()
    }


def is_safe(available, maximum, allocation):
    """Güvenlik algoritması (8.6.3.1). Dönen: (güvenli mi, güvenli sıra)."""
    need = compute_need(maximum, allocation)
    finished = {p: False for p in maximum}
    order, stuck = run_to_completion(available, need, allocation, finished)
    if stuck:
        return False, []
    return True, order


@dataclass
class RequestDecision:
    status: str  # "SAFE" | "UNSAFE" | "WAIT"
    sequence: list  # isteğin verildiği varsayılan durumdaki güvenli sıra (SAFE ise)


def check_request(process, request, available, maximum, allocation) -> RequestDecision:
    """Kaynak isteği algoritması (8.6.3.2). Girdileri değiştirmez, sadece değerlendirir."""
    need = compute_need(maximum, allocation)[process]

    # 1) Process, baştan bildirdiği Max'ı aşamaz.
    for r, amount in request.items():
        if amount > need.get(r, 0):
            raise ValueError(
                f"{process}, bildirdiği Max'ı aşıyor: {r} için ihtiyaç {need.get(r, 0)}, istek {amount}."
            )

    # 2) Boşta yeterli kaynak yoksa beklemek zorunda (güvenlikten bağımsız).
    if any(amount > available.get(r, 0) for r, amount in request.items()):
        return RequestDecision("WAIT", [])

    # 3) İsteği vermiş gibi yap, oluşan durum güvenli mi bak.
    new_available = {r: n - request.get(r, 0) for r, n in available.items()}
    new_allocation = {p: dict(held) for p, held in allocation.items()}
    held = new_allocation.setdefault(process, {})
    for r, amount in request.items():
        held[r] = held.get(r, 0) + amount

    safe, sequence = is_safe(new_available, maximum, new_allocation)
    return RequestDecision("SAFE" if safe else "UNSAFE", sequence)


# --- Simülasyon nesneleriyle (Process / Resource) çalışan yardımcılar ---

def system_state(processes, resources):
    """Process ve kaynaklardan (available, maximum, allocation) tablolarını kurar.

    Max bildirmeyen bir process varsa Banker's uygulanamaz → None döner.
    """
    if not processes or any(p.max_claim is None for p in processes):
        return None
    available = {r.name: r.available_instances for r in resources}
    # Max'ta adı geçmeyen kaynak için Max = 0 (o kaynağı hiç isteyemez).
    maximum = {p.name: {r.name: p.max_claim.get(r.name, 0) for r in resources} for p in processes}
    allocation = {p.name: dict(p.held_resources) for p in processes}
    return available, maximum, allocation


def safety_of(processes, resources):
    """Sistemin şu anki durumu güvenli mi? (güvenli mi, güvenli sıra) ya da Banker's uygulanamıyorsa None."""
    state = system_state(processes, resources)
    return None if state is None else is_safe(*state)


def evaluate_acquire(process, resource, amount, processes, resources):
    """Bir acquire isteğini, gerçekleşmeden ÖNCE değerlendirir. Banker's uygulanamıyorsa None."""
    state = system_state(processes, resources)
    if state is None:
        return None
    return check_request(process.name, {resource.name: amount}, *state)


def safety_text(safety) -> str:
    """safety_of() sonucunu konsol ve arayüz için okunur metne çevirir."""
    if safety is None:
        return "Banker's analizi yok (senaryoda Max bildirilmemiş)."
    safe, sequence = safety
    if safe:
        return f"Güvenli durum. Güvenli sıra: {' → '.join(sequence)}"
    return "GÜVENSİZ durum: güvenli sıra yok, deadlock oluşabilir."
