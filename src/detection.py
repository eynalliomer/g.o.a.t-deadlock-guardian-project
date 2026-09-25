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
