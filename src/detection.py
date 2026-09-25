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
    finish = {name: not held for name, held in allocation.items()}

    progress = True
    while progress:
        progress = False
        for name in finish:
            if finish[name]:
                continue
            if all(amount <= work[r] for r, amount in request[name].items()):
                # P'nin isteği karşılanabiliyor → işini bitirip elindekileri bırakacağını varsay.
                for r, amount in allocation[name].items():
                    work[r] += amount
                finish[name] = True
                progress = True

    return sorted(name for name, done in finish.items() if not done)
