from dataclasses import dataclass

WHITE, GRAY, BLACK = 0, 1, 2  # ziyaret edilmedi / yolda (yığında) / bitti


def build_rag(resources) -> dict:
    """Kaynakların mevcut durumundan Resource Allocation Graph kurar.

    Dönen sözlük: {düğüm_adı: [komşu_düğüm_adları]}
      - atama kenarı  R → P : R'nin bir birimi P'nin elinde
      - istek kenarı  P → R : P, R'yi bekliyor
    """
    graph = {}
    for resource in resources:
        graph.setdefault(resource.name, [])
        for process in resource.allocation:
            graph[resource.name].append(process.name)
            graph.setdefault(process.name, [])
        for process, _ in resource.waiting_queue:
            graph.setdefault(process.name, []).append(resource.name)
    return graph


def find_cycle(graph: dict):
    """Grafta döngü arar (DFS, üç renk). Döngü varsa düğüm listesini, yoksa None döner."""
    color = {node: WHITE for node in graph}
    path = []  # şu anki DFS yolu (gri düğümler)

    def dfs(node):
        color[node] = GRAY
        path.append(node)
        for neighbor in graph[node]:
            if color[neighbor] == GRAY:  # yoldaki bir düğüme geri döndük → döngü
                return path[path.index(neighbor):]
            if color[neighbor] == WHITE:
                cycle = dfs(neighbor)
                if cycle:
                    return cycle
        color[node] = BLACK
        path.pop()
        return None

    for node in graph:
        if color[node] == WHITE:
            cycle = dfs(node)
            if cycle:
                return cycle
    return None


def detect_deadlock(resources) -> list:
    """Çok örnekli kaynaklar için tespit algoritması (Silberschatz 8.7.2).

    Deadlock'taki process adlarını sıralı liste olarak döner; deadlock yoksa boş liste.
    """
    work = {r.name: r.available_instances for r in resources}
    allocation = {}  # {process_adı: {kaynak_adı: tutulan_adet}}
    request = {}  # {process_adı: {kaynak_adı: beklenen_adet}}
    for resource in resources:
        for process, amount in resource.allocation.items():
            allocation.setdefault(process.name, {})[resource.name] = amount
            request.setdefault(process.name, {})
        for process, amount in resource.waiting_queue:
            request.setdefault(process.name, {})[resource.name] = amount
            allocation.setdefault(process.name, {})

    # Elinde hiçbir şey olmayan process kimseyi kilitleyemez → baştan bitmiş sayılır.
    finished = {name: not held for name, held in allocation.items()}
    _, stuck = run_to_completion(work, request, allocation, finished)
    return sorted(stuck)


def find_cycles(graph: dict) -> list:
    """Birbirinden ayrık (ortak düğümü olmayan) bütün döngüleri bulur.

    Bir döngü bulunca onun düğümlerini graftan çıkarıp aramayı tekrarlar; böylece
    birbirinden bağımsız iki deadlock ayrı ayrı raporlanır.
    """
    remaining = {node: list(neighbors) for node, neighbors in graph.items()}
    cycles = []
    while (cycle := find_cycle(remaining)) is not None:
        cycles.append(cycle)
        removed = set(cycle)
        remaining = {
            node: [n for n in neighbors if n not in removed]
            for node, neighbors in remaining.items()
            if node not in removed
        }
    return cycles


def run_to_completion(work, demand, allocation, finished):
    """Work/Finish döngüsü: tespit algoritması ve Banker's güvenlik kontrolünün ortak çekirdeği.

    demand: her process'in bitmek için istediği ({process: {kaynak: adet}});
      tespitte Request (şu an beklediği), Banker's'ta Need (en kötü durumda isteyebileceği).
    finished: {process: baştan bitmiş sayılıyor mu}
    Dönen: (bitiş sırası, bitemeyen processler)
    """
    work = dict(work)  # çağıranın sözlüğünü bozmamak için kopya
    finished = dict(finished)
    order = []
    progress = True
    while progress:
        progress = False
        for name in finished:
            if finished[name]:
                continue
            if all(amount <= work.get(r, 0) for r, amount in demand.get(name, {}).items()):
                # İsteği karşılanabiliyor → işini bitirip elindekileri bırakacağını varsay.
                for r, amount in allocation.get(name, {}).items():
                    work[r] = work.get(r, 0) + amount
                finished[name] = True
                order.append(name)
                progress = True
    stuck = [name for name, done in finished.items() if not done]
    return order, stuck

@dataclass
class DeadlockReport:
    deadlocked: list  # deadlock'taki process adları (tespit algoritmasına göre)
    cycles: list  # RAG'deki birbirinden ayrık döngüler (yoksa boş)

    @property
    def cycle(self):
        """İlk döngü (yoksa None); tek döngülü kullanım için."""
        return self.cycles[0] if self.cycles else None

    @property
    def has_deadlock(self) -> bool:
        return bool(self.deadlocked)

    @staticmethod
    def format_cycle(cycle) -> str:
        # Aynı döngü hep aynı yazılsın diye alfabetik en küçük düğümden başlat (ör. P1 → R2 → ...).
        start = cycle.index(min(cycle))
        ordered = cycle[start:] + cycle[:start]
        return " → ".join(ordered + [ordered[0]])

    def cycle_path(self) -> str:
        """Bütün döngüler; birden fazlaysa numaralı (Döngü 1: ..., Döngü 2: ...)."""
        paths = [self.format_cycle(c) for c in self.cycles]
        if len(paths) <= 1:
            return "".join(paths)
        return " | ".join(f"Döngü {i}: {p}" for i, p in enumerate(paths, start=1))

    def cycles_text(self) -> str:
        """Etiketiyle birlikte döngü metni: "Döngü: ..." ya da "Döngü 1: ... | Döngü 2: ..."."""
        return self.cycle_path() if len(self.cycles) > 1 else f"Döngü: {self.cycle_path()}"

    def summary(self) -> str:
        if self.has_deadlock:
            return f"DEADLOCK! Takılı processler: {', '.join(self.deadlocked)} | {self.cycles_text()}"
        if self.cycle:
            return f"Döngü var ({self.cycle_path()}) ama deadlock yok: çok örnekli kaynak sayesinde çözülebilir."
        return "Deadlock yok."


def analyze(resources) -> DeadlockReport:
    """RAG döngü aramasını ve tespit algoritmasını birlikte çalıştırıp tek raporda toplar."""
    return DeadlockReport(
        deadlocked=detect_deadlock(resources),
        cycles=find_cycles(build_rag(resources)),
    )
