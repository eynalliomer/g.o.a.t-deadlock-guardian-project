"""Resource Allocation Graph'ı SVG olarak çizer (Silberschatz Şekil 8.4 gösterimi).

RAG iki parçalı (bipartite) bir graftır: kenarlar hep process ile kaynak arasındadır.
Bu yüzden processleri üst sıraya, kaynakları alt sıraya dizmek yeterli; bütün oklar
iki sıra arasında akar ve hiçbir kenar bir düğümün içinden geçmez.
"""

SPACING = 140  # aynı sıradaki iki düğüm arası yatay mesafe
PROCESS_Y = 60  # process sırasının merkez yüksekliği
RESOURCE_Y = 210  # kaynak dikdörtgenlerinin üst kenarı
RADIUS = 24  # process dairesinin yarıçapı
RES_W, RES_H = 84, 50
OFFSET = 8  # aynı çift arasında hem atama hem istek varsa okları yan yana ayırmak için

NORMAL, HOT, WARN = "#555", "#c0392b", "#e67e22"  # WARN: döngü var ama deadlock yok


def _row_positions(names, width):
    """Bir sıradaki düğümleri yatayda ortalayarak x koordinatlarını verir."""
    start = (width - len(names) * SPACING) / 2 + SPACING / 2
    return {name: start + i * SPACING for i, name in enumerate(names)}


def _cycle_edges(report):
    """Döngüdeki ardışık düğüm çiftleri (u, v); son düğümden başa dönüş dahil."""
    if report is None or not report.cycle:
        return set()
    cycle = report.cycle
    return {(cycle[i], cycle[(i + 1) % len(cycle)]) for i in range(len(cycle))}


def _arrow(x1, y1, x2, y2, kind, hot, label="", hot_color=HOT):
    color = hot_color if hot else NORMAL
    width = 3 if hot else 1.6
    dash = ' stroke-dasharray="6,4"' if kind == "request" else ""
    marker = ("arrow-red" if hot_color == HOT else "arrow-orange") if hot else "arrow"
    css = f"edge {kind} cycle" if hot else f"edge {kind}"
    text = ""
    if label:
        text = (f'<text x="{(x1 + x2) / 2 + 6}" y="{(y1 + y2) / 2}" font-size="12" '
                f'fill="{color}">{label}</text>')
    return (f'<g class="{css}"><line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" '
            f'stroke-width="{width}"{dash} marker-end="url(#{marker})"/>{text}</g>')


def render_rag_svg(processes, resources, report=None) -> str:
    width = max(len(processes), len(resources), 1) * SPACING + 40
    height = RESOURCE_Y + RES_H + 30
    px = _row_positions([p.name for p in processes], width)
    rx = _row_positions([r.name for r in resources], width)
    hot_edges = _cycle_edges(report)
    deadlocked = set(report.deadlocked) if report else set()
    # Döngü rengi durum şeridiyle aynı: deadlock varsa kırmızı, yalnızca döngü varsa turuncu.
    hot_color = HOT if report and report.has_deadlock else WARN

    parts = []

    # Kenarlar önce çizilir ki düğümler okların üstünde kalsın.
    for r in resources:
        top = RESOURCE_Y
        for p, amount in r.allocation.items():  # atama: R → P (ok process'e girer)
            x1, x2 = rx[r.name] - OFFSET, px[p.name] - OFFSET
            label = f"×{amount}" if amount > 1 else ""
            hot = (r.name, p.name) in hot_edges
            parts.append(_arrow(x1, top, x2, PROCESS_Y + RADIUS, "assign", hot, label, hot_color))
        for p, amount in r.waiting_queue:  # istek: P → R (ok kaynağa girer)
            x1, x2 = px[p.name] + OFFSET, rx[r.name] + OFFSET
            label = f"×{amount}" if amount > 1 else ""
            hot = (p.name, r.name) in hot_edges
            parts.append(_arrow(x1, PROCESS_Y + RADIUS, x2, top, "request", hot, label, hot_color))

    for p in processes:
        is_dead = p.name in deadlocked
        css = "node process deadlocked" if is_dead else "node process"
        fill = "#fdedec" if is_dead else "white"
        stroke = HOT if is_dead else NORMAL
        parts.append(
            f'<g class="{css}"><circle cx="{px[p.name]}" cy="{PROCESS_Y}" r="{RADIUS}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
            f'<text x="{px[p.name]}" y="{PROCESS_Y + 5}" text-anchor="middle" '
            f'font-weight="bold">{p.name}</text></g>'
        )

    for r in resources:
        x = rx[r.name] - RES_W / 2
        # Her örnek için bir nokta: dolu = verilmiş, boş = boşta.
        used = r.total_instances - r.available_instances
        dot_gap = RES_W / (r.total_instances + 1)
        dots = "".join(
            f'<circle class="instance {"used" if i < used else "free"}" '
            f'cx="{x + dot_gap * (i + 1)}" cy="{RESOURCE_Y + 34}" r="5" '
            f'fill="{NORMAL if i < used else "white"}" stroke="{NORMAL}"/>'
            for i in range(r.total_instances)
        )
        parts.append(
            f'<g class="node resource"><rect x="{x}" y="{RESOURCE_Y}" width="{RES_W}" '
            f'height="{RES_H}" rx="4" fill="white" stroke="#3498db" stroke-width="2"/>'
            f'<text x="{rx[r.name]}" y="{RESOURCE_Y + 18}" text-anchor="middle" '
            f'font-weight="bold">{r.name}</text>{dots}</g>'
        )

    defs = (
        "<defs>"
        f'<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{NORMAL}"/></marker>'
        f'<marker id="arrow-red" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{HOT}"/></marker>'
        f'<marker id="arrow-orange" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
        f'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{WARN}"/></marker>'
        "</defs>"
    )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'font-family="sans-serif">{defs}{"".join(parts)}</svg>')
